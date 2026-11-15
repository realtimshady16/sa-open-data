#!/usr/bin/env python3
"""Retry the AGSA auditees that returned HTTP 429 during the bulk sweep.

The sweep in fetch_ago_outcomes.py runs at 0.15 s/request, which AGSA rate-limits.
On 2026-11-10 that cost 18 of 257 auditees. This re-fetches *only* the recorded
failures, with real backoff, and merges them back into ago/audit-opinions.json and
ago/audit-opinions.csv. Idempotent: running it with nothing to do is a no-op.
"""
import csv
import json
import time
import urllib.error
import urllib.request

RAW = "/home/realtimshady16/thinking/.raw/sa-manifestos/ago"
BASE = "https://mfma-2025.agsa.co.za/api"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36")
CSV_FIELDS = ["municipality", "slug", "type", "period", "engagement",
              "opinion", "reliable", "useful", "late"]

WAITS = [15, 45, 90, 180]  # seconds, on successive 429s


def get(path, timeout=60):
    last = None
    for wait in WAITS + [None]:
        try:
            req = urllib.request.Request(BASE + path,
                                         headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "ignore"))
        except urllib.error.HTTPError as e:
            last = e
            if e.code != 429:
                raise
            if wait is None:
                raise
            retry_after = e.headers.get("Retry-After")
            nap = int(retry_after) if (retry_after or "").isdigit() else wait
            print(f"  429 on {path}; sleeping {nap}s", flush=True)
            time.sleep(nap)
    raise last


def flatten(entry):
    rows = []
    for o in entry.get("opinions") or []:
        rows.append({
            "municipality": entry.get("name"), "slug": entry.get("slug"),
            "type": entry.get("type"), "period": o.get("period"),
            "engagement": o.get("engagement"), "opinion": o.get("audit_opinion"),
            "reliable": o.get("information_reliable"),
            "useful": o.get("information_useful"),
            "late": o.get("not_submitted_in_time"),
        })
    return rows


def repair_groups(doc):
    """Fill in `group` for entries recovered by a retry, from allauditees.json.

    The bulk sweep sets group from the auditee list it walked; a retry only knows the
    slug, so recovered rows land with group=None. 18 rows did on 2026-11-10.
    """
    path = f"{RAW}/allauditees.json"
    try:
        groups = json.load(open(path))
    except FileNotFoundError:
        return 0
    by_slug = {}
    for key, items in groups.items():
        if isinstance(items, list):
            for a in items:
                if isinstance(a, dict) and a.get("slug"):
                    by_slug[a["slug"]] = key
    fixed = 0
    for e in doc["data"]:
        if not e.get("group") and e.get("slug") in by_slug:
            e["group"] = by_slug[e["slug"]]
            fixed += 1
    return fixed


def main():
    doc = json.load(open(f"{RAW}/audit-opinions.json"))
    todo = [(slug, err) for slug, err in doc.get("failed", [])]
    if not todo:
        fixed = repair_groups(doc)
        if not fixed:
            print("nothing to retry")
            return
        print(f"no retries needed; repaired {fixed} missing group values")
        todo = []

    by_slug = {e["slug"]: e for e in doc["data"]}
    still_failed, added = [], 0
    for i, (slug, _err) in enumerate(todo, 1):
        try:
            d = get(f"/municipalities/{slug}").get("data") or {}
            ops = d.get("audit_opinions") or []
            by_slug[slug] = {
                "id": d.get("id"), "auditee_id": d.get("auditee_id"),
                "name": d.get("name"), "slug": slug, "type": d.get("type"),
                "group": (by_slug.get(slug) or {}).get("group"),
                "district_id": d.get("district_id"),
                "required_intervention": d.get("required_intervention"),
                "opinions": [
                    {k: o.get(k) for k in ("period", "engagement", "audit_opinion",
                                           "opinion_evaluation", "information_reliable",
                                           "information_useful", "not_submitted_in_time")}
                    for o in ops],
            }
            added += 1
            print(f"[{i}/{len(todo)}] {d.get('name')}: {len(ops)} periods", flush=True)
        except Exception as e:  # keep whatever we could not get, honestly
            still_failed.append([slug, str(e)])
            print(f"[{i}/{len(todo)}] STILL FAIL {slug}: {e}", flush=True)
        time.sleep(4)

    data = sorted(by_slug.values(), key=lambda e: e.get("name") or "")
    doc["data"] = data
    doc["municipalities"] = len(data)
    doc["failed"] = still_failed
    doc["retriedAt"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    repair_groups(doc)
    json.dump(doc, open(f"{RAW}/audit-opinions.json", "w"), indent=1)

    rows = []
    for e in data:
        rows.extend(flatten(e))
    with open(f"{RAW}/audit-opinions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"\nrecovered {added}/{len(todo)}; {len(data)} municipalities, "
          f"{len(rows)} opinion rows; {len(still_failed)} still failing")


if __name__ == "__main__":
    main()
