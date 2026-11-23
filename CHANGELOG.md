# Changelog

Versions are git tags. Only **v0.1.0** has a DOI (`10.5281/zenodo.24241806`); the later tags
exist on GitHub only, so cite them by URL until a Zenodo release is published. Data files have
not changed since v0.1.0 except for the crosswalk added in v0.2.0 — later releases are
documentation, a derived join, and corrections.

## Unreleased — after v0.3.0, 2026-11-18

- **The static view is published** at `https://realtimshady16.github.io/sa-open-data/`, built by
  `.github/workflows/pages.yml` from `datasets/` on every push. `site/` stays git-ignored, so
  the view is still not part of the record. No captured dataset changed.
- **A defect in that view, fixed before publishing:** 44 district pages rendered a missing IEC
  council record as "— seats up for election in 2021 … no party holds more than half, so a
  coalition had to be formed", i.e. it asserted a hung council from absent data. District
  councils are not directly elected (60% delegations from the local municipalities, 40% PR,
  Municipal Structures Act 117 of 1998), so those pages now say that instead.

- **`SOURCES.md` corrected in five rows** after a session in the collections tree: the Master
  List of Schools is held (DBE-direct, 2024 national + 2026 provinces) and parsed, not a DataFirst
  dependency; school-level NSC is held as 13 reports with one parsed, so catalogue 685 is dropped;
  PACSA is 11 of 45 rather than 2; SAFOODS is held at 1,362 rows with analysis-only terms rather
  than "terms unverified"; and PMBEJD is marked private-use-only.
- **A rights preamble in the ledger:** *held is not publishable*, and nothing in this repository
  derives from the two sources marked private use only.

## v0.3.0 — 2026-11-18

Documentation and integrity release. No captured dataset changed.

- **`SOURCES.md`** — a 99-row ledger of South African data sources: publisher, access mechanism,
  held / partial / not-held / unreachable, path, date checked. Includes the ranked gap list and
  the rule that a failed request is not an absent source.
- **`CHANGELOG.md`** — this file.
- **Manifest now covers the crosswalk** (`crosswalk.csv`, `unmatched.json`). It did not before:
  the claim "every data file's sha256 is in `MANIFEST.json`" was false from v0.2.0 while the
  checksum check still passed, because the check only walked the manifest. `MANIFEST.json` is
  13 files / 22.0 MB.
- **`tools/check_manifest.py`** — verifies checksums *and* reports data files that exist but are
  not listed, which is the failure that hid the gap above. Replaces the inline snippet in the
  README.
- **Resolved the open reconciliation in `docs/coverage-and-caveats.md`.** The file said 211 live
  municipalities was "two short of the standard 205 local, most likely the 2026 demarcation
  changes. Unresolved." It was neither: Municipal Money's `is_disestablished` flag marks
  boundary *change*, not liveness, and is set for two live Limpopo locals — **LIM343 Thulamela**
  (land lost and gained) and **LIM344 Makhado** (land lost). 205 local + 44 district + 8 metro =
  257 live; 35 genuinely disestablished. The crosswalk's own `status` column was right all along.
- **`docs/provenance.md`** gained a crosswalk section (it was added in v0.2.0 without one):
  inputs, method, the two slugs that stay ambiguous, and the warning that open-admin-data's
  names are stale while its codes are good.
- **README** brought up to date: the crosswalk and the site generator are in the file tree, the
  static view is documented as built rather than promised, "Cite it" distinguishes the DOI
  (v0.1.0) from the tags (later, no DOI), and the "possible additions" list is replaced by the
  gaps that are real.

## v0.2.1 — 2026-11-15

- Crosswalk extended to full coverage; the site gains a plain-language layer over the raw
  indicator tables. README documents the static build.

## v0.2.0 — 2026-11-15

- **`datasets/crosswalk/`** — 292 rows, one per municipal entity, carrying Municipal Money,
  IEC, AGSA, Stats SA P9115 and open-admin-data keys on the same row. Exact matches: Municipal
  Money 292/292, IEC 213/213. Name-then-district matching: AGSA 249/257, P9115 249/257; the
  remainder are in `unmatched.json`, not guessed. Built by `scripts/build_crosswalk.py`.
- A static site generator: one page per municipality, joined through the crosswalk.

## v0.1.1 — 2026-11-15

- **Correction:** the claim that the Internet Archive held only the AGSA landing page came from a
  CDX query without `matchType`, which can only match a site root. Measured properly: **363
  URLs** for `mfma-2025.agsa.co.za`, of which 4 are API endpoints. The auditee list is archived;
  the 257 × 8 opinion responses are not. Recorded in `docs/archive-audit.md` with the method
  rule that came out of it: always pass `matchType`, never conclude absence from an empty or
  failed response.

## v0.1.0 — 2026-11-15

First release, DOI [10.5281/zenodo.24241806](https://doi.org/10.5281/zenodo.24241806).

- **Municipal Money** (National Treasury / OpenUp): 292 municipal financial profiles, 292
  geographies, 21,538 long-format indicator rows, captured 2026-11-10.
- **AGSA audit outcomes** (Auditor-General, MFMA 2024-25): 257 auditees × 8 periods = 2,056
  opinions, captured 2026-11-10.
- **IEC council composition** (Electoral Commission): seats by party and largest party for 213
  councils after the 2016 and 2021 elections.
- **Stats SA P9115**: free basic services per municipality, derived from the 2022/23 unit-data
  workbook.
- Provenance, method, caveats, licence decision, unmodified fetchers, `MANIFEST.json`, and a
  per-data licence split: CC BY 4.0 for data, MIT for code.
