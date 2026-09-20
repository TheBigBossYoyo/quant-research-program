# EUR 500 implementation feasibility and minimum practical capital

Venue filters: documented rules from the dated snapshot futures_exchangeInfo_20260908T094615.json (server time 2026-09-08); this is rule documentation, not a market observation, and it does not verify account-specific fees, margin tiers or spreads. Prices used to convert lot sizes to notionals are the last development close on disk (2024-12-31) and are labelled scenario prices; no 2025/2026 data is used. Order sizes are the actual order notionals of the supplemented replication (stress case) expressed as fractions of the component sleeve equity.

Structure being sized: 12 assets x 2 components = 24 equal sleeves. At EUR 500 and 1.0 USDT per EUR each sleeve holds 20.83 USDT. The trend sleeve resizes in fractional steps (median order about 0.29 x sleeve, a one-vote change out of seven); the breakout sleeve enters at about 1 x sleeve.

## Contract status and filters

| Asset | Status in snapshot | Lot step | Lot value (USDT, scenario price) | Min notional (USDT) | Trend median order / sleeve | Breakout median order / sleeve |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| SOLUSDT | TRADING | 0.01 | 1.89 | 5 | 0.288 | 0.999 |
| XRPUSDT | TRADING | 0.1 | 0.21 | 5 | 0.287 | 0.999 |
| BNBUSDT | TRADING | 0.01 | 7.02 | 5 | 0.287 | 0.999 |
| DOTUSDT | TRADING | 0.1 | 0.66 | 5 | 0.289 | 0.999 |
| DOGEUSDT | TRADING | 1.0 | 0.32 | 5 | 0.288 | 0.999 |
| ADAUSDT | TRADING | 1.0 | 0.84 | 5 | 0.288 | 0.999 |
| AVAXUSDT | TRADING | 1.0 | 35.69 | 5 | 0.287 | 0.999 |
| AXSUSDT | TRADING | 1.0 | 6.21 | 5 | 0.288 | 0.999 |
| MATICUSDT | ABSENT (contract terminated) | n/a | n/a | n/a | 0.289 | 0.999 |
| FTMUSDT | SETTLING | 1.0 | 0.68 | 5 | 0.288 | 0.999 |
| LTCUSDT | TRADING | 0.001 | 0.10 | 20 | 0.288 | 0.999 |
| LINKUSDT | TRADING | 0.01 | 0.20 | 20 | 0.288 | 0.999 |

## At EUR 500 (1.0 USDT per EUR)

| Asset | Component | Sleeve (USDT) | Median order (USDT) | Share of orders below min notional | Share of orders below one lot |
| --- | --- | ---: | ---: | ---: | ---: |
| SOLUSDT | trend | 20.83 | 6.01 | 1% | 0% |
| SOLUSDT | breakout | 20.83 | 20.81 | 0% | 0% |
| XRPUSDT | trend | 20.83 | 5.98 | 2% | 0% |
| XRPUSDT | breakout | 20.83 | 20.81 | 0% | 0% |
| BNBUSDT | trend | 20.83 | 5.97 | 1% | 79% |
| BNBUSDT | breakout | 20.83 | 20.81 | 0% | 0% |
| DOTUSDT | trend | 20.83 | 6.03 | 2% | 0% |
| DOTUSDT | breakout | 20.83 | 20.81 | 0% | 0% |
| DOGEUSDT | trend | 20.83 | 6.01 | 1% | 0% |
| DOGEUSDT | breakout | 20.83 | 20.81 | 0% | 0% |
| ADAUSDT | trend | 20.83 | 6.01 | 2% | 0% |
| ADAUSDT | breakout | 20.83 | 20.81 | 0% | 0% |
| AVAXUSDT | trend | 20.83 | 5.99 | 2% | 100% |
| AVAXUSDT | breakout | 20.83 | 20.81 | 0% | 98% |
| AXSUSDT | trend | 20.83 | 6.01 | 2% | 65% |
| AXSUSDT | breakout | 20.83 | 20.81 | 0% | 0% |
| FTMUSDT | trend | 20.83 | 5.99 | 2% | 0% |
| FTMUSDT | breakout | 20.83 | 20.81 | 0% | 0% |
| LTCUSDT | trend | 20.83 | 5.99 | 100% | 0% |
| LTCUSDT | breakout | 20.83 | 20.81 | 9% | 0% |
| LINKUSDT | trend | 20.83 | 6.01 | 99% | 0% |
| LINKUSDT | breakout | 20.83 | 20.81 | 8% | 0% |

## Minimum practical capital

Required sleeve equity per asset/component is the larger of (min notional / 5th-percentile order fraction) and (lot value / (5th-percentile order fraction x granularity)); portfolio capital is 24 x the largest requirement because the frozen allocation is equal-weight and cannot be distorted to fit a budget.

| Granularity rule | Minimum capital (USDT, = EUR at 1.0) | Binding asset | Binding component | Binding constraint |
| --- | ---: | --- | --- | --- |
| lot <= 10% of order (rounding error <= 5%) | 31,511 | AVAXUSDT | trend | lot granularity |
| lot <= 25% of order (rounding error <= 12.5%) | 12,604 | AVAXUSDT | trend | lot granularity |

Verdict: the diversified 12-asset E040 portfolio is NOT implementable at EUR 500. Most trend-sleeve orders fall below the 5-20 USDT minimum notionals, and whole-lot quantity steps on several contracts (for example one whole coin per lot) make the fractional trend resizing unrepresentable at that size. MINIMUM PRACTICAL CAPITAL is given above for two rounding-tolerance rules; it is a scenario figure, not a promotion. Two contracts in the frozen universe are not tradeable today in their original form (MATICUSDT terminated 2024-09; FTMUSDT marked SETTLING in the snapshot), which is disclosed, not corrected, because Phase 4 evaluates the 2022-2024 frozen universe.

Supporting scenario table from the analysis run: reports\E045_20260909T140237\capital_scenarios.csv (its all-orders column is dominated by microscopic resize orders and is not a capital figure).
