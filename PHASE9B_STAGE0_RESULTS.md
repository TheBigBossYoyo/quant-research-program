# PHASE 9B STAGE 0 — RESULTS

Executed 2026-09-21 under `PHASE9B_STAGE0_PREREGISTRATION.md`
(sha256 `8f107feb574ac6878211a65606e431bd263228839f29616f4eba662cd18c0082`) as repaired by
`PHASE9B_STAGE0_AMENDMENT1.md`. Source: OSAP October 2025 release, sha256
`6cdaf0ff05…7a1817`. Machine record: `reports/phase9b/PHASE9B_STAGE0_RUN.json`. Full table:
`PHASE9B_STAGE0_RESULTS.csv`. Superseded first run: `reports/phase9b/superseded_run1/`.

All returns are decimal. Annualized mean = 12 × monthly mean. Annualized volatility = √12 × monthly
sample sd. Newey-West lag from the frozen rule `floor(4·(T/100)^(2/9))`: 4, 4 and 3 for the EARLY,
MODERN and RECENT windows. Nothing dated 2018-01-01 or later was loaded.

**This is a low-friction external mechanism screen on published third-party portfolios, not a backtest
of anything this programme could trade.**

---

## 1. Long-short spreads (the sorting test)

| signal | window | n | ann. mean | ann. vol | Sharpe | NW t | cumulative |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **AnalystRevision** | EARLY 1990-2004 | 180 | **+9.92%** | 5.98% | 1.66 | **6.54** | +328% |
| **AnalystRevision** | **MODERN 2005-2017** | 156 | **+2.39%** | 6.50% | 0.37 | **1.28** | +32.5% |
| **AnalystRevision** | RECENT 2010-2017 | 96 | **+2.32%** | 4.66% | 0.50 | 1.48 | +19.4% |
| REV6 | EARLY 1990-2004 | 180 | +10.31% | 8.88% | 1.16 | 4.66 | +340% |
| REV6 | MODERN 2005-2017 | 156 | **+7.04%** | 10.66% | 0.66 | **2.48** | +131% |
| REV6 | RECENT 2010-2017 | 96 | +7.42% | 6.80% | 1.09 | 3.33 | +77.5% |

The primary signal's spread survives in sign and collapses in significance. Its Sharpe falls from 1.66
to 0.37 and its t from 6.5 to 1.3 — the sort still separates returns on average, but over thirteen
years of monthly data you cannot distinguish that average from zero.

## 2. Early versus modern decay

| signal | 1990-2004 | 2005-2017 | modern / early |
| --- | ---: | ---: | ---: |
| **AnalystRevision** | +9.92%/yr | +2.39%/yr | **0.241** |
| REV6 | +10.31%/yr | +7.04%/yr | 0.683 |

The primary signal retains about **a quarter** of its pre-2005 strength. This is the standard
post-publication decay pattern, and here it is severe enough to cross the significance threshold.

## 3. Long-leg test — the part that matters for a long-only book

`AnalystRevision`, port 05, against the two benchmarks frozen before execution.

### B1 — EWCOV (gate): equal-weighted average of the covered stocks, same file, same universe

| window | n matched | long leg | benchmark | **excess** | NW t of excess |
| --- | ---: | ---: | ---: | ---: | ---: |
| MODERN 2005-2017 | 156 / 156 | +10.41%/yr | +9.59%/yr | **+0.82%/yr** | 0.79 |
| RECENT 2010-2017 | 96 / 96 | +13.13%/yr | +12.74%/yr | **+0.39%/yr** | 0.34 |

Positive in both windows, so gate C5 passes — but by a margin of well under one percent a year, with
t-statistics of 0.79 and 0.34. The long leg is, statistically, the average covered stock.

### B2 — CRSP value-weighted market (reported, not gating)

| window | n matched | long leg | market | **excess** | NW t of excess |
| --- | ---: | ---: | ---: | ---: | ---: |
| MODERN 2005-2017 | 156 / 156 | +10.41%/yr | +9.60%/yr | **+0.82%/yr** | 0.27 |
| RECENT 2010-2017 | 96 / 96 | +13.13%/yr | +14.08%/yr | **−0.95%/yr** | −0.30 |

**`beats_b1_but_not_b2 = true`.** The preregistration required this pattern to be flagged, and it has
occurred: in 2010-2017 the long leg beats the equal-weighted covered universe and **loses to the
value-weighted market**. That is the third time this programme has produced that exact object — the
Phase 8 insider-purchase cell and the Phase 8B repurchase cell (E062) both beat an equal-weighted
universe and lost to the index a retail account could actually buy. The long leg also carries 18-21%
annualized volatility against the market's 12-14%.

For completeness, `REV6`'s long leg behaves the same way: +2.16%/yr over B1 (t 1.12) and +2.41%/yr
over B2 (t 0.58) in 2005-2017, but **−0.18%/yr** against B2 in 2010-2017.

## 4. Gate-by-gate

| # | condition | threshold | observed | result |
| --- | --- | --- | --- | --- |
| C1 | AnalystRevision LS 2005-2017 mean | > 0 | +2.39%/yr | **PASS** |
| C2 | AnalystRevision LS 2005-2017 NW t | ≥ 2.0 | **1.28** | **FAIL** |
| C3 | AnalystRevision LS 2010-2017 mean | > 0 | +2.32%/yr | PASS |
| C4 | REV6 LS 2005-2017 mean | > 0 | +7.04%/yr | PASS |
| C5 | AnalystRevision long-leg excess over B1 > 0 in both windows | both > 0 | +0.82%, +0.39% | PASS |

Four of five pass. **C2 fails**, and C2 is the condition that separates "the sort still works" from
"the sort still points the right way on average". Under the frozen rule — C1 holds, C2 fails —
the classification is `AMBIGUOUS_ANALYST_REVISION_EVIDENCE`.

## 5. Integrity of this run

- The preregistration and source hashes were re-verified before any statistic was computed.
- Run 1 contained two mechanical defects (percent-vs-decimal units; last-trading-day vs calendar
  month-end alignment), documented in `PHASE9B_STAGE0_AMENDMENT1.md` **before** the corrected run and
  predicted there to be gate-invariant. The corrected run reproduced **all five condition flags
  identically**, and the script asserts this automatically and raises if any gate flips. Run 1 is
  retained unchanged; none of its numbers is quoted as a result.
- The repair changed the reported magnitudes and fixed the B2 diagnostic. It did not change, and could
  not have changed, the decision.
- 376 tests pass, 18 of them specific to this stage.
- **0 cells added. Cumulative ledger 490.** No additional OSAP predictor was loaded or inspected.
