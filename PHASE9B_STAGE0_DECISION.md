# PHASE 9B STAGE 0 — DECISION

Decided 2026-09-21 by the rule frozen in `PHASE9B_STAGE0_PREREGISTRATION.md` §6, on the corrected run
documented in `PHASE9B_STAGE0_RESULTS.md`.

## Decision

# AMBIGUOUS_ANALYST_REVISION_EVIDENCE

Programme-level status:

# ANALYST_REVISION_FAMILY_DATA_BLOCKED_AND_EXTERNAL_EVIDENCE_INCONCLUSIVE

## Why

The frozen rule routes on two conditions before anything else is considered:

> condition 1 fails → `REJECT_ANALYST_REVISION_MECHANISM`
> condition 1 holds but condition 2 fails → `AMBIGUOUS_ANALYST_REVISION_EVIDENCE`

| | threshold | observed |
| --- | --- | --- |
| **C1** AnalystRevision long-short 2005-2017 mean | > 0 | **+2.39%/yr — passes** |
| **C2** AnalystRevision long-short 2005-2017 NW t | ≥ 2.0 | **1.28 — fails** |

C3 (+2.32%/yr in 2010-2017), C4 (REV6 +7.04%/yr) and C5 (long-leg excess over B1 positive in both
windows) all pass. That does not rescue it: the rule was written so that C1 passing and C2 failing is
ambiguous regardless of what follows, precisely so that a weak primary result could not be carried
over the line by corroborating evidence.

## What this actually means

The analyst-revision sort still points in the right direction in the modern era and has lost roughly
three quarters of its strength: 9.92%/yr in 1990-2004 against 2.39%/yr in 2005-2017, a ratio of 0.24,
with the Sharpe falling from 1.66 to 0.37. Over thirteen years of monthly data the modern spread
cannot be distinguished from zero.

And the part that matters for this programme is weaker still. We can only trade long-only. The long
leg beat the equal-weighted covered universe by **+0.82%/yr** (t 0.79) in 2005-2017 and **+0.39%/yr**
(t 0.34) in 2010-2017 — positive, and indistinguishable from the average covered stock. Against the
value-weighted market it was **+0.82%/yr** and then **−0.95%/yr**, at 18-21% volatility versus the
market's 12-14%.

**The preregistered warning fired.** `beats_b1_but_not_b2 = true`: the long leg beats an equal-weighted
universe and loses to the index a retail account could buy. This programme has now produced that exact
object three times — the Phase 8 insider-purchase cell, the Phase 8B repurchase cell (E062), and now
the published long leg of the analyst-revision sort. Each time the equal-weighted comparison flattered
a position that a retail investor would have been better off not holding.

And all of that is measured **gross, costless, equal-weighted, monthly-rebalanced, across the whole
CRSP cross-section including microcaps** — in someone else's implementation, on data we cannot license.
Any Trading 212 version at EUR 500-1,000 would be strictly worse: fewer names, 0.15% FX each way,
monthly turnover, no microcaps.

## What is explicitly NOT concluded

- **Not a rejection.** C1 passed. The mechanism is not demonstrably dead, and saying so would overstate
  the evidence in the other direction.
- **REV6 does not rescue it.** REV6 is materially stronger (+7.04%/yr, t 2.48, retaining 68% of its
  early strength) and it is the most tempting thing in this result. It was frozen as *corroboration*
  and explicitly cannot substitute for the primary signal. Promoting it now would be exactly the
  signal-shopping the preregistration was written to prevent. Its long leg also fails against the
  value-weighted market in 2010-2017 (−0.18%/yr), so it would not have changed the economic picture.
- **No additional analyst signal was inspected.** `ChNAnalyst`, `ForecastDispersion` and
  `EarningsForecastDisparity` were excluded by name before execution and were not loaded. An ambiguous
  result may not be converted into a pass by looking at them, and it has not been.
- **No threshold, window, benchmark or HAC lag was changed after the returns were seen.**

## Consequences

- The analyst-consensus-revision family stays **open but dormant**: data-blocked by licence
  (Phase 9A), and not rescued by the free external evidence.
- **No purchase.** Stage 0 was explicitly incapable of authorising one, and an ambiguous result with a
  long leg that loses to the market in the recent window is the weakest possible case for spending
  money on institution-only data.
- **No strategy, no validation, no holdout, no paper trading.** Validation 2018-2021 and holdout
  2022-01..2026-08 remain completely unopened.
- **Ledger: 0 cells added, cumulative 490.** Stage 0 analysed fixed third-party published portfolios
  for source-selection purposes. It is recorded, as the preregistration required, that **this result
  determined whether the family remains open** — two signals, three windows, one primary decision
  statistic.

## What would change this

1. A class-A point-in-time consensus source becoming licensable to an individual (§4 of
   `PHASE9A_RECOMMENDATION.md`). Even then, this Stage 0 result is a reason for scepticism, not
   enthusiasm: any Phase 9B Stage 1 would start from a long leg worth under 1%/yr gross.
2. A genuinely different use of consensus data than cross-sectional revision sorting — a different
   mechanism, requiring its own preregistration, not a retune of this one.
3. Nothing else. Re-running this with different windows, lags, benchmarks or signals is not permitted
   and would not be informative.

## Next

Per `PHASE9A_RECOMMENDATION.md` §6, option 1 has now been executed and returned an ambiguous verdict.
The open moves are option 2 (a free Nasdaq Data Link Personal account, to confirm what ZEEH pricing
shows — optional, and it will not unlock deep history) and option 3 (name the next genuinely distinct
mechanism, or close the equity programme at "no qualifying strategy on obtainable data").

On the evidence, option 3 is the honest one to put to the user.
