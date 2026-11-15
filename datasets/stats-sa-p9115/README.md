# Stats SA P9115 — free basic services per municipality

Derived 2026-11-09 from Table 12 of the P9115 2022/23 unit-data workbook. Publisher: Statistics
South Africa.

| File | What |
|---|---|
| `fbs-2023.json` | 257 municipalities: indigent households identified, beneficiaries of water / electricity / sanitation / waste, and the coverage ratios |
| `fbs-2023.csv` | the same, flat |

Coverage = beneficiaries ÷ identified, per service. It is the ratio parties' manifestos promise
to fix via the indigent register, so it doubles as a test of a promise.

**The workbook is not redistributed here.** Source:
`https://www.statssa.gov.za/publications/P9115/` → `P9115_2022 Unit Data.xlsx` (HTTP 200 on
2026-11-15), also archived by the Wayback Machine on 2024-06-29. Copy it to `/tmp` before
opening — `openpyxl` intermittently fails on btrfs.

**Do not rank parties on this.** A third of municipalities report zero beneficiaries and the rest
report near 100%; that is submission behaviour, not delivery.
