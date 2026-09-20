"""E057: portfolio stage for the low-realized-risk family (S7 idio vol primary; S6 range, S9 MAX neighbours), development only.

Preregistered in EXPERIMENTS.md (2026-09-12). Reuses the E051 engine: Tier 2 LIQ1000 from 1998, top-N long-only,
monthly or quarterly rebalance, next-open execution, three cost cases, three delisting rules, gates S0-S6 + multiplicity.
Usage (from research/): PYTHONUTF8=1 python phase7a_lowrisk_portfolio.py --t2-start 1998
"""
from datetime import datetime, timezone
import argparse
import json

import numpy as np
import pandas as pd
from scipy import stats as sps

import phase6_eodhd_panel as pnl
import phase6_stock_universe as su
import phase6_stock_engine as se
import phase6_e051_run as run
import phase7a_xs_screen as xs
from phase6_lock import ROOT, assert_development

CELLS = [(f'LR_{sid}_N{n}_{reb}', sid, n, reb) for sid in ('S7', 'S6', 'S9') for n in (30, 50) for reb in ('M', 'Q')]
N_PHASE7A_TRIALS = 24


def quarterly_scores(scores, elig, n):
    """Selection refreshed at Mar/Jun/Sep/Dec signal dates; carried forward otherwise (only names still eligible)."""
    out = pd.DataFrame(np.nan, index=scores.index, columns=scores.columns)
    held = []
    for t in scores.index:
        if t.month in (3, 6, 9, 12) or not held:
            held = se.select_top(scores.loc[t], elig.loc[t], n)
        else:
            held = [c for c in held if bool(elig.loc[t, c])]
        out.loc[t, held] = 1.0
    return out


def main(t2_start, boot):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E057_{stamp}'; out_dir.mkdir(parents=True)
    close = pnl.load_panel('close'); open_ = pnl.load_panel('open'); adj = pnl.load_panel('adj_close'); vol = pnl.load_panel('volume'); sf = pnl.load_panel('split_factor')
    for p in (close, open_, adj, vol, sf):
        assert_development(p.index)
    cal = su.trading_calendar(close)
    close, open_, adj, vol, sf = (x.reindex(cal) for x in (close, open_, adj, vol, sf))
    me = su.month_end_dates(cal); sig = me[:-1]; ex = su.next_open_dates(cal, sig)
    ret, ended = su.holding_returns(open_, close, adj, ex, cal, run.DEV_END, split_factor=sf)
    sig_used = sig[:len(ret)]
    integrity = su.integrity_panels(close, adj, sf, sig_used)
    feats = su.features_at(sig_used, close, adj, vol, sf, integrity=integrity)
    membership = su.constituent_membership(sig_used)
    elig, rank = {}, {}
    for tier in ('LIQ1000', 'PIT_SP1500'):
        E, R = [], []
        for t in sig_used:
            if tier == 'LIQ1000':
                ok, rk = su.eligibility(feats[t]); ok[:] = ok & (t.year >= t2_start)
            else:
                ok, rk = su.eligibility(feats[t], membership=membership.loc[t] if t in membership.index else None, liquidity_rank=False)
                if t < su.PIT_FIRST_SIGNAL:
                    ok[:] = False
            E.append(ok.rename(t)); R.append(rk.rename(t))
        elig[tier] = pd.DataFrame(E).reindex(columns=close.columns).fillna(False).astype(bool)
        rank[tier] = pd.DataFrame(R).reindex(columns=close.columns)
    frames = run.load_etf_frames()
    spy_daily = frames['SPY']['adj_close'].pct_change()
    sigs = xs.signals_at(sig_used, cal, open_, close, adj, vol, sf, feats, spy_daily)
    scores = {sid: -sigs[sid] for sid in ('S7', 'S6', 'S9')}   # LOW bucket -> higher score
    venue = su.load_last_venue()
    haircuts = {m: (lambda info, v, m=m: su.delisting_haircut(info, v, m)) for m in ('base', 'all100', 'all30')}
    _, etf_ret, _ = run.etf_monthly(frames, ['SPY'] + run.SECTOR_ETFS, sig_used, ex)
    spy = etf_ret['SPY'].copy(); spy.index = sig_used[:len(spy)]
    sector_rets = etf_ret[run.SECTOR_ETFS].copy(); sector_rets.index = sig_used[:len(sector_rets)]
    rf = run.load_ff3()['RF']
    benches = {}
    for tier in elig:
        b = se.equal_weight_benchmark(elig[tier], ret, ended=ended, venue=venue, haircut=haircuts['base']); benches[tier] = b['net'][b['n_held'] > 0]
    results, monthly = {}, {}
    cells = CELLS + [('LR_S7_N30_M_TIER1', 'S7', 30, 'M')]
    for cell, sid, n, reb in cells:
        tier = 'PIT_SP1500' if cell.endswith('TIER1') else 'LIQ1000'
        sc = scores[sid].where(elig[tier]) if reb == 'M' else quarterly_scores(scores[sid].where(elig[tier]), elig[tier], n)
        el = elig[tier] if reb == 'M' else (sc.notna())
        runs = {}
        for cc in ('optimistic', 'base', 'stress'):
            runs[(cc, 'base')] = se.simulate(sc, el, ret, rank=rank[tier], n=n, ended=ended, venue=venue, haircut=haircuts['base'], cost_case=cc)
        for hm in ('all100', 'all30'):
            runs[('base', hm)] = se.simulate(sc, el, ret, rank=rank[tier], n=n, ended=ended, venue=venue, haircut=haircuts[hm], cost_case='base')
        per = {}
        for (cc, hm), r in runs.items():
            m = r['monthly']; m = m[m['n_held'] > 0]
            per[f'{cc}|{hm}'] = run.stats_block(m['net'], benches[tier], spy, rf, boot)
            per[f'{cc}|{hm}']['turnover_oneway_yr'] = float((m['turnover_buy'] + m['turnover_sell']).mean() * 6); per[f'{cc}|{hm}']['cost_yr'] = float(m['cost'].mean() * 12)
        mb = runs[('base', 'base')]['monthly']; mb = mb[mb['n_held'] > 0]
        sb = per['base|base']
        sv = run.survivor(sb, per['stress|base'], len(mb))
        contrib = runs[('base', 'base')]['contributions'].reindex(mb.index); tot = float(contrib.sum().sum())
        top = (contrib.sum() / tot).sort_values(ascending=False).head(10) if tot > 0 else pd.Series(dtype=float)
        results[cell] = dict(signal=sid, N=n, rebalance=reb, tier=tier, stats=per, survivor=sv, sector_betas=run.sector_betas(mb['net'], sector_rets, rf),
                             top10_name_share=float(top.sum()) if len(top) else np.nan, avg_held=float(mb['n_held'].mean()),
                             feasibility={c: run.feasibility(mb, n, c, run.GATES['eur_usd']) for c in (500, 1000)})
        monthly[cell] = mb['net']
        print(f"{cell:20} months {len(mb)} net CAGR {sb['net']['cagr']*100:5.1f} vs EW {sb['bench']['cagr']*100:5.1f} vs SPY {sb['spy']['cagr']*100:5.1f} | Sharpe {sb['net']['sharpe']:.2f} vs SPY {sb['spy']['sharpe']:.2f} | DD {sb['net']['max_dd']*100:4.0f} vs {sb['spy']['max_dd']*100:4.0f} | "
              f"excess-EW {sb['excess_ew']['mean']*1200:5.2f}%/yr t {sb['excess_ew']['t']:5.2f} | alpha-SPY t {sb['capm_vs_spy']['t']:5.2f} beta {sb['capm_vs_spy']['betas'][0]:.2f} | 2000-17 {sb['cagr_2000_2017']['net']*100:5.1f} vs SPY {sb['cagr_2000_2017']['spy']*100:5.1f} | "
              f"E4 {sb['eras'].get('E4', {}).get('net_cagr', np.nan)*100:5.1f} | last36 {sb['recent_36m']['mean']*1200:5.1f} | to {sb['turnover_oneway_yr']:.1f}x | fails {[k for k, v in sv['checks'].items() if not v]}", flush=True)
    core = [c for c in results if not c.endswith('TIER1')]
    pv = {c: 1 - sps.norm.cdf(results[c]['stats']['base|base']['excess_ew']['t']) for c in core}
    bh = run.bh_fdr(pv, run.GATES['bh_fdr'])
    srs = [results[c]['stats']['base|base']['net']['sharpe'] for c in core]
    for c in core:
        net = monthly[c]
        results[c]['bh_pass'] = c in bh
        results[c]['dsr'] = dict(zip(('prob', 'sr0_annual'), run.deflated_sharpe(results[c]['stats']['base|base']['net']['sharpe'], len(net), N_PHASE7A_TRIALS, float(np.var(srs, ddof=1)), float(sps.skew(net)), float(sps.kurtosis(net, fisher=False)))))
        results[c]['survivor']['multiplicity_pass'] = bool(results[c]['bh_pass'] and results[c]['dsr']['prob'] >= run.GATES['dsr_min'])
        results[c]['survivor']['final'] = bool(results[c]['survivor']['passes'] and results[c]['survivor']['multiplicity_pass'])
        print(c, 'BH', results[c]['bh_pass'], 'DSR', round(results[c]['dsr']['prob'], 3), 'FINAL', results[c]['survivor']['final'])
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=dict(experiment='E057', stamp=stamp, t2_start=t2_start, boot=boot, cells=[c[0] for c in cells], gates=run.GATES, n_trials_dsr=N_PHASE7A_TRIALS,
                                                                    benchmarks={k: se.ann_stats(v) for k, v in benches.items()}), results=results), indent=1, default=float), encoding='utf8')
    pd.DataFrame(monthly).to_csv(out_dir / 'monthly_net.csv'); pd.DataFrame(benches).to_csv(out_dir / 'benchmarks_monthly.csv'); spy.to_csv(out_dir / 'spy_monthly.csv')
    print(out_dir)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--t2-start', type=int, default=1998); ap.add_argument('--boot', type=int, default=2000); a = ap.parse_args()
    main(a.t2_start, a.boot)
