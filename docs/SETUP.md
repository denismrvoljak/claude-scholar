# Setup

## 1. Get the workspace

**New project**

```bash
npx degit denismrvoljak/claude-scholar my-thesis
cd my-thesis
git init && git add -A && git commit -m "Scaffold from claude-scholar"
```

`degit` copies the files without the upstream git history. `git clone` works too if you would rather keep the history and change the remote afterwards.

**Existing project**

```
/plugin marketplace add denismrvoljak/claude-scholar
/plugin install claude-scholar@claude-scholar
```

The skills become available as `/claude-scholar:onboard`, `/claude-scholar:write`, and so on. `/onboard` will create the directories it needs without touching what you already have.

## 2. Credentials

```bash
cp .env.example .env
```

Nothing in `.env` is required. Filling it in improves rate limits and unlocks your library's databases. `.env` is gitignored — keep it that way, and never paste a key into a section file, a commit message, or the chat.

## 3. Optional: browser access to subscription databases

```bash
claude mcp add playwright npx @playwright/mcp@latest
```

Only needed if you want Scopus, Web of Science, EBSCO, or similar. See [DATABASES.md](DATABASES.md) for the proxy setup and how the login handoff works.

## 4. Collect your institution's documents

Put whatever you have into `docs/guidelines/` before onboarding: study regulations, course description, assignment brief, supervisor's structure guide, exam form page, marking rubric. PDFs, screenshots, and pasted text all work, and links to public pages are fine too.

This is the highest-value ten minutes of the whole setup. Onboarding reads these documents and turns them into rules that every later session enforces, so a length limit or a mandated chapter is caught while it is still a formatting question rather than a rewrite.

If you have a sample of the target — a graded exemplar, a previous report of your own, something your supervisor pointed at — put it in `reference_material/`. A failed previous attempt is just as useful as a good one, for the opposite reason.

## 5. Onboard

```bash
claude
```

```
/onboard
```

Fifteen to twenty minutes of questions, then it writes your `CLAUDE.md`, your rules, your section files, and your facts file. Answer "I don't know yet" freely — it records the gap rather than inventing an answer, and you can fill it in later.

## 6. Work

```
/plan-section introduction     # decide what goes in it, and what is missing
/research <the gap that blocks you>
/write introduction
/review introduction
/status                        # where the budget stands
```

And, if the work is defended orally, before you think you need it:

```
/teach                         # inventory what you will be asked, and test what you can actually say
/teach examine                 # adversarial mock, once there is a full draft
```

## Optional: read the project in Obsidian

```
Obsidian → Open folder as vault → pick the project root
```

No import, no conversion, no lock-in — the markdown files stay exactly as they are and Claude Code keeps editing them normally. What you get is search across every section and source summary at once, an outline view for long chapters, and rendered LaTeX (which is what makes `/ingest` output readable). `.obsidian/` is already gitignored.

## Maintenance habits

Three things, and the whole setup rests on them:

**Feedback goes into the rules the day it arrives.** A supervisor comment written into `.claude/rules/writing.md` is enforced on every future draft. The same comment left in an email is re-learned every time.

**Numbers go into `docs/facts.md` before they go into a section.** Then the sample size is the same in the abstract, the methodology, and the results, and it stays that way through the analysis you rerun in week nine.

**Commit often.** The document is plain text, so `git diff` shows exactly what changed between drafts, and `git log` is most of your AI usage declaration already written.

## Optional: converting PDFs

If your source material is PDFs — lecture slides, papers, scanned handouts — `/ingest` turns them into Markdown the workspace can read and search:

```bash
pip install pypdfium2 pillow
pip install anthropic          # or: openai / google-genai
export ANTHROPIC_API_KEY=...   # or OPENAI_API_KEY / GEMINI_API_KEY
```

It uses whichever key you already have — only that provider's SDK needs installing.

Then, in Claude Code:

```
/ingest ~/Downloads/course-slides/
```

It estimates the cost before spending anything, caches each page as it goes so long runs resume after an interruption, and offers a half-price batch mode for large backlogs. See [the credits](../README.md#credits) for where the approach came from.
