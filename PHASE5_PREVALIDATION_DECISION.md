# PHASE5_PREVALIDATION_DECISION

# **DO_NOT_OPEN_2025**

Branch A classification: **TREND_REPLICATION_FAILURE**

Basis: PHASE5_TREND_FROZEN_SPEC.md section 5 (hash 96b70e8c..., fixed before any cohort-2 performance), applied to the supplemented cohort-2 replication E047_20260909T151953 and its analysis E048_20260909T152237. Cohort 2 (PHASE5_COHORT2.json, SHA256 5ca28d27..., eligibility 2020-12-31): LINK, LTC, XRP, BCH, BNB, ADA, EOS, TRX, XTZ, XLM, VET, ETC; window 2021-01-01..2024-12-31; frozen seven-vote slow trend only; stress costs 9.05 bps per side plus actual funding; one sleeve per asset; equal-weight cohort portfolio net of 14 bps allocation-transfer estimates. Branch B (capital-efficiency research) does not enter this decision by construction.

## Gate conditions

| # | Condition | Threshold | Observed | Result |
| --- | --- | --- | --- | --- |
| G1 | Assets | >= 8 | 12 | PASS |
| G2 | Positive net fraction | >= 2/3 | 5 of 12 = 0.417 (positive: BNB, ADA, XLM, VET, ETC) | FAIL |
| G3 | Positive Sharpe fraction | >= 2/3 | 10 of 12 = 0.833 | PASS |
| G4 | Median Sharpe | >= 0.3 | 0.295 | FAIL (by 0.005) |
| G5 | Median two-factor alpha (underlying + BTC) | > 0 | +31.1% per year (9 of 12 positive; 1 interval excludes zero) | PASS |
| G6 | Common-time-block 95% lower bound of the median two-factor alpha | > 0 at 14/30/60 days | -37.0% / -30.5% / -33.3% per year | FAIL |
| G7 | New names (7): positive-net fraction >= 1/2 and median Sharpe > 0 | both | 3 of 7 = 0.429 positive; median Sharpe 0.250 | FAIL |
| G8 | Calendar-2021 portfolio return | > 0 | +87.4% | PASS |
| G9 | Portfolio positive in >= 3 of 4 years | required | 2021 +87.4%, 2022 -6.5%, 2023 -10.6%, 2024 +36.6% (2 of 4) | FAIL |
| G10 | Asset-conservative 14 bps: portfolio > 0 and positive fraction >= 1/2 | both | portfolio +75.5%; positive fraction 0.417 | FAIL |
| G11 | Volatility-scaled slippage: portfolio > 0 | required | +78.4% | PASS |
| G12 | Remove best year: portfolio > 0 | required | +14.2% (2021 removed) | PASS |
| G13 | Top-5 trade share < 50%; top-year share < 60% | both | 15.4%; 60.4% | FAIL (top year) |
| G14 | Portfolio maximum drawdown | > -40% | -56.7% | FAIL |
| G15 | Cohort overlap with Phase 4 | <= 50% | 5 of 12 = 41.7% | PASS |
| G16 | No unresolved accounting/data defects | required | trade-contribution reconciliation exact; documented archive gaps in TRX/XLM/VET supplemented from official daily archives before the valid run; first pass retained as superseded | PASS |

Nine of sixteen conditions fail. Under the frozen classification rule, TREND_REPLICATION_FAILURE applies because the median net return is negative (-32.1%) and the positive fraction is at most one half (0.417); the mixed-replication and weak-signal labels are therefore not reached.

## What the numbers say and do not say

- The sign of the risk-adjusted effect largely transported (10 of 12 positive Sharpe, 9 of 12 positive two-factor alpha, 2021 portfolio +87%), but the compounded outcome did not: sleeves run at 0.74 average gross exposure through 78-96% drawdowns, so volatility drag turns a median Sharpe of 0.30 into a median net loss of 32%. A replication gate written on net returns, as this one was, fails; the same evidence read through arithmetic Sharpe alone would read "weak". Both readings are recorded; the preregistered one governs.
- The cross-cohort meta-analysis does not rescue it: cohort 2 over the same 2022-2024 window as cohort 1 has a portfolio Sharpe of 0.32 against 0.75 for cohort 1, the two cohort portfolios are 0.88 correlated, the difference in portfolio Sharpe has a 95% interval of [-1.08, +0.16], and every dependence-aware interval (cohort 2, new names, cohort 1) includes zero.
- 2021 is genuinely new evidence and it is positive (portfolio +87%, 7 of 12 assets positive, median Sharpe 0.68 in that year), but it is also the single best year (60.4% of positive P&L) and the year of the largest synchronised alt rally in the sample; the remaining three years net to -3% for cohort 2.

## Consequences

- 2025 remains LOCKED; 2026 UNTOUCHED. No PRE_2025_FINAL_FREEZE.md exists.
- The slow-trend mechanism is downgraded: as a stand-alone sleeve on liquid-but-old altcoin perpetuals it does not survive an independent cohort at 1x sizing. E040 remains the frozen benchmark, unmodified; no rescue by parameter, timeframe, sizing or cohort change is permitted inside Phase 5.
- Cumulative economic hypotheses: 386 after E047 (Branch B architectures add two more when E049 completes: 388).
