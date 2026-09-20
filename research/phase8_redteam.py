"""Phase 8 red team and small-capital simulation for the E058 cells (development only; diagnostics, no new hypotheses).

Attacks (PHASE8_PROMOTION_GATE.md / user list): one year, one stock, one insider; removal of top contributors (re-simulation
without the top 5 / top 10 events); FF3 loadings (size, value) of monthly net returns; liquidity-rank distribution of
entries; entries during market drawdowns; timely vs late and amended-original exclusion (re-simulation); sector mix of
the PIT subset (current S&P sector labels, SECTOR_NOT_PIT); execution delay and cost stress are read from E058.
Small capital: EUR 500 and EUR 1,000 with a EUR 1 minimum order. Usage: PYTHONUTF8=1 python phase8_redteam.py E058_<stamp>
"""
from datetime import datetime, timezone
import json
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm

import phase8_insider_backtest as bt
import phase6_e051_run as run
import phase6_french as fr
from phase6_lock import ROOT

EUR_USD = 1.1652


def ff3_loadings(net, rf_period):
    ff = fr.load('ff3_monthly', 'main'); ff.columns = [c.strip() for c in ff.columns]
    ff.index = ff.index.to_period('M')
    idx = net.index.to_period('M')
    X = ff.reindex(idx)
    y = net.to_numpy() - X['RF'].to_numpy()
    m = sm.OLS(y, sm.add_constant(X[['Mkt-RF', 'SMB', 'HML']].to_numpy()), missing='drop').fit(cov_type='HAC', cov_kwds=dict(maxlags=6))
    return dict(alpha_ann=float(m.params[0] * 12), alpha_t=float(m.tvalues[0]), mkt=float(m.params[1]), smb=float(m.params[2]), hml=float(m.params[3]), r2=float(m.rsquared))


def main(run_name):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E058RT_{stamp}'; out_dir.mkdir(parents=True)
    res = json.loads((ROOT / 'reports' / run_name / 'results.json').read_text(encoding='utf8'))
    ev = pd.read_parquet(ROOT / 'reports' / run_name / 'events_used.parquet')
    monthly = pd.read_csv(ROOT / 'reports' / run_name / 'monthly_net.csv', index_col=0, parse_dates=True)
    bench_m = pd.read_csv(ROOT / 'reports' / run_name / 'bench_monthly.csv', index_col=0, parse_dates=True).iloc[:, 0]
    spy_m = pd.read_csv(ROOT / 'reports' / run_name / 'spy_monthly.csv', index_col=0, parse_dates=True).iloc[:, 0]
    rf = run.load_ff3()['RF']
    U = bt.load_universe()
    ao, _, spy_ao, _ = bt.daily_benchmarks(U); ended_info = bt.ended_map(U); venue = bt.su.load_last_venue(); cal = U['cal']
    out = {}
    spy_dd = (spy_ao / spy_ao.cummax() - 1.0)
    for cell, f in bt.CELLS.items():
        sel = ev[f(ev)]
        tr = pd.read_csv(ROOT / 'reports' / run_name / f'trades_{cell}.csv')
        r = dict(n_events=int(len(sel)))
        # concentration
        pos_pnl = tr['pnl'].clip(lower=0).sum()
        tr['year'] = pd.DatetimeIndex(cal[tr['exit_idx'].astype(int)]).year
        r['pnl_share_by_year'] = {int(k): float(v / tr['pnl'].sum()) for k, v in tr.groupby('year')['pnl'].sum().items()} if tr['pnl'].sum() != 0 else {}
        r['top_ticker_share_of_gains'] = float(tr.groupby('code')['pnl'].sum().max() / pos_pnl) if pos_pnl > 0 else np.nan
        r['top5_events_share_of_gains'] = float(tr['pnl'].nlargest(5).sum() / pos_pnl) if pos_pnl > 0 else np.nan
        ins = sel.set_index(sel.index)['owners'] if 'owners' in sel.columns else None
        if ins is not None:
            tr['owner'] = tr['event'].map(ins)
            r['top_insider_share_of_gains'] = float(tr.groupby('owner')['pnl'].sum().max() / pos_pnl) if pos_pnl > 0 else np.nan
        # removal of top contributors: re-simulate without the top 5 / 10 events by pnl
        for k in (5, 10):
            drop = set(tr.nlargest(k, 'pnl')['event'])
            sim = bt.simulate_slots(sel.drop(index=[i for i in drop if i in sel.index]), ao, cal, ended_info, venue)
            ws = bt.window_stats(bt.monthly_from_equity(sim['equity'], cal), bench_m, spy_m, rf)
            r[f'drop_top{k}_2013_excess'] = ws.get('w2013_2017', {}).get('excess_ann', np.nan); r[f'drop_top{k}_2013_t'] = ws.get('w2013_2017', {}).get('excess_t', np.nan)
        # amended originals excluded; timely only; late only
        for name, mask in (('exclude_later_amended', ~sel['later_amended']), ('timely_only', sel['timely']), ('late_only', ~sel['timely'])):
            sim = bt.simulate_slots(sel[mask], ao, cal, ended_info, venue)
            ws = bt.window_stats(bt.monthly_from_equity(sim['equity'], cal), bench_m, spy_m, rf)
            r[name] = dict(n=int(mask.sum()), excess_2013=ws.get('w2013_2017', {}).get('excess_ann', np.nan), t_2013=ws.get('w2013_2017', {}).get('excess_t', np.nan), excess_2009_2012=ws.get('w2009_2012', {}).get('excess_ann', np.nan))
        # factor loadings, liquidity, crash-timing
        net = monthly[cell].dropna()
        r['ff3_2013_2017'] = ff3_loadings(net['2013-01-01':'2017-12-31'], None); r['ff3_2009_2017'] = ff3_loadings(net['2009-01-01':'2017-12-31'], None)
        r['rank_quantiles'] = {q: float(sel['rank'].quantile(q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)}; r['share_rank_gt_500'] = float((sel['rank'] > 500).mean())
        dd_at_entry = spy_dd.iloc[sel['entry_idx'].to_numpy()].to_numpy()
        r['share_entries_spy_dd_gt_10pct'] = float(np.nanmean(dd_at_entry < -0.10)); r['share_entries_spy_dd_gt_20pct'] = float(np.nanmean(dd_at_entry < -0.20))
        r['median_purchase_value'] = float(sel['value'].median()); r['share_pit'] = float(sel['pit'].mean())
        # small capital
        for cap_eur in (500, 1000):
            sim = bt.simulate_slots(sel, ao, cal, ended_info, venue, capital=cap_eur * EUR_USD)
            trc = sim['trades']; eq = sim['equity']
            years = len(eq) / 252
            r[f'eur{cap_eur}'] = dict(final_multiple=float(eq.iloc[-1] / (cap_eur * EUR_USD)), median_trade_usd=float(trc['notional'].median()) if len(trc) else np.nan,
                                     skipped_min_order=sim['skipped_min'], skipped_full=sim['skipped_full'], n_trades=int(len(trc)),
                                     avg_simultaneous=float((trc['exit_idx'] - trc['entry_idx']).sum() / max(1, len(eq))) if len(trc) else 0.0,
                                     annual_cost_eur=float(trc['notional'].sum() * 2 * 0.00075 / years / EUR_USD) if len(trc) else 0.0,
                                     fractional_needed=True)
        out[cell] = r
        print(cell, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k in ('top_ticker_share_of_gains', 'top5_events_share_of_gains', 'top_insider_share_of_gains', 'drop_top5_2013_excess', 'drop_top10_2013_excess', 'share_rank_gt_500', 'share_entries_spy_dd_gt_10pct')},
              'ff3 2013-17', {k: round(v, 2) for k, v in r['ff3_2013_2017'].items()}, 'timely', r['timely_only']['excess_2013'], 'late', r['late_only']['excess_2013'], flush=True)
    # sector mix (PIT subset, current sector labels)
    labels = run.sector_labels()
    pit_ev = ev[ev['pit']]
    out['sector_mix_pit_subset'] = pit_ev['code'].map(labels).value_counts(normalize=True).round(3).to_dict()
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=dict(experiment='E058RT', stamp=stamp, base_run=run_name), results=out), indent=1, default=float), encoding='utf8')
    print(out_dir)


if __name__ == '__main__':
    main(sys.argv[1])
