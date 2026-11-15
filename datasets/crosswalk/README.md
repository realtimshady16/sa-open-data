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
| AGSA | **257** | 257 | name+province, district elimination, then verified aliases |
| Stats SA P9115 | **257** | 257 | same |

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

## The nine aliases, and how each was verified

Nothing here is a similarity score. Each row was settled by looking at the district's
children in the spine and finding the one entity the source must mean. The basis is stored
per row (`alias_basis_agsa`, `alias_basis_p9115`) so the reasoning travels with the data.

| Source name | Code | Basis |
|---|---|---|
| Ingquza Hill | `EC153` | orthographic variant of Ngquza Hill (Municipal Money: "Ngquza Hills") |
| iNkosi uMtubatuba | `KZN275` | honorific dropped: "iNkosi uMtubatuba" vs "Mtubatuba" |
| uMfolozi | `KZN281` | u- prefix: "uMfolozi" vs "Mfolozi" |
| Fetakgomo Tubatse / Fetakgomo-Tubatse | `LIM476` | 2016 merger, vs "Greater Tubatse/Fetakgomo" |
| City of Mbombela | `MP326` | `MP322` is an empty ghost row; `MP326` is Mbombela and carries MM/IEC |
| Pixley Ka Seme District | `DC7` | type DM + Northern Cape; `MP304` is a Mpumalanga local of the same name |
| uMgungundhlovu District | `DC22` | spelling, vs "Umgungundlovu" |
| Umzimkulu | `KZN435` | spelling, vs "Umzimkhulu" |
| Dr Nkosasana Dlamini Zuma | `KZN436` | spelling, vs "Nkosazana" |

The script prints a warning if an alias stops matching anything, so a stale entry surfaces
instead of quietly doing nothing.

## Three normalisation bugs worth knowing

Each of these silently under-matched before it was fixed, and each looks like a data problem
rather than a code problem:

1. **Hyphens deleted rather than spaced.** "Fetakgomo-Tubatse" became `fetakgomotubatse` while
   "Fetakgomo Tubatse" stayed `fetakgomo tubatse`. Hyphens and slashes are word separators;
   dots and apostrophes should just be deleted.
2. **Accents deleted rather than folded.** "Naudé" became `naud`, which matches nothing.
   Decompose (NFKD) and drop the combining marks instead.
3. **Candidates not de-duplicated.** The same code arrived twice whenever the OpenAdminData and
   Municipal Money names agreed, so every easy match looked ambiguous.

Plus one structural one: **OpenAdminData's district names are pre-2014** (Cacadu, uThungulu,
Sisonke), so a district map built only from it fails precisely where renames live. The map now
considers both naming schemes.

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
