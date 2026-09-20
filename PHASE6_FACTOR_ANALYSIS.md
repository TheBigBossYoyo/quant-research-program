# PHASE6_FACTOR_ANALYSIS - family-level evidence (E050_20260909T211001, development 1963-07..2017-12, French library CRSP vintage 202607, value-weighted)

Cap on every classification here: FACTOR_EVIDENCE. These are portfolio-level, cost-free, survivorship-free series; they say whether a family ranks returns over six decades, not whether a top-N Trading 212 portfolio makes money. Statistics: Newey-West HAC(6) t on monthly means; stationary block bootstrap (24-month expected block, 4,000 draws, seed 20260909); eras E1 1963-79, E2 1980-99, E3 2000-09, E4 2010-17. All ten preregistered trials are reported; none was dropped.

## 1. Results table (monthly, percent)

| Trial | L/S mean | HAC t | Sharpe | Boot 95% CI of mean | Eras positive | Spearman | Long-only excess vs market: mean, FF3 alpha (t) | Post-2000 L/S t | Classification |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- | ---: | --- |
| H1 momentum 12-2 deciles (D10-D1) | 1.272 | 4.48 | 0.64 | [0.78, 1.73] | 4/4 | 0.99 | 0.571; 0.566 (5.00) | 0.64 | FACTOR_EVIDENCE |
| H2 short-term reversal (D1-D10) | 0.348 | 1.92 | 0.23 | [-0.01, 0.71] | 4/4 | 0.92 | 0.111; -0.186 (-1.31) | 0.59 | REJECTED; break-even one-way cost 6.9 bps at f=0.8 (< 20 bps): family terminated |
| H3 low total variance (Q1-Q5) | 0.237 | 0.91 | 0.13 | [-0.24, 0.73] | 3/4 | 0.00 | -0.001; 0.096 (1.70) | 0.92 | REJECTED (raw); L/S FF3 alpha 0.665 (t 4.29) |
| H4 low residual variance (Q1-Q5) | 0.276 | 1.10 | 0.16 | [-0.19, 0.75] | 3/4 | 0.00 | 0.023; 0.116 (2.64) | 0.75 | REJECTED (raw); L/S FF3 alpha 0.687 (t 5.05) |
| H5a industry momentum 12-1 (top10-bottom10 of 49) | 0.676 | 3.64 | 0.51 | [0.36, 1.01] | 4/4 | 1.00 | 0.332; 0.402 (4.19) | 0.69 | FACTOR_EVIDENCE |
| H5b industry momentum 6-1 | 0.425 | 2.57 | 0.34 | [0.12, 0.75] | 4/4 | 0.90 | 0.188; 0.246 (2.84) | 1.33 | WEAK_SIGNAL |

| Timing trial | CAPM alpha (t) | Sharpe vs B&H | Max DD vs B&H | CAGR vs B&H | Era Sharpe wins | Post-2000 alpha t | Classification |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| H6a market trend SMA10 | 0.199 (2.02) | 0.51 vs 0.41 | -24.3% vs -50.3% | 10.3% vs 10.2% | 2/4 | 2.88 | WEAK_SIGNAL |
| H6b market trend SMA12 | 0.219 (2.24) | 0.53 vs 0.41 | -24.3% vs -50.3% | 10.6% vs 10.2% | 2/4 | 2.68 | WEAK_SIGNAL |
| H7a vol-managed, cap 1.0 | 0.108 (1.74) | 0.47 vs 0.40 | -16.0% vs -50.3% | 9.0% vs 10.1% | 3/4 | 2.45 | WEAK_SIGNAL |
| H7b vol-managed, cap 1.5 | 0.171 (2.19) | 0.51 vs 0.40 | -16.0% vs -50.3% | 10.0% vs 10.1% | 3/4 | 2.76 | WEAK_SIGNAL |

Multiplicity: Benjamini-Hochberg at 0.05 across the seven primary trials passes H1 and H5a only; within-neighbourhood Bonferroni (2 cells) leaves H5b, H6 and H7 where the gates put them. Cumulative hypothesis count 398.

## 2. Interpretation per family

- Momentum (A): the strongest family. Deciles are almost perfectly monotonic (rho 0.99); the long-only top decile beats the market by 0.57 percent per month with an FF3 alpha t of 5.0 and a small market beta (0.05 over FF3). The problem is the modern era: post-2000 the L/S t is 0.64 (mean 0.41 percent), E3 contributes 0.25 percent and E4 0.60 percent per month, and the long-only excess is 0.15-0.19 percent per month in E3/E4 (t 0.75). The 2009 crash erased 100 percent of one year's arithmetic L/S return (see the red-team report); the long-only top decile lost 16.6 percent relative to the market in 2009. Momentum is FACTOR_EVIDENCE over 54 years and inconclusive over the last 18 development years; stock-level work must therefore treat 2000-2017 as a mandatory era, not an afterthought.
- Industry relative strength (F): 12-1 passes every gate with a perfect quintile ordering and a long-only top-10 excess of 0.33 percent per month (FF3 alpha t 4.2) at near-zero market beta. Same modern-era decay pattern (post-2000 t 0.69). The 6-1 version is weaker (WEAK_SIGNAL) but, interestingly, holds up better post-2000 (t 1.33); this is a neighbourhood observation, not a selection.
- Short-term reversal (E): the D1-D10 spread is 0.35 percent per month with t 1.9, and it is entirely a beta/size exposure (FF3 alpha t 0.4). With near-complete monthly turnover the break-even one-way cost is 5.5-11 bps under the stated turnover assumptions, below the 20 bps automated base case. Terminated at the family level; no stock-level compute.
- Low volatility (D): raw returns are not monotonic (the fourth quintile earns the most, the fifth the least) and the raw Lo-Hi spread has t 0.9-1.1. The effect is entirely risk-adjusted: L/S CAPM/FF3 alphas have t 3.5-5.1 because the low-variance quintile carries beta 0.6-0.8. For an unlevered long-only account the low-variance quintile returns roughly the market with lower beta and shallower drawdowns; it is not a return engine and cannot be levered here (mandate section 38). REJECTED as an alpha family under the preregistered raw-return gates. Preserved note: as a risk-control property inside a momentum portfolio (Stage 6, momentum + low volatility rank average) it may reduce drawdown without adding return; that is a portfolio-construction question, to be tested only at stock level with the multiplicity counted.
- Trend as market filter (C): halves the maximum drawdown (-24 percent vs -50 percent) at unchanged CAGR, alpha t 2.0-2.2, but loses on Sharpe in both long bull eras (E2, E4), so replication across eras fails. WEAK_SIGNAL, appropriate as a drawdown overlay candidate, not as alpha. Post-2000 alpha t 2.7-2.9 reflects the two large bear markets in that window.
- Volatility-managed exposure (G): the cap-1.0 (deployable, no leverage) version cuts drawdown to -16 percent and raises Sharpe modestly at the price of 1.1 points of CAGR; alpha t 1.74. Era wins 3/4. WEAK_SIGNAL. With a 1.5 cap (not deployable in Invest) alpha t 2.2. Same lesson as Phase 5: volatility scaling changes geometric growth and drawdown; here it improves the risk profile but does not create return.

## 3. What earns stock-level compute (after the data purchase)

1. Cross-sectional momentum 12-1 (Family A) with residual momentum (Family B) as the direct comparison, top-N long-only at monthly rebalance; mandatory era table including 2000-2017; crash-window behaviour (2009, 2020 is validation) as a red-team item.
2. Industry/sector relative strength (Family F) and sector-neutral stock momentum, to separate stock selection from sector bets.
3. Overlays tested only on survivors (Stage 6): trend filter (SMA10/12) and volatility management (cap 1.0) on the top-N momentum portfolio; low-volatility as a rank-average component for drawdown, not return.
Not funded: short-term reversal (terminated), stand-alone low volatility (no raw premium), quality/value (no point-in-time fundamentals within budget).

## 4. Caveats that stay attached to these numbers

French deciles use NYSE breakpoints over all CRSP stocks: the value-weighted top decile is dominated by large caps but still includes names below the liquidity threshold a Trading 212 universe would impose. No costs, no turnover, no delisting haircut beyond CRSP's own treatment, no fractional-share rounding. Industry momentum uses SIC-based industries, not GICS. The market filter and volatility overlay are index-level results and say nothing about stock-level implementation. None of these numbers may be quoted as a strategy return.
