# EUR500 operational feasibility

No deployment feasibility claim. Exact exchange/account minimum notionals and quantity steps have not been established without using current market endpoints. Candle volume does not establish spread or capacity. The table gives reproducible lower-bound scenarios for the frozen allocation; ignoring lot rounding is optimistic. Reversal turnover can combine an exit and entry, so these figures are optimistic bounds, not a complete order-validity simulation. FX is a scenario, not a2026 price observation.

| eur | usd_per_eur_assumption | minimum_notional_usd_assumption | executions | fraction_below_min | capital_eur_for_99pct_orders | capital_eur_for_all_observed_orders | status |
|---|---|---|---|---|---|---|---|
| 500 | 0.9 | 5 | 10960 | 0.030201 | 709.44 | 1.2134e+08 | SCENARIO_ONLY; quantity steps, split reversal fills, prices at execution and actual venue filters not verified |
| 500 | 0.9 | 10 | 10960 | 0.73029 | 1418.9 | 2.4268e+08 | SCENARIO_ONLY; quantity steps, split reversal fills, prices at execution and actual venue filters not verified |
| 500 | 0.9 | 20 | 10960 | 0.98896 | 2837.8 | 4.8536e+08 | SCENARIO_ONLY; quantity steps, split reversal fills, prices at execution and actual venue filters not verified |
| 500 | 1 | 5 | 10960 | 0.015237 | 638.5 | 1.0921e+08 | SCENARIO_ONLY; quantity steps, split reversal fills, prices at execution and actual venue filters not verified |
| 500 | 1 | 10 | 10960 | 0.72774 | 1277 | 2.1841e+08 | SCENARIO_ONLY; quantity steps, split reversal fills, prices at execution and actual venue filters not verified |
| 500 | 1 | 20 | 10960 | 0.87473 | 2554 | 4.3683e+08 | SCENARIO_ONLY; quantity steps, split reversal fills, prices at execution and actual venue filters not verified |
| 500 | 1.1 | 5 | 10960 | 0.012044 | 580.45 | 9.9279e+07 | SCENARIO_ONLY; quantity steps, split reversal fills, prices at execution and actual venue filters not verified |
| 500 | 1.1 | 10 | 10960 | 0.72573 | 1160.9 | 1.9856e+08 | SCENARIO_ONLY; quantity steps, split reversal fills, prices at execution and actual venue filters not verified |
| 500 | 1.1 | 20 | 10960 | 0.85958 | 2321.8 | 3.9711e+08 | SCENARIO_ONLY; quantity steps, split reversal fills, prices at execution and actual venue filters not verified |

Minimum practical capital: UNVERIFIED. The99% execution figure is an indicative threshold allowing1% order omissions, which would itself change the strategy and is not adopted. The all-orders figure is a lower bound before lot rounding; no allocation is distorted to fit EUR500.
