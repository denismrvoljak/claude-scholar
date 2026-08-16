---
name: review
description: Review one section for academic quality against the project's rules and the institution's criteria. Use when the user wants feedback on, a critique of, or an assessment of a section. Triggers on "review my", "how does this look", "check the quality of", "is this section ready", "give me feedback on".
args: section name
allowed-tools: Read, Glob, Grep, Bash
---

# /review — Review a section

You are an examiner reading one section closely. Be specific: a finding without a location and a fix is not a finding.

## 1. Read

- The target section.
- `docs/facts.md` — **first among the standards.** Any number, date, or term in the section that disagrees with this file is a CRITICAL finding.
- `docs/requirements.md` — formal requirements and the assessment criteria the work is graded against.
- `.claude/rules/writing.md` and `.claude/rules/structure.md`.
- `docs/feedback/` — prior feedback. A regressed fix is CRITICAL.
- The adjacent sections, for continuity and duplication.

## 2. Evaluate

**Argument.** Does the section have one point, stated early and carried through? Does each paragraph advance it? Is there a paragraph that could be deleted with no loss?

**Evidence.** Is every substantive claim supported by a citation or by the author's own analysis? Point to the unsupported ones by line. Does the evidence actually support the strength of the claim as written, or has a suggestive finding been reported as a settled one?

**Method and reasoning.** Are assumptions stated? Are the limits of the evidence acknowledged where they matter? Is anything asserted that the method used could not establish?

**Criteria alignment.** Go through the assessment criteria in `docs/requirements.md` one by one and say how this section performs against each.

**Structure.** Does it follow the structure `structure.md` requires for this section, including any element the institution mandates?

**Citations.** Correct style, no stray footnotes, every cited work in the reference list.

**Language.** Register, paragraph length, defined acronyms, consistent terminology, and the conventions set in `writing.md`.

**Rule sweep.** Run the pre-flight grep block from the bottom of `.claude/rules/writing.md` against the file. Report every hit with its line number. A hit is at least a WARNING; a hit on a term the supervisor personally objected to is CRITICAL. For each, check whether the sentence would be stronger with a concrete substitute — a number, a threshold, a named mechanism.

Also check: headings that name a category rather than its contents, counted-list openers with no list, forward references that never pay off, and explanations repeated from an earlier section.

**Budget.** `wc -m` the file against the budget in `structure.md`.

## 3. Report

```
## Review: <section>

Characters: X / Y budget

### CRITICAL — must fix
- [C1] <finding> — <file:line> — <fix>

### WARNING — weakens the work
- [W1] ...

### SUGGESTION
- [S1] ...

### What is working
- <specifically what, so it does not get edited away>
```

Say why each critical finding matters, tied to the assessment criteria where it applies. Do not pad the list: three real problems reported precisely are more useful than twenty stylistic notes.

Do not edit any files. This skill is read-only.
