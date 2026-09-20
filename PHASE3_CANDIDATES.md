# PHASE3_CANDIDATES — classification ledger (updated 2026-09-09)

Classification vocabulary: REJECTED / WEAK_SIGNAL / PORTFOLIO_COMPONENT_CANDIDATE / RESEARCH-PROMISING / VALIDATION-CANDIDATE / PAPER-TRADING ELIGIBLE. Protected data: 2025 validation unopened; 2026 holdout never downloaded.

| ID | Family / architecture | Market, TF | Development evidence (stressed costs) | Multiplicity / OOS | Classification |
|---|---|---|---|---|---|
| E032 A1/A3 (selected best cells) | Slow-trend regime: price vs 150–250 SMA; MA slope | perp BTC/ETH 4h–1D; spot BTC/ETH 4h | Sharpe 1.2–1.5, DD −42% to −55% vs B&H −77% to −94%; alpha over B&H +32% to +86%/yr with intervals excluding zero, beta 0.1–0.3; plateaus; PBO 0–0.14; crash years handled (2022: −5% to +156% vs −65%) | Textbook DSR 0.03–0.23 at N=120; walk-forward efficiency 0.24–0.72 (A1 cells OOS Sharpe 0.9–1.1 over 4–7 held-out years) | WEAK_SIGNAL (selection-inflated; see E035) |
| E035 plateau ensemble | Unselected mean of seven slow-trend signs | perp/spot BTC/ETH 4h, 1D | Sharpe 0.68–1.15; alpha excludes zero in 2/8 cells; below vol-managed B&H in 6/8 | DSR 0.13–0.55 at N=11 | WEAK_SIGNAL — documented low-beta trend component |
| E032 B1/B3 | Supertrend flip / with daily regime | same | Sharpe ≤ 1.24; never above the MA cells on the same bars | — | REJECTED (no incremental value over MA regime) |
| E032 C1/C2/C4/C6 | Donchian breakout variants | same | Sharpe ≤ 1.08, dominated by MA family | — | WEAK_SIGNAL (dominated) |
| E033 M1/M2/M3 | Pullback-with-trend (EMA distance, RSI, Bollinger) | perp/spot 1h, 4h | 4–21 trades, Sharpe ≈ 0 | — | REJECTED |
| E033 F3 | RSI-slope persistence in regime | same | median Sharpe −1.4; one cost-heavy cell at 0.76 | DSR 0.27 | REJECTED |
| E033 N2 | 4h Supertrend + 1h pullback + 15m breakout | spot 15m 2022–24 | Sharpe −1.7 | — | REJECTED |
| E036 O1–O4 | Liquid relative strength ± absolute overlay | perp universe top-30, weekly | L/S Sharpe ≤ 0.32 (p ≥ 0.22); long-only overlay best Sharpe 0.66 with −80% DD on 3–5 names | placebo 0.06–0.24; DSR ≤ 0.66 | REJECTED |
| E037 E1/E2/E3 | z-score mean reversion, unconditional / range-gated / low-vol-gated | BTC/ETH perp+spot 1h, 4h | E1 median Sharpe −1.2; E2 gate improves by +0.6 to +1.5 but best cells trade 3–12 times (CAGR ≤ 3.6%) | — | REJECTED |
| E038 D1/D2 | Compression (ATR pct < 20%) breakout ± volume | BTC/ETH perp+spot 4h, 1D | perp 4h D1: Sharpe 1.10, CAGR 27%, DD −24%, 92 trades, control 0.25; D2 raises medians in 6/8 cells | PBO 0.13; WF 0.57; DSR 0.71 | WEAK_SIGNAL (perp 4h) |
| E039 G/H/J/L | MACD, ADX, VWAP distance, candle structure as incremental information | BTC/ETH perp+spot 4h, 1D | no partial IC for MACD/ADX/VWAP; candle body/CLV one-bar reversal IC −0.045 (≈3 bps at 4h); all filters degrade the regime | — | MACD/ADX/VWAP/wicks REJECTED; body/CLV WEAK_SIGNAL |
| E040 | Equal-weight / inverse-vol of E035 trend + E038 breakout | perp BTC/ETH 4h | Sharpe 1.27/1.14 (EW), DD −27%/−36%; inverse-vol 1.18/1.03, DD −19%/−27%; alpha excludes zero; corr 0.33/0.15 | fails one gate per weighting; components fail deflation | WEAK_SIGNAL (red-teamed) |
| E041 | Ridge / ridge-logistic stacking of 18 features vs E040 baseline | perp BTC/ETH 4h, OOS 2022–24 | OOS Sharpe −0.6 to −3.2 vs baseline 0.7–1.0 | — | REJECTED |

Portfolio components on hand: none credible enough for an ensemble yet (the only documented component is the E035 trend exposure, whose alpha is not distinguishable from zero in most cells).
