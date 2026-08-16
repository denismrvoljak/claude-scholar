# Figure rules

> **Template file.** `/onboard` sets the palette and any institutional constraints.

## General

- Numbered consecutively across the whole document.
- Captions and explanation live in the prose, not inside the figure file. The figure carries labels only.
- Referred to at least once in the text. A figure nothing points at should not exist.
- Source line beneath the caption if adapted from someone else's work.
- Saved to `figures/` with a descriptive filename.
- **Cost**: <a pasted image counts N characters against the limit regardless of size; a table typed as text counts its actual characters>. Check `docs/requirements.md` and decide accordingly which form each visual takes.

## Stack

A single self-contained HTML file with an inline `<style>` block, no build step, and no external font loading. Chart.js and Mermaid are permitted where they earn their place. Nothing else.

## Palette

<Replace with the project's colours. Neutral defaults below, chosen to remain distinguishable in greyscale.>

```css
--text:      #1A1A1A;   /* body text, headings   */
--text-dim:  #6B7280;   /* secondary labels      */
--bg:        #F5F5F3;   /* page background       */
--surface:   #FFFFFF;   /* cards, plot areas     */
--accent:    #35607A;   /* neutral emphasis      */
--positive:  #1F6F43;   /* increase, success     */
--negative:  #8C3115;   /* decrease, failure     */
--caution:   #8A6A12;   /* uncertainty, warning  */
```

Semantic use only: positive for up and good, negative for down and bad, caution for uncertain, accent for neutral emphasis. Never encode meaning in colour alone — add a label, a pattern, or a marker, so the figure survives greyscale printing and colour-blind readers.

## Typography

Serif for headings, sans-serif for body and UI text, monospace for labels and code. Use local fallback stacks so the figure renders identically without network access:

```css
--font-serif: "Iowan Old Style", Palatino, Georgia, serif;
--font-sans:  Inter, "Helvetica Neue", Helvetica, Arial, sans-serif;
--font-mono:  "SFMono-Regular", Menlo, Consolas, monospace;
```

Nothing below roughly 12px equivalent. Figures are read on paper as often as on screen.

## Honesty

- Bar charts start at zero. Any truncated axis is marked as truncated.
- Uncertainty is shown where it exists. A point estimate without its interval overstates the evidence.
- Axis labels carry units. Sample sizes appear on the figure or in the caption.
- The visual encoding matches the claim: no dual axes chosen to make two series appear to move together, no area used to encode a linear quantity.

## Layout

Cards on a tinted background, subtle borders rather than heavy shadows, rounded corners. Right-align numeric table columns. For multi-column card layouts use CSS subgrid so that headings and labels align across cards; flexbox alone lets each card size itself and the rows drift.

For connectors and loops between elements, measure real positions with `getBoundingClientRect` and draw SVG paths. Percentage-positioned decoration breaks at the first viewport change.

One idea per figure. If a description contains two, it is two figures.
