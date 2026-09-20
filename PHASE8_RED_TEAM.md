# PHASE8_RED_TEAM - attacks on the E058 insider-purchase cells (E058_20260912T185148, E058RT_20260912T190236; development only)

Role: hostile reviewer. The question is whether the only positive number in Phase 8, the director-only cell's +7.6 percent a year over the equal-weight universe in 2013-2017, is private information or a repackaged style exposure, and whether any cell hides a promotable architecture.

## 1. Concentration and contributor removal (MANUAL_USD, primary)

| Cell | Top ticker share of gains | Top 5 events share | Top insider share | 2013-17 excess after dropping top 5 events | after dropping top 10 | Best-year share of 2009-17 excess |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| C1_ANY | 3.5% | 9.8% | 1.7% | 2.82% | 2.82% | 93% |
| C2_CLUSTER | 3.6% | 9.8% | 1.6% | 0.05% | 0.14% | 479% |
| C3_OPPORTUNISTIC | 3.0% | 9.2% | 2.6% | -5.60% | -5.60% | -18% |
| C4_OFFICER | 5.1% | 17.0% | 0.4% | 0.69% | 0.69% | 181% |
| C5_DIRECTOR_ONLY | 5.1% | 11.2% | 1.3% | 7.55% | 7.55% | 28% |

No cell depends on one stock, one insider or a handful of events; the director-only excess survives removal of its ten best events. Concentration is not the objection.

## 2. Style exposure: Fama-French three-factor regression of monthly net returns (2013-2017; 2009-2017 in brackets)

| Cell | Alpha (ann.) | Alpha t | Mkt | SMB | HML | R2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| C1_ANY | -6.6% (-4.3%) | -1.22 (-1.22) | 1.18 (1.19) | 0.09 (0.21) | 0.30 (0.10) | 0.60 |
| C2_CLUSTER | -9.1% (-5.2%) | -1.80 (-1.43) | 1.16 (1.14) | 0.38 (0.38) | 0.45 (0.27) | 0.60 |
| C3_OPPORTUNISTIC | -12.9% (-6.6%) | -3.09 (-1.86) | 1.04 (0.98) | 0.23 (0.36) | 0.42 (0.10) | 0.55 |
| C4_OFFICER | -6.4% (-3.2%) | -1.40 (-0.96) | 1.03 (1.09) | 0.15 (0.19) | 0.33 (0.14) | 0.47 |
| C5_DIRECTOR_ONLY | -2.2% (-2.5%) | -0.62 (-0.91) | 1.20 (1.26) | 0.17 (0.20) | 0.20 (0.12) | 0.70 |

Every cell has a NEGATIVE three-factor alpha in 2013-2017 (director-only -2 percent a year, t -0.6; opportunistic -13 percent, t -3.1) with market betas of 1.0-1.2, positive size loadings and value loadings of 0.2-0.45. The answer to the central question is yes: these portfolios are insiders buying beaten-down, smaller, higher-book-to-market stocks, and the excess over the equal-weight universe is the compensation for that exposure in a window when it paid, not private information.

## 3. Liquidity, timing and filing diagnostics

| Cell | Share of entries in ranks 501-1000 | Median liquidity rank | Share of entries while SPY drawdown > 10% (> 20%) | Timely-only 2013-17 excess | Late-only 2013-17 excess | Excluding later-amended originals | Median purchase USD | PIT S&P 1500 share |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| C1_ANY | 50% | 496 | 32% (20%) | 1.93% | 3.28% | 3.61% (t 1.01) | 186,862 | 43% |
| C2_CLUSTER | 52% | 530 | 31% (19%) | -0.22% | -2.29% | -0.64% (t -0.17) | 202,500 | 40% |
| C3_OPPORTUNISTIC | 57% | 589 | 24% (11%) | -4.20% | -7.51% | -5.82% (t -1.26) | 295,877 | 50% |
| C4_OFFICER | 55% | 570 | 31% (20%) | -1.29% | -3.93% | 0.90% (t 0.19) | 189,802 | 39% |
| C5_DIRECTOR_ONLY | 45% | 438 | 31% (20%) | 7.26% | 1.08% | 7.74% (t 2.71) | 122,900 | 46% |

Sector mix of the PIT S&P 1500 subset (current labels, SECTOR_NOT_PIT): {'Industrials': 0.203, 'Consumer Cyclical': 0.153, 'Financial Services': 0.134, 'Energy': 0.099, 'Healthcare': 0.09, 'Consumer Defensive': 0.087, 'Basic Materials': 0.076, 'Technology': 0.056, 'Real Estate': 0.046, 'Utilities': 0.043, 'Communication Services': 0.011}. Half of all entries sit in the less liquid half of the universe (ranks 501-1000), which is where the STRESS cost case applies; about 30 percent of entries happen while SPY is more than 10 percent below its high (insiders buy dips), so part of the equal-weight excess is dip-buying beta. Timely and late filings do not separate in a consistent direction across cells; excluding originals that were later amended changes nothing material.

## 4. Execution, cost and holding sensitivities (from PHASE8_INSIDER_RESULTS.md section 2)

One extra session of delay, the 63- and 252-session holds, 10 and 40 slots, the all100/all30 delisting rules and the STRESS cost case move the 2013-2017 excess by a few points but never create an alpha against SPY; the automated (API, 20-25 bps) case keeps the director-only excess over the equal-weight universe at +6.9 percent a year, so costs are not what separates this family from promotion; the benchmark is.

## 5. Verdict

The insider-purchase family, implemented causally and long-only, does not beat the deployable alternative in 2013-2017 in any preregistered cell. The one cell that beats the equal-weight universe (director-only) does so through market, size and value exposure. Development gate: FAIL for all five cells. Nothing is frozen for validation.
