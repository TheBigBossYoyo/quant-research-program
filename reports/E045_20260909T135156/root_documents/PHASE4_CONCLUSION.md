# Phase4 conclusion

**CROSS_ASSET_WEAK_SIGNAL - DO_NOT_OPEN_2025**

The exact E040 signals were reused, with user-approved accounting corrections tested before freeze.12 historically preregistered assets were evaluated over2022-2024, including later contract termination.

Positive net assets: 66.7%. Median Sharpe: 0.702. Median factor-adjusted annual intercept: 53.87%. Positive alpha fraction: 75.0%. Median maximum drawdown: -37.4%. Primary portfolio Sharpe: 0.912; CAGR: 22.62%; maximum drawdown: -24.0%.

## Results

| asset | history_start | history_end | sharpe | alpha | asset_beta | max_dd | trades | top5_trade_positive_pnl_share | trend_sharpe | breakout_sharpe | conservative_stress_sharpe | classification |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOLUSDT | 2022-01-01 00:00:00+00:00 | 2024-12-31 23:00:00+00:00 | 1.1625 | 1.5815 | 0.077811 | -0.31745 | 198 | 0.58068 | 1.2179 | 0.22416 | 1.092 | positive net risk-adjusted sign |
| XRPUSDT | 2022-01-01 00:00:00+00:00 | 2024-12-31 23:00:00+00:00 | 0.12544 | -0.20185 | 0.14875 | -0.61689 | 249 | 0.65015 | 0.26821 | -0.37023 | 0.029606 | positive net risk-adjusted sign |
| BNBUSDT | 2022-01-01 00:00:00+00:00 | 2024-12-31 23:00:00+00:00 | 0.025779 | 0.51877 | 0.11022 | -0.38521 | 274 | 0.54952 | -0.021653 | 0.14147 | -0.11033 | positive net risk-adjusted sign |
| DOTUSDT | 2022-01-01 00:00:00+00:00 | 2024-12-31 23:00:00+00:00 | 0.58999 | -0.21039 | 0.24415 | -0.3043 | 199 | 0.49116 | 0.64959 | 0.058816 | 0.50356 | positive net risk-adjusted sign |
| DOGEUSDT | 2022-01-01 00:00:00+00:00 | 2024-12-31 23:00:00+00:00 | 1.0082 | 1.5003 | 0.35543 | -0.35205 | 174 | 0.60553 | 0.79416 | 0.88393 | 0.93838 | positive net risk-adjusted sign |
| ADAUSDT | 2022-01-01 00:00:00+00:00 | 2024-12-31 23:00:00+00:00 | 1.0106 | -0.38238 | 0.27707 | -0.3637 | 215 | 0.56371 | 0.69 | 0.95995 | 0.9207 | positive net risk-adjusted sign |
| AVAXUSDT | 2022-01-01 00:00:00+00:00 | 2024-12-31 23:00:00+00:00 | 1.1517 | 0.3824 | 0.22543 | -0.34954 | 221 | 0.50471 | 0.93947 | 0.75096 | 1.0733 | positive net risk-adjusted sign |
| AXSUSDT | 2022-01-01 00:00:00+00:00 | 2024-12-31 23:00:00+00:00 | 0.81455 | 1.1281 | 0.1912 | -0.3343 | 204 | 0.36206 | 0.65511 | 0.58764 | 0.73809 | positive net risk-adjusted sign |
| MATICUSDT | 2022-01-01 00:00:00+00:00 | 2024-09-04 08:00:00+00:00 | 0.48205 | 1.1337 | 0.14399 | -0.43658 | 196 | 0.38179 | 0.275 | 0.59206 | 0.40692 | positive net risk-adjusted sign |
| FTMUSDT | 2022-01-01 00:00:00+00:00 | 2024-12-31 23:00:00+00:00 | 0.96313 | 2.0146 | 0.19118 | -0.44399 | 165 | 0.5076 | 1.1478 | -0.098827 | 0.91089 | positive net risk-adjusted sign |
| LTCUSDT | 2022-01-01 00:00:00+00:00 | 2024-12-31 23:00:00+00:00 | -0.30665 | 0.2492 | 0.1426 | -0.655 | 240 | 0.53981 | -0.38185 | 0.11402 | -0.41204 | negative/nonpositive sign |
| LINKUSDT | 2022-01-01 00:00:00+00:00 | 2024-12-31 23:00:00+00:00 | -0.32165 | 0.55858 | 0.25804 | -0.67111 | 256 | 0.52387 | -0.38762 | 0.061838 | -0.41276 | negative/nonpositive sign |

## Predefined stress cases

| case | total_net_return | cagr | volatility | sharpe | sortino | calmar | max_dd | drawdown_duration_days | expected_shortfall_95 | annual_arithmetic_return | trades | average_trade | median_trade | win_rate | profit_factor | payoff_ratio | expectancy | top_month_positive_pnl_share | top_quarter_positive_pnl_share | top_year_positive_pnl_share | positive_asset_fraction |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 0.92163 | 0.243 | 0.26079 | 0.96393 | 1.535 | 1.0694 | -0.22723 | 514 | -0.029271 | 0.25138 | 0 | None | None | None | None | None | None | 0.24303 | 0.31566 | 0.54253 | 0.66667 |
| stress | 0.8449 | 0.22624 | 0.26088 | 0.91164 | 1.4486 | 0.94192 | -0.2402 | 516 | -0.02932 | 0.23783 | 0 | None | None | None | None | None | None | 0.24244 | 0.31806 | 0.5451 | 0.66667 |
| slippage_1_5 | 0.77124 | 0.20972 | 0.26097 | 0.85939 | 1.3626 | 0.82912 | -0.25294 | 541 | -0.029368 | 0.22427 | 0 | None | None | None | None | None | None | 0.24183 | 0.32031 | 0.54871 | 0.66667 |
| slippage_2 | 0.70052 | 0.19341 | 0.26106 | 0.80717 | 1.277 | 0.72857 | -0.26547 | 542 | -0.029418 | 0.21072 | 0 | None | None | None | None | None | None | 0.24126 | 0.32028 | 0.5536 | 0.66667 |
| asset_conservative | 0.66792 | 0.18574 | 0.26111 | 0.78238 | 1.2365 | 0.68452 | -0.27135 | 542 | -0.029442 | 0.20429 | 0 | None | None | None | None | None | None | 0.24101 | 0.32033 | 0.55646 | 0.66667 |
| delay1 | 0.69058 | 0.19109 | 0.25887 | 0.80436 | 1.2582 | 0.67426 | -0.2834 | 506 | -0.029734 | 0.20822 | 0 | None | None | None | None | None | None | 0.23285 | 0.3342 | 0.63488 | 0.66667 |
| adverse_funding | 0.60074 | 0.16962 | 0.26127 | 0.72963 | 1.15 | 0.6016 | -0.28195 | 544 | -0.029513 | 0.19063 | 0 | None | None | None | None | None | None | 0.24128 | 0.32083 | 0.56786 | 0.66667 |

## Scientific limits

- Same2022-2024 crypto regime across all assets;12 names are not12 independent time histories.
- Historical2021 liquidity cohort avoids current-survivor selection, but archive coverage is not guaranteed exhaustive. The universe was previously used for other signal research.
- The primary window is three years;2021 is excluded from performance and cannot explain the primary result. No new regime is manufactured.
- Funding is now complete where audited but settlement marks remain hourly-open proxies; missing marks use disclosed trade-open proxies. Adverse funding stress is reported.
- Open prices are execution proxies. Current spreads, lot rounding, minimum notionals and liquidation tiers are not fully verified; EUR500 feasibility is not established.
- Targets preserve the original sizing; drift above1x can occur, so this is not hard-capped unlevered exposure.
- Strategy-return sleeve combinations require external capital transfers; estimated costs are deducted for portfolio diagnostics.
- BTC/ETH are shown solely as discovery comparators and never enter replication sign statistics.

2025 remains LOCKED.2026 remains UNTOUCHED. No live trading, subscriptions or capital exposure. No parameter changes or losing-asset exclusions.

Charts and full statistical outputs: C:\Users\Youssef\Documents\Trading\GPT 5.6 Astra plus Claude Opus 5\reports\E045_20260909T135156
