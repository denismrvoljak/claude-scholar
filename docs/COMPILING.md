# Reading and compiling

Two practical questions this setup doesn't answer on its own: how you read a hundred thousand characters of markdown spread across eight files while you're writing it, and how it becomes the document you actually submit.

## Reading: open the folder in Obsidian

[Obsidian](https://obsidian.md) opens any folder of markdown files as a vault, with no import step and no lock-in — the files stay exactly as they are on disk, and Claude Code keeps editing them normally. Point it at the project root and you get:

- **Every section, source summary, and research log in one searchable place.** Searching across `sections/` and `resources/` at once is how you find the paper you half-remember reading in month two.
- **An outline view** for navigating a 28,000-character methodology chapter without scrolling.
- **Rendered LaTeX.** `$...$` and `$$...$$` display as real equations. This matters most for `/ingest` output: converted lecture slides and papers come back with their maths intact, and in Obsidian they read as notes rather than as source.
- **Working links between files**, so a `[[wikilink]]` or a relative markdown link from a section to a source summary is one click.

`.obsidian/` is already in `.gitignore`, so your workspace layout stays yours and out of the repository.

Nothing here depends on Obsidian. Any markdown editor works, and so does reading the files on GitHub. It is just the option that makes a long project navigable.

## Compiling: do it once, by hand, near the end

**The recommendation is to not automate this.** Write in markdown for the months of drafting, and convert to Word once, when the content is close to final.

That is not a limitation of the setup, it is what the work is actually like. The Word-side tasks are the ones a converter cannot do for you:

- Equations have to become native Word equation objects, not images or pasted Unicode (see `.claude/rules/typography.md` for why).
- Cross-references to sections, figures, and tables need to be Word's live references so the numbering survives an edit.
- Figures and tables need captions attached in Word, and a generated table of contents.
- Page numbering has to switch from roman to arabic at the introduction.

A build script gets you a rough `.docx` and leaves every one of those still to do by hand. Doing the conversion once, deliberately, at the point where the content has stopped moving, is less total work than maintaining a pipeline you then have to correct anyway.

Convert whichever way suits you: paste section by section, run the files through Pandoc as a starting point, or open the markdown in a converter and clean up. The output is a starting draft either way, and the formatting pass that follows is the real job.

## What this means for the character count

`/status` counts characters with `wc -m` on the markdown source. That number is a **planning estimate**, and it is wrong in two directions at once:

- It **overcounts** by including markdown syntax — `##`, `**`, link brackets, comment lines — none of which exist in the compiled document.
- It **undercounts** by ignoring the rule most institutions apply, where a figure pasted as an image counts a fixed number of characters regardless of size (commonly 800 each).

Which way it nets out depends on how figure-heavy the document is. Treat the in-repo count as the number that tells you whether a chapter is drifting over budget while there is still time to do something about it. That is what it is good for, and it is genuinely useful for that.

**The authoritative count comes from Word, after compiling**, using your institution's own exclusion rules — normally front page, table of contents, bibliography, and appendices excluded. That is the number that goes on the front page, and the only one worth defending.

So check it for real at least once well before the deadline, not on submission day. Discovering you are four thousand characters over with a week left is a manageable edit. Discovering it the night before is not.
