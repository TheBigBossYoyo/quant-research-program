# Cross-sectional perpetual universe screen — development only

**Update after E016/E015/E017: still no candidate.** On the five-year 2020–2024 sample the 7-day relative taker-flow continuation passed the IC gate and the cheap ledger gates (stressed CAGR 34.6%, Sharpe 1.31, drawdown -25.7%) but was rejected for promotion by the 207-trial bound and then failed the hostile audit: post-2020 excess return not distinguishable from zero, the top ten names exceed all price P&L, the short leg loses 21% a year, and the liquid half of the universe lost money in the 2020 year that drives the headline. A within-week placebo (0 of 200) shows the rank carries real information; the economics do not survive. Slower 14/28-day variants were counted and also fail. Details: EXPERIMENTS.md (E015–E017) and reports/E016_20260908T192328, E015_20260908T192617, E017_20260908T193309.

**E014 (2022–2024): no candidate.** E014 tested four preregistered cross-sectional features on a survivorship-aware universe of 393 USDT-margined perpetuals and none passed the Bonferroni-adjusted information-coefficient gate. The failure is one of statistical power at 147 weekly observations, not of unstable signs, so the same cells are being rerun on a five-year development sample (E016) and counted again. Cumulative hypotheses after E014: 199.

## Universe and data (ENV002)

Daily klines and funding-rate archives were downloaded from the public Binance archive for every USDT-quoted UM perpetual with at least one development month, 2022–2024 only: 7,793 kline files and 7,791 funding files, all SHA256-verified against the archive checksums, 233,049 symbol-days and 823,925 funding events (30% at four-hour intervals, a handful at two hours). Delisted contracts are retained by the archive, so membership comes from file existence: 23 symbols delisted inside the window are included until their last bar and exited at their last observed open. The 2026 holdout was never downloaded; 2025 was not downloaded at this stage.

Seven daily rows on 19–20 September 2023 and 30 November 2023 report taker-buy volume above total volume by 6–70%. The loader quarantines the taker field on those rows, keeps their prices and volume, reports them in the integrity output, and a regression test covers the behaviour.

Eligibility at signal day t uses only bars up to t: at least 60 observed daily bars, a bar on day t, trailing 30-day median quote volume of at least 20 million USDT. About 104 names were eligible per week.

## Stage 1: weekly cross-sectional information coefficients

Signal at the close of day t, execution at the open of day t+2, forward return to the open of day t+9. Critical |t| = 2.50 (two-sided, 0.05/4).

| Feature | Mean IC | t | 2022 / 2023 / 2024 | IC at 1 / 2 / 4 weeks |
|---|---:|---:|---|---|
| 7-day return | -0.020 | -1.37 | +0.006 / -0.045 / -0.016 | -0.020 / -0.023 / -0.007 |
| 30-day return | -0.031 | -2.22 | -0.033 / -0.050 / -0.012 | -0.031 / -0.030 / -0.029 |
| 7-day funding | -0.016 | -1.36 | +0.019 / -0.020 / -0.042 | -0.016 / -0.023 / -0.027 |
| 7-day taker imbalance | +0.025 | +1.94 | +0.029 / +0.003 / +0.043 | +0.025 / +0.029 / +0.051 |

Thirty-day cross-sectional reversal and seven-day relative-flow continuation carry the same sign in all three years; funding dispersion does not. No hypothesis ledger was run because no cell passed.

## Baselines at 14 bps per executed notional

| Baseline | CAGR | Sharpe | Max daily drawdown | Annual turnover |
|---|---:|---:|---:|---:|
| Equal-weight long, eligible universe, weekly | -18.4% | 0.13 | -77.7% | 9.9x |
| BTC long | +20.1% | 0.61 | -67.6% | 0.5x |

## Interpretation and limits

Effects of this size need roughly 300 weekly observations to clear the gate. The preregistered response is to extend the development sample backward to 2020 for the same cells (E016), which adds the 2020 crash and the 2021 bull market and its reversal; parameters, thresholds, cadence and costs are unchanged, and the rerun is counted as eight further hypotheses. Lowering the liquidity floor or rebalancing daily would also raise the observation count but were not preregistered and would be retunes.

The screen is indicative: alt-perpetual friction is uncalibrated (7/14/28 bps cases), funding notional uses a close-of-day proxy, delisting exits assume the last observed open, and there is no depth or queue model. Development data only. Outputs: reports/E014_20260908T190826 (results.json, metrics.csv, sources.json).
