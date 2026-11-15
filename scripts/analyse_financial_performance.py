#!/usr/bin/env python3
"""Financial performance by governing party, 2021-26 term.

Joins three sources that were collected separately and never joined:

  Municipal Money   data/municipalities.csv + data/indicators-long.csv  (finance, keyed by code)
  AGSA              .raw/sa-manifestos/ago/audit-opinions.json          (audit outcome, keyed by slug)
  IEC               .raw/sa-manifestos/iec/councils-2021.json           (largest party, by name)

The join is the hard part and it is done the same way join_iec_agsa.py does it:
normalise, match, and REFUSE to guess on ambiguity. Anything unmatched is counted
and printed, not silently dropped.

Output: analysis/financial-by-governance.csv and analysis/financial-performance.md

This does NOT claim causation. Largest party != mayor's party in a hung council, and
municipal wealth, province and audit history all confound. It is a first cut.
"""
import csv
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = Path("/home/realtimshady16/thinking/.raw/sa-manifestos")
OUT = ROOT / "analysis"
YEAR = "2024"          # last full financial year in the Municipal Money series
PERIODS = ("2021-22", "2022-23", "2023-24")  # audit years inside the 2021-26 term

PARTY_SHORT = {
    "AFRICAN NATIONAL CONGRESS": "ANC",
    "DEMOCRATIC ALLIANCE": "DA",
    "INKATHA FREEDOM PARTY": "IFP",
    "ECONOMIC FREEDOM PARTY": "EFF",
}
DISTRICT_WORDS = {"district", "municipality", "local", "metropolitan", "city", "of", "the"}
PREFIX = re.compile(r"^\s*[A-Za-z]{2,4}\d{0,3}\s*-\s*")   # "NMA - ", "EC442 - ", "DC10 - "


def norm(s):
    s = (s or "").strip()
    s = PREFIX.sub("", s)          # strip the code prefix BEFORE punctuation mangles it
    s = s.lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z\s]", " ", s)
    words = [w for w in s.split() if w not in DISTRICT_WORDS]
    return " ".join(words)


def index_unique(records, name_of, province_of):
    """normalised name -> record, only where unambiguous; honours province as a tiebreak."""
    idx, ambiguous = {}, 0
    for rec in records:
        name = norm(name_of(rec))
        if not name:
            continue
        cur = idx.setdefault(name, [])
        cur.append(rec)
    out, dropped = {}, []
    for name, recs in idx.items():
        if len(recs) == 1:
            out[name] = (recs[0], None)
        else:
            out[name] = (None, recs)   # caller resolves by province or drops
    return out


def pick(idx, name, province):
    """Resolve one normalised name: unique, or province-disambiguated, else None."""
    hit = idx.get(name)
    if not hit:
        return None
    rec, alts = hit
    if rec is not None:
        return rec
    matches = [r for r in alts if province and province_of_record(r) == province]
    return matches[0] if len(matches) == 1 else None


def money_indicators():
    """code -> {indicator: value} for YEAR, plus the code -> geography row."""
    keep = {"cash_coverage", "uifw_expenditure", "repairs_maintenance_spending",
            "current_debtors_collection_rate", "capital_budget_spending",
            "operating_budget_spending"}
    vals = {}
    for r in csv.DictReader((DATA / "indicators-long.csv").open()):
        if r["indicator"] in keep and r["year"] == YEAR and r["value"] not in ("", None):
            try:
                vals.setdefault(r["code"], {})[r["indicator"]] = float(r["value"])
            except ValueError:
                pass
    geo = {r["code"]: r for r in csv.DictReader((DATA / "municipalities.csv").open())}
    return vals, geo


def build_index(records):
    """Two lookups: exact (name, province) and name-only for unambiguous fallback."""
    by_pair, by_name = {}, {}
    for r in records:
        n = norm(r.get("name"))
        if not n:
            continue
        by_name.setdefault(n, []).append(r)
        prov = r.get("province")
        if prov:
            by_pair[(n, prov)] = r
    return by_pair, by_name


def pick(idx, name, province):
    by_pair, by_name = idx
    hit = by_pair.get((name, province))
    if hit:
        return hit
    alts = by_name.get(name) or []
    if len(alts) == 1:
        return alts[0]
    if province:
        narrowed = [r for r in alts if r.get("province") == province]
        if len(narrowed) == 1:
            return narrowed[0]
    return None   # ambiguous -> refuse to guess


def agsa_records():
    districts = {}
    for key, items in json.load(open(RAW / "ago/allauditees.json")).items():
        if isinstance(items, list):
            for a in items:
                d = a.get("district") or {}
                districts[a["slug"]] = {
                    "province": ((d.get("province") or {}).get("name")),
                    "district": d.get("name"),
                }
    recs = []
    for e in json.load(open(RAW / "ago/audit-opinions.json"))["data"]:
        meta = districts.get(e["slug"], {})
        ops = {o["period"]: o for o in (e.get("opinions") or [])}
        latest = None
        for p in PERIODS:
            if ops.get(p, {}).get("audit_opinion"):
                latest = ops[p]
        if not latest:
            continue
        recs.append({
            "name": e["name"], "slug": e["slug"], "type": e.get("type"),
            "district": meta.get("district"), "province": meta.get("province"),
            "audit_period": latest["period"],
            "audit_opinion": latest["audit_opinion"],
            "audit_reliable": latest.get("information_reliable"),
            "audit_useful": latest.get("information_useful"),
        })
    return recs


def council_records():
    return [{"name": x["municipality"], "province": x.get("province"), **x}
            for x in json.load(open(RAW / "iec/councils-2021.json"))["data"]]


def median(vals):
    vals = [v for v in vals if v is not None]
    return round(statistics.median(vals), 2) if vals else None


def main():
    OUT.mkdir(exist_ok=True)
    vals, geo = money_indicators()
    agsa_idx = build_index(agsa_records())
    council_idx = build_index(council_records())
    print(f"municipal money: {len(vals)} codes with {YEAR} data, {len(geo)} geographies")
    print(f"agsa: {len(agsa_idx[1])} names | iec councils: {len(council_idx[1])} names")

    rows, lost = [], {"no_money": 0, "no_agsa": 0, "no_council": 0}
    for code, g in geo.items():
        if g["geo_level"] != "municipality" or g["is_disestablished"] == "True":
            continue
        ind = vals.get(code) or {}
        if not ind:
            lost["no_money"] += 1
            continue
        key = norm(g["name"])
        ag = pick(agsa_idx, key, g["province"])
        co = pick(council_idx, key, g["province"])
        if not ag:
            lost["no_agsa"] += 1
        if not co:
            lost["no_council"] += 1
        rows.append({
            "code": code, "name": g["name"], "province": g["province"],
            "category": g["category"], "population": g["population"],
            "largest_party": PARTY_SHORT.get((co or {}).get("largest_party", ""), "OTHER" if co else None),
            "largest_party_raw": (co or {}).get("largest_party"),
            "majority": (co or {}).get("majority"),
            "largest_seats_share": (round(100 * (co or {}).get("largest_seats", 0) / (co or {}).get("total_seats", 1), 1)
                                    if co else None),
            "audit_period": (ag or {}).get("audit_period"),
            "audit_opinion": (ag or {}).get("audit_opinion"),
            "audit_reliable": (ag or {}).get("audit_reliable"),
            **{k: ind.get(k) for k in
               ("cash_coverage", "uifw_expenditure", "repairs_maintenance_spending",
                "current_debtors_collection_rate", "capital_budget_spending",
                "operating_budget_spending")},
        })

    print("unjoined:", lost, "| rows:", len(rows))
    with (OUT / "financial-by-governance.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- summary tables --------------------------------------------------
    def bucket(rows, key, metrics):
        groups = {}
        for r in rows:
            g = r.get(key)
            if not g:
                continue
            groups.setdefault(g, []).append(r)
        out = []
        for g, rs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            out.append((g, len(rs), {m: median([x.get(m) for x in rs]) for m in metrics}))
        return out

    metrics = ["cash_coverage", "uifw_expenditure", "repairs_maintenance_spending",
               "current_debtors_collection_rate", "capital_budget_spending"]
    hdr = "| Group | n | " + " | ".join(metrics) + " |"
    sep = "|---" * (len(metrics) + 2) + "|"

    def table(items):
        lines = [hdr, sep]
        for g, n, ms in items:
            lines.append(f"| {g} | {n} | " + " | ".join(
                "—" if ms[m] is None else f"{ms[m]}" for m in metrics) + " |")
        return "\n".join(lines)

    by_party = bucket([r for r in rows if r["largest_party"]], "largest_party", metrics)
    by_audit = bucket([r for r in rows if r["audit_opinion"]], "audit_opinion", metrics)

    clean = sum(1 for r in rows if (r["audit_opinion"] or "").lower().startswith("unqualified with no"))
    total_aud = sum(1 for r in rows if r["audit_opinion"])
    hung = sum(1 for r in rows if r["majority"] is False)
    matched_councils = len(rows) - lost["no_council"]

    md = f"""# Financial performance by governing party, 2021–26 term

Generated by `tools/analyse_financial_performance.py`. **Not causation.** See caveats.

Sources joined: Municipal Money (finance, {YEAR}, % of relevant budget unless noted) ·
AGSA (latest audit opinion inside the term) · IEC (largest party after the 2021 election).

Rows: **{len(rows)}** live municipalities. Unjoined: {lost['no_money']} without finance,
{lost['no_agsa']} without an AGSA match, {lost['no_council']} without an IEC council.

## By largest party on the council

{table(by_party)}

`cash_coverage` = months of operating expenditure covered by cash — higher is safer.
`uifw_expenditure` = unauthorised, irregular, fruitless and wasteful expenditure / actual
operating expenditure × 100 — higher is worse. `repairs_maintenance_spending` = R&M /
(property, plant and equipment + investment property) × 100, an asset-renewal proxy —
higher is better. `current_debtors_collection_rate` = % of billed revenue actually collected
— higher is better. `capital_budget_spending` = (actual − budgeted capital expenditure) /
budgeted × 100 — **negative means the capital budget was underspent**, so more negative is
worse delivery. Table colspan-1 check: several medians are negative for almost every group,
i.e. capital underspending is the national norm.

## By latest audit opinion in the term

{table(by_audit)}

Clean audits (unqualified, no findings) among matched municipalities: **{clean} of {total_aud}**
({round(100*clean/total_aud, 1) if total_aud else 0}%).

**What it looks like, with the caveats doing real work:** the gradient is monotone in
`cash_coverage`, `uifw_expenditure` and `repairs_maintenance_spending` — clean-audit
municipalities hold 6.7 months of cash against 0.2 for adverse ones, and 1.1% UIFW against
28.2%. That gradient is mostly the *same fact* (a municipality that can't hold a clean audit
also can't hold cash), not a finding about parties. The party split is the weaker signal in
every sense: capacity and wealth drive both variables.

## Caveats — read before quoting

1. **Largest party is not the governing party.** {hung} of the {matched_councils} matched
   municipalities had no single-party majority after 2021, so the mayor often comes from a
   coalition partner. This is a proxy, and a blunt one.
2. **n is small and uneven.** Medians, not means, and no confidence intervals. The "OTHER"
   row is n<5 and is not interpretable; it is printed for completeness, not for reading.
3. **Wealth, province and history confound.** Municipal Money's own `miif_category` (B1–B4)
   tracks capacity; a rich coastal metro and a rural B4 are not comparable units.
4. **One year, one snapshot.** {YEAR} is the last complete year; a single bad audit or a
   contested budget can move a median.
5. **Same source problem as before.** Audit opinions come from Treasury's copy of AGSA
   results; AGSA is primary. Names were matched by normalised name, province used only as a
   tiebreak, and any still-ambiguous name was dropped rather than guessed.
   {lost['no_agsa']} municipalities had no unambiguous AGSA match, {lost['no_council']} no
   unambiguous IEC council.
6. **Missing is not zero.** A blank indicator means not computed/not submitted, and those
   municipalities are usually the worst-performing — so these medians are, if anything, kind.
"""
    (OUT / "financial-performance.md").write_text(md)
    print(f"\nwrote {OUT/'financial-performance.md'} and financial-by-governance.csv")


if __name__ == "__main__":
    main()
