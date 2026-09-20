# Initial research findings — 2026-09-08

**Verdict: no strategy currently passes. No paper/live eligibility.**

These are development-only results for 2022–2024, in USDT, using current standard spot commission plus assumed execution friction. No OOS performance is claimed. 2025 archives were acquired but were not loaded into analysis; 2026 final test was not acquired. No credentials or orders were used.

## Evidence and decision

- 70 registered signal-asset configurations; 20 simple benchmark configurations. Three cost scenarios each; all 270 results retained.
- Zero of 42 configurations at 5/15/60 minutes produced positive base-cost cumulative returns. This rejects these specific rules under these assumptions, not all short-horizon alpha.
- Two daily 48-bar momentum candidates passed the cheap stress screen. Both failed even unadjusted 95% uncertainty checks; multiple-testing correction strengthens rejection.
- Both also suffered approximately 45–47% development drawdowns at 1x exposure when invested. Leverage is not justified.
- Eight additional neighboring signal-asset configurations were examined only for falsification (78 total). No parameter replacement or retuning adopted.
- All 96 raw monthly archives (43,010,937 compressed bytes) match official SHA256. Development: 315,632 observed bars per asset; sixteen missing and fourteen zero-volume bars each. Signal completeness and executable bucket-open observations are separated.

## Serious candidate comparison

| Strategy | Market | Timeframe | Net CAGR | Sharpe | Sortino | Max DD | Trades | Costs | OOS | Robustness / verdict |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| momentum 48 | BTCUSDT | daily | 26.1% | 0.81 | 1.21 | -45.0% | 30 | 12 bps/side | Not opened | REJECTED for promotion |
| flow 1 | BTCUSDT | daily | 22.2% | 0.81 | 1.30 | -32.7% | 198 | 12 bps/side | Not opened | REJECTED for promotion |
| sma 20 | BTCUSDT | daily | 19.5% | 0.67 | 1.00 | -56.3% | 62 | 12 bps/side | Not opened | Benchmark only |
| buyhold 0 | BTCUSDT | daily | 25.1% | 0.68 | 1.01 | -66.7% | 1 | 12 bps/side | Not opened | Benchmark only |
| momentum 48 | ETHUSDT | daily | 17.2% | 0.58 | 0.85 | -46.6% | 25 | 12 bps/side | Not opened | REJECTED for promotion |
| flow 1 | ETHUSDT | daily | 10.6% | 0.45 | 0.70 | -40.9% | 230 | 12 bps/side | Not opened | REJECTED for promotion |
| sma 20 | ETHUSDT | daily | -6.5% | 0.09 | 0.13 | -49.9% | 55 | 12 bps/side | Not opened | Benchmark only |
| buyhold 0 | ETHUSDT | daily | -4.3% | 0.28 | 0.40 | -74.0% | 1 | 12 bps/side | Not opened | Benchmark only |

## Uncertainty and adversarial risk

- BTCUSDT: 14-day block-bootstrap Sharpe 95% interval [-0.40, 2.00], annualized arithmetic alpha versus buyhold [-19.9%, 44.9%]. Both include zero. These are descriptive development intervals, not held-out estimates.
- ETHUSDT: 14-day block-bootstrap Sharpe 95% interval [-0.47, 1.65], annualized arithmetic alpha versus buyhold [-20.0%, 54.8%]. Both include zero. These are descriptive development intervals, not held-out estimates.
- BTCUSDT: in 4,000 resampled 365-day paths at 1x, maximum drawdown exceeded 30% in 38.8% and 50% in 3.7%. Conditional resampling is not a calibrated future probability. Alpha intervals also include zero with 7/30/60-day blocks.
- ETHUSDT: in 4,000 resampled 365-day paths at 1x, maximum drawdown exceeded 30% in 63.2% and 50% in 9.8%. Conditional resampling is not a calibrated future probability. Alpha intervals also include zero with 7/30/60-day blocks.

BTC neighboring lookbacks all remain positive at stressed costs but retain roughly 46–54% maximum drawdowns. ETH is more parameter-sensitive. A broad positive region does not remove uncertainty, beta exposure or unacceptable tail risk. No need to consume validation to rescue these failed evidence gates.

## Capital and implementation limits

The symbol snapshots give a 5-USDT minimum notional for both assets, quantity steps 0.00001 BTC and 0.0001 ETH, and a 0.01-USDT price tick. These are current snapshots, not historical filter histories. EUR500 is not assumed equal to 500 USDT. No EUR conversion return series or account entitlements were available. Minimum efficient capital is **not established**.

- BTCUSDT: 0.1% of the historical first-percentile five-minute quote volume is 547.26 USDT. This is a conservative volume-based order bound, not an executable depth estimate.
- ETHUSDT: 0.1% of the historical first-percentile five-minute quote volume is 230.16 USDT. This is a conservative volume-based order bound, not an executable depth estimate.

A 500-USDT hypothetical order passes that volume bound for BTC but not ETH; split/smaller orders or narrower liquidity conditions would be needed under the proposed rule. Actual order size is not modeled in the first screen. Zero-volume intervals cannot execute. Fees: 10 bps optimistic (fee-only floor), 12 bps base (10+2 assumed friction), 24 bps stress (20+4). No maker fill, BNB discount, borrow, funding or leverage assumption.

Rounding, minimum notionals, fee-asset dust, historical spreads/depth, partial fills, disconnect handling, EUR conversion and independent circuit breakers are not implemented in this Phase-I screen. Costs/slippage are scenarios, not venue-calibrated fills; no execution or capital-readiness claim is permitted. Actual risk allocation remains zero.

## Research integrity and next decision

The earlier E001_20260908T093818 and E002_20260908T093848 runs are superseded because an incomplete aggregate bar could erase a valid earlier fill. The original artifacts remain on disk; a targeted regression test and corrected rerun replace their evidentiary role. Fourteen tests pass.

Do not expand random indicators or unlock holdout after this failure. Highest-value next branch is to establish actual account jurisdiction, Binance product entitlements and Trading 212 account/currency, then preregister a feasible alternative (long-only same-currency equities/ETFs with corporate-action-safe data, or properly funded carry if derivatives are permitted). Current records do not establish those user-specific facts. Longer-history crypto trend research is possible, but is not a reason to promote this weak three-year result.

See VENUE_CONSTRAINTS_2026-09-08.md for official source URLs, retrieval date, account-specific unknowns and measured-versus-assumed distinctions. No paid subscriptions or live trading.

## Complete base-cost screen (including failures)

| Market | Minutes | Rule | Lookback | Net CAGR | Sharpe | Max DD | Trades | Decision |
|---|---:|---|---:|---:|---:|---:|---:|---|
| BTCUSDT | 5 | momentum | 3 | -100.0% | -86.15 | -100.0% | 44027 | REJECTED for promotion |
| BTCUSDT | 5 | momentum | 12 | -100.0% | -42.82 | -100.0% | 22644 | REJECTED for promotion |
| BTCUSDT | 5 | momentum | 48 | -100.0% | -20.11 | -100.0% | 12116 | REJECTED for promotion |
| BTCUSDT | 5 | reversal | 3 | -100.0% | -93.46 | -100.0% | 44031 | REJECTED for promotion |
| BTCUSDT | 5 | reversal | 12 | -100.0% | -48.45 | -100.0% | 22647 | REJECTED for promotion |
| BTCUSDT | 5 | reversal | 48 | -100.0% | -25.26 | -100.0% | 12118 | REJECTED for promotion |
| BTCUSDT | 5 | flow | 1 | -100.0% | -133.69 | -100.0% | 72778 | REJECTED for promotion |
| BTCUSDT | 5 | sma | 20 | -100.0% | -37.59 | -100.0% | 20482 | Benchmark |
| BTCUSDT | 5 | buyhold | 0 | 26.3% | 0.70 | -67.6% | 1 | Benchmark |
| BTCUSDT | 15 | momentum | 3 | -100.0% | -32.76 | -100.0% | 15070 | REJECTED for promotion |
| BTCUSDT | 15 | momentum | 12 | -99.8% | -14.51 | -100.0% | 7921 | REJECTED for promotion |
| BTCUSDT | 15 | momentum | 48 | -95.6% | -6.74 | -100.0% | 4146 | REJECTED for promotion |
| BTCUSDT | 15 | reversal | 3 | -100.0% | -31.22 | -100.0% | 15073 | REJECTED for promotion |
| BTCUSDT | 15 | reversal | 12 | -99.8% | -17.11 | -100.0% | 7920 | REJECTED for promotion |
| BTCUSDT | 15 | reversal | 48 | -96.2% | -8.76 | -100.0% | 4144 | REJECTED for promotion |
| BTCUSDT | 15 | flow | 1 | -100.0% | -51.36 | -100.0% | 23910 | REJECTED for promotion |
| BTCUSDT | 15 | sma | 20 | -99.7% | -13.08 | -100.0% | 7000 | Benchmark |
| BTCUSDT | 15 | buyhold | 0 | 26.2% | 0.70 | -67.5% | 1 | Benchmark |
| BTCUSDT | 60 | momentum | 3 | -95.2% | -7.67 | -100.0% | 3919 | REJECTED for promotion |
| BTCUSDT | 60 | momentum | 12 | -75.9% | -3.28 | -98.6% | 1989 | REJECTED for promotion |
| BTCUSDT | 60 | momentum | 48 | -40.6% | -1.13 | -84.3% | 946 | REJECTED for promotion |
| BTCUSDT | 60 | reversal | 3 | -95.0% | -8.11 | -100.0% | 3919 | REJECTED for promotion |
| BTCUSDT | 60 | reversal | 12 | -78.2% | -3.97 | -99.1% | 1991 | REJECTED for promotion |
| BTCUSDT | 60 | reversal | 48 | -53.3% | -1.80 | -90.6% | 947 | REJECTED for promotion |
| BTCUSDT | 60 | flow | 1 | -99.3% | -13.51 | -100.0% | 5901 | REJECTED for promotion |
| BTCUSDT | 60 | sma | 20 | -67.3% | -2.52 | -96.5% | 1666 | Benchmark |
| BTCUSDT | 60 | buyhold | 0 | 25.9% | 0.69 | -67.4% | 1 | Benchmark |
| BTCUSDT | 240 | momentum | 3 | -37.9% | -1.03 | -81.3% | 964 | REJECTED for promotion |
| BTCUSDT | 240 | momentum | 12 | -13.6% | -0.20 | -69.0% | 486 | REJECTED for promotion |
| BTCUSDT | 240 | momentum | 48 | 3.6% | 0.28 | -66.2% | 198 | REJECTED for promotion |
| BTCUSDT | 240 | reversal | 3 | -56.5% | -2.07 | -92.1% | 964 | REJECTED for promotion |
| BTCUSDT | 240 | reversal | 12 | -33.2% | -0.86 | -73.3% | 487 | REJECTED for promotion |
| BTCUSDT | 240 | reversal | 48 | -8.5% | -0.02 | -57.2% | 198 | REJECTED for promotion |
| BTCUSDT | 240 | flow | 1 | -70.0% | -3.41 | -97.3% | 1431 | REJECTED for promotion |
| BTCUSDT | 240 | sma | 20 | 8.2% | 0.39 | -47.2% | 385 | Benchmark |
| BTCUSDT | 240 | buyhold | 0 | 25.8% | 0.69 | -67.2% | 1 | Benchmark |
| BTCUSDT | 1440 | momentum | 3 | 11.0% | 0.47 | -50.2% | 166 | REJECTED for promotion |
| BTCUSDT | 1440 | momentum | 12 | 16.8% | 0.59 | -50.8% | 78 | REJECTED for promotion |
| BTCUSDT | 1440 | momentum | 48 | 26.1% | 0.81 | -45.0% | 30 | REJECTED for promotion |
| BTCUSDT | 1440 | reversal | 3 | -12.1% | -0.12 | -57.5% | 167 | REJECTED for promotion |
| BTCUSDT | 1440 | reversal | 12 | -2.9% | 0.11 | -49.8% | 78 | REJECTED for promotion |
| BTCUSDT | 1440 | reversal | 48 | 0.8% | 0.20 | -55.0% | 30 | REJECTED for promotion |
| BTCUSDT | 1440 | flow | 1 | 22.2% | 0.81 | -32.7% | 198 | REJECTED for promotion |
| BTCUSDT | 1440 | sma | 20 | 19.5% | 0.67 | -56.3% | 62 | Benchmark |
| BTCUSDT | 1440 | buyhold | 0 | 25.1% | 0.68 | -66.7% | 1 | Benchmark |
| ETHUSDT | 5 | momentum | 3 | -100.0% | -74.54 | -100.0% | 43971 | REJECTED for promotion |
| ETHUSDT | 5 | momentum | 12 | -100.0% | -34.97 | -100.0% | 22507 | REJECTED for promotion |
| ETHUSDT | 5 | momentum | 48 | -100.0% | -16.76 | -100.0% | 11641 | REJECTED for promotion |
| ETHUSDT | 5 | reversal | 3 | -100.0% | -75.67 | -100.0% | 43973 | REJECTED for promotion |
| ETHUSDT | 5 | reversal | 12 | -100.0% | -39.73 | -100.0% | 22513 | REJECTED for promotion |
| ETHUSDT | 5 | reversal | 48 | -100.0% | -21.10 | -100.0% | 11643 | REJECTED for promotion |
| ETHUSDT | 5 | flow | 1 | -100.0% | -116.21 | -100.0% | 71527 | REJECTED for promotion |
| ETHUSDT | 5 | sma | 20 | -100.0% | -31.59 | -100.0% | 20409 | Benchmark |
| ETHUSDT | 5 | buyhold | 0 | -3.4% | 0.29 | -77.1% | 1 | Benchmark |
| ETHUSDT | 15 | momentum | 3 | -100.0% | -26.35 | -100.0% | 15078 | REJECTED for promotion |
| ETHUSDT | 15 | momentum | 12 | -99.8% | -12.19 | -100.0% | 7824 | REJECTED for promotion |
| ETHUSDT | 15 | momentum | 48 | -94.1% | -5.23 | -100.0% | 3810 | REJECTED for promotion |
| ETHUSDT | 15 | reversal | 3 | -100.0% | -25.61 | -100.0% | 15088 | REJECTED for promotion |
| ETHUSDT | 15 | reversal | 12 | -99.8% | -13.57 | -100.0% | 7826 | REJECTED for promotion |
| ETHUSDT | 15 | reversal | 48 | -96.3% | -7.05 | -100.0% | 3809 | REJECTED for promotion |
| ETHUSDT | 15 | flow | 1 | -100.0% | -39.72 | -100.0% | 23475 | REJECTED for promotion |
| ETHUSDT | 15 | sma | 20 | -99.7% | -11.64 | -100.0% | 6945 | Benchmark |
| ETHUSDT | 15 | buyhold | 0 | -3.4% | 0.29 | -76.8% | 1 | Benchmark |
| ETHUSDT | 60 | momentum | 3 | -96.1% | -6.76 | -100.0% | 3892 | REJECTED for promotion |
| ETHUSDT | 60 | momentum | 12 | -73.9% | -2.50 | -98.2% | 1887 | REJECTED for promotion |
| ETHUSDT | 60 | momentum | 48 | -38.4% | -0.85 | -80.7% | 934 | REJECTED for promotion |
| ETHUSDT | 60 | reversal | 3 | -95.0% | -6.35 | -100.0% | 3893 | REJECTED for promotion |
| ETHUSDT | 60 | reversal | 12 | -81.9% | -3.49 | -99.5% | 1892 | REJECTED for promotion |
| ETHUSDT | 60 | reversal | 48 | -64.9% | -1.82 | -96.3% | 934 | REJECTED for promotion |
| ETHUSDT | 60 | flow | 1 | -99.3% | -10.27 | -100.0% | 5924 | REJECTED for promotion |
| ETHUSDT | 60 | sma | 20 | -57.2% | -1.54 | -92.2% | 1596 | Benchmark |
| ETHUSDT | 60 | buyhold | 0 | -3.6% | 0.29 | -76.7% | 1 | Benchmark |
| ETHUSDT | 240 | momentum | 3 | -39.7% | -0.86 | -84.3% | 933 | REJECTED for promotion |
| ETHUSDT | 240 | momentum | 12 | -19.1% | -0.28 | -65.3% | 471 | REJECTED for promotion |
| ETHUSDT | 240 | momentum | 48 | -11.1% | -0.06 | -58.3% | 189 | REJECTED for promotion |
| ETHUSDT | 240 | reversal | 3 | -63.9% | -1.91 | -95.6% | 933 | REJECTED for promotion |
| ETHUSDT | 240 | reversal | 12 | -44.3% | -0.89 | -84.5% | 470 | REJECTED for promotion |
| ETHUSDT | 240 | reversal | 48 | -16.0% | -0.08 | -74.1% | 187 | REJECTED for promotion |
| ETHUSDT | 240 | flow | 1 | -69.4% | -2.20 | -97.2% | 1503 | REJECTED for promotion |
| ETHUSDT | 240 | sma | 20 | 3.0% | 0.28 | -51.4% | 385 | Benchmark |
| ETHUSDT | 240 | buyhold | 0 | -3.4% | 0.29 | -76.2% | 1 | Benchmark |
| ETHUSDT | 1440 | momentum | 3 | -12.2% | -0.04 | -58.1% | 154 | REJECTED for promotion |
| ETHUSDT | 1440 | momentum | 12 | -0.8% | 0.22 | -47.1% | 73 | REJECTED for promotion |
| ETHUSDT | 1440 | momentum | 48 | 17.2% | 0.58 | -46.6% | 25 | REJECTED for promotion |
| ETHUSDT | 1440 | reversal | 3 | -13.3% | -0.05 | -64.7% | 153 | REJECTED for promotion |
| ETHUSDT | 1440 | reversal | 12 | -11.8% | -0.03 | -63.8% | 73 | REJECTED for promotion |
| ETHUSDT | 1440 | reversal | 48 | -13.3% | -0.07 | -68.3% | 24 | REJECTED for promotion |
| ETHUSDT | 1440 | flow | 1 | 10.6% | 0.45 | -40.9% | 230 | REJECTED for promotion |
| ETHUSDT | 1440 | sma | 20 | -6.5% | 0.09 | -49.9% | 55 | Benchmark |
| ETHUSDT | 1440 | buyhold | 0 | -4.3% | 0.28 | -74.0% | 1 | Benchmark |

Full metrics, cost scenarios, calendar returns, integrity/provenance, parameters, seeds and code fingerprints:

- E001_20260908T094021/results.json and metrics.csv
- E002_20260908T094107/results.json
- E003_20260908T094233/results.json and parameter_surface.csv
