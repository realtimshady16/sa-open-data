# Archive audit — what the Wayback Machine actually holds

Checked 2026-11-15, in response to a claim in v0.1.0 that turned out to be too strong.

## The mistake, first

The first pass queried the CDX API like this:

```
cdx/search/cdx?url=mfma-2025.agsa.co.za&output=json
```

No `matchType`. The default is **exact match on the URL**, so that query can only ever return
captures of the site root — it is structurally incapable of finding anything deeper. Reading
its output as "the archive has one page" was a conclusion drawn from a query that could not
have produced any other answer.

Correct form: `&matchType=domain` (everything under a host) or `&matchType=prefix` (everything
under a path). Both are used below.

## What is actually archived

| Site | Unique URLs captured | Of which API/data URLs | Verdict |
|---|---|---|---|
| `mfma-2025.agsa.co.za` (domain) | **363** | **4** — `api/allauditees`, `api/homepagedata`, `api/navbar-x`, `api/pages/overview` | the shell and the auditee list, **not** the audit opinions |
| `results.elections.org.za` (domain, from 2026) | **1,042** | **0** under `api/` | captures are dominated by Cloudflare `cdn-cgi/challenge-platform` paths — the archive is recording the bot defence, not the results |
| `municipalmoney.gov.za/api/` (prefix) | **341** | many | substantially archived |
| `www.statssa.gov.za/publications/P9115/` (prefix) | **72** | many xlsx/pdf | well archived, including unit-data workbooks |
| `www.elections.org.za` (domain) | unknown — the CDX API returned **HTTP 503 "Temporarily Offline"** on both attempts | — | unresolved |

Two limits on the numbers: `www.elections.org.za` could not be measured, and the
`results.elections.org.za/dashboards/` prefix returned 503 as well. Rate limiting from the
Internet Archive is aggressive under several quick queries; a real audit should space requests
and record failures rather than treat them as empty results.

## What this does and does not change

**Unchanged:** the per-municipality audit opinions (257 × 8 = 2,056 rows) have **no** archived
captures. Neither does the IEC council composition, whose API path has zero. Those remain the
reason this repository exists.

**Changed:** "the Archive holds exactly one capture, the landing page" was wrong. It holds 363
URLs for AGSA, including the auditee list — enough to reconstruct *who* was audited, but not
*what they were found to have done*.

## Method for the next audit

```bash
cdx() { curl -sS --max-time 90 \
  "http://web.archive.org/cdx/search/cdx?url=$1&matchType=$2&output=json\
&limit=3000&collapse=urlkey&fl=original,mimetype,timestamp"; }
cdx "mfma-2025.agsa.co.za" domain
cdx "results.elections.org.za" domain
```

Rules, learned the hard way:

1. **Always pass `matchType`.** Without it you are measuring a single URL, not a site.
2. **Never conclude absence from an empty or failed response.** Check the HTTP status and byte
   count. `bytes=0` with `http=200` is an empty result; `http=503` is not an answer at all.
3. Space requests by ~20 s against the Internet Archive or you get "Temporarily Offline".
4. Filter by mimetype before believing a count: 1,042 captures that are Cloudflare challenge
   pages is not preservation.
