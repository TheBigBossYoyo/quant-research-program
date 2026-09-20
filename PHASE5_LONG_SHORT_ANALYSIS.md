# PHASE5_LONG_SHORT_ANALYSIS

Cohort-2 equal-weight trend portfolio, stress costs. Long/short P&L from the ledger episode accounting (fees and funding assigned to the side that paid them).

```
{
 "portfolio_long_contribution": 1.5506648318766483,
 "portfolio_short_contribution": -0.07988019616608444,
 "short_side_sharpe": -0.05184530102913616,
 "long_side_sharpe": 0.8036522695266334,
 "short_side_expectancy_annual": -0.01995638028789926,
 "drawdown_full": -0.5667518599343837,
 "drawdown_without_short_contribution": -0.5157619071796342,
 "sharpe_without_short_contribution": 0.787753950414204,
 "short_contribution_by_year": {
  "2021": 0.014044993832264957,
  "2022": 0.29454832285590604,
  "2023": -0.24971161483001644,
  "2024": -0.13876189802423902
 },
 "long_contribution_by_year": {
  "2021": 1.0086013913631835,
  "2022": -0.24880977697655624,
  "2023": 0.2021342405808089,
  "2024": 0.5887389769092118
 },
 "assets_with_positive_short_pnl": 2,
 "assets_with_positive_long_pnl": 8
}
```

## Per asset (USDT per 10,000 sleeve capital)

| asset | long_pnl_usdt | short_pnl_usdt | total_net_return | sharpe | long_share_of_gross_pnl |
|---|---|---|---|---|---|
| LINKUSDT | -3516 | -5337 | -0.8853 | -0.1788 | -0.3971 |
| LTCUSDT | -7069 | -1528 | -0.8597 | -0.3114 | -0.8222 |
| XRPUSDT | 3627 | -5838 | -0.221 | 0.3394 | 0.3832 |
| BCHUSDT | 1594 | -5987 | -0.4394 | 0.2411 | 0.2102 |
| BNBUSDT | 9.316e+04 | -5.594e+04 | 3.723 | 0.8482 | 0.6248 |
| ADAUSDT | 4.885e+04 | -4147 | 4.47 | 0.9166 | 0.9217 |
| EOSUSDT | -3458 | -2339 | -0.5797 | 0.1767 | -0.5965 |
| TRXUSDT | 1035 | -5249 | -0.4214 | 0.2024 | 0.1647 |
| XTZUSDT | -3559 | -1207 | -0.4766 | 0.2501 | -0.7468 |
| XLMUSDT | 5321 | -1758 | 0.3562 | 0.4942 | 0.7516 |
| VETUSDT | 1.367e+05 | 2007 | 13.87 | 1.17 | 0.9855 |
| ETCUSDT | 1.896e+04 | 3540 | 2.25 | 0.7586 | 0.8426 |
