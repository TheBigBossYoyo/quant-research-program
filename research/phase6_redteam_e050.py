"""Red-team diagnostics for the E050 survivors (H1 momentum 12-2, H5a industry momentum 12-1). No hypotheses.

Attacks (mandate section 56): microcap effect (equal- vs value-weighted), one-crisis attribution (2009 momentum
crash and 2000-2002), one-decade dependence (rolling 120-month t-statistics), worst-month concentration, and the
long-only top bucket's dependence on the market. Development segment only. Output: reports/<E050 dir>/redteam.json.
Usage (from research/): PYTHONUTF8=1 python phase6_redteam_e050.py E050_<stamp>
"""
import json
import sys
import numpy as np
import pandas as pd

import phase6_french as fr
from phase6_factor_screen import hac_mean, hac_alpha, sharpe, load_factors, ERAS
from phase6_lock import ROOT, assert_development


def rolling_t(x, window=120):
    x = x.dropna()
    out = {}
    for end in range(window, len(x) + 1, 12):
        s = x.iloc[end - window:end]
        out[str(s.index[-1].date())] = hac_mean(s)['t']
    return out


def attack(ls, lo, factors, label):
    ls = ls.dropna()
    lo = lo.dropna()
    res = {}
    res['full'] = dict(ls=hac_mean(ls), lo=hac_mean(lo), ls_sharpe=sharpe(ls))
    for name, a, b in (('ex_2009', '2009-01-01', '2009-12-31'), ('ex_2000_2002', '2000-01-01', '2002-12-31'), ('ex_2008_2009', '2008-01-01', '2009-12-31')):
        mask = ~((ls.index >= a) & (ls.index <= b))
        res[name] = dict(ls=hac_mean(ls[mask]), lo=hac_mean(lo[mask]))
    cum = ls.sum()
    worst = ls.nsmallest(12)
    best = ls.nlargest(12)
    res['concentration'] = dict(worst_12_months_sum_share_of_total=float(worst.sum() / cum), best_12_months_sum_share_of_total=float(best.sum() / cum),
                                worst_month=dict(date=str(ls.idxmin().date()), value=float(ls.min())), best_month=dict(date=str(ls.idxmax().date()), value=float(ls.max())),
                                calendar_2009_ls=float(ls['2009'].sum()), calendar_2009_lo=float(lo['2009'].sum()))
    res['rolling_120m_t'] = rolling_t(ls)
    rt = pd.Series(res['rolling_120m_t'])
    res['rolling_summary'] = dict(windows=int(len(rt)), min_t=float(rt.min()), share_t_above_2=float((rt > 2).mean()), share_negative=float((rt < 0).mean()),
                                  last_five=[float(v) for v in rt.tail(5)])
    dd_idx = (1 + ls).cumprod()
    res['ls_max_drawdown'] = float((dd_idx / dd_idx.cummax() - 1).min())
    res['lo_beta_ff3'] = hac_alpha(lo, factors[['Mkt-RF', 'SMB', 'HML']].reindex(lo.index))
    bear = factors['Mkt-RF'].reindex(ls.index).rolling(24).sum().shift(1) < 0
    res['conditional_on_prior_24m_market'] = dict(after_bear=hac_mean(ls[bear.fillna(False)]), after_bull=hac_mean(ls[~bear.fillna(True)]))
    return res


def run(report):
    out_dir = ROOT / 'reports' / report
    assert out_dir.exists(), out_dir
    factors = load_factors()
    assert_development(factors.index)
    out = {}
    # H1: VW versus EW deciles
    for wkey, tag in (('vw_monthly', 'value_weighted'), ('ew_monthly', 'equal_weighted')):
        dec = fr.load('mom10_monthly', wkey).reindex(factors.index).dropna()
        ls = dec.iloc[:, -1] - dec.iloc[:, 0]
        lo = dec.iloc[:, -1] - factors['Mkt']
        out[f'H1_{tag}'] = attack(ls, lo, factors, tag)
    # H5a: VW industries (EW industries would double-count the same VW industry series; the microcap attack is
    # the 49-industry EW-firm series)
    for wkey, tag in (('vw_monthly', 'value_weighted'), ('ew_monthly', 'equal_weighted_firms')):
        ind = fr.load('ind49_monthly', wkey).reindex(factors.index)
        gross = np.log1p(ind)
        sig = gross.shift(2).rolling(11).sum().where(gross.shift(2).rolling(11).count() == 11)
        rows_ls, rows_lo = [], []
        for t in ind.index:
            s = sig.loc[t].dropna()
            r = ind.loc[t].reindex(s.index).dropna()
            s = s.reindex(r.index)
            if len(s) < 20:
                continue
            order = s.sort_values()
            rows_ls.append((t, r[order.index[-10:]].mean() - r[order.index[:10]].mean()))
            rows_lo.append((t, r[order.index[-10:]].mean() - r.mean()))
        out[f'H5a_{tag}'] = attack(pd.Series(dict(rows_ls)), pd.Series(dict(rows_lo)), factors, tag)
    (out_dir / 'redteam.json').write_text(json.dumps(out, indent=1, default=float), encoding='utf8')
    for k, v in out.items():
        print(k, 'full LS mean %.3f%% t %.2f | ex2009 t %.2f | ex2000-02 t %.2f | ex2008-09 t %.2f | worst12 share %.2f best12 share %.2f | 2009 LS %.1f%% LO %.1f%% | rolling min t %.2f, share>2 %.2f, neg %.2f, last5 %s | LS DD %.1f%% | after bear t %.2f (n %d) after bull t %.2f (n %d)' % (
            v['full']['ls']['mean'] * 100, v['full']['ls']['t'], v['ex_2009']['ls']['t'], v['ex_2000_2002']['ls']['t'], v['ex_2008_2009']['ls']['t'],
            v['concentration']['worst_12_months_sum_share_of_total'], v['concentration']['best_12_months_sum_share_of_total'],
            v['concentration']['calendar_2009_ls'] * 100, v['concentration']['calendar_2009_lo'] * 100,
            v['rolling_summary']['min_t'], v['rolling_summary']['share_t_above_2'], v['rolling_summary']['share_negative'], [round(x, 2) for x in v['rolling_summary']['last_five']],
            v['ls_max_drawdown'] * 100, v['conditional_on_prior_24m_market']['after_bear']['t'], v['conditional_on_prior_24m_market']['after_bear']['n'],
            v['conditional_on_prior_24m_market']['after_bull']['t'], v['conditional_on_prior_24m_market']['after_bull']['n']))
    return out


if __name__ == '__main__':
    run(sys.argv[1])
