# PHASE3_RESEARCH_MAP — audit of what was actually executed (built 2026-09-09 from EXPERIMENTS.md and report directories E001–E031)

Counting convention carried forward: 367 counted hypotheses through Phase 2. Phase 3 introduces a hierarchical ledger (economic hypotheses / architecture variants / parameter configurations) and continues the economic-hypothesis count from 368; architecture and parameter counts are tracked separately (see EXPERIMENTS.md, "Phase 3 multiplicity framework").

"Previously tested?" means an experiment directory with results exists, not that a prompt mentioned it.

| Family | Previously tested? | Depth of prior testing | Reason to reopen? | New information/mechanism | Priority |
|---|---|---|---|---|---|
| A. Moving-average trend (price/MA regime, dual MA, slope, distance, multi-timeframe) | Partially: E001 tested a 20-bar SMA displacement as a long/cash *baseline* only (spot 5m–1d, 2022–24); E020 tested 10-month SMA on ETFs (monthly). No dual-MA, slope, distance or MTF architecture was ever run; no ATR stops, no vol sizing, no long/short on perps with MA regimes | Shallow (baselines only) | Yes: core family never tested as an architecture; trend systems have skewed trade distributions that IC screens under-rate | Longer history (spot 1h from 2017, perp 1h from 2020) adds the 2018 bear, 2019 range, 2020–21 bull; ATR stops and vol targeting are new | 1 |
| B. Supertrend | No | None | Yes | ATR-band trend state; incremental value test vs MA/Donchian | 1 |
| C. Donchian / breakout (channel, ATR-sized, volume-confirmed, HTF-filtered, compression, trailing exit) | No (only trailing-return momentum at fixed lookbacks, E001/E010) | None as breakout architecture | Yes | Extreme-state entries with trailing exits; positive-skew payoff | 1 |
| D. Volatility compression/expansion | No | None | Yes | ATR/bandwidth percentile transitions; conditional breakout | 6 |
| E. Bollinger / z-score mean reversion (regime-conditioned) | No; only raw trailing-return reversal (E001/E010) and hourly flow reversal (E012/E024) which were cost-dominated at 5m–1h | Shallow, unconditioned | Yes, only at horizons where the move exceeds costs (1h–4h bars) and only with regime conditioning | Range/trend regime gate; volatility-normalised displacement | 4 |
| F. RSI as continuous feature (pullback-in-trend, range reversion, persistence) | No | None | Yes | Normalised directional persistence; pullback-with-trend architecture | 2 |
| G. MACD | No | None | Yes, as incremental-information test only | Smoothed momentum difference vs raw momentum | 7 (ablation within A) |
| H. ADX / trend strength | No | None | Yes, as conditional state variable | Trend-strength gating of A/B/C | 2–3 (as filter) |
| I. ATR | Only as a volatility descriptor in E003 regimes | None as stop/sizing device | Yes | Stops, sizing, breakout definition | Used inside A–F |
| J. VWAP | No | None | Yes (crypto rolling/session VWAP; volume data exist) | Displacement from traded-volume location; reclaim/rejection | 4 |
| K. Volume features | Partially: taker imbalance (E001, E012, E016 cross-sectional), abnormal volume rank (E018) | Moderate but as ranks, not as breakout confirmation | Yes, as confirmation/exhaustion conditioning of C | Relative volume interaction with breakouts | 3 (inside C) |
| L. Candle structure | No | None | Yes, as incremental-information ablation | Body/wick/close-location after controlling trend/vol | 7 |
| M. Pullback with trend | No | None | Yes: highest-priority untested architecture | HTF trend + LTF pullback + resumption trigger | 2 |
| N. Multi-timeframe systems | No | None | Yes | Completed-bar HTF regime feeding LTF triggers | 3 |
| O. Relative strength (liquid large caps, long-only or long/short) | Partially: E014/E016/E023 cross-sectional 7/30/90-day momentum on the full 396-name universe (rejected; 2020 concentration, illiquid names) | Moderate, but universe-wide equal-weight quintiles only | Yes, restricted to liquid large caps with absolute-momentum overlay and volatility adjustment; ETF relative strength (E020 tested 12-1 momentum top-3 monthly, rejected) | Liquidity-screened universe; risk-adjusted and residual momentum; absolute+relative combination | 5 |
| P. Regime switching (trend/vol/correlation/liquidity states) | Partially: descriptive regime splits in E003; vol30 rank in E018; no regime-conditioned strategy | Shallow | Yes, as conditioning layer for A/C/E | Percentile-based causal states | 4 (with E) |
| Q. Ensembles of surviving components | No (no component ever survived) | None | Only if ≥2 components reach PORTFOLIO_COMPONENT_CANDIDATE | Correlation-aware combination with shrinkage | 7 |
| R. Regularized ML alpha stacking | No | None | Only after Stage-D components exist | Ridge/logistic over the feature library; must beat simpler baseline OOS | 8 |
| S. Carry / funding (delta-neutral, cross-sectional) | Yes: E004–E009 (ETH/BTC carry, demoted vs short-rate reference), E014/E016 fund7 rank (insignificant) | Deep | No standalone reopening; funding only as a cost/credit inside perp ledgers | — | Closed |
| T. Session / seasonality | Yes: E021 (session, funding-hour; cost-destroyed at 5m) | Moderate for spot 5m | Only as a conditioning variable at ≥1h bars, not standalone | — | Low |
| U. Microstructure (depth, flow, sweeps, OI, positioning, spot sync, passive fills, IV shocks) | Yes: E012–E013, E024–E031 | Deep; cost arithmetic recorded | No, absent new fee structure or queue data | — | Closed |
| V. ETF trend/momentum (Trading 212 long-only) | Yes: E020 (trend12, sma10, 12-1 momentum, combined; all below equal weight on 2009–19) | Moderate (four rules, monthly) | Possibly later with a longer development window and regime conditioning; labelled RESEARCH-ONLY under current broker constraints for anything needing shorts | — | Low |

## Prioritized hypothesis tree (Phase 3)

1. **Trend and breakout on BTC/ETH (spot 1h 2017–2024; perp 1h 2020–2024; 4h and daily derived; 15m from spot 5m 2022–2024)** — Families A, B, C with ATR stops/trailing exits and volatility sizing; incremental-value tests (Supertrend vs MA vs Donchian); ADX/volume/HTF conditioning as ablations.
2. **Pullback with trend (M) and RSI/Bollinger pullback triggers (F/E)** on the same data, HTF from completed bars.
3. **Multi-timeframe (N)** variants of 1–2.
4. **Regime-conditioned mean reversion (E, P)** at 1h–4h bars where the expected move can exceed costs.
5. **Liquid large-cap relative strength (O)** on the perpetual universe restricted by liquidity; long-only and long/short.
6. **Volatility compression/expansion (D)**.
7. **Ensembles (Q) and regularized stacking (R)** only for survivors.

Protected data: 2025 validation unopened; 2026 holdout never downloaded; nothing changes in Phase 3.
