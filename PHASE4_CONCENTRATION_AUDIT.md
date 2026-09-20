# Concentration audit

Top-trade shares use net dollar P&L, not sums of gross percentage returns. Combined sleeves are scaled by actual daily portfolio capital. All allocation-transfer costs are subtracted from the positive-trade denominator for a conservative portfolio top5 bound. Best-year removal drops that calendar year. Single-asset best-trade interval deletion is a coarse adverse diagnostic because other concurrent component trades are also removed; exact portfolio dollar-contribution deletion is reported separately. None changes the frozen strategy.

| asset | top1_trade_positive_pnl_share | top5_trade_positive_pnl_share | top10_trade_positive_pnl_share | top_month_positive_pnl_share | top_quarter_positive_pnl_share | top_year_positive_pnl_share |
|---|---|---|---|---|---|---|
| SOLUSDT | 0.26951 | 0.59518 | 0.76834 | 0.15806 | 0.52845 | 0.76405 |
| XRPUSDT | 0.33987 | 0.65586 | 0.83001 | 0.39419 | 0.68849 | 1 |
| BNBUSDT | 0.22029 | 0.54952 | 0.73366 | 0.22559 | 0.53716 | 1 |
| DOTUSDT | 0.14791 | 0.49116 | 0.66308 | 0.22841 | 0.34875 | 0.508 |
| DOGEUSDT | 0.33118 | 0.60553 | 0.76574 | 0.3323 | 0.57179 | 0.9062 |
| ADAUSDT | 0.27844 | 0.56371 | 0.71745 | 0.35686 | 0.3325 | 0.55463 |
| AVAXUSDT | 0.20036 | 0.50471 | 0.65703 | 0.15844 | 0.34107 | 0.57856 |
| AXSUSDT | 0.099371 | 0.36206 | 0.56877 | 0.16008 | 0.34417 | 0.57309 |
| MATICUSDT | 0.095857 | 0.38179 | 0.64245 | 0.1681 | 0.26654 | 0.51334 |
| FTMUSDT | 0.14627 | 0.50671 | 0.71439 | 0.21871 | 0.30138 | 0.47774 |
| LTCUSDT | 0.18389 | 0.53527 | 0.79267 | 0.2301 | 0.60614 | nan |
| LINKUSDT | 0.1514 | 0.52387 | 0.69086 | 0.15686 | 0.28071 | 1 |


Primary portfolio diagnostics:

{
  "best_year": 2024,
  "remove_best_year": {
    "total_net_return": 0.3472226985996105,
    "cagr": 0.16069922831007788,
    "volatility": 0.2650667344570069,
    "sharpe": 0.6939079888715102,
    "sortino": 1.0943664278025704,
    "calmar": 0.6671709833386587,
    "max_dd": -0.2408666328770871,
    "drawdown_duration_days": 516,
    "expected_shortfall_95": -0.03011093558360036,
    "annual_arithmetic_return": 0.18393192462380029,
    "trades": 0,
    "average_trade": null,
    "median_trade": null,
    "win_rate": null,
    "profit_factor": null,
    "payoff_ratio": null,
    "expectancy": null,
    "top_month_positive_pnl_share": 0.14064156809024908,
    "top_quarter_positive_pnl_share": 0.5445736484538486,
    "top_year_positive_pnl_share": 0.8203362893004109
  },
  "top5_trade_share_conservative": 0.13168720315799398,
  "unassigned_allocation_cost": 162.67522507297326,
  "trade_contribution_reconciliation_error": -3.456079866737127e-11,
  "remove_best1_trade_contributions": {
    "total_net_return": 0.6957545772870264,
    "cagr": 0.19229734004983112,
    "volatility": 0.2617943175795523,
    "sharpe": 0.8020905376658344,
    "sortino": 1.2616864672003323,
    "calmar": 0.7983560767753141,
    "max_dd": -0.2408666328770871,
    "drawdown_duration_days": 516,
    "expected_shortfall_95": -0.029798897115892994,
    "annual_arithmetic_return": 0.2099827449452433,
    "trades": 0,
    "average_trade": null,
    "median_trade": null,
    "win_rate": null,
    "profit_factor": null,
    "payoff_ratio": null,
    "expectancy": null,
    "top_month_positive_pnl_share": 0.2004154928089999,
    "top_quarter_positive_pnl_share": 0.33486991740605604,
    "top_year_positive_pnl_share": 0.5009408346926801
  },
  "remove_best5_trade_contributions": {
    "total_net_return": 0.3690498513237923,
    "cagr": 0.11027764979372012,
    "volatility": 0.25354266006942816,
    "sharpe": 0.5386291846753023,
    "sortino": 0.8381352125112882,
    "calmar": 0.45783697175687343,
    "max_dd": -0.2408666328770871,
    "drawdown_duration_days": 629,
    "expected_shortfall_95": -0.029120467754056144,
    "annual_arithmetic_return": 0.1365654762736034,
    "trades": 0,
    "average_trade": null,
    "median_trade": null,
    "win_rate": null,
    "profit_factor": null,
    "payoff_ratio": null,
    "expectancy": null,
    "top_month_positive_pnl_share": 0.12133498269209944,
    "top_quarter_positive_pnl_share": 0.314961642139208,
    "top_year_positive_pnl_share": 0.4924735398324808
  }
}

Full per-asset/portfolio diagnostics: C:\Users\Youssef\Documents\Trading\GPT 5.6 Astra plus Claude Opus 5\reports\E045_20260909T140237\concentration.json
