# claude-scholar

A Claude Code workspace for writing academic work: master theses, internship and project reports, literature reviews, and course papers.

It is not a prompt collection. It is a project layout plus a set of skills that keep a long piece of academic writing consistent over months: one file per chapter, one source-of-truth file for every number and date, explicit style rules that Claude checks itself against, verified citations, and a character budget per section.

The setup is deliberately generic. An interactive `/onboard` session turns it into *your* project: your institution's formal requirements, your deliverable type, your writing style, your topic, and whatever prior work you already have.

> Community project. Not affiliated with or endorsed by Anthropic.

---

## Quickstart

### A. Start a new writing project

```bash
npx degit denismrvoljak/claude-scholar my-thesis
cd my-thesis
claude
```

Then, in Claude Code:

```
/onboard
```

`/onboard` interviews you (10–20 minutes), then writes your `CLAUDE.md`, your style and structure rules, your section files, and a facts file. Everything after that is ordinary work: `/plan-section`, `/research`, `/write`, `/review`.

### B. Add the skills to a project you already have

```
/plugin marketplace add denismrvoljak/claude-scholar
/plugin install claude-scholar@claude-scholar
```

Then run `/claude-scholar:onboard` in your project directory. It scaffolds the missing directories in place and leaves your existing files alone.

---

## What you get

### Skills

| Command | What it does |
|---------|--------------|
| `/onboard` | Interactive setup. Establishes requirements, style, structure, and imports prior work. Run once. |
| `/plan-section <section>` | Plans a section before drafting: outline, citations to use, figures needed, character budget, gaps. |
| `/write <section>` | Drafts or revises a section against your style rules and facts file, then self-checks with your banned-phrase greps. |
| `/research <topic>` | Finds sources via OpenAlex, Semantic Scholar, and (optionally) your library's subscription databases through a browser. Saves a structured research log. |
| `/save-material <url>` | Fetches a paper or resource and files it as a structured summary with a ready-to-paste reference entry. |
| `/verify-sources <file>` | Checks every citation actually exists, assigns a quality tier, and rejects the ones that do not resolve. |
| `/review <section>` | Reviews one section: argument, citations, style-rule violations, character count. |
| `/full-review` | Reviews the whole document: cross-chapter coherence, red thread, terminology drift, citation completeness, guideline compliance. |
| `/figure <description>` | Builds a self-contained HTML figure in your project's visual style. |
| `/status` | Progress dashboard: character counts per section against budget, resources saved, plans written. |
| `/facts` | Audits the document against the facts file and flags every number, date, or term that drifted. |
| `/teach` | Teaches you your own document to the depth an oral defence needs: concept inventory, lessons built on retrieval practice, and adversarial mock examination. |
| `/ingest` | Converts PDFs — lecture slides, papers, scans — into clean Markdown with LaTeX equations and described figures. |

### Agents

- `project-researcher` — read-only sweep of your own resources, notes, drafts, and prior work.
- `web-researcher` — autonomous source hunting with quality tiering.
- `academic-reviewer` — rigorous examiner-style review against your institution's criteria.

### Rules

`.claude/rules/` holds the constraints Claude reads before writing anything:

- `writing.md` — style, citation format, banned words and phrasings, pre-flight greps
- `structure.md` — section order, character budgets, cross-referencing
- `research.md` — how research logs and resource summaries are filed
- `figures.md` — visual system for figures
- `typography.md` — the house style for the final Word/PDF export

These are generic until `/onboard` rewrites them for your project. They are meant to be edited by hand afterwards: every time your supervisor tells you something, put it in the rules file, not in a chat message you will lose.

---

## The ideas that make it work

**One facts file.** `docs/facts.md` is the single source of truth for every number, date, sample size, and terminology decision. Sections quote it, never memory. `/write` reads it first, `/review` flags drift, `/facts` audits the whole document. This is what stops the classic failure of a thesis where the sample size is 4,312 in the methodology and "roughly 4,000" in the results, and 4,132 in the abstract.

**Rules over reminders.** Supervisor feedback and self-corrections go into `.claude/rules/writing.md` as hard constraints, including a banned-phrase list with a grep block that `/write` runs on itself before reporting back. The list grows over the life of the project and never has to be re-explained.

**Character budgets are structural.** Most institutions count characters including spaces, and exclude the front matter, bibliography, and appendices. `structure.md` carries a per-section budget, `/status` shows the burn-down, and `/review` flags an over-budget section while it is still cheap to fix.

**Citations are verified, not trusted.** Models invent plausible references. `/research` requires a DOI or a resolvable URL before a source is recommended, and `/verify-sources` re-checks a finished reference list against OpenAlex and Semantic Scholar and reports what it could not confirm.

**Sections are files.** `paper.md` is a manifest that lists the section files in order. Chapters stay independently editable and reviewable, and character counting is per file.

**Your source material has to be readable.** Course slides, papers, and scanned handouts arrive as PDFs, and the ones that matter most are the ones text extraction handles worst — a slide deck exported from PowerPoint extracts as scrambled fragments, and a scan extracts as nothing at all. `/ingest` renders each page and transcribes it with a vision model instead: equations come back as LaTeX, tables as tables, figures as descriptions of what they show. The output is greppable, diffable, citable by page, and small enough to hand to an agent whole. It caches per page, so a six-thousand-page backlog survives an interrupted run.

**Submitting is not the end.** Most academic work is defended out loud, with no notes and usually no AI in the room. `/teach` treats that as the real deadline: it inventories everything an examiner could ask about, tests what you can actually produce unaided rather than what you think you know, teaches into the gaps, and then turns adversarial and examines you on your own weakest claims. A document you cannot explain without the tool is a problem worth finding in week ten rather than in the room.

---

## Research database access

Two tiers, and you can use either or both. See [docs/DATABASES.md](docs/DATABASES.md) for the full setup.

**Tier 1 — open APIs (no institution needed).** OpenAlex and Semantic Scholar cover metadata, abstracts, citation counts, and both directions of the citation graph. This is what makes snowball searching work: find one strong anchor paper, then walk forward through who cited it and backward through what it cited. Copy `.env.example` to `.env` and add keys. Both work without a key at lower rate limits.

**Tier 2 — your library's subscription databases (Scopus, Web of Science, EBSCO, JSTOR, ProQuest).** These sit behind an institutional login, so an API key will not reach them. Instead, `/research` drives a real browser through the [Playwright MCP server](https://github.com/microsoft/playwright-mcp): it opens the database through your library's proxy, and if a login screen appears it stops and asks you to sign in by hand in the visible browser window, then continues the search from there. Your credentials are never seen by, sent to, or stored by the agent. Put your proxy URL pattern in `.env` during `/onboard` and the skill uses it automatically.

---

## Repository layout

```
my-thesis/
├── .claude/
│   ├── CLAUDE.md          # project context — rewritten by /onboard
│   ├── settings.json      # permissions
│   ├── rules/             # writing, structure, research, figures, typography
│   ├── skills/            # the commands above
│   └── agents/            # subagents
├── docs/
│   ├── facts.md           # single source of truth for numbers and terms
│   ├── guidelines/        # your institution's official requirements (you supply)
│   ├── plans/             # section plans
│   └── research/          # research logs and verification reports
├── sections/              # one file per chapter
├── resources/
│   ├── theoretical/       # academic paper summaries
│   └── practical/         # domain, company, or dataset references
├── reference_material/    # sample reports, prior drafts, supervisor feedback
├── teach/                 # exam preparation: inventory, lessons, question bank, records
├── scripts/               # pdf_to_markdown.py — the /ingest converter
├── figures/               # self-contained HTML figures
├── appendices/
├── paper.md               # section manifest, in order
└── .env                   # API keys and library proxy (gitignored)
```

## Profiles

`/onboard` starts from a profile and adapts it to your answers. Profiles live in [`profiles/`](profiles/) and are plain markdown you can read and argue with:

- `thesis-empirical.md` — research questions, theory, methodology, results, discussion, conclusion
- `thesis-theoretical.md` — argument-driven or literature-based thesis with no primary data collection
- `reflective-report.md` — internship or practice report structured around learning goals, theory serving reflection
- `course-paper.md` — short paper or essay, single argument, tight budget

Nothing forces you into one. If your programme mandates a different chapter order, `/onboard` takes it verbatim from your guideline documents and the profile only supplies defaults for what those documents leave open.

## Requirements

- [Claude Code](https://code.claude.com)
- Optional: [Playwright MCP](https://github.com/microsoft/playwright-mcp) for subscription databases — `claude mcp add playwright npx @playwright/mcp@latest`
- Optional: free API keys from [OpenAlex](https://openalex.org) and [Semantic Scholar](https://www.semanticscholar.org/product/api)
- Optional, for `/ingest`: `pip install pypdfium2 pillow` plus one provider SDK (`anthropic`, `openai`, or `google-genai`) and the matching API key — it uses whichever you already have

## Credits

The PDF-to-Markdown approach behind `/ingest` — render each page, transcribe the image, cache per page so long runs resume — is from [a script by kocieusz](https://gist.github.com/kocieusz/85e3cfcf623f4cfe02a7a485c0307d3c), written to convert 75+ PDFs and roughly 6,000 pages of lecture material into an LLM-readable knowledge base. `scripts/pdf_to_markdown.py` is an independent implementation of that idea.

## A note on academic integrity

This setup is built for the case where you do the thinking and the tool does the drafting, checking, and bookkeeping. That is not the same as the case where the tool does the thinking, and most institutions treat the two very differently.

Check what your programme allows before you use any of it, and check whether you have to declare it. Many now require a written statement of how generative AI was used. `/onboard` asks about this and, if your institution requires a declaration, keeps a running log at `docs/ai_usage.md` so you are not reconstructing it from memory the week before submission. Some programmes also bar AI tools at the oral defence, which is worth knowing early: if you cannot explain a paragraph without the tool, it should not be in your document.

## Licence

MIT. See [LICENSE](LICENSE).
