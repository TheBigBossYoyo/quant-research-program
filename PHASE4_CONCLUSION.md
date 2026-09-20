# PHASE4_CONCLUSION - frozen E040 cross-asset replication (2022-2024), 9 September 2026

## 1. Exact frozen strategy

Frozen before any replication performance was computed (PHASE4_E040_FROZEN_SPEC.md; canonical configuration phase4_e040_frozen_config.yaml, SHA256 aeb65b7447f0e5d923d254688d2e319695792557ec577fe69c64c5916bba0b89; FROZEN_E040_HASH 9928aa464bd7f88bb44e76566f01593d87786ff048043620c514c20a96142ca0; source hashes for ta_engine.py, ta_ensemble.py, ta_volcomp.py, ta_combo.py, phase4_engine.py and config/research.json embedded in the configuration and checked by freeze_check() before every run).

- Timeframe: 4h bars (UTC, epoch-aligned), signals from completed bars, orders at the next scheduled 4h open, funding and pre-existing stops processed on hourly observations.
- Slow-trend component: seven equally averaged votes, sign(close - SMA150/200/250) and sign(SMA100/150/200/250 - same SMA five bars earlier); full-period SMA warm-up; NaN votes skipped; target in [-1, 1]; position resized only when the target changes; no stop; terminal position marked, not liquidated.
- Compression-breakout component: prior 20-bar high/low channel; Wilder ATR14; entry only when the preceding bar's ATR percentile rank over 250 bars (minimum 120) is below 0.20; no volume confirmation; 3 x ATR stop from the prior completed bar at entry, trailing on completed 4h extremes; a stopped direction stays blocked until the raw target leaves it; terminal liquidation.
- Combination: 50/50 daily component returns (primary); causal inverse 60-day volatility (secondary, weights shifted one day, cash when undefined).
- Sizing: original target sizing on current equity; no leverage optimisation, no hard gross cap (exposure drifts above 1x between resize events and is reported, not capped).
- Costs (stress case, the preregistered primary case): 5 bps fee + 0.05 bps half-spread + 4 bps slippage = 9.05 bps per side plus actual signed funding; base 7.05 bps; 1.5x and 2x slippage; asset-conservative 14 bps; one extra 4h delay; adverse funding (+1 bp absolute per settlement against incoming holdings).

## 2. Execution/accounting defects discovered and corrected (E042, user-authorised: "correct execution/accounting, preserve all signal rules")

- Defect 1 (causality): a missing hour later inside a 4h bar could cancel an order at that bar's opening observation. Corrected by separating the raw hourly execution open from the complete-bucket signal OHLC; a later outage can no longer affect an earlier fill. Regression test: test_future_outage_does_not_cancel_earlier_open.
- Defect 2 (funding): funding owed at an earlier settlement disappeared if the position was stopped later in the same bar. Corrected by debiting/crediting funding to incoming holdings at the scheduled settlement before orders and stops. Regression tests: test_funding_precedes_stop, test_no_entry_funding_and_exit_funding, test_short_funding_credit.
- Amendment 2 (E043, before any performance): SOLUSDT has 49 funding settlements that do not fall on 4h boundaries. Funding is now applied at its actual hourly settlement while signals, entries and trailing-stop ratchets stay on the 4h schedule (test_nonboundary_funding_and_4h_orders, test_trailing_stop_ratchets_only_after_full4h_bar). No other replication asset has non-4h settlements.
- Also: absorbing insolvency, first-day return retained, funding timestamp jitter (max 31 ms) snapped to the scheduled hour with every displacement logged, funding-mark proxy with labelled trade-open fallback (6-9 settlements per asset) and a separate adverse stress.

## 3. Effect of the corrections on BTC/ETH (E042, exact original reproduced first)

| Series | Original equal-weight Sharpe | Corrected | Original CAGR | Corrected | Max DD original / corrected |
| --- | ---: | ---: | ---: | ---: | --- |
| BTCUSDT | 1.26935 | 1.26914 | 44.88% | 44.87% | -27.17% / -27.17% |
| ETHUSDT | 1.14365 | 1.14293 | 45.12% | 45.08% | -36.23% / -36.28% |

Signal arrays are identical (asserted); maximum absolute equity difference 22.6 USDT (BTC trend) to 196 USDT (ETH trend) on a 10,000 USDT path. The E040 discovery result was not caused by the defects. Measured maximum trend exposure 1.29x (BTC) and 1.51x (ETH): E040 is not a strict 1x strategy.

## 4. Frozen replication universe (E043; PHASE4_UNIVERSE.json SHA256 2785a6cc3b3f6a3e8373b92ffccc9cacefbe588c345a45366d17005dc04c9b81)

Selected as of 2021-12-31 from all archived USDT-M perpetual contracts (later delistings included): listing age >= 365 days, >= 360 observed 2021 daily bars, median daily quote turnover >= 20m USDT over 2021-07-01..2021-12-31, top 12 by that liquidity excluding BTC/ETH. Result: SOL, XRP, BNB, DOT, DOGE, ADA, AVAX, AXS, MATIC, FTM, LTC, LINK. No asset was added, removed or replaced afterwards. MATICUSDT: the contract was settled by Binance on 2024-09-04 09:00 UTC (announcement retained); the preregistered treatment exits at the last scheduled 4h open before that notice-known time, 08:00 UTC, and holds the sleeve in cash thereafter, staying in the 12-name denominator; not replaced by POL.

## 5. Data-quality and supplementation audit

All 1,126 monthly 1h kline/mark archives and 20 daily supplements are checksum-verified (SHA256 against Binance .CHECKSUM files). The E043 integrity audit, run before any replication performance, disclosed 120 missing hours in each of the SOLUSDT, XRPUSDT, FTMUSDT and LTCUSDT monthly kline archives (2022-02-26..28, 2022-04-01..02); every other history and every mark archive was complete. Official daily archives covering exactly those days were retrieved 09:23-09:24 UTC, before the first pass (E044_20260909T092223, started 09:22, finished 10:25) produced any result, so the supplementation was fixed by the integrity finding and not by performance. The merge adds rows only where the monthly archive has none and fails on any conflicting overlap (research/phase4_run.py, four regression tests). After supplementation all fourteen histories have zero missing hours. The first pass is retained and labelled superseded; the mechanism of its distortion (full-window SMAs NaN for up to 250 bars after each gap, all seven trend votes NaN for 238 bars per asset, forced flat) is documented in PHASE4_DATA_SUPPLEMENTATION_AUDIT.md together with the hashed audit table (PHASE4_DATA_SUPPLEMENTATION_ADDENDUM.md). Assets whose inputs did not change reproduce to the last digit between the first pass and the rerun.

## 6. All twelve replication results (stress case: 9.05 bps per side plus actual funding; equal 50/50 E040; 2022-01-01 to 2024-12-31; MATIC to 2024-09-04 08:00 UTC)

| Asset | Net return | CAGR | Sharpe | Sortino | Calmar | Max DD | DD days | PF | Trades | Win rate | Avg win | Avg loss | Payoff | Expectancy | Beta (asset) | Beta (BTC) | Alpha 5-factor [95% CI] | Alpha underlying-only | Top-5 trade share | Top-year share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| SOLUSDT | +198.5% | 43.9% | 1.010 | 1.73 | 1.38 | -31.7% | 266 | 1.69 | 213 | 19.3% | +8.3% | -1.0% | 8.0 | +0.76% | 0.08 | 0.00 | +134% [-24%, +293%] | +47% | 60% | 76% |
| XRPUSDT | -18.1% | -6.4% | -0.017 | -0.03 | -0.10 | -63.6% | 1074 | 0.87 | 264 | 14.4% | +5.3% | -0.8% | 6.5 | +0.07% | 0.15 | -0.05 | -11% [-136%, +114%] | -3% | 66% | 100% |
| BNBUSDT | -8.4% | -2.9% | 0.026 | 0.04 | -0.07 | -38.5% | 874 | 0.94 | 274 | 14.2% | +3.3% | -0.6% | 6.0 | -0.00% | 0.11 | -0.07 | +52% [-34%, +137%] | +0% | 55% | 100% |
| DOTUSDT | +57.8% | 16.4% | 0.590 | 0.97 | 0.54 | -30.4% | 518 | 1.30 | 199 | 21.1% | +5.5% | -1.1% | 5.1 | +0.32% | 0.25 | -0.07 | -21% [-153%, +110%] | +22% | 49% | 51% |
| DOGEUSDT | +185.9% | 41.9% | 1.008 | 1.75 | 1.19 | -35.2% | 485 | 2.13 | 174 | 26.4% | +6.2% | -1.1% | 5.6 | +0.83% | 0.36 | -0.13 | +150% [+3%, +297%] | +36% | 61% | 91% |
| ADAUSDT | +149.3% | 35.6% | 1.011 | 1.69 | 0.98 | -36.4% | 555 | 1.77 | 215 | 22.8% | +5.4% | -0.9% | 6.1 | +0.54% | 0.28 | -0.07 | -39% [-169%, +91%] | +37% | 56% | 55% |
| AVAXUSDT | +226.7% | 48.3% | 1.152 | 1.89 | 1.38 | -35.0% | 455 | 1.93 | 221 | 23.5% | +6.5% | -1.1% | 6.2 | +0.73% | 0.23 | -0.11 | +38% [-80%, +157%] | +48% | 50% | 58% |
| AXSUSDT | +121.1% | 30.2% | 0.815 | 1.39 | 0.90 | -33.4% | 316 | 1.40 | 204 | 21.6% | +6.1% | -1.1% | 5.8 | +0.49% | 0.19 | -0.15 | +113% [-37%, +263%] | +35% | 36% | 57% |
| MATICUSDT | +40.4% | 12.0% | 0.482 | 0.78 | 0.27 | -43.7% | 741 | 1.21 | 196 | 20.9% | +5.8% | -1.2% | 4.8 | +0.26% | 0.15 | -0.07 | +113% [-22%, +247%] | +19% | 38% | 51% |
| FTMUSDT | +251.3% | 52.0% | 1.060 | 1.71 | 1.17 | -44.4% | 324 | 1.62 | 172 | 21.5% | +10.1% | -1.5% | 6.7 | +0.99% | 0.18 | -0.12 | +176% [+4%, +347%] | +54% | 51% | 48% |
| LTCUSDT | -45.0% | -18.0% | -0.441 | -0.67 | -0.28 | -65.6% | 932 | 0.69 | 245 | 13.5% | +4.0% | -0.9% | 4.6 | -0.21% | 0.14 | -0.15 | +21% [-84%, +127%] | -15% | 54% | n/a |
| LINKUSDT | -47.7% | -19.4% | -0.322 | -0.50 | -0.29 | -67.1% | 964 | 0.69 | 256 | 17.6% | +4.4% | -1.2% | 3.8 | -0.18% | 0.26 | -0.18 | +56% [-80%, +191%] | -15% | 52% | 100% |

Turnover 54-76x per year of sleeve equity (annual transaction cost 4.9-6.9% of equity), average gross exposure 0.39-0.46, hourly maximum exposure 1.05-1.37 (equal E040), 1.19-1.73 on the trend sleeve alone, share of hours above 1x about 1-3%. Full per-component tables with every requested metric: PHASE4_REPLICATION_TABLES.md; per-asset stress cases: reports/E044_20260909T135755/metrics.csv. Discovery comparators on the same engine and window: BTC Sharpe 1.060 / CAGR 28.9% / DD -20.7%; ETH 0.692 / 18.0% / -36.3%.

The trend sleeve alone: Sharpe -0.53 (LTC) to 1.25 (FTM), median 0.65, drawdowns -46% to -91%. The breakout sleeve alone: Sharpe -0.37 (XRP) to 0.96 (ADA), median 0.18, drawdowns -13% to -53%.

## 7. Number positive / negative

Equal E040 net return: 8 positive (SOL, DOT, DOGE, ADA, AVAX, AXS, MATIC, FTM), 4 negative (XRP, BNB, LTC, LINK). Positive Sharpe 9 of 12 (BNB positive but below 0.03). Positive 5-factor alpha 9 of 12; positive underlying-only alpha 9 of 12 (BNB at +0.2%). Trend sleeve: 7 of 12 positive net, 9 of 12 positive Sharpe. Breakout sleeve: 7 of 12 positive net, 10 of 12 positive Sharpe. The counts are unchanged across all seven cost/delay/funding cases (8 of 12 in every case).

## 8. Median performance

Median net return +89% (three years), median CAGR 23%, median Sharpe 0.702, median maximum drawdown -37.4%, median expectancy +0.40% per trade, median trend-sleeve Sharpe 0.652, median breakout-sleeve Sharpe 0.183. Median Sharpe by cost case: base 0.735, stress 0.702, 1.5x slippage 0.669, 2x slippage 0.636, 14 bps 0.621, one extra 4h delay 0.613, adverse funding 0.577.

## 9. Factor-adjusted evidence (RAW versus FACTOR-ADJUSTED replication)

RAW: 8 of 12 positive net, median Sharpe 0.70, median return +89%.

FACTOR-ADJUSTED (preregistered daily regression on underlying, BTC, equal-weight replication market, lagged BTC 30-day volatility, lagged BTC 200-day trend sign; HAC 14): median intercept +53.6% per year, 9 of 12 positive, only DOGE and FTM with intervals excluding zero; median factor-adjusted Sharpe 1.70. Caveat recorded in the red-team report: because volatility and trend-state regressors are included, this intercept is the return conditional on zero volatility and neutral trend state, an extrapolation; the underlying-only regression gives a median intercept of +28.5% per year (9 of 12 positive, every interval including zero), betas 0.08-0.36, BTC betas -0.18 to 0.00, market betas negative.

DEPENDENCE-AWARE: common-time-block bootstrap (2,000 resamples, seed 20260909, dates resampled jointly across all names, regressions refitted per resample): median alpha 95% interval [-26%, +137%] (14-day blocks), [-25%, +139%] (30-day), [-24%, +131%] (60-day); median Sharpe [-0.15, +1.40]; positive fraction [0.42, 1.00]. The descriptive asset-only bootstrap [+5%, +124%] is reported but is invalid as inference because the names are dependent. Heterogeneity: alpha standard deviation 71 points, IQR 105 points, range -39% to +176%. Sign consistency across years: positive-asset counts 7/8/9 of 12 in 2022/2023/2024; median yearly Sharpe 0.23/0.96/0.72; median yearly factor alpha -14%/+184%/-83%.

## 10. Slow-trend replication verdict

WEAK PARTIAL REPLICATION. The sign generalizes (9 of 12 positive Sharpe, 7 of 12 positive net, median Sharpe 0.65 against 1.06/0.96 on BTC/ETH), the sleeve provides 76% of portfolio P&L and was net short through 2022, but its stand-alone drawdowns (median -63%, up to -91%) and its dependence on the two Q4 rallies (seven of the ten largest portfolio contributions) make it a beta-like risk profile, not a stand-alone edge. No component interval excludes zero after Holm correction (none excludes zero even uncorrected).

## 11. Compression-breakout verdict

DOES NOT GENERALIZE ADEQUATELY. Median Sharpe 0.18 (against 1.10/0.82 on BTC/ETH), 7 of 12 positive net, median factor intercept +13% per year and underlying-only intercept +5%, 24% of portfolio P&L, though with the lowest drawdowns (-13% to -53%) and the lowest cross-asset correlation (0.22). Its sign persists in 10 of 12 names but its economic magnitude collapsed.

Component question answer: **B, TREND ONLY, and only weakly.** E040 is not modified in response to this diagnostic.

## 12. Cross-asset portfolio performance (net of estimated allocation-transfer costs at 14 bps; stress-case sleeves)

| Portfolio | CAGR | Sharpe | Sortino | Calmar | Max DD | DD days | ES 95% | Turnover/yr | Cost/yr | Avg gross | Avg net | Alpha [95% CI] | HHI | Top month | Top year |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Equal assets, equal components (PRIMARY) | 21.5% | 0.869 | 1.37 | 0.89 | -24.1% | 516 | -3.0% | 68x | 6.4% | 0.44 | -0.04 | +66% [-13%, +144%] | 0.083 | 24.5% | 56.4% |
| Equal assets, cluster cap 50% | 20.7% | 0.869 | 1.37 | 0.89 | -23.2% | 515 | -2.9% | 66x | 6.3% | 0.42 | -0.03 | +63% [-14%, +140%] | 0.079 | 24.8% | 57.8% |
| Causal inverse-vol assets | 18.9% | 0.828 | 1.32 | 0.79 | -24.0% | 542 | -2.8% | 67x | 6.4% | 0.41 | -0.03 | +45% [-31%, +121%] | 0.087 | 25.4% | 59.9% |
| Risk parity (180-day covariance, numerically stable throughout) | 18.0% | 0.826 | 1.32 | 0.69 | -25.9% | 542 | -2.7% | 61x | 5.8% | 0.38 | -0.02 | +50% [-21%, +122%] | 0.082 | 27.2% | 61.8% |
| Equal assets, inverse-vol components (secondary) | 15.9% | 0.909 | 1.54 | 1.00 | -15.9% | 473 | -1.9% | 50x | 4.9% | 0.28 | -0.03 | +44% [-21%, +108%] | 0.083 | 18.8% | 58.5% |
| BTC E040 (corrected, same window) | 28.9% | 1.060 | 1.87 | 1.40 | -20.7% | 253 | -2.8% | | | 0.46 | | | | | |
| ETH E040 (corrected) | 18.0% | 0.692 | 1.16 | 0.49 | -36.3% | 691 | -3.1% | | | 0.43 | | | | | |
| BTC/ETH E040 50/50 (original combination) | 24.2% | 0.955 | | | -22.2% | | | | | | | | | | |
| Replication underlyings, equal-weight price-only | -7.4% | 0.272 | | | -78.5% | | | | | | | | | | |

Contribution by asset (USDT per 10,000 initial, primary): FTM 1,591; AVAX 1,519; DOGE 1,445; SOL 1,252; ADA 1,058; AXS 919; DOT 628; MATIC 521; XRP 106; BNB -35; LINK -385; LTC -499. By component: trend 6,143 (76%), breakout 1,976 (24%). Primary portfolio calendar years: 2022 +6.2%, 2023 +26.8%, 2024 +33.3%; 58% of months positive. The cross-asset portfolio is comparable to, and below, the BTC/ETH discovery combination; it is far above the replication underlyings, which lost money over the window.

## 13. Diversification evidence

Average pairwise correlations: underlying daily returns 0.64 (0.48-0.80); E040 strategy returns 0.39 (0.17-0.64); trend sleeves 0.40; breakout sleeves 0.22; drawdown paths 0.37 (-0.23 to 0.89); strategy returns on stress days (BTC down more than 5% or any day in 2022) 0.44. A DOT/ADA/AVAX/AXS cluster (0.51-0.64) is the main common block; a multi-asset causal correlation cluster (|rho| >= 0.65 over 180 days) exists on 68% of days but the 50% cluster cap changes nothing material (Sharpe 0.869 both ways). 2022 crash period: underlyings -53% to -94%; seven of twelve sleeves positive; net exposure -10% to -25% (short-tilted trend); worst sleeves LINK -46%, LTC -22%, XRP -16%, MATIC -14%. Diversification is genuine relative to holding the coins, but it is diversification within one regime: the portfolio drawdown (-24%) and the per-asset drawdowns (-30% to -67%) cluster in the same 2022-2023 window.

## 14. Concentration evidence (adversarial; no rule changed)

Primary portfolio: 2,633 component episodes; top trade 3.3% of positive P&L, top 5 13.2%, top 10 20.2%; best year 2024 with 56.4% of positive P&L; best month 24.5%. Removing the best year: +34.7% total (Sharpe 0.69). Removing the best trade contribution: Sharpe 0.80; removing the best five: +36.9%, Sharpe 0.54. Per asset the picture is worse: top-5 trades 36-66% of positive P&L, top year 48-100% (100% for XRP, BNB, LINK), and removing the best five trade intervals turns every single asset negative. Seven of the ten largest contributions are trend longs entered in October-November 2023 or 2024.

## 15. Cost and funding stress (primary portfolio; positive-asset count 8 of 12 in every case)

| Case | Per-side cost | Net return | CAGR | Sharpe | Max DD |
| --- | --- | ---: | ---: | ---: | ---: |
| base | 7.05 bps | +87.1% | 23.2% | 0.921 | -22.8% |
| stress (primary) | 9.05 bps | +79.6% | 21.5% | 0.869 | -24.1% |
| 1.5x slippage | 11.05 bps | +72.3% | 19.9% | 0.817 | -25.4% |
| 2x slippage | 13.05 bps | +65.4% | 18.2% | 0.765 | -26.6% |
| asset-conservative | 14 bps | +62.2% | 17.5% | 0.740 | -27.2% |
| adverse funding (+1 bp per settlement against holdings, at 9.05 bps) | | +55.6% | 15.9% | 0.688 | -28.3% |

No failure in the sense of a sign change; every additional 2 bps per side costs roughly 0.05 Sharpe, and the funding perturbation is the single most expensive stress.

## 16. Delay stress

One additional 4h bar of execution delay (orders at the second scheduled open after the signal): portfolio +64.2%, CAGR 17.9%, Sharpe 0.760, DD -28.3%; per-asset median Sharpe 0.613 with 8 of 12 positive. Not fragile to modest implementation delay; the degradation (0.11 Sharpe) is of the same order as doubling slippage.

## 17. Monte Carlo / bootstrap risk (2,000 resamples, seed 20260909; conditional frequencies, not calibrated probabilities)

| Portfolio | Method | Median max DD | 90th pct | 95th pct | P(DD>20%) | P(DD>30%) | P(DD>40%) | Ruin |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Primary (equal/equal) | 14-day blocks | 26.7% | 38.7% | 43.1% | 83% | 35% | 8% | 0 |
| Primary | 60-day blocks | 26.1% | 38.6% | 42.9% | 83% | 32% | 8% | 0 |
| Primary | permutation | 28.1% | 37.5% | 40.6% | 94% | 39% | 6% | 0 |
| Inverse-vol assets | 14-day blocks | 25.2% | 36.9% | 41.3% | 79% | 28% | 6% | 0 |
| Risk parity | 14-day blocks | 23.7% | 35.1% | 39.3% | 72% | 23% | 5% | 0 |
| Inverse-vol components, equal assets | 14-day blocks | 16.8% | 25.0% | 28.2% | 29% | 4% | 0.2% | 0 |

Per asset (14-day blocks): P(DD>40%) 31% (ADA) to 96% (LINK); median simulated drawdown 35-67%. Risk of ruin (equity to zero) is zero in every resample because exposure is near 1x, but exchange liquidation is not modelled and the trend sleeve drifts to 1.2-1.7x between resizes.

## 18. EUR 500 feasibility

NOT FEASIBLE. At EUR 500 each of the 24 sleeves holds about 21 USDT; the trend sleeve's typical order (0.29 x sleeve, about 6 USDT) is below the 20 USDT minimum notional on LTC and LINK for 99-100% of orders and below one whole-coin lot on AVAX (100%), BNB (79%) and AXS (65%). MINIMUM PRACTICAL CAPITAL (documented venue filters from the 2026-09-08 snapshot, end-2024 scenario prices, 5th-percentile order sizes): about 12,600 USDT if lot rounding may reach 12.5% of an order, about 31,500 USDT if it may reach 5%; AVAX's one-coin lot on the trend sleeve is binding. MATIC no longer exists and FTM is marked SETTLING in the snapshot. The portfolio was not degraded to fit EUR 500. Details: PHASE4_CAPITAL_FEASIBILITY.md.

## 19. Red-team findings (PHASE4_RED_TEAM_REPORT.md)

Strongest attacks: the return is timed to two synchronized Q4 rallies; the only dependence-aware statistic says the median effect is indistinguishable from zero; the breakout leg collapsed; two gates pass by a hair (positive fraction exactly 2/3, top-year share 56.4% of 60%); the preregistered five-factor intercept is a conditional extrapolation and must not be quoted as excess return; two of twelve contracts no longer trade; the strategy cannot be run at the research budget. Strongest defence: frozen rule, frozen cohort with losers retained, low beta, positive 2022, cost/delay/funding/concentration-removal survival, real diversification relative to the coins.

## 20. Exact preregistered gate outcome

11 of 12 conditions pass; condition 6 (common-time-block 95% lower bound of the median factor alpha > 0 at 14/30/60-day blocks) fails with lower bounds of -26%, -25% and -24% per year. Classification: CROSS_ASSET_WEAK_SIGNAL. Decision: **DO_NOT_OPEN_2025**. Gate-by-gate table: PHASE4_PREVALIDATION_DECISION.md.

## 21. 2025 status

2025 remained LOCKED throughout. No 2025 file was downloaded, read, hashed or summarised; the loader firewall and its tests are unchanged; no PRE_2025_FINAL_FREEZE.md exists because the gate did not pass.

## 22. One-shot validation

Not performed (gate failed). Nothing in this phase constitutes out-of-sample validation of E040 beyond the 2022-2024 cross-section.

## 23. 2026 confirmation

2026-01-01 onward was never downloaded, queried, listed or inspected. Every acquisition path and date guard ends at 2024-12-31 (tests test_2026_firewall, guard_path on every archive read). The 2026-09-08 exchange-filter snapshot contains contract rules only, no prices.

## 24. Final classification

**CROSS_ASSET_WEAK_SIGNAL - DO_NOT_OPEN_2025.** The exact frozen E040 mechanism transported its sign to a majority of an independently selected cross-section, with low beta and diversified, cost-robust portfolio behaviour, but not its magnitude: the breakout leg did not generalize, the effect is unresolved once cross-asset dependence is respected, and the pass margins are thin. E040 stays frozen and unmodified; no validation or capital stage is authorised; the strategy is not implementable at EUR 500. Cumulative economic hypotheses: 385. Reproducibility: reports/E044_20260909T135755 (replication; results.json with source, config and universe hashes), reports/E045_20260909T140237 (analysis; results.json, charts/), superseded runs retained and labelled (E044_20260909T092223 first pass, E044_20260909T135238 guard failure, E045_20260909T135156 dry run), 124 tests passing.

## Files

PHASE4_E040_FROZEN_SPEC.md, phase4_e040_frozen_config.yaml, PHASE4_FREEZE_HASHES.json, PHASE4_UNIVERSE.json/.sha256, PHASE4_UNIVERSE_PREREGISTRATION.md, PHASE4_DATA_EXECUTION_ADDENDUM.md, PHASE4_DATA_SUPPLEMENTATION_ADDENDUM.md (hashed), PHASE4_DATA_SUPPLEMENTATION_AUDIT.md, PHASE4_REPLICATION_TABLES.md, PHASE4_REPLICATION_RESULTS.csv, PHASE4_COMPONENT_RESULTS.csv, PHASE4_PORTFOLIO_RESULTS.csv, PHASE4_SCOREBOARD.md, PHASE4_FACTOR_ANALYSIS.md, PHASE4_CONCENTRATION_AUDIT.md, PHASE4_MONTE_CARLO.md, PHASE4_CAPITAL_FEASIBILITY.md, PHASE4_RED_TEAM_REPORT.md, PHASE4_PREVALIDATION_DECISION.md, PHASE4_FUTURE_HYPOTHESES.md.
