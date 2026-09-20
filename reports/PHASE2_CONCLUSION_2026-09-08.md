# Phase 2 conclusion — information-frontier expansion — 8 September 2026

## Verdict

**No strategy currently passes, and the newly accessible information frontier does not produce one.** Phase 2 changed the information set five times — displayed order-book liquidity, trade-level aggressor flow on perpetuals and spot, five-minute open interest and positioning ratios, and a per-second implied-volatility index — and tested 124 preregistered hypotheses (E024–E031) with execution modeled from the start. Cumulative count across both phases: 367. The 2025 validation set was never analysed and the 2026 holdout never downloaded; no file dated 2025 or later was acquired from any feed. No orders, credentials or capital were involved.

## What the new information revealed

| Information set | Experiments | Statistically credible effects | Best executable edge | Why it fails |
|---|---|---|---|---|
| Displayed depth ±1–5% (30-s snapshots), trade-level flow, sweeps, open interest | E024, E026 | Depth imbalance IC +0.04 (5 min) → +0.06 (30 min) → +0.05 (2 h) in both assets; liquidity-normalised flow and sweeps revert | ≤ 2.0 bps per extreme-decile trade | Taker round trip 12.1 bps; required IC 0.20 at 30 min, 0.07–0.10 at 2–4 h |
| Passive capture of the depth drift | E027, E030 | Signal halves adverse selection versus placebo | −7 to −10 bps per fill; 5–6% fill rate | Fills occur only when price moves through the order; negative even at the front-of-queue bound |
| Synchronized spot trades | E028 | Basis dislocation and spot flow revert (IC −0.01 to −0.02) | ≤ 0.6 bps | Venues arbitraged within a fraction of a basis point |
| Positioning ratios (top-trader, retail, taker) | E029 | Taker ratio reverts (IC −0.03 to −0.04) | ≤ 0.5 bps | Same reversal family; positioning ratios insignificant on 93 days |
| Implied volatility index (BVOL) | E031 | 2-hour IV shock borderline (ETH); daily VRP/IV-level large but unmeasurable | 4.4 bps (2 h); daily cells not significant | 78 independent weeks cannot resolve daily effects; minute effect below cost |

Cost model: taker fee 5 bps, half-spread 0.05 bps (measured: one-tick spread), slippage 1/2/4 bps; maker fee 2 bps for passive tests; 5-second latency allowance, with 30-second stress. Every experiment used deterministic every-third-day samples (194 days per symbol, 2023-06 to 2024-12) with daily-block bootstraps and Bonferroni gates across cells.

## The arithmetic that closes the taker branch

Forward-return dispersion on the sampled days is 15–17 bps at 5 minutes, 35–42 bps at 30 minutes, 68–84 bps at 2 hours and 95–121 bps at 4 hours. An extreme-decile edge is roughly IC × dispersion × 1.75, so clearing 12.1 bps needs an IC near 0.45 at 5 minutes, 0.2 at 30 minutes and 0.06–0.10 at 2–4 hours. The best measured IC is 0.064; at 4 hours it is 0.054 and not significant after adjustment, with a measured edge of 1.6–2.0 bps. No combination of features with ICs of 0.01–0.06 reaches these thresholds, which is why no model-combination search was run: it would add trials without changing the answer.

## What was deliberately not tested, and why

- **bookTicker touch-level state** (2023-05 to 2024-03, 50 GB per symbol): touch-level imbalance decays faster than the 1% depth imbalance that already carries the largest IC; it cannot beat the cost arithmetic at retail horizons and the passive route is closed.
- **Option end-of-hour summaries** (skew, term structure): only 147 days exist (May–October 2023); no skew hypothesis can be adequately powered.
- **Cross-sectional depth across the perpetual universe**: over 100 GB for a family already shown to pay one to two basis points.
- **Liquidation/forced-order data**: not present in the public archive.
- **Macro releases, on-chain flows, sentiment**: not causally timestamped at the required quality for free, and the mandate warns against weak alternative-data narratives.

## Reopening conditions

1. A materially different cost structure: a maker-rebate tier, institutional fees, or a venue with sub-basis-point taker costs would change the arithmetic for the depth-imbalance and flow-reversal effects, which are real. This is an account decision, not a research one.
2. Queue-position information (an order-book event stream with own-order placement) to model passive fills honestly; the public archive does not provide it.
3. Longer option history (several years) for the daily variance-risk-premium and IV-level effects, whose point estimates were large but unmeasurable on eighteen months.
4. A liquidation feed with causal timestamps.
5. The Phase 1 reopening conditions remain (broader regimes for the cross-sectional flow effect; checksum-grade ETF data).

## Integrity notes

Defects found during Phase 2: none in ledgers or features; a NaN-serialisation issue and a timezone mismatch in reporting code were fixed and the affected runs repeated unchanged; one run was refused by the code-hash guard after a concurrent source edit and repeated. Source-missing days: one bookDepth day, ten BVOL days, recorded and left as gaps. Test count at close: 82. Every experiment directory carries results.json with code hash, seeds, cost cases and the full set of rejected cells.
