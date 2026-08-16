---
name: full-review
description: Holistic review of the entire document rather than a single section. Use when the user asks whether the whole thing is ready, wants cross-chapter coherence checked, or asks about overall argument flow, terminology drift, or guideline compliance across the document. Triggers on "review the whole thesis", "review the whole report", "check everything", "holistic review", "does it hold together", "are the chapters connected".
allowed-tools: Read, Glob, Grep, Bash, Agent
---

# /full-review — Review the document as one thing

A document can have six strong sections and still fail: theory introduced and never used, a conclusion that answers a different question than the introduction asked, the same number given three ways, a promise in Chapter 1 that nothing delivers. Those failures are invisible from inside any single section, which is why this review exists.

## 1. Read everything

Every file in `sections/`, in order, plus `docs/facts.md`, `docs/requirements.md`, `.claude/rules/`, and `docs/feedback/`. For a long document, dispatch parallel subagents to read groups of sections and report back, then do the cross-cutting analysis yourself — the connections are the point and they cannot be delegated piecemeal.

## 2. Assess

**A. The red thread.** Trace the central argument from the research question to the conclusion. For each question or learning goal: where it is posed, where it is addressed, where it is answered. Mark any that is posed and never answered, or answered without having been posed.

**B. Chapter coherence.** Does each chapter set up the next? Does the roadmap in the introduction match what the document actually does? Is there a section that serves no part of the argument?

**C. Theory into practice.** Is every concept introduced before it is used? Is the theory in the literature review actually applied later, or introduced and abandoned? Are there claims in the analysis or discussion with no theoretical or empirical footing?

**D. Facts.** Grep every number, percentage, date, and sample size across all sections and check each against `docs/facts.md`. Report every disagreement with both locations. This check catches more real errors than any other in this list.

**E. Terminology.** List the recurring concepts and every variant used for each. Any concept named more than one way is a finding. Check acronyms are defined once, on first use, and used consistently afterwards.

**F. Citations.** Extract every in-text citation and cross-check against the reference list, in both directions: cited but not listed, listed but never cited. Flag sections that are conspicuously thin on sources given what they claim.

**G. Requirements.** Against `docs/requirements.md`: total length versus the limit, per-section budgets, citation style, every mandated structural element, abstract length, figure and table numbering, appendix policy, front-page requirements.

**H. Assessment criteria.** Go through the institution's criteria one at a time and grade the document against each, with the evidence for the grade.

## 3. Report

```
# Full Review — <date>

## Overall
<Three to five sentences. Would this pass, and what is the single biggest risk?>

## Length
| Section | Chars | Budget | Status |
|---------|------:|-------:|--------|
| ... | | | |
| **Total** | | | |

## A. Red thread
- RQ1: posed §1.3 → addressed §4.2 → answered §6.1 [COMPLETE / INCOMPLETE]

## B–H
<One block per dimension, each finding tagged CRITICAL / WARNING / OK with exact locations.>

## Priority actions
<Ordered by impact on the grade, not by section order. Say what to do, not just what is wrong.>
```

Distinguish throughout between what is missing and what is wrong — they need different work. Where a section is still a stub, note it and spend the effort on sections with real content.

Do not edit any files. This skill is read-only.
