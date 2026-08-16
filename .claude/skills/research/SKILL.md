---
name: research
description: Research a topic and save structured findings. Use when the user wants to find papers, search for academic sources, explore a topic, look up literature, find references, or gather evidence. Triggers on "find papers on", "what does the literature say about", "search for sources on", "is there research on".
args: topic to research
context: fork
---

# /research — Find and evaluate sources

Your job is to come back with a small number of real, relevant, high-quality sources and an honest account of how you found them. A long list padded with plausible-looking references is worse than nothing, because every entry has to be checked by hand later.

Read `.claude/CLAUDE.md` and `docs/requirements.md` first so you know what the document is about and what counts as an acceptable source here.

## 1. Check what you already have

Search `resources/` and `docs/research/` before searching the web. Prior sessions may already have covered this topic or an adjacent one. Say what you found and build on it rather than starting over.

## 2. Search

Use several methods. Any one of them alone has a characteristic blind spot.

### Method A — Keyword search, for breadth

Search the open web and the open indexes for the topic. Two habits matter more than the choice of engine:

- **Phrase-search multi-word concepts.** `"learning to rank"` finds the field; `learning to rank` finds sentences about ranking that happen to contain "learning".
- **Search titles when you want precision and full text when you want recall.** Run both and compare.

Vary the vocabulary deliberately. Fields name the same idea differently, and the paper you need may use the term you did not think of.

### Method B — Citation chains through open APIs, for depth

This is the highest-yield method and it should be part of every session. Find one or two strong anchor papers, then walk the citation graph outward in both directions.

**OpenAlex** — best for bulk search, filtering, and metadata. No key required; an email address in `OPENALEX_MAILTO` puts you in the faster polite pool.

```
Search:      https://api.openalex.org/works?search={query}&per_page=25&sort=cited_by_count:desc&mailto={email}
By DOI:      https://api.openalex.org/works/doi:{doi}
Filtered:    https://api.openalex.org/works?filter=default.search:{query},type:article,from_publication_date:2015-01-01&sort=cited_by_count:desc
```

Each work carries `cited_by_api_url` (fetch it for papers citing this one) and `referenced_works` (OpenAlex IDs of what it cites).

**Semantic Scholar** — best for the citation graph itself and for abstracts. Works unauthenticated at about one request per second; `SEMANTIC_SCHOLAR_API_KEY` raises that, sent as the header `x-api-key`.

```
Search:      https://api.semanticscholar.org/graph/v1/paper/search?query={q}&fields=title,authors,year,citationCount,externalIds,venue,abstract&limit=20
By DOI:      https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,authors,year,citationCount,venue,abstract,references,citations
Citing it:   https://api.semanticscholar.org/graph/v1/paper/{id}/citations?fields=title,authors,year,citationCount,venue&limit=50
It cites:    https://api.semanticscholar.org/graph/v1/paper/{id}/references?fields=title,authors,year,citationCount,venue&limit=50
```

**Crossref** for authoritative bibliographic metadata, **Unpaywall** (`https://api.unpaywall.org/v2/{doi}?email={email}`) to find a legal open-access PDF when the publisher version is locked.

**Snowball procedure**: anchor paper → fetch its citations and references → sort by citation count → read the titles → pick the two most promising and repeat. Two levels is usually enough. Note that citation count measures uptake, not correctness, and it penalises anything published in the last two years.

### Method C — Subscription databases through a browser, for quality

Scopus, Web of Science, EBSCO, JSTOR, and ProQuest index peer-reviewed literature with structured metadata and no preprint noise. They sit behind an institutional login, so no API key reaches them. Drive them with the Playwright MCP browser instead.

Check `.claude/rules/research.md` and `.env` for the databases in scope and their proxied URLs (`DB_SCOPUS_URL`, `DB_WEB_OF_SCIENCE_URL`, `DB_EBSCO_URL`, `DB_OTHER_URL`). If only `LIBRARY_PROXY_SUFFIX` is set, construct the URL by appending the suffix to the publisher host, e.g. `www.scopus.com` becomes `www-scopus-com.ez.example.edu`.

**The login flow.** Navigate to the search form. Many proxies pass authentication through automatically. If a login page, institution picker, or SSO screen appears instead:

1. Stop. Do not type anything into any credential field, and do not read the page for stored credentials.
2. Tell the user exactly what is on screen and what to do: sign in themselves in the browser window that is already open, and say when they are through.
3. Wait for them. Do not retry, do not navigate away, do not try another route into the database.
4. When they confirm, take a fresh snapshot and continue from the authenticated page.

The user's credentials are theirs. You never see them, never store them, and never ask for them in chat.

**Searching, once you are in.** The mechanics differ per database, but the pattern holds: choose the field (title/abstract/keywords is usually right, title-only for precision), enter phrase-quoted terms, run several term combinations rather than one, sort by citation count to find what the field has accepted, and read the abstract before recording anything. Follow the "cited by" and "references" links for the same snowball procedure as Method B. Note any per-database syntax quirks in `.claude/rules/research.md` as you learn them, so the next session starts ahead.

## 3. Record each source

- Authors, year, title, venue
- DOI or a resolvable URL — **required**
- Key findings, and the method that produced them
- Which section of the document this supports, and what claim it would back
- Quality tier (below), citation count, and whether it is peer-reviewed
- How you found it: which search, or cited by which paper

## 4. Document the search itself

In the research file, record the databases searched, the exact query strings, roughly how many results you scanned, and the date. This makes the search reproducible in spirit and is often required in the methodology chapter of a literature-heavy document.

## 5. Save

Write to `docs/research/research_<topic>_<YYYY-MM-DD>.md` in the format set by `.claude/rules/research.md`.

## 6. Recommend next steps

Which sources are worth a full summary via `/save-material`, which anchors are worth another round of snowballing, what you could not find, and what remains unanswered.

## Quality bar

**Reject unless all three hold:**

- The source exists, confirmed in at least one index or on the publisher's site. Models generate convincing citations to papers that were never written. Verify before you write it down.
- It has a DOI or a resolvable URL. Without one, mark it unverified and do not recommend it.
- Its publication year is not in the future.

**Tier every source you keep:**

- **Tier 1** — peer-reviewed journal or major conference. Prefer these.
- **Tier 2** — credible practitioner or preprint: well-cited arXiv work, engineering publications from organisations with real data. Useful, but say plainly that they are not peer-reviewed.
- **Tier 3** — workshop papers, minor venues, lightly cited preprints. Use to fill a specific gap Tiers 1 and 2 leave open.
- **Tier 4** — no DOI, working papers, repository-only uploads, popular press. Flag, do not build an argument on it.

Be honest about the limits of the search. Ten verified sources with an accurate account of what was not covered beats forty of uncertain provenance.
