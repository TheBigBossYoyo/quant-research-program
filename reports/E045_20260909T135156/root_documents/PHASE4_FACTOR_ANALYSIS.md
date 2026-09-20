# Phase4 factor analysis

Daily net returns regressed on underlying return, BTC, equal-weight replication market, lagged30-day BTC volatility and lagged200-day BTC trend sign. HAC14-day95% intervals. The market includes the tested name; common factors are correlated and coefficients can be unstable. Volatility and trend are state controls, not necessarily tradable factor portfolios. The intercept is conditional and depends on this specification. No claim of causal alpha. OLS residual Sharpe is approximately zero by construction; factor-adjusted Sharpe retains the fitted intercept. The asset-only regression is reported alongside the richer model.

| asset | component | alpha | alpha_ci_low | alpha_ci_high | asset_beta | btc_beta | market_beta | r_squared | residual_sharpe | factor_adjusted_sharpe | univariate_alpha | univariate_beta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOLUSDT | trend | 2.5276 | -0.40319 | 5.4584 | 0.13029 | 0.0174 | -0.26497 | 0.018874 | 2.4888e-15 | 3.1508 | 0.99609 | -0.016714 |
| XRPUSDT | trend | -0.77336 | -2.94 | 1.3933 | 0.30107 | -0.076849 | -0.27346 | 0.10156 | 1.541e-14 | -1.301 | 0.092976 | 0.11541 |
| BNBUSDT | trend | 1.2678 | -0.29295 | 2.8286 | 0.21604 | -0.11125 | -0.11807 | 0.033768 | -2.0799e-14 | 2.6612 | -0.018237 | 0.028144 |
| DOTUSDT | trend | -0.43764 | -2.4025 | 1.5272 | 0.49472 | -0.1641 | -0.53211 | 0.11581 | 4.8887e-14 | -0.71176 | 0.42301 | -0.011402 |
| DOGEUSDT | trend | 2.1515 | -0.23007 | 4.5331 | 0.69092 | -0.25552 | -0.51302 | 0.28331 | -5.7198e-14 | 3.1797 | 0.45492 | 0.28805 |
| ADAUSDT | trend | -0.56619 | -2.755 | 1.6226 | 0.42011 | -0.17212 | -0.46293 | 0.10653 | 5.3033e-15 | -0.90234 | 0.46156 | -0.020289 |
| AVAXUSDT | trend | 1.3293 | -0.7694 | 3.4281 | 0.39973 | -0.25831 | -0.39236 | 0.086299 | -3.9212e-16 | 1.8798 | 0.69183 | 0.036974 |
| AXSUSDT | trend | 2.039 | -0.3061 | 4.3841 | 0.27658 | -0.30302 | -0.34439 | 0.10138 | -1.939e-14 | 2.8364 | 0.47899 | -0.0442 |
| MATICUSDT | trend | 2.2241 | 0.076145 | 4.3721 | 0.23274 | -0.13241 | -0.25435 | 0.050151 | 2.805e-14 | 3.4505 | 0.18261 | 0.0031356 |
| FTMUSDT | trend | 2.9588 | -0.027602 | 5.9452 | 0.37246 | -0.1585 | -0.42574 | 0.086895 | -2.4704e-14 | 3.4622 | 1.0005 | 0.10552 |
| LTCUSDT | trend | 0.28731 | -1.6964 | 2.271 | 0.28666 | -0.21958 | -0.097937 | 0.061551 | -5.2891e-14 | 0.50183 | -0.24382 | 0.10754 |
| LINKUSDT | trend | 1.4169 | -1.019 | 3.8528 | 0.486 | -0.33038 | -0.38975 | 0.14791 | -4.4847e-14 | 2.0933 | -0.31781 | 0.087415 |
| SOLUSDT | breakout | 0.63537 | -0.39272 | 1.6635 | 0.025336 | 0.034102 | -0.03314 | 0.0060978 | 3.0046e-15 | 1.9907 | 0.061006 | 0.018473 |
| XRPUSDT | breakout | 0.36966 | -0.5873 | 1.3266 | -0.0035802 | -0.016411 | -0.036418 | 0.029661 | 1.8881e-15 | 1.7161 | -0.061001 | -0.030623 |
| BNBUSDT | breakout | -0.23029 | -0.72346 | 0.26288 | 0.0044037 | -0.026967 | 0.019715 | 0.0039304 | -1.2128e-15 | -1.3355 | 0.022836 | 0.0058448 |
| DOTUSDT | breakout | 0.016866 | -1.224 | 1.2577 | -0.0064135 | 0.016436 | -0.032217 | 0.0061011 | -1.8332e-15 | 0.058681 | 0.013199 | -0.024338 |
| DOGEUSDT | breakout | 0.84915 | -0.33306 | 2.0314 | 0.019934 | -0.012541 | -0.048838 | 0.012283 | -1.7607e-15 | 2.9678 | 0.26306 | -0.013739 |
| ADAUSDT | breakout | -0.19857 | -1.6473 | 1.2502 | 0.13403 | 0.012508 | -0.11913 | 0.037614 | 5.1861e-15 | -0.6877 | 0.27448 | 0.04645 |
| AVAXUSDT | breakout | -0.56453 | -1.9171 | 0.78804 | 0.051125 | 0.029872 | -0.10967 | 0.011486 | -4.2037e-16 | -1.6046 | 0.26653 | -0.0092076 |
| AXSUSDT | breakout | 0.21714 | -1.1307 | 1.565 | 0.10582 | -0.0028375 | -0.16426 | 0.032072 | -1.2657e-14 | 0.58529 | 0.22297 | 0.0034143 |
| MATICUSDT | breakout | 0.043264 | -1.1222 | 1.2087 | 0.055235 | -0.012901 | -0.10539 | 0.024264 | 1.4241e-14 | 0.13384 | 0.18848 | -0.022469 |
| FTMUSDT | breakout | 1.0703 | -0.096436 | 2.2371 | 0.0098994 | -0.035069 | -0.0099197 | 0.004715 | 1.1205e-16 | 2.8832 | -0.035411 | -0.0055192 |
| LTCUSDT | breakout | 0.2111 | -0.71386 | 1.1361 | -0.0014541 | -0.0030189 | -0.025186 | 0.008393 | -7.0666e-16 | 0.89658 | 0.030745 | -0.022441 |
| LINKUSDT | breakout | -0.29976 | -1.1144 | 0.51486 | 0.030077 | -0.043942 | -0.0033902 | 0.0050235 | -7.4944e-15 | -0.94938 | 0.015528 | 0.01053 |
| SOLUSDT | equal | 1.5815 | 0.020897 | 3.1421 | 0.077811 | 0.025751 | -0.14905 | 0.017118 | 6.2073e-15 | 3.505 | 0.52855 | 0.00087981 |
| XRPUSDT | equal | -0.20185 | -1.4605 | 1.0568 | 0.14875 | -0.04663 | -0.15494 | 0.091649 | 1.3276e-14 | -0.60905 | 0.015988 | 0.042393 |
| BNBUSDT | equal | 0.51877 | -0.33338 | 1.3709 | 0.11022 | -0.069111 | -0.049179 | 0.027524 | -2.2555e-14 | 1.9444 | 0.0022995 | 0.016994 |
| DOTUSDT | equal | -0.21039 | -1.5223 | 1.1015 | 0.24415 | -0.073834 | -0.28216 | 0.094729 | 4.1315e-14 | -0.59069 | 0.2181 | -0.01787 |
| DOGEUSDT | equal | 1.5003 | 0.02893 | 2.9717 | 0.35543 | -0.13403 | -0.28093 | 0.249 | -5.17e-14 | 3.9259 | 0.35899 | 0.13716 |
| ADAUSDT | equal | -0.38238 | -1.6816 | 0.91681 | 0.27707 | -0.079805 | -0.29103 | 0.11973 | 7.9591e-15 | -1.1123 | 0.36802 | 0.013081 |
| AVAXUSDT | equal | 0.3824 | -0.80284 | 1.5676 | 0.22543 | -0.11422 | -0.25101 | 0.085694 | 1.993e-15 | 0.95875 | 0.47918 | 0.013883 |
| AXSUSDT | equal | 1.1281 | -0.37365 | 2.6298 | 0.1912 | -0.15293 | -0.25432 | 0.11757 | -1.9034e-14 | 2.7232 | 0.35098 | -0.020393 |
| MATICUSDT | equal | 1.1337 | -0.21281 | 2.4802 | 0.14399 | -0.072657 | -0.17987 | 0.061652 | 3.2672e-14 | 3.0039 | 0.18555 | -0.0096669 |
| FTMUSDT | equal | 2.0146 | 0.36656 | 3.6626 | 0.19118 | -0.096784 | -0.21783 | 0.073018 | -1.8872e-14 | 4.0724 | 0.48252 | 0.050001 |
| LTCUSDT | equal | 0.2492 | -0.80508 | 1.3035 | 0.1426 | -0.1113 | -0.061562 | 0.051459 | -4.9943e-14 | 0.78971 | -0.10654 | 0.042552 |
| LINKUSDT | equal | 0.55858 | -0.7979 | 1.9151 | 0.25804 | -0.18716 | -0.19657 | 0.13416 | -4.4381e-14 | 1.4591 | -0.15114 | 0.048973 |
| SOLUSDT | inverse_vol | 0.98069 | -0.19032 | 2.1517 | 0.047503 | 0.029921 | -0.087099 | 0.01074 | 4.242e-15 | 3.0004 | 0.27894 | 0.0078392 |
| XRPUSDT | inverse_vol | 0.22658 | -0.62877 | 1.0819 | 0.033981 | -0.011865 | -0.092305 | 0.064374 | 5.2859e-15 | 1.0449 | 0.0043971 | -0.024503 |
| BNBUSDT | inverse_vol | 0.049863 | -0.53588 | 0.6356 | 0.047736 | -0.04441 | -0.00027456 | 0.014098 | -1.5232e-14 | 0.2977 | -0.018333 | 0.018312 |
| DOTUSDT | inverse_vol | -0.35268 | -1.4359 | 0.73056 | 0.060526 | -0.017718 | -0.11614 | 0.044259 | 1.2079e-14 | -1.3515 | 0.078916 | -0.04098 |
| DOGEUSDT | inverse_vol | 1.4243 | -0.050537 | 2.8991 | 0.18715 | -0.085391 | -0.17655 | 0.14642 | -3.2969e-14 | 4.8175 | 0.36175 | 0.049477 |
| ADAUSDT | inverse_vol | -0.039087 | -1.296 | 1.2179 | 0.14153 | -0.0086161 | -0.17392 | 0.057886 | 6.6794e-15 | -0.14944 | 0.27884 | 0.0017915 |
| AVAXUSDT | inverse_vol | 0.012652 | -1.1255 | 1.1508 | 0.13702 | -0.023128 | -0.18409 | 0.048246 | -1.3192e-15 | 0.039255 | 0.38892 | 0.0061486 |
| AXSUSDT | inverse_vol | 0.6018 | -0.76022 | 1.9638 | 0.15241 | -0.059182 | -0.22715 | 0.10077 | -2.1315e-14 | 1.8565 | 0.33609 | -0.0087688 |
| MATICUSDT | inverse_vol | 0.57371 | -0.54442 | 1.6918 | 0.10172 | -0.045147 | -0.12589 | 0.048718 | 2.7011e-14 | 1.9887 | 0.25039 | -0.0034682 |
| FTMUSDT | inverse_vol | 1.8349 | 0.66315 | 3.0067 | 0.040156 | -0.063509 | -0.059467 | 0.024598 | -7.0351e-15 | 5.3714 | 0.30724 | -0.0092197 |
| LTCUSDT | inverse_vol | 0.017899 | -0.83889 | 0.87469 | 0.014685 | -0.012543 | -0.038141 | 0.013479 | -6.903e-15 | 0.080041 | -0.054803 | -0.020713 |
| LINKUSDT | inverse_vol | 0.16406 | -0.7993 | 1.1274 | 0.09666 | -0.08606 | -0.081339 | 0.047832 | -2.3676e-14 | 0.57565 | -0.11363 | 0.0069125 |

## Cross-asset inference

{
  "14": {
    "median_alpha_ci95": [
      -0.24046824050188734,
      1.3859864160301694
    ],
    "median_sharpe_ci95": [
      -0.14352852144749192,
      1.417801450789342
    ],
    "positive_fraction_ci95": [
      0.4166666666666667,
      1.0
    ],
    "note": "Common calendar blocks across all assets; factor exposures estimated on full sample, paired return/factor bootstrap with coefficients re-estimated in each common time resample"
  },
  "30": {
    "median_alpha_ci95": [
      -0.2140965903209162,
      1.4201866145052022
    ],
    "median_sharpe_ci95": [
      -0.12945674452285746,
      1.4279139089142692
    ],
    "positive_fraction_ci95": [
      0.4166666666666667,
      1.0
    ],
    "note": "Common calendar blocks across all assets; factor exposures estimated on full sample, paired return/factor bootstrap with coefficients re-estimated in each common time resample"
  },
  "60": {
    "median_alpha_ci95": [
      -0.18590697546308096,
      1.3368954484932236
    ],
    "median_sharpe_ci95": [
      -0.1237858661924557,
      1.3809603931703283
    ],
    "positive_fraction_ci95": [
      0.4166666666666667,
      1.0
    ],
    "note": "Common calendar blocks across all assets; factor exposures estimated on full sample, paired return/factor bootstrap with coefficients re-estimated in each common time resample"
  },
  "asset_bootstrap_descriptive": [
    0.023675975194885346,
    1.3170047551257427
  ],
  "heterogeneity": {
    "alpha_std": 0.7796389595510118,
    "alpha_iqr": 1.0889068550110719,
    "alpha_min": -0.3823779253528958,
    "alpha_max": 2.0145687171200883,
    "random_effects": "Not used: correlated crypto units violate independent-effect sampling assumptions"
  }
}

Common dates are resampled together and regressions are refitted within each resample. Asset-only bootstrap is descriptive because names are dependent. Random-effects pooling is omitted because independent-effect assumptions are inappropriate. Component analyses are supporting evidence; no unadjusted component significance claim is used for promotion.
