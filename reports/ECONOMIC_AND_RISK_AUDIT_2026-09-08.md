# Economic and risk audit

**The ETH carry candidate remains rejected for promotion. Its economic case is weaker than its positive USDT return suggests.** This audit uses development data only and does not establish that the mechanism can never be useful.

## Opportunity cost and currency exposure

| Development measure, 2022–2024 | Base case | Doubled-cost case |
|---|---:|---:|
| ETH capped carry indicative CAGR in USDT | 2.11% | 2.07% |
| Lagged USD three-month yield accrual reference | 4.26% | 4.26% |
| Annualized relative wealth change versus reference | -2.06% | -2.10% |
| Conditional GBP-translated annual volatility | 9.29% | 9.29% |
| Conditional GBP-translated maximum daily drawdown | -17.72% | -17.72% |

The strategy underperformed the reference in each development calendar year. The ordinary 95% block-bootstrap interval for annualized arithmetic excess return was approximately -2.92% to -1.16% in the base case. A positive mean versus zero-interest USDT cash does not establish an attractive return on committed capital.

The reference accrues the preceding calendar day's available three-month Treasury yield on a calendar-day basis. It is **not** a realized bond total-return index, a guaranteed broker cash offer or evidence that this user can earn that exact return. It omits instrument expenses, spread, taxes and rollover price effects. Its purpose is to measure the economic hurdle, not recommend a security. Data source: Board of Governors of the Federal Reserve System, [DGS3MO via FRED](https://fred.stlouisfed.org/series/DGS3MO), retrieved 8 September 2026.

GBP figures divide NAV by USD per GBP from [DEXUSUK via FRED](https://fred.stlouisfed.org/series/DEXUSUK), also sourced from the Federal Reserve. This is a conditional currency translation assuming USDT=USD; it omits depeg/redemption and conversion costs. Latest-vintage daily reference observations and carried nonbusiness-day valuations are asynchronous with hourly crypto marks. They are not achievable conversion fills or point-in-time macro signals. GBP is relevant to the reported Trading 212 account currency, but the user's overall reporting currency has not been established.

The GBP-translated historical CAGR happens to be higher (4.71% base), partly because idle USD cash itself appreciated against GBP over these endpoints. That is currency exposure, not additional crypto alpha. Neither this endpoint benefit nor the 2.11% USDT return compensates automatically for exchange, stablecoin and collateral risks.

## Risk-control defect and correction

The former capped ledger could downgrade a mandatory flatten after an outage: a collateral halt scheduled a full close; the next observation could not execute; a recovered mark and high gross exposure then replaced the full close with a trim. A targeted synthetic test failed with a residual position of 1.537 units instead of zero.

The halt now remains latched until the position is closed. No automatic restart exists. All 28 tests pass. The corrected E008_20260908T170123 base/stress ledgers match the prior E008_20260908T165321 ledgers exactly because neither historical path triggered a halt. This proves the return figures were unchanged; it does not validate real outage execution or intrahour margin survival.

## Decision and next research

Do not advance this carry candidate simply by obtaining exact account fees. Its opportunity cost, currency risk, mark-price proxies and execution assumptions need a stronger economic justification. Account-specific fees and maintenance tiers remain UNVERIFIED; the user need not supply keys or repeatedly search for these values.

Independent research is not globally blocked by that account fact. The next useful branch is a bounded screen of directional perpetual signals using the already acquired hourly price/funding data and published lower futures transaction costs, with both sides accounted for explicitly. Register this separately; do not infer that losses in spot under higher fees establish failure of every perpetual strategy. Keep the 2025 validation gate closed until a candidate passes its preregistered development requirements. Final 2026 remains locked and undownloaded.

Results and source hashes: E009_20260908T170120/results.json and comparison CSVs. Raw FRED data and download metadata are preserved. No account access, orders or subscriptions occurred.
