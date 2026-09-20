# PHASE5_PLAN - independent slow-trend replication (Branch A) and capital-efficient implementation research (Branch B)

Started 2026-09-09 after Phase 4 closed as CROSS_ASSET_WEAK_SIGNAL / DO_NOT_OPEN_2025. E040 stays FROZEN RESEARCH BENCHMARK (hash 9928aa46...). 2025 LOCKED, 2026 UNTOUCHED, both enforced by guard_dates/guard_path on every read.

## Primary economic hypothesis (Branch A, one hypothesis, cumulative 386 when run)

A slow/medium-term trend persistence premium exists across liquid crypto perpetuals and appears in independent cohorts and regimes when the exact frozen seven-vote slow-trend rule (PHASE5_TREND_FROZEN_SPEC.md) is applied unchanged at 4h with Phase 4 execution/accounting.

## Branch A design (frozen before any cohort-2 performance)

1. Second cohort, eligibility date 2020-12-31 (one year earlier than Phase 4): all archived USDT-M perpetual contracts with daily history in data/raw/universe/klines_1d; listing on or before 2020-03-31 (>= 275 days known history at selection; the archive panel begins 2020-01-01 so a 365-day rule would leave only BTC/ETH); >= 90% of calendar days observed since listing during 2020; median daily quote turnover >= 20m USDT over 2020-07-01..2020-12-31; top 12 by that liquidity excluding BTC/ETH; later delistings retained with cash sleeves after documented termination. Script: research/phase5_cohort.py; output PHASE5_COHORT2_PREREGISTRATION.md + PHASE5_COHORT2.json/.sha256. Hashed before any strategy run.
2. Overlap analysis with the Phase 4 cohort (names, liquidity rank similarity, underlying return correlation, common-factor loadings) is reported before performance and determines the independence label: the "genuinely new" evidence cells are (a) the non-overlapping names over 2021-2024 and (b) calendar 2021 for every cohort-2 name (a period never used for any strategy performance in Phases 3-4).
3. Data: monthly 1h klines from listing to 2024-12, monthly markPriceKlines where Binance publishes them, funding archives from 2021-01; checksum-verified; supplement rule from Phase 4 applies to any documented gap; hourly event accounting unchanged. Primary window 2021-01-01..2024-12-31 (warm-up from listing, no pre-2021 performance evaluated).
4. Engine: phase4_engine.ledger(component='trend') exactly; no breakout; one sleeve per asset; equal-weight cohort portfolio; inverse-vol asset weighting secondary.
5. Cost cases (diagnostics, not hypotheses): base 7.05, stress 9.05 (primary), slippage 1.5x/2x, asset-conservative 14 bps, extra 4h delay, adverse funding +1 bp, and a new volatility-scaled slippage case (slippage = 4 bps x max(1, asset 30-day vol / BTC 30-day vol, lagged), capped at 4x) as the older-cohort execution-realism bound. Historical hourly gap statistics (|open - previous close|) and mark/trade deviations are reported per asset as execution-risk descriptors.
6. Statistics: per-asset stats (phase4_stats.stats), factor regressions (PRIMARY alpha = unconditional two-factor intercept on underlying + BTC, the Phase 4 lesson; the Phase 4 five-factor state model reported secondarily), common-time-block bootstrap 14/30/60 x 2000 (seed 20260909), hierarchical cohort-level summary (cohort 1 trend-only 2022-2024 from E044; cohort 2 2021-2024; new-names cell; 2021 cell), preregistered calendar half-year regimes plus lagged BTC-200-day trend state, long/short decomposition from ledger long_pnl/short_pnl, crash windows (2021-05, 2021-12..2022-06, 2022-11 FTX, 2024-08), concentration removals, Monte Carlo.
7. Gates and classifications: PHASE5_TREND_FROZEN_SPEC.md section 5, fixed now.

## Branch B design (CAPITAL_EFFICIENCY_RESEARCH; new architectures, new IDs; never presented as E040)

1. Small-capital universe from venue rules and history only (PHASE5_CAPITAL_UNIVERSE.md): USDT-M perpetual in the 2026-09-08 rule snapshot with status TRADING, minimum notional <= 20 USDT, lot value <= 5 USDT at the last development close, listed on or before 2020-12-31 with complete hourly history on disk; ranked by the Phase 4 as-of-2021-12-31 liquidity table; subsets N = 2,3,4,5 = top-N by that liquidity rank. No performance input.
2. Architectures (each preregistered in PHASE5_CAPITAL_SPEC.md before performance): B1 trend-only; B2 one position per asset, portfolio-level capital split (no sub-sleeves); B3 score-based positioning (target exposure_i = score_i x capital / N, risk scalar 1.0 and 0.5); dead-band {0, 0.10, 0.25} on score change; minimum-trade accumulation buffer; causal 20% volatility-target overlay (lagged 30-day portfolio vol, cap 1x gross). Capital 500 / 1,000 / 2,500 / 5,000 USDT with exact lot steps and minimum notionals.
3. Metrics: target vs achieved weight, tracking error vs unconstrained, skipped-order fraction, turnover and cost, Sharpe/DD retention vs the unconstrained trend-only portfolio; classifications per mandate section 37.

## Order of work and resume points

1. PHASE5_TREND_FROZEN_SPEC.md (done when hashed) -> 2. cohort-2 selection + overlap (E046) -> 3. acquisition + integrity (ENV009) -> 4. replication run (E047) -> 5. analysis, temporal, long/short, cross-cohort (E048) -> 6. Branch B spec, universe, run (E049) -> 7. red team, decision, conclusion -> 8. EQUITY_DATA_FEASIBILITY.md (desk assessment only, no purchase).
Run every Phase 5 script with PYTHONUTF8=1 from research/; never edit research/ while a run is in progress.
