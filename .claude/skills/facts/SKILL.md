---
name: facts
description: Audit the document against the facts file and record new facts in it. Use when the user wants to check that numbers, dates, and terminology are consistent across sections, or wants to add or update an authoritative figure. Triggers on "check the numbers", "are the figures consistent", "update the facts", "add this to facts", "fact check".
args: optional — a fact to record, or a section to audit
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# /facts — Keep one version of the truth

`docs/facts.md` is the single source of truth for every number, date, sample size, definition, and terminology decision in the project. Sections quote it. When a figure changes, it changes here first and propagates outward.

This matters because the most damaging errors in a long document are not bad arguments, they are a sample size that is 4,312 in the methodology, "roughly 4,000" in the results, and 4,132 in the abstract. An examiner who finds one of those stops trusting all of them.

## Mode A — Record a fact

When given a new figure, date, definition, or decision:

1. Check whether `docs/facts.md` already covers it. If it does and the value differs, do not silently overwrite: show both, ask which is correct, and ask what changed.
2. Record it with everything needed to defend it later: the value, where it came from (query, file, notebook, source document), when it was produced, and any caveat on how it should be reported.
3. If the fact contradicts something already written in `sections/`, grep for the old value and list every location that now needs updating. Do not edit the sections without being asked.

## Mode B — Audit

Given a section, or the whole document:

1. Read `docs/facts.md`.
2. Extract every number, percentage, date, sample size, currency amount, and defined term from the target files.
3. Check each against the facts file, and report:
   - **Contradictions** — the document says one thing, the facts file another. Both locations, both values.
   - **Unrecorded** — a figure appears in the document that the facts file does not carry. It needs a source, or it needs to go.
   - **Drift** — the same quantity reported at different precision or rounding in different places, or a term used in a variant form.
   - **Stale** — a fact in the file that no section uses any more, which usually means an analysis was superseded and the file was not updated.
4. Report as a table with file and line for each. Do not fix anything unless asked.

## Structure of the facts file

Group by what the facts are about, not by which section uses them, since most are used in several. A workable set of headings:

```markdown
# Facts, decisions, and assumptions
Single source of truth. When a number appears in more than one place, this file is authoritative.
Last updated: <date>

## 1. Data and sample
<Sizes, date ranges, collection method, inclusion and exclusion rules, and what each snapshot or extract is called.>

## 2. Results
<Every reported figure, with its interval or error where it has one, and the analysis that produced it.>

## 3. Definitions and terminology
<The exact wording for each recurring term, its preferred form, and the near-synonyms that are not to be used.>

## 4. Decisions
<Methodological choices, when they were made, why, and what was rejected. This section answers most defence questions.>

## 5. Assumptions and known limits
<What the work takes for granted and where the evidence stops.>
```

Where the project has several datasets, snapshots, or study waves that could be confused, give each one an unambiguous name and use that name everywhere. Conflating two of them is the single most common factual error in an empirical document, and the hardest to spot once it is written.
