# Coverage and caveats

Read before quoting a number.

## 292 profiles is not 257 municipalities

Municipal Money serves **292** municipal profiles. The AGSA auditee list has **257**.

```
292 = 248 municipalities (211 live + 37 disestablished) + 44 districts
257 auditees = 166 local (LM) + 39 (ICM) + 44 district (DM) + 8 metro (MET)
```

The 37 disestablished entities are the pre-2016 composites — Baviaans, Nxuba, Tsolwana and
friends — which still carry audit history up to about 2015. They are useful for time series
and wrong for any current count. Join on code; never on row count.

**Open reconciliation:** 211 live municipalities is 203 local + 8 metro, against the standard
205 local. Two short, most likely the 2026 demarcation changes. Unresolved.

## Two municipalities are called Emalahleni

One in Mpumalanga (Nkangala), one in the Eastern Cape (Chris Hani). 257 municipalities, 256
distinct names. Any join on name silently merges them. This single collision is the whole
naming problem in one word, and it is why the joiners take a province and refuse ambiguity.

## Null means not computed, never zero

Indicator values carry `cube_version` and sometimes `rating: null` / `result: null`. A null is
an absence of computation, not a measured zero. Since the municipalities with missing
indicators are usually the worst performers, treating null as zero flatters the bottom of the
distribution.

## Sign conventions

- `cash_coverage` — months of operating expenditure covered by cash. Higher is safer.
- `uifw_expenditure` — unauthorised, irregular, fruitless and wasteful expenditure as % of
  actual operating expenditure. Higher is worse.
- `repairs_maintenance_spending` — R&M as % of (PPE + investment property). Higher is better.
- `current_debtors_collection_rate` — % of billed revenue collected. Higher is better.
- `capital_budget_spending` — `(actual − budgeted) / budgeted × 100`. **Negative means
  underspent**, so more negative is worse delivery. Nearly every median here is negative:
  capital underspending is the national norm.

## Audit opinions are Treasury's copy

The `audit_opinions` field in Municipal Money, and the AGSA sweep here, are copies. AGSA is the
primary source. Where they disagree, AGSA wins.

## Largest party is not the governing party

In the 2021–26 term, 70 of 213 councils had no single-party majority. The largest party is a
proxy for governance and a blunt one; in a hung council the mayor often comes from a coalition
partner.

## The financial analysis makes no causal claim

The gradient by audit opinion is monotone and real: clean-audit municipalities hold ~6.7 months
of cash and ~1.1% UIFW, against ~0.2 months and ~28.2% for adverse. But that gradient is
largely *the same fact* — a municipality that cannot hold a clean audit also cannot hold cash.
Capacity, wealth and province drive both. The party split is the weaker signal of the two, and
nobody should quote it without them. 2024 is one year, and medians on n=13 (IFP) are not a
finding.

## P9115 is submission behaviour

A third of municipalities report zero free-basic-service beneficiaries and the rest report
close to 100%. That is a reporting artefact, not a delivery pattern. Do not rank parties on it.

## What is missing entirely

- Ward-level anything.
- Any transaction-level municipal spending (mSCOA strings are not public).
- Demarcation crosswalks beyond what the disestablished flag implies.
- Facility registers (schools, clinics) — dirty everywhere, published clean by nobody.
