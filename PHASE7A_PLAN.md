# PHASE7A_PLAN - Zero-additional-cost EODHD alpha search (opened 2026-09-12)

## 0. Inherited state
Cumulative ledger 455 cells. Closed families (not reopened): stock momentum 12/6/9-1 in every tested form, residual momentum, vol-scaled momentum, sector-ETF momentum, dividend yield, long-term reversal, low beta/variance at stock level (family-level modern failure), every SPY/bond allocation overlay, GTAA. Locks unchanged: development < 2018-01-01; validation 2018-2021 unopened; holdout 2022-01..2026-08 untouched. No purchases.

## 1. Objective
Extract the remaining research value of the paid EODHD data (EOD All-World + S&P 500/400/600 historical constituents) before cancellation: find any genuinely distinct, low-turnover, long-only mechanism with plausible net profitability for a EUR 500-1,000 Trading 212 account in today's market. Modern evidence first (2000-2017 required, 2010-2017 preferred; point-in-time constituent data cover 2012-04..2017-12).

## 2. Funnel and gates (fixed before any result)

Stage 1, E055 cross-sectional screen (cheap, gross, no portfolio): on the Tier 2 LIQ1000 universe (1998-2017, integrity rules I1-I5, eligibility as E051) and on Tier 1 PIT S&P 1500 (2012-2017), for each preregistered signal: Fama-MacBeth monthly slope of next-month open-to-open return on the rank-normalised signal (HAC t), decile long-only spread (top decile in the preregistered direction, equal weight, minus the equal-weight eligible universe) with HAC t, decile monotonicity (Spearman). Windows: 1998-2017, 2000-2017, 2010-2017; Tier 1 2012-2017.
Advance gate A (per signal): (A1) 2010-2017 top-decile gross excess vs the EW universe >= +2 percent a year on Tier 2; (A2) 2000-2017 HAC t of that excess >= 1.5; (A3) Fama-MacBeth slope sign agrees with the preregistered direction in 2000-2017 and 2010-2017; (A4) Tier 1 2012-2017 top-decile excess >= 0. Signals failing A are REJECTED at Stage 1 (no portfolio compute).

Stage 2, E056 index-event study (PIT constituents 2012-04..2017-12; effective dates only, no announcement dates exist in the data): for every addition, deletion and migration event, cumulative abnormal return versus the equal-weight PIT universe from the first open after the effective date to +1, +3, +6, +12 months; events split into (i) deletions where the security keeps trading >= 6 months (discretionary deletions and demotions), (ii) deletions where the series ends within 2 months (mergers/delistings; untradeable, reported only), (iii) additions, split into promotions from another S&P index and outside additions. Tradable long-only calendar-time portfolios (equal weight of all events entered in the last H months, H fixed at 6, monthly rebalance, base costs): P1 buy discretionary deletions/demotions; P2 buy outside additions (mirror test, expected to fail post-2010); P3 buy promotions (expected to fail). Directions fixed now: post-deletion REVERSAL (P1 positive), post-inclusion NO DRIFT or reversal (P2, P3 non-positive). Advance gate B: P1 net excess vs the Tier 1 EW universe >= +3 percent a year with HAC t >= 1.5 over 2012-2017 and positive in at least 4 of the 6 calendar years; event count >= 150.

Stage 3, E057 portfolio stage (only for Stage 1/2 survivors): E051 engine, top-N long-only (N in {30, 50}), monthly and quarterly rebalance, three cost cases, three delisting rules; E051 survivor gates S0-S6 and multiplicity across all Phase 7A cells; feasibility at EUR 500/1,000.

Stage 4 (only after >= 2 independent survivors): rank-average combination; conditioning on beta/idiosyncratic volatility as a risk filter, counted as cells.

## 3. Preregistered signal families for E055 (direction fixed; one primary definition each; no parameter search)

| ID | Family (economic mechanism) | Definition at signal date t (month-end close; all inputs <= t) | Direction of the long-only bucket |
| --- | --- | --- | --- |
| S1 | 52-week-high proximity (anchoring; George-Hwang) | split-adjusted close_t / max split-adjusted close over the trailing 252 days | high ratio |
| S2 | overnight-return persistence (Lou-Polk-Skouras: investor-clientele demand shows up overnight) | sum over the trailing 252 days of log(open_d / close_{d-1}) | high |
| S3 | intraday-return reversal (same paper: intraday component reverses) | sum over the trailing 252 days of log(close_d / open_d) | LOW (contrarian) |
| S4 | abnormal volume / attention (Gervais-Kaniel-Mingelgrin high-volume premium) | mean dollar volume last 21 days / mean dollar volume last 252 days | high |
| S5 | liquidity premium (Datar-Naik-Radcliffe, Amihud) | 63-day median dollar volume (level, within the top-1000) | LOW |
| S6 | range compression / quiet-price state | (max close - min close over the last 21 days) / close_t, split-adjusted | LOW |
| S7 | idiosyncratic volatility (Ang et al.; stock-level modern check, conditioning candidate) | sd of daily residuals from a 63-day regression on SPY | LOW |
| S8 | market beta (conditioning candidate) | 252-day beta on SPY daily returns | LOW |
| S9 | lottery demand (Bali-Cakici-Whitelaw MAX) | maximum daily return in the last 21 days | LOW |
9 cells (cumulative 455 -> 464). E056 adds 3 tradable portfolios plus descriptive event tables (cumulative 464 -> 467). E057 cells are counted when preregistered.

## 4. Costs, execution, benchmarks
As E051: signal at the month-end close, orders at the next open, held open-to-open; base 20/20.3 bps per side, optimistic 3, stress 30-45; Shumway delisting rule with sensitivities; EW eligible universe of the same tier and SPY as benchmarks; EUR 500-1,000 feasibility.

## 5. Phase outcome (exactly one)
PROMISING_CANDIDATE_READY_FOR_VALIDATION (a Stage 3 survivor passes S0-S6 and multiplicity, frozen with a hash) / EODHD_OPPORTUNITY_SET_EXHAUSTED / NEW_DATA_SOURCE_JUSTIFIED (a family passes on the family level but needs data outside the subscription). Plus a cancellation recommendation for the two EODHD subscriptions.
