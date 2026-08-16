---
name: save-material
description: Fetch a paper or web resource and save it as a structured markdown summary in the project resources. Use when the user shares a URL, DOI, paper title, or reference and wants it saved. Triggers on "save this paper", "add this source", "download and summarise", "store this reference", or when a link to a paper or technical resource is pasted.
args: URL, DOI, or paper identifier
context: fork
---

# /save-material — File a source properly

## Steps

1. **Resolve the source.** Fetch the URL, or look the paper up by DOI or title through OpenAlex, Semantic Scholar, or Crossref. If the publisher version is paywalled, try Unpaywall (`https://api.unpaywall.org/v2/{doi}?email={email}`) for a legal open-access copy. If you cannot reach the full text, say so and summarise from the abstract and metadata, marking clearly which parts of your summary rest on the abstract alone.

2. **Check for duplicates.** Search `resources/` for the same work before creating a file. If it exists, update it rather than adding a second copy.

3. **Choose the destination.**
   - Academic work → `resources/theoretical/<firstauthor_year>.md`
   - Domain, company, dataset, tool, or standards documentation → `resources/practical/<descriptive_name>.md`

4. **Write the summary.**

```markdown
# <Title>

## Metadata
- **Authors**:
- **Year**:
- **Venue**:
- **DOI / URL**:
- **Type**: journal article | conference paper | preprint | report | documentation | blog post
- **Peer-reviewed**: yes | no
- **Citation count** (as of <date>):
- **Access**: open | paywalled | read via institutional access

## What it argues
<The main contribution in a few sentences, in plain terms.>

## Method
<How the evidence was produced, and on what data or cases. Note the sample and the setting — this is what determines whether the finding transfers.>

## Findings relevant here
<Only what bears on this project, with page numbers where you would want to quote.>

## How this project uses it
- **Section(s)**:
- **Claim it supports**:
- **Limits**: <where it does not apply, or where its setting differs from this project's>

## Contradicts or complicates
<Sources in this project that it disagrees with, if any. This field is the reason the summary is worth writing.>

## Reference entry
<Formatted in the project's citation style, ready to paste.>
```

5. **Report** what was saved, which sections it serves, and whether it conflicts with anything already in `resources/`.

Do not overstate a source. If the paper is tangential, say it is tangential.
