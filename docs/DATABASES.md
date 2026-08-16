# Research database access

Two tiers of source discovery. Use both: they fail differently, and the overlap is smaller than you would expect.

---

## Tier 1 — Open APIs

No institution required, no login, and fast enough to snowball through a citation network in a single session. This is where most of the work happens.

### OpenAlex

An open index of roughly 250 million scholarly works, with references and citations resolved into a graph. No key required. Putting an email in `OPENALEX_MAILTO` places you in the "polite pool", which is faster and more reliable.

```
Search             https://api.openalex.org/works?search={query}&per_page=25&sort=cited_by_count:desc&mailto={email}
By DOI             https://api.openalex.org/works/doi:{doi}
Filtered search    https://api.openalex.org/works?filter=default.search:{q},type:article,from_publication_date:2015-01-01
Author's works     https://api.openalex.org/works?filter=author.id:{id}
```

Each work object carries `cited_by_api_url` — fetch it to get everything citing this paper — and `referenced_works`, the list of works it cites. Those two fields are the whole snowball method.

### Semantic Scholar

Better abstracts and a cleaner citation-graph API. Works unauthenticated at about one request per second; a free key raises the limit and is worth requesting if you plan long sessions. Sent as the header `x-api-key`.

```
Search       https://api.semanticscholar.org/graph/v1/paper/search?query={q}&fields=title,authors,year,citationCount,externalIds,venue,abstract&limit=20
By DOI       https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,authors,year,venue,abstract,references,citations
Citations    https://api.semanticscholar.org/graph/v1/paper/{id}/citations?fields=title,authors,year,citationCount,venue&limit=50
References   https://api.semanticscholar.org/graph/v1/paper/{id}/references?fields=title,authors,year,citationCount,venue&limit=50
```

### Crossref and Unpaywall

Crossref holds the authoritative record for anything with a DOI, which makes it the best final check on a reference list. Unpaywall takes a DOI and returns a legal open-access copy where one exists:

```
https://api.unpaywall.org/v2/{doi}?email={your_email}
```

Between Unpaywall and the author's own institutional repository, a large share of paywalled literature is legally readable without a subscription.

### Why the citation graph matters more than keyword search

Keyword search finds papers that use your vocabulary. The literature that matters most often does not: it is in an adjacent field, published before your terminology settled, or naming the same construct differently. Citation chains route around vocabulary entirely. Find one paper that is unambiguously about your problem, then read what it cites and who cites it, and the field's actual structure appears in about twenty minutes.

---

## Tier 2 — Your library's subscription databases

Scopus, Web of Science, EBSCO Business Source, JSTOR, ProQuest, and the publisher platforms index peer-reviewed literature with curated metadata and no preprint noise. They are behind an institutional login, so no API key will reach them.

### How it works here

`/research` opens the database in a real browser through the [Playwright MCP server](https://github.com/microsoft/playwright-mcp) and searches it the way you would. When it hits a login screen, it stops and asks you to sign in yourself in the browser window that is already open, then continues from the authenticated page.

The division of labour is deliberate: **you handle the credentials, the agent handles the searching.** It does not type into credential fields, does not read stored passwords, and does not ask for your login in chat. Institutional accounts usually control far more than a library subscription, and a research tool has no business holding one.

### Setup

```bash
claude mcp add playwright npx @playwright/mcp@latest
```

Then find your proxy pattern. Open any database through your library portal and look at the URL. Most academic libraries use EZproxy, which rewrites the publisher's hostname:

```
www.scopus.com  →  www-scopus-com.ez.statsbiblioteket.dk       (Aarhus University)
www.scopus.com  →  www-scopus-com.ezproxy.example.edu          (typical EZproxy)
```

The suffix is what you save in `.env`:

```bash
LIBRARY_PROXY_SUFFIX=.ezproxy.example.edu
DB_SCOPUS_URL=https://www-scopus-com.ezproxy.example.edu/search/form.uri
DB_WEB_OF_SCIENCE_URL=https://www-webofscience-com.ezproxy.example.edu/wos/woscc/basic-search
DB_EBSCO_URL=https://web-p-ebscohost-com.ezproxy.example.edu/ehost/search/advanced
```

Some institutions use VPN or IP-based access instead of a rewriting proxy. Then the plain publisher URL works while you are connected, and `LIBRARY_PROXY_SUFFIX` stays empty.

### Searching them well

The interfaces differ, the technique does not:

- Search the title, abstract, and keywords field by default. Narrow to title-only when you are drowning in results, widen to full text when you are getting none.
- Phrase-quote every multi-word concept.
- Run four or five term combinations rather than one perfect query. Recall comes from variation, not from cleverness.
- Sort by citation count to see what the field has accepted, then sort by date to see what has happened since.
- Use "cited by" and "references" links for the same snowball procedure as Tier 1.
- Note the syntax quirks of each database in `.claude/rules/research.md` as you learn them. Proximity operators and wildcard characters differ, and the difference is invisible until a search silently returns nothing.

### If a database blocks automation

Some publishers detect and block automated browsing, and some licences forbid systematic downloading. Respect both. Where a database resists, use it by hand and paste the results in, or take the DOIs and pull the metadata through Tier 1. Do not try to work around a block: a licence violation can cost an institution its subscription.

---

## What each tier is for

| | Open APIs | Subscription databases |
|---|---|---|
| Coverage | Very broad, includes preprints and grey literature | Curated, peer-reviewed, field-specific |
| Metadata quality | Good, occasionally messy | Consistent and structured |
| Citation graph | Excellent, both directions, free | Good, and often more accurate |
| Speed | Seconds | Minutes, with a browser in the loop |
| Best for | Snowballing, verification, bulk screening | Systematic search, business and management literature, anything where a peer-review filter matters |

Start in Tier 1 to map the field cheaply. Move to Tier 2 when you need a defensible systematic search, or when the field's literature is in journals the open indexes cover badly.
