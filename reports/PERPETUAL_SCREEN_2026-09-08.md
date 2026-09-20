# Directional perpetual screen — development only

**No candidate qualifies for promotion.** Lower futures fees and short access did not produce robust evidence from the registered momentum/reversal family.

E010 tested 36 signal configurations: BTCUSDT and ETHUSDT, 1/4/24-hour bars, 3/12/48-bar momentum or reversal. Six long baselines were included. Each ran with fee-only, base and stressed costs of 5/7/14 basis points per executed notional. Initial directional exposure was 50% of account equity; signed quantities and funding, side changes, current quantity steps/minima, and a latched risk halt were explicitly modeled. No account, orders or private API were used.

All 24 hourly/four-hour configurations had negative base-cost returns. Daily ETH 48-bar momentum alone passed the cheap screen. Its subsequent audit failed:

| Measure | Base | Stress | Stress plus one extra signal-bar delay |
|---|---:|---:|---:|
| Indicative annual return | 9.67% | 8.39% | 0.74% |
| Daily Sharpe | 0.46 | 0.42 | 0.18 |
| Maximum observed drawdown | -39.00% | -39.08% | -38.28% |
| Executed fills | 52 | 52 | 51 |

Stressed calendar returns were 25.76% in 2022, 2.01% in 2023 and -0.72% in 2024. Delay sensitivity and concentration in 2022 undermine the economic case. The additional delay was a falsification test, not a replacement parameter.

E011 used 10,000 daily block resamples at 7/30/60-day lengths with a correction for 119 tested configurations. Daily returns were compared with a lagged short-rate accrual opportunity-cost reference and the similarly adjusted long-perpetual baseline. Even the ordinary 95% intervals for mean return and benchmark intercept included zero. The 30-day stressed annual intercept interval was approximately -22.64% to 42.05%. No validation data was needed to reject promotion.

The first E010 run, E010_20260908T170827, is superseded. A data audit found a zero-volume futures hour on 28 October 2024 at 20:00 UTC for both assets, and a regression exposed that the new ledger initially ignored tradability. The corrected run E010_20260908T171214 defers fills at such observations. Thirty-three tests pass, including signed funding, short accounting, round trips, flips and unavailable fills. Full failed configurations and costs remain in metrics.csv/results.json. Audit: E011_20260908T171422.

These are indicative screens, not verified liquidation backtests. Current filters are applied as forward-feasibility assumptions; account-specific fees/maintenance, executable spreads/depth, funding/fill timestamp micro-ordering and intrahour shocks remain unresolved. Return figures are in USDT. The Treasury accrual comparison is an opportunity-cost proxy, not a tradable index. No OOS claim is made.

The 2025 validation set remains unanalyzed; 2026 final data remains undownloaded and locked. The next independent research branch should test a genuinely different preregistered mechanism, such as aggregate aggressive-flow information on perpetuals, before any broader feature or ML search. Do not repeatedly optimize these rejected trailing-return rules.
