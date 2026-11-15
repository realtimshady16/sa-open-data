# SA open data — a preserved copy

A small, verifiable archive of South African public datasets, captured **2026-11-09 to
2026-11-10** while working on local-government politics and party performance. Published here
for one reason: **none of these three sources is preserved anywhere else, and two of them are
scheduled to disappear.**

This is not a data portal and it is not maintained as a service. It is a record: here is what
the data said, here is when it was taken, here is the checksum, here is the script that took
it. You can reproduce every byte.

## Why this exists

The 2026 public record of South African local government has three legs:

| Source | Publisher | Archive status (checked 2026-11-15) |
|---|---|---|
| Municipal Money | National Treasury / OpenUp | live; **no preservation plan needed** — but bulk API may change |
| AGSA MFMA audit outcomes | Auditor-General | **year-stamped site** (`mfma-2025`). Wayback holds exactly one capture: the landing page. The API is not archived. When `mfma-2026` replaces it, this data goes with it |
| IEC council results | Electoral Commission | `results.elections.org.za` is live, but Wayback holds **no usable captures** — one 302 from 2021 and a page of 404s |

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
MANIFEST.json             size, sha256, row/record counts, source URL per file
LICENCE-OPTIONS.md        undecided — see below
```

## Verify it

Every file's sha256 is in `MANIFEST.json`. To check the tree matches what was published:

```bash
python3 - <<'EOF'
import hashlib, json
man = json.load(open("MANIFEST.json"))
bad = 0
for e in man["files"]:
    h = hashlib.sha256(open(e["path"], "rb").read()).hexdigest()
    if h != e["sha256"]:
        bad += 1
        print("MISMATCH", e["path"])
print("ok" if not bad else f"{bad} mismatched")
EOF
```

## Licence

**Not yet chosen** — `LICENCE-OPTIONS.md` lays out the choices and what each one costs. Until a
licence is committed, the default is all rights reserved, and this repository should be read
as a citation record rather than as a dataset you may redistribute.

The underlying statistics are not ours to license. They are produced by National Treasury,
the Auditor-General, the IEC and Statistics South Africa from public money. What is ours to
license is the arrangement, the derived tables and the documentation — and even that is a
modest claim, since facts are not copyrightable.

## Data quality

`docs/coverage-and-caveats.md` lists the specific things that will bite anyone reusing this:
the difference between 292 profiles and 257 auditees, two municipalities called Emalahleni,
the sign convention on capital spending, and the fact that a null indicator means *not
computed*, never zero. Read it before quoting a number.
