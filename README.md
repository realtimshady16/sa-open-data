# SA open data — a preserved copy

[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey)](LICENSE-DATA)
[![Code: MIT](https://img.shields.io/badge/code-MIT-blue)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24241806.svg)](https://doi.org/10.5281/zenodo.24241806)

A small, verifiable archive of South African public datasets, captured **2026-11-09 to
2026-11-10** while working on local-government politics and party performance. Published here
for one reason: **none of these sources is preserved anywhere else, and two of them are
scheduled to disappear.**

This is not a data portal and it is not maintained as a service. It is a record: here is what
the data said, here is when it was taken, here is the checksum, here is the script that took
it. You can reproduce every byte.

## Why this exists

The 2026 public record of South African local government has three legs:

| Source | Publisher | Archive status (checked 2026-11-15) |
|---|---|---|
| Municipal Money | National Treasury / OpenUp | live and stable; no bulk preservation needed |
| AGSA MFMA audit outcomes | Auditor-General | **year-stamped site** (`mfma-2025`). Wayback holds **363 URLs** — the shell plus 4 API endpoints — but **none of the 257 per-municipality opinion responses**. `mfma-2026` does not yet resolve. See `docs/archive-audit.md` |
| IEC council results | Electoral Commission | 1,042 Wayback captures from 2026, but **zero under `api/`** — and the captures are mostly Cloudflare challenge pages, i.e. the bot defence rather than the results. The `/api/v1/` path returned **404 on reprobe** |
| Stats SA P9115 | Statistics South Africa | live and **well archived** — unit-data workbooks captured 2019–2024 |

So the AGSA audit sweep (257 auditees × 8 periods) and the IEC council compositions exist in
two places: the state's servers, and here.

## What is in here

```
datasets/
  municipal-money/        292 municipal profiles, financial indicators, geography   (20 MB)
  agsa-audit-outcomes/    257 auditees × 8 periods = 2,056 audit opinions          (888 KB)
  iec-councils/           council composition after the 2016 and 2021 elections     (420 KB)
  stats-sa-p9115/         free basic services per municipality (P9115 Table 12)     (120 KB)
  crosswalk/              292 rows × 5 sources' keys — the join, not a matching job  (60 KB)
scripts/                  the fetchers and derivations, unmodified
tools/build_site.py       the static view: one page per municipality (output ignored)
docs/provenance.md        publisher, endpoint, capture date, live status, archive status
docs/method.md            how each dataset was obtained, and where it is fragile
docs/coverage-and-caveats.md   what the numbers are NOT
docs/archive-audit.md     what the Internet Archive actually holds of these sources
docs/licence-decision.md  which licences were chosen and why
SOURCES.md                a ledger: every SA source we know of, and whether we hold it
MANIFEST.json             size, sha256, row/record counts, source URL per data file
CHANGELOG.md              what changed in each release
```

## The static view

`tools/build_site.py` renders one HTML page per municipality — finance, audit history, council
composition, free basic services, joined through the crosswalk — plus an index, with no server
and no network at build time. It writes to `site/`, which is git-ignored: **the site is a view
of the data, not part of the record.** Rebuild it any time:

```bash
python3 tools/build_site.py && python3 -m http.server -d site 8000
```

It is published at **https://realtimshady16.github.io/sa-open-data/** by
`.github/workflows/pages.yml`, which runs the same command on every push that touches
`datasets/` or the generator and deploys the output as a Pages artefact. `site/` is not
committed, so the published bytes are always a build of the data in the tree — and can be
reproduced locally with the one command above.

## What the site says, and what it refuses to say

One page per live municipality: five money numbers with a plain-language caption on each, the
Auditor-General's verdicts by year with a key, and who won the 2021 election. It is deliberately
not a ranking, not a score, and not a causal claim — poor audit outcomes, weak finances and
party control share causes and none of them explains another. `key.html` states the limits.

44 district municipalities have no council record because **district councils are not directly
elected**: 60% of their seats come from delegations of the local municipalities inside them and
40% by proportional representation (Municipal Structures Act 117 of 1998). Their pages say that
rather than showing an empty result.

## Cite it

The repository and the DOI are not the same object, and the difference matters:

| | Covers | How to cite |
|---|---|---|
| **DOI `10.5281/zenodo.24241806`** | the archived snapshot of **v0.1.0** only | `Evertse, T. (2026). SA open data: preserved copies of South African local-government datasets (v0.1.0). Zenodo. https://doi.org/10.5281/zenodo.24241806` |
| **Concept DOI `10.5281/zenodo.24241805`** | always the latest *published* version | same, without a version number |
| **Tags `v0.1.1` … `v0.3.0`** | later work — the crosswalk, the coverage correction, `SOURCES.md` | cite by tag: `github.com/realtimshady16/sa-open-data/tree/v0.3.0` |

No Zenodo release exists for `v0.1.1`, `v0.2.0`, `v0.2.1` or `v0.3.0`. They are on GitHub with
tags and checksums but **without a DOI**, so a citation that names one of them must give the
tag URL. Publishing a release at `v0.3.0` would give the ledger, the crosswalk and the coverage
correction their own version DOI; the `.zenodo.json` in this tree is already prepared for it.

`CITATION.cff` is included so GitHub renders a citation widget, and it names the **concept**
DOI, because the widget sits on `main` and `main` is newer than the archived record.

## Verify it

Every **data** file's sha256 is in `MANIFEST.json`, and `tools/check_manifest.py` re-checks the
tree *and* reports any data file that is not listed, so the manifest cannot silently fall behind
the datasets:

```bash
python3 tools/check_manifest.py
```

## Licence

**Data: [CC BY 4.0](LICENSE-DATA). Code: [MIT](LICENSE).** Chosen 2026-11-15; the reasoning,
including the option that was rejected and why, is in `docs/licence-decision.md`.

Attribution only — copy it, adapt it, publish it commercially, build a dashboard on it. What is
asked for is credit.

The underlying statistics are not ours to license. They are produced by National Treasury, the
Auditor-General, the IEC and Statistics South Africa from public money, and facts are not
copyrightable. What is licensed here is the arrangement, the derived tables and the
documentation. Someone could independently fetch the same numbers with no obligation to this
repository, and that is correct.

## What else exists, and what we don't have

`SOURCES.md` is a ledger rather than a link list: every South African source encountered while
building this, marked **✓ held**, **◐ partial**, **○ exists but not held** or **✗ unreachable**,
with the date checked. It exists because a link list tells you the internet is big while a
ledger tells you what is missing — and because several of the ✗ marks are failures of
access, not absences of data.

## Data quality

`docs/coverage-and-caveats.md` lists the things that will bite anyone reusing this: the
difference between 292 profiles and 257 auditees, two municipalities called Emalahleni, the
sign convention on capital spending, and the fact that a null indicator means *not computed*,
never zero. Read it before quoting a number.

## What is next, and what it is not

The installed parts are done: five datasets, the crosswalk, the ledger, the site generator.
What is genuinely missing, in the order the gaps bite:

- **Ward-level anything.** Not available anywhere clean. This is the largest hole in the
  municipal picture and it is a data-absence, not a build-absence.
- **Transaction-level municipal spending.** Exists only in mSCOA machinery that is not public.
- **Coalition agreements for the 138 hung councils.** Political documents, not datasets, and
  the reason the largest-party column is described as a blunt proxy.
- **A second demarcation crosswalk, when boundaries move again.** Municipal Money's
  `is_disestablished` flag is already wrong for two live Limpopo locals (see
  `docs/coverage-and-caveats.md`), which is why the crosswalk carries its own status column.
- **Anything with a refresh cadence.** Deliberately absent. The repository's job is to still be
  accurate in 2031, which argues for fewer moving parts rather than more.
