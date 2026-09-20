# PHASE8_INSIDER_RESULTS - E058 slot portfolios (E058_20260912T185148; development only; MANUAL_USD primary costs; 20 slots; 126-session hold)

Frozen rules: PHASE8_PREREGISTRATION.md (hash in PHASE8_PREREGISTRATION.sha256). Two earlier runs were superseded for benchmark/label defects found before interpretation (reports/E058_superseded_*). Benchmarks: equal-weight Tier 2 eligible universe (monthly rebalanced, delisting bookings identical) and SPY. All cells, variants and cost cases are in PHASE8_INSIDER_PORTFOLIOS.csv.

## 1. Primary architecture by cell

| Cell | Events | 2009-2012 excess vs EW (t) | 2013-2017 excess vs EW (t) | Years positive 2013-17 | 2013-17 net CAGR / EW / SPY | Net Sharpe / SPY | Alpha vs SPY (t) | Beta | Max DD 2009-17 / SPY | Turnover one-way | Avg positions | Skipped (slots full / already held) | AUTOMATED 2013-17 excess | Gates failed | BH | DSR |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | --- | ---: | ---: | --- | ---: | --- | --- | ---: |
| C1_ANY | 6,603 | 0.21% (0.08) | 2.82% (0.75) | 3/5 | 10.7% / 8.2% / 15.2% | 0.71 / 1.51 | -7.0% (-1.45) | 1.25 | -33% / -17% | 1.80x | 18.94 | 5417 / 818 | 2.21% | G1_excess, G2_t, G3_years, G4_alpha, G5_dd, G8_concentration | N | 0.67 |
| C2_CLUSTER | 2,081 | 0.45% (0.10) | 0.05% (0.02) | 2/5 | 7.4% / 8.2% / 15.2% | 0.48 / 1.51 | -8.3% (-1.61) | 1.15 | -36% / -17% | 1.84x | 18.94 | 1234 / 487 | -0.53% | G1_excess, G2_t, G3_years, G4_alpha, G5_dd, G7_automated, G8_concentration | N | 0.49 |
| C3_OPPORTUNISTIC | 1,128 | -1.12% (-0.36) | -5.60% (-1.42) | 1/5 | 1.8% / 8.2% / 15.2% | 0.18 / 1.51 | -12.8% (-2.93) | 1.07 | -37% / -17% | 1.75x | 17.57 | 295 / 499 | -6.18% | G1_excess, G2_t, G3_years, G4_alpha, G5_dd, G7_automated, G8_concentration, G9_early | N | 0.24 |
| C4_OFFICER | 2,144 | 1.99% (1.21) | 0.69% (0.15) | 2/5 | 8.3% / 8.2% / 15.2% | 0.56 / 1.51 | -5.8% (-1.20) | 1.03 | -36% / -17% | 1.83x | 18.86 | 1368 / 415 | 0.09% | G1_excess, G2_t, G3_years, G4_alpha, G5_dd, G8_concentration | N | 0.56 |
| C5_DIRECTOR_ONLY | 3,703 | 0.90% (0.24) | 7.55% (2.78) | 5/5 | 16.1% / 8.2% / 15.2% | 1.07 / 1.51 | -1.8% (-0.52) | 1.23 | -28% / -17% | 1.79x | 18.92 | 3003 / 338 | 6.93% | G4_alpha | Y | 0.89 |

## 2. Sensitivities (MANUAL_USD unless stated; 2013-2017 excess vs EW, t)

| Cell | h63 | h252 | slots 10 | slots 40 | delay +1 | all100 | all30 | STRESS costs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1_ANY | 2.40% (1.04) | 7.18% (1.79) | 6.18% (1.13) | 0.39% (0.14) | 2.18% (0.56) | 2.82% (0.75) | 2.55% (0.69) | 1.63% (0.43) |
| C2_CLUSTER | -1.86% (-0.47) | -0.80% (-0.21) | 0.76% (0.17) | -2.46% (-0.99) | -0.32% (-0.09) | 0.05% (0.02) | 0.05% (0.02) | -1.12% (-0.31) |
| C3_OPPORTUNISTIC | -1.76% (-0.56) | -5.35% (-2.72) | -3.16% (-0.49) | -4.40% (-2.09) | -4.92% (-1.24) | -5.60% (-1.42) | -5.61% (-1.42) | -6.78% (-1.72) |
| C4_OFFICER | -6.69% (-2.15) | -1.67% (-0.19) | 2.36% (0.27) | -2.62% (-0.67) | 1.25% (0.27) | 0.69% (0.15) | -1.28% (-0.28) | -0.55% (-0.12) |
| C5_DIRECTOR_ONLY | 2.65% (0.71) | 8.29% (2.35) | 11.67% (3.64) | 4.46% (2.84) | 8.53% (3.41) | 7.55% (2.78) | 7.16% (2.76) | 6.35% (2.35) |

## 3. Yearly excess over the EW universe (MANUAL_USD, primary)

| Cell | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C1_ANY | 5.6% | -2.6% | -3.9% | 1.8% | 13.6% | 12.0% | -17.1% | 5.3% | -0.0% |
| C2_CLUSTER | 5.7% | -3.0% | 2.5% | -3.4% | -4.3% | 5.8% | -8.1% | 10.0% | -3.2% |
| C3_OPPORTUNISTIC | -1.9% | 1.1% | -5.5% | 1.8% | -0.3% | -9.6% | -9.8% | 5.7% | -13.6% |
| C4_OFFICER | 1.2% | 1.1% | 3.7% | 2.0% | 1.2% | -4.1% | -13.6% | 20.5% | -0.7% |
| C5_DIRECTOR_ONLY | 2.4% | -3.5% | -0.2% | 4.9% | 11.0% | 5.6% | 11.4% | 4.4% | 4.8% |

## 4. Gate outcome

No cell passes G1-G10 with multiplicity. C5 DIRECTOR_ONLY passes every gate except G4 (CAPM alpha versus SPY, t -0.52): its 2013-2017 excess over the equal-weight universe (+7.6 percent a year, t 2.8, five positive years, BH-FDR pass) is explained by market exposure, so it does not beat the deployable alternative; its deflated-Sharpe probability is 0.89, below 0.90. C1 ANY earns +2.8 percent a year over the equal-weight universe in 2013-2017 (t 0.75) with a negative alpha against SPY (t -1.45). Clusters, opportunistic and officer purchases do not beat the universe. DEVELOPMENT GATE: FAIL.
