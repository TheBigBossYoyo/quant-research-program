"""E052: Phase 6B modern-evidence screen of economically distinct families on the French library (development only).

Preregistered in EXPERIMENTS.md / PHASE6B_PLAN.md (2026-09-12). Long-only value-weighted bucket minus the market
(Mkt-RF + RF), decision windows 2000-01..2017-12 and 2010-01..2017-12. Gate ME: 2000-2017 HAC t >= 1.0 and 2010-2017
mean >= 0. Every trial is reported. Usage (from research/): PYTHONUTF8=1 python phase6b_family_screen.py
"""
from datetime import datetime, timezone
import json

import numpy as np
import pandas as pd

import phase6_french as fr
from phase6_factor_screen import hac_mean, sharpe, max_drawdown, load_factors
from phase6_lock import ROOT, assert_development

WINDOWS = {'full': ('1963-07-01', '2017-12-31'), 'w2000': ('2000-01-01', '2017-12-31'), 'w2010': ('2010-01-01', '2017-12-31')}
TRIALS = [  # id, family, file key, long bucket, short bucket (for the informational spread), direction note
    ('F1', 'dividend yield (price-computable value proxy)', 'dp_monthly', 'Hi 30', 'Lo 30', 'high yield outperforms'),
    ('F2', 'long-term reversal 60-13', 'ltrev10_monthly', 'Lo PRIOR', 'Hi PRIOR', 'past 5-year losers outperform'),
    ('F3', 'low beta', 'beta_monthly', 'Lo 20', 'Hi 20', 'low beta earns >= market with lower risk'),
    ('F4a', 'low total variance (E050 H3 re-read)', 'var_monthly', 'Lo 20', 'Hi 20', 'low variance'),
    ('F4b', 'low residual variance (E050 H4 re-read)', 'resvar_monthly', 'Lo 20', 'Hi 20', 'low residual variance'),
    ('F5', 'operating profitability (reference: needs fundamentals)', 'op_monthly', 'Hi 30', 'Lo 30', 'high profitability outperforms'),
    ('F6', 'book-to-market (reference)', 'beme_monthly', 'Hi 30', 'Lo 30', 'value outperforms'),
    ('F7', 'investment / asset growth (reference)', 'inv_monthly', 'Lo 30', 'Hi 30', 'conservative outperforms'),
    ('F8', 'accruals (reference)', 'ac_monthly', 'Lo 20', 'Hi 20', 'low accruals outperform'),
    ('F9', 'net share issuance (reference)', 'ni_monthly', '< 0', 'Hi 20', 'repurchasers (negative net issuance) outperform'),
]


def window_stats(x, mkt_total):
    out = {}
    for name, (a, b) in WINDOWS.items():
        s = x[a:b].dropna()
        if len(s) < 24:
            continue
        out[name] = dict(**hac_mean(s), ann_mean=float(s.mean() * 12), sharpe_excess=sharpe(s))
    roll = x['2000-01-01':'2017-12-31'].dropna()
    windows = [roll[:f'{y}-12-31'].tail(60) for y in range(2004, 2018)]
    windows = [w for w in windows if len(w) == 60]
    out['rolling60_positive_share_2000'] = float(np.mean([w.mean() > 0 for w in windows])) if windows else np.nan
    out['rolling60_min_ann'] = float(min(w.mean() * 12 for w in windows)) if windows else np.nan
    return out


def run():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E052_{stamp}'
    out_dir.mkdir(parents=True)
    ff = load_factors()
    mkt = ff['Mkt']
    results = {}
    for tid, fam, key, lo, hi, direction in TRIALS:
        kind = 'vw_monthly'
        df = fr.load(key, kind)
        df.columns = [c.strip() for c in df.columns]
        assert_development(df.index)
        long = df[lo]
        spread = df[lo] - df[hi]
        idx = long.index.intersection(mkt.index)
        ex = (long.reindex(idx) - mkt.reindex(idx)).dropna()
        st = window_stats(ex, mkt)
        bucket_total = long.reindex(idx)
        res = dict(family=fam, file=key, long_bucket=lo, short_bucket=hi, direction=direction, months=int(len(ex)),
                   long_minus_market=st, spread=window_stats(spread.reindex(idx).dropna(), mkt),
                   bucket=dict(cagr_2000=float((1 + bucket_total['2000':'2017']).prod() ** (12 / len(bucket_total['2000':'2017'])) - 1),
                               mkt_cagr_2000=float((1 + mkt['2000':'2017']).prod() ** (12 / len(mkt['2000':'2017'])) - 1),
                               cagr_2010=float((1 + bucket_total['2010':'2017']).prod() ** (12 / len(bucket_total['2010':'2017'])) - 1),
                               mkt_cagr_2010=float((1 + mkt['2010':'2017']).prod() ** (12 / len(mkt['2010':'2017'])) - 1),
                               max_dd_2000=max_drawdown(bucket_total['2000':'2017']), mkt_max_dd_2000=max_drawdown(mkt['2000':'2017']),
                               vol_2000=float(bucket_total['2000':'2017'].std() * np.sqrt(12)), mkt_vol_2000=float(mkt['2000':'2017'].std() * np.sqrt(12))))
        me = dict(ME1_t2000_ge_1=st['w2000']['t'] >= 1.0, ME2_mean2010_ge_0=st['w2010']['mean'] >= 0)
        me['passes'] = all(me.values())
        res['gate_ME'] = me
        if key == 'dp_monthly':
            zero = (df['<= 0'].reindex(idx) - mkt.reindex(idx)).dropna()
            res['zero_dividend_minus_market'] = window_stats(zero, mkt)
        results[tid] = res
        print(f"{tid} {fam[:40]:40} 2000-17 excess {st['w2000']['ann_mean']*100:6.2f}%/yr t {st['w2000']['t']:5.2f} | 2010-17 {st['w2010']['ann_mean']*100:6.2f}% t {st['w2010']['t']:5.2f} | "
              f"roll60+ {st['rolling60_positive_share_2000']:.2f} | bucket CAGR00 {res['bucket']['cagr_2000']*100:5.1f} vs mkt {res['bucket']['mkt_cagr_2000']*100:5.1f} | DD {res['bucket']['max_dd_2000']*100:5.0f} vs {res['bucket']['mkt_max_dd_2000']*100:5.0f} | ME {me['passes']}")
    meta = dict(experiment='E052', stamp=stamp, windows=WINDOWS, trials=[t[0] for t in TRIALS], french_manifest=str(fr.MANIFEST.relative_to(ROOT)))
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=meta, results=results), indent=1, default=float), encoding='utf8')
    print(out_dir)
    return results


if __name__ == '__main__':
    run()
