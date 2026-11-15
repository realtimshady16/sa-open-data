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
| DataFirst | UCT | Microdata: census, QLFS, GHS, NIDS | Stata/SPSS/CSV | ○ | 200 — free account + data-use agreement |
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

## Prices — the three indices that anchor everything else

| Source | Publisher | What it holds | Access | Held | Status |
|---|---|---|---|---|---|
| **CPI history** (P0141) | Stats SA | Monthly headline and group index numbers **from 1980 to present** (Dec 2024 = 100) in one 3-page file | PDF table | **✓** `prices/cpi-history` | 200 |
| CPI monthly release | Stats SA | Headline, group and category inflation, contributions | PDF | **✓** Dec 2025 | 200 |
| CPI basket and weights | Stats SA | The 2025 weights — themselves a spending-share estimate | PDF | **✓** 2025 presentation | 200 |
| **PPI** (P0142.1) | Stats SA | Producer prices, monthly, by industry | PDF, 15 pp | **✓** Jul 2026 | 200 |
| **RPPI** (P0160) | Stats SA | Residential property prices, monthly, by metropolitan area | PDF, 12 pp | **✓** May 2026 | 200 |
| RPPI experimental series (D0160) | Stats SA / SARB / IMF | The earlier experimental index | PDF | ○ | superseded by P0160 |
| House price indices (private) | ABSA · FNB · Pam Golding | Alternative measures with longer histories | Reports | ○ | commercial |

**Why held together.** CPI turns nominal series into real ones; PPI says where cost pressure
originates; RPPI prices the largest asset most households will ever hold, and the one carrying the
debt in SARB's household figures.

**The trap.** CPI was substantially recompiled in **January 2009** and re-based (currently
Dec 2024 = 100). Series crossing those breaks must be rebased, not concatenated — the history
file says so on its own first page, and it is the same mistake the municipal boundary series
offers anyone who doesn't read the notes.

## Household spending, and where the money actually goes

South Africa measures this twice over, badly and well: **surveys** that ask households what they
spend (accurate for the poor, under-reported for the rich, and systematically silent on alcohol,
gambling and anything shameful), and **industry and regulator series** that count the money as it
arrives (accurate in aggregate, blind to who spent it). Any honest picture triangulates the two,
and knows which one is speaking.

| Source | Publisher | What it holds | Access | Held | Status |
|---|---|---|---|---|---|
| **Income & Expenditure Survey (P0100)** | Stats SA | **The spine.** Household spending by COICOP category, income, and grant receipt. Editions 2005/06, 2010/11, 2015/16, 2022/23 | Report PDFs + microdata | **✓** report held (348 pp); microdata ○ | 200 — `publications/P0100/P01002022.pdf`; microdata on DataFirst (200, free account) |
| Household final consumption expenditure | Stats SA (GDP release) | Quarterly spending by category, aggregate | Excel from GDP release | ○ | — |
| CPI and its **weights** (P0141) | Stats SA | Monthly prices, and the basket weights that are themselves a spending-share estimate | Excel / PDF | **✓** Dec 2025 release + the 2025 basket/weights presentation | 200 |
| General Household Survey (P0318) | Stats SA | Grant receipt, services access, ICT use in households | Microdata | ○ | — |
| Living conditions / NIDS | Stats SA / UCT | Panel welfare, food poverty, grant dependence | Microdata | ○ | — |
| Retail trade sales (P6242.1) | Stats SA | Monthly retail turnover by category | Excel | ○ | 200 |

### Grants and social security

| Source | Publisher | What it holds | Access | Status |
|---|---|---|---|---|
| SASSA | South African Social Security Agency | Beneficiary numbers by grant type and province, expenditure, payment dates | Web + reports | **✓** Social assistance report, Jun 2026 (123 pp) | 200 — but **paths churn** (the obvious `/statistical-reports/` URL 404s) |
| Social protection vote | National Treasury | Budget allocation, including SRD grant | Budget documents | — |
| SASSA annual report | SASSA | Audited spend and beneficiary counts | PDF | — |

### The discretionary categories, counted rather than asked

| Category | Source | What it holds | Access | Status |
|---|---|---|---|---|
| Gambling | National Gambling Board | Gross gaming revenue by province and mode (casino, betting, LPM) | Reports | **✓** `Summary: Gambling Sector Performance FY2024-25` (49 pp, 121 GGR mentions) — **not** the annual report, which carries none | 200 |
| Gambling (provincial) | Gauteng Gambling Board · WCGRB | Province-level GGR, licences, enforcement | Annual reports | **✓** GGB 2024/25 (140 pp), WCGRB 2023/24 (156 pp) | 200 |
| Alcohol & tobacco · fuel | SARS | Excise and fuel-levy collections by product | Annual **workbooks** (chapter zips) | **✓** Tax Statistics 2025 ch.1 and ch.6 | 200 |
| Vehicles | NAAMSA | Monthly new vehicle sales by segment — the cleanest monthly series in the country | Web / releases | **✓** Oct 2026 release + flash stats | 200 |
| Broadcast & streaming | ICASA | State of the ICT Sector: subscription TV, internet penetration, data prices | Report PDF | **✓** 2025 and 2026 editions | 200 |
| Electricity | NERSA · Eskom | Tariffs, sales volumes; Eskom data portal has generation and demand | Web / CSV | 200 both |
| Fuel | SAPIA · DMRE | Volumes by product; regulated prices | Web | **403** to curl (exists) |
| Insurance & savings | ASISA · SARB | Industry flows; household debt and saving in the Quarterly Bulletin | Web / PDF | 200 both |
| Financial inclusion | FinMark Trust (FinScope) | Who has a bank account, credit, insurance | Survey reports | 200 |
| Medicines | Code4SA `medicine-price-registry` | Single Exit Price mechanism, with an API | GitHub | Apache-2.0 |
| Food | PMBEJD · NAMC · CPI food group | Monthly basket (held), farm-gate spreads, headline prices | PDF / API | PMBEJD **✓ held** |

### What this combination can and cannot say

- **Can:** the shape of household spending by category, for 2005/06 → 2022/23, and monthly
  movement in the price of that same basket. Grant dependence by household. Gaming revenue and
  excise as independent checks on the "shameful" categories.
- **Cannot:** who spent it. IES is a survey with a five-year gap; retail trade and excise have no
  income dimension; SASSA knows recipients but not their other spending.
- **The honest warning:** survey and industry numbers disagree by construction. Under-reporting is
  not noise, it is pattern — alcohol and gambling are under-stated in surveys, and province-level
  industry totals double-count between operators. Triangulate, then say which leg you're standing
  on.

## Schooling and higher education

Added 2026-11-15. Two departments, one funding agency, and a set of things that are simply not
published as data — which is worth knowing before a project assumes they are.

| Source | Publisher | What it holds | Access | Held | Status |
|---|---|---|---|---|---|
| **Master List of Schools** (EMIS) | DBE, via DataFirst | Every school: name, phase, quintile, address, learner and educator counts | Microdata | ○ | DataFirst catalogue 985, free account |
| **NSC examinations 2008–2025, school level** | DBE, via DataFirst | Per-school matric results, derived from the "343" reports | Microdata | ○ | DataFirst catalogue 685 |
| NSC 2024 school performance report | DBE | Per-school performance, five-year view | PDF | **✓** 155 pp | 200 |
| DBE annual report 2024/25 | DBE | Programme performance, learner numbers, NSNP, infrastructure | PDF | **✓** 203 pp | 200 |
| Statistics on post-school education 2023 | DHET | Enrolment, graduates, throughput, dropouts by institution | PDF | **✓** 156 pp | 200 |
| HEMIS | DHET | The higher-education management information system behind the statistics above | Portal | ○ | not openly downloadable |
| NSFAS | NSFAS | Funded students, disbursements, annual reports, APPs | Web + PDF | ✗ | **TLS certificate verify failed** — same failure as the Demarcation Board |
| CAPS / NCS Grades R–12 | DBE | The curriculum itself, per subject, per phase | PDF | ○ | `education.gov.za/Curriculum/` |
| National School Nutrition Programme | DBE | Meals, schools, budget | PDF reports | ○ | latest public annual report located is 2011/12 |
| NEIMS school infrastructure | DBE | Water, sanitation, electricity, classrooms per school | **Not openly downloadable** | ○ | report-level only |
| School fees and exemptions | SGBs / provincial | Fees are set per school by governing bodies | **Not published centrally** | ✗ as data | the gap nobody mentions |
| Teacher and psychologist establishment | DBE / provinces | Posts per school, learner-support staff | Not published as a series | ✗ as data | the second gap |

### What this actually means

- **The spine is the Master List of Schools** — one row per school, joined to NSC results by
  EMIS number. That join is the education equivalent of the municipal crosswalk, and it is
  available today behind a free DataFirst account.
- **Infrastructure is the weak leg.** NEIMS is the system, but what circulates publicly is
  analysis of it, not the dataset. Any "schools without water" claim is circulating someone
  else's extraction.
- **Two things people ask about are not data at all**: fees (set per school, published in
  governing-body minutes if anywhere) and learner-support staffing (psychologists, social
  workers). Both are real absences, not access failures.

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

## How this was collected, so it can be collected again

**Record entry points, not file URLs.** Three publishers taught this in one day:

- **DBE links files through `LinkClick.aspx?fileticket=<hash>`** — the ticket is a content hash,
  not an address. A saved list of 794 ticket URLs is worthless in a year; the *page* is stable.
  The recipe is: fetch the page, re-derive links by their **label** (`"School Performance Report"`).
- **Stats SA's P-series landing pages** return a ~1 KB Incapsula challenge to a script, while the
  file paths under `/publications/` are open. Know the path pattern; don't crawl the index.
- **PACSA's live site** answers every PDF path with its homepage (same byte count, `text/html`) —
  a soft 404. Only the Internet Archive captures are real.

**Then always re-probe.** `api.elections.org.za/api/v1/` returned 200 on 9 November 2026 and 404
on 15 November 2026. A URL is a claim about the present, not a fact.

**Politeness that worked:** one request at a time, 5 seconds apart, a descriptive User-Agent with
a contact URL. Zero 429s across ~40 requests at that pace; throttling only appeared when something
hammered (AGSA at 0.15 s/request cost 18 of 257 auditees; Wayback content fetches need shallow
passes 30 minutes apart, not deep retries).

**Never authenticate as a person.** DataFirst microdata is downloaded by the named researcher and
parsed locally. A data-use agreement is signed by a human; a script logging in on their behalf
sits outside its terms and taints the provenance of everything built downstream.

## What is held locally

Collected documents live in `~/thinking/.raw/collections/` with a `manifest.csv` (sha256, bytes,
HTTP status, publisher, timestamp). **Not published in this repository**, deliberately: these are
third-party documents under their own copyright — the same category as the manifesto corpus. The
tables extracted from them are ours to publish; the PDFs are not.

Fetched 2026-11-15 at one request every 5 s with a descriptive User-Agent: Stats SA IES 2022/23 ·
CPI Dec 2025 + 2025 weights · SASSA social assistance Jun 2026 · ICASA ICT sector 2025 and 2026 ·
NGB gambling performance 2024-25 · GGB and WCGRB annual reports · SARS Tax Statistics 2025
chapters 1 and 6 · NAAMSA Oct 2026. **Zero 429s at that pace** — the throttling only appears when
something hammers.

## Adding a row

- Record the **publisher**, not the aggregator.
- Give the access mechanism, because "web portal" and "bulk CSV" are different projects.
- Mark the status, and put the **date** on it.
- Never mark ✗ from a failed request without saying what failed: `429`, `403`, `000` (DNS/TLS)
  and `404` mean four different things, and only one of them is "gone".

## Licence

This ledger: CC BY 4.0, like the rest of the repository. The sources it describes carry their
own terms, and several carry none at all — which means all rights reserved, not permission.
