---
name: ingest
description: Convert PDFs — lecture slides, papers, course materials, scanned handouts — into clean Markdown the workspace can read, search, and cite. Use when the user has PDFs to bring into the project, mentions course materials or slide decks, asks to convert or extract or OCR a PDF, or when a PDF in the project turns out to be unreadable as text. Triggers on "convert these PDFs", "ingest my slides", "turn this into markdown", "extract the text from", "I have a folder of lectures", "OCR this".
args: path to a PDF or a directory of PDFs
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# /ingest — Turn PDFs into readable Markdown

Academic work arrives as PDFs, and the ones that matter most are the ones ordinary text extraction handles worst: lecture slides exported from PowerPoint, papers dense with equations, scanned handouts, figures whose meaning is entirely in the picture. Extracted text from those comes out scrambled, or empty, or missing exactly the equation the argument turns on.

This converts them by rendering each page to an image and transcribing it with a vision model. Equations come back as LaTeX, tables as Markdown tables, and figures as descriptions of what they show. The result is a file you can read in an editor, grep, diff, cite by page, and hand to an agent in full.

The approach comes from [a script by kocieusz](https://gist.github.com/kocieusz/85e3cfcf623f4cfe02a7a485c0307d3c), written to convert 75+ PDFs and about 6,000 pages of lecture material into an LLM-readable knowledge base.

## Before running anything

**Check the dependencies.** `pip install pypdfium2 pillow` always, plus the SDK for whichever provider is being used. The script names the missing one if any.

**Check for credentials.** The script works with whichever API key the author already has and picks it up automatically:

| Key in the environment | Provider | SDK |
|------------------------|----------|-----|
| `ANTHROPIC_API_KEY` | `anthropic` | `pip install anthropic` |
| `OPENAI_API_KEY` | `openai` | `pip install openai` |
| `GEMINI_API_KEY` or `GOOGLE_API_KEY` | `gemini` | `pip install google-genai` |

If several are set, Anthropic wins; `--provider` forces one. If none is set, say so before rendering anything rather than after.

All three paths are checked by `scripts/test_providers.py`, which points each SDK at a local mock endpoint and verifies the image reaches the wire and the response parses back. It costs nothing and needs no key. Run it if a provider starts failing after an SDK upgrade — it isolates a broken call shape from a rejected model ID in seconds.

**Set the model explicitly if the default is rejected.** Every provider's model list moves, and the defaults in the script go stale. `--model <id>` overrides, and a model-not-found error means the default has been superseded rather than that anything is broken. Only the Anthropic price table is maintained in the script; for the others, `--price-in` and `--price-out` produce an estimate from the provider's current published rates.

**Ask what the documents are**, unless it is obvious from the filenames. Slides and papers want different handling, and it changes the output:

- **Lecture slides** — the highest-value case and the one text extraction fails worst. Page label should be `Slide`.
- **Papers** — usually have a usable text layer, but equations and figures still need the vision pass.
- **Scans and photographs** — no text layer at all; vision is the only option.
- **Books and long reports** — check the page count before committing. A 400-page book is a real cost.

**Estimate first, always.** Run with `--dry-run` and show the page count and cost before spending anything. On a folder this is the difference between a two-dollar job and a two-hundred-dollar one, and the author should see the number before it is spent, not after.

```bash
python scripts/pdf_to_markdown.py <path> --dry-run
```

If the total is more than a few dollars, present the options rather than picking for them:

- **A cheaper model.** Every provider has a small fast model at a fraction of the flagship's price. Quality drops on dense equations and complex figures — for a maths-heavy lecture deck the saving is usually false economy, for clean prose it is not.
- **Batch mode** (`--batch`) — half price, turnaround up to 24 hours. Implemented for Anthropic. For a large backlog being converted once, it is almost always the right call.
- **A subset** — convert the material actually needed now, not the whole folder.

## Running it

```bash
# One file, alongside the original
python scripts/pdf_to_markdown.py lecture_03.pdf

# A folder, into the project's practical resources
python scripts/pdf_to_markdown.py ~/Downloads/course/ --out resources/practical/

# A large backlog, at half price
python scripts/pdf_to_markdown.py ~/Downloads/course/ --out resources/practical/ --batch

# A different provider or model
python scripts/pdf_to_markdown.py scan.pdf --provider openai --model <model-id>
```

Useful flags: `--concurrency` (parallel pages, default 4), `--scale` and `--max-edge` (render resolution — raise for dense small print, lower to cut cost), `--label Slide`, `--no-text-layer`, `--keep-cache`.

**It resumes.** Each page is cached as it completes, so an interrupted run picks up where it stopped and a failed page is retried on the next run rather than re-transcribing the whole document. On a long job this matters more than anything else in the script. Do not delete the cache directory to "start clean" unless the transcriptions themselves are wrong.

**Failures do not abort the run.** A page that fails after retries is recorded in the output's front matter as `failed_pages` and marked in place. Re-run the same command to retry only those.

## After it runs

1. **Spot-check the output.** Open the Markdown next to the PDF and compare a few pages: one with an equation, one with a figure, one with a table. Vision transcription is good but not perfect, and the failure mode that matters is a plausible-looking wrong number.
2. **File it properly.** Course material and technical documentation belong in `resources/practical/`. If a converted PDF is an academic source that will be cited, run `/save-material` on it to produce a proper structured summary with a reference entry — the raw transcription is the source text, not the summary.
3. **Add the source to `docs/facts.md`** if it carries figures the document will rely on.
4. **Check the repo size.** Transcriptions are small, but the source PDFs are not. `.gitignore` already excludes `resources/pdfs/`; keep the PDFs out of git and the Markdown in.

## What to tell the author about the output

Two things, honestly:

**It is a transcription, not a source.** Any number, equation, or figure detail should be verified against the original PDF before it is quoted in their own work. A transcription error that reaches the final document is theirs to defend, and "the tool misread it" is not a defence an examiner accepts.

**Cite the original.** The reference is the paper, the book, or the lecture — never the Markdown file. The transcription is a working copy, and it has no bibliographic standing.

## Copyright

Converting material the author already has legitimate access to, for their own study and reference, is ordinary use. Redistributing the conversion is a different act, and licensed course material and paywalled papers usually forbid it. If converted material is going into a repository, keep that repository private, and note it if the author seems about to publish one.
