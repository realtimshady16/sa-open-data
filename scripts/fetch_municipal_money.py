#!/usr/bin/env python3
"""Fetch Municipal Money's public municipal profiles into the project.

Municipal Money is National Treasury data, run by OpenUp. Two paginated GETs
cover the whole country (292 records as of 2026-11-10), so this is API use, not
crawling. robots.txt still says `Crawl-Delay: 120`; we are more polite than
needed anyway (2 s between requests, one descriptive UA, no parallel calls).

Writes into data/:
  municipal-profiles-<date>.json   raw combined API payload
  geography-<date>.json            names, province, category, disestablished flag
  municipalities.csv               one row per entity, wide
  indicators-long.csv              entity x year x indicator
  PROVENANCE.md                    endpoints, counts, caveats

Idempotent and re-runnable. Nothing here interprets the data.
"""
from __future__ import annotations

import csv
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://municipalmoney.gov.za/api"
UA = "hellotim.co.za civic-data collection (tim@hellotim.co.za)"
PAGE = 150
SLEEP = 2.0
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

fetched = []


def get(url: str) -> tuple[object, int]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read()
        status = r.status
    fetched.append({"url": url, "status": status, "bytes": len(body)})
    time.sleep(SLEEP)
    return json.loads(body), status


def main() -> int:
    DATA.mkdir(exist_ok=True)

    profiles, offset = [], 0
    while True:
        payload, status = get(f"{BASE}/municipality-profile/?limit={PAGE}&offset={offset}")
        if status != 200:
            print(f"FAIL page offset={offset} status={status}", file=sys.stderr)
            return 1
        results = payload.get("results", [])
        profiles.extend(results)
        print(f"page offset={offset:<4} got {len(results):>3}  total {len(profiles):>3} / {payload.get('count')}")
        if not payload.get("next") or not results:
            break
        offset += PAGE

    geo_raw, _ = get(f"{BASE}/geography/geography/")
    # Districts are in the profile API too (DC*), so do not filter to local level.
    geo = {g["geo_code"]: g for g in geo_raw if g.get("geo_code")}

    # ---- wide table -------------------------------------------------------
    wide_fields = [
        "code", "name", "long_name", "province", "geo_level", "category", "miif_category",
        "is_disestablished", "population", "square_kms", "parent_code", "parent_level",
        "website", "phone", "latest_audit_year", "latest_audit_result", "latest_audit_rating",
        "audit_years_with_opinion", "audit_years_missing",
        "grants_snapshot_year", "grants_snapshot_quarter",
        "mayor_name", "mayor_role", "demarcation_land_lost", "demarcation_land_gained",
    ]
    rows = []
    for p in profiles:
        code = p.get("demarcation", {}).get("code")
        g = geo.get(code, {})
        opinions = sorted(p.get("audit_opinions", {}).get("values", []),
                          key=lambda x: x.get("date") or 0)
        with_op = [o for o in opinions if o.get("result")]
        latest = with_op[-1] if with_op else {}
        officials = p.get("mayoral_staff", {}).get("officials") or []
        mayor = next((o for o in officials if "Mayor" in (o.get("role") or "")), officials[0] if officials else {})
        contact = p.get("muni_contact", {})
        grants = p.get("indicators", {}).get("grants", {}) or {}
        snap = grants.get("snapshot_date") or {}
        dem = p.get("demarcation", {})
        rows.append({
            "code": code,
            "name": g.get("name"),
            "long_name": g.get("long_name"),
            "province": g.get("province_name"),
            "geo_level": g.get("geo_level"),
            "category": g.get("category"),
            "miif_category": g.get("miif_category"),
            "is_disestablished": g.get("is_disestablished"),
            "population": g.get("population"),
            "square_kms": g.get("square_kms"),
            "parent_code": g.get("parent_code"),
            "parent_level": g.get("parent_level"),
            "website": contact.get("url") or g.get("url"),
            "phone": contact.get("phone_number") or g.get("phone_number"),
            "latest_audit_year": latest.get("date"),
            "latest_audit_result": latest.get("result"),
            "latest_audit_rating": latest.get("rating"),
            "audit_years_with_opinion": len(with_op),
            "audit_years_missing": len(opinions) - len(with_op),
            "grants_snapshot_year": snap.get("year"),
            "grants_snapshot_quarter": snap.get("quarter"),
            "mayor_name": mayor.get("name"),
            "mayor_role": mayor.get("role"),
            "demarcation_land_lost": len(dem.get("land_lost") or []),
            "demarcation_land_gained": len(dem.get("land_gained") or []),
        })
    rows.sort(key=lambda r: (r["code"] or ""))
    with (DATA / "municipalities.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=wide_fields)
        w.writeheader()
        w.writerows(rows)

    # ---- long indicator table --------------------------------------------
    long_rows = []
    for p in profiles:
        code = p.get("demarcation", {}).get("code")
        ind = p.get("indicators", {}) or {}
        for name, block in ind.items():
            if not isinstance(block, dict):
                continue
            for v in block.get("values") or []:
                if not isinstance(v, dict):
                    continue
                long_rows.append({
                    "code": code, "indicator": name, "year": v.get("date"),
                    "value": v.get("result"), "rating": v.get("rating"),
                    "cube_version": v.get("cube_version"),
                })
            totals = block.get("totals")
            if isinstance(totals, dict):
                for year, fields in totals.items():
                    if not isinstance(fields, dict):
                        continue
                    for scope, val in fields.items():
                        long_rows.append({
                            "code": code, "indicator": f"grants_totals_{scope}",
                            "year": year, "value": val, "rating": None,
                            "cube_version": None,
                        })
    long_rows.sort(key=lambda r: (r["code"] or "", r["indicator"], str(r["year"])))
    with (DATA / "indicators-long.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["code", "indicator", "year", "value", "rating", "cube_version"])
        w.writeheader()
        w.writerows(long_rows)

    # ---- raw payloads -----------------------------------------------------
    (DATA / f"municipal-profiles-{TODAY}.json").write_text(json.dumps(profiles, indent=1))
    (DATA / f"geography-{TODAY}.json").write_text(json.dumps(geo_raw, indent=1))

    # ---- provenance -------------------------------------------------------
    n_geo = len(geo)
    live = sum(1 for r in rows if not r["is_disestablished"])
    dead = sum(1 for r in rows if r["is_disestablished"])
    with (DATA / "PROVENANCE.md").open("w") as f:
        f.write(f"""# Municipal Money collection — {TODAY}

Generated by `tools/fetch_municipal_money.py`. Do not hand-edit the CSVs; re-run.

| | |
|---|---|
| Publisher | National Treasury, via Municipal Money (built and run by OpenUp) |
| Base | `{BASE}` |
| User agent | `{UA}` |
| Requests | {len(fetched)}, {SLEEP:.0f} s apart, sequential |
| Records | {len(profiles)} municipal profiles, {n_geo} municipal geographies |
| Live / disestablished | {live} / {dead} |
| Licence | **not stated on the API** — treat as Treasury public data pending confirmation |
| robots.txt | `User-agent: *` / `Allow: /` / `Crawl-Delay: 120` |

## Requests

| URL | Status | Bytes |
|---|---|---|
""" + "".join(f"| `{r['url']}` | {r['status']} | {r['bytes']:,} |\n" for r in fetched) + f"""
## Notes and caveats

- **{len(profiles)} records vs 257 auditees.** The API includes disestablished
  municipalities (`is_disestablished: true`), which is why the count exceeds the
  AGSA auditee list. This is not an error and it is not the same population —
  join on `code`, never on count.
- `geography/geography/` returns the whole country in one response; it ignores
  `limit`. Names, province, `geo_level` (municipality/district), `category` (A/B/C),
  population and the disestablished flag come from there, joined on `geo_code` =
  `demarcation.code`. **Keep districts**: 44 of the {len(profiles)} profiles are
  district codes (`DC*`), and filtering geography to local level leaves them nameless.
- The site sitemap lists 295 profile URLs against {len(profiles)} API records.
  Unreconciled; do not assume the sitemap is complete or current.
- `audit_opinions` in the API is Treasury's copy of AGSA results. AGSA remains
  the primary source for audit outcomes; this copy is convenient, not authoritative.
- Indicator values carry `cube_version` (`v2`) and sometimes `rating`/`result` null.
  Null means *not computed*, not zero.
""")

    print(f"\nwrote {DATA}")
    for p in sorted(DATA.iterdir()):
        print(f"  {p.name:<34} {p.stat().st_size:>10,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
