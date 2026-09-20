"""E053-RT: red-team diagnostics for the E053 allocation architectures (development only; no new hypotheses).

(i) long history: SPY versus a cash leg earning the French one-month T-bill rate, 1994-01..2017-12, for the absolute-momentum
    (12-month) rule, the SMA10 rule and the volatility-managed rule (IEF does not exist before 2002-07);
(ii) parameter neighbourhood: lookback 6/9/12 months, SMA 8/10/12, vol window 21/63/126, all reported;
(iii) one-month execution delay (signal acted on at the open after the NEXT month-end);
(iv) start-year sensitivity: CAGR/DD versus SPY for start years 2005..2012 (G1a, G3 with IEF);
(v) year-by-year net return versus SPY for G1a, G3, G4.
Usage (from research/): PYTHONUTF8=1 python phase6b_etf_redteam.py
"""
from datetime import datetime, timezone
import json

import numpy as np
import pandas as pd

import phase6b_etf_allocation as al
import phase6_e051_run as run
from phase6_factor_screen import hac_alpha, sharpe, max_drawdown
from phase6_lock import ROOT


def cagr(x):
    x = x.dropna(); return float((1 + x).prod() ** (12 / len(x)) - 1) if len(x) else np.nan


def summarize(net, spy, rfm):
    net = net.dropna(); s = spy.reindex(net.index); r = rfm.reindex(net.index)
    return dict(start=str(net.index[0].date()), end=str(net.index[-1].date()), cagr=cagr(net), spy_cagr=cagr(s), sharpe=sharpe(net - r), spy_sharpe=sharpe(s - r),
                max_dd=max_drawdown(net), spy_max_dd=max_drawdown(s), alpha_t=hac_alpha(net - r, pd.DataFrame({'m': s - r}, index=net.index))['t'],
                cagr_2010=cagr(net['2010':'2017']), spy_cagr_2010=cagr(s['2010':'2017']), excess_2010_2017=float((net - s)['2010':'2017'].mean() * 12))


def cash_leg_returns(ret, rfm):
    """Returns frame with a synthetic CASH column earning the monthly RF."""
    out = ret.copy(); out['CASH'] = rfm.reindex(ret.index); return out


def rule_absmom(mp, rfm, lb, safe):
    r = mp['SPY'] / mp['SPY'].shift(lb) - 1
    rf = (1 + rfm).rolling(lb).apply(np.prod) - 1
    on = r > rf
    return pd.DataFrame({'SPY': on.astype(float), safe: (~on).astype(float)}, index=mp.index).where(r.notna())


def rule_sma(mp, n, safe):
    m = mp['SPY'].rolling(n).mean(); on = mp['SPY'] > m
    return pd.DataFrame({'SPY': on.astype(float), safe: (~on).astype(float)}, index=mp.index).where(m.notna())


def rule_vol(mp, rv, safe):
    target = rv.expanding(36).median().shift(1); w = (target / rv).clip(upper=1.0)
    return pd.DataFrame({'SPY': w, safe: 1 - w}, index=mp.index).where(w.notna())


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E053RT_{stamp}'; out_dir.mkdir(parents=True)
    rf = run.load_ff3()['RF']
    frames = al.load_frames()
    mp, ret, rv63, rfm = al.monthly_inputs(frames, rf)
    spy_daily = frames['SPY']['adj_close'].pct_change()
    rv = {w: (spy_daily.rolling(w).std().reindex(mp.index) * np.sqrt(252)) for w in (21, 63, 126)}
    retc = cash_leg_returns(ret, rfm)
    spy = ret['SPY']
    res = {}
    # (i) long history with cash leg, from 1994
    long_start = pd.Timestamp('1994-01-01')
    sel = mp.index >= long_start
    for name, w in [('absmom12_cash', rule_absmom(mp, rfm, 12, 'CASH')), ('sma10_cash', rule_sma(mp, 10, 'CASH')), ('vol63_cash', rule_vol(mp, rv[63], 'CASH'))]:
        m = al.simulate(w[sel], retc, al.COSTS['base'])
        res[f'long_{name}'] = summarize(m['net'], spy, rfm)
        res[f'long_{name}']['turnover_oneway_yr'] = float(m['turnover'].mean() * 6)
        yr = (1 + m['net']).groupby(m.index.year).prod() - 1; sy = (1 + spy.reindex(m.index)).groupby(m.index.year).prod() - 1
        res[f'long_{name}']['years_beating_spy'] = int((yr > sy).sum()); res[f'long_{name}']['years'] = int(len(yr))
        res[f'long_{name}']['yearly'] = {int(y): [round(float(a), 3), round(float(b), 3)] for y, a, b in zip(yr.index, yr, sy)}
    # (ii) neighbourhood with IEF from 2004 (and cash for vol windows where IEF exists)
    sel04 = mp.index >= al.START
    for lb in (6, 9, 12):
        m = al.simulate(rule_absmom(mp, rfm, lb, 'IEF')[sel04], ret, al.COSTS['base']); res[f'nb_absmom{lb}_IEF'] = summarize(m['net'], spy, rfm)
    for n in (8, 10, 12):
        m = al.simulate(rule_sma(mp, n, 'IEF')[sel04], ret, al.COSTS['base']); res[f'nb_sma{n}_IEF'] = summarize(m['net'], spy, rfm)
    for wdw in (21, 63, 126):
        m = al.simulate(rule_vol(mp, rv[wdw], 'IEF')[sel04], ret, al.COSTS['base']); res[f'nb_vol{wdw}_IEF'] = summarize(m['net'], spy, rfm)
    # (iii) one-month delay: weights shifted by one signal date
    for name, w in [('absmom12_IEF', rule_absmom(mp, rfm, 12, 'IEF')), ('sma10_IEF', rule_sma(mp, 10, 'IEF')), ('vol63_IEF', rule_vol(mp, rv[63], 'IEF'))]:
        m = al.simulate(w.shift(1)[sel04], ret, al.COSTS['base']); res[f'delay1_{name}'] = summarize(m['net'], spy, rfm)
        m2 = al.simulate(w[sel04], ret, al.COSTS['stress']); res[f'stress_{name}'] = summarize(m2['net'], spy, rfm)
    # (iv) start-year sensitivity
    for name, w in [('absmom12_IEF', rule_absmom(mp, rfm, 12, 'IEF')), ('vol63_IEF', rule_vol(mp, rv[63], 'IEF'))]:
        tab = {}
        for y in range(2005, 2013):
            m = al.simulate(w[mp.index >= pd.Timestamp(f'{y}-01-01')], ret, al.COSTS['base'])
            s = summarize(m['net'], spy, rfm); tab[y] = dict(cagr=round(s['cagr'], 4), spy=round(s['spy_cagr'], 4), dd=round(s['max_dd'], 3), spy_dd=round(s['spy_max_dd'], 3), alpha_t=round(s['alpha_t'], 2))
        res[f'startyear_{name}'] = tab
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=dict(experiment='E053RT', stamp=stamp), results=res), indent=1, default=float), encoding='utf8')
    for k, v in res.items():
        if k.startswith('startyear'):
            print(k, {y: (d['cagr'], d['spy'], d['dd']) for y, d in v.items()})
        else:
            print(f"{k:24} {v['start']}..{v['end']} CAGR {v['cagr']*100:5.1f} vs {v['spy_cagr']*100:5.1f} | Sh {v['sharpe']:.2f} vs {v['spy_sharpe']:.2f} | DD {v['max_dd']*100:4.0f} vs {v['spy_max_dd']*100:4.0f} | 2010-17 {v['cagr_2010']*100:5.1f} vs {v['spy_cagr_2010']*100:5.1f} | alpha t {v['alpha_t']:5.2f}"
                  + (f" | yrs>SPY {v['years_beating_spy']}/{v['years']}" if 'years' in v else ''))
    print(out_dir)


if __name__ == '__main__':
    main()
