# IEC — council composition, 2016 and 2021

Captured 2026-11-09 from the Electoral Commission's results site. 213 councils per election.

| File | What |
|---|---|
| `councils-2016.json` | seats by party, largest party, majority flag, total seats, per council |
| `councils-2021.json` | same for 2021 |

Municipality names carry a prefix (`NMA - Nelson Mandela Bay`, `EC442 - Umzimvubu`), which is a
join hazard: strip the prefix **before** stripping punctuation, or every code survives as a word
and 193 of 200 matches fail.

In the 2021–26 term, 70 of 213 councils had no single-party majority. Largest party is not the
governing party in those.

**Preservation note:** `results.elections.org.za` is live, but the Wayback Machine holds no
usable capture — one 302 from 2021 and a page of 404s. `api.elections.org.za/api/v1/` returned
404 on reprobe 2026-11-15.
