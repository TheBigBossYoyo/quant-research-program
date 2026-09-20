# PHASE3_CONCLUSION — broad systematic alpha discovery — 9 September 2026

## Verdict

**No strategy reaches VALIDATION-CANDIDATE.** Phase 3 executed ten preregistered experiments (E032–E041) across the trend, breakout, pullback, multi-timeframe, regime-conditioned mean-reversion, relative-strength, volatility-compression, indicator-ablation, ensemble and regularized-stacking families on BTC/ETH spot (2017–2024) and perpetuals (2020–2024) at 1h/4h/1D, with a hierarchical multiplicity framework (economic hypotheses counted, architectures FDR-controlled and deflated, parameters judged by plateaus, CSCV overfitting probability and expanding-window walk-forward). Cumulative economic hypotheses: 384 (Phase 1–2: 367). The 2025 validation set was never analysed and the 2026 holdout never downloaded.

The phase did find real structure that earlier phases could not see: slow-trend regimes on BTC/ETH perpetuals have positive alpha over buy-and-hold with low beta, and compression breakouts at 4h are drawdown-efficient; their combination has development Sharpe 1.1–1.3 with correlation 0.15–0.33. It is classified WEAK_SIGNAL because the components do not survive the deflation appropriate to the search that produced them, the sample is five bull-biased years, and no combination met all preregistered gates. That classification is the honest one; it is recorded with a red-team report and it is not a validation candidate.

## Coverage matrix (mandate §59 B)

| Family | Architectures executed | Markets / TF | Best stressed result | Multiplicity / OOS | Classification |
|---|---|---|---|---|---|
| Trend (A: price/MA, dual MA, slope, distance) | 4 architectures, 21 parameter cells × 12 market cells (E032); unselected ensemble (E035) | BTC/ETH spot+perp, 1h/4h/1D | Sharpe 1.45 (selected), 1.06–1.15 (unselected); alpha over B&H +32–86%/yr in selected cells | DSR 0.03–0.23 (N=120); ensemble DSR ≤ 0.55; WF eff 0.24–0.72 | WEAK_SIGNAL |
| Supertrend (B) | flip, +HTF regime | same | ≤ 1.24, never above MA cells | — | REJECTED (no incremental value) |
| Breakout (C) | channel, ATR trail, HTF, vol-targeted | same | ≤ 1.08, dominated by MA | — | WEAK_SIGNAL (dominated) |
| Volatility compression (D) + volume (K) | compression breakout ± volume | 4h/1D | perp 4h Sharpe 1.10, DD −24%, control 0.25 | DSR 0.71; WF 0.57; PBO 0.13 | WEAK_SIGNAL (perp 4h) |
| Mean reversion (E) + regime (P) | z-score unconditional / range-gated / low-vol-gated | 1h/4h | E1 median −1.2; gated best 0.76 with 12 trades | — | REJECTED |
| RSI (F), pullback (M), multi-timeframe (N) | EMA/RSI/Bollinger pullback, RSI slope, 4h/1h/15m stack | 1h/4h/15m | Sharpe ≈ 0 to −1.7 | — | REJECTED |
| MACD (G), ADX (H), VWAP (J), candle (L) | partial-IC and filter ablations on the trend regime | 4h/1D | no partial IC (G/H/J); body/CLV one-bar reversal IC −0.045 (≈3 bps at 4h) | — | REJECTED / WEAK_SIGNAL (L, sub-cost) |
| ATR (I) | stops, trailing exits, vol sizing inside A/C/D/E | — | used as risk devices; no standalone claim | — | n/a |
| Relative strength (O) | L/S and long-only ± absolute overlay, liquid top-30 | perp universe weekly | L/S ≤ 0.32; long-only 0.66 with −80% DD | placebo 0.06–0.24 | REJECTED |
| Ensembles (Q) | equal-weight, inverse-vol of the two weak components | perp 4h | Sharpe 1.27/1.14, alpha excludes zero, corr 0.15–0.33, DD −19% to −36% | fails one gate per weighting | WEAK_SIGNAL |
| Regularized stacking (R) | ridge and ridge-logistic, yearly expanding refit, 18 features | perp 4h, OOS 2022–24 | OOS Sharpe −1.2 to −3.2 vs baseline 1.0 (1,800–3,300 trades) | — | REJECTED |
| Carry (S), microstructure (U), session effects (T), ETF trend/momentum (V) | tested in Phases 1–2 (E004–E031, E020) | — | see prior conclusions | — | closed |

Equity/ETF architectures beyond E020 (monthly trend and momentum on 12 GBP UCITS ETFs, 2009–2019, all below equal weight) were not extended in Phase 3: a market-neutral equity architecture would be RESEARCH-ONLY UNDER CURRENT BROKER CONSTRAINTS and free checksum-grade equity data of sufficient breadth is not available; this remains the largest untested area and is listed as a reopening condition rather than declared exhausted.

## What was learned

- Crypto at 4h–1D carries a genuine slow-trend premium relative to buy-and-hold (low beta, positive intercepts, 2022 handled), but the size that survives an honest deflation is a Sharpe near one with 30–45% drawdowns at 1x — a beta-like risk profile, not a standalone edge for €500.
- Breakouts from compression are the only breakout variant with a drawdown advantage; volume confirmation helps but starves the rule of trades.
- Everything mean-reverting on BTC/ETH loses at 1h–4h unless gated so tightly that it stops trading; the candle-structure reversal is real and worth three basis points.
- Indicators are redundant transformations of the trend state: MACD, ADX, VWAP distance and Supertrend add nothing to a slow moving-average regime.
- Machine-learning stacking over these features destroys value through turnover; the simple two-component combination is the better model.

## Reopening conditions

1. Freeze the E040 combination as written (rule hashes in E035/E038/E040 results) and evaluate it on the locked 2025 set only if a further development regime becomes available first (for example an additional liquid asset set at 4h with the rule frozen beforehand), so that a validation pass would not be a single five-year sample's luck.
2. Equity/ETF cross-sectional and market-neutral architectures with checksum-grade, corporate-action-safe data (paid data within the EUR 50/month budget would need a written justification).
3. Phase 1–2 conditions (fee structure, queue data, option history).

Integrity: 103 tests pass; every experiment directory carries results.json with code hash, cost cases and full configuration tables; superseded runs (E035 first run) are retained and labelled.
