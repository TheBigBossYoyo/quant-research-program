# RED_TEAM_REPORT — Phase 3 best development combination (E040: slow-trend ensemble + compression breakout, perp BTC/ETH 4h)

Written 2026-09-09. Researcher case and red-team case are both recorded; the classification stays WEAK_SIGNAL under the preregistered rules.

## Researcher case

- Two mechanisms with plausible economics: multi-week trend persistence (under-reaction, positioning inertia) and expansion after volatility compression (resolution of two-sided positioning). Both are low-beta to buy-and-hold (0.1–0.3).
- Development evidence at stressed costs (7.05 bps per side plus funding): trend ensemble Sharpe 1.06 (BTC) / 0.96 (ETH); breakout 1.10 / 0.82 with drawdowns of −24% / −25%; return correlation 0.33 / 0.15; equal-weight combination Sharpe 1.27 / 1.14, alpha over buy-and-hold +44% [+11%, +77%] and +38% [+2%, +74%] per year; inverse-vol combination drawdown −19% / −27%.
- Selection-free construction: the trend component averages the whole preregistered neighbourhood; the breakout component uses the preregistered channel (20) and compression threshold (20%) without the volume-parameter variant.
- Crash behaviour of the trend family (E034): 2022 bear −5% to +156% against −65% for buy-and-hold; March 2020 −5% to +31%.

## Red-team case

1. **Overfit by selection.** The trend family's best cells had textbook Deflated Sharpe 0.03–0.23 at 120 cells; the unselected ensemble still fails DSR (0.13–0.55) and alpha excludes zero in only 2 of 8 cells. The breakout component's DSR is 0.71 at 24 cells. The combination inherits both burdens; a DSR of "N = 2 combinations" understates the search that produced its parts.
2. **Sample.** Perpetual history is five years (2020–2024) with one bear year; BTC/ETH buy-and-hold Sharpe 1.1–1.2 over the window makes any long-biased rule look good; the trend component is long-biased in exposure even with low daily beta.
3. **Walk-forward.** Parameter-selection walk-forward efficiency for the trend cells was 0.24–0.72; the breakout cell 0.57. Out-of-sample year Sharpes swing from −0.7 to +1.8.
4. **Costs.** Alt-style friction is not the issue (BTC/ETH spreads are a tick), but funding is applied only from 2022 (no 2020–21 funding history on disk): 2020–21 perpetual results are slightly flattered.
5. **Drawdown gate.** The equal-weight combination's drawdown (−27% / −36%) is worse than the breakout component alone; Monte Carlo on the trend cells put a 30% drawdown as near-certain over a year at 1x.
6. **Concentration.** Trend cells: top five trades supply 30–66% of positive P&L; top year 33–49%. A rule that earns half its P&L in one year on five years of data is fragile.
7. **Regime dependence.** The breakout component is helped by volume confirmation in six of eight cells but that variant has 3–56 trades; the compression definition (ATR percentile below 20% of the trailing 250 bars) is a single point that was not walk-forward-selected.
8. **Execution.** 4h decisions with next-open execution are realistic for a retail account; 15x leverage is irrelevant (unlevered); minimum notionals are fine at 500 USDT for BTC/ETH perps. No hidden fill assumptions.

## Verdict

The combination is the most credible thing Phase 3 found and it does not clear the preregistered bar: components fail multiplicity, the combination fails one gate in each weighting, and the sample is too short and too bull-biased to distinguish alpha from timed beta with confidence. Classification WEAK_SIGNAL; no validation access; no promotion. What would change the verdict: a further independent development regime (e.g., a 2025-style year, which is locked), or the same result on additional liquid assets with the rule frozen first.
