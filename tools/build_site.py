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
.card .cap{color:var(--dim);font-size:.78rem;line-height:1.4;margin-top:.35rem}
.dim{color:var(--dim)}
details{margin:1rem 0;border:1px solid var(--line);border-radius:3px;padding:.6rem .8rem}
summary{cursor:pointer;color:var(--acc);font-size:.9rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);
       color:var(--dim);font-size:.82rem}
"""



# ---------------------------------------------------------------------------
# Plain-language layer. Every number on the site gets a caption that says what it means
# and which direction is good, because a table of municipal finance is unreadable to
# anyone who has not already spent a week with it.
OPINION_GUIDE = {
    "unqualified with no findings":
        ("Clean", "ok",
         "The auditors found nothing wrong. The rarest outcome and the one to look for."),
    "unqualified with findings":
        ("Clean, with notes", "ok",
         "The numbers are fair, but the auditors found problems worth mentioning — often "
         "how money was spent rather than whether it was counted correctly."),
    "qualified":
        ("Qualified", "bad",
         "Parts of the books could not be trusted. Something is materially wrong, in a "
         "specific area the report names."),
    "adverse":
        ("Adverse", "bad",
         "The books as a whole do not fairly show the municipality's finances."),
    "disclaimer":
        ("Disclaimer", "bad",
         "The auditors could not get enough evidence to form an opinion at all. This is the "
         "worst outcome, and it usually means records were missing or withheld."),
    "outstanding":
        ("Not yet audited", "dim",
         "The audit for that year was not complete in this capture."),
}

METRIC_HELP = {
    "cash_coverage": ("Cash on hand", " months",
                      "How many months the municipality could keep paying its bills from "
                      "cash if all income stopped tomorrow. Below one month is a crisis; "
                      "three or more is comfortable."),
    "uifw_expenditure": ("Money spent wrongly", "%",
                         "Unauthorised, irregular, fruitless and wasteful expenditure as a "
                         "share of day-to-day spending. Lower is better. High figures often "
                         "mean money went out without following the rules, not that it was "
                         "stolen — though sometimes it means that too."),
    "repairs_maintenance_spending": ("Upkeep", "%",
                                     "Spending on repairs and maintenance as a share of the "
                                     "value of the assets it is supposed to maintain. Low "
                                     "numbers mean infrastructure is being run down."),
    "current_debtors_collection_rate": ("Bills actually paid", "%",
                                        "Of what the municipality billed residents and "
                                        "businesses, how much it actually collected. Low "
                                        "numbers mean services go unpaid for."),
    "capital_budget_spending": ("Building budget used", "%",
                                "How much of the capital (building and infrastructure) budget "
                                "was actually spent. Negative means underspent."),
}


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
<h2>How to read this</h2>
<div class="note">
<p><strong>One row per municipality.</strong> "Metro" is a big city that governs itself;
"local" is a town or district municipality's child; "district" sits above several locals and
shares services like water and roads between them.</p>
<p><strong>Largest party</strong> is who won the most seats in 2021 — not necessarily who
governs. If no party holds more than half, a coalition or minority government ran the place.</p>
<p><strong>Latest audit</strong> is the Auditor-General's verdict on the books. "Clean" is
unqualified with no findings; anything else means the auditors found a problem, and the
<a href="key.html">key</a> explains each verdict in one line.</p>
<p><strong>Cash</strong> is how many months the municipality could keep paying its bills from
cash if income stopped. Under one month is a crisis.</p>
</div>

<h2>{len(cards)} live entities</h2>
<table><thead><tr><th>Municipality</th><th>Province</th><th>Cat</th><th class="num">Population</th>
<th>Largest party (2021)</th><th>Latest audit</th><th class="num">Cash (months)</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<footer><a href="key.html">How to read this</a> · Data CC BY 4.0 · code MIT ·
<a href="https://github.com/realtimshady16/sa-open-data">source</a></footer>
</main></body></html>"""
    (OUT / "index.html").write_text(index)

    # ---- one page per entity -------------------------------------------------
    for slug, r, m, ags, co, i in cards:
        ops = sorted((o for o in (ags.get("opinions") or []) if o.get("audit_opinion")),
                     key=lambda o: o.get("period") or "")
        def verdict(op):
            key = (op or "").lower().replace(" of opinion", "").strip()
            for k, (label, cls, _help) in OPINION_GUIDE.items():
                if key.startswith(k):
                    return label, cls
            return op or "—", "dim"

        op_rows = "".join(
            f"<tr><td>{esc(o['period'])}</td>"
            f"<td class=\"{verdict(o['audit_opinion'])[1]}\">{esc(verdict(o['audit_opinion'])[0])}</td>"
            f"<td>{esc('yes' if (o.get('information_reliable') or '').lower().startswith('y') else 'no' if o.get('information_reliable') else '')}</td>"
            f"<td>{esc('yes' if (o.get('information_useful') or '').lower().startswith('y') else 'no' if o.get('information_useful') else '')}</td>"
            f"<td class=\"dim\">{esc(o['audit_opinion'])}</td></tr>" for o in ops)
        legend_rows = "".join(
            f"<tr><td class=\"{cls}\"><strong>{label}</strong></td><td>{esc(help_text)}</td></tr>"
            for label, cls, help_text in OPINION_GUIDE.values())
        parties = sorted((co.get("parties") or []), key=lambda p: -(p.get("total") or 0))[:5]
        party_rows = "".join(
            f"<tr><td>{esc((p['party'] or '').title())}</td><td class=\"num\">{p.get('total')}</td></tr>"
            for p in parties)
        cards_html = "".join(
            f'<div class="card"><div class="v">{num(i.get(k), 1, METRIC_HELP[k][1])}</div>'
            f'<div class="l">{METRIC_HELP[k][0]}</div>'
            f'<div class="cap">{METRIC_HELP[k][2]}</div></div>'
            for k in ("cash_coverage", "uifw_expenditure", "repairs_maintenance_spending",
                      "current_debtors_collection_rate", "capital_budget_spending"))

        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(r['oad_name'])} — finance, audit, government</title>
<style>{CSS}</style></head><body><main>
<div class="kicker"><a href="index.html">← all municipalities</a> · <a href="key.html">key</a> · {esc(r['code'])} · {esc(r['oad_level'])}</div>
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
<table><thead><tr><th>Year</th><th>Verdict</th><th>Books reliable?</th><th>Books useful?</th>
<th class="dim">Auditor's words</th></tr></thead>
<tbody>{op_rows or '<tr><td colspan="5">No audited periods in this capture.</td></tr>'}</tbody></table>
<details><summary>What the verdicts mean</summary>
<table><tbody>{legend_rows}</tbody></table></details>
<p class="note">"Reliable" asks whether the numbers can be trusted; "useful" asks whether the
report is good enough to plan with. A municipality can be reliable but not useful.</p>

<h2>Who governs</h2>
<p>{esc(co.get('total_seats') or '—')} seats up for election in 2021.
{'One party holds more than half, so it governs alone.' if co.get('majority') else 'No party holds more than half, so a coalition or a minority government had to be formed.'}
The largest party was <strong>{esc((co.get('largest_party') or '—').title())}</strong>
with {esc(co.get('largest_seats') or '—')} seats.</p>
<p class="note">Largest party is <em>not</em> the same as the governing party in a hung council.
The mayor can come from a smaller coalition partner.</p>
<table><thead><tr><th>Party</th><th class="num">Seats</th></tr></thead><tbody>{party_rows}</tbody></table>

<footer>Sources: National Treasury / Municipal Money · Auditor-General (MFMA 2024-25) ·
IEC · Stats SA P9115. Captured 2026-11-10. Largest party is not the governing party in a
hung council. Data CC BY 4.0 · <a href="https://github.com/realtimshady16/sa-open-data">source</a></footer>
</main></body></html>"""
        (OUT / f"{slug}.html").write_text(page)

    # ---- key -----------------------------------------------------------------
    opinion_rows = "".join(
        f'<tr><td class="{cls}"><strong>{label}</strong></td><td>{esc(help_text)}</td></tr>'
        for label, cls, help_text in OPINION_GUIDE.values())
    metric_rows = "".join(
        f'<tr><td><strong>{METRIC_HELP[k][0]}</strong></td><td>{esc(METRIC_HELP[k][2])}</td></tr>'
        for k in ("cash_coverage", "uifw_expenditure", "repairs_maintenance_spending",
                  "current_debtors_collection_rate", "capital_budget_spending"))

    key = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Key — how to read this data</title>
<style>{CSS}</style></head><body><main>
<div class="kicker"><a href="index.html">← all municipalities</a> · key</div>
<h1>How to read this</h1>
<p class="note">Everything here is a published number, joined on the municipality's code.
Nothing is estimated and nothing is modelled. Where a number is missing the page says so.</p>

<h2>The three kinds of municipality</h2>
<table><tbody>
<tr><td><strong>Metropolitan</strong></td><td>A big city that runs everything itself — Cape Town,
Johannesburg, eThekwini. Eight of them.</td></tr>
<tr><td><strong>Local</strong></td><td>A town or rural municipality. Handles its own services and
sits inside a district.</td></tr>
<tr><td><strong>District</strong></td><td>Sits above several local municipalities and shares
services between them — water, roads, disaster management. 44 of them.</td></tr>
</tbody></table>

<h2>The Auditor-General's verdicts</h2>
<p>The Auditor-General checks whether the books are honest. There are only a few outcomes, and
they are worth knowing because they are the clearest single signal of whether a municipality is
functioning.</p>
<table><tbody>{opinion_rows}</tbody></table>
<p class="note">Two extra columns on each page: <strong>reliable</strong> asks whether the numbers
can be trusted, <strong>useful</strong> asks whether the report is good enough to plan with. A
municipality can be reliable but not useful.</p>

<h2>The five money numbers</h2>
<table><tbody>{metric_rows}</tbody></table>

<h2>Who governs</h2>
<p>A council is elected every five years. If one party wins more than half the seats it governs
alone. If not, the council is <em>hung</em> and a coalition or minority arrangement forms — which
is why the largest party and the governing party can differ. In 2021, 70 of 213 councils were
hung.</p>

<h2>What this is not</h2>
<ul>
<li><strong>Not advice.</strong> No ranking, no scores, no "best municipality".</li>
<li><strong>Not a causal claim.</strong> Poor audit outcomes and weak finances share causes —
capacity, wealth, history. Neither explains the other, and this site does not try.</li>
<li><strong>Not current.</strong> Finance is the 2024 financial year; audits run to 2024–25;
councils are from the 2021 election. Captured 9–10 November 2026.</li>
<li><strong>Not complete.</strong> A blank means the source did not publish or compute the
number, never zero.</li>
</ul>

<h2>Sources</h2>
<ul>
<li>Finance and municipal profile — National Treasury, via Municipal Money (built by OpenUp)</li>
<li>Audit outcomes — Auditor-General of South Africa, MFMA 2024-25</li>
<li>Council seats — Electoral Commission of South Africa, 2021 local election</li>
<li>Free basic services — Statistics South Africa, P9115</li>
<li>Codes and hierarchy — OpenAdminData administrative divisions (CC BY 4.0)</li>
</ul>
<footer>Data CC BY 4.0 · code MIT ·
<a href="https://github.com/realtimshady16/sa-open-data">source</a></footer>
</main></body></html>"""
    (OUT / "key.html").write_text(key)

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
