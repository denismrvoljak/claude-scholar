# Customising

The setup is meant to be edited. Onboarding gets it roughly right; the version that actually fits your project is the one you have been correcting for two months.

## What lives where

| File | Holds | Changes |
|------|-------|---------|
| `.claude/CLAUDE.md` | What the project is, read at the start of every session | Rarely |
| `.claude/rules/writing.md` | Style, terminology, banned phrasings | Every time you get feedback |
| `.claude/rules/structure.md` | Chapter order and character budgets | When the structure changes |
| `.claude/rules/research.md` | Databases and source standards | Rarely |
| `.claude/rules/figures.md` | Visual system | Once |
| `.claude/rules/typography.md` | Export format | Once |
| `docs/requirements.md` | The institution's rules, with sources | When you confirm something |
| `docs/facts.md` | Numbers, dates, terms, decisions | Constantly |
| `.claude/skills/*/SKILL.md` | How each command behaves | When a command keeps doing the wrong thing |

The distinction that matters: `CLAUDE.md` is loaded into every session automatically and should stay short, while the rules files are read by the skills that need them and can be as long as they need to be. Detail belongs in the rules.

## Adding a rule

Rules work when they are specific and carry their reason. Compare:

> Avoid vague language.

with

> Replace scale words ("several", "many", "a large sample") with the verified figure from `docs/facts.md`. Supervisor comment, 14 March: "how many is several?"

The second gets followed, because it says what to do, where the replacement comes from, and why the rule exists. The first is a mood.

For anything mechanically checkable, add a grep to the pre-flight block at the bottom of `writing.md`. `/write` runs that block against every file it edits and fixes the hits before reporting back, which turns a rule into an enforcement.

## Changing the structure

Edit `.claude/rules/structure.md` and `paper.md` together, and check the arithmetic: the per-section budgets sum to the limit, minus whatever the figures cost. Then create or rename the files in `sections/`. Skills read the structure file rather than assuming a chapter list, so nothing else needs touching.

## Adding a command

Create `.claude/skills/<name>/SKILL.md` with frontmatter:

```markdown
---
name: my-command
description: What it does and when to use it. Written for a model deciding whether to invoke it, so include the phrases a user would actually say.
allowed-tools: Read, Write, Glob, Grep, Bash
---

# /my-command

<Instructions. Be specific about which files to read and in what order — that is what separates a skill that works from a prompt that sometimes works.>
```

Two habits make skills reliable: tell them exactly which files to read first, and give them a way to check their own output before reporting back.

Ideas that have proved worth building, depending on the project: a defence-preparation command that generates likely examiner questions from the document's weakest claims, a translation command for a document that has to exist in two languages, and a data-provenance command for a quantitative project, which re-runs the analysis and checks the reported numbers against `docs/facts.md`.

## Adapting to a different kind of work

The layout assumes a long document with sections, sources, and a length limit. That covers theses, reports, dissertations, and most coursework. For work shaped differently:

- **A systematic review** needs the search protocol to be a first-class artefact, since the protocol is the method. Expand `research.md` into a full PRISMA-style protocol and keep screening decisions in `docs/`.
- **A monograph or a paper-based thesis** works with one file per paper instead of one per chapter, plus a wrapper. Adjust `paper.md`.
- **A group project** benefits from an authorship column in `structure.md`, so it stays clear who owns which section when the deadline compresses.

## Keeping up with upstream

This is a template, not a dependency. Once you have onboarded, your copy is yours and will diverge, which is correct. If you want a later improvement, copy the specific file across by hand and check it does not clash with a rule you have since written. Nothing here auto-updates, and nothing should.
