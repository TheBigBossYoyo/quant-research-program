# PHASE8_INSIDER_EVENT_STUDY - causal abnormal returns after Form 4 purchase filings (E058_20260912T185148; development 2009-01..2017-12; frozen rules)

Events entered after eligibility: 6,603 of 50,842 issuer-filing-day events in the window (D9: Tier 2 eligibility share 0.13; PIT S&P 1500 subset 2,836). Per year: {'2009': 693, '2010': 648, '2011': 827, '2012': 732, '2013': 615, '2014': 672, '2015': 836, '2016': 839, '2017': 741}. Cells: {'C1_ANY': 6603, 'C2_CLUSTER': 2081, 'C3_OPPORTUNISTIC': 1128, 'C4_OFFICER': 2144, 'C5_DIRECTOR_ONLY': 3703}. Entry at the open of the first trading day strictly after FILING_DATE. Abnormal return = event open-to-open return minus the buy-and-hold equal-weight return of the members eligible at the event signal date over the same window (AR_EW), or minus SPY (AR_SPY). Confidence intervals: bootstrap over entry months (1,000 draws, seed 20260912), which respects overlap. Horizons are descriptive, not hypotheses.

## 1. Mean abnormal return versus the equal-weight eligible universe (full window 2009-2017; 2013-2017 in brackets; 95 percent month-cluster CI for the full window)

| Cell | n | +5 | +21 | +63 | +126 | +252 |
| --- | ---: | --- | --- | --- | --- | --- |
| C1_ANY | 6,603 | -1.97% [-4.87%, -0.02%] (-0.84%) | -1.96% [-4.71%, 0.10%] (-0.51%) | -1.72% [-4.53%, 0.57%] (-0.66%) | -2.92% [-6.31%, 0.20%] (-1.07%) | -5.59% [-9.56%, -2.11%] (-0.47%) |
| C2_CLUSTER | 2,081 | -0.70% [-2.47%, 0.48%] (-0.91%) | -0.50% [-2.01%, 0.90%] (-0.90%) | -0.44% [-3.15%, 2.38%] (-2.01%) | -1.77% [-5.61%, 2.11%] (-3.09%) | -5.54% [-10.33%, -1.15%] (-3.49%) |
| C3_OPPORTUNISTIC | 1,128 | -1.36% [-3.77%, 0.33%] (-1.37%) | -0.87% [-2.54%, 0.44%] (-0.51%) | -1.72% [-4.42%, 0.47%] (-3.01%) | -3.79% [-7.52%, -0.69%] (-4.63%) | -5.14% [-9.79%, -1.33%] (-3.86%) |
| C4_OFFICER | 2,144 | -0.26% [-1.67%, 0.68%] (-0.33%) | -0.70% [-2.06%, 0.47%] (-0.72%) | -0.84% [-3.17%, 1.40%] (-1.74%) | -2.86% [-6.70%, 0.58%] (-3.94%) | -7.31% [-11.27%, -3.71%] (-5.14%) |
| C5_DIRECTOR_ONLY | 3,703 | -1.86% [-4.10%, -0.12%] (-0.98%) | -1.72% [-4.46%, 0.41%] (-0.46%) | -0.95% [-3.23%, 1.05%] (0.20%) | -1.62% [-4.89%, 1.07%] (0.90%) | -3.18% [-7.61%, 0.80%] (2.52%) |

## 2. Mean abnormal return versus SPY (full window)

| Cell | +5 | +21 | +63 | +126 | +252 |
| --- | --- | --- | --- | --- | --- |
| C1_ANY | 0.35% | 0.34% | 0.70% | 0.26% | -0.67% |
| C2_CLUSTER | 0.48% | 0.36% | 0.69% | -0.14% | -1.47% |
| C3_OPPORTUNISTIC | 0.25% | -0.23% | -1.23% | -3.07% | -5.09% |
| C4_OFFICER | 0.57% | -0.02% | 0.32% | -1.24% | -3.13% |
| C5_DIRECTOR_ONLY | 0.22% | 0.62% | 1.24% | 1.54% | 1.31% |

## 3. Diagnostics on C1 at +126 sessions (AR_EW, full window)

| Subset | n | mean | 95% CI | share positive |
| --- | ---: | ---: | --- | ---: |
| timely | 6,120 | -3.06% | [-6.59%, 0.10%] | 51% |
| late | 477 | -1.24% | [-5.38%, 2.33%] | 48% |
| direct | 4,975 | -3.27% | [-6.83%, -0.31%] | 51% |
| indirect_only | 1,622 | -1.88% | [-6.62%, 2.39%] | 48% |
| pit_sp1500 | 2,836 | 0.41% | [-1.92%, 2.28%] | 56% |
| value_top_half | 3,376 | -3.10% | [-6.90%, 0.27%] | 52% |
| value_bottom_half | 3,221 | -2.74% | [-6.49%, 0.25%] | 49% |

## 4. Reading

After a purchase filing and the conservative next-day-open entry, purchased stocks do not outperform the equal-weight liquid universe at any horizon in the full window: at +5 and +21 sessions the point estimates are negative for every cell (the announcement-day reaction is over before the entry and the following weeks show mild reversal), and at +126 sessions they are negative for C1-C4 and about zero for director-only purchases. In 2013-2017 the director-only cell is the only one with positive point estimates at +126 and +252 sessions (about +1 and +2.5 percent), inside their intervals. Versus SPY the estimates are more negative because the equal-weight universe underperformed SPY in the window. Timely versus late filings, direct versus indirect ownership and purchase size do not separate; the PIT S&P 1500 subset shows the same pattern.
