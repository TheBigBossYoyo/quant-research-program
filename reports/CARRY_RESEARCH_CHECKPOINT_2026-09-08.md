# Carry checkpoint — 2026-09-08

**ETH continuous carry is RESEARCH-PROMISING only. No strategy is paper/live eligible.**

This follows INITIAL_RESEARCH_REPORT_2026-09-08.md. User subsequently confirmed Tunisia residence, all Binance products enabled, Trading212 Invest GBP with a UK account detail. These are user-reported facts; do not infer UK residence or independently verified entitlements.

## Development results, 2022–2024 only

| Candidate | Base indicative CAGR | Stressed CAGR | Base final equity from500USDT | Critical weakness | Verdict |
|---|---:|---:|---:|---|---|
| BTC monthly full reset | 1.67% | -0.52% | 525.42USDT | Costs erase return | REJECTED |
| ETH monthly full reset | 1.65% | -0.64% | 525.18USDT | Costs erase return | REJECTED |
| BTC continuous | 3.75% | 3.67% | 558.36USDT | Separate futures wallet fails20% extra rally | REJECTED for this architecture |
| ETH continuous | 2.65% | 2.59% | 540.81USDT | Exposure drift, exact fees/maintenance and price proxies unresolved | RESEARCH-PROMISING only |

Equal base quantities of long spot/short perpetual; no borrowing or collateral transfers. Current futures quantity steps applied to both legs. Monthly version reallocates from current equity without capital injections. Continuous version holds initial quantity. Gross starts at or below1x but can drift.500USDT is illustrative, not EUR500.

Base costs: spot12bps/futures7bps each execution (published10/5bps taker plus2bps assumed friction). Stress doubles totals. Charge all four actual entry/exit notionals. Funding uses provided settlement marks or explicitly approximate hourly mark opens; none credited at entry or after exit. [Official futures fees, retrieved2026-09-08](https://www.binance.com/en/fee/futureFee).

BTC minimum adverse futures-wallet/notional ratio2.89% shows how a smooth combined equity curve can hide liquidation. ETH ratio86.87% passes this specific20% extra-mark-jump scenario; this is not a verified maintenance calculation or estimated future probability. Maximum gross drift is1.064x ETH/1.942x BTC base. ETH violates the initial1x operational setting: a causal cap is required, not a waived limit.

ETH base calendar returns0.36%/2.10%/5.55%. E007 used10000 circular daily block resamples,7/30/60day blocks,seed20260908+symbol index and82-trial Bonferroni correction. ETH stressed lower annual arithmetic mean bounds1.48%/1.05%/0.81%. These are conditional development estimates, not OOS evidence. Observed hourly combined DD0.60% misses intrahour basis extremes. Cash benchmark0USDT excludes GBP interest, conversion and opportunity costs. A modest return does not justify venue/stablecoin/collateral risk without those comparisons.

## Integrity

96 spot plus144 futures/mark archives matched official SHA256. Funding:3288 events per asset. Mark archives lacked72BTC hours (2022-07-31,2022-10-02,2023-02-24) and48ETH hours (last two dates). Five public REST supplements restored all120 hours, preserving raw originals and source hashes. Futures/mark series now each26304 hourly rows.

Funding responses lack2005 settlement marks per asset. On1283 overlapping known marks, proxy absolute error median0bps,p99 roughly1bp,max2.40BTC/2.94ETH bps. This does not verify missing-period exact marks. Parsing/gap failures and superseded spot results are recorded, not hidden. No validation2025 analysis; final2026 remains undownloaded. No credentials, orders or paid services.

## Required next gate

Account-specific ETH spot taker, ETH USDⓈ-M maker/taker and applicable maintenance tier/cumulative deduction are pending (values only, no secrets). Public symbol metadata cannot establish signed USER_DATA facts. [Official account reference](https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/User-Commission-Rate). [Public funding/mark reference](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History).

After these facts arrive, preregister a causal exposure cap and independent collateral buffer/halts; test development only, compare cash/FX opportunity costs and executable quotes, then decide whether to open2025 validation. Final2026 stays locked until architecture freeze. This is not permission to trade or an automatic transition.

Outputs: E004_20260908T094758,E005_20260908T164103,E006_20260908T164403,E007_20260908T164535. Reproduce with `python -m unittest discover -s tests -v`, then research/carry_screen.py, research/carry_backtest.py, research/continuous_carry.py and research/carry_uncertainty.py. Scripts create timestamped outputs. Source snapshot, versions and hashes are preserved; no Git repository existed at baseline.
