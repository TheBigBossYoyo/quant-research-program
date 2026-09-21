# PHASE 9A — point-in-time semantics test log

Date: 2026-09-21. Every test below is a **schema / semantics** test. No returns were computed, no
strategy was formed, no locked window was evaluated. Raw captures: `reports/phase9a/raw/`.

The single governing test:

> **T0 — the two-date test.** Does the schema carry an observation/as-of date that is a *different
> field* from the target fiscal period, and can it be queried? If not, the product cannot answer
> "what did consensus say on date t" no matter how much history it advertises.

---

## T1 — Nasdaq Data Link `ZACKS/EEH`: two-date test — **PASS**

Method: anonymous GET of the public metadata route (no key required), plus the rendered product
documentation page.

```
GET https://data.nasdaq.com/api/v3/datatables/ZACKS/EEH/metadata   -> HTTP 200
{"vendor_code":"ZACKS","datatable_code":"EEH",
 "name":"Zacks Consensus Earnings Estimates History",
 "filters":["per_end_date","ticker","obs_date","per_type"],
 "primary_key":["m_ticker","per_end_date","obs_date","per_type"],
 "premium":true,
 "status":{"refreshed_at":"2026-09-21T09:46:26.000Z","status":"ON TIME","update_frequency":"CONTINUOUS"}}
```

`obs_date` and `per_end_date` are **separate primary-key columns**, and `obs_date` is a **filter**, so
the table is sliceable as of an arbitrary historical date. Documented definition, verbatim:

> `obs_date` — "Observation date (YYYY-MM-DD) corresponding to the date on which contributed estimates
> were changed and the consensus was revised."

A row is written *when the consensus moved*, which is the natural key for a revision series.
Result: **class A, TRUE_PIT_HISTORY.**

Same test applied across the vendor namespace (all anonymous, all HTTP 200):

| table | obs_date in primary key? | class |
| --- | --- | --- |
| `ZACKS/EEH` | yes | A |
| `ZACKS/SEH` | yes | A (sales) |
| `ZACKS/TP` | yes | A (target price) |
| `ZACKS/ES` | no (per_end_date only) | D |
| `ZACKS/EE`, `ZACKS/SE`, `ZACKS/SEE` | no | E |
| `ZACKS/EA` | no (expected-report dates) | E |
| `ZACKS/AR` | no | E |
| `ZACKS/MT` | n/a (reference) | — |

Reconstruction check: with `obs_date` filterable, consensus(t), consensus(t−30d) and consensus(t−60d)
are three queries on the same table, and a complete snapshot series is available rather than fixed lags.
This is the preferred structure in the brief, not the fallback.

## T2 — EODHD `/api/calendar/trends`: two-date test — **FAIL**, plus access denied

Access probe, 2026-09-21, existing subscription token (redacted in all stored files):

| request | status |
| --- | --- |
| `/api/user` | **200** (token valid, `dailyRateLimit` 100000) |
| `/api/calendar/trends?symbols=AAPL.US` | **403 Forbidden** |
| `/api/calendar/trends?symbols=MSFT.US,AAPL.US` | **403 Forbidden** |
| `/api/calendar/trends?symbols=AAPL.US&from=2014-01-01&to=2014-12-31` | **403 Forbidden** |
| `/api/calendar/trends?symbols=AAPL.US&from=2017-01-01&to=2017-12-31` | **403 Forbidden** |
| `/api/calendar/trends?symbols=BSC_old.US` (delisted) | **403 Forbidden** |
| `/api/calendar/trends?symbols=TWTR.US` (delisted) | **403 Forbidden** |
| `/api/calendar/earnings?symbols=AAPL.US&from=2014-01-01&to=2014-12-31` | **403 Forbidden** |

Body in every case: `Forbidden. Please contact support@eodhistoricaldata.com`. The 200 on `/api/user`
in the same run proves this is a package entitlement, not authentication. Per the brief, the status was
recorded and probing stopped; no package was added.

Documentation test, answering the brief's questions directly:

| question | answer, from EODHD's own field table |
| --- | --- |
| Does every row contain an as-of/observation timestamp? | **No.** There is no as-of, updated, snapshot or timestamp field in the response at all. |
| Is `date` the fiscal period end or the snapshot date? | **Fiscal period end** — "Fiscal period end the estimate refers to — quarter end for a quarterly record, year end for an annual one". |
| Can the API be queried as of an arbitrary historical date? | **No.** The endpoint takes no `from`/`to` filters; `symbols` is the only required parameter. |
| Can one reconstruct consensus on 2014-06-30 / 2015-06-30 / 2017-06-30? | **No.** Nothing in the payload records when a value was observed. |
| Are 7/30/60/90-days-ago relative to a historical snapshot or to the current record? | **To the read.** The doc annotates its own example "read on 18 August 2026" and says "the estimate fields in it move as analysts publish". |
| Are old revisions immutable or reconstructed? | **Undecidable, which is itself disqualifying** — with no write timestamp there is no way to demonstrate immutability. |
| How far back does true revision history go? | None. The advertised "96 records … 2017 to 2027" are **fiscal period ends**, repeated across horizon labels (`0q/+1q/0y/+1y`), not observation dates. |
| Are delisted securities available? | Untested (403 on both delisted probes). |

Result: **class C, FISCAL_PERIOD_HISTORY_ONLY → NOT_SUITABLE_FOR_BACKTESTING_REVISIONS.**

## T3 — Alpha Vantage `EARNINGS_ESTIMATES`: freeze test — **PARTIAL PASS**, anchor unobservable

Method: `function=EARNINGS_ESTIMATES&symbol=IBM&apikey=demo` (HTTP 200, 40,981 bytes). The demo key
serves IBM only; MSFT/AAPL/TWTR returned the demo-key notice, so cross-symbol behaviour is UNVERIFIED.

Two-date test: **FAIL** — `date` is the fiscal period end, `horizon` is "fiscal year"/"fiscal quarter",
and there is no observation-date field.

Freeze test (the informative one). If a past-period row were recomputed live, its lag fields would all
equal the current value, because a settled quarter attracts no revisions. Observed for **2017-06-30**,
a quarter reported nine years ago:

```
eps_estimate_average           2.7500
eps_estimate_average_7_days_ago  2.7500
eps_estimate_average_30_days_ago 2.7500
eps_estimate_average_60_days_ago 2.7700
eps_estimate_average_90_days_ago 3.1700
```

Flat at 7 and 30 days, moving at 60 and 90 — the settling pattern of a consensus approaching a report.
The row was therefore **frozen at a snapshot near that quarter's report date and retained**, not
recomputed. The same shape holds for the recently reported 2025-12-31 quarter (4.2884 / 4.2931 /
4.3068 / 4.3118 / 4.3083).

Coverage: 41 rows, 39 quarters from **2017-06-30** to 2026-12-31 plus 2 fiscal years; every row carries
the full lag block.

Result: **class B, PARTIAL_PIT_HISTORY — but not usable here.** Three compounding defects:

1. the snapshot's anchor date is **not in the schema** (assumed ≈ report date, unverifiable);
2. exactly **one snapshot per fiscal period**, taken at the end of the estimation window, so it may
   only be read after the report — it is the revision history of the quarter just reported, not a
   forward consensus tradable before it;
3. history begins **2017-06**, below the 2010 floor. Per the brief: do not backtest.

## T4 — FMP: two-date test — **FAIL**, conceded by the vendor

`analyst-estimates` / `financial-estimates` return one row per target fiscal period with no observation
field. FMP's own guidance (2026-08-13) names the error this would cause — "Reconstructing historical
knowledge from a current response" — and instructs users to "use a source that explicitly supports
point-in-time estimate vintages". No separate FMP revision time-series product exists.
Result: **class C → REJECT_FMP_FOR_REVISION_BACKTESTING.**

## T5 — the immutability test that has NOT been run (precondition for any purchase)

Documented `obs_date` semantics are not the same as verified immutability. A vendor could rewrite
historical rows on restatement, silently destroying the point-in-time property. The test is cheap and
needs no paid subscription, only a free Nasdaq Data Link account:

1. Create a free Nasdaq Data Link account (no credit card). The `ZACKS/EEH` **free sample** covers 30
   large-cap tickers for `obs_date` in 2018.
2. Pull the sample, hash it, store it.
3. Wait ≥ 14 days, pull again, diff.
4. **Pass** = byte-identical for all rows whose `obs_date` is in the past. **Fail** = any historical row
   changed, which would demote the product from class A to "reconstructed history".

Note on the data lock: the sample's `obs_date` falls in the locked 2018–2021 validation window. The test
reads **estimate values only** — no prices, no returns, no signal, no selection — and its single output
is a byte-equality verdict. That is a vendor-integrity check, not a use of locked data for strategy
selection, and it must be recorded as such if run.

## Summary table

| source | two-date test | class | blocking defect |
| --- | --- | --- | --- |
| Nasdaq Data Link `ZACKS/EEH` | **PASS** | **A** | licence: deep history institution-only |
| Nasdaq Data Link `ZACKS/SEH` | **PASS** | **A** (sales) | same licence |
| Nasdaq Data Link `ZACKS/TP` | **PASS** | **A** (targets) | same licence |
| Alpha Vantage `EARNINGS_ESTIMATES` | FAIL (freeze test partial pass) | B (weak) | no anchor date; 1 snapshot/period; starts 2017-06 |
| EODHD `/calendar/trends` | FAIL | C | no observation field; no date filter; 403 on our token |
| FMP `analyst-estimates` | FAIL | C | vendor concedes no PIT vintages |
| Finnhub estimates | not pursued | — | USD 3,500/month |
| Polygon / Benzinga | n/a | — | ratings not consensus; USD 99/month; from 2012 |
| Intrinio (Zacks) | inherits Zacks | A-source | ENTERPRISE only, business licence |
| LSEG I/B/E/S PIT | **PASS** (reference standard) | A | institutional only |
| OSAP firm-level signals | n/a (derived signals) | — | CRSP `permno` key, unjoinable to our panel |
