# Municipal identifier crosswalk

One row per South African municipal entity, with every source's own key on that row, so a new
dataset is a join rather than a matching project.

Built by `scripts/build_crosswalk.py`. 292 rows: **257 live** (8 metro, 205 local, 44 district)
plus **35 disestablished** pre-2016 entities retained because AGSA still carries their audit
history.

## The finding that made this cheap

Three of the five sources turned out to share one identifier — the **demarcation code** — they
just spell it differently:

| Source | Where the code hides | Example |
|---|---|---|
| Municipal Money | `code` column | `EC102` |
| IEC | **prefix of the display name** | `EC442 - Umzimvubu` |
| OpenAdminData | `name.local` (the local-language name *is* the code) | `KZN263` |
| AGSA | nowhere — slug and name only | `1-matatiele` |
| Stats SA P9115 | nowhere — name and district only | `Matatiele Local Municipality` |

So 60% of the join is exact, not fuzzy. The IEC prefixes are not abbreviations to be guessed at:
all 213 councils carry their code, including the eight metros (`BUF`, `CPT`, `EKU`, `ETH`, `JHB`,
`MAN`, `NMA`, `TSH`).

## Coverage

| Source | Matched | Of | Method |
|---|---|---|---|
| Municipal Money | **292** | 292 | exact code |
| IEC 2016 | **213** | 213 | exact code (display-name prefix) |
| IEC 2021 | **213** | 213 | exact code |
| AGSA | **249** | 257 | name+province, then district elimination |
| Stats SA P9115 | **249** | 257 | name, then district elimination |

## Three tiers, in order, each recorded

1. **Exact code.** Nothing else.
2. **Name + province**, unique-only. Candidate lists are de-duplicated first: the same code
   arrives twice when the OpenAdminData name and the Municipal Money name agree, which in the
   first version made every easy match look ambiguous.
3. **District elimination.** If an unmatched AGSA or P9115 entity names district D, exactly one
   child of D still lacks that source, and exactly one unmatched row sits in D, the pairing is
   forced. `match_method_*` records this, so an inference never masquerades as a name match.

Anything still unmatched is written to `unmatched.json` with its candidates. **Nothing is
guessed.** Municipal Money's code column is the spine; every other source is attached to it.

## The eight exceptions, and what they are

Both sources fail on the same eight, which is the useful part — it means it is one problem, not
two.

| Entity | District | Likely cause |
|---|---|---|
| Dr Beyers Naudé | Sarah Baartman | renamed (was Baviaans-adjacent amalgamation in 2016) |
| Ingquza Hill | O.R. Tambo | renamed (formerly Qaukeni) |
| uMfolozi | King Cetshwayo | renamed (formerly Mfolozi) |
| Big 5 Hlabisa / The Big 5 Hlabisa | uMkhanyakude | numeral: OAD says "Big **Five** Hlabisa" |
| iNkosi uMtubatuba | uMkhanyakude | spelling / honorific prefix |
| Fetakgomo Tubatse / Fetakgomo-Tubatse | Sekhukhune | 2016 merger, hyphenation |
| City of Mbombela | Ehlanzeni | **genuinely ambiguous**: candidates `MP322`, `MP326` (Umjindi was merged into Mbombela) |
| Pixley Ka Seme District | Pixley Ka Seme - NC | **genuinely ambiguous**: `DC7` (Northern Cape district) vs `MP304` (a Mpumalanga local of the same name) |
| uMgungundhlovu District | uMgungundhlovu | P9115 only; spelling |
| Umzimkulu / Dr Nkosasana Dlamini Zuma | Harry Gwala | renamed (Umzimkulu → Dr Nkosazana Dlamini-Zuma) |

Two are real ambiguity and should stay unmatched until a human decides. The rest are renames
that a person can settle in minutes — the tool lists them rather than picking.

## A caution about the spine source

OpenAdminData is the best structured source available and it is **not current everywhere**:
`DC10` is still named **Cacadu** there (it has been Sarah Baartman since 2014), district `O.R.
Tambo` is written `O.R.Tambo`, and several 2016 mergers are absent. It matched anyway because
Municipal Money's names are current — but do not treat OAD labels as authoritative for naming,
only for codes and hierarchy.

## Using it

```python
import csv
# Municipal Money code -> AGSA slug -> IEC display name
x = {r["code"]: r for r in csv.DictReader(open("datasets/crosswalk/crosswalk.csv"))}
x["EC102"]["agsa_slug"]        # '1-blue-crane-route'
x["NMA"]["iec_2021_name"]      # 'NMA - Nelson Mandela Bay'
```

Licence: CC BY 4.0, like the rest of `datasets/`.
