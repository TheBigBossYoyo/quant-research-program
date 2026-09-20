"""E053: Phase 6B ETF allocation architectures on EODHD US ETFs (development only, preregistered 2026-09-12).

Monthly signals at the month-end close; trades at the next open (open-to-open holding returns from adjusted opens);
2004-01..2017-12 (every leg exists from 2004-11 when GLD starts; G4 starts 2004-12, others 2004-01 unless stated);
base cost 20 bps per side of traded notional (also optimistic 3 / stress 30); benchmarks SPY buy-and-hold and 60/40
SPY/AGG rebalanced quarterly. US ETFs are signal/return proxies for the UCITS lines Trading 212 offers.
Usage (from research/): PYTHONUTF8=1 python phase6b_etf_allocation.py
"""
from datetime import datetime, timezone
import json

import numpy as np
import pandas as pd

import phase6_eodhd as e
import phase6_eodhd_panel as pnl
import phase6_stock_universe as su
import phase6_e051_run as run
from phase6_factor_screen import hac_mean, hac_alpha, sharpe, max_drawdown
from phase6_lock import ROOT, enforce, assert_development

CODES = ['SPY', 'IEF', 'AGG', 'EFA', 'GLD', 'XLP', 'XLV', 'XLU', 'TLT', 'SHY']
COSTS = {'optimistic': 0.0003, 'base': 0.0020, 'stress': 0.0030}
START = pd.Timestamp('2004-01-01')
GATES = dict(cagr_vs_spy_pts=-0.01, dd_shallower_pts=0.15, cagr_2010_share=0.70, max_turnover=2.0)


def load_frames():
    frames = {}
    for man in ('phase6_eodhd_etf_manifest.json', 'phase6_eodhd_etf_manifest_6b.json'):
        for rec in json.loads((e.META / man).read_text(encoding='utf8')):
            if rec['code'] in CODES:
                frames[rec['code']] = enforce(pnl.read_eod_csv(ROOT / rec['file']), 'development')
    return frames


def monthly_inputs(frames, rf):
    close = pd.DataFrame({c: frames[c]['close'] for c in CODES})
    open_ = pd.DataFrame({c: frames[c]['open'] for c in CODES})
    adj = pd.DataFrame({c: frames[c]['adj_close'] for c in CODES})
    cal = close.index[close['SPY'].notna()]
    close, open_, adj = (x.reindex(cal) for x in (close, open_, adj))
    me = su.month_end_dates(cal)
    sig = me[:-1]
    ex = su.next_open_dates(cal, sig)
    ao = open_ * adj / close
    ret = pd.DataFrame({c: ao[c].reindex(ex).pct_change().shift(-1) for c in CODES}).iloc[:-1]
    ret.index = sig[:len(ret)]
    mp = adj.reindex(sig[:len(ret)])
    daily = adj.pct_change()
    rv63 = daily['SPY'].rolling(63).std().reindex(sig[:len(ret)]) * np.sqrt(252)
    per = pd.DatetimeIndex(mp.index).to_period('M')
    rfm = rf.reindex(per).to_numpy()
    return mp, ret, rv63, pd.Series(rfm, index=mp.index)


def weights_g1a(mp, rfm):
    r12 = mp['SPY'] / mp['SPY'].shift(12) - 1
    rf12 = (1 + rfm).rolling(12).apply(np.prod) - 1
    on = (r12 > rf12)
    return pd.DataFrame({'SPY': on.astype(float), 'IEF': (~on).astype(float)}, index=mp.index).where(r12.notna())


def weights_g1b(mp, rfm):
    on = mp['SPY'] > mp['SPY'].rolling(10).mean()
    return pd.DataFrame({'SPY': on.astype(float), 'IEF': (~on).astype(float)}, index=mp.index).where(mp['SPY'].rolling(10).mean().notna())


def weights_g2(mp, rfm):
    r12 = mp[['SPY', 'EFA']] / mp[['SPY', 'EFA']].shift(12) - 1
    rf12 = (1 + rfm).rolling(12).apply(np.prod) - 1
    best = r12.idxmax(axis=1)
    best_r = r12.max(axis=1)
    w = pd.DataFrame(0.0, index=mp.index, columns=['SPY', 'EFA', 'AGG'])
    for t in mp.index:
        if pd.isna(best_r.loc[t]):
            w.loc[t] = np.nan
        elif best_r.loc[t] > rf12.loc[t]:
            w.loc[t, best.loc[t]] = 1.0
        else:
            w.loc[t, 'AGG'] = 1.0
    return w


def weights_g3(mp, rfm, rv63):
    target = rv63.expanding(36).median().shift(1)
    wspy = (target / rv63).clip(upper=1.0)
    return pd.DataFrame({'SPY': wspy, 'IEF': 1.0 - wspy}, index=mp.index).where(wspy.notna())


def weights_g4(mp, rfm):
    w = pd.DataFrame(np.nan, index=mp.index, columns=['SPY', 'IEF', 'GLD'])
    ok = mp[['SPY', 'IEF', 'GLD']].notna().all(axis=1)
    w.loc[ok] = [0.6, 0.3, 0.1]
    return w


def weights_g5(mp, rfm):
    on = mp['SPY'] > mp['SPY'].rolling(10).mean()
    w = pd.DataFrame(0.0, index=mp.index, columns=['SPY', 'XLP', 'XLV', 'XLU'])
    w.loc[on, 'SPY'] = 1.0
    w.loc[~on, ['XLP', 'XLV', 'XLU']] = 1.0 / 3
    return w.where(mp['SPY'].rolling(10).mean().notna())


def weights_bench60_40(mp, rfm):
    w = pd.DataFrame(np.nan, index=mp.index, columns=['SPY', 'AGG'])
    ok = mp[['SPY', 'AGG']].notna().all(axis=1)
    w.loc[ok] = [0.6, 0.4]
    return w


def simulate(weights, ret, cost, rebalance='monthly', drift=True):
    """Target weights at each signal date; positions drift within the month; rebalance to target monthly (or
    quarterly: only in Mar/Jun/Sep/Dec signal months, otherwise hold the drifted weights)."""
    cols = weights.columns
    prev = pd.Series(0.0, index=cols)
    rows = []
    for t in weights.index:
        target = weights.loc[t]
        if target.isna().any():
            continue
        is_rebal = (rebalance == 'monthly') or (t.month in (3, 6, 9, 12)) or prev.sum() == 0
        w = target if is_rebal else prev
        delta = (w - prev).abs().sum() if is_rebal else 0.0
        r = ret.loc[t, cols].fillna(0.0)
        gross = float((w * r).sum())
        c = float(delta * cost)
        net = (1 - c) * (1 + gross) - 1
        rows.append(dict(signal=t, gross=gross, net=net, cost=c, turnover=float(delta), w_spy=float(w.get('SPY', 0.0))))
        grown = w * (1 + r)
        prev = grown / grown.sum() if grown.sum() > 0 else w
    return pd.DataFrame(rows).set_index('signal')


def stats(net, spy, rfm):
    net = net.dropna(); idx = net.index; s = spy.reindex(idx); r = rfm.reindex(idx)
    a, b = '2010-01-01', '2017-12-31'
    def cagr(x):
        x = x.dropna(); return float((1 + x).prod() ** (12 / len(x)) - 1) if len(x) else np.nan
    capm = hac_alpha(net - r, pd.DataFrame({'m': s - r}, index=idx))
    roll = [net[:f'{y}-12-31'].tail(60) for y in range(2008, 2018)]
    roll = [(w, s.reindex(w.index)) for w in roll if len(w) == 60]
    return dict(months=int(len(net)), start=str(idx[0].date()), end=str(idx[-1].date()), cagr=cagr(net), spy_cagr=cagr(s), sharpe=sharpe(net - r), spy_sharpe=sharpe(s - r),
                max_dd=max_drawdown(net), spy_max_dd=max_drawdown(s), cagr_2010=cagr(net[a:b]), spy_cagr_2010=cagr(s[a:b]),
                excess_vs_spy=hac_mean(net - s), capm_alpha=capm, worst_12m=float((1 + net).rolling(12).apply(np.prod).min() - 1),
                rolling60_excess_positive_share=float(np.mean([w.mean() > sp.mean() for w, sp in roll])) if roll else np.nan,
                last36_excess_ann=float((net - s)['2015-01-01':'2017-12-31'].mean() * 12))


def gate(st, turnover):
    g = GATES
    checks = dict(cagr=st['cagr'] >= st['spy_cagr'] + g['cagr_vs_spy_pts'], dd=st['max_dd'] >= st['spy_max_dd'] + g['dd_shallower_pts'],
                  cagr_2010=st['cagr_2010'] >= g['cagr_2010_share'] * st['spy_cagr_2010'], turnover=turnover <= g['max_turnover'])
    return dict(checks={k: bool(v) for k, v in checks.items()}, passes=all(checks.values()))


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E053_{stamp}'
    out_dir.mkdir(parents=True)
    rf = run.load_ff3()['RF']
    frames = load_frames()
    mp, ret, rv63, rfm = monthly_inputs(frames, rf)
    for x in (mp, ret):
        assert_development(x.index)
    mp, ret, rv63, rfm = (x[x.index >= START] for x in (mp, ret, rv63, rfm))
    spy = ret['SPY']
    arch = {'G1a_absmom12_SPY_IEF': (weights_g1a(mp, rfm), 'monthly'), 'G1b_sma10_SPY_IEF': (weights_g1b(mp, rfm), 'monthly'),
            'G2_dualmom_SPY_EFA_AGG': (weights_g2(mp, rfm), 'monthly'), 'G3_volmanaged_SPY_IEF': (weights_g3(mp, rfm, rv63), 'monthly'),
            'G4_static_60_30_10_q': (weights_g4(mp, rfm), 'quarterly'), 'G5_regime_SPY_defensive': (weights_g5(mp, rfm), 'monthly')}
    bench = {'SPY': simulate(pd.DataFrame({'SPY': 1.0}, index=mp.index), ret, 0.0, 'quarterly'),
             '60_40_q': simulate(weights_bench60_40(mp, rfm), ret, COSTS['base'], 'quarterly')}
    results, monthly = {}, {}
    for name, (w, reb) in arch.items():
        res = {}
        for cc, cost in COSTS.items():
            m = simulate(w, ret, cost, reb)
            st = stats(m['net'], spy, rfm)
            st['turnover_oneway_yr'] = float(m['turnover'].mean() * 12 / 2)
            st['cost_yr'] = float(m['cost'].mean() * 12)
            st['mean_w_spy'] = float(m['w_spy'].mean())
            res[cc] = st
            if cc == 'base':
                monthly[name] = m['net']
                res['gate'] = gate(st, st['turnover_oneway_yr'])
        results[name] = res
        b = res['base']
        print(f"{name:26} {b['start']}..{b['end']} CAGR {b['cagr']*100:5.1f} vs SPY {b['spy_cagr']*100:5.1f} | Sharpe {b['sharpe']:.2f} vs {b['spy_sharpe']:.2f} | DD {b['max_dd']*100:5.0f} vs {b['spy_max_dd']*100:5.0f} | "
              f"2010-17 {b['cagr_2010']*100:5.1f} vs {b['spy_cagr_2010']*100:5.1f} | alpha t {b['capm_alpha']['t']:5.2f} | to {b['turnover_oneway_yr']:.2f}/yr | last36 {b['last36_excess_ann']*100:5.1f} | gate {res['gate']['passes']}", flush=True)
    for name, m in bench.items():
        st = stats(m['net'], spy, rfm); results[f'BENCH_{name}'] = dict(base=st); monthly[f'BENCH_{name}'] = m['net']
        print(f"BENCH {name}: CAGR {st['cagr']*100:.1f} Sharpe {st['sharpe']:.2f} DD {st['max_dd']*100:.0f}")
    pv = {k: 1 - __import__('scipy').stats.norm.cdf(v['base']['capm_alpha']['t']) for k, v in results.items() if not k.startswith('BENCH')}
    bh = run.bh_fdr(pv, 0.05)
    for k in pv:
        results[k]['bh_pass'] = k in bh
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=dict(experiment='E053', stamp=stamp, start=str(START.date()), gates=GATES, costs=COSTS),
                                                          results=results), indent=1, default=float), encoding='utf8')
    pd.DataFrame(monthly).to_csv(out_dir / 'monthly_net.csv')
    print(out_dir)


if __name__ == '__main__':
    main()
