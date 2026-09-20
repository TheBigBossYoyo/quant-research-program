# Concentration audit

Top-trade shares use net dollar P&L, not sums of gross percentage returns. Combined sleeves are scaled by actual daily portfolio capital. All allocation-transfer costs are subtracted from the positive-trade denominator for a conservative portfolio top5 bound. Best-year removal drops that calendar year. Single-asset best-trade interval deletion is a coarse adverse diagnostic because other concurrent component trades are also removed; exact portfolio dollar-contribution deletion is reported separately. None changes the frozen strategy.

| asset | top1_trade_positive_pnl_share | top5_trade_positive_pnl_share | top10_trade_positive_pnl_share | top_month_positive_pnl_share | top_quarter_positive_pnl_share | top_year_positive_pnl_share |
|---|---|---|---|---|---|---|
| SOLUSDT | 0.26358 | 0.58068 | 0.76088 | 0.15781 | 0.49861 | 0.70224 |
| XRPUSDT | 0.33006 | 0.65015 | 0.81477 | 0.37654 | 0.63082 | 1 |
| BNBUSDT | 0.22029 | 0.54952 | 0.73366 | 0.22559 | 0.53716 | 1 |
| DOTUSDT | 0.14791 | 0.49116 | 0.66308 | 0.22841 | 0.34875 | 0.508 |
| DOGEUSDT | 0.33118 | 0.60553 | 0.76574 | 0.3323 | 0.57179 | 0.9062 |
| ADAUSDT | 0.27844 | 0.56371 | 0.71745 | 0.35686 | 0.3325 | 0.55463 |
| AVAXUSDT | 0.20036 | 0.50471 | 0.65703 | 0.15844 | 0.34107 | 0.57856 |
| AXSUSDT | 0.099371 | 0.36206 | 0.56877 | 0.16008 | 0.34417 | 0.57309 |
| MATICUSDT | 0.095857 | 0.38179 | 0.64245 | 0.1681 | 0.26654 | 0.51334 |
| FTMUSDT | 0.14871 | 0.5076 | 0.71876 | 0.21914 | 0.30451 | 0.51374 |
| LTCUSDT | 0.21206 | 0.53981 | 0.77439 | 0.19873 | 0.6374 | nan |
| LINKUSDT | 0.1514 | 0.52387 | 0.69086 | 0.15686 | 0.28071 | 1 |


Primary portfolio diagnostics:

{
  "best_year": 2024,
  "remove_best_year": {
    "total_net_return": 0.38434917008071445,
    "cagr": 0.1765836859657346,
    "volatility": 0.2597208981696924,
    "sharpe": 0.7551541842671783,
    "sortino": 1.1999337088196549,
    "calmar": 0.73516770377582,
    "max_dd": -0.24019510794448817,
    "drawdown_duration_days": 516,
    "expected_shortfall_95": -0.02916943978794806,
    "annual_arithmetic_return": 0.19612932299447294,
    "trades": 0,
    "average_trade": null,
    "median_trade": null,
    "win_rate": null,
    "profit_factor": null,
    "payoff_ratio": null,
    "expectancy": null,
    "top_month_positive_pnl_share": 0.13670715278986031,
    "top_quarter_positive_pnl_share": 0.5197166495995464,
    "top_year_positive_pnl_share": 0.7614322828068338
  },
  "top5_trade_share_conservative": 0.13127975927564892,
  "unassigned_allocation_cost": 165.92689084387166,
  "trade_contribution_reconciliation_error": -4.3655745685100555e-11,
  "remove_best1_trade_contributions": {
    "total_net_return": 0.7423073296751512,
    "cagr": 0.20309961117161146,
    "volatility": 0.2582006388619415,
    "sharpe": 0.8445867540059183,
    "sortino": 1.3351182108850048,
    "calmar": 0.8455609812775625,
    "max_dd": -0.24019510794448817,
    "drawdown_duration_days": 516,
    "expected_shortfall_95": -0.02916969499587337,
    "annual_arithmetic_return": 0.21807283945866154,
    "trades": 0,
    "average_trade": null,
    "median_trade": null,
    "win_rate": null,
    "profit_factor": null,
    "payoff_ratio": null,
    "expectancy": null,
    "top_month_positive_pnl_share": 0.1983361066565031,
    "top_quarter_positive_pnl_share": 0.3253632802305034,
    "top_year_positive_pnl_share": 0.48222366300907543
  },
  "remove_best5_trade_contributions": {
    "total_net_return": 0.4066337326173006,
    "cagr": 0.12033681858547851,
    "volatility": 0.24983683310124266,
    "sharpe": 0.5790001778016538,
    "sortino": 0.905354310145861,
    "calmar": 0.5009961260880039,
    "max_dd": -0.24019510794448817,
    "drawdown_duration_days": 629,
    "expected_shortfall_95": -0.028487092498720393,
    "annual_arithmetic_return": 0.1446555707870216,
    "trades": 0,
    "average_trade": null,
    "median_trade": null,
    "win_rate": null,
    "profit_factor": null,
    "payoff_ratio": null,
    "expectancy": null,
    "top_month_positive_pnl_share": 0.11970405296055817,
    "top_quarter_positive_pnl_share": 0.3466815939745869,
    "top_year_positive_pnl_share": 0.45891849576453836
  }
}

Full per-asset/portfolio diagnostics: C:\Users\Youssef\Documents\Trading\GPT 5.6 Astra plus Claude Opus 5\reports\E045_20260909T135156\concentration.json
