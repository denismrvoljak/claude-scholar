---
name: ingest
description: Convert PDFs — lecture slides, papers, course materials, scanned handouts — into clean Markdown the workspace can read, search, and cite. Use when the user has PDFs to bring into the project, mentions course materials or slide decks, asks to convert or extract or OCR a PDF, or when a PDF in the project turns out to be unreadable as text. Triggers on "convert these PDFs", "ingest my slides", "turn this into markdown", "extract the text from", "I have a folder of lectures", "OCR this".
args: path to a PDF or a directory of PDFs
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# /ingest — Turn PDFs into readable Markdown

Academic work arrives as PDFs, and the ones that matter most are the ones ordinary text extraction handles worst: lecture slides exported from PowerPoint, papers dense with equations, scanned handouts, figures whose meaning is entirely in the picture. Extracted text from those comes out scrambled, or empty, or missing exactly the equation the argument turns on.

This converts them by looking at each page and transcribing it. Equations come back as LaTeX, tables as Markdown tables, and figures as descriptions of what they show. The result is a file the author can read in an editor, grep, diff, cite by page, and hand to an agent in full.

It runs here, in the session. The `Read` tool renders PDF pages as images directly into the conversation, so the transcription is done by the model already in the room, on the author's existing subscription. There is no API key, no SDK, no `pip install`, and nothing to configure. The author gives a path and the Markdown appears.

## 1. Find the PDFs and count the pages

Page count decides everything that follows, so establish it first. Any of these work; use the first one available:

```bash
pdfinfo file.pdf | grep Pages                       # poppler, if installed
mdls -name kMDItemNumberOfPages file.pdf            # macOS, no install needed
python3 -c "import re,sys; print(len(re.findall(rb'/Type\s*/Page[^s]', open(sys.argv[1],'rb').read())))" file.pdf
```

For a folder, count every file and report the total before transcribing anything.

## 2. Ask what the documents are

Unless the filenames make it obvious. It changes the output:

- **Lecture slides** — the highest-value case and the one text extraction fails worst. Page marker is `Slide N`, and slide decks are mostly whitespace, so they transcribe fast.
- **Papers** — usually have a usable text layer, but equations and figures still need to be looked at.
- **Scans and photographs** — no text layer at all; looking at the page is the only option.
- **Books and long reports** — check the page count before committing. A 400-page book is a long job.

## 3. Show the size before spending anything

There is no invoice here, but there is a real cost: usage against the author's plan, and time. Roughly **2,000–3,000 tokens per page** all in — about 1,300 for the rendered page image, the rest for the transcription coming back. A 70-slide lecture deck is therefore on the order of 150k–200k tokens. State the estimate and the shape of the job:

> 4 decks, 212 pages total. Roughly 500k tokens, split across 6 workers, about ten minutes. Proceed?

Wait for a yes on anything above about 50 pages. Below that, just do it.

If the total is large enough to give the author pause, the honest options are a subset — the material actually needed this week rather than the whole folder — or converting the decks one at a time across several sessions. Both are better than a single run that stalls halfway through.

## 4. Read in chunks of ten pages

`Read` accepts at most 20 pages per call, and the `pages` argument is **required** above 10. Ten is the working chunk size — twenty pages of images at once crowds out the transcription itself.

```
Read(file_path="lecture_03.pdf", pages="1-10")
Read(file_path="lecture_03.pdf", pages="11-20")
```

Transcribe each chunk immediately after reading it, then move on. Do not read three chunks and then start writing.

## 5. Delegate anything past twenty pages

Page images are large and they stay in context for the rest of the session. Beyond about 20 pages, transcribe through subagents instead: **one worker per 40-page block**, each writing its own part file. The images land in the worker's context and die with it, the main thread only ever sees paths. This is what makes a folder of lecture decks possible at all.

Workers for independent blocks are independent — launch them in one message so they run concurrently.

```
.ingest-parts/
  lecture_03.p001-040.md
  lecture_03.p041-070.md
```

Give each worker its page range, its output path, the page marker to use (`Slide` or `Page`), and the transcription rules below **verbatim** — a worker that improvises its own format produces a part file that does not join cleanly to the others.

## 6. The transcription rules

Hand these to every worker, unchanged:

> Read your assigned page range in chunks of at most 10 pages, using the `pages` argument. Transcribe each chunk to your part file before reading the next one, appending as you go, so an interruption loses one chunk rather than all of them.
>
> - Open every page with `## <Label> <n>` — the marker the caller gave you, and the PDF's own page number. This is what makes the output citable.
> - Transcribe what is on the page. Do not summarise it, do not improve it, do not merge two slides that cover one idea, and do not add anything the page does not contain.
> - Equations as LaTeX: `$...$` inline, `$$...$$` displayed. Never as a Unicode approximation.
> - Tables as Markdown tables, with the original column order.
> - Code as fenced blocks, with the language tagged.
> - Figures, diagrams, and plots: `**[Figure: ...]**` followed by a description of what it actually shows — axes and their units, the trend, the labels, the arrows and what they connect. A reader who cannot open the PDF should get the point of the figure from your description. This is the part of the job text extraction cannot do, so do it properly.
> - Speaker notes, footnotes, and slide numbers printed on the page: keep them, marked as what they are.
> - Anything you genuinely cannot make out: `[unreadable]`, in place. Never guess at a number.
> - A blank or near-blank page still gets its heading, with `*(no content)*` beneath it. The page numbering has to stay aligned with the PDF.
>
> Reply with only the path you wrote and the page range you covered. The file is the deliverable.

## 7. Assemble

Concatenate the part files in page order into the final Markdown, with front matter recording what this is:

```markdown
---
source: lecture_03.pdf
source_path: ~/Downloads/course/lecture_03.pdf
pages: 70
transcribed: 2026-08-21
method: in-session vision transcription (claude-scholar /ingest)
---
```

Use `date +%F` for the date rather than assuming it. Then delete `.ingest-parts/` once the assembled file is verified — but not before.

**It resumes.** A part file that already exists and ends at its assigned last page is done; skip it and re-launch only the workers whose blocks are missing or truncated. Check this before starting, on every run. A long job interrupted at page 300 should cost 40 pages of rework, not 300.

## 8. Cross-check the text layer, if there is one

Free and worth doing where `pdftotext` is available:

```bash
pdftotext -f 1 -l 10 lecture_03.pdf - | head -50
```

The layer is unusable as a transcription — that is why this skill exists — but it holds correctly spelled proper nouns, author names, and digits. Where it disagrees with the transcription on a name or a number, the text layer is usually right. Fix those and note it.

## After it runs

1. **Spot-check the output.** Open the Markdown next to the PDF and compare a few pages: one with an equation, one with a figure, one with a table. Transcription is good but not perfect, and the failure mode that matters is a plausible-looking wrong number.
2. **File it properly.** Course material and technical documentation belong in `resources/practical/`. If a converted PDF is an academic source that will be cited, run `/save-material` on it to produce a proper structured summary with a reference entry — the raw transcription is the source text, not the summary.
3. **Add the source to `docs/facts.md`** if it carries figures the document will rely on.
4. **Check the repo size.** Transcriptions are small, but the source PDFs are not. `.gitignore` already excludes `resources/pdfs/`; keep the PDFs out of git and the Markdown in.

## What to tell the author about the output

Two things, honestly:

**It is a transcription, not a source.** Any number, equation, or figure detail should be verified against the original PDF before it is quoted in their own work. A transcription error that reaches the final document is theirs to defend, and "the tool misread it" is not a defence an examiner accepts.

**Cite the original.** The reference is the paper, the book, or the lecture — never the Markdown file. The transcription is a working copy, and it has no bibliographic standing.

## Copyright

Converting material the author already has legitimate access to, for their own study and reference, is ordinary use. Redistributing the conversion is a different act, and licensed course material and paywalled papers usually forbid it. If converted material is going into a repository, keep that repository private, and note it if the author seems about to publish one.

## Credits

The page-by-page approach — render each page, transcribe the image rather than the text layer, keep equations as LaTeX and describe the figures — is from [a script by kocieusz](https://gist.github.com/kocieusz/85e3cfcf623f4cfe02a7a485c0307d3c), written to convert 75+ PDFs and about 6,000 pages of lecture material into an LLM-readable knowledge base. This skill does the same thing without the script or the API key.
