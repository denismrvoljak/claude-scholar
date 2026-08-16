---
name: onboard
description: Set up this workspace for a specific academic writing project. Interviews the author about their institution's requirements, deliverable type, topic, writing style, and existing work, then generates the project's CLAUDE.md, style and structure rules, section files, and facts file. Use when the user says "onboard", "set up this project", "configure this for my thesis", "get started", "adapt this template", or is running claude-scholar for the first time in an empty or freshly cloned workspace.
args: optional profile hint, e.g. "thesis" or "internship report"
---

# /onboard — Turn the template into your project

You are setting up a long-running academic writing workspace for one specific author, one specific deliverable, and one specific set of institutional rules. Everything in this repository is currently generic. Your job is to interview the author, then rewrite the generic parts so that no later session has to ask these questions again.

Two things to hold onto throughout:

**Their requirements beat your defaults.** If the author's programme mandates a chapter order, a citation style, or a length limit, that is the answer, even when a profile suggests otherwise. Profiles fill gaps, they do not override.

**Write down the why.** A rule with a reason attached survives; a rule without one gets argued with in three weeks. When the author says "my supervisor hates the word 'leverage'", record the supervisor as the source.

## Phase 0 — Read the room before asking anything

Do this before the first question, and keep it quick.

1. `ls` the working directory. Establish which case you are in:
   - **Fresh template** — the claude-scholar files are here and `sections/` is empty. Full setup.
   - **Existing project** — there is already writing, data, notes, or a different structure here. You are adding the workspace around work in progress. Do not overwrite anything you did not create. Inventory first, ask second.
   - **Plugin mode** — the skills came from the plugin and the template directories do not exist. Create them as you go. Profiles live under `${CLAUDE_PLUGIN_ROOT}/profiles/`.
2. If anything is already written, skim it: `sections/`, `docs/`, any loose `.md`, and the git log. A single question that shows you read their draft buys more trust than ten that show you did not.
3. Check whether `.env` exists and whether Playwright MCP is available (look for `playwright` MCP tools). You will need both answers in Phase 7.

Then open with one short paragraph: what you found, and what the next 15 minutes will cover. Do not dump a checklist.

## Phase 1 — The deliverable

Ask with `AskUserQuestion`, batched. Keep to four questions per call.

- **Deliverable type** → picks the starting profile: empirical thesis, theoretical or literature-based thesis, reflective or internship report, course paper, other.
- **Institution and programme** (free text: university, faculty, degree, semester).
- **Language** of the document, and the spelling convention (British, American, other). This decides more than it looks like it does: it sets every later style check.
- **Deadline**, and whether this is a first attempt or a resubmission. A resubmission changes everything downstream, because prior feedback becomes the highest-authority document in the project.

Read the matching profile in `profiles/` (or `${CLAUDE_PLUGIN_ROOT}/profiles/`) now. It gives you the default chapter list, the default budget split, and the questions specific to that genre. Treat it as a draft to be corrected, not a template to be applied.

## Phase 2 — The formal requirements

This is the phase that most protects the author's grade, so do not rush it. The goal is a `docs/requirements.md` that states, with a source for each line, exactly what the institution demands.

Ask them to put whatever they have into `docs/guidelines/`: the study regulations, the course description, the supervisor's structure guide, the assignment brief, the exam-form page. PDFs, screenshots, and pasted text all work. Ask for URLs to anything official that is public and fetch it.

Then extract, and say where each answer came from:

- **Length limit** and its unit — characters including spaces, words, or standard pages. If it is pages, get the page definition (many institutions define a page as a fixed character count, e.g. 2,400 characters including spaces).
- **What is excluded from the count** — usually front page, table of contents, bibliography, and appendices. Sometimes the abstract. Get this exactly.
- **How figures and tables count.** A common rule is that a pasted image counts as a fixed number of characters regardless of size, while a table typed as text counts its actual characters. This single rule changes how the author should build every figure.
- **Whether the count must appear on the front page.**
- **Citation style** — Harvard, APA 7, IEEE, Vancouver, Chicago. Get the exact variant, and whether footnote citations are permitted or forbidden.
- **Abstract or summary** — required? Language? Separate limit?
- **Required structural elements** — philosophy of science section, learning-goal structure, reflection chapter, declaration pages, whatever the programme insists on.
- **Assessment criteria** — the actual list the examiner grades against. Copy it verbatim. `/review` and `/full-review` will check against it, so a paraphrase is worse than useless.
- **Appendix policy** — must the document be understandable without the appendices?
- **Submission mechanics** — file format, portal, oral defence format, whether AI tools are permitted at the defence.

If something is unknown, write `UNKNOWN — confirm with <who>` rather than guessing. An honest gap gets resolved; an invented number gets discovered at submission.

Write `docs/requirements.md` with a source note per line: `Source: study regulations §4.2` or `Source: supervisor email, 2026-03-14`.

## Phase 3 — The model to write like

Ask whether they have a sample of the target: a previous report of their own, a graded exemplar, a paper their supervisor pointed at, or a departmental template. Ask them to put it in `reference_material/`.

If they provide one, read it and extract a style profile. Be specific and evidence-based, quoting short examples:

- Person and voice: first person singular, first person plural, or impersonal? Is "I" acceptable in this genre at this institution?
- Tense conventions for method, results, and discussion.
- Typical paragraph length and section depth.
- Citation density: roughly how many citations per page, and where they cluster.
- How theory is integrated: a separate chapter, or woven into each analytical section?
- How figures and tables are captioned and referenced.
- Register: how formal, how hedged, how much the author is allowed to have a position.

Ask explicitly what they want to *copy* and what they want to *avoid* from the sample. A failed previous attempt is a valuable sample precisely because of what to avoid.

If they have no sample, say so plainly and fall back to the profile's defaults. Do not invent a house style and present it as the institution's.

## Phase 4 — The project itself

Free-form conversation, not a form. What you need to come away with:

- **Working title**, and whether it is fixed or provisional.
- **The problem** in the author's own words, and who it matters to.
- **Research questions** or, for a reflective report, the learning goals. Get them written down verbatim even if they are still rough. Everything downstream is checked against them.
- **Empirical setting** — case company, dataset, interviews, experiment, secondary data, or none.
- **Method** — quantitative, qualitative, mixed, design-science, conceptual.
- **The intended contribution.** Ask what a reader should be able to do or know afterwards that they could not before.
- **Theoretical anchors** already chosen, and whether they were chosen freely or mandated by a supervisor.
- **Delimitation** — what is deliberately out of scope. Most institutions grade this explicitly, and most authors never write it down until far too late.

Push back gently where a research question is not answerable, where the method cannot produce evidence for the claim, or where the scope is visibly too large for the length limit. Say it in one or two sentences, then continue. You are not the supervisor and this is not the moment for a full critique, but flagging a fatal scope problem in week one is worth more than any other thing this skill does.

## Phase 5 — What already exists

Inventory their prior work, because the most common failure of an AI writing setup is that it cannot see the six months of work that happened before it was installed.

Ask about, and where possible index:

- Existing drafts, in this repo or elsewhere. Get paths.
- Notes, supervision meeting notes, feedback documents, exam reports.
- Data, analysis code, notebooks, experiment logs, model outputs.
- Papers already read and saved, in any form — a Zotero export, a folder of PDFs, a list in a text file.
- Figures already produced.
- Anything already submitted or presented.

Offer to import: convert scattered notes into `docs/` files, turn a reading list into `resources/theoretical/` stubs, and record supervisor feedback in `docs/feedback/` with dates. For material that stays where it is, write the paths into `CLAUDE.md` so later sessions know it exists.

Seed `docs/facts.md` with every number, date, and definition you can already pin down. Explain what the file is for while you do it: it is the single source of truth, sections quote it rather than memory, and when a number changes it changes there first. This is the highest-leverage file in the project and it needs the author to believe in it from day one.

## Phase 6 — House style

Some of this comes from Phase 3, some has to be asked. Batch it.

- Words, phrases, and constructions to ban. Seed from any supervisor feedback already collected. Common ones: "leverage", "utilise", "seamless", "robust", "holistic", "actionable". Ask directly whether em dashes and semicolons are wanted or forbidden — authors usually have a firm opinion and it is cheap to honour.
- Terminology decisions: the preferred term for each recurring concept, including hyphenation and capitalisation, and which near-synonyms are forbidden so the vocabulary stays stable.
- Acronym policy.
- Number and unit formatting, decimal separator, date format.
- Whether they want a figure palette of their own (case company colours, for instance) or the neutral default.

Write all of it into `.claude/rules/writing.md`, and build the pre-flight grep block at the bottom of that file from their actual banned list, so `/write` can check itself. Tell them the list is meant to grow: every correction they ever make to a draft belongs there instead of in a chat message.

## Phase 7 — Research access

- Copy `.env.example` to `.env` if it does not exist. Never write a key into any file except `.env`, and never echo a key back into the conversation.
- Ask for an academic contact email for the OpenAlex and Crossref polite pools. Explain that no key is required for either, and that Semantic Scholar works unauthenticated but is rate-limited.
- Ask whether they have institutional access to subscription databases, and which ones they actually use.
- If yes, get the library proxy suffix. Tell them how to find it: open any database through the library portal and read the host in the URL bar, e.g. `www-scopus-com.ez.statsbiblioteket.dk`. Save it as `LIBRARY_PROXY_SUFFIX` and save the full proxied search-form URLs they use as `DB_*_URL`.
- Explain the login flow once, in plain terms: `/research` opens the database in a real browser window through Playwright MCP, and when a login page appears it stops and waits for them to sign in themselves. The agent never sees or stores the credentials, and it resumes from the authenticated page afterwards.
- If Playwright MCP is not installed and they want subscription databases, give them the command: `claude mcp add playwright npx @playwright/mcp@latest`.
- Record which databases are in scope in `.claude/rules/research.md`, along with the search-syntax quirks of each one they use.

## Phase 8 — AI usage policy

Ask what their institution requires: nothing, a declaration appendix, a detailed log, or a prohibition on certain uses. Ask specifically whether AI tools are permitted at the oral defence, because many programmes forbid them.

If any declaration is required, create `docs/ai_usage.md` now and note in `CLAUDE.md` that substantive AI-assisted work should be appended to it as it happens. Reconstructing this from memory in submission week is miserable and inaccurate.

Say once, without lecturing, that the author must be able to defend every sentence in the document as their own understanding.

## Phase 9 — Confirm, then generate

Present a compact summary: deliverable, limit and counting rules, citation style, chapter list with per-section budgets, style rules captured, sources of research access, prior work found. Ask for corrections. Fix what they correct. Only then write.

Files to generate or rewrite:

| File | Contents |
|------|----------|
| `.claude/CLAUDE.md` | Project context: what this is, the institution and course, constraints, structure, key terminology, where prior work lives, available commands. Replaces the template's placeholders. |
| `.claude/rules/writing.md` | Their style, citation format, banned list, terminology decisions, and the pre-flight grep block built from their banned words. |
| `.claude/rules/structure.md` | Their chapter order, their per-section character budgets summing to their limit, cross-referencing conventions. |
| `.claude/rules/research.md` | Their databases, their filing conventions, their source-quality bar. |
| `.claude/rules/figures.md` | Their palette and figure conventions, including how figures count against the limit. |
| `.claude/rules/typography.md` | House style for the final export. Adjust to any institutional template. |
| `docs/requirements.md` | Phase 2 output, with a source per line. |
| `docs/facts.md` | Seeded single source of truth. |
| `docs/ai_usage.md` | Only if required. |
| `sections/*.md` | One file per chapter, each with its heading skeleton, a one-line note on what belongs there, and its budget. |
| `paper.md` | Section manifest in order, with the title. |
| `README.md` | Short project README. Note that it was scaffolded from claude-scholar and link back. |

Budget arithmetic must be right: the per-section budgets sum to the total limit, and figure allowances are accounted for if figures count against it. Show the table.

Delete nothing the author wrote. If a file you were going to generate already exists with real content, merge into it or ask.

## Phase 10 — Hand over

Close with a short, concrete first move. Not a menu of possibilities: the actual next command, chosen from what you now know. Usually `/plan-section <the section they are closest to being able to write>`, or `/research <the gap that blocks everything else>`.

Mention that `.claude/rules/` is theirs to edit by hand, and that the single habit that makes this setup pay off is putting every piece of feedback into the rules or the facts file the day it arrives.

Two things worth mentioning once, here, so they are not discovered late: opening the project folder in Obsidian makes months of accumulated sections and source summaries navigable, and compiling to Word is a deliberate manual pass near the end rather than something to automate (`docs/COMPILING.md`). Say plainly that the character counts `/status` reports are a planning estimate, and that the count that goes on the front page comes from the compiled document.

If the work ends in an oral defence, say now that `/teach` exists for it and is worth starting before the document is finished rather than after. Make sure the exam format, duration, examiners, and any rule about notes or AI in the room are recorded in `CLAUDE.md`, since that is what `/teach` builds its mission from.

Do not run a second onboarding later. If the project changes shape, edit the rules directly or ask for a targeted update.
