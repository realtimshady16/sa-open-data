# Sources ledger — what exists, and what we actually hold

This is not a list of links. It is a **ledger**: every row is a source, and every row says
whether we have it, how much of it, and where it lives. A link list tells you the internet is
big; a ledger tells you what is missing.

Checked **2026-11-15** unless a different date is shown. Statuses are perishable — that is the
point of the date column. See `docs/archive-audit.md` for why.

## How to read the marks

| Mark | Meaning |
|---|---|
| **✓** | Held, essentially complete, with a checksum in `MANIFEST.json` or a manifest on disk |
| **◐** | Held partially — a sample, a derived table, or an interrupted fetch |
| **○** | Exists, live, **not held** |
| **✗** | Not reachable: dead, blocked, or TLS-broken. **This is not the same as "does not exist"** |
| — | Not checked |

Every ✗ in this file was verified as a failure, not inferred from an empty result. That
distinction cost me three wrong claims in one evening.

---

## Local government — the core

| Source | Publisher | What it holds | Access | Held | Where | Status |
|---|---|---|---|---|---|---|
| Municipal Money API | National Treasury / OpenUp | 292 municipal profiles: budgets, spend, cash coverage, UIFW, repairs, debtors, audit opinions, mayor contacts | JSON API, 2 paginated GETs for the whole country | **✓** | `datasets/municipal-money` | 200 |
| AGSA MFMA audit outcomes | Auditor-General | 257 auditees × 8 periods = 2,056 opinions, 2017-18 → 2024-25 | JSON API, one GET per auditee (429s without pacing) | **✓** | `datasets/agsa-audit-outcomes` | 200 |
| AGSA MFMA **reports** (PDFs) | Auditor-General | The consolidated general reports and per-municipality findings — the prose behind the verdicts | PDF | ○ | — | 200 |
| IEC council composition | Electoral Commission | 213 councils × 2016 and 2021: seats by party, largest party, majority | JSON via results site | **✓** | `datasets/iec-councils` | 200; `/api/v1/` path **404** |
| IEC results dashboards (2026) | Electoral Commission | The live 2026 LGE results site | Web app | ○ | — | 200 live; **no archived API captures** |
| Stats SA P9115 | Statistics South Africa | Free basic services: indigent households, beneficiaries, coverage ratios | XLSX workbook (Incapsula; needs browser UA) | **◐** derived table only | `datasets/stats-sa-p9115` | 200 |
| OpenAdminData divisions | open-admin-data | 9 provinces / 52 districts / 213 municipalities / 4,392 wards with codes and coordinates | JSON, CSV, NDJSON | **✓** used as spine, not redistributed | fork: `oss/south-africa-administrative-divisions` | CC BY 4.0 |
| Municipal Demarcation Board | MDB | Boundary changes — the thing every time series breaks on | Web | ✗ | — | **TLS certificate chain broken** |
| Vulekamali | Treasury / OpenUp | National and provincial budgets | Web + JSON API | ○ | — | 200 |
| eTenders | National Treasury | Public procurement: who was awarded what | Web portal | ○ | — | 200 |
| PMG | Parliamentary Monitoring Group | Hansard, written questions and replies, bills | Web + CMS | ○ | — | 200 |
| SAFLII | SAFLII | Court judgments, full text | HTML | ○ | — | **403** to curl (bot block; not absence) |
| LawLibrary / Laws.Africa | Laws.Africa | Legislation in Akoma Ntoso XML | HTML + API v3 | ○ | — | 200; API needs a token |
| OpenByLaws | Laws.Africa | Municipal by-laws | HTML | ○ | — | 200 |

## Food — prices, composition, affordability

| Source | Publisher | What it holds | Access | Held | Where | Status |
|---|---|---|---|---|---|---|
| Household Affordability Index | PMBEJD | Monthly food basket: ~44 items × 7 areas, 2,550–2,780 price values per report | PDF, 129 links, **Aug 2018 → present** | **✓** 117 docs + text | `~/thinking/.raw/food/pmbejd` | 200 |
| Food Price Barometer | PACSA (predecessor to PMBEJD) | The same basket from **2012** onward; the series changes hands here | PDF, Wayback only | **◐** 2 of 45 | same tree, `pacsa/` | **429 rate-limited**; manifest of 45 captures written |
| SAFOODS | SAMRC | South African food composition database | Via MRC | ○ | — | terms unverified |
| FoodFinder | SAMRC | Intake and labelling analysis built on SAFOODS | **Paid annual licence** | ✗ not free | — | verified paid |
| Food Price Monitor | NAMC | Farm-gate to retail price spreads | PDF / XLSX | ○ | — | 200 |
| Open Food Facts | Open Food Facts | Product barcodes, ingredients, nutrition | Bulk + API | ○ | — | data ODbL, code AGPL |

## Climate, water, energy

| Source | Publisher | What it holds | Access | Held | Status |
|---|---|---|---|---|---|
| NIWIS | Dept of Water & Sanitation | Dam levels, rainfall, river flow | Dashboards, XLSX | ○ | 200 |
| SAWS | SA Weather Service | Weather observations and forecasts | Web | ○ | 200 |
| SANBI BGIS | SANBI | Biodiversity layers, ecosystem threat, land cover | WMS/WFS + shapefiles | ○ | 200 |
| Eskom data portal | Eskom | Grid demand, generation mix, UCLF | CSV | ○ | 200 (`data.eskom.co.za` is dead) |
| CSIR Energy Centre | CSIR | Annual energy-mix and generation statistics | PDF / XLSX | ○ | 200 |
| DFFE | Dept of Environment | Environmental regulation and monitoring | Web | ○ | **000** — no response to a browser UA |
| DMRE | Dept of Mineral & Energy Resources | Mining and energy regulation | Web | ○ | **000** |

## Economy, tax, population

| Source | Publisher | What it holds | Access | Held | Status |
|---|---|---|---|---|---|
| SARB | Reserve Bank | Rates, reserves, BoP, time series | Portal query → CSV/XLSX | ○ | 200 (direct CSV paths are not guessable) |
| SARS tax statistics | SARS / Treasury | Income tax distribution, wage brackets | Annual PDF + Excel | ○ | 200 (person-level microdata gated) |
| Stats SA publications | Statistics South Africa | CPI, GDP, QLFS, census | Workbooks | ◐ P9115 only | 200, Incapsula |
| DataFirst | UCT | Microdata: census, QLFS, GHS, NIDS | Stata/SPSS/CSV | ○ | free account + data-use agreement |
| Land Portal | Land Portal Foundation | Land governance index | Web | ○ | 200 (deeds are paid) |

## Language and corpora

| Source | Publisher | What it holds | Access | Held | Status |
|---|---|---|---|---|---|
| SADiLaR repository | SADiLaR | NCHLT POS- and lemma-annotated corpora per language (isiZulu, isiXhosa, isiNdebele visible), plus speech corpora | DSpace, browse + download | ○ | 200 |
| SADiLaR | SADiLaR | The national digital-language infrastructure: training, tools, DH support | Web | ○ | 200 |
| CTexT | North-West University | MT, NER; `nwu-ctext/afrikaans_ner_corpus` on HF | Repos + HF | ○ | 200 |
| Autshumato | CTexT / NWU | Open machine translation system | Source + web | ○ | **403** to curl (exists; not verifiable from here) |
| DSFSI | University of Cape Town | 50+ SA datasets registry; local NLP datasets | GitHub | ○ fork exists | `oss/dsfsi-datasets` |
| Masakhane | Masakhane | MT, NER, QA, news datasets for African languages | GitHub + HF | ○ | `masakhane-mt` stale since 2022 |
| MzansiLM | UCT NLP | 125M-parameter multilingual SA model | HF | **◐** local | `apps/mzantsivibes-ai` |
| HF language mirrors | Various | NCHLT speech (Xhosa), `opus_xhosanavy`, Wikipedia dumps (Sotho/Tswana), sentence pairs | HF API | ○ | uneven licensing |

**Caution on that block:** much of what surfaces under these language names is **synthetic**
instruction data (`saillab/alpaca-*`). Useful for fine-tuning, useless for measurement. And
licensing ranges from CC0 to unlicensed, which means all rights reserved.

## Preservation

| Tool | Use | Held |
|---|---|---|
| Wayback CDX API | Query what the Archive captured for a URL (always pass `matchType`) | ✓ used |
| Wayback Save Page Now | Push a live URL into the archive — the archive is passive by default | ✓ 11 URLs pushed 2026-11-15 |
| Zenodo | DOI minting from a GitHub release | ✓ `v0.1.0` → `10.5281/zenodo.24241806` |

---

## Gaps, ranked by what they cost us

1. **Coalition outcomes** for the 138 hung councils — not a data problem, a time problem.
2. **AGSA report PDFs** — we hold the verdicts, not the reasoning. The findings are where the
   accountability lives.
3. **Food composition** (SAFOODS) — the other half of nutrition-per-rand, and its terms are
   unknown.
4. **Ward-level anything** — the finest grain available is municipality, and that hides most
   inequality.
5. **Procurement** (eTenders) — audit says the books were wrong; tenders say where the money
   went.
6. **PMG questions** — the only place ministers answer in writing, on the record, by date.

## Adding a row

- Record the **publisher**, not the aggregator.
- Give the access mechanism, because "web portal" and "bulk CSV" are different projects.
- Mark the status, and put the **date** on it.
- Never mark ✗ from a failed request without saying what failed: `429`, `403`, `000` (DNS/TLS)
  and `404` mean four different things, and only one of them is "gone".

## Licence

This ledger: CC BY 4.0, like the rest of the repository. The sources it describes carry their
own terms, and several carry none at all — which means all rights reserved, not permission.
