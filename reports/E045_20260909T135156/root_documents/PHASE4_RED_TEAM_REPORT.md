# Phase4 red-team report

Verdict: CROSS_ASSET_WEAK_SIGNAL. Decision: DO_NOT_OPEN_2025.

- Same2022-2024 crypto regime across all assets;12 names are not12 independent time histories.
- Historical2021 liquidity cohort avoids current-survivor selection, but archive coverage is not guaranteed exhaustive. The universe was previously used for other signal research.
- The primary window is three years;2021 is excluded from performance and cannot explain the primary result. No new regime is manufactured.
- Funding is now complete where audited but settlement marks remain hourly-open proxies; missing marks use disclosed trade-open proxies. Adverse funding stress is reported.
- Open prices are execution proxies. Current spreads, lot rounding, minimum notionals and liquidation tiers are not fully verified; EUR500 feasibility is not established.
- Targets preserve the original sizing; drift above1x can occur, so this is not hard-capped unlevered exposure.
- Strategy-return sleeve combinations require external capital transfers; estimated costs are deducted for portfolio diagnostics.
- BTC/ETH are shown solely as discovery comparators and never enter replication sign statistics.

## Direct attacks

Shared beta/bull bias: factor regressions and2022 bear results saved.
One2021 event: absent from primary performance by design.
One trade/year: concentration and removal diagnostics saved; no exclusions adopted.
Asset-selection bias: universe hashed before E044, all12 retained including MATIC after notice-based exit.
Funding omission: archive rates, jitter, mark substitutions and adverse stress saved per asset.
Data contamination: exact original reproduction; approved accounting fix; frozen source/config/universe checked before execution; all acquisition bounds end2024.

## Frozen gate results

| gate | passed |
|---|---|
| asset_count | True |
| positive_fraction | True |
| positive_alpha_fraction | True |
| median_sharpe | True |
| median_alpha | True |
| common_block_lower_alpha | False |
| portfolio_drawdown | True |
| top5_trade_concentration | True |
| top_year_concentration | True |
| conservative_stress | True |
| remove_best_year | True |
| no_unresolved_accounting_or_data_defects | True |


## Component evidence

| component | median_sharpe | positive_fraction | median_alpha |
|---|---|---|---|
| breakout | 0.18281 | 0.58333 | 0.12718 |
| trend | 0.65235 | 0.58333 | 1.3731 |


No signal changed after outcomes.
