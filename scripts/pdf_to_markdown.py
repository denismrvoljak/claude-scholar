#!/usr/bin/env python3
"""Convert PDFs to Markdown by rendering each page and transcribing it with a vision model.

Why this exists
---------------
Text-layer extraction (pdfplumber, pdftotext, PyPDF) fails on the documents
academic work is actually made of: lecture slides exported to PDF, papers full
of equations, scanned handouts, charts whose meaning lives in the picture. The
text layer is either absent, or present but ordered by drawing sequence rather
than reading order.

Rendering each page to an image and asking a vision model to transcribe it
sidesteps all of that. Equations come back as LaTeX, tables as Markdown, and
figures as descriptions of what they show.

Credit
------
The render-page-then-transcribe approach, and the per-page caching that makes
a multi-thousand-page run resumable, are from a script by Kacper Kocieszewski
(github.com/kocieusz), who used it to convert 75+ PDFs and roughly 6,000 pages
of lecture material into Markdown for LLM-readable course wikis:

    https://gist.github.com/kocieusz/85e3cfcf623f4cfe02a7a485c0307d3c

This is an independent implementation of that idea. Differences from the
original: Claude instead of OpenAI, BSD-licensed pypdfium2 instead of
AGPL PyMuPDF, concurrent pages, the text layer passed as a transcription hint,
per-page failures that don't abort the run, a cost estimate before you spend
anything, and a Batches API mode that halves the price on large jobs.

Usage
-----
    python pdf_to_markdown.py lecture.pdf
    python pdf_to_markdown.py slides/ --out resources/practical/
    python pdf_to_markdown.py big.pdf --dry-run          # page count + cost estimate
    python pdf_to_markdown.py big.pdf --batch            # 50% cheaper, slower
    python pdf_to_markdown.py scan.pdf --model claude-sonnet-5

Install
-------
    pip install anthropic pypdfium2 pillow
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

try:
    import pypdfium2 as pdfium
except ImportError:
    sys.exit("Missing dependency: pip install pypdfium2")

try:
    import anthropic
except ImportError:
    sys.exit("Missing dependency: pip install anthropic")


# --- Model and cost ---------------------------------------------------------

DEFAULT_MODEL = "claude-opus-5"

# USD per million tokens (input, output). Batch API is half of both.
# Check current pricing at https://platform.claude.com/docs/en/pricing
PRICING = {
    "claude-opus-5": (5.00, 25.00),
    "claude-opus-4-8": (5.00, 25.00),
    "claude-sonnet-5": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
}

# Rough per-page estimate for a rendered slide plus its transcription.
EST_INPUT_TOKENS_PER_PAGE = 2200
EST_OUTPUT_TOKENS_PER_PAGE = 700


SYSTEM_PROMPT = """\
You transcribe a single page of a document into clean Markdown. Accuracy is the \
whole job: this transcription replaces the original for every downstream reader, \
so anything you drop is lost and anything you invent becomes a false citation.

Rules:

1. Transcribe the page's text exactly. Do not summarise, do not paraphrase, do \
not correct the author's errors, and do not add anything that is not on the page.
2. Mathematics goes in LaTeX: $...$ inline, $$...$$ for display equations. \
Transcribe every symbol, subscript, and index precisely.
3. Preserve the reading structure with Markdown headings, lists, and emphasis. \
On a slide, the slide title is a heading.
4. Tables become Markdown tables. If a table is too complex for Markdown, \
transcribe it as text and keep the row and column relationships explicit.
5. For a figure, chart, diagram, or image, write a description inside a \
blockquote: what it shows, its axes and their units, the trend or relationship \
it demonstrates, and any labelled values you can read. Someone who cannot see \
the figure should be able to follow the argument that depends on it.
6. Transcribe code blocks verbatim inside fenced blocks, with the language tag \
where you can identify it.
7. Keep citations, references, and footnotes exactly as written.
8. If part of the page is illegible, write [illegible] rather than guessing. A \
marked gap is recoverable; a plausible invention is not.
9. Ignore pure page furniture: running headers, slide numbers, and institutional \
footers, unless they carry real content.

Output only the Markdown transcription. No preamble, no commentary, no code \
fence around the whole response.
"""


@dataclass
class Page:
    index: int          # 0-based
    number: int         # 1-based, for labels
    png: bytes
    text_layer: str


# --- Rendering --------------------------------------------------------------


def render_pages(pdf_path: Path, scale: float, max_edge: int) -> list[Page]:
    """Render every page to PNG bytes, and pull the text layer as a hint."""
    from PIL import Image

    doc = pdfium.PdfDocument(str(pdf_path))
    pages: list[Page] = []

    for i in range(len(doc)):
        page = doc[i]

        try:
            text_layer = page.get_textpage().get_text_range().strip()
        except Exception:
            text_layer = ""

        image = page.render(scale=scale).to_pil()

        # Cap the long edge. Bigger is not better past the model's limit — it
        # costs tokens without adding legibility.
        longest = max(image.size)
        if longest > max_edge:
            ratio = max_edge / longest
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        pages.append(Page(index=i, number=i + 1, png=buffer.getvalue(), text_layer=text_layer))

    doc.close()
    return pages


def build_message(page: Page, label: str, use_text_layer: bool) -> list[dict]:
    """One user message: the page image, plus the text layer as a transcription hint."""
    prompt = f"Transcribe {label} {page.number}."

    # The text layer is often mis-ordered but its *characters* are exact. Giving
    # it to the model alongside the image measurably improves names, numbers,
    # and citations, where vision alone can slip.
    if use_text_layer and page.text_layer:
        excerpt = page.text_layer[:4000]
        prompt += (
            "\n\nThe PDF's embedded text layer for this page is below. Its reading "
            "order is unreliable, but the characters are exact — use it to confirm "
            "spellings, numbers, and symbols. The image is authoritative for layout "
            "and for anything the text layer omits.\n\n"
            f"<text_layer>\n{excerpt}\n</text_layer>"
        )

    return [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64.standard_b64encode(page.png).decode("utf-8"),
            },
        },
        {"type": "text", "text": prompt},
    ]


def request_params(page: Page, model: str, label: str, use_text_layer: bool) -> dict:
    return {
        "model": model,
        "max_tokens": 8000,
        "system": SYSTEM_PROMPT,
        # Transcription is not a reasoning task. Low effort keeps thinking spend
        # down without disabling thinking, which on current models can leak
        # internal tags into the visible response.
        "output_config": {"effort": "low"},
        "messages": [{"role": "user", "content": build_message(page, label, use_text_layer)}],
    }


def extract_text(message) -> str:
    return "".join(block.text for block in message.content if block.type == "text").strip()


# --- Live mode --------------------------------------------------------------


def transcribe_live(
    client, pages: list[Page], cache_dir: Path, model: str, label: str,
    use_text_layer: bool, concurrency: int,
) -> list[int]:
    """Transcribe pages concurrently. Returns the page numbers that failed."""
    todo = [p for p in pages if not (cache_dir / f"page_{p.number:04d}.md").exists()]
    cached = len(pages) - len(todo)
    if cached:
        print(f"  {cached} page(s) already transcribed, resuming")
    if not todo:
        return []

    failed: list[int] = []
    done = 0

    def work(page: Page) -> tuple[int, str | None, str | None]:
        # The SDK retries 429s and 5xx with backoff on its own; this loop covers
        # the rest, and gives an overloaded API room to recover on a long run.
        for attempt in range(4):
            try:
                message = client.messages.create(**request_params(page, model, label, use_text_layer))
                return page.number, extract_text(message), None
            except anthropic.APIStatusError as exc:
                if exc.status_code < 500 and exc.status_code != 429:
                    return page.number, None, f"{exc.status_code}: {exc.message}"
                time.sleep(2 ** attempt)
            except anthropic.APIConnectionError as exc:
                time.sleep(2 ** attempt)
                if attempt == 3:
                    return page.number, None, f"connection error: {exc}"
        return page.number, None, "exhausted retries"

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(work, p): p for p in todo}
        for future in as_completed(futures):
            number, text, error = future.result()
            done += 1
            if error:
                failed.append(number)
                print(f"  [{done}/{len(todo)}] page {number} FAILED — {error}")
            else:
                (cache_dir / f"page_{number:04d}.md").write_text(text, encoding="utf-8")
                print(f"  [{done}/{len(todo)}] page {number}")

    return sorted(failed)


# --- Batch mode -------------------------------------------------------------

# A batch is capped at 256 MB, and a rendered page carries roughly 1 MB of
# base64. Chunking keeps each submission comfortably inside that.
BATCH_CHUNK = 40


def transcribe_batch(
    client, pages: list[Page], cache_dir: Path, model: str, label: str,
    use_text_layer: bool, poll_seconds: int,
) -> list[int]:
    """Transcribe via the Batches API: half price, up to 24h turnaround."""
    todo = [p for p in pages if not (cache_dir / f"page_{p.number:04d}.md").exists()]
    cached = len(pages) - len(todo)
    if cached:
        print(f"  {cached} page(s) already transcribed, resuming")
    if not todo:
        return []

    failed: list[int] = []

    for start in range(0, len(todo), BATCH_CHUNK):
        chunk = todo[start : start + BATCH_CHUNK]
        requests = [
            {
                "custom_id": f"page-{p.number:04d}",
                "params": request_params(p, model, label, use_text_layer),
            }
            for p in chunk
        ]

        batch = client.messages.batches.create(requests=requests)
        print(
            f"  submitted batch {batch.id} "
            f"(pages {chunk[0].number}-{chunk[-1].number}); polling every {poll_seconds}s"
        )

        while True:
            batch = client.messages.batches.retrieve(batch.id)
            if batch.processing_status == "ended":
                break
            time.sleep(poll_seconds)

        for result in client.messages.batches.results(batch.id):
            number = int(result.custom_id.split("-")[1])
            if result.result.type == "succeeded":
                text = extract_text(result.result.message)
                (cache_dir / f"page_{number:04d}.md").write_text(text, encoding="utf-8")
            else:
                failed.append(number)
                print(f"  page {number} FAILED — {result.result.type}")

        print(f"  batch {batch.id} done")

    return sorted(failed)


# --- Assembly ---------------------------------------------------------------


def compile_markdown(
    pdf_path: Path, pages: list[Page], cache_dir: Path, out_path: Path,
    model: str, label: str, failed: list[int],
) -> None:
    parts = [
        "---",
        f'source_file: "{pdf_path.name}"',
        f"source_pages: {len(pages)}",
        f'transcribed_by: "{model}"',
        f'transcribed_at: "{time.strftime("%Y-%m-%d")}"',
    ]
    if failed:
        parts.append(f"failed_pages: {failed}")
    parts += [
        "---",
        "",
        f"# {pdf_path.stem.replace('_', ' ').replace('-', ' ')}",
        "",
        "> Machine transcription of a PDF, page by page, from rendered images. "
        "Check any figure, number, or equation against the original before "
        "quoting it in your own work.",
        "",
    ]

    for page in pages:
        cached = cache_dir / f"page_{page.number:04d}.md"
        parts.append(f"## {label} {page.number}")
        parts.append("")
        if cached.exists():
            parts.append(cached.read_text(encoding="utf-8"))
        else:
            parts.append(f"*[{label} {page.number} could not be transcribed.]*")
        parts += ["", "---", ""]

    out_path.write_text("\n".join(parts), encoding="utf-8")


# --- Driver -----------------------------------------------------------------


def guess_label(pdf_path: Path, pages: list[Page]) -> str:
    """Slides and papers want different page labels."""
    if not pages:
        return "Page"
    sample = pages[: min(5, len(pages))]
    # Slide exports are landscape and text-sparse; papers are portrait and dense.
    landscape = sum(1 for p in sample if len(p.text_layer) < 900)
    if landscape >= len(sample) * 0.8 and re.search(r"slide|lecture|deck|present", pdf_path.stem, re.I):
        return "Slide"
    return "Page"


def estimate_cost(page_count: int, model: str, batch: bool) -> float:
    rate_in, rate_out = PRICING.get(model, PRICING[DEFAULT_MODEL])
    if batch:
        rate_in, rate_out = rate_in / 2, rate_out / 2
    cost_in = page_count * EST_INPUT_TOKENS_PER_PAGE / 1_000_000 * rate_in
    cost_out = page_count * EST_OUTPUT_TOKENS_PER_PAGE / 1_000_000 * rate_out
    return cost_in + cost_out


def process(pdf_path: Path, args, client) -> int:
    print(f"\n{pdf_path.name}")
    pages = render_pages(pdf_path, args.scale, args.max_edge)
    label = args.label or guess_label(pdf_path, pages)
    cost = estimate_cost(len(pages), args.model, args.batch)
    print(f"  {len(pages)} page(s) · ~${cost:.2f} estimated · {args.model}")

    if args.dry_run:
        return 0

    out_dir = Path(args.out) if args.out else pdf_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{pdf_path.stem}.md"

    cache_dir = out_dir / f".transcribe_cache_{pdf_path.stem}"
    cache_dir.mkdir(exist_ok=True)

    if args.batch:
        failed = transcribe_batch(
            client, pages, cache_dir, args.model, label, not args.no_text_layer, args.poll
        )
    else:
        failed = transcribe_live(
            client, pages, cache_dir, args.model, label, not args.no_text_layer, args.concurrency
        )

    compile_markdown(pdf_path, pages, cache_dir, out_path, args.model, label, failed)

    if failed:
        print(f"  wrote {out_path} — {len(failed)} page(s) failed: {failed}")
        print("  cache kept; re-run to retry only the failures")
        return 1

    print(f"  wrote {out_path}")
    if not args.keep_cache:
        for f in cache_dir.iterdir():
            f.unlink()
        cache_dir.rmdir()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert PDFs to Markdown by transcribing rendered pages with a vision model.",
        epilog="Approach credit: Kacper Kocieszewski (github.com/kocieusz).",
    )
    parser.add_argument("input", help="A PDF file, or a directory of PDFs")
    parser.add_argument("--out", help="Output directory (default: alongside the input)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Default: {DEFAULT_MODEL}")
    parser.add_argument("--dry-run", action="store_true", help="Page count and cost estimate only")
    parser.add_argument("--batch", action="store_true",
                        help="Use the Batches API: half price, up to 24h turnaround")
    parser.add_argument("--poll", type=int, default=60, help="Batch poll interval in seconds")
    parser.add_argument("--concurrency", type=int, default=4, help="Parallel pages in live mode")
    parser.add_argument("--scale", type=float, default=2.0, help="Render scale (2.0 ≈ 144 DPI)")
    parser.add_argument("--max-edge", type=int, default=2000, help="Cap on the image's long edge")
    parser.add_argument("--label", help='Page label: "Page" or "Slide" (default: inferred)')
    parser.add_argument("--no-text-layer", action="store_true",
                        help="Do not pass the embedded text layer as a hint")
    parser.add_argument("--keep-cache", action="store_true", help="Keep per-page files after compiling")
    args = parser.parse_args()

    if args.model not in PRICING:
        print(f"Note: no cost estimate on file for {args.model}; using {DEFAULT_MODEL} rates.")

    target = Path(args.input)
    if target.is_dir():
        pdfs = sorted(target.glob("*.pdf"))
        if not pdfs:
            return print(f"No PDFs in {target}") or 1
    elif target.is_file():
        pdfs = [target]
    else:
        return print(f"Not found: {target}") or 1

    client = None if args.dry_run else anthropic.Anthropic()

    exit_code = 0
    for pdf in pdfs:
        try:
            exit_code |= process(pdf, args, client)
        except Exception as exc:
            print(f"  {pdf.name} FAILED: {exc}")
            exit_code = 1

    if args.dry_run and len(pdfs) > 1:
        print(f"\n{len(pdfs)} file(s). Run without --dry-run to transcribe.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
