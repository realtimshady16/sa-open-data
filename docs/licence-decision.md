# Licence decision

**Decided 2026-11-15: CC BY 4.0 for the data, MIT for the code.**

Why: this exists to be used by people who will never read a licence — a journalist on deadline,
an honours student, a council official. Attribution-only is the option that produces reuse
rather than correspondence. ODbL (share-alike on the database) was the runner-up and was
rejected knowingly: it buys "improvements stay public" at the cost of some commercial users and
more support questions than this project will ever staff.

Files: `LICENSE` (MIT, covers `scripts/`), `LICENSE-DATA` (CC BY 4.0, covers `datasets/`),
`CITATION.cff`. Release tag: `v0.1.0`.

What follows is the reasoning as written *before* the decision, kept because it is the record of
what the alternatives cost.

---

# Licence options (as considered)

Nothing is licensed yet. Until a `LICENSE` file exists, default copyright applies and nobody may
redistribute this. **Do not treat this repository as reusable until this is decided.**

Two separate choices, because they are two different things:

- **A. The data** (tables, JSON, derived CSVs)
- **B. The code** (`scripts/`)

A third thing is not a licence at all but matters more than either: **a citation file**. People
reuse what they can cite.

---

## A. Data licence — four real options

### Option 1 — CC BY 4.0  ← *recommended*

Attribution only. Anyone may copy, adapt, publish commercially, and build on it, provided they
credit the source.

- **For:** the most widely understood licence among journalists, NGOs and students. Zero
  friction. Compatible with everything downstream except share-alike licences.
- **Against:** gives away the option of forcing improvements back. A consultancy can improve the
  tables and sell them without returning anything.
- **Practical note:** CC licences are written for creative works, not databases. They work, and
  everyone uses them anyway, but they do not speak to database rights specifically.

### Option 2 — ODbL 1.0

Share-alike on the *database*. Anyone publishing a derived database must publish theirs under
ODbL too. Apps built on top can be any licence.

- **For:** improvements stay public. This is what OpenStreetMap and Open Food Facts use, and it
  is the honest licence for a public-good dataset.
- **Against:** scares off some commercial users; complicates mixing with CC BY material; the
  "derived database" boundary confuses people, so you get asked about it.
- **If chosen:** it is a statement of intent, not just a licence — "this stays public."

### Option 3 — PDDL 1.0 or CC0 1.0

Public-domain dedication: no conditions at all.

- **For:** maximum reuse, zero legal reading, ideal for something that should just be
  infrastructure.
- **Against:** nobody is obliged to credit you, which for a preservation project means the copy
  loses its trail. Also: you cannot dedicate what you do not own, and we do not own the
  underlying statistics.

### Option 4 — CC BY-SA 4.0

Attribution plus share-alike on the *content*.

- **For:** the familiar Wikipedia licence; improvements stay open.
- **Against:** share-alike on content rather than database is a poor fit for tabular data, and
  it clashes more often than ODbL does.

---

## B. Code licence — pick one, it is easy

| Licence | Effect | When to choose |
|---|---|---|
| **MIT** ← *recommended* | do anything, keep the notice | smallest possible friction; the scripts are utilities, not products |
| Apache-2.0 | same, plus an explicit patent grant | if you think a company might adopt the fetchers |
| GPL-3.0 | derivatives must ship under GPL | if you want the tooling to stay open, not just the data |

There is no real argument for putting the data and the code under the same licence. Two files:
`LICENSE` (code) and `LICENSE-DATA` (data) is the standard pattern, plus `CITATION.cff`.

---

## C. The claim we actually have

Worth being precise, because it changes what a licence can do:

- **We do not own the statistics.** National Treasury, the Auditor-General, the IEC and
  Statistics South Africa produced them with public money. Facts are not copyrightable.
- **What we own:** the arrangement, the derived tables, the cleaning, the documentation, and the
  scripts.
- **What that means:** a licence here grants rights over *our* contribution. Someone could
  independently fetch the same API and publish the same numbers with no obligation to us — and
  that is correct.
- **One unresolved question:** whether any upstream term attaches to the AGSA or Municipal Money
  responses. Neither states a licence. Under the strict reading adopted in the Mzantsi Vibes
  project, "no licence published" is not permission — it is an absence. This repository records
  the data; publishing a licence over it is a slightly bolder claim than the underlying facts
  support. Worth deciding deliberately rather than by default.

## Recommendation

**CC BY 4.0 for the data, MIT for the code, plus `CITATION.cff`.** Reason: this exists to be
used by people who will never read a licence — a journalist on deadline, an honours student, a
council official. Attribution-only is the option that produces reuse rather than correspondence.
If the intent is instead "this stays public and improvements come back," choose **ODbL** and
accept the extra friction knowingly.

## Also worth adding when it is decided

- `CITATION.cff` — a DOI-able citation block. Zenodo will mint a DOI for a tagged release, which
  is the difference between "a repo" and "a citable dataset" for anyone writing a paper.
- A "how to cite" line in the README.
- A version tag at the point the licence lands (`v0.1.0`), so the licence and the content are
  pinned together.
