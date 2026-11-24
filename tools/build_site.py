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
:root{--bg:#141110;--fg:#e8ded2;--dim:#a89684;--line:#2e2723;--acc:#c9743a;
      --ok:#7d9f74;--warn:#c9a24a;--bad:#cf6444;--card:#1a1614}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);
     font:17px/1.65 ui-serif,Georgia,"Iowan Old Style",serif;padding:2rem 1.25rem 5rem}
.skip{position:absolute;left:-9999px}.skip:focus{left:1rem;top:1rem;z-index:4;background:var(--bg);padding:.5rem}
main{max-width:62rem;margin:0 auto}
a{color:var(--acc);text-decoration:none;border-bottom:1px solid rgba(201,116,58,.35)}
a:hover{border-bottom-color:var(--acc)}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
h1{font-size:clamp(1.6rem,4vw,2.1rem);line-height:1.15;margin:.2rem 0 1.4rem;letter-spacing:-.02em}
h2{font-size:.78rem;text-transform:uppercase;letter-spacing:.14em;color:var(--dim);
   margin:2.6rem 0 .7rem;font-family:ui-sans-serif,system-ui,sans-serif;font-weight:600}
.kicker{color:var(--dim);font-size:.8rem;text-transform:uppercase;letter-spacing:.16em;
        font-family:ui-sans-serif,system-ui,sans-serif}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}

/* tables: a sticky head, tabular figures, and no row-height jitter from wrapping */
.tablewrap{overflow-x:auto;margin:0 -.25rem}
table{width:100%;border-collapse:collapse;font-size:.95rem}
th,td{text-align:left;padding:.42rem .45rem;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--dim);font-weight:600;font-size:.74rem;text-transform:uppercase;letter-spacing:.1em;
   font-family:ui-sans-serif,system-ui,sans-serif;position:sticky;top:0;background:var(--bg);
   box-shadow:0 1px 0 var(--line);z-index:2;white-space:nowrap}
th[data-sort]{cursor:pointer;user-select:none}
th[data-sort]:hover{color:var(--fg)}
th[data-sort] button{all:unset;cursor:pointer}
th[data-sort] button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
th[data-sort]::after{content:"↕";opacity:.55;margin-left:.35em;font-size:.9em}
th[data-sort].asc::after{content:"↑";opacity:1}
th[data-sort].desc::after{content:"↓";opacity:1}
td.num{text-align:right;font-variant-numeric:tabular-nums}
tbody tr:hover{background:var(--card)}
tbody#rows tr{cursor:pointer}
td.nw{white-space:nowrap}

/* index controls */
.controls{display:flex;gap:.6rem;align-items:center;flex-wrap:wrap;margin:1rem 0 .6rem}
.controls input{flex:1 1 16rem;min-width:12rem;background:var(--card);border:1px solid var(--line);
  color:var(--fg);font:inherit;font-size:.95rem;padding:.5rem .7rem;border-radius:3px}
.controls input::placeholder{color:var(--dim)}
.chips{display:flex;gap:.45rem;flex-wrap:wrap;margin:.45rem 0 .7rem}
.chip,.mobile-sort select,.mobile-sort button{background:var(--card);border:1px solid var(--line);color:var(--fg);font:inherit;font-size:.82rem;padding:.38rem .6rem;min-height:40px;border-radius:3px}
.chip{cursor:pointer}.chip:hover,.chip[aria-pressed="true"]{border-color:var(--acc);color:var(--acc)}
.mobile-sort{display:none;gap:.45rem;align-items:center;margin:.35rem 0 .7rem}
.legend{color:var(--dim);font-size:.82rem;margin:.3rem 0 .8rem}
.flag{color:var(--warn);font-size:.76rem;line-height:1.4;margin-top:.5rem}
.count{color:var(--dim);font-size:.85rem;font-variant-numeric:tabular-nums}
.empty{padding:1.4rem .5rem;color:var(--dim)}

/* cards: content height, never stretched to the tallest sibling */
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(11.5rem,1fr));gap:.9rem;
      margin:1rem 0;align-items:start}
.card{border:1px solid var(--line);padding:.8rem .9rem;border-radius:3px;background:var(--card)}
.card .v{font-size:1.45rem;font-variant-numeric:tabular-nums;line-height:1.2}
.card .l{color:var(--dim);font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;margin-top:.2rem}
.card .cap{color:var(--dim);font-size:.8rem;line-height:1.45;margin-top:.5rem}
.note{color:var(--dim);font-size:.88rem;border-left:2px solid var(--line);padding-left:.9rem}
.ok{color:var(--ok)}.warn{color:var(--warn)}.bad{color:var(--bad)}.dim{color:var(--dim)}
details{margin:1rem 0;border:1px solid var(--line);border-radius:3px;padding:.6rem .8rem}
summary{cursor:pointer;color:var(--acc);font-size:.9rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);
       color:var(--dim);font-size:.82rem}

/* Narrow screens: seven columns cannot fit a phone, and horizontal scrolling hides the two
   columns that matter. Below 640px each row becomes a name and one line of facts instead. */
@media (max-width:1050px){
  body{padding:1.25rem .9rem 4rem;font-size:16px}
  th,td{padding:.4rem .35rem;font-size:.88rem}
  .controls input{flex:1 1 100%}
  .mobile-sort{display:flex}
  .tablewrap{overflow-x:visible;margin:0}
  table.wide thead, table.wide thead th{display:none}
  table.wide th[data-sort]::after{content:none}
  table.wide, table.wide tbody, table.wide tr, table.wide td{display:block;width:auto}
  table.wide tr{padding:.6rem 0;border-bottom:1px solid var(--line)}
  table.wide tr:hover{background:transparent}
  table.wide td{border:none;padding:0;text-align:left;white-space:normal}
  table.wide td:first-child{font-size:1.02rem;line-height:1.3}
  table.wide td:nth-child(2){margin-top:.1rem}
  table.wide td:nth-child(n+2){display:inline;font-size:.84rem;color:var(--dim)}
  table.wide td:nth-child(n+2).ok{color:var(--ok)}
  table.wide td:nth-child(n+2).warn{color:var(--warn)}
  table.wide td:nth-child(n+2).bad{color:var(--bad)}
  table.wide td:nth-child(3){display:none}                 /* category: not useful on a phone */
  table.wide td:nth-child(n+2)::after{content:" · ";color:var(--line)}
  table.wide td:nth-child(4)::before{content:"pop "}
  table.wide td:nth-child(5)::before{content:"party "}
  table.wide td:nth-child(6)::before{content:"audit "}
  table.wide td:nth-child(7)::before{content:"cash "}
  table.wide td:nth-child(7)::after{content:""}
  .card .cap{font-size:.82rem}
}
@media (max-width:640px){.grid{grid-template-columns:1fr}}
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
        ("Clean, with notes", "warn",
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
                      "cash if all income stopped tomorrow. It is an indicator to investigate, "
                      "not a score or a prediction."),
    "uifw_expenditure": ("Money spent wrongly", "%",
                         "Unauthorised, irregular, fruitless and wasteful expenditure as a "
                         "share of day-to-day spending. Lower is better. High figures often "
                         "mean money went out without following the rules, not that it was "
                         "stolen — though sometimes it means that too."),
    "repairs_maintenance_spending": ("Upkeep", "%",
                                     "Spending on repairs and maintenance as a share of the "
                                     "value of the assets it is supposed to maintain. Low "
                                     "numbers mean infrastructure is being run down."),
    "current_debtors_collection_rate": ("Revenue collected", "%",
                                        "Of what the municipality billed residents and "
                                        "businesses, how much it actually collected. Low "
                                        "numbers mean services go unpaid for. It can exceed 100% "
                                        "when old debt is recovered."),
    "capital_budget_spending": ("Capital budget variance", "%",
                                "Actual capital spending minus the budget, as a share of the "
                                "budget. Negative means underspent."),
}


def esc(v):
    return html.escape("" if v is None else str(v))


# The index is 257 rows of full party names, most of which wrap and make every row a different
# height. Abbreviate, and keep the full name in the title attribute so nothing is lost.
PARTY_ABBREV = {
    "african national congress": "ANC",
    "democratic alliance": "DA",
    "economic freedom fighters": "EFF",
    "inkatha freedom party": "IFP",
    "freedom front plus": "FF+",
    "vryheidsfront plus": "FF+",
    "patriotic alliance": "PA",
    "african christian democratic party": "ACDP",
    "congress of the people": "COPE",
    "united democratic movement": "UDM",
    "national freedom party": "NFP",
    "pan africanist congress of azania": "PAC",
    "african transformation movement": "ATM",
    "cape coloured congress": "CCC",
    "good": "GOOD",
    "african independent congress": "AIC",
    "minority front": "MF",
    "al jama-ah": "AL JAMA-AH",
    "african people's convention": "APC",
    "azanian people's organisation": "AZAPO",
    "bolsheviks party of south africa": "BPSA",
    "independent civic organisation of south africa": "ICOSA",
    "socialist revolutionary workers party": "SRWP",
}


def prettify(name):
    """Title case, but the small words stay small: 'Organisation of South Africa'."""
    small = {"of", "the", "and", "for", "in", "on", "a", "an"}
    words = name.replace("_", " ").title().split()
    return " ".join(w.lower() if i and w.lower() in small else w
                    for i, w in enumerate(words))


def party(name):
    """Abbreviated party label plus the full name for the hover title."""
    if not name:
        return "—", ""
    full = prettify(name)
    ab = PARTY_ABBREV.get(full.lower())
    return (ab, full) if ab else (full, full)


def audit_class(opinion):
    """Three levels, not two: findings-only is not the same as qualified."""
    o = (opinion or "").lower()
    if not o:
        return "dim"
    if o.startswith("unqualified with no"):
        return "ok"
    if o.startswith("unqualified with findings"):
        return "warn"
    return "bad"


def verdict_of(opinion):
    """The plain-language label for an audit opinion, plus its colour class."""
    key = (opinion or "").lower().replace(" of opinion", "").strip()
    for k, (label, cls, _help) in OPINION_GUIDE.items():
        if key.startswith(k):
            return label, cls
    return (opinion or "—"), audit_class(opinion)


def audit_rank(opinion):
    """Lower is a more serious outcome, so risk-first sorting is meaningful."""
    label, _ = verdict_of(opinion)
    return {"Disclaimer": 0, "Adverse": 1, "Qualified": 2,
            "Clean, with notes": 3, "Clean": 4, "Not yet audited": 5}.get(label, 6)


def cash_class(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return ""
    return "bad" if f < 1 else ("warn" if f < 3 else "")


# Small, dependency-free controls: filter the 257 rows, and keep sorting available on a phone.
# Inline and dependency-free, because the whole point is that this page works with no server.
INDEX_JS = r"""
const rows = [...document.querySelectorAll('tbody#rows tr')];
const q = document.getElementById('q');
const count = document.getElementById('count');
const empty = document.getElementById('empty');
const chips = [...document.querySelectorAll('.chip')];
const sortSelect = document.getElementById('mobile-sort');
const sortDir = document.getElementById('sort-dir');
let direction = 1;
let shown = rows.length;
rows.forEach(tr => tr.addEventListener('click', event => {
  if (!event.target.closest('a')) tr.querySelector('a').click();
}));

function apply() {
  const tokens = q.value.normalize('NFD').replace(/\p{Diacritic}/gu, '').trim().toLowerCase().split(/\s+/).filter(Boolean);
  const active = chips.filter(c => c.getAttribute('aria-pressed') === 'true').map(c => c.dataset.filter);
  shown = 0;
  for (const tr of rows) {
    const hit = (tokens.length === 0 || tokens.every(token => tr.dataset.search.includes(token))) &&
      (!active.length || active.every(f => tr.dataset[f] === 'true'));
    tr.hidden = !hit;
    if (hit) shown++;
  }
  count.textContent = (tokens.length || active.length) ? shown + ' of ' + rows.length + ' shown' : rows.length + ' municipalities';
  empty.hidden = shown > 0;
}
q.addEventListener('input', apply);
chips.forEach(chip => chip.addEventListener('click', () => {
  chip.setAttribute('aria-pressed', chip.getAttribute('aria-pressed') !== 'true');
  apply();
}));
apply();

function sortBy(i, dir) {
    const th = document.querySelector('th[data-sort="' + i + '"]');
    const numeric = th.dataset.num === '1';
    document.querySelectorAll('th[data-sort]').forEach(o => { o.classList.remove('asc','desc'); o.removeAttribute('aria-sort'); });
    th.classList.add(dir === 1 ? 'asc' : 'desc');
    th.setAttribute('aria-sort', dir === 1 ? 'ascending' : 'descending');
    const body = document.getElementById('rows');
    rows.sort((a, b) => {
      const av = a.children[i].dataset.v ?? a.children[i].textContent.trim().replace(/[,\u2014]/g,'');
      const bv = b.children[i].dataset.v ?? b.children[i].textContent.trim().replace(/[,\u2014]/g,'');
      if (numeric) {
        const an = parseFloat(av), bn = parseFloat(bv);
        if (isNaN(an) && isNaN(bn)) return 0;
        if (isNaN(an)) return 1;            // blanks sort last in both directions
        if (isNaN(bn)) return -1;
        return (an - bn) * dir;
      }
      return av.localeCompare(bv, 'en', {sensitivity:'base'}) * dir;
    });
    for (const tr of rows) body.appendChild(tr);
}
document.querySelectorAll('th[data-sort]').forEach(th => th.addEventListener('click', () => {
  direction = th.classList.contains('asc') ? -1 : 1;
  sortBy(+th.dataset.sort, direction);
}));
sortSelect.addEventListener('change', () => {
  const i = +sortSelect.value;
  direction = document.querySelector('th[data-sort="' + i + '"]').dataset.num === '1' ? -1 : 1;
  sortDir.textContent = direction === 1 ? 'A–Z / low–high' : 'Z–A / high–low';
  sortBy(i, direction);
});
sortDir.addEventListener('click', () => {
  direction *= -1;
  sortDir.textContent = direction === 1 ? 'A–Z / low–high' : 'Z–A / high–low';
  sortBy(+sortSelect.value, direction);
});
"""


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
    # Preserve source bytes, but do not repeat a known display typo across 31 public pages.
    for row in xwalk:
        row["province"] = (row.get("province") or "").replace("Nothern", "Northern")
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
        p_ab, p_full = party(co.get("largest_party"))
        cash = i.get("cash_coverage")
        name = r["oad_name"] or r["code"]
        v_label, v_class = verdict_of(opinion)
        province = (r.get("province") or "").replace("Nothern", "Northern")
        search = " ".join((name, province, m.get("category") or "",
                           p_ab, p_full, opinion, v_label)).lower()
        search = "".join(ch for ch in __import__('unicodedata').normalize('NFD', search)
                         if not __import__('unicodedata').combining(ch))
        audit_concern = bool(opinion and v_label != "Clean")
        low_cash = bool(cash and float(cash) < 1)
        rows.append(
            f'<tr data-search="{esc(search)}" data-audit-concern="{str(audit_concern).lower()}" data-low-cash="{str(low_cash).lower()}">'
            f'<td><a href="{slug}.html">{esc(name)}</a></td>'
            f'<td class="nw dim">{esc(province)}</td>'
            f'<td class="nw">{esc(m.get("category") or "—")}</td>'
            f'<td class="num" data-v="{esc(m.get("population") or "")}">{num(m.get("population"), 0)}</td>'
            f'<td class="nw" data-v="{esc(p_full)}">{esc(p_ab) if p_ab != p_full else esc(p_full)}</td>'
            f'<td class="nw {v_class}" title="{esc(opinion)}" data-v="{audit_rank(opinion)}">'
            f'{esc(v_label)}</td>'
            f'<td class="num {cash_class(cash)}" data-v="{esc(cash or "")}">{num(cash)}</td>'
            f'</tr>')

    def th(i, label, num_col=False, extra=""):
        return (f'<th data-sort="{i}"' + (' data-num="1"' if num_col else '') +
                (f' {extra}' if extra else '') + f'><button type="button">{label}</button></th>')

    index = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>South African municipalities — {len(cards)} places, one table</title>
<meta name="description" content="Finance, audit outcomes and 2021 election results for every
South African municipality, from published sources. No ranking, no scores, no causal claims.">
<style>{CSS}</style></head><body><a class="skip" href="#municipalities">Skip to municipalities</a><main>
<div class="kicker">SA open data · local view</div>
<h1>Every South African municipality,<br>and what its books say</h1>
<p class="note">Built from four published datasets joined on the demarcation code:
Municipal Money (finance, 2024), the Auditor-General (outcomes to 2024-25), the IEC
(largest party after 2021) and Stats SA (free basic services). Captured 9–10 November 2026.
No causal claims — see the caveats on any page.</p>
<details open><summary>How to read this</summary>
<div class="note">
<p><strong>One row per municipality.</strong> "Metro" is a big city that governs itself;
"local" is a town or rural municipality within a district; "district" sits above several locals and
shares services like water and roads between them.</p>
<p><strong>Largest party</strong> is who won the most seats in 2021 — not necessarily who
governs. If no party holds more than half, a coalition or minority government ran the place.
Districts are not directly elected, so their rows show a dash.</p>
<p><strong>Latest audit</strong> is the Auditor-General's verdict on the books. "Clean" is
unqualified with no findings; anything else means the auditors found a problem, and the
<a href="key.html">key</a> explains each verdict in one line.</p>
<p><strong>Cash</strong> is how many months the municipality could keep paying its bills from
cash if income stopped. Under one month is a crisis. It is a point-in-time figure and a
municipality can hold cash it cannot spend freely, so treat outliers as a question, not a
grade.</p>
</div></details>

<h2>Pick a municipality</h2>
<div class="controls">
  <input id="q" type="search" placeholder="Filter by name, province, party or audit outcome"
         aria-label="Filter municipalities" autocomplete="off">
  <span class="count" id="count" aria-live="polite">{len(cards)} municipalities</span>
</div>
<div class="chips" aria-label="Quick filters">
  <button class="chip" type="button" data-filter="auditConcern" aria-pressed="false">Audit concerns</button>
  <button class="chip" type="button" data-filter="lowCash" aria-pressed="false">Cash below 1 month</button>
</div>
<div class="mobile-sort"><label for="mobile-sort">Sort</label><select id="mobile-sort">
  <option value="0">Municipality</option><option value="3">Population</option>
  <option value="5">Latest audit</option><option value="6">Cash (months)</option>
</select><button id="sort-dir" type="button">A–Z / low–high</button></div>
<p class="legend"><span class="ok">Clean</span> = no findings; <span class="warn">clean, with notes</span> = findings; <span class="bad">qualified, adverse or disclaimer</span> = material concern. Cat A = metro, B = local, C = district. Party is the 2021 largest party; — means no direct-election result. Cash — means not computed; 0.0 is the source value rounded to one decimal.</p>
<div class="tablewrap" id="municipalities">
<table class="wide" style="font-size:.9rem"><thead><tr>
{th(0, "Municipality")}{th(1, "Province")}{th(2, "Cat")}
{th(3, "Population", True)}{th(4, "Party (2021)")}{th(5, "Latest audit", True)}
{th(6, "Cash (months)", True)}
</tr></thead><tbody id="rows">{''.join(rows)}</tbody></table>
</div>
<p class="empty" id="empty" role="status" hidden>No municipality matches that. Try a province, a party, or
part of a name.</p>
<footer><a href="key.html">How to read this</a> · data CC BY 4.0 · code MIT ·
<a href="https://github.com/realtimshady16/sa-open-data">source</a></footer>
</main><script>{INDEX_JS}</script></body></html>"""
    (OUT / "index.html").write_text(index)

    # ---- one page per entity -------------------------------------------------
    for slug, r, m, ags, co, i in cards:
        ops = sorted((o for o in (ags.get("opinions") or []) if o.get("audit_opinion")),
                     key=lambda o: o.get("period") or "")

        # The source also carries information_reliable / information_useful flags. They are not
        # in the render: across 2 056 audit periods they do not track the opinion at all (263
        # "unqualified with no findings" periods are flagged unreliable, 447 "qualified" ones are
        # flagged reliable), so labelling them "books reliable / useful" asserts something the
        # source does not say. The columns are still in datasets/ for anyone who knows the code.
        def audit_display(opinion):
            label, _ = verdict_of(opinion)
            return label if label.lower() == opinion.lower() else f"{label} — {opinion}"

        op_rows = "".join(
            f"<tr><td class=\"nw\">{esc(o['period'])}</td>"
            f"<td class=\"nw {verdict_of(o['audit_opinion'])[1]}\">{esc(audit_display(o['audit_opinion']))}</td></tr>" for o in ops)
        legend_rows = "".join(
            f"<tr><td class=\"{cls}\"><strong>{label}</strong></td><td>{esc(help_text)}</td></tr>"
            for label, cls, help_text in OPINION_GUIDE.values())
        parties = sorted((co.get("parties") or []), key=lambda p: -(p.get("total") or 0))[:5]
        party_rows = "".join(
            f"<tr><td>{esc((p['party'] or '').title())}</td>"
            f"<td class=\"num nw\">{p.get('total')}</td></tr>"
            for p in parties)
        def metric_flag(k, value):
            try:
                n = float(value)
            except (TypeError, ValueError):
                return ""
            if k == "cash_coverage" and n > 24:
                return '<div class="flag">Unusually high — a source value to investigate, not a grade.</div>'
            if k == "cash_coverage" and n < 0.05:
                return '<div class="flag">Reported near zero by the source — treat it as a question, not proof of no cash.</div>'
            if k == "current_debtors_collection_rate" and n < 0.05:
                return '<div class="flag">Reported as 0.0% by the source — treat it as a question, not a finding about the municipality.</div>'
            if k == "current_debtors_collection_rate" and n > 400:
                return '<div class="flag">Exceptionally high — it may include historic collections; check the source before interpreting it.</div>'
            if k == "current_debtors_collection_rate" and n > 120:
                return '<div class="flag">Above 100% usually means old debt was collected too.</div>'
            if k == "capital_budget_spending" and abs(n) > 100:
                return '<div class="flag">Unusually large reported variance — treat it as a question, not a grade.</div>'
            return ""

        cards_html = "".join(
            f'<div class="card"><div class="v">{num(i.get(k), 1, METRIC_HELP[k][1])}</div>'
            f'<div class="l">{METRIC_HELP[k][0]}</div>'
            f'<div class="cap">{METRIC_HELP[k][2]}</div>{metric_flag(k, i.get(k))}</div>'
            for k in ("cash_coverage", "uifw_expenditure", "repairs_maintenance_spending",
                      "current_debtors_collection_rate", "capital_budget_spending"))

        # 44 district municipalities have no IEC council record, because district councils are
        # not directly contested. Rendering that absence with the local-municipality template
        # used to print "— seats" and assert a hung council that never existed.
        if co:
            leaders = [p for p in (co.get("parties") or []) if p.get("total") == co.get("largest_seats")]
            leading_sentence = (f"The largest party was <strong>{esc((co.get('largest_party') or '—').title())}</strong> with {esc(co.get('largest_seats') or '—')} seats."
                                if len(leaders) <= 1 else
                                f"The most seats were shared by <strong>{esc(' and '.join((p.get('party') or '—').title() for p in leaders))}</strong> with {esc(co.get('largest_seats') or '—')} each.")
            governing_html = f"""<p>{esc(co.get('total_seats') or '—')} seats up for election in 2021.
{'One party holds more than half, so it governs alone.' if co.get('majority') else 'No party holds more than half, so a coalition or a minority government had to be formed.'}
{leading_sentence}</p>
<p class="note">Largest party is <em>not</em> the same as the governing party in a hung council.
The mayor can come from a smaller coalition partner.</p>
<div class="tablewrap" style="max-width:26rem">
<table><thead><tr><th>Party</th><th class="num">Seats</th></tr></thead><tbody>{party_rows}</tbody></table>
</div>"""
        else:
            governing_html = """<p>District councils are not directly elected. Under the Municipal
Structures Act 117 of 1998, 60% of their seats are filled by councillors delegated from the
local municipalities inside the district and 40% by proportional representation.</p>
<p class="note">The council dataset used here records councils contested directly, so districts
are not in it. This page therefore reports no largest party — that is a gap in the source, not
a hung council and not zero seats. The local municipalities inside this district each have
their own page and their own 2021 result.</p>"""
        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(r['oad_name'])} — finance, audit, government</title>
<meta name="description" content="{esc(r['oad_name'])}: {esc(r['province'])}, audit outcomes and
2021 election result from published sources. Finance year 2024, audits to 2024-25.">
<style>{CSS}</style></head><body><a class="skip" href="#content">Skip to municipality data</a><main id="content">
<div class="kicker"><a href="index.html">← all municipalities</a> · <a href="key.html">key</a> · {esc(r['code'])} · {esc(r['oad_level'])}</div>
<h1>{esc(r['oad_name'] or r['code'])}</h1>
<p class="note">{esc(r['province'])}{' · category ' + esc(m.get('category') or '—') if m.get('category') else ''}
{' · population ' + num(m.get('population'), 0) if m.get('population') else ''}</p>

<h2>Financial position, 2024</h2>
<div class="grid">{cards_html}</div>
<p class="note">A blank means not computed, never zero. These are indicators to investigate,
not a municipal ranking or a prediction of performance.</p>

<h2>Audit outcomes</h2>
<div class="tablewrap">
<table><thead><tr><th>Year</th><th>Verdict</th></tr></thead>
<tbody>{op_rows or '<tr><td colspan="2">No audited periods in this capture.</td></tr>'}</tbody></table>
</div>
<details><summary>What the verdicts mean</summary>
<table><tbody>{legend_rows}</tbody></table></details>
<p class="note">One row per financial year, oldest first. Where the plain-language verdict differs
from the Auditor-General's phrase, the source phrase follows it after the dash. The source also flags whether reported <em>performance</em> information was reliable
and useful — it is in the data files, but it is not shown here, because a flag that does not
track the audit opinion would read as a judgement on the financial statements.</p>

<h2>Who governs</h2>
{governing_html}

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
<p class="note">The Auditor-General's data also carries two flags, <strong>reliable</strong> and
<strong>useful</strong>, about reported performance information. They are in the data files but
<em>not</em> shown on these pages: across 2 056 audit periods they do not track the opinion at all
(263 "unqualified with no findings" periods are flagged unreliable; 447 "qualified" ones are
flagged reliable), so printing them beside a verdict would read as a judgement on the financial
statements. A blank everywhere else means not computed, never zero.</p>

<h2>The five money numbers</h2>
<table><tbody>{metric_rows}</tbody></table>

<h2>Who governs</h2>
<p>A council is elected every five years. If one party wins more than half the seats it governs
alone. If not, the council is <em>hung</em> and a coalition or minority arrangement forms — which
is why the largest party and the governing party can differ. In 2021, 70 of 213 councils were
hung.</p>
<p class="note"><strong>District municipalities are the exception.</strong> Their councils are not
elected directly: 60% of the seats are filled by councillors delegated from the local
municipalities inside the district and 40% by proportional representation, so the direct-election
dataset these pages use does not cover them. Their pages say so instead of showing an empty
result.</p>

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
