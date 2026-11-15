#!/usr/bin/env python3
"""Generate a static site from the repository's data. No server, no build tool, no network.

One page per municipality, plus an index. Everything is derived from files already in
datasets/, joined through datasets/crosswalk/crosswalk.csv. Output goes to site/ which is
git-ignored: the site is a view of the data, not part of the record.

    python3 tools/build_site.py && python3 -m http.server -d site 8000
"""
import csv
import html
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "datasets"
OUT = ROOT / "site"

CSS = """
:root{--bg:#141110;--fg:#e8ded2;--dim:#a89684;--line:#2e2723;--acc:#c9743a;--ok:#6d8f6a;--bad:#a8503f}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
     font:17px/1.65 ui-serif,Georgia,"Iowan Old Style",serif;padding:2rem 1.25rem 5rem}
main{max-width:60rem;margin:0 auto}
a{color:var(--acc);text-decoration:none;border-bottom:1px solid rgba(201,116,58,.35)}
a:hover{border-bottom-color:var(--acc)}
h1{font-size:2.1rem;line-height:1.15;margin:.2rem 0 1.4rem;letter-spacing:-.02em}
h2{font-size:.78rem;text-transform:uppercase;letter-spacing:.14em;color:var(--dim);
   margin:2.6rem 0 .7rem;font-family:ui-sans-serif,system-ui,sans-serif;font-weight:600}
.kicker{color:var(--dim);font-size:.8rem;text-transform:uppercase;letter-spacing:.16em;
        font-family:ui-sans-serif,system-ui,sans-serif}
table{width:100%;border-collapse:collapse;font-size:.95rem}
th,td{text-align:left;padding:.45rem .5rem;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--dim);font-weight:600;font-size:.78rem;text-transform:uppercase;letter-spacing:.1em;
   font-family:ui-sans-serif,system-ui,sans-serif}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr));gap:1rem;margin:1rem 0}
.card{border:1px solid var(--line);padding:.8rem .9rem;border-radius:3px}
.card .v{font-size:1.5rem;font-variant-numeric:tabular-nums}
.card .l{color:var(--dim);font-size:.74rem;text-transform:uppercase;letter-spacing:.1em}
.note{color:var(--dim);font-size:.88rem;border-left:2px solid var(--line);padding-left:.9rem}
.ok{color:var(--ok)}.bad{color:var(--bad)}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);
       color:var(--dim);font-size:.82rem}
"""


def esc(v):
    return html.escape("" if v is None else str(v))


def num(v, dp=1, suffix=""):
    if v in (None, "", "None"):
        return "—"
    try:
        f = float(v)
    except ValueError:
        return esc(v)
    return f"{f:,.{dp}f}{suffix}"


def main():
    OUT.mkdir(exist_ok=True)
    xwalk = list(csv.DictReader(open(D / "crosswalk/crosswalk.csv")))
    mm = {r["code"]: r for r in csv.DictReader(open(D / "municipal-money/municipalities-2026-11-10.csv"))}
    ind = defaultdict(dict)
    for r in csv.DictReader(open(D / "municipal-money/indicators-long-2026-11-10.csv")):
        if r["year"] == "2024" and r["value"]:
            ind[r["code"]][r["indicator"]] = r["value"]
    agsa = {e["slug"]: e for e in json.load(open(D / "agsa-audit-outcomes/audit-opinions-2026-11-10.json"))["data"]}
    council = {c["municipality"]: c for c in json.load(open(D / "iec-councils/councils-2021.json"))["data"]}

    def public(r):
        return r["status"] == "live" and r["oad_level"] in ("metro", "local", "district")

    cards = []
    for r in sorted((x for x in xwalk if public(x)), key=lambda r: r["oad_name"] or r["code"]):
        code = r["code"]
        m = mm.get(code, {})
        ags = agsa.get(r["agsa_slug"] or "", {})
        co = council.get(r["iec_2021_name"] or "", {})
        i = ind.get(code, {})
        slug = f"{code}-{(r['oad_name'] or code).lower().replace(' ', '-')}"
        slug = "".join(ch for ch in slug if ch.isalnum() or ch in "-_")
        cards.append((slug, r, m, ags, co, i))

    # ---- index ---------------------------------------------------------------
    rows = []
    for slug, r, m, ags, co, i in cards:
        op = (ags.get("opinions") or [{}])
        latest = next((o for o in reversed(op) if o.get("audit_opinion")), {})
        opinion = latest.get("audit_opinion") or ""
        klass = "ok" if opinion.startswith("Unqualified with no") else ("bad" if opinion else "")
        rows.append(f"""<tr><td><a href="{slug}.html">{esc(r['oad_name'] or r['code'])}</a></td>
<td>{esc(r['province'])}</td><td>{esc(m.get('category') or '')}</td>
<td>{num(m.get('population'), 0)}</td>
<td>{esc((co.get('largest_party') or '').title().replace('African National Congress','ANC').replace('Democratic Alliance','DA').replace('Economic Freedom Party','EFF'))}</td>
<td class="{klass}">{esc(opinion)}</td>
<td class="num">{num(i.get('cash_coverage'))}</td></tr>""")

    index = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>South African municipalities — {len(cards)} places, one table</title>
<style>{CSS}</style></head><body><main>
<div class="kicker">SA open data · local view</div>
<h1>Every South African municipality,<br>and what its books say</h1>
<p class="note">Built from four published datasets joined on the demarcation code:
Municipal Money (finance, 2024), the Auditor-General (outcomes to 2024-25), the IEC
(largest party after 2021) and Stats SA (free basic services). Captured 9–10 November 2026.
No causal claims — see the caveats on any page.</p>
<h2>{len(cards)} live entities</h2>
<table><thead><tr><th>Municipality</th><th>Province</th><th>Cat</th><th class="num">Population</th>
<th>Largest party (2021)</th><th>Latest audit</th><th class="num">Cash (months)</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<footer>Data CC BY 4.0 · code MIT ·
<a href="https://github.com/realtimshady16/sa-open-data">source</a></footer>
</main></body></html>"""
    (OUT / "index.html").write_text(index)

    # ---- one page per entity -------------------------------------------------
    for slug, r, m, ags, co, i in cards:
        ops = sorted((o for o in (ags.get("opinions") or []) if o.get("audit_opinion")),
                     key=lambda o: o.get("period") or "")
        op_rows = "".join(
            f"<tr><td>{esc(o['period'])}</td><td>{esc(o['audit_opinion'])}</td>"
            f"<td>{esc(o.get('information_reliable') or '')}</td>"
            f"<td>{esc(o.get('information_useful') or '')}</td></tr>" for o in ops)
        parties = sorted((co.get("parties") or []), key=lambda p: -(p.get("total") or 0))[:5]
        party_rows = "".join(
            f"<tr><td>{esc((p['party'] or '').title())}</td><td class=\"num\">{p.get('total')}</td></tr>"
            for p in parties)
        metrics = [("Cash coverage", "cash_coverage", " months"),
                   ("UIFW", "uifw_expenditure", "%"),
                   ("Repairs &amp; maintenance", "repairs_maintenance_spending", "%"),
                   ("Debtors collected", "current_debtors_collection_rate", "%"),
                   ("Capital vs budget", "capital_budget_spending", "%")]
        cards_html = "".join(
            f'<div class="card"><div class="v">{num(i.get(k), 1, s)}</div>'
            f'<div class="l">{label}</div></div>' for label, k, s in metrics)

        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(r['oad_name'])} — finance, audit, government</title>
<style>{CSS}</style></head><body><main>
<div class="kicker"><a href="index.html">← all municipalities</a> · {esc(r['code'])} · {esc(r['oad_level'])}</div>
<h1>{esc(r['oad_name'] or r['code'])}</h1>
<p class="note">{esc(r['province'])}{' · category ' + esc(m.get('category') or '—') if m.get('category') else ''}
{' · population ' + num(m.get('population'), 0) if m.get('population') else ''}</p>

<h2>Financial position, 2024</h2>
<div class="grid">{cards_html}</div>
<p class="note">Cash coverage is months of operating expenditure covered by cash (higher is safer).
UIFW is unauthorised, irregular, fruitless and wasteful expenditure as a share of operating
expenditure (higher is worse). Capital vs budget is a signed variance — negative means the capital
budget was underspent. A blank means not computed, never zero.</p>

<h2>Audit outcomes</h2>
<table><thead><tr><th>Period</th><th>Opinion</th><th>Reliable</th><th>Useful</th></tr></thead>
<tbody>{op_rows or '<tr><td colspan="4">No audited periods in this capture.</td></tr>'}</tbody></table>

<h2>Council after the 2021 election</h2>
<p>{esc(co.get('total_seats') or '—')} seats ·
{'single-party majority' if co.get('majority') else 'no single-party majority'} ·
largest party <strong>{esc((co.get('largest_party') or '—').title())}</strong>
with {esc(co.get('largest_seats') or '—')} seats.</p>
<table><thead><tr><th>Party</th><th class="num">Seats</th></tr></thead><tbody>{party_rows}</tbody></table>

<footer>Sources: National Treasury / Municipal Money · Auditor-General (MFMA 2024-25) ·
IEC · Stats SA P9115. Captured 2026-11-10. Largest party is not the governing party in a
hung council. Data CC BY 4.0 · <a href="https://github.com/realtimshady16/sa-open-data">source</a></footer>
</main></body></html>"""
        (OUT / f"{slug}.html").write_text(page)

    # ---- sanity --------------------------------------------------------------
    sizes = [p.stat().st_size for p in OUT.glob("*.html")]
    print(f"wrote {len(sizes)} pages to {OUT}")
    print(f"total {sum(sizes)/1024:.0f} KB, largest {max(sizes)/1024:.0f} KB")
    no_audit = sum(1 for _, r, m, ags, co, i in cards if not (ags.get("opinions") or []))
    no_co = sum(1 for _, r, m, ags, co, i in cards if not co)
    print(f"pages without audit data: {no_audit} | without council data: {no_co}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
