# PHASE 9A — Point-in-time analyst estimate revision data audit

Audit date: **2026-09-21**. No backtest was run. No locked data was opened. Nothing was purchased.
Cumulative strategy-cell ledger unchanged at **490** (an information-source audit adds no cells).

Raw evidence: `reports/phase9a/raw/` (20 files, `SHA256SUMS.txt`).
Point-in-time semantics test log: `PHASE9A_POINT_IN_TIME_TESTS.md`.
Prices and licence terms: `PHASE9A_PRICING_AUDIT.md`.
Machine-readable summary: `PHASE9A_PROVIDER_MATRIX.csv`.
Decision: `PHASE9A_RECOMMENDATION.md`. Forward design: `PHASE9B_DRAFT.md`.

---

## 1. What had to be true

A qualifying source must let us answer, for issuer *i* at historical date *t*:
*what did the consensus say as of t, and how had it changed over the previous weeks?*

The operational test used throughout this audit is a **schema test, not a marketing test**:

> The as-of/observation date and the target fiscal period must be **two distinct fields**, and the
> observation date must be **queryable**. A field called `date` that is the fiscal period end is not
> point-in-time history, however much history the product claims.

Classification scale (as preregistered in the Phase 9A brief):

| class | meaning |
| --- | --- |
| **A. TRUE_PIT_HISTORY** | consensus snapshots with observable, queryable as-of dates |
| **B. PARTIAL_PIT_HISTORY** | only 7/30/60/90-day prior values, no full snapshot series |
| **C. FISCAL_PERIOD_HISTORY_ONLY** | old target periods, no historical observation-date series |
| **D. SURPRISE_HISTORY_ONLY** | actual versus final/near-final estimate |
| **E. CURRENT_SNAPSHOT_ONLY** | today's numbers, nothing else |

Only **A** is sufficient for the primary revision strategy. **B** is usable only if the prior snapshots
are genuinely preserved and the anchor date is observable.

## 2. Result in one line

**Class A data exists, is exactly the right shape, and cannot be bought by an individual.**

The Zacks consensus history on Nasdaq Data Link (`ZACKS/EEH`) is a textbook point-in-time revision
database — `obs_date` is a *separate, filterable primary-key column* from `per_end_date`, history to
1979, 23,000+ listed **and delisted** North American issuers. Nasdaq's own FAQ then states that the
Zacks agreement **restricts deeper history to institutions**, and an individual may subscribe to only
a few years. Every other audited source is class B/C/D/E, or is priced at USD 99–3,500 per month, or both.

## 3. Provider-by-provider findings

### 3.1 Nasdaq Data Link / Zacks — **class A**, blocked by licence

Product **ZEEH**, "North American Consensus Earnings Estimate History" (`data.nasdaq.com/databases/ZEEH`).
Tables `ZACKS/EEH` and `ZACKS/MT`. Verified from the rendered product page *and* from the anonymous
metadata endpoint (`reports/phase9a/raw/ndl_ZACKS_EEH_metadata_20260921.json`), which returns:

```json
"primary_key":["m_ticker","per_end_date","obs_date","per_type"],
"filters":["per_end_date","ticker","obs_date","per_type"],
"premium":true
```

`obs_date` is documented verbatim as:

> "Observation date (YYYY-MM-DD) corresponding to the date on which contributed estimates were changed
> and the consensus was revised."

That is the field this whole audit was looking for, and it is both a primary key and a query filter,
so the table can be sliced *as of* any historical date without reconstruction.

Columns present: `eps_mean_est`, `eps_median_est`, `eps_cnt_est` (analyst count), `eps_high_est`,
`eps_low_est`, `eps_std_dev_est` (dispersion), `eps_cnt_est_rev_up`, `eps_cnt_est_rev_down`
(revision breadth). Target period is carried separately as `per_end_date` + `per_type` (Q/A) plus
fiscal and calendar year/quarter labels. Coverage: "23,000+ U.S. and Canadian **listed and delisted**
companies", history from **Jan 1979**, updated daily at 10:00 UTC with a 1-day reporting lag.

Sibling products discovered by enumerating the vendor namespace anonymously (all `premium: true`):

| table | product | primary key | what it adds |
| --- | --- | --- | --- |
| `ZACKS/EEH` | ZEEH, EPS estimate history, 1979+ | m_ticker, per_end_date, **obs_date**, per_type | the core revision series |
| `ZACKS/SEH` | ZSEH, sales estimate history, 2000+, 13,000+ names incl. **6,000+ delisted** | m_ticker, per_end_date, **obs_date**, per_type | revenue consensus revisions |
| `ZACKS/TP` | target price history | m_ticker, **obs_date** | price-target revisions |
| `ZACKS/ES` | consensus earnings surprises | m_ticker, per_end_date | class D only |
| `ZACKS/EE`, `ZACKS/SE`, `ZACKS/SEE` | current consensus (earnings / sales / Street) | *no* obs_date | class E |
| `ZACKS/MT` | master table | m_ticker | `active_ticker_flag`, `comp_cik`, SIC/sector, split history |

`ZACKS/MT` carries `comp_cik`, which matters: it gives a CIK→ticker bridge into the SEC identifiers
this repository already uses, so the survivorship-aware join to the local EODHD active+delisted price
panel is tractable.

**The blocker.** Nasdaq Data Link's own FAQ, verbatim:

> "Q: Why can't I subscribe to full history for Zacks data?
> If you are viewing the Zacks data feeds and see that you may only subscribe to a limited amount of
> history (e.g. fewer than 3 years of history), even though the data documentation states the data feed
> has many more years of history, this is because our agreement with Zacks restricts deeper history to
> institutions only.
> As per our agreement with Zacks, deeper history or full history may only be licensed to
> institutions/businesses and not to individuals."

A Personal account therefore cannot obtain the 2010–2017 development window this programme requires,
at any price it can see. A Business account is a different legal representation about the use of the
data, not a workaround, and the pricing behind it is quote-based ("Contact Sales") rather than listed.

Zacks direct (`zacksdata.com`) is quote-only, routed through a named sales contact, and explicitly
points individual investors back to NasdaqData.com and Intrinio.

### 3.2 EODHD `/api/calendar/trends` — **class C**, and not accessible on the current token

Probed live on 2026-09-21 with the existing subscription token. Seven requests, all
**HTTP 403 `Forbidden`** (`reports/phase9a/raw/eodhd_trends_*_20260921.txt`); `/api/user` returned 200
on the same token in the same run, so this is a package entitlement boundary, not an auth failure.
Per the brief, access was not upgraded and probing stopped there.

The documentation alone is sufficient to disqualify it. EODHD's own field table says, verbatim:

- `date` — "Fiscal period end the estimate refers to — quarter end for a quarterly record, year end for an annual one"
- `period` — "Which horizon this record was: 0q current quarter, +1q next quarter, 0y current fiscal year,
  +1y next fiscal year. The same label repeats across many dates, **because the file keeps the history**"
- `epsTrendCurrent … epsTrend90daysAgo` — "The same EPS consensus as it stood at those points"

and the worked example is annotated: "the record above is the first of Apple's 96, **read on 18 August
2026**, and the estimate fields in it **move as analysts publish**."

So: the "history" the product advertises is history of **target fiscal periods**, not of observation
dates. There is **no as-of, updated, snapshot or timestamp field anywhere in the response**, the
endpoint takes **no `from`/`to` filters**, and the trailing 7/30/60/90-day values are anchored to the
moment you call the API. There is no way to ask what the consensus was on 2014-06-30, and no way to
prove that a past-period row was frozen rather than recomputed, because nothing records when it was
written. Documented history also starts around 2017, below the 2010 floor.

Verdict: **NOT_SUITABLE_FOR_BACKTESTING_REVISIONS**, exactly the failure mode the brief anticipated.

### 3.3 Alpha Vantage `EARNINGS_ESTIMATES` — **class B (weak)**, history starts 2017

The free `demo` key serves the full IBM response, so the schema was characterised without an account
(`reports/phase9a/raw/alphavantage_EARNINGS_ESTIMATES_IBM_20260921.json`). The endpoint is listed as
"Trending", not "Premium", so it appears to be on the free tier (25 requests/day) — the demo key is
restricted to IBM, so per-symbol behaviour beyond IBM is **UNVERIFIED**.

41 rows: 39 fiscal quarters from **2017-06-30** to 2026-12-31 plus 2 fiscal years. Fields:
`date`, `horizon`, `eps_estimate_average/high/low`, `eps_estimate_analyst_count`,
`eps_estimate_average_{7,30,60,90}_days_ago`, `eps_estimate_revision_{up,down}_trailing_{7,30}_days`,
`revenue_estimate_average/high/low`, `revenue_estimate_analyst_count`.

`date` is the fiscal period end. **There is no observation-date field.** However, the past-period rows
are not live: for the 2017-06-30 quarter the row still reads current 2.7500, 7d 2.7500, 30d 2.7500,
60d 2.7700, 90d 3.1700. A live row for a quarter reported nine years ago would show all five values
equal, because nobody revises a settled period. The dispersion across the lag fields is therefore
evidence that the row was **frozen at a snapshot near that quarter's report date** and retained
(see `PHASE9A_POINT_IN_TIME_TESTS.md`, test T3).

That makes it genuinely class B — but weak B, for three reasons that compound:

1. **The anchor date is not observable.** "30 days ago" is 30 days before an unrecorded date we can
   only assume is the report date. Every feature built on it inherits an unverifiable timing assumption.
2. **One snapshot per fiscal period**, taken at the *end* of the estimation window. A backtest may
   only use it after the report date, so it yields the revision history of the quarter that has just
   been reported — not a forward-looking consensus we could have traded on ahead of it.
3. **History starts 2017-06**, below the 2010 floor. Per the brief: do not backtest.

### 3.4 Financial Modeling Prep — **class C. REJECT_FMP_FOR_REVISION_BACKTESTING**

FMP's `analyst-estimates` / `financial-estimates` endpoints return one row per target fiscal period.
FMP's own educational material (2026-08-13, "Align Earnings Dates, Fiscal Quarters, Estimates, and
Reported") states the limitation more bluntly than any competitor would:

> "Estimate matching requires point-in-time evidence: A current consensus response should not be
> described as the pre-announcement estimate unless the record was actually observed before the
> announcement or the dataset explicitly provides historical vintages."

and lists "Reconstructing historical knowledge from a current response" as the canonical error, closing with:

> "If the workflow needs historical consensus, retain repeated snapshots or **use a source that
> explicitly supports point-in-time estimate vintages**."

No separate FMP revisions time-series product was found. FMP does sell `historical-grades` and
`historical-ratings` — dated analyst *rating* actions, not consensus estimates — which is a different
family and not a substitute. Rejected regardless of price.

### 3.5 Intrinio — **HIGH_QUALITY_BUT_OUTSIDE_CURRENT_BUDGET**

Intrinio resells the same Zacks estimates (EPS, sales, surprises, long-term growth, ratings, target
prices; "20+ years" history). Every one of those feeds is tagged **ENTERPRISE** and licensed for
**Business Use**. The self-serve **Individual plan is USD 150/month** and its feed list does not
include any estimate feed. Enterprise starts at **USD 1,250/month** plus per-feed charges.

### 3.6 Finnhub — priced out

Public pricing now has exactly two tiers: **Free (USD 0)** and **All-In-One (USD 3,500/month, billed
annually)**. EPS and revenue estimates ("20+ years historical & 5 years forward") sit entirely in the
paid tier. 70× the budget ceiling; PIT semantics were not pursued further.

### 3.7 Polygon.io / Benzinga — wrong content, over budget

Benzinga analyst datasets on Polygon start at **USD 99/month for individual users**, history to 2012.
The content is analyst *ratings, price targets and insights*, not consensus EPS estimate snapshots.
Not the family being audited, and above the ceiling.

### 3.8 Estimize / ExtractAlpha — contact-gated, structurally unsuitable as primary

Crowdsourced estimates plus a licensed sell-side consensus; historical test files are offered free to
academics and fintech developers on request. Coverage starts ~2011, is concentrated in names with
enough contributors, and is contributor-driven, so the cross-section is self-selected in a way that
would need its own survivorship treatment. Not a primary source; a possible corroborating dataset
only if a human requests access.

### 3.9 LSEG I/B/E/S Point-in-Time, FactSet, S&P Capital IQ, WRDS — the academic standard, not available

I/B/E/S Point in Time is a daily snapshot database from 2000-01-01 and is what the literature uses.
Institutional licensing only; WRDS requires an institutional affiliation. Out of reach, recorded for
completeness.

### 3.10 Open Source Asset Pricing (Chen & Zimmermann) — free, and the one genuinely useful free asset

Not a consensus database, but directly relevant and free. The October 2025 release publishes 209
firm-level predictor characteristics plus monthly and daily long-short portfolio returns for 212
predictors, under an academic citation licence.

`SignalDoc.csv` (`reports/phase9a/raw/osap_SignalDoc_20260921.csv`) shows **21 signals in the
`Analyst` data category**, sourced from IBES, and they are the exact hypothesis family Phase 9B would
test — including `AnalystRevision` ("EPS forecast revision"), `REV6` ("Earnings forecast revisions"),
`ChNAnalyst`, `ForecastDispersion`, `EarningsForecastDisparity`, `FEPS`, `sfe`, `UpRecomm`/`DownRecomm`.
The construction code is public: `AnalystRevision` is FY1 `meanest(t) / meanest(t-1)` on the IBES
monthly summary file, output as `[permno, yyyymm, AnalystRevision]`
(`reports/phase9a/raw/osap_AnalystRevision_construction_20260921.py`).

Two hard limits, stated plainly:

- **Identifier.** Firm-level files are keyed on CRSP `permno`. We have no CRSP licence and no legitimate
  permno↔ticker crosswalk, so the firm-level panel **cannot be joined to the local EODHD price panel**.
  It cannot produce a tradable strategy here.
- **Signals, not consensus.** We would inherit their feature definitions rather than define our own.

What it *can* do is decisive and costs nothing: the published **long-short portfolio return series**
need no identifier mapping at all. Restricted to the development window (≤ 2017-12) they answer,
before any money is spent, whether the analyst-revision mechanism was still alive gross-of-costs in
the modern sample. Since those portfolios are decile long-short, CRSP-universe and costless, they are
an **upper bound** on what a long-only retail implementation could capture. If the mechanism is
already dead there, no purchase is justified. That is the Stage 0 gate in `PHASE9B_DRAFT.md`.

## 4. Coverage, survivorship and live continuity

| requirement | best available answer |
| --- | --- |
| **2010–2017 development history** | Only Zacks ZEEH (1979+) and ZSEH (2000+) clear it — institution-only. Alpha Vantage starts 2017-06; EODHD ~2017; Polygon/Benzinga 2012 and wrong content. |
| **Delisted issuers in the *signal*** | Zacks: "23,000+ listed and delisted" (ZEEH), "6,000+ delisted" (ZSEH) — the only audited source that states delisted estimate coverage explicitly. Alpha Vantage, EODHD and FMP make no such claim; a universe built from them would be conditioned on 2026 survival, on top of the 1997–99 truncation already documented in the local EODHD panel. |
| **Live continuity** | Zacks feeds update daily and would carry research → paper → live without changing the signal definition. Alpha Vantage updates live but only ever exposes one frozen row per period. OSAP is annual-release research data ending 2024-12 and cannot support live trading. |

## 5. Honesty notes on this audit

- Nothing was purchased, no account was created, no form was submitted, and no paid tier was probed.
- The EODHD probe used the existing subscription token; it was never printed, and the evidence bundle
  was scanned to confirm no file contains it.
- The Alpha Vantage sample contains estimate values for fiscal periods inside the locked 2018–2021 and
  2022–2026 windows. **No price, return or performance figure from any locked window was read**, and
  those values were used only to characterise vendor schema semantics — never to form, tune or select
  a signal. The data lock is intact.
- The Zacks `obs_date` immutability claim is **documented but not empirically verified**: proving that
  old rows are never rewritten requires two reads separated in time, which requires access. A free,
  account-only immutability test is specified in `PHASE9A_POINT_IN_TIME_TESTS.md` (test T5) and is a
  precondition in the Phase 9B draft rather than an assumption.
- 358 automated tests pass at this checkpoint. No repository code was changed by this audit.
