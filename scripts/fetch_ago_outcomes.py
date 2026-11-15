#!/usr/bin/env python3
"""Collect Auditor-General MFMA audit outcomes per municipality.

AGSA's 2024-25 local government site is a JS app, but its JSON API is open:
  GET /api/allauditees                → every auditee (municipalities + entities)
  GET /api/municipalities/{slug}      → metadata + audit_opinions[] per period

Output: ago/audit-opinions.json (per municipality, per period) and a flat CSV. This is the
input for the performance axis: audit outcome x governing party x term. It deliberately does
NOT join to IEC results or to governance — that join is a separate step with its own matching
problem (names differ: "NMA - Nelson Mandela Bay" vs "Nelson Mandela Bay").
"""
import csv, json, os, time, urllib.error, urllib.request

RAW = "/home/realtimshady16/thinking/.raw/sa-manifestos/ago"
BASE = "https://mfma-2025.agsa.co.za/api"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
os.makedirs(RAW, exist_ok=True)


def get(path, timeout=45):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA, "Accept": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "ignore"))
        except urllib.error.HTTPError as e:
            # AGSA rate-limits this endpoint. On 2026-11-10 a 0.15 s cadence cost
            # 18 of 257 auditees to HTTP 429. Back off properly; retry_ago_failures.py
            # recovers anything still missing.
            if attempt == 2:
                raise
            nap = 30 * (attempt + 1) if e.code == 429 else 2 * (attempt + 1)
            print(f"  {e.code} on {path}; sleeping {nap}s", flush=True)
            time.sleep(nap)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def main():
    auditees = get("/allauditees")
    # Response is grouped by type: LM local, DM district, MET metro, ME municipal entity,
    # ICM holds the remaining local municipalities (166 LM + 39 ICM = 205 local). ME = entities.
    groups = {k: v for k, v in auditees.items() if isinstance(v, list)}
    print({k: len(v) for k, v in groups.items()}, flush=True)
    rows = []
    for key in ("LM", "DM", "MET", "ICM"):
        for r in groups.get(key, []):
            r = dict(r)
            r["group"] = key
            rows.append(r)
    print(f"{len(rows)} municipalities to fetch", flush=True)

    out, flat, failed = [], [], []
    for i, a in enumerate(rows, 1):
        slug = a.get("slug")
        try:
            d = get(f"/municipalities/{slug}")
        except Exception as e:
            failed.append((slug, repr(e)[:80]))
            print(f"[{i}/{len(rows)}] FAIL {slug}", flush=True)
            continue
        data = d.get("data") or {}
        ops = data.get("audit_opinions") or []
        out.append({
            "id": data.get("id"), "auditee_id": data.get("auditee_id"),
            "name": data.get("name"), "slug": slug, "type": data.get("type"),
            "group": a.get("group"),
            "district_id": data.get("district_id"),
            "required_intervention": data.get("required_intervention"),
            "opinions": [
                {k: o.get(k) for k in ("period", "engagement", "audit_opinion",
                                       "opinion_evaluation", "information_reliable",
                                       "information_useful", "not_submitted_in_time")}
                for o in ops],
        })
        for o in ops:
            flat.append({
                "municipality": data.get("name"), "slug": slug, "type": data.get("type"),
                "period": o.get("period"), "engagement": o.get("engagement"),
                "opinion": o.get("audit_opinion"),
                "reliable": o.get("information_reliable"),
                "useful": o.get("information_useful"),
                "late": o.get("not_submitted_in_time"),
            })
        if i % 20 == 0:
            print(f"[{i}/{len(rows)}] {data.get('name')}: {len(ops)} periods", flush=True)
        time.sleep(0.6)

    json.dump({"generatedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "municipalities": len(out), "failed": failed, "data": out},
              open(f"{RAW}/audit-opinions.json", "w"), indent=1)
    with open(f"{RAW}/audit-opinions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(flat[0].keys()))
        w.writeheader()
        w.writerows(flat)

    periods = sorted({r["period"] for r in flat})
    print(f"\n{len(out)} municipalities, {len(flat)} opinion rows, periods {periods}", flush=True)
    print(f"{len(failed)} failures", flush=True)
    for p in periods:
        opt = {}
        for r in flat:
            if r["period"] == p and r["engagement"] == "FA":
                opt[r["opinion"]] = opt.get(r["opinion"], 0) + 1
        print(f"  {p}: {opt}", flush=True)


if __name__ == "__main__":
    main()
