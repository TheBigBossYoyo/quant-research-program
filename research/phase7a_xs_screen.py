"""E055: Phase 7A cross-sectional screen of nine preregistered price/volume families (development only, gross).

Signals are evaluated at the month-end close with inputs <= t; the dependent variable is the open-to-open return
of the following month (same holding returns as E051, integrity rule I5 applied, no delisting haircut at this stage).
Tier 2 LIQ1000 from 1998, Tier 1 PIT_SP1500 from 2012-04. For each signal and tier: Fama-MacBeth slope of the return
on the rank-normalised signal, top-decile (in the preregistered direction) equal-weight gross excess over the EW eligible
universe, decile monotonicity. Advance gate A per PHASE7A_PLAN.md section 2.
Usage (from research/): PYTHONUTF8=1 python phase7a_xs_screen.py --t2-start 1998
"""
from datetime import datetime, timezone
import argparse
import json

import numpy as np
import pandas as pd
from scipy import stats as sps

import phase6_eodhd_panel as pnl
import phase6_stock_universe as su
import phase6_e051_run as run
from phase6_factor_screen import hac_mean
from phase6_lock import ROOT, assert_development

SIGNALS = {  # id: (name, direction of the long bucket: +1 high, -1 low)
    'S1': ('52wk_high_proximity', +1), 'S2': ('overnight_12m', +1), 'S3': ('intraday_12m', -1), 'S4': ('abnormal_volume_1m_12m', +1),
    'S5': ('liquidity_level_63d', -1), 'S6': ('range_21d', -1), 'S7': ('idio_vol_63d', -1), 'S8': ('beta_252d', -1), 'S9': ('max_ret_21d', -1),
}
WINDOWS = {'w1998': ('1998-01-01', '2017-12-31'), 'w2000': ('2000-01-01', '2017-12-31'), 'w2010': ('2010-01-01', '2017-12-31'), 'w2012': ('2012-04-01', '2017-12-31')}
GATE = dict(a1_excess_2010=0.02, a2_t_2000=1.5)


def daily_components(open_, close, sf):
    so, sc = open_ / sf, close / sf
    overnight = np.log(so / sc.shift(1))
    intraday = np.log(sc / so)
    return so, sc, overnight, intraday


def signals_at(sig_dates, cal, open_, close, adj, vol, sf, feats, spy_daily):
    so, sc, overnight, intraday = daily_components(open_, close, sf)
    dv = sc * vol
    dret = adj.pct_change()
    out = {k: {} for k in SIGNALS}
    m = spy_daily.reindex(cal).to_numpy()
    for t in sig_dates:
        i = cal.get_loc(t)
        w252 = slice(max(0, i - 251), i + 1)
        w63 = slice(max(0, i - 62), i + 1)
        w21 = slice(max(0, i - 20), i + 1)
        scw = sc.iloc[w252]
        out['S1'][t] = sc.iloc[i] / scw.max(axis=0)
        out['S2'][t] = overnight.iloc[w252].sum(axis=0, min_count=200)
        out['S3'][t] = intraday.iloc[w252].sum(axis=0, min_count=200)
        out['S4'][t] = dv.iloc[w21].mean(axis=0) / dv.iloc[w252].mean(axis=0)
        out['S5'][t] = feats[t]['med_dv']
        w = sc.iloc[w21]
        out['S6'][t] = (w.max(axis=0) - w.min(axis=0)) / sc.iloc[i]
        # 63-day idiosyncratic vol and 252-day beta versus SPY (vectorised OLS)
        for key, sl in (('S7', w63), ('S8', w252)):
            Y = dret.iloc[sl].to_numpy(dtype=float)
            x = m[sl]
            ok = np.isfinite(x)
            Y, x = Y[ok], x[ok]
            xm = x - x.mean()
            valid = np.isfinite(Y)
            Yz = np.where(valid, Y, 0.0)
            n = valid.sum(axis=0)
            ym = Yz.sum(axis=0) / np.maximum(n, 1)
            cov = ((Yz - ym) * valid * xm[:, None]).sum(axis=0)
            varx = ((xm ** 2)[:, None] * valid).sum(axis=0)
            beta = cov / np.where(varx > 0, varx, np.nan)
            if key == 'S8':
                s = pd.Series(beta, index=dret.columns)
                s[n < 200] = np.nan
                out['S8'][t] = s
            else:
                resid = (Yz - ym) - beta * xm[:, None]
                resid[~valid] = 0.0
                ivol = np.sqrt((resid ** 2).sum(axis=0) / np.maximum(n - 2, 1))
                s = pd.Series(ivol, index=dret.columns)
                s[n < 50] = np.nan
                out['S7'][t] = s
        out['S9'][t] = dret.iloc[w21].max(axis=0)
    return {k: pd.DataFrame(v).T for k, v in out.items()}


def screen(signal, direction, elig, ret, tiers_start=None):
    """Monthly FM slope and top-decile excess for one signal on one eligibility frame."""
    rows = []
    dec_means = []
    for k, t in enumerate(elig.index):
        e = elig.loc[t]
        if e.sum() < 100:
            continue
        s = signal.loc[t].reindex(e.index).where(e)
        r = ret.iloc[k].reindex(e.index).where(e)
        ok = s.notna() & r.notna()
        if ok.sum() < 100:
            continue
        s, r = s[ok], r[ok]
        rank = s.rank(pct=True) * direction
        rank = rank - rank.mean()
        slope = float((rank * (r - r.mean())).sum() / (rank ** 2).sum())
        dec = pd.qcut(s.rank(method='first') * direction, 10, labels=False)
        dm = r.groupby(dec).mean()
        top = float(dm.iloc[-1]) if len(dm) == 10 else np.nan
        rows.append(dict(t=t, slope=slope, top_excess=top - float(r.mean()), universe=float(r.mean()), n=int(ok.sum())))
        if len(dm) == 10:
            dec_means.append(dm.to_numpy())
    df = pd.DataFrame(rows).set_index('t')
    out = {}
    for w, (a, b) in WINDOWS.items():
        x = df[a:b]
        if len(x) < 24:
            continue
        out[w] = dict(months=int(len(x)), slope_t=hac_mean(x['slope'])['t'], slope_mean=float(x['slope'].mean()),
                      top_excess_ann=float(x['top_excess'].mean() * 12), top_excess_t=hac_mean(x['top_excess'])['t'],
                      top_cagr=float((1 + x['top_excess'] + x['universe']).prod() ** (12 / len(x)) - 1), universe_cagr=float((1 + x['universe']).prod() ** (12 / len(x)) - 1))
    dm = np.nanmean(np.array(dec_means), axis=0) if dec_means else None
    out['decile_means_ann'] = [float(v * 12) for v in dm] if dm is not None else None
    out['spearman_deciles'] = float(sps.spearmanr(np.arange(10), dm)[0]) if dm is not None else np.nan
    return out


def main(t2_start, out_name='E055'):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'{out_name}_{stamp}'
    out_dir.mkdir(parents=True)
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
    elig = {}
    for tier in ('LIQ1000', 'PIT_SP1500'):
        E = []
        for t in sig_used:
            if tier == 'LIQ1000':
                ok, _ = su.eligibility(feats[t]); ok[:] = ok & (t.year >= t2_start)
            else:
                ok, _ = su.eligibility(feats[t], membership=membership.loc[t] if t in membership.index else None, liquidity_rank=False)
                if t < su.PIT_FIRST_SIGNAL:
                    ok[:] = False
            E.append(ok.rename(t))
        elig[tier] = pd.DataFrame(E).reindex(columns=close.columns).fillna(False).astype(bool)
    frames = run.load_etf_frames()
    spy_daily = frames['SPY']['adj_close'].pct_change()
    print('computing signals', flush=True)
    sigs = signals_at(sig_used, cal, open_, close, adj, vol, sf, feats, spy_daily)
    results = {}
    for sid, (name, direction) in SIGNALS.items():
        res = dict(name=name, direction=direction)
        for tier in ('LIQ1000', 'PIT_SP1500'):
            res[tier] = screen(sigs[sid], direction, elig[tier], ret)
        t2, t1 = res['LIQ1000'], res['PIT_SP1500']
        gate = dict(a1_excess_2010=t2.get('w2010', {}).get('top_excess_ann', np.nan) >= GATE['a1_excess_2010'],
                    a2_t_2000=t2.get('w2000', {}).get('top_excess_t', np.nan) >= GATE['a2_t_2000'],
                    a3_sign=(t2.get('w2000', {}).get('slope_mean', 0) > 0) and (t2.get('w2010', {}).get('slope_mean', 0) > 0),
                    a4_tier1=t1.get('w2012', {}).get('top_excess_ann', np.nan) >= 0)
        gate['passes'] = all(bool(v) for v in gate.values())
        res['gate_A'] = {k: bool(v) for k, v in gate.items()}
        results[sid] = res
        w0, w1, w2 = t2.get('w1998', {}), t2.get('w2000', {}), t2.get('w2010', {})
        print(f"{sid} {name:24} T2 1998-17 top-dec excess {w0.get('top_excess_ann', np.nan)*100:6.2f}%/yr t {w0.get('top_excess_t', np.nan):5.2f} | 2000-17 {w1.get('top_excess_ann', np.nan)*100:6.2f}% t {w1.get('top_excess_t', np.nan):5.2f} slope t {w1.get('slope_t', np.nan):5.2f} | "
              f"2010-17 {w2.get('top_excess_ann', np.nan)*100:6.2f}% t {w2.get('top_excess_t', np.nan):5.2f} | rho {t2['spearman_deciles']:5.2f} | T1 2012-17 {t1.get('w2012', {}).get('top_excess_ann', np.nan)*100:6.2f}% t {t1.get('w2012', {}).get('top_excess_t', np.nan):5.2f} | gate {gate['passes']}", flush=True)
    meta = dict(experiment=out_name, stamp=stamp, t2_start=t2_start, signals=SIGNALS, gate=GATE, windows=WINDOWS, signals_n=len(sig_used),
                eligible_median={k: float(v.sum(axis=1)[v.sum(axis=1) > 0].median()) for k, v in elig.items()})
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=meta, results=results), indent=1, default=float), encoding='utf8')
    print(out_dir)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--t2-start', type=int, default=1998); a = ap.parse_args()
    main(a.t2_start)
