#!/usr/bin/env python3
"""Build the identifier crosswalk across five South African municipal sources.

The problem this solves: every publisher keys municipalities differently, so every new
dataset starts with a matching project. Three of the five turn out to share an exact code,
which makes most of this deterministic and leaves only two sources needing name matching.

  IEC        prefix of the display name ("EC442 - Umzimvubu") == demarcation code   EXACT
  OpenAdminData  name.local is the demarcation code ("KZN263")                      EXACT
  Municipal Money  code column                                                      EXACT
  AGSA       slug + name + district, no code                                        NAME
  Stats SA P9115  name + district text                                              NAME

Outputs (relative to repo root):
  datasets/crosswalk/crosswalk.csv      one row per canonical entity
  datasets/crosswalk/unmatched.json     everything that did not match, with the reason
  datasets/crosswalk/README.md          rules, collisions, and what is unresolved

Reads from a checkout of the sources; paths are set below.
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HERE = REPO / "datasets"
OAD = Path.home() / "Projects/oss/south-africa-administrative-divisions/data"
RAW = Path.home() / "thinking/.raw/sa-manifestos"

STOP = {"district", "municipality", "local", "metropolitan", "metro", "city", "of", "the",
        "area", "management", "metropole"}
PREFIX = re.compile(r"^\s*[A-Za-z]{2,4}\d{0,3}\s*-\s*")


def norm(s):
    s = (s or "").strip()
    s = PREFIX.sub("", s)
    s = s.lower()
    s = re.sub(r"\(.*?\)", " ", s)
    # delete punctuation rather than turning it into a space: "O.R. Tambo" -> "or tambo",
    # not "o r tambo", which is what broke the first attempt at district names.
    s = re.sub(r"[^a-z0-9\s]", "", s)
    return " ".join(w for w in s.split() if w not in STOP)


def code_of(name):
    """IEC display names start with the demarcation code; strip it."""
    # codes are 3 letters + 3 digits (KZN435) or a 3-letter metro (NMA); 6 chars, not 5
    m = re.match(r"^\s*([A-Za-z]{2,4}\d{0,3})\s*-\s*", name or "")
    return m.group(1).upper() if m else None


def main():
    # ---- canonical spine: OpenAdminData municipalities + districts -------------
    rows = {}
    for x in json.load(open(OAD / "all-municipality.json")):
        code = x["name"]["local"].upper()
        level = "metro" if not re.fullmatch(r"[A-Z]{2,3}\d{3}", code) else "local"
        rows[code] = {
            "code": code, "oad_id": x["id"], "oad_name": x["name"]["en"],
            "oad_level": level, "province": x["ancestors"][0]["name"]["en"],
            "parent_code": x["parent"]["name"]["local"].upper(),
            "status": "live",
        }
    for x in json.load(open(OAD / "all-district.json")):
        code = x["name"]["local"].upper()
        if code in rows:          # metros appear as their own "district"; already a row
            continue
        rows[code] = {
            "code": code, "oad_id": x["id"], "oad_name": x["name"]["en"],
            "oad_level": "district", "province": x["ancestors"][0]["name"]["en"],
            "parent_code": None, "status": "live",
        }

    # ---- Municipal Money: exact code, plus disestablished entities -------------
    mm_by_code = {}
    for r in csv.DictReader(open(HERE / "municipal-money/municipalities-2026-11-10.csv")):
        mm_by_code[r["code"].upper()] = r
    for code, r in mm_by_code.items():
        if code not in rows:      # 37 disestablished pre-2016 entities
            rows[code] = {
                "code": code, "oad_id": None, "oad_name": None,
                "oad_level": r["geo_level"], "province": r["province"],
                "parent_code": r["parent_code"], "status": "disestablished",
            }

    # ---- IEC: prefix is the code ----------------------------------------------
    for year in ("2016", "2021"):
        for c in json.load(open(RAW / f"iec/councils-{year}.json"))["data"]:
            code = code_of(c["municipality"])
            if code and code in rows:
                rows[code][f"iec_{year}_name"] = c["municipality"]
            elif code:
                rows.setdefault(code, {"code": code, "status": "unknown"})[f"iec_{year}_name"] = c["municipality"]

    # ---- AGSA: name + province, unique only -----------------------------------
    districts = {}
    for key, items in json.load(open(RAW / "ago/allauditees.json")).items():
        if isinstance(items, list):
            for a in items:
                d = a.get("district") or {}
                districts[a["slug"]] = {
                    "province": (d.get("province") or {}).get("name"),
                    "district": d.get("name"),
                }
    name_idx = defaultdict(list)
    name_loose = defaultdict(list)      # spacing-insensitive second key: "o.r.tambo" vs "or tambo"
    for code, r in rows.items():
        for n in (r.get("oad_name"), (mm_by_code.get(code) or {}).get("name")):
            if n:
                name_idx[norm(n)].append(code)
                name_loose[norm(n).replace(" ", "")].append(code)

    agsa_unmatched = []
    for e in json.load(open(RAW / "ago/audit-opinions.json"))["data"]:
        meta = districts.get(e["slug"], {})
        cands = sorted(set(name_idx.get(norm(e["name"]), [])))   # oad + mm name share a code
        if not cands:
            cands = sorted(set(name_loose.get(norm(e["name"]).replace(" ", ""), [])))
        if meta.get("province"):
            prov = [c for c in cands if rows[c].get("province") == meta["province"]]
            cands = prov or cands
        if len(cands) == 1:
            rows[cands[0]]["agsa_slug"] = e["slug"]
            rows[cands[0]]["agsa_name"] = e["name"]
            rows[cands[0]]["agsa_type"] = e.get("type")
            rows[cands[0]]["agsa_district"] = meta.get("district")
            rows[cands[0]]["match_method_agsa_slug"] = "name+province"
        else:
            agsa_unmatched.append({"agsa_name": e["name"], "slug": e["slug"],
                                   "type": e.get("type"), "province": meta.get("province"),
                                   "district": meta.get("district"), "candidates": cands})

    # ---- Stats SA P9115: name + district --------------------------------------
    p9115_unmatched = []
    for p in json.load(open(HERE / "stats-sa-p9115/fbs-2023.json"))["data"]:
        cands = sorted(set(name_idx.get(norm(p["municipality"]), [])))
        if not cands:
            cands = sorted(set(name_loose.get(norm(p["municipality"]).replace(" ", ""), [])))
        if len(cands) > 1 and p.get("district"):
            cands = [c for c in cands if norm(rows[c].get("agsa_district") or "") == norm(p["district"])] or cands
        if len(cands) == 1:
            rows[cands[0]]["p9115_name"] = p["municipality"]
            rows[cands[0]]["p9115_district"] = p.get("district")
            rows[cands[0]]["match_method_p9115_name"] = "name"
        else:
            p9115_unmatched.append({"p9115_name": p["municipality"], "district": p.get("district"),
                                    "candidates": cands})

    # ---- second pass: resolve by elimination within a district ----------------
    # A rename should not need a hand-written alias if it can be proven. If an unmatched
    # AGSA/P9115 entity names district D, and exactly one child of D still lacks that
    # source, and exactly one unmatched row sits in D, the pairing is forced by
    # elimination -- not by string similarity. Recorded as its own match_method so the
    # inference is visible rather than looking like a name match that happened to work.
    def district_codes():
        return {norm(r.get("oad_name") or ""): c
                for c, r in rows.items() if r.get("oad_level") == "district"}

    def eliminate(unmatched, district_field, col, payload):
        dmap = district_codes()
        by_district = defaultdict(list)
        unresolved = []
        for u in unmatched:
            dcode = dmap.get(norm(u.get(district_field) or ""))
            if dcode:
                by_district[dcode].append(u)
            else:
                unresolved.append(u)
        fixed, ambiguous = 0, []
        for dcode, group in by_district.items():
            kids = [c for c, r in rows.items() if r.get("parent_code") == dcode and not r.get(col)]
            if len(group) == 1 and len(kids) == 1:
                rows[kids[0]].update(payload(group[0]))
                rows[kids[0]]["match_method_" + col] = "district-elimination"
                fixed += 1
            else:
                ambiguous.extend(group)
        return unresolved + ambiguous, fixed

    agsa_left, agsa_fixed = eliminate(
        agsa_unmatched, "district", "agsa_slug",
        lambda u: {"agsa_slug": u["slug"], "agsa_name": u["agsa_name"],
                   "agsa_type": u["type"], "agsa_district": u["district"] if "district" in u else None})
    p9115_left, p9115_fixed = eliminate(
        p9115_unmatched, "district", "p9115_name",
        lambda u: {"p9115_name": u["p9115_name"], "p9115_district": u["district"]})

    agsa_unmatched, p9115_unmatched = agsa_left, p9115_left
    print(f"  resolved by district elimination: AGSA {agsa_fixed}, P9115 {p9115_fixed}")

    # ---- write -----------------------------------------------------------------
    out = HERE / "crosswalk"
    out.mkdir(parents=True, exist_ok=True)
    cols = ["code", "oad_id", "oad_name", "oad_level", "province", "parent_code", "status",
            "iec_2016_name", "iec_2021_name", "agsa_slug", "agsa_name", "agsa_type",
            "agsa_district", "p9115_name", "p9115_district",
            "match_method_agsa_slug", "match_method_p9115_name"]
    ordered = sorted(rows.values(), key=lambda r: (r.get("oad_level") or "zz", r["code"]))
    with (out / "crosswalk.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(ordered)

    json.dump({"agsa_unmatched": agsa_unmatched, "p9115_unmatched": p9115_unmatched},
              open(out / "unmatched.json", "w"), indent=1)

    # ---- report ----------------------------------------------------------------
    n = len(ordered)
    def count(k):
        return sum(1 for r in ordered if r.get(k))
    print(f"canonical rows: {n}")
    print(f"  live vs disestablished: {sum(1 for r in ordered if r['status']=='live')} / "
          f"{sum(1 for r in ordered if r['status']=='disestablished')}")
    print(f"  by level: {dict((k, sum(1 for r in ordered if r['oad_level']==k)) for k in ('metro','local','district','municipality'))}")
    print(f"  MM code present : {sum(1 for c in mm_by_code if c in rows)}/{len(mm_by_code)}")
    print(f"  IEC 2016 / 2021 : {count('iec_2016_name')} / {count('iec_2021_name')}")
    print(f"  AGSA            : {count('agsa_slug')} matched, {len(agsa_unmatched)} unmatched")
    print(f"  P9115           : {count('p9115_name')} matched, {len(p9115_unmatched)} unmatched")
    unknown = [r['code'] for r in ordered if r.get('status') == 'unknown']
    if unknown:
        print(f"  codes with no spine row: {unknown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
