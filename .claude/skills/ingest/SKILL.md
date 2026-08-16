---
name: ingest
description: Convert PDFs — lecture slides, papers, course materials, scanned handouts — into clean Markdown the workspace can read, search, and cite. Use when the user has PDFs to bring into the project, mentions course materials or slide decks, asks to convert or extract or OCR a PDF, or when a PDF in the project turns out to be unreadable as text. Triggers on "convert these PDFs", "ingest my slides", "turn this into markdown", "extract the text from", "I have a folder of lectures", "OCR this".
args: path to a PDF or a directory of PDFs
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# /ingest — Turn PDFs into readable Markdown

Academic work arrives as PDFs, and the ones that matter most are the ones ordinary text extraction handles worst: lecture slides exported from PowerPoint, papers dense with equations, scanned handouts, figures whose meaning is entirely in the picture. Extracted text from those comes out scrambled, or empty, or missing exactly the equation the argument turns on.

This converts them by rendering each page to an image and transcribing it with a vision model. Equations come back as LaTeX, tables as Markdown tables, and figures as descriptions of what they show. The result is a file you can read in an editor, grep, diff, cite by page, and hand to an agent in full.

The approach comes from [a script by Kacper Kocieszewski](https://gist.github.com/kocieusz/85e3cfcf623f4cfe02a7a485c0307d3c), written to convert 75+ PDFs and about 6,000 pages of lecture material into an LLM-readable knowledge base.

## Before running anything

**Check the dependencies.** `pip install anthropic pypdfium2 pillow`. The script says which one is missing if any are.

**Check for credentials.** The script needs `ANTHROPIC_API_KEY` in the environment, or an `ant auth login` profile. If neither is present, say so before rendering anything rather than after.

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

- **A cheaper model** (`--model claude-sonnet-5`, or `claude-haiku-4-5` for clean, text-heavy scans). Quality drops on dense equations and complex figures — for a maths-heavy lecture deck the saving is usually false economy, for clean prose it is not.
- **The Batches API** (`--batch`) — half price, and turnaround up to 24 hours. For a large backlog being converted once, this is almost always the right call.
- **A subset** — convert the material actually needed now, not the whole folder.

## Running it

```bash
# One file, alongside the original
python scripts/pdf_to_markdown.py lecture_03.pdf

# A folder, into the project's practical resources
python scripts/pdf_to_markdown.py ~/Downloads/course/ --out resources/practical/

# A large backlog, at half price
python scripts/pdf_to_markdown.py ~/Downloads/course/ --out resources/practical/ --batch
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
