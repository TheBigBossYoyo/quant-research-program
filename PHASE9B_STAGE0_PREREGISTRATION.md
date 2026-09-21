# PHASE 9B STAGE 0 — PREREGISTRATION

Frozen 2026-09-21. This document is hashed and committed **before any return observation is read,
parsed, aggregated, printed or plotted**. Its SHA256 is recorded in the commit that introduces it and
is re-verified by the execution script before any statistic is computed.

Stage 0 is **not** a strategy test and **adds no cell to the 490-cell ledger**. It is an external
evidence screen used for one purpose: deciding whether the analyst-consensus-revision family deserves
further discussion despite the Phase 9A finding that point-in-time consensus data is licence-blocked
for individuals (`PHASE9A_RECOMMENDATION.md`).

---

## 0. What Stage 0 is, stated correctly

Stage 0 is a **LOW-FRICTION EXTERNAL MECHANISM SCREEN**.

The OSAP portfolios are:

- **published third-party implementations**, built by other researchers from licensed IBES data we
  cannot see;
- **gross and costless** relative to any retail implementation we could run;
- useful for determining whether **analyst-revision sorting still generated cross-sectional return
  differences** in the development era;
- **not a direct backtest of any strategy this programme could trade.**

**Correction carried forward from `PHASE9B_DRAFT.md`.** That draft described these long-short
portfolios as an "upper bound" on a long-only implementation. That claim is withdrawn: it is not
generally true. Because

```
long-short return = long-leg return - short-leg return
```

and the short leg can have either sign, a long-short spread can be smaller **or** larger than the
long leg's own excess return. A large spread can be produced entirely by a collapsing short leg while
the long leg does nothing, and a modest spread can coexist with a strong long leg. Nothing about the
spread bounds the long side in either direction.

This matters directly here, because our implementation must be **long-only**. The long leg is
therefore the economically relevant object, and it is tested separately in §5 rather than inferred.

## 1. Frozen signal set

| role | signal | OSAP definition (from `SignalDoc.csv`, verbatim) |
| --- | --- | --- |
| **PRIMARY** | `AnalystRevision` | "keep fpi == \"1\", last obs each month. Signal is meanest / last month's meanest." Hawkins, Chamberlin and Daniel (1984). |
| **CORROBORATION** | `REV6` | "Define revisions as the change in the mean earnings estimate (meanest) for the next quarter from month t-1 to t, scaled by stock price in month t-1. REV6 is the sum of that variable from months t-6 to t." Chan, Jegadeesh and Lakonishok (1996). |

**Excluded from this decision, by name, and not to be inspected during Stage 0:** `ChNAnalyst`,
`ForecastDispersion`, `EarningsForecastDisparity`, and every other member of the OSAP `Analyst`
category. They are different mechanisms (coverage decline, disagreement, forecast-horizon disparity),
not consensus-revision drift. Excluding them prevents signal shopping across the category.

**No additional OSAP predictor may be scanned after `AnalystRevision` and `REV6` results are seen.**

Both signals carry `Sign = 1` and `Stock Weight = EW` and `Portfolio Period = 1` (monthly rebalancing)
in `SignalDoc.csv`. `AnalystRevision` has `LS Quantile = 0.2`; `REV6` is unspecified and the published
file uses quintiles for both.

## 2. Frozen data sources and hashes

### 2.1 Portfolio returns (primary source)

| field | value |
| --- | --- |
| release | Open Source Asset Pricing (Chen and Zimmermann), **October 2025 release** |
| page | https://www.openassetpricing.com/data/ |
| item | "All 212 predictor portfolio sort csvs in a single file (still following OPs)" |
| URL | `https://drive.usercontent.google.com/download?id=1g7w-yQ6Cg2qbMEkER9Q3vgns4JszXQo6&export=download&confirm=t` |
| local | `data/raw/phase9b/PredictorPortsFull_202510.csv` (gitignored; vendor file) |
| bytes | 77,651,932 |
| **sha256** | **`6cdaf0ff051222b813e6f8404d7a30b94e146b421625f202bd04473fe97a1817`** |
| columns | `signalname, port, date, ret, signallag, Nlong, Nshort` |
| rows | 1,226,794 across 212 distinct signals |

Structural facts established **before the freeze**, from counts only, by
`research/phase9b_stage0_fetch.py manifest` (recorded in
`reports/phase9b/PHASE9B_STAGE0_SOURCE_MANIFEST.json`):

- both signals expose ports `01..05` plus `LS`; dates are month-end;
- `AnalystRevision` 1976-03-31 → 2024-12-31, 2,585 rows before 2018;
- `REV6` 1976-09-30 → 2024-12-31, 2,976 rows before 2018;
- for `AnalystRevision`, the `LS` row's `Nlong` series matches port `05` exactly (502 pre-2018
  months, median 673, min 171, max 4063) and its `Nshort` matches port `01` (median 670.5, min 171,
  max 3530). **This establishes, without reading any return, that `LS = port 05 − port 01` and that
  port `05` is the long leg.** The same holds for `REV6`.
- `AnalystRevision` has badly unbalanced middle bins: of 502 pre-2018 months, all five quintiles are
  populated in only **141**, while ports `01` and `05` are populated in all 502. This is expected from
  a discrete signal (the `meanest` ratio piles at exactly 1.0 when no analyst moved), which collapses
  interior breakpoints. `REV6` is balanced (496/496).

**Ordering disclosure, stated plainly.** The file was downloaded and hashed *before* this
preregistration was written, because a hash cannot be recorded for a file that has not been fetched.
Only `signalname`, `port`, `date`, `Nlong` and `Nshort` were ever loaded. The `ret` column was not
read, sampled, aggregated or displayed at any point before this document was hashed and committed, and
`research/phase9b_stage0_fetch.py` is committed alongside it so that this is auditable rather than
asserted. No knowledge of any return observation informed any choice below.

### 2.2 Secondary market benchmark

| field | value |
| --- | --- |
| source | Kenneth R. French Data Library, monthly 3-factor file, already on disk from 2026-09-09 |
| file | `data/raw/phase6/french/F-F_Research_Data_Factors_CSV.zip` |
| **sha256** | **`b840dba55d319f4818fc7300e65c52eff5f64870c8d495fa58ff5d4cd749f5eb`** |
| CRSP vintage | 202607 |
| loader | `research/phase6_french.load('ff3_monthly', block='block0', segment='development')` |
| series | `Mkt-RF + RF` = CRSP value-weighted total market return, decimal |

## 3. Frozen windows and the date lock

| window | range (inclusive) | role |
| --- | --- | --- |
| **EARLY** | 1990-01-01 .. 2004-12-31 | decay reference |
| **MODERN PRIMARY** | 2005-01-01 .. 2017-12-31 | **the Stage 0 decision window** |
| **RECENT ROBUSTNESS** | 2010-01-01 .. 2017-12-31 | preregistered recent-era check |

**Hard exclusion.** Every observation dated **2018-01-01 or later is rejected in code immediately
after the date column is parsed and before the `ret` column is used for anything.** Nothing from
2018 onward may be loaded into memory for analysis, summarised, plotted, printed or inspected.

Implementation, both layers mandatory:

1. `frame = frame[frame['date'] < '2018-01-01']` applied at load time, followed by an assertion that
   `frame['date'].max() < 2018-01-01`, raising `RuntimeError` otherwise;
2. the existing repository firewall `research/phase6_lock.enforce(frame, segment='development')`,
   whose development bound is `[1900-01-01, 2018-01-01)` and which raises `LockError` for the
   validation and holdout segments unless a human-authorised unlock file with a matching decision-
   document hash exists. No unlock file exists and none will be created.

Our own validation (2018-2021) and holdout (2022-01..2026-08) are untouched by Stage 0 and remain
closed under every outcome.

## 4. Frozen statistics

For each of `AnalystRevision` and `REV6`, on the `LS` port, in each of the three windows:

- number of monthly observations `n`;
- arithmetic **mean monthly** return;
- **annualized arithmetic mean** = `12 × monthly mean`;
- **annualized volatility** = `sqrt(12) × monthly standard deviation` (sample sd, ddof=1);
- **Sharpe** = annualized mean / annualized volatility. For a long-short spread this is a
  zero-financing-cost convention with no risk-free subtraction, and is labelled as such;
- **Newey-West t-statistic** of the mean monthly return;
- **cumulative return**, `prod(1+r) − 1`, reported as **descriptive output only** and used in no gate.

### Newey-West lag rule — fixed here, before any return is read

```
L = floor( 4 * (T / 100) ** (2/9) )      T = number of monthly observations in the window
```

This is the standard Newey-West (1994) / Stock-Watson automatic bandwidth rule. It is a function of
sample size alone, contains no discretion, and is applied identically to every series and every
window. For the windows above it yields L = 4 (EARLY, T=180), L = 4 (MODERN, T=156) and L = 3
(RECENT, T=96).

Implementation: `statsmodels.api.OLS(y, np.ones(T)).fit(cov_type='HAC',
cov_kwds={'maxlags': L, 'use_correction': False})`, t-statistic of the constant.

**No other HAC lag will be computed, and none will be substituted after results are seen.** If any
alternative lag is ever reported it must be labelled a post hoc diagnostic and must not touch a gate.

## 5. Long-leg test — source and benchmarks frozen now

**Availability: YES.** The published file exposes the quantile portfolios separately, and §2.1
establishes structurally that port `05` is the long leg for both signals. The long-leg gate is
therefore observable and `LONG_LEG_GATE_NOT_OBSERVABLE` does not apply.

Two benchmarks are frozen here. Both are fixed before any return is read; neither may be swapped,
re-weighted or supplemented afterwards.

### B1 — GATE benchmark: `EWCOV`, same file, same universe, same weighting

For each month, across the quantile ports `01..05` that are populated in that month:

```
EWCOV(t) = sum_p ( ret_p(t) * Nlong_p(t) ) / sum_p ( Nlong_p(t) )
```

This is the equal-weighted return of exactly the stocks the published sort placed in a portfolio that
month — same source file, same CRSP universe, same EW weighting, same rebalancing, same month. It is
derived from the published data rather than imported, so it is not a manufactured benchmark.

`Nlong`-weighting rather than a simple mean across ports is required because `AnalystRevision`'s
interior bins are unpopulated in most months (§2.1); a simple mean would silently mis-weight the
cross-section. Months in which `EWCOV` cannot be formed are excluded and **counted in the output**.

### B2 — SECONDARY benchmark, reported but NOT gating: CRSP value-weighted market

`Mkt-RF + RF` from §2.2. Same underlying universe (CRSP), different weighting (value-weighted), and it
approximates an index a retail investor can actually buy.

**B2 cannot change the Stage 0 classification.** It is preregistered as a reported diagnostic because
this programme has twice produced a candidate that beat an equal-weighted universe and lost to the
value-weighted index it would have had to compete with — the Phase 8 insider cell and the Phase 8B
repurchase cell (E062). If the long leg beats B1 but loses to B2, that pattern **must be stated
explicitly in `PHASE9B_STAGE0_DECISION.md`** as a material caveat on any supportive verdict.

For each signal and each of B1 and B2, in **2005-2017** and **2010-2017**, report: long-leg return,
benchmark return, excess (long − benchmark), and the Newey-West t-statistic of the excess under the
same lag rule.

## 6. Frozen decision rule

`AnalystRevision` is the primary signal. `REV6` corroborates and cannot substitute for it.

**MECHANISM SUPPORTED — all five must hold:**

1. `AnalystRevision` 2005-2017 long-short mean **> 0**;
2. `AnalystRevision` 2005-2017 Newey-West **t ≥ 2.0**;
3. `AnalystRevision` 2010-2017 long-short mean **> 0**;
4. `REV6` 2005-2017 long-short mean **> 0**;
5. `AnalystRevision` long-leg excess over **B1** **> 0 in both** 2005-2017 and 2010-2017.

**Outcomes:**

| condition | classification |
| --- | --- |
| 1-5 all hold | `MECHANISM_SUPPORTED_BUT_PIT_DATA_LICENSE_BLOCKED` |
| 1-4 hold, long-leg gate unavailable | `MECHANISM_SUPPORTED_LONG_ONLY_RELEVANCE_UNRESOLVED` |
| condition 1 fails | `REJECT_ANALYST_REVISION_MECHANISM` |
| condition 1 holds but condition 2 fails, **or** the remaining evidence conflicts | `AMBIGUOUS_ANALYST_REVISION_EVIDENCE` |

"Remaining evidence conflicts" means: 1 and 2 hold but any of 3, 4 or 5 fails.

**An ambiguous result may not be converted into a pass by inspecting additional analyst signals, by
changing a window, by changing the HAC lag, by changing the benchmark, or by any other means. These
thresholds do not move after returns are seen.**

## 7. Interpretation limits

A supportive Stage 0 result does **not** authorize a purchase, a strategy, validation access, holdout
access, or paper trading. It means only:

`ANALYST_REVISION_MECHANISM_SUPPORTED_BUT_PIT_DATA_LICENSE_BLOCKED`

A rejection means:

`ANALYST_REVISION_FAMILY_CLOSED_ON_EXTERNAL_DEVELOPMENT_ERA_EVIDENCE`

An ambiguous result means:

`ANALYST_REVISION_FAMILY_DATA_BLOCKED_AND_EXTERNAL_EVIDENCE_INCONCLUSIVE`

## 8. Multiplicity and ledger

**No strategy cell is added. The cumulative ledger stays at 490.** Stage 0 analyses fixed, pre-existing,
third-party published portfolios for source-selection purposes; it constructs no signal, fits no
parameter, selects no universe and trades nothing.

It is nevertheless recorded explicitly that **the Stage 0 result determines whether this research family
remains open**, and that two signals were examined in three windows with one primary decision window —
a decision made on a single preregistered primary statistic, not on the best of six.

## 9. Known limitations, stated before the result

- These are **third-party** portfolios built from IBES data we cannot inspect or reproduce. We are
  trusting Chen and Zimmermann's implementation; `SignalDoc.csv` rates `AnalystRevision`'s replication
  quality only `2_fair` and notes the original paper "only longs top 20 stocks according to signal. We
  were more flexible."
- They are **gross and costless**, equal-weighted, monthly rebalanced, over the full CRSP cross-section
  including microcaps that Trading 212 may not offer and that we could not trade at EUR 500-1,000.
- The original-paper samples are old (`AnalystRevision` 1975-1980, `REV6` 1977-1992), so 2005-2017 is
  far out of sample for both — which is the point, and also a reason to expect decay.
- `AnalystRevision`'s unbalanced interior bins mean its quintile sort is coarser than a clean quintile
  sort; the extreme portfolios are well populated but the cross-section is not evenly divided.
- A positive Stage 0 tells us a **sorting variable we cannot legally obtain** still separated returns.
  It does not tell us that a long-only, top-N, cost-bearing retail portfolio would have worked.

## 10. Execution

Executed exactly once, by `research/phase9b_stage0.py`, which re-verifies the SHA256 of this document
and of the source file before computing anything and refuses to run on a mismatch.

Outputs: `PHASE9B_STAGE0_RESULTS.md`, `PHASE9B_STAGE0_RESULTS.csv`, `PHASE9B_STAGE0_DECISION.md`.
