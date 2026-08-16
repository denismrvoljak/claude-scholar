# <Project title>

> **This is the template.** Run `/onboard` and it will be replaced with your project's real context. Until then, every skill falls back to generic defaults.

## What this is

<One paragraph: the deliverable, the institution and programme, the topic, and what the work is trying to establish. Written so that a session starting cold knows what it is working on.>

## Course and formal context

- **Institution / programme**: <...>
- **Deliverable**: <master thesis / internship report / literature review / course paper>
- **Supervisor**: <name, and what they care about>
- **Deadline**: <date>. <First attempt / resubmission.>
- **Length limit**: <N> <characters including spaces / words / pages>. <What is excluded.>
- **Citation style**: <...>
- **Exam form**: <written only / written plus oral defence>. <Any rule about AI tools at the defence.>

Full requirements, with a source for each line: `docs/requirements.md`.

## Research question<s>

<Verbatim, as they will appear in the document. Or the learning goals, for a reflective report. Everything the project does is checked against these.>

## Delimitation

<What is deliberately out of scope, and why. Most institutions grade this explicitly.>

## Project structure

- `paper.md` — the section manifest, in order
- `sections/` — one file per chapter
- `docs/facts.md` — **single source of truth** for every number, date, and term. Read it before writing anything; it wins over any draft.
- `docs/requirements.md` — formal requirements and assessment criteria
- `docs/guidelines/` — the institution's own documents
- `docs/plans/`, `docs/research/`, `docs/feedback/`
- `resources/theoretical/`, `resources/practical/` — source summaries
- `reference_material/` — sample work, prior drafts, exemplars
- `figures/`, `appendices/`

## Prior work and where it lives

<Paths to data, analysis code, notebooks, notes, earlier drafts, and anything outside this repository that a session needs to know exists.>

## Key terminology

<The recurring terms of this project, in their exact preferred form. The full table, including forbidden variants, is in `.claude/rules/writing.md`.>

## Constraints that shape the writing

<The two or three that actually bite. For example: the length limit forces choices about what gets full treatment; the assessment criteria weight the analysis chapter most; the supervisor requires a philosophy-of-science subsection.>

## Commands

| Command | Purpose |
|---------|---------|
| `/plan-section <s>` | Plan a section before drafting |
| `/write <s>` | Draft or revise a section |
| `/research <topic>` | Find and evaluate sources |
| `/save-material <url>` | File a source as a structured summary |
| `/verify-sources <file>` | Check citations exist and are used correctly |
| `/review <s>` | Review one section |
| `/full-review` | Review the whole document |
| `/figure <desc>` | Build a figure |
| `/facts` | Audit or update the source of truth |
| `/status` | Progress against budget |
| `/teach` | Learn the work to defence depth; mock examination |

## Working agreement

- Numbers and dates come from `docs/facts.md`, never from memory or an older draft.
- Feedback goes into `.claude/rules/` or `docs/facts.md` the day it arrives, not into a chat message.
- Claims carry citations or the project's own evidence. Neither means the sentence does not ship.
- <Any AI-usage declaration requirement, and where the log lives.>
