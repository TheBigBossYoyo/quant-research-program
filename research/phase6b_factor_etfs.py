"""E052b: deployable factor-ETF proxies versus SPY on their development histories (diagnostic, no new stock-level hypotheses).

Buy-and-hold monthly total returns (adjusted close) of live US factor/dividend/low-vol ETFs against SPY over each ETF's
own development history (< 2018): excess CAGR, CAPM alpha t, drawdown, 2010-2017 excess, last 36 months. These ETFs are
the deployable form of families screened in E052 (dividend, low volatility, value, quality, momentum); their survival
is not a survivorship problem for an index-tracking comparison but the histories are short. Usage: PYTHONUTF8=1 python phase6b_factor_etfs.py
"""
from datetime import datetime, timezone
import json

import numpy as np
import pandas as pd

import phase6_eodhd as e
import phase6_eodhd_panel as pnl
import phase6_e051_run as run
from phase6_factor_screen import hac_alpha, hac_mean, sharpe, max_drawdown
from phase6_lock import ROOT, enforce

ETFS = {'DVY': 'dividend yield (Dow Jones Select Dividend)', 'SDY': 'dividend aristocrats (20y growers)', 'VIG': 'dividend growers (10y)', 'HDV': 'high dividend quality screen',
        'SCHD': 'dividend quality/yield', 'VTV': 'large value', 'VBR': 'small value', 'USMV': 'min volatility', 'SPLV': 'low volatility (100 lowest of S&P 500)',
        'QUAL': 'quality (ROE, leverage, earnings stability)', 'MTUM': 'momentum (reference only)'}


def cagr(x):
    x = x.dropna(); return float((1 + x).prod() ** (12 / len(x)) - 1) if len(x) else np.nan


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E052B_{stamp}'; out_dir.mkdir(parents=True)
    rf = run.load_ff3()['RF']
    frames = {}
    for man in ('phase6_eodhd_etf_manifest.json', 'phase6_eodhd_etf_manifest_6b.json'):
        for rec in json.loads((e.META / man).read_text(encoding='utf8')):
            if rec['code'] in ETFS or rec['code'] == 'SPY':
                frames[rec['code']] = enforce(pnl.read_eod_csv(ROOT / rec['file']), 'development')
    mo = {c: frames[c]['adj_close'].resample('ME').last().pct_change() for c in frames}
    spy = mo['SPY']
    res = {}
    for c, desc in ETFS.items():
        r = mo[c].dropna().iloc[1:]
        idx = r.index.intersection(spy.index)
        r, s = r.reindex(idx), spy.reindex(idx)
        rfm = rf.reindex(idx.to_period('M')).to_numpy()
        ex = r - s
        d = dict(family=desc, start=str(idx[0].date()), end=str(idx[-1].date()), months=int(len(idx)), cagr=cagr(r), spy_cagr=cagr(s), excess_cagr=cagr(r) - cagr(s),
                 excess_t=hac_mean(ex)['t'], alpha_t=hac_alpha(r - rfm, pd.DataFrame({'m': s - rfm}, index=idx))['t'], beta=hac_alpha(r - rfm, pd.DataFrame({'m': s - rfm}, index=idx))['betas'][0],
                 max_dd=max_drawdown(r), spy_max_dd=max_drawdown(s), cagr_2010=cagr(r['2010':'2017']), spy_cagr_2010=cagr(s['2010':'2017']), last36_excess_ann=float(ex['2015':'2017'].mean() * 12),
                 sharpe=sharpe(r - rfm), spy_sharpe=sharpe(s - rfm))
        res[c] = d
        print(f"{c:5} {desc[:34]:34} {d['start']}..{d['end']} CAGR {d['cagr']*100:5.1f} vs SPY {d['spy_cagr']*100:5.1f} | alpha t {d['alpha_t']:5.2f} beta {d['beta']:.2f} | DD {d['max_dd']*100:4.0f} vs {d['spy_max_dd']*100:4.0f} | 2010-17 {d['cagr_2010']*100:5.1f} vs {d['spy_cagr_2010']*100:5.1f} | last36 {d['last36_excess_ann']*100:5.1f}")
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=dict(experiment='E052B', stamp=stamp), results=res), indent=1, default=float), encoding='utf8')
    print(out_dir)


if __name__ == '__main__':
    main()
