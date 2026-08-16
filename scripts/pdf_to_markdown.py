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
The render-page-then-transcribe approach, and the per-page caching that makes a
multi-thousand-page run resumable, are from a script by kocieusz
(github.com/kocieusz), used to convert 75+ PDFs and roughly 6,000 pages of
lecture material into Markdown for LLM-readable course wikis:

    https://gist.github.com/kocieusz/85e3cfcf623f4cfe02a7a485c0307d3c

This is an independent implementation of that idea. Differences from the
original: any of three providers rather than one, BSD-licensed pypdfium2
instead of AGPL PyMuPDF, concurrent pages, the PDF's text layer passed as a
transcription hint, per-page failures that don't abort the run, a cost estimate
before you spend anything, and a batch mode that halves the price.

Providers
---------
Works with whichever API key you already have. The script auto-detects:

    ANTHROPIC_API_KEY   pip install anthropic
    OPENAI_API_KEY      pip install openai
    GEMINI_API_KEY      pip install google-genai   (GOOGLE_API_KEY also accepted)

Only the provider you use needs its package installed. Force one with
--provider, and set the model with --model — the built-in defaults go stale as
providers ship new models, so check the current list if a model is rejected.

Usage
-----
    python pdf_to_markdown.py lecture.pdf
    python pdf_to_markdown.py slides/ --out resources/practical/
    python pdf_to_markdown.py big.pdf --dry-run              # pages + cost estimate
    python pdf_to_markdown.py big.pdf --batch                # half price (Anthropic)
    python pdf_to_markdown.py scan.pdf --provider openai --model <model-id>

Install
-------
    pip install pypdfium2 pillow      # always
    pip install anthropic             # or: openai / google-genai
"""

from __future__ import annotations

import argparse
import base64
import io
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
    sys.exit("Missing dependency: pip install pypdfium2 pillow")


# --- Providers --------------------------------------------------------------

# Default models per provider. These go out of date as providers ship new
# models — pass --model to override, and check the provider's current model
# list if one is rejected. Only the Anthropic rates below are verified; supply
# --price-in / --price-out for a cost estimate on the others.
PROVIDERS = {
    "anthropic": {
        "env": ["ANTHROPIC_API_KEY"],
        "package": "anthropic",
        "install": "pip install anthropic",
        "default_model": "claude-opus-5",
        "batch": True,
        # USD per million tokens (input, output).
        "pricing": {
            "claude-opus-5": (5.00, 25.00),
            "claude-opus-4-8": (5.00, 25.00),
            "claude-sonnet-5": (3.00, 15.00),
            "claude-haiku-4-5": (1.00, 5.00),
        },
    },
    "openai": {
        "env": ["OPENAI_API_KEY"],
        "package": "openai",
        "install": "pip install openai",
        "default_model": "gpt-4o",
        "batch": False,
        "pricing": {},
    },
    "gemini": {
        "env": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "package": "google.genai",
        "install": "pip install google-genai",
        "default_model": "gemini-2.0-flash",
        "batch": False,
        "pricing": {},
    },
}

# Rough per-page token estimate for a rendered page plus its transcription.
EST_INPUT_TOKENS_PER_PAGE = 2200
EST_OUTPUT_TOKENS_PER_PAGE = 700


def detect_provider() -> str | None:
    """First provider with a key in the environment. Anthropic wins ties."""
    for name in ("anthropic", "openai", "gemini"):
        if any(os.getenv(var) for var in PROVIDERS[name]["env"]):
            return name
    return None


def make_client(provider: str):
    """Import and construct only the SDK actually being used."""
    spec = PROVIDERS[provider]
    if not any(os.getenv(var) for var in spec["env"]):
        sys.exit(f"Provider '{provider}' needs one of: {', '.join(spec['env'])}")
    try:
        if provider == "anthropic":
            import anthropic
            return anthropic.Anthropic()
        if provider == "openai":
            import openai
            return openai.OpenAI()
        if provider == "gemini":
            from google import genai
            key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            return genai.Client(api_key=key)
    except ImportError:
        sys.exit(f"Provider '{provider}' needs its SDK: {spec['install']}")
    raise ValueError(provider)


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

MAX_OUTPUT_TOKENS = 8000


@dataclass
class Page:
    index: int          # 0-based
    number: int         # 1-based, for labels
    png: bytes
    text_layer: str


# --- Rendering --------------------------------------------------------------


def render_pages(pdf_path: Path, scale: float, max_edge: int) -> list[Page]:
    """Render every page to PNG bytes, and pull the text layer as a hint."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Missing dependency: pip install pillow")

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
            image = image.resize((int(image.width * ratio), int(image.height * ratio)), Image.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        pages.append(Page(index=i, number=i + 1, png=buffer.getvalue(), text_layer=text_layer))

    doc.close()
    return pages


def build_prompt(page: Page, label: str, use_text_layer: bool) -> str:
    prompt = f"Transcribe {label} {page.number}."

    # The text layer is often mis-ordered but its *characters* are exact. Giving
    # it to the model alongside the image measurably improves names, numbers,
    # and citations, where vision alone can slip.
    if use_text_layer and page.text_layer:
        prompt += (
            "\n\nThe PDF's embedded text layer for this page is below. Its reading "
            "order is unreliable, but the characters are exact — use it to confirm "
            "spellings, numbers, and symbols. The image is authoritative for layout "
            "and for anything the text layer omits.\n\n"
            f"<text_layer>\n{page.text_layer[:4000]}\n</text_layer>"
        )
    return prompt


# --- Per-provider transcription --------------------------------------------


def transcribe_anthropic(client, page: Page, model: str, prompt: str) -> str:
    message = client.messages.create(**anthropic_params(page, model, prompt))
    return "".join(b.text for b in message.content if b.type == "text").strip()


def anthropic_params(page: Page, model: str, prompt: str) -> dict:
    """Also used to build Batches API request bodies."""
    return {
        "model": model,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "system": SYSTEM_PROMPT,
        # Transcription is not a reasoning task. Low effort keeps thinking spend
        # down without disabling thinking, which on current Claude models can
        # leak internal tags into the visible response.
        "output_config": {"effort": "low"},
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64.standard_b64encode(page.png).decode(),
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }],
    }


def transcribe_openai(client, page: Page, model: str, prompt: str) -> str:
    data_url = "data:image/png;base64," + base64.standard_b64encode(page.png).decode()
    response = client.chat.completions.create(
        model=model,
        max_completion_tokens=MAX_OUTPUT_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
                    {"type": "text", "text": prompt},
                ],
            },
        ],
    )
    return (response.choices[0].message.content or "").strip()


def transcribe_gemini(client, page: Page, model: str, prompt: str) -> str:
    from google.genai import types

    response = client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_bytes(data=page.png, mime_type="image/png"),
            prompt,
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        ),
    )
    return (response.text or "").strip()


TRANSCRIBERS = {
    "anthropic": transcribe_anthropic,
    "openai": transcribe_openai,
    "gemini": transcribe_gemini,
}


# --- Live mode --------------------------------------------------------------


def is_retryable(exc: Exception) -> bool:
    """Rate limits, overloads, and transport failures are worth another try.

    Deliberately message-based: it works the same across three SDKs without
    importing all of them, and the cost of one wasted retry is a few seconds.
    """
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if isinstance(status, int):
        return status == 429 or status >= 500
    text = str(exc).lower()
    return any(s in text for s in
               ("rate limit", "429", "500", "502", "503", "504", "overload",
                "timeout", "timed out", "connection", "unavailable"))


def transcribe_live(
    client, provider: str, pages: list[Page], cache_dir: Path, model: str,
    label: str, use_text_layer: bool, concurrency: int,
) -> list[int]:
    """Transcribe pages concurrently. Returns the page numbers that failed."""
    todo = [p for p in pages if not (cache_dir / f"page_{p.number:04d}.md").exists()]
    cached = len(pages) - len(todo)
    if cached:
        print(f"  {cached} page(s) already transcribed, resuming")
    if not todo:
        return []

    transcribe = TRANSCRIBERS[provider]
    failed: list[int] = []
    done = 0

    def work(page: Page) -> tuple[int, str | None, str | None]:
        prompt = build_prompt(page, label, use_text_layer)
        for attempt in range(4):
            try:
                return page.number, transcribe(client, page, model, prompt), None
            except Exception as exc:
                if not is_retryable(exc) or attempt == 3:
                    return page.number, None, f"{type(exc).__name__}: {exc}"
                time.sleep(2 ** attempt)
        return page.number, None, "exhausted retries"

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(work, p) for p in todo]
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


# --- Batch mode (Anthropic) -------------------------------------------------

# A batch is capped at 256 MB, and a rendered page carries roughly 1 MB of
# base64. Chunking keeps each submission comfortably inside that.
BATCH_CHUNK = 40


def transcribe_batch(
    client, pages: list[Page], cache_dir: Path, model: str, label: str,
    use_text_layer: bool, poll_seconds: int,
) -> list[int]:
    """Transcribe via Anthropic's Batches API: half price, up to 24h turnaround."""
    todo = [p for p in pages if not (cache_dir / f"page_{p.number:04d}.md").exists()]
    cached = len(pages) - len(todo)
    if cached:
        print(f"  {cached} page(s) already transcribed, resuming")
    if not todo:
        return []

    failed: list[int] = []

    for start in range(0, len(todo), BATCH_CHUNK):
        chunk = todo[start : start + BATCH_CHUNK]
        batch = client.messages.batches.create(requests=[
            {
                "custom_id": f"page-{p.number:04d}",
                "params": anthropic_params(p, model, build_prompt(p, label, use_text_layer)),
            }
            for p in chunk
        ])
        print(f"  submitted batch {batch.id} (pages {chunk[0].number}-{chunk[-1].number}); "
              f"polling every {poll_seconds}s")

        while True:
            batch = client.messages.batches.retrieve(batch.id)
            if batch.processing_status == "ended":
                break
            time.sleep(poll_seconds)

        for result in client.messages.batches.results(batch.id):
            number = int(result.custom_id.split("-")[1])
            if result.result.type == "succeeded":
                text = "".join(
                    b.text for b in result.result.message.content if b.type == "text"
                ).strip()
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
        parts.append(cached.read_text(encoding="utf-8") if cached.exists()
                     else f"*[{label} {page.number} could not be transcribed.]*")
        parts += ["", "---", ""]

    out_path.write_text("\n".join(parts), encoding="utf-8")


# --- Driver -----------------------------------------------------------------


def guess_label(pdf_path: Path, pages: list[Page]) -> str:
    """Slides and papers want different page labels."""
    if not pages:
        return "Page"
    sample = pages[: min(5, len(pages))]
    sparse = sum(1 for p in sample if len(p.text_layer) < 900)
    if sparse >= len(sample) * 0.8 and re.search(r"slide|lecture|deck|present", pdf_path.stem, re.I):
        return "Slide"
    return "Page"


def estimate_cost(page_count: int, provider: str, model: str, args) -> float | None:
    """None when no rates are known — better than inventing a number."""
    if args.price_in is not None and args.price_out is not None:
        rate_in, rate_out = args.price_in, args.price_out
    else:
        rates = PROVIDERS[provider]["pricing"].get(model)
        if not rates:
            return None
        rate_in, rate_out = rates

    if args.batch:
        rate_in, rate_out = rate_in / 2, rate_out / 2
    return (page_count * EST_INPUT_TOKENS_PER_PAGE / 1_000_000 * rate_in
            + page_count * EST_OUTPUT_TOKENS_PER_PAGE / 1_000_000 * rate_out)


def process(pdf_path: Path, args, client) -> int:
    print(f"\n{pdf_path.name}")
    pages = render_pages(pdf_path, args.scale, args.max_edge)
    label = args.label or guess_label(pdf_path, pages)

    cost = estimate_cost(len(pages), args.provider, args.model, args)
    cost_note = f"~${cost:.2f} estimated" if cost is not None else (
        f"~{len(pages) * (EST_INPUT_TOKENS_PER_PAGE + EST_OUTPUT_TOKENS_PER_PAGE) // 1000}k tokens "
        "(pass --price-in/--price-out for a cost estimate)")
    print(f"  {len(pages)} page(s) · {cost_note} · {args.provider}/{args.model}")

    if args.dry_run:
        return 0

    out_dir = Path(args.out) if args.out else pdf_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{pdf_path.stem}.md"

    cache_dir = out_dir / f".transcribe_cache_{pdf_path.stem}"
    cache_dir.mkdir(exist_ok=True)

    if args.batch:
        failed = transcribe_batch(client, pages, cache_dir, args.model, label,
                                  not args.no_text_layer, args.poll)
    else:
        failed = transcribe_live(client, args.provider, pages, cache_dir, args.model,
                                 label, not args.no_text_layer, args.concurrency)

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
        epilog="Approach credit: kocieusz (github.com/kocieusz).",
    )
    parser.add_argument("input", help="A PDF file, or a directory of PDFs")
    parser.add_argument("--out", help="Output directory (default: alongside the input)")
    parser.add_argument("--provider", choices=sorted(PROVIDERS),
                        help="Default: whichever API key is in the environment")
    parser.add_argument("--model", help="Default: the provider's default (see --help notes)")
    parser.add_argument("--dry-run", action="store_true", help="Page count and cost estimate only")
    parser.add_argument("--batch", action="store_true",
                        help="Batch API: half price, up to 24h turnaround (Anthropic only)")
    parser.add_argument("--poll", type=int, default=60, help="Batch poll interval in seconds")
    parser.add_argument("--concurrency", type=int, default=4, help="Parallel pages in live mode")
    parser.add_argument("--scale", type=float, default=2.0, help="Render scale (2.0 ≈ 144 DPI)")
    parser.add_argument("--max-edge", type=int, default=2000, help="Cap on the image's long edge")
    parser.add_argument("--label", help='Page label: "Page" or "Slide" (default: inferred)')
    parser.add_argument("--no-text-layer", action="store_true",
                        help="Do not pass the embedded text layer as a hint")
    parser.add_argument("--keep-cache", action="store_true", help="Keep per-page files after compiling")
    parser.add_argument("--price-in", type=float, help="USD per 1M input tokens, for the estimate")
    parser.add_argument("--price-out", type=float, help="USD per 1M output tokens, for the estimate")
    args = parser.parse_args()

    if not args.provider:
        args.provider = detect_provider()
        if not args.provider:
            keys = ", ".join(v for p in PROVIDERS.values() for v in p["env"])
            return print(f"No API key found. Set one of: {keys}\n"
                         f"Or pass --provider explicitly.") or 1
    if not args.model:
        args.model = PROVIDERS[args.provider]["default_model"]

    if args.batch and not PROVIDERS[args.provider]["batch"]:
        return print(f"--batch is not implemented for {args.provider}. "
                     f"Run without it, or use --provider anthropic.") or 1

    target = Path(args.input)
    if target.is_dir():
        pdfs = sorted(target.glob("*.pdf"))
        if not pdfs:
            return print(f"No PDFs in {target}") or 1
    elif target.is_file():
        pdfs = [target]
    else:
        return print(f"Not found: {target}") or 1

    client = None if args.dry_run else make_client(args.provider)

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
