# Writing rules

> **Template file.** `/onboard` rewrites this for your project. Everything in angle brackets is a placeholder. After onboarding, this file is yours: every correction you or your supervisor ever make belongs here, so it never has to be made twice.

## Voice and register

- **Person**: <first person singular / first person plural / impersonal>. <Reflective reports usually take "I". Empirical theses in most business and engineering programmes take the impersonal or the first person plural. Check your institution's sample work.>
- **Tense**: present for established knowledge and for what the document itself does, past for what was done and found.
- Active voice wherever it does not force an awkward construction.
- Formal, but not inflated. The goal is a reader who follows the argument without effort, not one who is impressed by the sentences.
- Paragraphs of three to five sentences, each making one point.
- No contractions, no colloquialisms, no rhetorical questions.

## Evidence

Every substantive claim is backed by a citation or by the document's own analysis. A sentence that asserts something about the world without either is a defect, not a stylistic choice.

Match the strength of the claim to the strength of the evidence. "X increases Y" needs a causal design. "X is associated with Y" is what a correlation supports. "X may contribute to Y" is what a single case study supports.

## Citations

- **Style**: <Harvard / APA 7 / IEEE / Vancouver / Chicago>. One style, applied everywhere.
- In-text: <(Author, Year)> or <Author (Year)>.
- Multiple authors: <(Author et al., Year)> from <N> authors onward.
- Several sources at once: <(Author, Year; Author, Year)>.
- Direct quotation: include the page number. Quote sparingly, and only when the wording itself is the point.
- <Footnotes for citation are forbidden / permitted.>
- Every cited work appears in the reference list, and every entry in the reference list is cited.

## Punctuation and formatting conventions

- **Em dashes**: <permitted / avoid>. <If avoided: restructure with commas, colons, parentheses, or a second sentence.>
- **Semicolons**: <permitted / avoid in prose>. <If avoided: keep them only inside multi-citation parentheses and in table cells.>
- **Numbers**: <spell out below ten, numerals from ten upward>. Always numerals with units and in results.
- **Decimal separator**: <. / ,>. **Thousands separator**: <, / space / none>.
- **Dates**: <format>.
- **Acronyms**: define on first use in the body, then use the acronym consistently. Do not redefine in later chapters. Every acronym also appears in the abbreviations list if the document has one.

## Terminology

One concept, one term, everywhere. Variation reads as a new concept and costs the reader.

| Concept | Use | Do not use |
|---------|-----|------------|
| <concept> | <preferred term, exact form> | <variants that are now forbidden> |

Add a row every time you catch yourself using two words for one thing.

## Banned words and constructions

Words that add length without adding meaning, or that a supervisor has objected to. Build this list from real feedback rather than from a generic style guide.

| Banned | Use instead | Source |
|--------|-------------|--------|
| leverage | use, draw on | generic |
| utilise | use | generic |
| seamless, robust, powerful, scalable | name the property concretely, with a number where one exists | generic |
| holistic, synergy, actionable, streamline | plain description of what is meant | generic |
| in order to | to | generic |
| very, really, quite | delete | generic |
| <supervisor's objection> | <substitute> | <supervisor, date> |

Beyond individual words, three constructions to avoid:

**Vague abstraction standing in for a fact.** "Better performance", "improved reliability", "significant scale" — name the metric and the number, or delete the sentence.

**A category label where the contents belong.** A heading or table row called "Operational considerations" tells the reader nothing. Say what is actually in it.

**A counted list with no list.** "There are three reasons for this" followed by two, or by none, is a promise the reader notices being broken. Enumerate them or drop the count.

## Repetition

Each explanation lives in exactly one place. Later sections refer back to it in a clause ("as established in Section 3.2") rather than restating it. Repetition is expensive in a document with a character limit and it reads as padding to an examiner.

## Cross-references

Refer by number: "Section 3.2", "Figure 4", "Table 2". Before keeping a forward reference, read the target and confirm it delivers what the reference promises.

## Pre-flight checks

`/write` runs this block against every file it edits and rewrites the hits. `/review` reports them with line numbers. Rebuild it from the banned list above whenever that list grows.

```bash
grep -Ein "leverag|utilis|seamless|robust|scalable|powerful|holistic|synergy|actionable|streamline|in order to" sections/<file>.md
grep -Ein "very |really |quite " sections/<file>.md
grep -En "three reasons|four reasons|five categories|several |various |a number of " sections/<file>.md
grep -En "significant" sections/<file>.md   # statistical claim, or filler? check each
```

<Add project-specific greps here: forbidden terminology variants, phrasings a supervisor objected to, claims that were corrected once and must not reappear.>
