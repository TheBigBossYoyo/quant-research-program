# PHASE5_RED_TEAM_REPORT - Branch A (independent slow-trend replication) and Branch B (capital-efficiency research)

Written 2026-09-09 after E047_20260909T151953 / E048_20260909T152237 (Branch A) and E049_20260909T153444 (Branch B) were frozen. Branch A verdict under the preregistered gate: TREND_REPLICATION_FAILURE, DO_NOT_OPEN_2025. Branch B: CAPITAL_EFFICIENT_WEAK_SIGNAL (capped by Branch A). Both cases are recorded; nothing was changed after the outcomes.

## Branch A

### Researcher case

1. The cohort was selected mechanically one year earlier than Phase 4 (end-2020 liquidity, listing before April 2020), overlaps Phase 4 by only 5 of 12 names, and contains the old-generation alts that a survivor-biased cohort would never include (EOS, XTZ, XLM, TRX, VET, BCH, ETC). Nothing was dropped after the fact.
2. The risk-adjusted sign transported: 10 of 12 sleeves have positive Sharpe, 9 of 12 positive two-factor alpha, the 2021 regime never before used returned +87% at the portfolio level with 7 of 12 assets positive, and the portfolio was net short and profitable in the May-2021 crash (+40%), the Nov-2021 to Jun-2022 bear (+23%) and the FTX window (+4%), with no window worse than -10% on its worst day.
3. New names alone have a portfolio Sharpe of 0.67 (2021-2024) and 0.54 (2022-2024) with 7 of 7 positive Sharpe; the direction of the effect is not specific to the Phase 4 names.
4. Costs are not the reason for failure: the volatility-scaled slippage case (asset multipliers 1.8-2.5x) and the 14 bps case leave the portfolio at +78% and +76%, and one extra 4h delay makes it slightly better (+138%).

### Red-team case

1. **Compounding kills it.** Median sleeve drawdown -80% (LINK -96%, LTC -92%, XRP -88%) at 0.74 average gross exposure. A 0.3 Sharpe sleeve with that path has negative geometric growth: 7 of 12 sleeves lost money, the median lost 32%. "Positive Sharpe on most names" and "most names lost money" are both true, and the gate that was written on net returns failed. Any fix (lower exposure, vol scaling) is a new architecture, not a rescue of this one.
2. **Not independent of cohort 1.** Over the shared 2022-2024 window the two cohort portfolios are 0.88 correlated (monthly 0.89) and cohort 2 has half the Sharpe (0.32 vs 0.75); the difference interval [-1.08, +0.16] does not exclude equality but the point estimate is a deterioration, not a replication. The only genuinely new cell, 2021, is one year and one synchronised alt rally.
3. **One year, one regime.** 2021 is 60.4% of positive portfolio P&L; the other three years net to -3%; the portfolio was positive in 2 of 4 years; the two half-years with BTC below its lagged 200-day average lost 25% in total. Median two-factor alpha by year: +19%, -41%, -11%, +32%. The phenomenon shows up when the whole asset class trends and is absent otherwise; that is timed beta with a short overlay, not a stand-alone premium.
4. **Dependence-aware intervals include zero everywhere:** cohort-2 median alpha [-37%, +78%], new-names [-33%, +92%], cohort-1 [-11%, +102%]; median Sharpe [-0.42, +1.07]; positive-fraction [0.17, 1.00]. The asset-level Sharpe distribution (10 of 12 positive) would look significant only under an independence assumption the data violate.
5. **Shorts are defence, not alpha.** Short side lifetime -8% of capital, Sharpe -0.05, positive in 2 of 12 sleeves; it earned +29% in 2022 and gave back -25% in 2023 and -14% in 2024. Removing the short contribution changes the drawdown from -57% to -52%: the defensive value is real but small.
6. **Exposure drift.** Maximum hourly gross reached 3.7x on XRP and 2.0x on LINK/VET without any liquidation model; the -96% LINK path is optimistic because an exchange would have liquidated it earlier.
7. **Funding marks.** 21-24 settlements per asset fall back to trade opens in 2021 where mark archives were incomplete; the adverse funding case costs 0.14 Sharpe. Execution descriptors (hourly gaps p99 0.03-0.21%, mark/trade deviation p99 0.08-0.21%) do not indicate hidden gap risk but say nothing about 2021 alt depth.
8. **Data.** Three of the seven new names had the same Binance archive gap as Phase 4; the first pass ran on it and was superseded under the preregistered rule before analysis, but the fact that this recurs means every future cohort must be gap-audited against indicator warm-up before its first run.
9. **What would rescue it, and why it is not allowed here:** halving exposure or volatility-targeting the sleeves (Branch B shows how much that changes drawdowns) would probably turn the net-return gate around; doing so on this cohort after seeing the result is exactly the retuning the mandate forbids.

## Branch B

### Researcher case

1. Pooling capital into one position per asset removes the operational barrier that killed the 24-sleeve E040 layout: at 500 USDT with 2-5 liquid names, skipped orders are 0-4% of score changes, tracking error is 0.2-3.4% of portfolio volatility, and Sharpe retention is 1.00 +/- 0.02. Minimum practical capital for this architecture is at or below 500 USDT for N = 2-5 (it was 12,600-31,500 USDT for E040).
2. The volatility-target overlay (20% target, lagged 30-day volatility, gross capped at 1x) turns 48-51% drawdowns into 23-30% with Sharpe 1.03-1.17 and roughly halves turnover; the 0.5 risk scalar achieves a similar drawdown at Sharpe 0.83-0.95.

### Red-team case

1. **It implements a signal that just failed replication.** The unconstrained five-name trend portfolio has a 2022-2024 Sharpe of 0.96 because ETH, SOL, DOT and DOGE were among the better trend names in the 2023-2024 rallies; the same rule on cohort 2 delivered 0.32 over the same window. Branch B measures execution fidelity, not edge; its classification is capped at WEAK_SIGNAL for that reason and would be capped at FEASIBLE_BUT_EDGE_DESTROYED if the reference itself were held to Branch A's standard.
2. **The universe is rule-based but not innocent.** The rules (lot value, minimum notional, listing age, liquidity rank) happen to select the liquid large caps that did well in 2023-2024 and exclude the cohort-2 names that did not; a small-capital trader in 2021 would have applied the same rules and got a different list. The 2022-2024 window is the Phase 4 window, already inspected.
3. **Vol targeting is in-sample and the 20% target was chosen once, not swept;** it still adds a parameter, and its Sharpe improvement comes almost entirely from cutting exposure in 2022, which any lagged volatility rule would have done in that year.
4. **Turnover and cost remain heavy:** 84-91x average equity per year and 7.6-8.3% of average equity in fees at 1x (40-50x and 3.6-4.5% with vol targeting), above the 54-76x of the Phase 4 sleeves because pooled positions are resized on every asset's vote flip; the frozen 4h resizing on every vote flip is inefficient and the preregistered dead-bands were inert because they were set below the vote step (0.286), so no turnover reduction was actually tested.
5. **Pending orders under vol targeting at 500 USDT:** the vol-scaled targets generate sub-minimum resizes that wait 500-3,200 hours in aggregate over three years (N=2 to N=5); at 1,000 USDT this falls to 160-840 hours. The 500 USDT figures are feasible but marginal.
6. **Nothing here has been paper-traded, and the venue rules are a 2026-09-08 snapshot** (contract statuses, lot steps and minimum notionals change; MATIC and FTM already did).

## Evidence-weighted conclusion

Branch A was the experiment that could have made the slow-trend mechanism credible, and it did not. The mechanism's direction is visible in every cell, but on an independent, older, less liquid cohort its economics at 1x are those of a strategy that lost money on most names and made all of its profit in one alt-season year. Downgrade: slow trend on crypto perpetuals is a description of regime behaviour, not a validated premium; 2025 stays locked and E040 stays a frozen benchmark. Branch B answers its own narrower question cleanly: the operational problem is solvable at 500-1,000 USDT with pooled positions on liquid contracts, and volatility targeting is the obvious next architecture, but both stand on an unreplicated signal and are classified accordingly. The next informative experiment is not another crypto cohort; it is either a different market class (equities/futures, data permitting) or a preregistered volatility-scaled architecture tested on a cohort and window that have not been inspected, which today does not exist without opening 2025.
