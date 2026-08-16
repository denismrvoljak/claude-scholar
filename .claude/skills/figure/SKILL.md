---
name: figure
description: Create a publication-quality figure as a self-contained HTML file. Use when the user wants a diagram, chart, visualisation, table, flowchart, architecture overview, pipeline diagram, or any visual element for the document. Also triggers on "draw", "visualise", "make a figure showing", "create a table of", or a request to illustrate a concept, data flow, or design.
args: description of the figure
allowed-tools: Read, Write, Edit, Bash, Glob
---

# /figure — Build a figure

## Output

A single self-contained HTML file in `figures/`, with an inline `<style>` block and no build step. Chart.js and Mermaid are permitted where they genuinely help; nothing else. The file is opened in a browser, screenshotted or printed, and pasted into the document.

Follow `.claude/rules/figures.md` — it holds this project's palette, typography, and conventions, and it is the authority where this skill and it disagree.

## Before you draw

1. **Know the cost.** In most institutions a pasted figure counts a fixed number of characters against the length limit regardless of size, while a table typed as text counts its actual characters. Check `docs/requirements.md`. This decides whether a small table should be a figure or prose, and it means a figure has to earn its place.
2. **Check `figures/`** for the existing numbering and for a figure that already makes this point.
3. **Settle on one message.** A figure carries one idea. If the description contains two, make two figures or drop one.

## Building it

- Diagram, flow, or architecture → Mermaid, or hand-built HTML and CSS where the layout matters.
- Chart → Chart.js, or plain HTML and CSS when the data is small enough that a library adds nothing.
- Table → an HTML table, right-aligned on numeric columns, units in the header.
- Captions and explanation live in the section prose, not inside the figure. The figure carries labels only.

Constraints that apply to every figure:

- **Readable in greyscale.** Never encode meaning in colour alone. Add labels, patterns, or markers.
- **Readable in print.** Nothing below roughly 12px equivalent.
- **Honest axes.** Baselines at zero for bar charts unless there is a stated reason otherwise, and any truncated axis marked as truncated.
- **Uncertainty shown** where it exists. A point estimate drawn without its interval overstates what the data supports.
- Consistent with the other figures in `figures/`. The set should look like one hand made it.

## After

Report the figure number, a caption ready for the prose, the file path, and the character cost against the budget.
