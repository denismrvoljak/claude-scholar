---
name: plan-section
description: Create a detailed writing plan for a section before drafting it. Use when the user wants to plan, outline, structure, or prepare a section before writing. Triggers on "plan the", "outline the", "what should I cover in", "how should I structure", "prepare to write".
args: section name (e.g. "introduction", "methodology")
allowed-tools: Read, Write, Glob, Grep, Bash
---

# /plan-section — Decide what to write before writing it

A plan is worth making because it exposes what is missing while the fix is still cheap. Its most valuable output is usually the list of gaps, not the outline.

## Steps

1. **Read the context**
   - `.claude/rules/structure.md` — the section's role and budget
   - `docs/requirements.md` — what the institution expects here, and the assessment criteria this section is graded against
   - `docs/facts.md` — the evidence available
   - The target file and both adjacent sections — what is already covered, so the plan does not duplicate it
   - `docs/research/` and `resources/` — the material on hand
   - `docs/feedback/` — anything the supervisor already said about this section

2. **Write the plan**

   - **Argument** — one paragraph stating what this section establishes and how it advances the document's central claim. If you cannot write this paragraph, the section is not ready to plan.
   - **Outline** — subsections in order, with the point each one makes.
   - **Evidence and citations** — for each claim, the specific source or the specific piece of the author's own analysis that supports it. Name files.
   - **Figures and tables** — what is needed, what each shows, and its cost against the character budget if images count.
   - **Budget** — the section total from `structure.md`, split across subsections.
   - **Dependencies** — what must be written or decided first, and which cross-references to plan for.
   - **Gaps** — claims with no source yet, analyses not yet run, decisions not yet made. Be concrete about what would close each one.

3. **Save** to `docs/plans/plan_<section>_<YYYY-MM-DD>.md`.

4. **Report** the plan in brief and lead with the blockers. If research is needed before drafting can start, say which `/research` query to run.
