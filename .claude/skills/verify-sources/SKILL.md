---
name: verify-sources
description: Verify that citations exist, resolve, and are what they claim to be. Use when the user wants to check citations, audit a reference list, confirm papers are real, or quality-check sources. Triggers on "verify sources", "check citations", "are these papers real", "audit references", "check my bibliography".
args: file path (e.g. sections/references.md) or a list of citations
context: fork
---

# /verify-sources — Check every citation

Language models produce citations that look correct and do not exist. So do hurried authors working from memory. This skill checks each one against an index and reports what it could not confirm.

## Input

A file path (a reference list, a research log, or a section) or a list of citations. If given a section, extract the in-text citations first.

## For each citation

### 1. Existence

Try in this order and stop at the first confirmation:

- **OpenAlex** — `https://api.openalex.org/works?search={url_encoded_title}&per_page=5&mailto={email}`, or `https://api.openalex.org/works/doi:{doi}` when a DOI is given.
- **Semantic Scholar** — `https://api.semanticscholar.org/graph/v1/paper/search?query={title}&fields=title,authors,year,externalIds,venue,citationCount&limit=5` (header `x-api-key`).
- **Crossref** — `https://api.crossref.org/works?query.bibliographic={citation}&rows=5&mailto={email}`.
- **Web search** as a last resort, against the publisher's own site.

**VERIFIED** requires the title, the first author, and the year to match. A one-year discrepancy is acceptable only for a preprint that was later published, and note it when it happens. A near-match on title with different authors is a *different paper* — the original is unverified.

### 2. Metadata

For verified sources, record the DOI, the actual venue, the publication year, the citation count, the type, and whether an open-access copy exists.

### 3. Tier

Tier 1 peer-reviewed journal or major conference; Tier 2 credible practitioner source or well-cited preprint; Tier 3 workshop or minor venue; Tier 4 unverifiable, working paper, or popular press.

### 4. Accuracy of use

Where the input is a section rather than a bare list, also check that the citation supports the sentence attached to it. Two failure modes matter and both are common: a real paper cited for a claim it does not make, and a real paper cited for a claim it makes about a different population or setting. Flag either, quoting the sentence.

## Output

Save to `docs/research/verification_<description>_<YYYY-MM-DD>.md`:

```markdown
# Source Verification: <description>
Date: <YYYY-MM-DD>
Input: <what was checked>

## Summary
Checked: X · Verified: X · Unverified: X · Tier 1: X · Tier 2: X · Tier 3: X · Tier 4: X

## Verified
| # | Citation | DOI | Venue | Cited by | Tier | Used in |
|---|----------|-----|-------|---------:|------|---------|

## Could not verify — action required
| # | Citation as given | What was searched | What was found instead |
|---|-------------------|-------------------|------------------------|

## Misattributed or overstated
| # | Citation | Sentence in the document | What the source actually says |
|---|----------|--------------------------|-------------------------------|

## Recommendation
<Which entries to remove, replace, or re-check by hand.>
```

## Rules

- Never mark a citation verified because it looks plausible. Search.
- Be most sceptical of very recent work, of sources with no DOI, and of anything the author does not remember reading.
- Check at least two indexes before declaring a paper non-existent — coverage gaps are real, especially for books, theses, and non-English work.
- Report failures plainly. An unverified citation left in a submitted document is an integrity problem, not a formatting one.
