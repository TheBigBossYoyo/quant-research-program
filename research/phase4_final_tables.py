"""Consolidated Phase 4 per-asset tables from persisted E044/E045 outputs. No strategy evaluation.

Writes PHASE4_REPLICATION_TABLES.md and reports/<E045>/final_tables.json. Reads only files already
produced by phase4_execute.py and phase4_report.py; adds average win/loss and exposure quantiles.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from core import ROOT
from phase4_data import universe

COMPONENTS = ['trend', 'breakout', 'equal', 'inverse_vol']
CASE = 'stress'


def fmt(x):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return 'n/a'
    if isinstance(x, (float, np.floating)):
        return f'{x:.4g}'
    return str(x)


def md_table(rows, columns):
    head = '| ' + ' | '.join(columns) + ' |\n|' + '|'.join(['---'] * len(columns)) + '|\n'
    body = ''.join('| ' + ' | '.join(fmt(r.get(c)) for c in columns) + ' |\n' for r in rows)
    return head + body


def trade_stats(path):
    if not path.exists():
        return {}
    t = pd.read_csv(path)
    if not len(t):
        return dict(average_win=None, average_loss=None, average_holding_hours=None)
    wins = t.ret[t.ret > 0]; losses = t.ret[t.ret < 0]
    hold = (pd.to_datetime(t.exit_time, utc=True) - pd.to_datetime(t.entry_time, utc=True)).dt.total_seconds() / 3600
    return dict(average_win=float(wins.mean()) if len(wins) else None, average_loss=float(losses.mean()) if len(losses) else None,
                average_holding_hours=float(hold.mean()))


def exposure_stats(source, sym, comp):
    """Hourly-event position size (|units*mark/equity|) quantiles; equal/inverse_vol use the sleeve mix."""
    if comp in ('trend', 'breakout'):
        p = pd.read_csv(source / sym / f'{comp}_{CASE}_path.csv', index_col=0, parse_dates=True)
        g = p.position.abs()
    else:
        pt = pd.read_csv(source / sym / f'trend_{CASE}_path.csv', index_col=0, parse_dates=True).position.abs()
        pb = pd.read_csv(source / sym / f'breakout_{CASE}_path.csv', index_col=0, parse_dates=True).position.abs()
        if comp == 'equal':
            g = .5 * pt + .5 * pb
        else:
            d = pd.read_csv(source / 'daily_panel.csv', parse_dates=['date'])
            w = d[(d.asset == sym) & (d.component == 'inverse_vol') & (d.case == CASE)]
            g = None
    if g is None:
        return dict(exposure_time_in_market=None)
    g = g[g.index >= pd.Timestamp('2022-01-01', tz='UTC')]
    return dict(exposure_time_in_market=float((g > 1e-9).mean()), exposure_p50=float(g.quantile(.5)), exposure_p90=float(g.quantile(.9)),
                exposure_p99=float(g.quantile(.99)), exposure_max=float(g.max()), exposure_share_above_1x=float((g > 1 + 1e-9).mean()))


def main():
    assets = universe()
    source = ROOT / 'reports' / (ROOT / 'reports/PHASE4_ACTIVE_REPLICATION.txt').read_text().strip()
    analysis = ROOT / 'reports' / (ROOT / 'reports/PHASE4_ACTIVE_ANALYSIS.txt').read_text().strip()
    M = pd.read_csv(source / 'metrics.csv'); F = pd.read_csv(analysis / 'factor_results.csv')
    M = M[M.case == CASE].merge(F, on=['asset', 'component'], how='left')
    rows = []
    for sym in assets + ['BTCUSDT', 'ETHUSDT']:
        for comp in COMPONENTS:
            m = M[(M.asset == sym) & (M.component == comp)]
            if not len(m):
                continue
            r = m.iloc[0].to_dict()
            r.update(trade_stats(source / sym / f'{comp}_{CASE}_trades.csv'))
            r.update(exposure_stats(source, sym, comp))
            r['role'] = 'discovery comparator' if sym in ('BTCUSDT', 'ETHUSDT') else 'replication'
            rows.append(r)
    R = pd.DataFrame(rows)
    cols_perf = ['asset', 'component', 'total_net_return', 'cagr', 'sharpe', 'sortino', 'calmar', 'max_dd', 'drawdown_duration_days', 'profit_factor', 'trades', 'win_rate', 'average_win', 'average_loss', 'payoff_ratio', 'expectancy', 'average_holding_hours']
    cols_risk = ['asset', 'component', 'annual_turnover', 'annual_transaction_cost', 'net_funding_usdt', 'gross_exposure', 'net_exposure', 'exposure_p50', 'exposure_p90', 'exposure_p99', 'exposure_max', 'exposure_share_above_1x', 'exposure_time_in_market', 'expected_shortfall_95']
    cols_factor = ['asset', 'component', 'asset_beta', 'btc_beta', 'market_beta', 'alpha', 'alpha_ci_low', 'alpha_ci_high', 'r_squared', 'factor_adjusted_sharpe', 'univariate_alpha', 'univariate_beta']
    cols_conc = ['asset', 'component', 'top1_trade_positive_pnl_share', 'top5_trade_positive_pnl_share', 'top10_trade_positive_pnl_share', 'top_month_positive_pnl_share', 'top_quarter_positive_pnl_share', 'top_year_positive_pnl_share']
    rep = R[R.role == 'replication']; disc = R[R.role != 'replication']
    md = ['# Phase 4 replication tables (frozen E040, stress cost case 9.05 bps per side plus funding, 2022-2024)', '',
          f'Source replication: {source.name}. Analysis: {analysis.name}. All twelve preregistered assets are shown for every component; losing assets are not omitted. BTC/ETH are discovery comparators, never part of replication statistics.', '',
          'Exposure columns are hourly-event |position notional / equity| from the simulated paths (2022-2024): p50/p90/p99/max and the share of hours above 1x. E040 targets about 1x when it resizes but can drift above 1x between resize events; there is no hard cap.', '']
    for comp in COMPONENTS:
        sub = rep[rep.component == comp].sort_values('asset').to_dict('records')
        if not sub:
            continue
        title = {'trend': 'Slow-trend component', 'breakout': 'Compression-breakout component', 'equal': 'Combined E040 (equal 50/50, primary)', 'inverse_vol': 'Combined E040 (causal inverse-vol, secondary)'}[comp]
        md += [f'## {title}', '', '### Performance', '', md_table(sub, cols_perf), '### Turnover, exposure and tails', '', md_table(sub, cols_risk),
               '### Factor regression (daily; underlying, BTC, replication market, lagged BTC vol, lagged BTC trend; HAC 14)', '', md_table(sub, cols_factor),
               '### Concentration', '', md_table(sub, cols_conc)]
    md += ['## Discovery comparators (BTC/ETH, same corrected engine and window)', '', md_table(disc.sort_values(['asset', 'component']).to_dict('records'), cols_perf), '']
    summary = {}
    for comp in COMPONENTS:
        sub = rep[rep.component == comp]
        summary[comp] = dict(positive_net_fraction=float((sub.total_net_return > 0).mean()), positive_sharpe_fraction=float((sub.sharpe > 0).mean()),
                             positive_alpha_fraction=float((sub.alpha > 0).mean()), positive_alpha_ci_excludes_zero=int((sub.alpha_ci_low > 0).sum()),
                             negative_alpha_ci_excludes_zero=int((sub.alpha_ci_high < 0).sum()), median_sharpe=float(sub.sharpe.median()), median_alpha=float(sub.alpha.median()),
                             median_factor_adjusted_sharpe=float(sub.factor_adjusted_sharpe.median()), median_max_dd=float(sub.max_dd.median()),
                             median_exposure_max=float(sub.exposure_max.median()) if sub.exposure_max.notna().any() else None,
                             assets_positive=sorted(sub[sub.total_net_return > 0].asset.tolist()), assets_negative=sorted(sub[sub.total_net_return <= 0].asset.tolist()))
    md += ['## Cross-asset summary by component', '', md_table([dict(component=k, **{kk: vv for kk, vv in v.items() if not isinstance(vv, list)}) for k, v in summary.items()],
                                                                 ['component', 'positive_net_fraction', 'positive_sharpe_fraction', 'positive_alpha_fraction', 'positive_alpha_ci_excludes_zero', 'negative_alpha_ci_excludes_zero', 'median_sharpe', 'median_alpha', 'median_factor_adjusted_sharpe', 'median_max_dd', 'median_exposure_max']), '']
    for k, v in summary.items():
        md.append(f"- {k}: positive {', '.join(v['assets_positive']) or 'none'}; non-positive {', '.join(v['assets_negative']) or 'none'}")
    (ROOT / 'PHASE4_REPLICATION_TABLES.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    R.to_csv(analysis / 'final_tables.csv', index=False)
    (analysis / 'final_tables.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print('FINAL_TABLES', json.dumps({k: {kk: vv for kk, vv in v.items() if not isinstance(vv, list)} for k, v in summary.items()}, indent=1))


if __name__ == '__main__':
    main()
