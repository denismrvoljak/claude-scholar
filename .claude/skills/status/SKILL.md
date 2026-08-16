---
name: status
description: Show a progress dashboard for the document. Use when the user wants to see overall progress, character counts, section status, or how much is left. Triggers on "how far along", "what's done", "show progress", "how many characters", "status".
allowed-tools: Read, Glob, Grep, Bash
---

# /status — Where the document stands

## Steps

1. **Measure each section** in `sections/`: `wc -m` for characters and `wc -w` for words, and classify the file as `empty`, `outline`, `drafted`, or `reviewed` by reading it. A file of headings with no prose is an outline, not a draft.

   These counts are a planning estimate, not the submitted figure. `wc -m` includes markdown syntax that will not survive compiling, and excludes the fixed per-image allowance most institutions charge for a pasted figure. Say so when the total gets close to the limit, and point at `docs/COMPILING.md` — the authoritative count comes from the compiled document, and it needs checking well before the deadline rather than on submission day.

2. **Read the budgets** from `.claude/rules/structure.md` and the hard limit from `docs/requirements.md`.

3. **Build the dashboard.**

```
## Progress — <date>

| Section | Status | Chars | Budget | % |
|---------|--------|------:|-------:|--:|
| ... | | | | |
| **Total** | | | | |

Figures: N at <cost> each = <total> chars against the limit
Remaining budget: <chars>   (estimate — the real count comes from the compiled document)

## Material
Theoretical sources: N · Practical sources: N · Research logs: N · Verified reference list: yes/no

## Plans
Sections with a plan: N/M. Without: <list>

## Recently touched
<Files modified in the last week, with dates.>
```

4. **Flag what needs attention**, in order of urgency: sections over budget, the total against the limit, sections with content but no citations, sections with no plan and no draft, and anything untouched for a long time while its deadline approaches.

Keep it short. This is a glance, not a review — if something looks wrong, say which command to run next.

Do not edit any files. This skill is read-only.
