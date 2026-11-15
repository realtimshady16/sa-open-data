# Municipal Money — municipal financial indicators

Captured 2026-11-10 from `https://municipalmoney.gov.za/api/`. Publisher: National Treasury
(data), Municipal Money / OpenUp (portal). No licence stated on the API.

| File | What |
|---|---|
| `municipal-profiles-2026-11-10.json` | 292 raw profiles — indicators, audit opinions, mayor contacts, demarcation |
| `municipalities-2026-11-10.csv` | one row per entity: code, name, province, level, category, population, latest audit opinion, key 2024 indicators |
| `indicators-long-2026-11-10.csv` | 21,538 rows: entity × year × indicator, 17 indicators |
| `geography-2026-11-10.json` | names, province, `geo_level`, category, population, `is_disestablished` |

Join key is `code`. **44 districts are included** — filtering to "municipality" leaves them
nameless. 37 entities are disestablished (pre-2016 composites) and still carry audit history;
they are wrong for any current count.

Indicators are already ratios: `cash_coverage` in months, `uifw_expenditure` and
`repairs_maintenance_spending` as percentages, `capital_budget_spending` as a signed variance
(negative = underspent). The `formula` field in the raw JSON is the authority — read it before
naming a column.
