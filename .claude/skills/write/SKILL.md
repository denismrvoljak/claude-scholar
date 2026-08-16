---
name: write
description: Draft or revise a section of the document. Use when the user wants to write, draft, expand, revise, rewrite, improve, or continue work on any section such as the introduction, literature review, methodology, analysis, discussion, or conclusion. Also triggers on "start writing", "flesh out", "add content to", "continue working on".
args: section name (e.g. "introduction", "methodology", "learning_goal_2")
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# /write — Draft or revise a section

You are drafting part of a long document that has to hold together across months of work. Consistency with what already exists matters as much as the quality of the new prose.

## 1. Identify the target

Map the argument to a file in `sections/`. If the name is ambiguous, list the candidates and ask. If the section does not exist, check `.claude/rules/structure.md` before creating it: an unplanned section is usually a sign the argument has drifted.

## 2. Read before writing

In this order, and do not skip the first two:

- `docs/facts.md` — every number, date, sample size, and terminology decision comes from here, not from memory and not from an older draft. Where a draft and this file disagree, this file wins.
- `.claude/rules/writing.md` — style, citation format, and the banned-phrase list. These are hard constraints, not preferences.
- `.claude/rules/structure.md` — this section's character budget and its place in the argument.
- `docs/requirements.md` — the institution's formal requirements and assessment criteria.
- The target file, to see what is already there.
- `docs/plans/plan_<section>_*.md` — an existing plan, if one was written.
- Adjacent sections, for transitions and terminology.
- `docs/feedback/` — feedback already given. Never regress a fix that was already made.
- Relevant material: glob `docs/research/*` and `resources/**/*.md` and read what bears on this section.

## 3. Write

- Open with an orienting paragraph: what this section does and why it is here.
- Every substantive claim carries a citation or rests on the document's own evidence. A claim that has neither does not belong in the draft.
- Follow the section-specific structure your profile and `structure.md` require.
- Prefer verified specifics to vague scale words. "4,312 responses over eleven weeks" beats "a large sample". If the exact figure is in `docs/facts.md`, use it.
- Tighten rather than inflate. If an explanation already exists in an earlier section, refer back to it in a clause instead of repeating it. Budget spent re-explaining is budget not spent on analysis.
- Keep the terminology fixed. One concept, one term, every time.
- Cite in the style set in `.claude/rules/writing.md` and nowhere else.

## 4. Self-check before reporting back

Run the pre-flight grep block from the bottom of `.claude/rules/writing.md` against the file you edited, and rewrite every hit. Then verify:

- Numbers, dates, and terms match `docs/facts.md` exactly.
- Headings and labels name what is actually in them, rather than gesturing at a category.
- Any counted-list opener ("three reasons", "five categories") is followed by that many items.
- Forward references ("Section 5 discusses…") actually pay off in the target section. Read it and check.
- Citations added here exist in the reference list, or are flagged for adding.

## 5. Report

- Character count (`wc -m`) against the section's budget.
- What was cut, consolidated, or moved.
- New citations that need a reference entry.
- Grep hits found and fixed.
- Anything you could not source, stated plainly rather than papered over.

## If the section is empty
Draft from the plan if one exists, otherwise from `.claude/rules/structure.md` and the available material. Say what you had to assume.

## If the section has content
Revise. Ask what to focus on if the instruction is open-ended, and never silently rewrite prose that was already reviewed and approved.
