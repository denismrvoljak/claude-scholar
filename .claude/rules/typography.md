# Typography and formatting

> **Template file.** If your institution supplies a template or mandates a format, that overrides everything here and `/onboard` should record it instead. Most do not, and then a consistent house style is worth fixing once rather than negotiating with every export.

The markdown in `sections/` is the source. This file governs the compiled document (usually Word or PDF) that is actually submitted.

## Page

- A4, 2.5 cm margins all round
- Line spacing 1.5, paragraph spacing 0 pt before and 6 pt after
- Left-aligned, ragged right. Full justification produces uneven word spacing that long technical terms make worse.
- Page numbers bottom centre: lowercase roman in the front matter, arabic from the introduction onward

## Fonts

| Role | Font | Fallbacks | Size |
|------|------|-----------|------|
| Body | Charter | EB Garamond, Times New Roman | 11 pt |
| Headings | Inter | Source Sans, Helvetica Neue, Arial | see below |
| Code, formulas in prose, variable names | JetBrains Mono | Menlo, Consolas, Courier New | 10 pt |
| Captions | Inter italic | as headings | 9 pt |

Serif body with sans-serif headings is the standard academic pairing and it fails gracefully. Verify the fallbacks by opening the file on a machine without your fonts installed before you submit.

| Level | Size | Numbering |
|-------|------|-----------|
| Chapter | 18 pt bold | `1` |
| Section | 14 pt bold | `1.1` |
| Subsection | 12 pt bold | `1.1.1` |
| Minor | 11 pt bold italic | unnumbered, sparingly |

No all caps, no underline. 12 pt above a heading, 6 pt below.

## Colour

Body text and headings stay near-monochrome. Colour belongs in figures, links, and chart accents, drawn from the palette in `figures.md`. Every figure must still read in greyscale.

## Formulas

Native equation objects (Word: Insert → Equation, Alt+=), never images and never Unicode approximations. Images of formulas do not scale, fail accessibility checks, and in institutions that count pasted images they cost characters.

- Inline maths flows with the paragraph; display maths sits on its own centred line, numbered at the right margin.
- Variables in prose use the equation font so notation matches. Vectors bold italic, matrices bold upright capitals, scalars italic.
- Every symbol is defined on first use and listed in the notation section.

## Tables and code

Tables: bold header row on a light fill with a single rule beneath, no vertical rules, numeric columns right-aligned, units in the header. Caption above, `Table N. <description>`.

Code and query blocks: monospace inside a single-cell shaded table, no syntax highlighting. Anything longer than about fifteen lines belongs in an appendix.

## Figures and quotations

Figures: caption below, `Figure N. <description>`, source line beneath if adapted.

Quotations: inline in double quotes up to about forty words, with a page number. Longer quotations are indented on both sides, without quote marks, at 10 pt and single spacing. If you are quoting at length, check that paraphrase would not serve better.

## Before you export

- All formulas are equation objects.
- Every figure and table has a caption and is referenced in the prose.
- All cross-references updated (in Word: select all, then F9).
- Page numbering switches correctly from roman to arabic.
- Character or word count matches what is printed on the front page, counted under the institution's exclusion rules.
- Reference list checked with `/verify-sources`.
- The PDF opens correctly on a machine that is not yours.
