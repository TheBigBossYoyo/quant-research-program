# Phase4 factor analysis

Daily net returns regressed on underlying return, BTC, equal-weight replication market, lagged30-day BTC volatility and lagged200-day BTC trend sign. HAC14-day95% intervals. The market includes the tested name; common factors are correlated and coefficients can be unstable. Volatility and trend are state controls, not necessarily tradable factor portfolios. The intercept is conditional and depends on this specification. No claim of causal alpha. OLS residual Sharpe is approximately zero by construction; factor-adjusted Sharpe retains the fitted intercept. The asset-only regression is reported alongside the richer model.

| asset | component | alpha | alpha_ci_low | alpha_ci_high | asset_beta | btc_beta | market_beta | r_squared | residual_sharpe | factor_adjusted_sharpe | univariate_alpha | univariate_beta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SOLUSDT | trend | 2.0534 | -0.91537 | 5.0222 | 0.13505 | -0.036433 | -0.26756 | 0.023306 | -1.075e-14 | 2.4979 | 0.88699 | -0.033354 |
| XRPUSDT | trend | -0.58407 | -2.755 | 1.5868 | 0.29664 | -0.081406 | -0.27414 | 0.098398 | -1.6347e-14 | -0.97261 | -0.0019664 | 0.10808 |
| BNBUSDT | trend | 1.2632 | -0.29774 | 2.8241 | 0.21975 | -0.1049 | -0.12565 | 0.034727 | -1.1142e-14 | 2.6528 | -0.018237 | 0.028144 |
| DOTUSDT | trend | -0.44313 | -2.4063 | 1.52 | 0.49995 | -0.15256 | -0.54401 | 0.11746 | 8.4445e-14 | -0.72136 | 0.42301 | -0.011402 |
| DOGEUSDT | trend | 2.1445 | -0.23577 | 4.5247 | 0.69195 | -0.24338 | -0.5217 | 0.28485 | -1.2978e-14 | 3.1727 | 0.45492 | 0.28805 |
| ADAUSDT | trend | -0.5786 | -2.7713 | 1.6141 | 0.42844 | -0.15896 | -0.47977 | 0.1089 | -7.1984e-15 | -0.92334 | 0.46156 | -0.020289 |
| AVAXUSDT | trend | 1.3275 | -0.77186 | 3.4269 | 0.40135 | -0.25193 | -0.39744 | 0.086617 | -2.8473e-14 | 1.8775 | 0.69183 | 0.036974 |
| AXSUSDT | trend | 2.0399 | -0.30456 | 4.3844 | 0.28069 | -0.29288 | -0.35579 | 0.10236 | -1.0755e-14 | 2.8392 | 0.47899 | -0.0442 |
| MATICUSDT | trend | 2.2116 | 0.062709 | 4.3605 | 0.23908 | -0.12016 | -0.27003 | 0.051874 | -2.11e-14 | 3.4342 | 0.18261 | 0.0031356 |
| FTMUSDT | trend | 2.4396 | -0.67701 | 5.5562 | 0.34699 | -0.21006 | -0.40215 | 0.077861 | -2.5423e-14 | 2.7865 | 1.124 | 0.075733 |
| LTCUSDT | trend | 0.21773 | -1.7707 | 2.2062 | 0.27678 | -0.29207 | -0.067926 | 0.064374 | 2.8247e-14 | 0.37381 | -0.3318 | 0.085139 |
| LINKUSDT | trend | 1.4116 | -1.0227 | 3.8458 | 0.49208 | -0.31704 | -0.40507 | 0.14969 | 1.6405e-14 | 2.0876 | -0.31781 | 0.087415 |
| SOLUSDT | breakout | 0.63491 | -0.39363 | 1.6635 | 0.025026 | 0.033617 | -0.032732 | 0.0060269 | -4.3222e-15 | 1.9892 | 0.061017 | 0.018342 |
| XRPUSDT | breakout | 0.37074 | -0.58678 | 1.3283 | -0.0033525 | -0.016345 | -0.036372 | 0.0295 | -1.888e-15 | 1.7211 | -0.060967 | -0.030511 |
| BNBUSDT | breakout | -0.23022 | -0.72352 | 0.26309 | 0.0042689 | -0.027328 | 0.020007 | 0.0039605 | -8.5097e-16 | -1.3351 | 0.022836 | 0.0058448 |
| DOTUSDT | breakout | 0.017078 | -1.2238 | 1.2579 | -0.0065518 | 0.016712 | -0.032128 | 0.0060859 | -2.4764e-15 | 0.059418 | 0.013199 | -0.024338 |
| DOGEUSDT | breakout | 0.84984 | -0.3326 | 2.0323 | 0.019734 | -0.012261 | -0.048567 | 0.012203 | -2.0352e-15 | 2.9701 | 0.26306 | -0.013739 |
| ADAUSDT | breakout | -0.19988 | -1.648 | 1.2482 | 0.13511 | 0.014776 | -0.12145 | 0.037925 | -1.2487e-15 | -0.69238 | 0.27448 | 0.04645 |
| AVAXUSDT | breakout | -0.56453 | -1.9172 | 0.78814 | 0.051308 | 0.031322 | -0.11048 | 0.011498 | -1.0509e-14 | -1.6046 | 0.26653 | -0.0092076 |
| AXSUSDT | breakout | 0.21771 | -1.1303 | 1.5658 | 0.10706 | 0.00080471 | -0.16783 | 0.032571 | -1.2025e-14 | 0.58696 | 0.22297 | 0.0034143 |
| MATICUSDT | breakout | 0.043873 | -1.1221 | 1.2099 | 0.0552 | -0.011962 | -0.10553 | 0.024133 | -9.5503e-15 | 0.13572 | 0.18848 | -0.022469 |
| FTMUSDT | breakout | 1.0705 | -0.095939 | 2.237 | 0.010285 | -0.035748 | -0.0099425 | 0.004743 | -1.1952e-15 | 2.8838 | -0.035408 | -0.0054888 |
| LTCUSDT | breakout | 0.21192 | -0.71339 | 1.1372 | -0.0011722 | -0.0029236 | -0.025327 | 0.0083487 | -7.8518e-16 | 0.90008 | 0.030799 | -0.022288 |
| LINKUSDT | breakout | -0.29953 | -1.1142 | 0.51515 | 0.029894 | -0.044197 | -0.0029639 | 0.0050207 | 2.9275e-15 | -0.94864 | 0.015528 | 0.01053 |
| SOLUSDT | equal | 1.3442 | -0.24172 | 2.93 | 0.080037 | -0.0014079 | -0.15015 | 0.019555 | -8.5109e-15 | 2.919 | 0.474 | -0.0075059 |
| XRPUSDT | equal | -0.10666 | -1.3566 | 1.1433 | 0.14665 | -0.048875 | -0.15526 | 0.08973 | -1.4541e-14 | -0.31839 | -0.031467 | 0.038783 |
| BNBUSDT | equal | 0.51649 | -0.33567 | 1.3687 | 0.11201 | -0.066114 | -0.052819 | 0.028152 | -1.2234e-14 | 1.9365 | 0.0022995 | 0.016994 |
| DOTUSDT | equal | -0.21303 | -1.5246 | 1.0985 | 0.2467 | -0.067926 | -0.28807 | 0.096028 | 7.1367e-14 | -0.59852 | 0.2181 | -0.01787 |
| DOGEUSDT | equal | 1.4972 | 0.026038 | 2.9683 | 0.35584 | -0.12782 | -0.28513 | 0.25028 | -1.346e-14 | 3.921 | 0.35899 | 0.13716 |
| ADAUSDT | equal | -0.38924 | -1.6887 | 0.91023 | 0.28177 | -0.07209 | -0.30061 | 0.12242 | -8.456e-15 | -1.134 | 0.36802 | 0.013081 |
| AVAXUSDT | equal | 0.38149 | -0.80398 | 1.567 | 0.22633 | -0.1103 | -0.25396 | 0.086024 | -3.0365e-14 | 0.95665 | 0.47918 | 0.013883 |
| AXSUSDT | equal | 1.1288 | -0.37263 | 2.6303 | 0.19388 | -0.14604 | -0.26181 | 0.11893 | -1.4806e-14 | 2.7271 | 0.35098 | -0.020393 |
| MATICUSDT | equal | 1.1277 | -0.21866 | 2.4741 | 0.14714 | -0.066063 | -0.18778 | 0.063312 | -1.9415e-14 | 2.9908 | 0.18555 | -0.0096669 |
| FTMUSDT | equal | 1.7551 | 0.0361 | 3.474 | 0.17864 | -0.1229 | -0.20605 | 0.066903 | -2.321e-14 | 3.481 | 0.54429 | 0.035122 |
| LTCUSDT | equal | 0.21483 | -0.842 | 1.2717 | 0.1378 | -0.14749 | -0.046626 | 0.055927 | 2.1075e-14 | 0.6719 | -0.1505 | 0.031425 |
| LINKUSDT | equal | 0.55602 | -0.7999 | 1.9119 | 0.26099 | -0.18062 | -0.20402 | 0.13554 | 1.3484e-14 | 1.4536 | -0.15114 | 0.048973 |
| SOLUSDT | inverse_vol | 0.88306 | -0.30003 | 2.0662 | 0.048664 | 0.02015 | -0.083799 | 0.010363 | -1.0321e-14 | 2.672 | 0.22877 | 0.0074753 |
| XRPUSDT | inverse_vol | 0.26068 | -0.58211 | 1.1035 | 0.032705 | -0.012862 | -0.089442 | 0.062006 | -6.8229e-15 | 1.1951 | -0.027316 | -0.024658 |
| BNBUSDT | inverse_vol | 0.050334 | -0.5355 | 0.63617 | 0.047411 | -0.044877 | 0.00037517 | 0.014099 | -7.5606e-15 | 0.30051 | -0.018333 | 0.018312 |
| DOTUSDT | inverse_vol | -0.35124 | -1.4339 | 0.73147 | 0.059461 | -0.017248 | -0.11481 | 0.04379 | 2.1849e-14 | -1.3456 | 0.078916 | -0.04098 |
| DOGEUSDT | inverse_vol | 1.4256 | -0.049576 | 2.9009 | 0.18667 | -0.083655 | -0.17647 | 0.14603 | -1.1737e-14 | 4.821 | 0.36175 | 0.049477 |
| ADAUSDT | inverse_vol | -0.039196 | -1.2949 | 1.2165 | 0.14208 | -0.0063868 | -0.17535 | 0.057867 | -3.4633e-15 | -0.14986 | 0.27884 | 0.0017915 |
| AVAXUSDT | inverse_vol | 0.01271 | -1.1258 | 1.1512 | 0.13729 | -0.020738 | -0.18537 | 0.048262 | -2.3803e-14 | 0.039434 | 0.38892 | 0.0061486 |
| AXSUSDT | inverse_vol | 0.60296 | -0.75909 | 1.965 | 0.15196 | -0.057738 | -0.2265 | 0.099894 | -1.4279e-14 | 1.8592 | 0.33609 | -0.0087688 |
| MATICUSDT | inverse_vol | 0.57488 | -0.54363 | 1.6934 | 0.10147 | -0.044341 | -0.12556 | 0.048345 | -1.6466e-14 | 1.9924 | 0.25039 | -0.0034682 |
| FTMUSDT | inverse_vol | 1.6249 | 0.43407 | 2.8157 | 0.034905 | -0.071639 | -0.051728 | 0.02366 | -1.1397e-14 | 4.7028 | 0.3208 | -0.013182 |
| LTCUSDT | inverse_vol | -0.016878 | -0.87583 | 0.84207 | 0.010543 | -0.026285 | -0.028289 | 0.015784 | 1.131e-16 | -0.075097 | -0.096267 | -0.023864 |
| LINKUSDT | inverse_vol | 0.16478 | -0.79853 | 1.1281 | 0.096375 | -0.085715 | -0.080856 | 0.04763 | 4.8644e-15 | 0.57811 | -0.11363 | 0.0069125 |

## Cross-asset inference

{
  "14": {
    "median_alpha_ci95": [
      -0.26051980048127915,
      1.3645047042125735
    ],
    "median_sharpe_ci95": [
      -0.1498252128289596,
      1.3982592808229095
    ],
    "positive_fraction_ci95": [
      0.4166666666666667,
      1.0
    ],
    "note": "Common calendar blocks across all assets; factor exposures estimated on full sample, paired return/factor bootstrap with coefficients re-estimated in each common time resample"
  },
  "30": {
    "median_alpha_ci95": [
      -0.2487761400978062,
      1.389174966033407
    ],
    "median_sharpe_ci95": [
      -0.12925047023476802,
      1.415031190398548
    ],
    "positive_fraction_ci95": [
      0.4166666666666667,
      1.0
    ],
    "note": "Common calendar blocks across all assets; factor exposures estimated on full sample, paired return/factor bootstrap with coefficients re-estimated in each common time resample"
  },
  "60": {
    "median_alpha_ci95": [
      -0.24142486803869975,
      1.3057806386990085
    ],
    "median_sharpe_ci95": [
      -0.1237858661924557,
      1.3797082644205756
    ],
    "positive_fraction_ci95": [
      0.4166666666666667,
      1.0
    ],
    "note": "Common calendar blocks across all assets; factor exposures estimated on full sample, paired return/factor bootstrap with coefficients re-estimated in each common time resample"
  },
  "asset_bootstrap_descriptive": [
    0.05408253306842707,
    1.236486469976199
  ],
  "heterogeneity": {
    "alpha_std": 0.7111883750776835,
    "alpha_iqr": 1.0481942610147619,
    "alpha_min": -0.38924176997025867,
    "alpha_max": 1.7550552353066216,
    "random_effects": "Not used: correlated crypto units violate independent-effect sampling assumptions"
  }
}

Common dates are resampled together and regressions are refitted within each resample. Asset-only bootstrap is descriptive because names are dependent. Random-effects pooling is omitted because independent-effect assumptions are inappropriate. Component analyses are supporting evidence; no unadjusted component significance claim is used for promotion.
