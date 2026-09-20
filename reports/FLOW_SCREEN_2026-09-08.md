# Aggressive-flow screen on perpetuals — development only

**No candidate qualifies.** Taker-flow imbalance on BTCUSDT/ETHUSDT perpetuals carries a small, statistically robust reversal signal at the one-hour horizon, but its economic size is an order of magnitude below taker transaction costs. E012 is REJECTED for tradability. Cumulative hypotheses tested: 159.

## What was tested

E012 was preregistered before any flow result: three features (one-bar imbalance, six-bar imbalance, spot-minus-perpetual imbalance), three timeframes (1h/4h/24h), two symbols, giving 18 information-coefficient cells and 36 directional hypotheses. Stage 1 was a block-bootstrap Spearman IC gate at Bonferroni level 0.05/18 against the open-to-open return two bars after the signal bar. Stage 2 ran the unchanged E010 signed ledger (50% gross, signed funding, 5/7/14 bps per executed notional, latched halt) only for Stage-1 survivors, with a sign-following rule and a trailing-quantile band rule. Seven new tests cover the imbalance formula, prefix invariance, forward-return alignment, the causal quantile rule, complete-bucket invalidation and bootstrap reproducibility; 40 tests pass.

## Stage 1: the effect exists but is tiny

| Cell | IC | Adjusted interval | Every year negative | Decay at 4 / 24 bars |
|---|---:|---:|:---:|---:|
| BTC 1h imb1 | -0.024 | -0.041 to -0.004 | yes | -0.015 / -0.005 |
| BTC 1h imb6 | -0.023 | -0.037 to -0.010 | yes | -0.025 / -0.011 |
| ETH 1h imb1 | -0.021 | -0.038 to -0.004 | yes | -0.017 / -0.005 |
| ETH 1h imb6 | -0.031 | -0.045 to -0.016 | yes | -0.023 / -0.006 |

No 4-hour, daily or cross-venue cell passed. The same-bar correlation between imbalance and the bar return is about 0.71, so aggressive flow moves price inside the bar; what remains predictable afterwards is small. Extreme-quintile forward means differ by roughly one basis point with a standard error near eleven basis points. The rank effect is detectable because the sample is large, not because the dollar edge is meaningful.

## Stage 2: costs dominate

| Rule (stress, 14 bps) | BTC CAGR | ETH CAGR | Fills | Drawdown |
|---|---:|---:|---:|---:|
| imb1 sign-following | -41.5% | -56.9% | 1639 / 1589 | -80% / -92% |
| imb6 sign-following | -41.5% | -57.1% | 1172 / 1563 | -80% / -92% |
| imb1 quantile band | -41.5% | -56.9% | 2144 / 3430 | -80% / -92% |
| imb6 quantile band | -41.1% | -57.1% | 2514 / 3515 | -80% / -92% |

Fee-only cases (5 bps) lost at the same rate. Hourly long baselines were +10.4% BTC and -4.6% ETH under stress. Fill counts fall with higher costs only because equity collapses below the minimum notional.

## Interpretation and limits

The reversal after aggressive flow is consistent with the compensation passive liquidity providers earn for absorbing that flow. A retail account executing with taker orders pays that premium rather than collecting it. Even a hypothetical maker round trip of four basis points exceeds the measurable edge, and no fill-probability or queue-position claim can be made from OHLCV taker aggregates. This result should not be rescued by retuning windows, thresholds or costs.

Development data only (2022–2024). Validation 2025 remains unanalyzed; the 2026 final holdout remains undownloaded. Outputs: reports/E012_20260908T180321 (results.json, ic.csv, metrics.csv).

## Next

E013 is preregistered: funding/basis positioning state on perpetuals at 8-hour and daily frequency, using data already on disk.
