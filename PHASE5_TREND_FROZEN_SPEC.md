# PHASE5_TREND_FROZEN_SPEC - the slow-trend component as the research object

Frozen 2026-09-09 before any Phase 5 performance. This is the exact slow-trend component of frozen E040; nothing is re-parameterised. E040 itself remains the FROZEN RESEARCH BENCHMARK and is not modified.

## 1. Rule (verbatim from the Phase 4 freeze)

Input: 4h OHLC bars (UTC, epoch-aligned, complete buckets only), built from official hourly klines by phase4_engine.aggregate.
Seven votes, equally averaged, computed on completed bars (ta_ensemble.ensemble_weight):
- sign(close - SMA150), sign(close - SMA200), sign(close - SMA250);
- sign(SMA100 - SMA100 five bars earlier), sign(SMA150 - SMA150 five bars earlier), sign(SMA200 - SMA200 five bars earlier), sign(SMA250 - SMA250 five bars earlier).
Simple moving averages with full-period warm-up; unavailable votes are skipped (pandas mean, skipna); score in [-1, 1]; NaN score is flat.
Position: target exposure = score x current equity, resized only when the score changes, executed at the next scheduled 4h open at the observed hourly open; no stop, no trailing exit; terminal position marked, not liquidated; funding debited/credited to incoming holdings at each scheduled settlement (hourly event accounting); insolvency absorbing. No EMA/WMA/Supertrend substitution, no period change, no timeframe change (4h only), no volume gate, no breakout leg.

## 2. Frozen implementation hashes (unchanged from Phase 4, verified by phase4_data.freeze_check before every run)

- research/ta_ensemble.py 	a9ac9306a152d5ffe51153b634143869a28376a3301c079b31996a9f42590a24
- research/ta_engine.py 	572331a73b9d3edc1092967e3da36b8a1c5647b088828b2b4447e893ee4863ce
- research/phase4_engine.py 	4f0b81093df2aaf5e7eee5cccf4cfed06f12aae51a485d0a845d8edaba3d2fb6
- Phase 4 configuration 	aeb65b7447f0e5d923d254688d2e319695792557ec577fe69c64c5916bba0b89 (FROZEN_E040_HASH 9928aa464bd7f88bb44e76566f01593d87786ff048043620c514c20a96142ca0)

Only ledger(component='trend') is used in Branch A. Loader/analysis scripts (phase5_*.py) are not part of the frozen rule; their hashes are recorded in each results.json.

## 3. Costs and execution (Branch A)

Primary case: stress, 9.05 bps per side (5 bps taker fee + 0.05 bps half-spread + 4 bps slippage) plus actual signed funding at scheduled settlements with hourly mark-open settlement price (trade-open fallback labelled). Diagnostics: base 7.05; 1.5x slippage 11.05; 2x slippage 13.05; asset-conservative 14; one extra 4h delay at 9.05; adverse funding +1 bp per settlement against incoming holdings; volatility-scaled slippage 4 bps x max(1, lagged 30-day asset vol / lagged 30-day BTC vol) capped at 4x (older, thinner contracts pay more). Execution proxies: hourly candle opens; no depth data; hourly gap and mark/trade deviation statistics reported per asset as descriptors, never as fills.

## 4. Study windows

Cohort 2 (eligibility 2020-12-31): warm-up from listing, performance 2021-01-01..2024-12-31; 2021 is a regime never used for strategy performance in Phases 3-4. Cohort 1 (Phase 4, eligibility 2021-12-31): trend-only sleeves 2022-2024 from E044_20260909T135755, not rerun. No 2025 data of any kind; 2026 never downloaded.

## 5. Branch A gates (fixed before performance; cohort-2 trend-only, stress case, 2021-2024, one sleeve per asset, equal-weight cohort portfolio net of 14 bps allocation-transfer cost estimates)

| # | Condition | Threshold |
| --- | --- | --- |
| G1 | Assets evaluated | >= 8 |
| G2 | Positive net fraction (total net return > 0) | >= 2/3 |
| G3 | Positive Sharpe fraction | >= 2/3 |
| G4 | Median Sharpe | >= 0.3 |
| G5 | Median unconditional two-factor alpha (daily intercept on underlying + BTC, HAC 14) | > 0 |
| G6 | Common-time-block bootstrap (14/30/60-day blocks, 2000 resamples, seed 20260909) 95% lower bound of the cross-asset median two-factor alpha | > 0 for every block length |
| G7 | New-information cell: non-overlapping names (not in the Phase 4 cohort) positive-net fraction | >= 1/2 and median Sharpe > 0 |
| G8 | New-regime cell: equal-weight cohort-2 trend portfolio calendar-2021 net return | > 0 |
| G9 | Year consistency: portfolio positive in at least 3 of 4 calendar years | required |
| G10 | Asset-conservative (14 bps) case: portfolio net return > 0 and positive-net fraction >= 1/2 | required |
| G11 | Volatility-scaled slippage case: portfolio net return > 0 | required |
| G12 | Remove best calendar year: portfolio net return > 0 | required |
| G13 | Portfolio top-5 trade share of positive P&L < 50%; top calendar-year share < 60% | required |
| G14 | Portfolio maximum drawdown | > -40% |
| G15 | Cohort overlap with Phase 4 (share of cohort-2 names also in cohort 1) | <= 50% for the evidence to count as an independent cohort |
| G16 | No unresolved accounting or data defects (reconciliation, gap handling, funding coverage) | required |

Classification (exact):
- TREND_REPLICATION_FAILURE: median net return <= 0 and positive fraction <= 1/2.
- TREND_MIXED_REPLICATION: positive fraction < 2/3, or G7 fails.
- TREND_CROSS_COHORT_WEAK_SIGNAL: positive majority (G2) but any other gate fails.
- TREND_CROSS_COHORT_RESEARCH_PROMISING: G1-G11 and G15-G16 pass and only concentration/risk gates (G12-G14) fail.
- TREND_VALIDATION_ELIGIBLE: every gate G1-G16 passes.
Decision: 2025 may be opened ONLY if TREND_VALIDATION_ELIGIBLE, and then only after a separate PRE_2025_FINAL_FREEZE.md (rule, cohort rules, portfolio construction, costs, acceptance criteria hashed) and one-shot evaluation; otherwise DO_NOT_OPEN_2025. Branch B outputs never contribute to this decision.

## 6. Multiplicity

Branch A is one economic hypothesis (cumulative 386). Cost/delay/regime/long-short/concentration analyses are diagnostics. Branch B architectures (score-based positioning; volatility-target overlay) are two new architectures (cumulative 388 after they run); dead-band and buffer settings are execution diagnostics inside those architectures, not separate hypotheses. Cohort-1 trend-only results are reused from E044, not rerun.
