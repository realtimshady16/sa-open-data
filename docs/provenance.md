# Provenance

Two dates matter throughout: **captured** (when the bytes were taken off the wire) and
**reprobed** (2026-11-15, when the sources were checked again for this repository). Both are
recorded. Where the two disagree, the disagreement is the information.

---

## 1. Municipal Money — municipal financial indicators

| | |
|---|---|
| Publisher | National Treasury (data), Municipal Money (portal, built by OpenUp) |
| Endpoints | `/api/municipality-profile/?limit=150&offset=0` and `offset=150`; `/api/geography/geography/` |
| Captured | 2026-11-10 |
| Records | 292 municipal profiles; 292 geographies (44 districts + 248 municipalities) |
| Requests | 3 GETs, sequential, 2 s apart, descriptive User-Agent with contact |
| robots.txt | `User-agent: *` / `Allow: /` / `Crawl-Delay: 120` |
| Status at capture | HTTP 200 |
| **Status at reprobe 2026-11-15** | `municipality-profile/?limit=1` → **200**; `geography/geography/` → **200** |
| Licence stated by publisher | **none found on the API** |
| Wayback | not needed (live), not checked exhaustively |

Note on the crawl delay: 120 s per request would make a 257-record sweep an 8.5-hour job.
Pagination is not crawling, and this was three requests. Recorded here because it was a
deliberate reading of the rule, not an oversight.

---

## 2. AGSA — municipal audit outcomes (MFMA)

| | |
|---|---|
| Publisher | Auditor-General of South Africa, MFMA 2024-25 site |
| Endpoints | `/api/allauditees`, then `/api/municipalities/{slug}` × 257 |
| Captured | 2026-11-10 (first sweep 2026-11-09, which was incomplete) |
| Records | 257 auditees, 2,056 audit opinions, periods 2017-18 → 2024-25 |
| Requests | 258 GETs at 0.6 s spacing; 18 lost to HTTP 429 and recovered separately |
| Status at capture | HTTP 200 after retry; **0 failures** in the final file |
| **Status at reprobe 2026-11-15** | `mfma-2025.agsa.co.za/` → **200**; `/api/allauditees` → **200**; `mfma-2024.agsa.co.za/` → **200**; **`mfma-2026` does not resolve (DNS NXDOMAIN)**; `agsa.co.za` → 200 |
| Licence stated by publisher | none |
| Wayback | **363 unique URLs** under `mfma-2025.agsa.co.za` (domain query), of which exactly **4 are API endpoints**: `allauditees`, `homepagedata`, `navbar-x`, `pages/overview`. **No captures of `/api/municipalities/{slug}`** — so the auditee list is recoverable and the audit opinions are not. Detail and the methodology error that produced the earlier claim: `docs/archive-audit.md` |

**This is the dataset with the shortest expected life.** The site is year-stamped, the API
carries no stable identifier outside it, and the archive has only the front door.

---

## 3. IEC — council composition

| | |
|---|---|
| Publisher | Electoral Commission of South Africa |
| Endpoints | `results.elections.org.za` (see `scripts/`), `api.elections.org.za/api/v1/` |
| Captured | 2026-11-09 |
| Records | 213 councils per election (2016, 2021), with seats by party and largest party |
| Status at capture | HTTP 200 via the results site |
| **Status at reprobe 2026-11-15** | `results.elections.org.za/` → **200**; `www.elections.org.za/` → **200**; **`api.elections.org.za/api/v1/` → 404** (the path the scripts used is no longer served) |
| Licence stated by publisher | none |
| Wayback | **no usable captures.** `results.elections.org.za` has a single 302 (2021-10-20) and 404s on every well-known path; `elections.org.za` captures from 2026 are 302s and malformed URLs |

The 404 on the API path is the reason `scripts/` are archived rather than relied on: they
record how the data was got, not a supported interface.

---

## 4. Stats SA — free basic services (P9115)

| | |
|---|---|
| Publisher | Statistics South Africa, P9115 (Non-Financial Census of Municipalities) |
| Source | Table 12 of the 2022/23 unit-data workbook |
| Captured | 2026-11-09 |
| Records | 257 municipalities; indent households identified and beneficiaries of water, electricity, sanitation, waste |
| Status at capture | HTTP 200 (site is Incapsula-protected; needs a browser User-Agent) |
| **Status at reprobe 2026-11-15** | `P9115_2022 Unit Data.xlsx` → **200 (still live)**; `?PPN=P9115` page → **200** |
| Licence stated by publisher | none found; Stats SA material is routinely quoted with attribution |
| Wayback | **well archived.** Unit-data workbooks captured 2019, 2021, 2023 and 2024 (2018, 2019, 2020, 2022 editions) plus time-series workbooks 2006–2020 and 2006–2022 |

The original workbook is **not redistributed here** — only the derived table and the URL —
because its terms are unstated and because the numbers are reproducible from the live file.

---

## 5. Municipal identifier crosswalk (derived, 2026-11-15)

Not captured from a publisher. Built by `scripts/build_crosswalk.py` from the four sources
above plus open-admin-data's South African administrative divisions (CC BY 4.0, working fork
at `oss/south-africa-administrative-divisions`), used as a spine and not redistributed.

| | |
|---|---|
| Publisher | this repository (derivation) |
| Inputs | Municipal Money `code`; IEC display-name prefix; AGSA slug + name; P9115 name + district; OpenAdminData `name.local` |
| Built | 2026-11-15 |
| Records | 292 rows: 257 live (8 metro, 205 local, 44 district) + 35 disestablished |
| Method | exact code where the source carries one (MM 292/292, IEC 213/213); name match then district elimination for AGSA 249/257 and P9115 249/257; the remainder listed in `unmatched.json`, not guessed |
| Status | derived from the inputs, so it is only as current as the 2026-11-10 capture |
| Stability | OpenAdminData's **names** are stale (`DC10` still "Cacadu"); its codes and hierarchy are good. Municipal Money's `is_disestablished` is a boundary-change flag, not a liveness flag — see `docs/coverage-and-caveats.md` |

Any future dataset that carries a demarcation code, a municipal name, or an EMIS/ward parent
should join here rather than re-matching. `unmatched.json` is empty for AGSA and P9115 as of
2026-11-18 — the eight residuals were resolved by hand and recorded in the crosswalk's own
README, which is the place they would reappear if a source changes shape.

---

## What was not published here, and why

- **Party manifestos** (328 MB of PDFs and OCR text held locally). Third-party documents
  under their own copyright; a corpus of reproductions is a different legal object from a
  table of statistics.
- **The Stats SA workbook** — see above; link and hash instead of the file.
- **Any scrape captured against a publisher's stated terms.** The source-policy rule used in
  the Mzantsi Vibes project (`sources/policy.json`) applies to this work too: a 404 on
  robots.txt means no rules published, not permission.

## Reprobe log (raw)

```
2026-11-15
  mfma-2025.agsa.co.za/                       200
  mfma-2025.agsa.co.za/api/allauditees        200
  mfma-2024.agsa.co.za/                       200
  mfma-2026.agsa.co.za/                       000 (could not resolve host)
  agsa.co.za                                  200
  municipalmoney.gov.za/api/municipality-profile/?limit=1   200
  municipalmoney.gov.za/api/geography/geography/            200
  results.elections.org.za/                   200
  api.elections.org.za/api/v1/                404
  www.elections.org.za/                       200
  statssa.gov.za/.../P9115_2022 Unit Data.xlsx 200
  statssa.gov.za/?page_id=1854&PPN=P9115       200
```
