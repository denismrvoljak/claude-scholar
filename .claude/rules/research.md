# Research rules

> **Template file.** `/onboard` fills in the databases you actually have access to.

## Where to search

**Open, no credentials needed**

| Source | Good for |
|--------|----------|
| OpenAlex | Bulk search, filtering, metadata, citation graph in both directions |
| Semantic Scholar | Citation chains, abstracts, influence data |
| Crossref | Authoritative bibliographic records |
| Unpaywall | Legal open-access copies of paywalled work by DOI |
| arXiv, SSRN, RePEc | Preprints, field-dependent |

**Institutional, credentials needed**

<The databases your library subscribes to and you actually use. For each: what it is good for, its proxied search URL, and any syntax quirks worth remembering.>

| Database | Good for | URL |
|----------|----------|-----|
| <Scopus> | <broad peer-reviewed coverage, citation counts> | `<proxied URL>` |
| <Web of Science> | <second opinion, older coverage> | `<proxied URL>` |
| <EBSCO Business Source> | <business, management, marketing> | `<proxied URL>` |

Institutional databases are reached through a browser, not an API. `/research` opens the search form and pauses for you to log in when a login screen appears. Credentials are never entered by the agent.

## Search technique

- Phrase-quote multi-word concepts. Unquoted terms match sentences that happen to contain the words.
- Run several vocabulary variants. Fields name the same idea differently, and the term you did not think of is where the good paper is.
- Sort by citation count to find what a field has accepted, but remember that recent work is structurally penalised by that sort and that uptake is not correctness.
- Snowball from anchors: forward citations to find what came after, backward references to find the foundations. Two levels is usually enough.
- Record the exact query strings. A literature-heavy document often has to report its search protocol, and reconstructing it afterwards is guesswork.

## Research logs

`docs/research/research_<topic>_<YYYY-MM-DD>.md`:

```markdown
# Research: <topic>
Date: <YYYY-MM-DD>

## Question
<What this session was trying to find out.>

## Search protocol
- Databases and indexes searched
- Exact query strings
- Results scanned per query
- Filters applied (years, document types, fields)

## Sources found
### <Title>
- Authors, year, venue, DOI
- What it argues, and on what evidence
- Relevance: which section, which claim
- Tier, citation count, peer-reviewed
- Found via: <query, or cited by X>

## What was not found
<Gaps in the literature, or gaps in the search. Say which.>

## Next
- Worth a full summary via /save-material: ...
- Worth snowballing: ...
- Still open: ...
```

## Resource summaries

- `resources/theoretical/<firstauthor_year>.md` — academic sources
- `resources/practical/<descriptive_name>.md` — domain, company, dataset, tool, and standards material

Format in `.claude/skills/save-material/SKILL.md`.

## Source quality

Required of every source that enters the document: it exists and has been confirmed in an index, it has a DOI or resolvable URL, and its publication year is not in the future.

Tiers: peer-reviewed journal or major conference; credible practitioner or well-cited preprint; workshop or minor venue; unverifiable or grey literature. Build arguments on the first two. Use the third to fill specific gaps. Flag the fourth and do not rest a claim on it.

Prefer fewer verified sources to more uncertain ones. Every unverified citation is work deferred, not work saved.
