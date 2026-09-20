# Phase 4 replication tables (frozen E040, stress cost case 9.05 bps per side plus funding, 2022-2024)

Source replication: E044_20260909T135755. Analysis: E045_20260909T140237. All twelve preregistered assets are shown for every component; losing assets are not omitted. BTC/ETH are discovery comparators, never part of replication statistics.

Exposure columns are hourly-event |position notional / equity| from the simulated paths (2022-2024): p50/p90/p99/max and the share of hours above 1x. E040 targets about 1x when it resizes but can drift above 1x between resize events; there is no hard cap.

## Slow-trend component

### Performance

| asset | component | total_net_return | cagr | sharpe | sortino | calmar | max_dd | drawdown_duration_days | profit_factor | trades | win_rate | average_win | average_loss | payoff_ratio | expectancy | average_holding_hours |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | trend | 1.059 | 0.2719 | 0.69 | 1.07 | 0.4043 | -0.6725 | 643 | 1.613 | 151 | 0.1325 | 0.1937 | -0.01584 | 12.22 | 0.01191 | 174.2 |
| AVAXUSDT | trend | 2.59 | 0.5307 | 0.9395 | 1.498 | 0.8264 | -0.6422 | 369 | 1.799 | 152 | 0.125 | 0.277 | -0.01665 | 16.63 | 0.02005 | 173 |
| AXSUSDT | trend | 0.9245 | 0.2436 | 0.6551 | 1.054 | 0.483 | -0.5044 | 372 | 1.286 | 133 | 0.1353 | 0.1707 | -0.0171 | 9.98 | 0.008312 | 197.7 |
| BNBUSDT | trend | -0.316 | -0.1188 | -0.02165 | -0.03319 | -0.2006 | -0.5922 | 874 | 0.8191 | 220 | 0.08182 | 0.105 | -0.009829 | 10.69 | -0.0004318 | 119.5 |
| DOGEUSDT | trend | 1.673 | 0.3874 | 0.7942 | 1.316 | 0.6559 | -0.5907 | 488 | 1.973 | 121 | 0.157 | 0.2418 | -0.02092 | 11.56 | 0.02034 | 217.3 |
| DOTUSDT | trend | 0.9057 | 0.2396 | 0.6496 | 1.025 | 0.5223 | -0.4586 | 518 | 1.413 | 131 | 0.1145 | 0.2059 | -0.01624 | 12.68 | 0.009193 | 200.8 |
| FTMUSDT | trend | 8.014 | 1.08 | 1.254 | 1.996 | 1.746 | -0.6183 | 320 | 1.826 | 112 | 0.1429 | 0.3982 | -0.02684 | 14.83 | 0.03387 | 234.8 |
| LINKUSDT | trend | -0.8069 | -0.4217 | -0.3876 | -0.5906 | -0.4637 | -0.9095 | 949 | 0.4743 | 195 | 0.08718 | 0.1464 | -0.02003 | 7.306 | -0.005527 | 134.8 |
| LTCUSDT | trend | -0.7756 | -0.3921 | -0.5269 | -0.7778 | -0.4418 | -0.8873 | 932 | 0.5007 | 195 | 0.07692 | 0.107 | -0.01578 | 6.783 | -0.006333 | 134.9 |
| MATICUSDT | trend | -0.09788 | -0.03372 | 0.275 | 0.4168 | -0.05204 | -0.648 | 871 | 0.9518 | 138 | 0.1159 | 0.1716 | -0.01984 | 8.65 | 0.002357 | 169.9 |
| SOLUSDT | trend | 4.027 | 0.7122 | 1.043 | 1.785 | 1.159 | -0.6148 | 496 | 1.858 | 157 | 0.121 | 0.3031 | -0.01597 | 18.99 | 0.02265 | 167.5 |
| XRPUSDT | trend | -0.3136 | -0.1178 | 0.1085 | 0.1777 | -0.1391 | -0.8471 | 1074 | 0.8128 | 209 | 0.08134 | 0.2268 | -0.0143 | 15.86 | 0.00531 | 125.8 |

### Turnover, exposure and tails

| asset | component | annual_turnover | annual_transaction_cost | net_funding_usdt | gross_exposure | net_exposure | exposure_p50 | exposure_p90 | exposure_p99 | exposure_max | exposure_share_above_1x | exposure_time_in_market | expected_shortfall_95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | trend | 89.35 | 0.08086 | 1365 | 0.7342 | -0.1365 | 0.7624 | 1.008 | 1.068 | 1.526 | 0.2856 | 0.9998 | -0.07502 |
| AVAXUSDT | trend | 85.05 | 0.07697 | 4016 | 0.7075 | -0.05904 | 0.7326 | 1.007 | 1.044 | 1.264 | 0.2749 | 0.9997 | -0.07976 |
| AXSUSDT | trend | 88.51 | 0.0801 | 6658 | 0.7112 | -0.1733 | 0.7214 | 1.003 | 1.106 | 1.511 | 0.2038 | 0.9998 | -0.08355 |
| BNBUSDT | trend | 113.7 | 0.1029 | 323 | 0.7157 | 0.05301 | 0.7197 | 1.002 | 1.037 | 1.207 | 0.2323 | 0.9998 | -0.05582 |
| DOGEUSDT | trend | 88.69 | 0.08026 | 1575 | 0.773 | -0.07383 | 0.8566 | 1.012 | 1.119 | 1.731 | 0.3504 | 0.9998 | -0.08651 |
| DOTUSDT | trend | 85.54 | 0.07741 | 2485 | 0.7477 | -0.1941 | 0.7872 | 1.006 | 1.064 | 1.194 | 0.2482 | 0.9998 | -0.07155 |
| FTMUSDT | trend | 68.96 | 0.06241 | 6746 | 0.7545 | -0.06652 | 0.7772 | 1.012 | 1.185 | 1.58 | 0.3328 | 0.9998 | -0.09931 |
| LINKUSDT | trend | 112.3 | 0.1016 | 282.3 | 0.7307 | 0.009892 | 0.7294 | 1.005 | 1.095 | 1.365 | 0.3 | 0.9997 | -0.08081 |
| LTCUSDT | trend | 108.3 | 0.09802 | 494.3 | 0.7253 | 0.003949 | 0.7227 | 1.006 | 1.074 | 1.262 | 0.3269 | 0.9998 | -0.07067 |
| MATICUSDT | trend | 79.69 | 0.07212 | 963.9 | 0.6321 | -0.1436 | 0.7214 | 1.008 | 1.119 | 1.359 | 0.2373 | 0.9998 | -0.07753 |
| SOLUSDT | trend | 96.6 | 0.08742 | 9093 | 0.7172 | 0.03515 | 0.739 | 1.008 | 1.098 | 1.332 | 0.3154 | 0.9998 | -0.08271 |
| XRPUSDT | trend | 105.2 | 0.0952 | 472 | 0.7257 | -0.05111 | 0.7328 | 1.005 | 1.061 | 1.666 | 0.2745 | 0.9998 | -0.06873 |

### Factor regression (daily; underlying, BTC, replication market, lagged BTC vol, lagged BTC trend; HAC 14)

| asset | component | asset_beta | btc_beta | market_beta | alpha | alpha_ci_low | alpha_ci_high | r_squared | factor_adjusted_sharpe | univariate_alpha | univariate_beta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | trend | 0.4284 | -0.159 | -0.4798 | -0.5786 | -2.771 | 1.614 | 0.1089 | -0.9233 | 0.4616 | -0.02029 |
| AVAXUSDT | trend | 0.4013 | -0.2519 | -0.3974 | 1.328 | -0.7719 | 3.427 | 0.08662 | 1.878 | 0.6918 | 0.03697 |
| AXSUSDT | trend | 0.2807 | -0.2929 | -0.3558 | 2.04 | -0.3046 | 4.384 | 0.1024 | 2.839 | 0.479 | -0.0442 |
| BNBUSDT | trend | 0.2198 | -0.1049 | -0.1256 | 1.263 | -0.2977 | 2.824 | 0.03473 | 2.653 | -0.01824 | 0.02814 |
| DOGEUSDT | trend | 0.6919 | -0.2434 | -0.5217 | 2.144 | -0.2358 | 4.525 | 0.2848 | 3.173 | 0.4549 | 0.2881 |
| DOTUSDT | trend | 0.5 | -0.1526 | -0.544 | -0.4431 | -2.406 | 1.52 | 0.1175 | -0.7214 | 0.423 | -0.0114 |
| FTMUSDT | trend | 0.347 | -0.2101 | -0.4021 | 2.44 | -0.677 | 5.556 | 0.07786 | 2.786 | 1.124 | 0.07573 |
| LINKUSDT | trend | 0.4921 | -0.317 | -0.4051 | 1.412 | -1.023 | 3.846 | 0.1497 | 2.088 | -0.3178 | 0.08742 |
| LTCUSDT | trend | 0.2768 | -0.2921 | -0.06793 | 0.2177 | -1.771 | 2.206 | 0.06437 | 0.3738 | -0.3318 | 0.08514 |
| MATICUSDT | trend | 0.2391 | -0.1202 | -0.27 | 2.212 | 0.06271 | 4.36 | 0.05187 | 3.434 | 0.1826 | 0.003136 |
| SOLUSDT | trend | 0.135 | -0.03643 | -0.2676 | 2.053 | -0.9154 | 5.022 | 0.02331 | 2.498 | 0.887 | -0.03335 |
| XRPUSDT | trend | 0.2966 | -0.08141 | -0.2741 | -0.5841 | -2.755 | 1.587 | 0.0984 | -0.9726 | -0.001966 | 0.1081 |

### Concentration

| asset | component | top1_trade_positive_pnl_share | top5_trade_positive_pnl_share | top10_trade_positive_pnl_share | top_month_positive_pnl_share | top_quarter_positive_pnl_share | top_year_positive_pnl_share |
|---|---|---|---|---|---|---|---|
| ADAUSDT | trend | 0.4379 | 0.8293 | 0.962 | 0.4741 | 0.4995 | 0.6282 |
| AVAXUSDT | trend | 0.3934 | 0.7685 | 0.9248 | 0.2442 | 0.6129 | 0.858 |
| AXSUSDT | trend | 0.1658 | 0.5746 | 0.8696 | 0.151 | 0.5129 | 0.6141 |
| BNBUSDT | trend | 0.3224 | 0.7986 | 0.971 | 0.2596 | 0.5788 | n/a |
| DOGEUSDT | trend | 0.488 | 0.8487 | 0.9651 | 0.4241 | 0.6292 | 0.9567 |
| DOTUSDT | trend | 0.228 | 0.7348 | 0.9428 | 0.2707 | 0.366 | 0.6335 |
| FTMUSDT | trend | 0.2005 | 0.6413 | 0.9114 | 0.2707 | 0.3657 | 0.5586 |
| LINKUSDT | trend | 0.3067 | 0.828 | 0.9622 | 0.174 | 0.4203 | n/a |
| LTCUSDT | trend | 0.4317 | 0.8851 | 0.9991 | 0.2035 | 0.8975 | n/a |
| MATICUSDT | trend | 0.1866 | 0.674 | 0.9029 | 0.2235 | 0.4111 | 1 |
| SOLUSDT | trend | 0.3558 | 0.8362 | 0.9773 | 0.2095 | 0.507 | 0.8524 |
| XRPUSDT | trend | 0.3747 | 0.8413 | 0.987 | 0.3456 | 0.5884 | 1 |

## Compression-breakout component

### Performance

| asset | component | total_net_return | cagr | sharpe | sortino | calmar | max_dd | drawdown_duration_days | profit_factor | trades | win_rate | average_win | average_loss | payoff_ratio | expectancy | average_holding_hours |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | breakout | 1.059 | 0.2719 | 0.96 | 1.837 | 2.015 | -0.1349 | 152 | 1.669 | 64 | 0.4375 | 0.06394 | -0.02603 | 2.457 | 0.01333 | 65.89 |
| AVAXUSDT | breakout | 0.8482 | 0.227 | 0.751 | 1.309 | 0.4815 | -0.4714 | 751 | 1.556 | 69 | 0.4783 | 0.06671 | -0.03965 | 1.683 | 0.01122 | 71.39 |
| AXSUSDT | breakout | 0.583 | 0.1653 | 0.5876 | 1.067 | 0.6256 | -0.2642 | 401 | 1.266 | 71 | 0.3662 | 0.08174 | -0.03329 | 2.455 | 0.008833 | 73.04 |
| BNBUSDT | breakout | 0.02974 | 0.009809 | 0.1415 | 0.2351 | 0.05294 | -0.1853 | 896 | 1.042 | 54 | 0.3889 | 0.03397 | -0.01989 | 1.708 | 0.001057 | 62.17 |
| DOGEUSDT | breakout | 0.9041 | 0.2392 | 0.8839 | 1.72 | 1.582 | -0.1512 | 229 | 1.81 | 53 | 0.5094 | 0.05593 | -0.02994 | 1.868 | 0.0138 | 57.75 |
| DOTUSDT | breakout | -0.06949 | -0.0237 | 0.05882 | 0.09168 | -0.05643 | -0.42 | 1072 | 0.9553 | 68 | 0.3824 | 0.05985 | -0.03593 | 1.666 | 0.0006937 | 73.49 |
| FTMUSDT | breakout | -0.2692 | -0.09918 | -0.09885 | -0.1577 | -0.2102 | -0.472 | 1092 | 0.8111 | 60 | 0.35 | 0.06776 | -0.0414 | 1.637 | -0.003193 | 66.75 |
| LINKUSDT | breakout | -0.08508 | -0.02918 | 0.06184 | 0.098 | -0.05474 | -0.533 | 1044 | 0.9281 | 61 | 0.4262 | 0.05525 | -0.04024 | 1.373 | 0.000461 | 73.11 |
| LTCUSDT | breakout | -0.001775 | -0.0005915 | 0.1142 | 0.1806 | -0.001767 | -0.3348 | 1044 | 0.9981 | 50 | 0.36 | 0.05474 | -0.02856 | 1.917 | 0.00143 | 66.74 |
| MATICUSDT | breakout | 0.5303 | 0.1522 | 0.5921 | 1.058 | 0.34 | -0.4477 | 928 | 1.349 | 58 | 0.3966 | 0.08442 | -0.0379 | 2.227 | 0.0106 | 74.5 |
| SOLUSDT | breakout | 0.06543 | 0.02133 | 0.2242 | 0.3451 | 0.06896 | -0.3093 | 606 | 1.05 | 56 | 0.375 | 0.07493 | -0.03975 | 1.885 | 0.003256 | 68.21 |
| XRPUSDT | breakout | -0.2686 | -0.09894 | -0.37 | -0.6086 | -0.2258 | -0.4382 | 1084 | 0.6821 | 55 | 0.3818 | 0.03523 | -0.0295 | 1.194 | -0.004785 | 53.4 |

### Turnover, exposure and tails

| asset | component | annual_turnover | annual_transaction_cost | net_funding_usdt | gross_exposure | net_exposure | exposure_p50 | exposure_p90 | exposure_p99 | exposure_max | exposure_share_above_1x | exposure_time_in_market | expected_shortfall_95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | breakout | 42.13 | 0.03813 | 221.5 | 0.157 | 0.002001 | 0 | 0.9997 | 1.03 | 1.103 | 0.09059 | 0.1603 | -0.03218 |
| AVAXUSDT | breakout | 44.98 | 0.04071 | 189.7 | 0.1806 | 0.004638 | 0 | 1 | 1.042 | 1.113 | 0.09649 | 0.1873 | -0.04177 |
| AXSUSDT | breakout | 46.27 | 0.04187 | 1351 | 0.1887 | -0.0284 | 0 | 0.9986 | 1.031 | 1.144 | 0.05798 | 0.1972 | -0.04216 |
| BNBUSDT | breakout | 35.58 | 0.0322 | 75.65 | 0.125 | -0.003656 | 0 | 0.9613 | 1.014 | 1.074 | 0.03357 | 0.1276 | -0.02165 |
| DOGEUSDT | breakout | 34.43 | 0.03116 | 75.67 | 0.1131 | -0.01671 | 0 | 0.9041 | 1.018 | 1.152 | 0.05953 | 0.1164 | -0.03101 |
| DOTUSDT | breakout | 44.27 | 0.04007 | 273 | 0.1819 | -0.0164 | 0 | 0.9995 | 1.024 | 1.104 | 0.066 | 0.19 | -0.03754 |
| FTMUSDT | breakout | 39.06 | 0.03535 | 174.4 | 0.1486 | -0.01487 | 0 | 0.9848 | 1.037 | 1.187 | 0.07824 | 0.1523 | -0.04957 |
| LINKUSDT | breakout | 40.12 | 0.03631 | 101.1 | 0.1662 | -0.002259 | 0 | 1 | 1.041 | 1.14 | 0.1067 | 0.1696 | -0.04176 |
| LTCUSDT | breakout | 32.7 | 0.02959 | 10.91 | 0.122 | -0.0245 | 0 | 0.9343 | 1.026 | 1.129 | 0.07052 | 0.1269 | -0.03035 |
| MATICUSDT | breakout | 37.55 | 0.03398 | 235.9 | 0.1547 | -0.01675 | 0 | 0.9998 | 1.023 | 1.18 | 0.08859 | 0.1842 | -0.03773 |
| SOLUSDT | breakout | 36.6 | 0.03313 | 175.5 | 0.1406 | 0.002788 | 0 | 0.9811 | 1.022 | 1.129 | 0.07961 | 0.1452 | -0.04386 |
| XRPUSDT | breakout | 36.06 | 0.03263 | 34.19 | 0.1091 | -0.02092 | 0 | 0.9228 | 1.02 | 1.11 | 0.05767 | 0.1117 | -0.02779 |

### Factor regression (daily; underlying, BTC, replication market, lagged BTC vol, lagged BTC trend; HAC 14)

| asset | component | asset_beta | btc_beta | market_beta | alpha | alpha_ci_low | alpha_ci_high | r_squared | factor_adjusted_sharpe | univariate_alpha | univariate_beta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | breakout | 0.1351 | 0.01478 | -0.1214 | -0.1999 | -1.648 | 1.248 | 0.03792 | -0.6924 | 0.2745 | 0.04645 |
| AVAXUSDT | breakout | 0.05131 | 0.03132 | -0.1105 | -0.5645 | -1.917 | 0.7881 | 0.0115 | -1.605 | 0.2665 | -0.009208 |
| AXSUSDT | breakout | 0.1071 | 0.0008047 | -0.1678 | 0.2177 | -1.13 | 1.566 | 0.03257 | 0.587 | 0.223 | 0.003414 |
| BNBUSDT | breakout | 0.004269 | -0.02733 | 0.02001 | -0.2302 | -0.7235 | 0.2631 | 0.00396 | -1.335 | 0.02284 | 0.005845 |
| DOGEUSDT | breakout | 0.01973 | -0.01226 | -0.04857 | 0.8498 | -0.3326 | 2.032 | 0.0122 | 2.97 | 0.2631 | -0.01374 |
| DOTUSDT | breakout | -0.006552 | 0.01671 | -0.03213 | 0.01708 | -1.224 | 1.258 | 0.006086 | 0.05942 | 0.0132 | -0.02434 |
| FTMUSDT | breakout | 0.01028 | -0.03575 | -0.009943 | 1.071 | -0.09594 | 2.237 | 0.004743 | 2.884 | -0.03541 | -0.005489 |
| LINKUSDT | breakout | 0.02989 | -0.0442 | -0.002964 | -0.2995 | -1.114 | 0.5151 | 0.005021 | -0.9486 | 0.01553 | 0.01053 |
| LTCUSDT | breakout | -0.001172 | -0.002924 | -0.02533 | 0.2119 | -0.7134 | 1.137 | 0.008349 | 0.9001 | 0.0308 | -0.02229 |
| MATICUSDT | breakout | 0.0552 | -0.01196 | -0.1055 | 0.04387 | -1.122 | 1.21 | 0.02413 | 0.1357 | 0.1885 | -0.02247 |
| SOLUSDT | breakout | 0.02503 | 0.03362 | -0.03273 | 0.6349 | -0.3936 | 1.663 | 0.006027 | 1.989 | 0.06102 | 0.01834 |
| XRPUSDT | breakout | -0.003352 | -0.01634 | -0.03637 | 0.3707 | -0.5868 | 1.328 | 0.0295 | 1.721 | -0.06097 | -0.03051 |

### Concentration

| asset | component | top1_trade_positive_pnl_share | top5_trade_positive_pnl_share | top10_trade_positive_pnl_share | top_month_positive_pnl_share | top_quarter_positive_pnl_share | top_year_positive_pnl_share |
|---|---|---|---|---|---|---|---|
| ADAUSDT | breakout | 0.1303 | 0.5143 | 0.7384 | 0.1786 | 0.3169 | 0.4797 |
| AVAXUSDT | breakout | 0.152 | 0.4831 | 0.6956 | 0.355 | 0.4538 | 0.9766 |
| AXSUSDT | breakout | 0.1477 | 0.4501 | 0.6827 | 0.2432 | 0.3909 | 1 |
| BNBUSDT | breakout | 0.125 | 0.54 | 0.7979 | 0.2798 | 0.3456 | 1 |
| DOGEUSDT | breakout | 0.1347 | 0.4839 | 0.6708 | 0.1886 | 0.2513 | 0.5504 |
| DOTUSDT | breakout | 0.1846 | 0.5111 | 0.7436 | 0.2882 | 0.3306 | 0.9084 |
| FTMUSDT | breakout | 0.1652 | 0.5822 | 0.8401 | 0.2138 | 0.3438 | n/a |
| LINKUSDT | breakout | 0.1771 | 0.5574 | 0.7624 | 0.3946 | 0.5168 | 1 |
| LTCUSDT | breakout | 0.1762 | 0.7065 | 0.9009 | 0.2488 | 0.3579 | 1 |
| MATICUSDT | breakout | 0.1573 | 0.6114 | 0.839 | 0.249 | 0.3282 | 0.9481 |
| SOLUSDT | breakout | 0.118 | 0.4728 | 0.7636 | 0.2032 | 0.3539 | 1 |
| XRPUSDT | breakout | 0.2002 | 0.7079 | 0.8988 | 0.3103 | 0.8114 | 1 |

## Combined E040 (equal 50/50, primary)

### Performance

| asset | component | total_net_return | cagr | sharpe | sortino | calmar | max_dd | drawdown_duration_days | profit_factor | trades | win_rate | average_win | average_loss | payoff_ratio | expectancy | average_holding_hours |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | equal | 1.493 | 0.3555 | 1.011 | 1.689 | 0.9774 | -0.3637 | 555 | 1.766 | 215 | 0.2279 | 0.05411 | -0.00893 | 6.06 | 0.005438 | 141.9 |
| AVAXUSDT | equal | 2.267 | 0.4833 | 1.152 | 1.891 | 1.383 | -0.3495 | 455 | 1.934 | 221 | 0.2353 | 0.06533 | -0.01062 | 6.152 | 0.007252 | 141.3 |
| AXSUSDT | equal | 1.211 | 0.3024 | 0.8145 | 1.39 | 0.9046 | -0.3343 | 316 | 1.396 | 204 | 0.2157 | 0.06098 | -0.01059 | 5.761 | 0.00485 | 154.3 |
| BNBUSDT | equal | -0.08405 | -0.02881 | 0.02578 | 0.04041 | -0.0748 | -0.3852 | 874 | 0.9368 | 274 | 0.1423 | 0.03333 | -0.005564 | 5.99 | -2.841e-05 | 108.2 |
| DOGEUSDT | equal | 1.859 | 0.4189 | 1.008 | 1.749 | 1.19 | -0.3521 | 485 | 2.133 | 174 | 0.2644 | 0.0623 | -0.01115 | 5.586 | 0.008266 | 168.7 |
| DOTUSDT | equal | 0.5782 | 0.1641 | 0.59 | 0.973 | 0.5393 | -0.3043 | 518 | 1.299 | 199 | 0.2111 | 0.05469 | -0.01063 | 5.146 | 0.003157 | 157.3 |
| FTMUSDT | equal | 2.513 | 0.5196 | 1.06 | 1.712 | 1.17 | -0.444 | 324 | 1.619 | 172 | 0.2151 | 0.101 | -0.01508 | 6.7 | 0.009894 | 176.2 |
| LINKUSDT | equal | -0.4768 | -0.194 | -0.3216 | -0.5001 | -0.2891 | -0.6711 | 964 | 0.689 | 256 | 0.1758 | 0.04355 | -0.0115 | 3.786 | -0.001825 | 120.1 |
| LTCUSDT | equal | -0.4496 | -0.1804 | -0.4411 | -0.6741 | -0.275 | -0.6558 | 932 | 0.6925 | 245 | 0.1347 | 0.03962 | -0.008634 | 4.589 | -0.002134 | 121 |
| MATICUSDT | equal | 0.4042 | 0.1197 | 0.4821 | 0.7816 | 0.2742 | -0.4366 | 741 | 1.207 | 196 | 0.2092 | 0.05772 | -0.01193 | 4.839 | 0.002641 | 141.7 |
| SOLUSDT | equal | 1.985 | 0.4394 | 1.01 | 1.733 | 1.384 | -0.3175 | 266 | 1.686 | 213 | 0.1925 | 0.08286 | -0.01031 | 8.04 | 0.007627 | 141.4 |
| XRPUSDT | equal | -0.1809 | -0.06429 | -0.01747 | -0.0293 | -0.101 | -0.6363 | 1074 | 0.8688 | 264 | 0.1439 | 0.05326 | -0.008142 | 6.541 | 0.0006959 | 110.7 |

### Turnover, exposure and tails

| asset | component | annual_turnover | annual_transaction_cost | net_funding_usdt | gross_exposure | net_exposure | exposure_p50 | exposure_p90 | exposure_p99 | exposure_max | exposure_share_above_1x | exposure_time_in_market | expected_shortfall_95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | equal | 65.74 | 0.05949 | n/a | 0.4456 | -0.06723 | 0.4484 | 0.8123 | 1.013 | 1.263 | 0.02099 | 0.9998 | -0.03781 |
| AVAXUSDT | equal | 65.02 | 0.05884 | n/a | 0.444 | -0.0272 | 0.4434 | 0.7908 | 1.007 | 1.093 | 0.01787 | 0.9998 | -0.0442 |
| AXSUSDT | equal | 67.39 | 0.06099 | n/a | 0.4499 | -0.1009 | 0.4419 | 0.8533 | 1.038 | 1.179 | 0.02289 | 0.9998 | -0.04496 |
| BNBUSDT | equal | 74.63 | 0.06754 | n/a | 0.4203 | 0.02468 | 0.4218 | 0.6834 | 1.005 | 1.053 | 0.02627 | 0.9998 | -0.03025 |
| DOGEUSDT | equal | 61.56 | 0.05571 | n/a | 0.443 | -0.04527 | 0.4804 | 0.7053 | 1.002 | 1.365 | 0.01365 | 0.9998 | -0.04475 |
| DOTUSDT | equal | 64.9 | 0.05874 | n/a | 0.4648 | -0.1053 | 0.4661 | 0.854 | 1.007 | 1.07 | 0.01703 | 0.9998 | -0.03867 |
| FTMUSDT | equal | 54.01 | 0.04888 | n/a | 0.4515 | -0.0407 | 0.469 | 0.803 | 1.015 | 1.156 | 0.02205 | 0.9998 | -0.05662 |
| LINKUSDT | equal | 76.2 | 0.06896 | n/a | 0.4485 | 0.003817 | 0.4511 | 0.8501 | 1.022 | 1.14 | 0.02023 | 0.9997 | -0.04454 |
| LTCUSDT | equal | 70.5 | 0.06381 | n/a | 0.4237 | -0.01027 | 0.4475 | 0.7122 | 1 | 1.095 | 0.01095 | 0.9998 | -0.03695 |
| MATICUSDT | equal | 58.62 | 0.05305 | n/a | 0.3934 | -0.0802 | 0.4356 | 0.8382 | 1.013 | 1.128 | 0.01658 | 0.9998 | -0.0422 |
| SOLUSDT | equal | 66.6 | 0.06027 | n/a | 0.4289 | 0.01897 | 0.4618 | 0.7176 | 1.001 | 1.117 | 0.02315 | 0.9998 | -0.04674 |
| XRPUSDT | equal | 70.62 | 0.06391 | n/a | 0.4174 | -0.03601 | 0.4515 | 0.6827 | 1.005 | 1.114 | 0.01353 | 0.9998 | -0.03707 |

### Factor regression (daily; underlying, BTC, replication market, lagged BTC vol, lagged BTC trend; HAC 14)

| asset | component | asset_beta | btc_beta | market_beta | alpha | alpha_ci_low | alpha_ci_high | r_squared | factor_adjusted_sharpe | univariate_alpha | univariate_beta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | equal | 0.2818 | -0.07209 | -0.3006 | -0.3892 | -1.689 | 0.9102 | 0.1224 | -1.134 | 0.368 | 0.01308 |
| AVAXUSDT | equal | 0.2263 | -0.1103 | -0.254 | 0.3815 | -0.804 | 1.567 | 0.08602 | 0.9566 | 0.4792 | 0.01388 |
| AXSUSDT | equal | 0.1939 | -0.146 | -0.2618 | 1.129 | -0.3726 | 2.63 | 0.1189 | 2.727 | 0.351 | -0.02039 |
| BNBUSDT | equal | 0.112 | -0.06611 | -0.05282 | 0.5165 | -0.3357 | 1.369 | 0.02815 | 1.937 | 0.0023 | 0.01699 |
| DOGEUSDT | equal | 0.3558 | -0.1278 | -0.2851 | 1.497 | 0.02604 | 2.968 | 0.2503 | 3.921 | 0.359 | 0.1372 |
| DOTUSDT | equal | 0.2467 | -0.06793 | -0.2881 | -0.213 | -1.525 | 1.099 | 0.09603 | -0.5985 | 0.2181 | -0.01787 |
| FTMUSDT | equal | 0.1786 | -0.1229 | -0.206 | 1.755 | 0.0361 | 3.474 | 0.0669 | 3.481 | 0.5443 | 0.03512 |
| LINKUSDT | equal | 0.261 | -0.1806 | -0.204 | 0.556 | -0.7999 | 1.912 | 0.1355 | 1.454 | -0.1511 | 0.04897 |
| LTCUSDT | equal | 0.1378 | -0.1475 | -0.04663 | 0.2148 | -0.842 | 1.272 | 0.05593 | 0.6719 | -0.1505 | 0.03143 |
| MATICUSDT | equal | 0.1471 | -0.06606 | -0.1878 | 1.128 | -0.2187 | 2.474 | 0.06331 | 2.991 | 0.1855 | -0.009667 |
| SOLUSDT | equal | 0.08004 | -0.001408 | -0.1501 | 1.344 | -0.2417 | 2.93 | 0.01956 | 2.919 | 0.474 | -0.007506 |
| XRPUSDT | equal | 0.1466 | -0.04888 | -0.1553 | -0.1067 | -1.357 | 1.143 | 0.08973 | -0.3184 | -0.03147 | 0.03878 |

### Concentration

| asset | component | top1_trade_positive_pnl_share | top5_trade_positive_pnl_share | top10_trade_positive_pnl_share | top_month_positive_pnl_share | top_quarter_positive_pnl_share | top_year_positive_pnl_share |
|---|---|---|---|---|---|---|---|
| ADAUSDT | equal | 0.2784 | 0.5637 | 0.7175 | 0.3569 | 0.3325 | 0.5546 |
| AVAXUSDT | equal | 0.2004 | 0.5047 | 0.657 | 0.1584 | 0.3411 | 0.5786 |
| AXSUSDT | equal | 0.09937 | 0.3621 | 0.5688 | 0.1601 | 0.3442 | 0.5731 |
| BNBUSDT | equal | 0.2203 | 0.5495 | 0.7337 | 0.2256 | 0.5372 | 1 |
| DOGEUSDT | equal | 0.3312 | 0.6055 | 0.7657 | 0.3323 | 0.5718 | 0.9062 |
| DOTUSDT | equal | 0.1479 | 0.4912 | 0.6631 | 0.2284 | 0.3487 | 0.508 |
| FTMUSDT | equal | 0.1463 | 0.5067 | 0.7144 | 0.2187 | 0.3014 | 0.4777 |
| LINKUSDT | equal | 0.1514 | 0.5239 | 0.6909 | 0.1569 | 0.2807 | 1 |
| LTCUSDT | equal | 0.1839 | 0.5353 | 0.7927 | 0.2301 | 0.6061 | n/a |
| MATICUSDT | equal | 0.09586 | 0.3818 | 0.6425 | 0.1681 | 0.2665 | 0.5133 |
| SOLUSDT | equal | 0.2695 | 0.5952 | 0.7683 | 0.1581 | 0.5285 | 0.764 |
| XRPUSDT | equal | 0.3399 | 0.6559 | 0.83 | 0.3942 | 0.6885 | 1 |

## Combined E040 (causal inverse-vol, secondary)

### Performance

| asset | component | total_net_return | cagr | sharpe | sortino | calmar | max_dd | drawdown_duration_days | profit_factor | trades | win_rate | average_win | average_loss | payoff_ratio | expectancy | average_holding_hours |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | inverse_vol | 1.077 | 0.2756 | 1.036 | 1.79 | 1.159 | -0.2377 | 245 | 1.57 | 215 | 0.2 | 0.04703 | -0.007523 | 6.251 | 0.003808 | 141.9 |
| AVAXUSDT | inverse_vol | 1.738 | 0.3986 | 1.179 | 1.991 | 1.265 | -0.3151 | 527 | 1.812 | 221 | 0.2217 | 0.05317 | -0.01036 | 5.131 | 0.005177 | 141.3 |
| AXSUSDT | inverse_vol | 1.337 | 0.3266 | 0.9935 | 1.804 | 1.096 | -0.298 | 287 | 1.52 | 204 | 0.2059 | 0.05492 | -0.009576 | 5.735 | 0.004829 | 154.3 |
| BNBUSDT | inverse_vol | -0.07877 | -0.02696 | -0.07882 | -0.1266 | -0.1022 | -0.2637 | 874 | 0.9083 | 274 | 0.135 | 0.02228 | -0.004017 | 5.546 | -0.0002172 | 108.2 |
| DOGEUSDT | inverse_vol | 1.803 | 0.4096 | 1.227 | 2.451 | 1.845 | -0.2219 | 431 | 2.186 | 174 | 0.2586 | 0.04968 | -0.009046 | 5.491 | 0.006868 | 168.7 |
| DOTUSDT | inverse_vol | 0.1627 | 0.05147 | 0.3193 | 0.5222 | 0.1713 | -0.3004 | 659 | 1.108 | 199 | 0.196 | 0.04364 | -0.01034 | 4.222 | 0.001177 | 157.3 |
| FTMUSDT | inverse_vol | 1.164 | 0.2931 | 0.908 | 1.469 | 0.9494 | -0.3087 | 368 | 1.474 | 172 | 0.1919 | 0.07605 | -0.01237 | 6.148 | 0.005529 | 176.2 |
| LINKUSDT | inverse_vol | -0.3684 | -0.1419 | -0.3799 | -0.5896 | -0.2501 | -0.5673 | 1030 | 0.6964 | 256 | 0.1602 | 0.0348 | -0.009104 | 3.823 | -0.001468 | 120.1 |
| LTCUSDT | inverse_vol | -0.3144 | -0.1181 | -0.4429 | -0.6911 | -0.2593 | -0.4555 | 932 | 0.7169 | 245 | 0.1388 | 0.02911 | -0.006795 | 4.284 | -0.001341 | 121 |
| MATICUSDT | inverse_vol | 0.8693 | 0.2316 | 0.8493 | 1.497 | 0.9079 | -0.2551 | 419 | 1.589 | 196 | 0.1735 | 0.05961 | -0.01001 | 5.952 | 0.003902 | 141.7 |
| SOLUSDT | inverse_vol | 0.7115 | 0.196 | 0.7018 | 1.172 | 0.686 | -0.2857 | 244 | 1.356 | 213 | 0.1831 | 0.0589 | -0.009734 | 6.051 | 0.003335 | 141.4 |
| XRPUSDT | inverse_vol | -0.185 | -0.06587 | -0.1928 | -0.3295 | -0.1542 | -0.4272 | 932 | 0.8161 | 264 | 0.1477 | 0.02554 | -0.00648 | 3.942 | -0.0005464 | 110.7 |

### Turnover, exposure and tails

| asset | component | annual_turnover | annual_transaction_cost | net_funding_usdt | gross_exposure | net_exposure | exposure_p50 | exposure_p90 | exposure_p99 | exposure_max | exposure_share_above_1x | exposure_time_in_market | expected_shortfall_95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | inverse_vol | 54.05 | 0.04892 | n/a | 0.3065 | -0.03699 | n/a | n/a | n/a | n/a | n/a | n/a | -0.02835 |
| AVAXUSDT | inverse_vol | 53.8 | 0.04869 | n/a | 0.3247 | -0.009548 | n/a | n/a | n/a | n/a | n/a | n/a | -0.03592 |
| AXSUSDT | inverse_vol | 52.5 | 0.04751 | n/a | 0.3142 | -0.07541 | n/a | n/a | n/a | n/a | n/a | n/a | -0.03434 |
| BNBUSDT | inverse_vol | 48.73 | 0.0441 | n/a | 0.233 | 0.005224 | n/a | n/a | n/a | n/a | n/a | n/a | -0.01994 |
| DOGEUSDT | inverse_vol | 45.42 | 0.0411 | n/a | 0.2589 | -0.04638 | n/a | n/a | n/a | n/a | n/a | n/a | -0.02973 |
| DOTUSDT | inverse_vol | 51.69 | 0.04678 | n/a | 0.3183 | -0.07663 | n/a | n/a | n/a | n/a | n/a | n/a | -0.02906 |
| FTMUSDT | inverse_vol | 40.82 | 0.03694 | n/a | 0.2688 | -0.05877 | n/a | n/a | n/a | n/a | n/a | n/a | -0.04067 |
| LINKUSDT | inverse_vol | 56.3 | 0.05095 | n/a | 0.3012 | -0.0107 | n/a | n/a | n/a | n/a | n/a | n/a | -0.03346 |
| LTCUSDT | inverse_vol | 47.49 | 0.04298 | n/a | 0.2385 | -0.01948 | n/a | n/a | n/a | n/a | n/a | n/a | -0.02755 |
| MATICUSDT | inverse_vol | 43.1 | 0.039 | n/a | 0.264 | -0.04818 | n/a | n/a | n/a | n/a | n/a | n/a | -0.03093 |
| SOLUSDT | inverse_vol | 50.43 | 0.04564 | n/a | 0.2664 | 0.01332 | n/a | n/a | n/a | n/a | n/a | n/a | -0.03753 |
| XRPUSDT | inverse_vol | 46.56 | 0.04214 | n/a | 0.2324 | -0.04455 | n/a | n/a | n/a | n/a | n/a | n/a | -0.02489 |

### Factor regression (daily; underlying, BTC, replication market, lagged BTC vol, lagged BTC trend; HAC 14)

| asset | component | asset_beta | btc_beta | market_beta | alpha | alpha_ci_low | alpha_ci_high | r_squared | factor_adjusted_sharpe | univariate_alpha | univariate_beta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADAUSDT | inverse_vol | 0.1421 | -0.006387 | -0.1753 | -0.0392 | -1.295 | 1.217 | 0.05787 | -0.1499 | 0.2788 | 0.001792 |
| AVAXUSDT | inverse_vol | 0.1373 | -0.02074 | -0.1854 | 0.01271 | -1.126 | 1.151 | 0.04826 | 0.03943 | 0.3889 | 0.006149 |
| AXSUSDT | inverse_vol | 0.152 | -0.05774 | -0.2265 | 0.603 | -0.7591 | 1.965 | 0.09989 | 1.859 | 0.3361 | -0.008769 |
| BNBUSDT | inverse_vol | 0.04741 | -0.04488 | 0.0003752 | 0.05033 | -0.5355 | 0.6362 | 0.0141 | 0.3005 | -0.01833 | 0.01831 |
| DOGEUSDT | inverse_vol | 0.1867 | -0.08366 | -0.1765 | 1.426 | -0.04958 | 2.901 | 0.146 | 4.821 | 0.3617 | 0.04948 |
| DOTUSDT | inverse_vol | 0.05946 | -0.01725 | -0.1148 | -0.3512 | -1.434 | 0.7315 | 0.04379 | -1.346 | 0.07892 | -0.04098 |
| FTMUSDT | inverse_vol | 0.0349 | -0.07164 | -0.05173 | 1.625 | 0.4341 | 2.816 | 0.02366 | 4.703 | 0.3208 | -0.01318 |
| LINKUSDT | inverse_vol | 0.09638 | -0.08571 | -0.08086 | 0.1648 | -0.7985 | 1.128 | 0.04763 | 0.5781 | -0.1136 | 0.006913 |
| LTCUSDT | inverse_vol | 0.01054 | -0.02629 | -0.02829 | -0.01688 | -0.8758 | 0.8421 | 0.01578 | -0.0751 | -0.09627 | -0.02386 |
| MATICUSDT | inverse_vol | 0.1015 | -0.04434 | -0.1256 | 0.5749 | -0.5436 | 1.693 | 0.04835 | 1.992 | 0.2504 | -0.003468 |
| SOLUSDT | inverse_vol | 0.04866 | 0.02015 | -0.0838 | 0.8831 | -0.3 | 2.066 | 0.01036 | 2.672 | 0.2288 | 0.007475 |
| XRPUSDT | inverse_vol | 0.03271 | -0.01286 | -0.08944 | 0.2607 | -0.5821 | 1.103 | 0.06201 | 1.195 | -0.02732 | -0.02466 |

### Concentration

| asset | component | top1_trade_positive_pnl_share | top5_trade_positive_pnl_share | top10_trade_positive_pnl_share | top_month_positive_pnl_share | top_quarter_positive_pnl_share | top_year_positive_pnl_share |
|---|---|---|---|---|---|---|---|
| ADAUSDT | inverse_vol | 0.1141 | 0.3983 | 0.6155 | 0.1917 | 0.1881 | 0.5404 |
| AVAXUSDT | inverse_vol | 0.08794 | 0.3979 | 0.5887 | 0.208 | 0.2578 | 0.7187 |
| AXSUSDT | inverse_vol | 0.1036 | 0.3504 | 0.5429 | 0.2285 | 0.278 | 0.5867 |
| BNBUSDT | inverse_vol | 0.09439 | 0.4052 | 0.6575 | 0.3002 | 0.3872 | n/a |
| DOGEUSDT | inverse_vol | 0.1723 | 0.4908 | 0.6873 | 0.176 | 0.412 | 0.7399 |
| DOTUSDT | inverse_vol | 0.128 | 0.4218 | 0.633 | 0.307 | 0.2798 | 0.622 |
| FTMUSDT | inverse_vol | 0.1054 | 0.3799 | 0.5899 | 0.1842 | 0.2876 | 0.4763 |
| LINKUSDT | inverse_vol | 0.118 | 0.4872 | 0.7082 | 0.2786 | 0.4537 | 1 |
| LTCUSDT | inverse_vol | 0.1523 | 0.5995 | 0.7711 | 0.213 | 0.4939 | n/a |
| MATICUSDT | inverse_vol | 0.1268 | 0.4485 | 0.6663 | 0.1927 | 0.2438 | 0.6285 |
| SOLUSDT | inverse_vol | 0.1544 | 0.4514 | 0.6693 | 0.1607 | 0.3702 | 0.7587 |
| XRPUSDT | inverse_vol | 0.1541 | 0.5858 | 0.7966 | 0.2036 | 0.4707 | 1 |

## Discovery comparators (BTC/ETH, same corrected engine and window)

| asset | component | total_net_return | cagr | sharpe | sortino | calmar | max_dd | drawdown_duration_days | profit_factor | trades | win_rate | average_win | average_loss | payoff_ratio | expectancy | average_holding_hours |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT | breakout | 1.145 | 0.2894 | 1.233 | 2.622 | 2.654 | -0.109 | 234 | 2.014 | 57 | 0.4211 | 0.06196 | -0.01908 | 3.247 | 0.01504 | 72.67 |
| BTCUSDT | equal | 1.143 | 0.289 | 1.06 | 1.873 | 1.398 | -0.2067 | 253 | 1.723 | 192 | 0.2031 | 0.04808 | -0.006521 | 7.374 | 0.004571 | 158.5 |
| BTCUSDT | inverse_vol | 0.8675 | 0.2312 | 1.076 | 2.081 | 1.833 | -0.1262 | 234 | 1.773 | 192 | 0.1823 | 0.0429 | -0.005444 | 7.88 | 0.003652 | 158.5 |
| BTCUSDT | trend | 0.8552 | 0.2285 | 0.6846 | 1.065 | 0.547 | -0.4177 | 293 | 1.472 | 135 | 0.1111 | 0.1539 | -0.01163 | 13.23 | 0.006759 | 194.8 |
| ETHUSDT | breakout | 0.6352 | 0.178 | 0.7395 | 1.42 | 0.7376 | -0.2413 | 629 | 1.657 | 51 | 0.5098 | 0.05563 | -0.03349 | 1.661 | 0.01194 | 66.78 |
| ETHUSDT | equal | 0.642 | 0.1796 | 0.6916 | 1.156 | 0.495 | -0.3628 | 691 | 1.389 | 200 | 0.225 | 0.04309 | -0.00865 | 4.982 | 0.002993 | 148.5 |
| ETHUSDT | inverse_vol | 0.9052 | 0.2394 | 0.9572 | 1.737 | 1.006 | -0.238 | 608 | 1.686 | 200 | 0.23 | 0.03642 | -0.006986 | 5.213 | 0.00359 | 148.5 |
| ETHUSDT | trend | 0.325 | 0.09825 | 0.4378 | 0.6648 | 0.166 | -0.5919 | 871 | 1.152 | 149 | 0.1275 | 0.1307 | -0.01448 | 9.025 | 0.004031 | 176.5 |


## Cross-asset summary by component

| component | positive_net_fraction | positive_sharpe_fraction | positive_alpha_fraction | positive_alpha_ci_excludes_zero | negative_alpha_ci_excludes_zero | median_sharpe | median_alpha | median_factor_adjusted_sharpe | median_max_dd | median_exposure_max |
|---|---|---|---|---|---|---|---|---|---|---|
| trend | 0.5833 | 0.75 | 0.75 | 1 | 0 | 0.6523 | 1.37 | 2.293 | -0.6302 | 1.362 |
| breakout | 0.5833 | 0.8333 | 0.6667 | 0 | 0 | 0.1828 | 0.1279 | 0.3613 | -0.3774 | 1.129 |
| equal | 0.6667 | 0.75 | 0.75 | 2 | 0 | 0.7023 | 0.5363 | 1.695 | -0.3745 | 1.123 |
| inverse_vol | 0.6667 | 0.6667 | 0.75 | 1 | 0 | 0.7755 | 0.2127 | 0.8866 | -0.2992 | n/a |


- trend: positive ADAUSDT, AVAXUSDT, AXSUSDT, DOGEUSDT, DOTUSDT, FTMUSDT, SOLUSDT; non-positive BNBUSDT, LINKUSDT, LTCUSDT, MATICUSDT, XRPUSDT
- breakout: positive ADAUSDT, AVAXUSDT, AXSUSDT, BNBUSDT, DOGEUSDT, MATICUSDT, SOLUSDT; non-positive DOTUSDT, FTMUSDT, LINKUSDT, LTCUSDT, XRPUSDT
- equal: positive ADAUSDT, AVAXUSDT, AXSUSDT, DOGEUSDT, DOTUSDT, FTMUSDT, MATICUSDT, SOLUSDT; non-positive BNBUSDT, LINKUSDT, LTCUSDT, XRPUSDT
- inverse_vol: positive ADAUSDT, AVAXUSDT, AXSUSDT, DOGEUSDT, DOTUSDT, FTMUSDT, MATICUSDT, SOLUSDT; non-positive BNBUSDT, LINKUSDT, LTCUSDT, XRPUSDT
