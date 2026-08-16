# Two projects this came from

claude-scholar was extracted from two real pieces of academic work with very different shapes. The differences between them are why the setup is built around a profile plus an interview rather than a fixed template.

Neither project's content is included here. What is described is how the workspace was configured, and what each configuration turned out to be worth.

---

## Project A — an empirical master thesis

A business and IT master thesis at a Danish university, built around a case company: replacing a rule-based ranking system with a predictive model, evaluated first offline and then in a live experiment. Roughly 132,000 characters, six chapters, a hard limit counted including spaces, with front matter, bibliography, and appendices excluded.

**Configured for it**

- Chapter budgets summing to the limit, with the analysis chapter given the largest share because the assessment criteria weighted it most.
- A facts file that grew to several hundred lines and became the most consulted file in the project. Two data extracts taken at different dates had to be kept apart, so each was given a name and a date, and every section was checked against them. Conflating them would have produced an error running through the whole results chapter.
- A banned-phrase list built entirely from supervisor comments and the author's own reactions to earlier drafts, with a grep block that the drafting command ran on itself.
- A deployment-gate rule recording the exact thresholds used, because an early draft had described them incorrectly and the corrected version had to stick.
- Institutional database access through the library proxy, used mainly for the literature review.

**What earned its keep**

The facts file, by a distance. Second was writing supervisor feedback into the rules rather than answering it once: terminology decisions made in April were still being enforced in August without anyone remembering them.

**What was learned the hard way**

An early version of the rules said "be concise". It did nothing. Replacing it with a specific list of banned words, each with the substitute and the person who objected, changed the drafts immediately. Vague rules are decoration.

---

## Project B — an internship report

A reflective report on founding a startup during an incubator programme, at the same faculty but a different genre entirely: about 57,600 characters, structured around three learning goals rather than research questions, written in the first person, with theory serving reflection rather than the reverse. It was a third attempt, which made prior feedback the highest-authority document in the project.

**Configured for it**

- A structure where each learning goal is self-contained: theory, then method, then findings, then reflection. The supervisor had asked for exactly this, so it went into the structure rules verbatim.
- A rule that every theory mention must attach to a specific experience in the same paragraph. The first attempt had failed partly for having theory that sat in its own chapter and never touched the practice.
- A much longer banned-phrase list than Project A, because the register was less forgiving: business idioms describing one's own actions, words carrying different meanings in different places, and any term a lay reader could not follow, since the exam required explaining the work in lay terms.
- A prior-feedback file treated as a checkable requirement, with the review command verifying each point had been addressed rather than merely discussed.

**What earned its keep**

Turning examiner feedback into a checklist the review command tested against. Two failed attempts had each addressed some feedback and quietly dropped the rest.

**What was learned the hard way**

The two projects wanted opposite things from the same setting. The thesis wanted an impersonal voice and theory as scaffolding; the report wanted "I" and theory as a lens on experience. Any template that fixes this in advance is wrong for one of them, which is why `/onboard` asks instead of assuming, and why the sample-analysis step exists: the fastest way to learn a genre's conventions is to read one instance of it closely.

---

## What generalises

**Character budgets change what gets written.** Knowing that a chapter has 18,000 characters, and that a pasted figure costs 800 of them, changes the plan rather than the edit. Discovering the limit at the end means cutting the analysis to fit the introduction.

**A single source of truth is worth more than better prose.** The errors that cost marks in empirical work are inconsistencies, not infelicities.

**Rules accumulate; conversations do not.** Every correction that goes into a rules file is enforced forever. Every correction that stays in a chat is made again next week.

**The institution's own documents are the specification.** Both projects were graded against published criteria that most students never read closely. Extracting them into a file the review commands check against turns a vague sense of quality into something checkable.
