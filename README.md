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
scripts/                  the fetchers and derivations, unmodified
docs/provenance.md        publisher, endpoint, capture date, live status, archive status
docs/method.md            how each dataset was obtained, and where it is fragile
docs/coverage-and-caveats.md   what the numbers are NOT
docs/licence-decision.md  which licences were chosen and why
SOURCES.md                a ledger: every SA source we know of, and whether we hold it
MANIFEST.json             size, sha256, row/record counts, source URL per data file
```

## Cite it

```
Evertse, T. (2026). SA open data: preserved copies of South African local-government
datasets (v0.1.0). Zenodo. https://doi.org/10.5281/zenodo.24241806
```

That is the **version DOI**, which pins v0.1.0 and is the one to cite for a specific
result. The **concept DOI** — <https://doi.org/10.5281/zenodo.24241805> — always resolves to
the latest version and is what to cite when you mean the dataset generally.

Both resolve through <https://zenodo.org/records/24241806>, which holds the archived snapshot
of the v0.1.0 tag. Later commits on `main` are not part of that record.

`CITATION.cff` is included so GitHub renders a citation widget. Tag `v0.1.0` is the citable
release. If a DOI is minted later (Zenodo), this section gets updated — the tag is the
permanent handle until then.

## Verify it

Every **data** file's sha256 is in `MANIFEST.json`. To check the tree matches what was
published:

```bash
python3 - <<'PY'
import hashlib, json
man = json.load(open("MANIFEST.json"))
bad = [e["path"] for e in man["files"]
       if hashlib.sha256(open(e["path"], "rb").read()).hexdigest() != e["sha256"]]
print("ok" if not bad else f"{len(bad)} mismatched: {bad}")
PY
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

## Possible additions, not promises

- A static HTML view — one page per municipality, no server, so it survives the CDN changing.
- A small chart layer over the indicator time series, generated at build time.
- Ward-level anything: not currently available anywhere clean.
- A demarcation crosswalk, once someone publishes a maintained one.

Nothing here is on a schedule. The repository's job is to still be accurate in 2031, which
argues for fewer moving parts rather than more.
