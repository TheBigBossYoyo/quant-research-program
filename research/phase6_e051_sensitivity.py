"""E051-SENS: preregistered universe-sensitivity diagnostic for the primary Tier 2 cells (post-E051, red-team stage).

PHASE6_UNIVERSE_CONSTRUCTION.md section 3 fixed the liquidity rank cap N = 1000 with a sensitivity band {500, 1500} and
the price floor USD 5 with a band {3, 10}. E051 is closed and its decision stands; this script asks a red-team question
only: does the null result depend on the speculative tail of the dollar-volume universe? It runs the 12-1 momentum top-30
and the volatility-scaled momentum top-30 on (a) rank cap 500 and (b) price floor USD 10, same everything else, and reports
the same statistics. Four cells, counted in the ledger as diagnostics (cumulative 422 -> 426). They cannot reopen the gate.

Usage (from research/): PYTHONUTF8=1 python phase6_e051_sensitivity.py --t2-start 1998
"""
from datetime import datetime, timezone
import argparse
import json

import numpy as np
import pandas as pd

import phase6_eodhd_panel as pnl
import phase6_stock_universe as su
import phase6_stock_engine as se
import phase6_e051_run as run
from phase6_lock import ROOT, assert_development

CELLS = [('SENS_rank500_mom12_N30', 'mom12', dict(RANK_CAP=500)), ('SENS_rank500_volmom12_N30', 'volmom12', dict(RANK_CAP=500)),
         ('SENS_price10_mom12_N30', 'mom12', dict(MIN_PRICE=10.0)), ('SENS_price10_volmom12_N30', 'volmom12', dict(MIN_PRICE=10.0))]


def main(t2_start_year, boot_draws):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E051SENS_{stamp}'
    out_dir.mkdir(parents=True)
    close = pnl.load_panel('close'); open_ = pnl.load_panel('open'); adj = pnl.load_panel('adj_close')
    vol = pnl.load_panel('volume'); sf = pnl.load_panel('split_factor')
    for p in (close, open_, adj, vol, sf):
        assert_development(p.index)
    cal = su.trading_calendar(close)
    close, open_, adj, vol, sf = (x.reindex(cal) for x in (close, open_, adj, vol, sf))
    me = su.month_end_dates(cal); sig = me[:-1]; ex = su.next_open_dates(cal, sig)
    ret, ended = su.holding_returns(open_, close, adj, ex, cal, run.DEV_END, split_factor=sf)
    sig_used = sig[:len(ret)]
    integrity = su.integrity_panels(close, adj, sf, sig_used)
    feats = su.features_at(sig_used, close, adj, vol, sf, integrity=integrity)
    mp = su.monthly_prices(adj, sig_used)
    scores = dict(mom12=su.momentum(mp, 12, 1))
    scores['volmom12'] = scores['mom12'] / su.realized_vol_12m(mp)
    venue = su.load_last_venue()
    haircut = lambda info, v: su.delisting_haircut(info, v, 'base')
    frames = run.load_etf_frames()
    etf_mp, etf_ret, _ = run.etf_monthly(frames, ['SPY'], sig_used, ex)
    spy = etf_ret['SPY'].copy(); spy.index = sig_used[:len(spy)]
    rf = run.load_ff3()['RF']
    results, monthly = {}, {}
    defaults = dict(RANK_CAP=su.RANK_CAP, MIN_PRICE=su.MIN_PRICE)
    for cell, key, override in CELLS:
        for k, v in override.items():
            setattr(su, k, v)
        E, R = [], []
        for t in sig_used:
            ok, rk = su.eligibility(feats[t])
            if t.year < t2_start_year:
                ok[:] = False
            E.append(ok.rename(t)); R.append(rk.rename(t))
        elig = pd.DataFrame(E).reindex(columns=close.columns).fillna(False).astype(bool)
        rank = pd.DataFrame(R).reindex(columns=close.columns)
        for k, v in defaults.items():
            setattr(su, k, v)
        b = se.equal_weight_benchmark(elig, ret, ended=ended, venue=venue, haircut=haircut)
        bench = b['net'][b['n_held'] > 0]
        stats = {}
        for cc in ('optimistic', 'base', 'stress'):
            o = se.simulate(scores[key], elig, ret, rank=rank, n=30, ended=ended, venue=venue, haircut=haircut, cost_case=cc)
            m = o['monthly']; m = m[m['n_held'] > 0]
            stats[cc] = run.stats_block(m['net'], bench, spy, rf, boot_draws)
            if cc == 'base':
                monthly[cell] = m['net']
        results[cell] = dict(override=override, stats=stats, survivor=run.survivor(stats['base'], stats['stress'], len(monthly[cell])),
                             bench=se.ann_stats(bench), eligible_median=float(elig.sum(axis=1)[elig.sum(axis=1) > 0].median()))
        sb = stats['base']
        print(f"{cell}: net CAGR {sb['net']['cagr']:.3f} Sharpe {sb['net']['sharpe']:.2f} DD {sb['net']['max_dd']:.2f} excess-EW/yr {sb['excess_ew']['mean']*12:.3f} t {sb['excess_ew']['t']:.2f} "
              f"eras {{{', '.join(f'{k}:{v['mean']*12:.3f}' for k, v in sb['eras'].items())}}} bench CAGR {sb['bench']['cagr']:.3f}", flush=True)
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=dict(experiment='E051SENS', stamp=stamp, t2_start_year=t2_start_year, boot_draws=boot_draws,
                                                                    cells=[c[0] for c in CELLS]), results=results), indent=1, default=float), encoding='utf8')
    pd.DataFrame(monthly).to_csv(out_dir / 'monthly_net.csv')
    print(out_dir)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--t2-start', type=int, required=True); ap.add_argument('--boot', type=int, default=2000)
    a = ap.parse_args(); main(a.t2_start, a.boot)
