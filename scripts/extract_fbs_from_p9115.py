#!/usr/bin/env python3
"""Extract free-basic-services delivery per municipality from Stats SA P9115 (2023).

Table 12 of the unit-data workbook gives, per municipality:
  indigent households identified (2022, 2023)
  beneficiaries of free basic water / electricity / sewerage+sanitation / solid waste

Coverage = beneficiaries / identified, per service. That ratio is the thing four parties'
manifestos promise to fix (the "indigent register"), so it doubles as a test of a promise.

Usage: python3 extract_fbs_from_p9115.py /tmp/p9115.xlsx  (copy it out of the btrfs path;
openpyxl intermittently fails to open the file in place)
"""
import csv, json, os, sys

RAW = "/home/realtimshady16/thinking/.raw/sa-manifestos"
OUT_JSON = f"{RAW}/stats/fbs-2023.json"
OUT_CSV = f"{RAW}/stats/fbs-2023.csv"


def num(v):
    if v is None:
        return None
    s = str(v).replace(",", "").replace(" ", "").strip()
    if s in ("", "-", "N/A", "n/a"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def main(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Table 12"]
    rows, district = [], None
    for r in ws.iter_rows(min_row=7, values_only=True):
        d, m = (r[0] or "").strip() if isinstance(r[0], str) else r[0], r[1]
        if d:
            district = str(d).strip()
        if not m:
            continue
        name = str(m).strip()
        identified = num(r[3])            # 2023 column
        water, elec, san, waste = num(r[5]), num(r[7]), num(r[9]), num(r[11])
        rec = {"municipality": name, "district": district, "identified": identified,
               "benef_water": water, "benef_electricity": elec,
               "benef_sanitation": san, "benef_waste": waste}
        for k in ("water", "electricity", "sanitation", "waste"):
            b = rec[f"benef_{k}"]
            rec[f"coverage_{k}"] = round(b / identified, 4) if (b is not None and identified) else None
        rows.append(rec)

    os.makedirs(f"{RAW}/stats", exist_ok=True)
    json.dump({"source": "Stats SA P9115, Table 12, 2023 column", "count": len(rows),
               "data": rows}, open(OUT_JSON, "w"), indent=1)
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    over = [r for r in rows if (r["coverage_water"] or 0) > 1.05]
    print(f"{len(rows)} municipalities extracted")
    print(f"{len(over)} report more water beneficiaries than indigent households identified "
          f"(ratio > 1.05) — plausible when the register undercounts, but check the definition")
    for r in rows[:3]:
        print(f"  {r['municipality'][:34]:34} identified {r['identified']}  "
              f"water {r['coverage_water']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/p9115.xlsx")
