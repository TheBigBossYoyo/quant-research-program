"""E050: preregistered family-level factor diagnostics on the Kenneth French library (Phase 6, development only).

Everything here follows the E050 preregistration in EXPERIMENTS.md (2026-09-09). No parameter is chosen
from results; the neighbourhood cells (H5 lookbacks, H6 SMA windows, H7 caps) are all reported.
Usage (from research/): PYTHONUTF8=1 python phase6_factor_screen.py
"""
from datetime import datetime, timezone
import csv
import json
import hashlib
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

import phase6_french as fr
from phase6_lock import ROOT, assert_development

SEED = 20260909
BOOT_DRAWS = 4000
BLOCK_MONTHS = 24
HAC_LAGS = 6
ERAS = [('E1', '1963-07-01', '1979-12-31'), ('E2', '1980-01-01', '1999-12-31'),
        ('E3', '2000-01-01', '2009-12-31'), ('E4', '2010-01-01', '2017-12-31')]
POST2000 = ('2000-01-01', '2017-12-31')


def hac_mean(x, lags=HAC_LAGS):
    x = pd.Series(x).dropna()
    m = sm.OLS(x.to_numpy(), np.ones((len(x), 1))).fit(cov_type='HAC', cov_kwds=dict(maxlags=lags))
    return dict(mean=float(m.params[0]), t=float(m.tvalues[0]), n=int(len(x)))


def hac_alpha(y, X, lags=HAC_LAGS):
    d = pd.concat([pd.Series(y, name='y'), X], axis=1).dropna()
    m = sm.OLS(d['y'].to_numpy(), sm.add_constant(d.drop(columns='y').to_numpy())).fit(cov_type='HAC', cov_kwds=dict(maxlags=lags))
    return dict(alpha=float(m.params[0]), t=float(m.tvalues[0]), betas=[float(b) for b in m.params[1:]], n=int(len(d)))


def stationary_bootstrap(x, draws=BOOT_DRAWS, block=BLOCK_MONTHS, seed=SEED):
    """Politis-Romano stationary bootstrap of the mean and annualised Sharpe of a monthly series."""
    x = np.asarray(pd.Series(x).dropna(), dtype=float)
    n = len(x)
    rng = np.random.default_rng(seed)
    p = 1.0 / block
    means = np.empty(draws)
    sharpes = np.empty(draws)
    for d in range(draws):
        idx = np.empty(n, dtype=int)
        idx[0] = rng.integers(n)
        new_block = rng.random(n) < p
        for i in range(1, n):
            idx[i] = rng.integers(n) if new_block[i] else (idx[i - 1] + 1) % n
        s = x[idx]
        means[d] = s.mean()
        sharpes[d] = s.mean() / s.std(ddof=1) * np.sqrt(12) if s.std(ddof=1) > 0 else 0.0
    return dict(mean_ci=[float(np.quantile(means, .025)), float(np.quantile(means, .975))],
                sharpe_ci=[float(np.quantile(sharpes, .025)), float(np.quantile(sharpes, .975))])


def sharpe(x):
    x = pd.Series(x).dropna()
    return float(x.mean() / x.std(ddof=1) * np.sqrt(12)) if x.std(ddof=1) > 0 else float('nan')


def max_drawdown(total_returns):
    idx = (1 + pd.Series(total_returns).dropna()).cumprod()
    return float((idx / idx.cummax() - 1).min())


def era_table(x):
    x = pd.Series(x).dropna()
    out = {}
    for name, a, b in ERAS:
        s = x[a:b]
        out[name] = dict(mean=float(s.mean()) if len(s) else float('nan'), n=int(len(s)), positive=bool(s.mean() > 0) if len(s) else None)
    return out


def summarize_premium(name, ls, lo, factors, buckets=None, direction=1):
    """Common statistics for a long/short premium `ls` and long-only excess `lo` (monthly decimals)."""
    ls = ls.dropna()
    lo = lo.dropna()
    res = dict(trial=name, months=int(len(ls)), start=str(ls.index[0].date()), end=str(ls.index[-1].date()))
    res['ls'] = dict(**hac_mean(ls), sharpe=sharpe(ls), boot=stationary_bootstrap(ls), eras=era_table(ls),
                     post2000=hac_mean(ls[POST2000[0]:POST2000[1]]),
                     capm=hac_alpha(ls, factors[['Mkt-RF']]), ff3=hac_alpha(ls, factors[['Mkt-RF', 'SMB', 'HML']]))
    res['lo'] = dict(**hac_mean(lo), sharpe=sharpe(lo), eras=era_table(lo), post2000=hac_mean(lo[POST2000[0]:POST2000[1]]),
                     capm=hac_alpha(lo, factors[['Mkt-RF']]), ff3=hac_alpha(lo, factors[['Mkt-RF', 'SMB', 'HML']]))
    if buckets is not None:
        means = buckets.mean()
        rho, pval = stats.spearmanr(np.arange(len(means)), means.to_numpy())
        res['monotonicity'] = dict(bucket_means=[float(v) for v in means], spearman=float(rho * direction), p=float(pval))
    return res


def gate_cross_sectional(res):
    ls = res['ls']
    eras_pos = sum(1 for e in ls['eras'].values() if e['positive'])
    checks = dict(a_t_ge_3=ls['t'] >= 3.0, b_boot_excludes_zero=ls['boot']['mean_ci'][0] > 0,
                  c_eras_ge_3of4=eras_pos >= 3, d_monotonic=res.get('monotonicity', {}).get('spearman', float('nan')) >= 0.7,
                  e_long_only_ff3_t_ge_2=res['lo']['ff3']['t'] >= 2.0)
    core = [checks[k] for k in ('a_t_ge_3', 'b_boot_excludes_zero', 'c_eras_ge_3of4', 'd_monotonic')]
    if all(core):
        label = 'FACTOR_EVIDENCE' if checks['e_long_only_ff3_t_ge_2'] else 'FACTOR_EVIDENCE (RESEARCH_ONLY_MARKET_NEUTRAL)'
    elif 2.0 <= ls['t'] < 3.0 or (ls['t'] >= 3.0 and sum(core) == 3):
        label = 'WEAK_SIGNAL'
    else:
        label = 'REJECTED'
    return dict(checks={k: bool(v) for k, v in checks.items()}, eras_positive=eras_pos, classification=label)


def gate_timing(res):
    t = res['alpha']['t']
    checks = dict(alpha_t_ge_2_5=t >= 2.5, sharpe_above_bh=res['sharpe'] > res['bh_sharpe'],
                  dd_shallower=res['max_dd'] > res['bh_max_dd'], eras_ge_3of4=res['eras_sharpe_wins'] >= 3)
    if all(checks.values()):
        label = 'FACTOR_EVIDENCE'
    elif 1.5 <= t < 2.5 or (t >= 2.5 and sum(checks.values()) == 3):
        label = 'WEAK_SIGNAL'
    else:
        label = 'REJECTED'
    return dict(checks={k: bool(v) for k, v in checks.items()}, classification=label)


def load_factors():
    ff3 = fr.load('ff3_monthly', 'main')
    ff3.columns = [c.strip() for c in ff3.columns]
    ff3['Mkt'] = ff3['Mkt-RF'] + ff3['RF']
    return ff3


def run():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E050_{stamp}'
    out_dir.mkdir(parents=True, exist_ok=False)
    manifest = fr.verify_manifest()
    factors = load_factors()
    assert_development(factors.index)
    results = {}

    # H1 momentum 12-2 deciles, H2 short-term reversal deciles
    for hid, key, ls_sign, name in (('H1', 'mom10_monthly', +1, 'momentum_12_2_deciles'),
                                    ('H2', 'strev10_monthly', -1, 'st_reversal_1_0_deciles')):
        dec = fr.load(key, 'vw_monthly')
        dec = dec.reindex(factors.index).dropna()
        ex = dec.sub(factors['RF'], axis=0)
        ls = (dec.iloc[:, -1] - dec.iloc[:, 0]) * ls_sign
        long_bucket = dec.iloc[:, -1] if ls_sign > 0 else dec.iloc[:, 0]
        lo = long_bucket - factors['Mkt']
        res = summarize_premium(name, ls, lo, factors, buckets=ex, direction=ls_sign)
        res['gate'] = gate_cross_sectional(res)
        if hid == 'H2':
            prem = res['lo']['mean']
            res['break_even_one_way_cost_bps'] = {f'f={f}': float(prem / (2 * f) * 1e4) for f in (0.5, 0.8, 1.0)}
            res['reversal_terminated'] = bool(res['break_even_one_way_cost_bps']['f=0.8'] < 20.0)
        results[hid] = res

    # H3/H4 variance and residual-variance quintiles
    for hid, key, name in (('H3', 'var_monthly', 'low_total_variance_quintiles'), ('H4', 'resvar_monthly', 'low_residual_variance_quintiles')):
        q = fr.load(key, 'vw_monthly').iloc[:, :5].reindex(factors.index).dropna()
        ex = q.sub(factors['RF'], axis=0)
        ls = q.iloc[:, 0] - q.iloc[:, 4]
        lo = q.iloc[:, 0] - factors['Mkt']
        res = summarize_premium(name, ls, lo, factors, buckets=ex, direction=-1)
        res['gate'] = gate_cross_sectional(res)
        results[hid] = res

    # H5 industry momentum on 49 VW industries
    ind = fr.load('ind49_monthly', 'vw_monthly').reindex(factors.index)
    for cell, lb in (('H5a', 12), ('H5b', 6)):
        gross = np.log1p(ind)
        sig = gross.shift(2).rolling(lb - 1).sum()  # months t-lb..t-2, all present
        sig = sig.where(gross.shift(2).rolling(lb - 1).count() == lb - 1)
        rows_ls, rows_lo, rows_q = [], [], []
        for t in ind.index:
            s = sig.loc[t].dropna()
            r = ind.loc[t].reindex(s.index).dropna()
            s = s.reindex(r.index)
            if len(s) < 20:
                continue
            order = s.sort_values()
            bottom, top = r[order.index[:10]].mean(), r[order.index[-10:]].mean()
            quint = [r[order.index[int(k * len(order) / 5):int((k + 1) * len(order) / 5)]].mean() for k in range(5)]
            rows_ls.append((t, top - bottom))
            rows_lo.append((t, top - r.mean()))
            rows_q.append((t, quint))
        ls = pd.Series(dict(rows_ls))
        lo = pd.Series(dict(rows_lo))
        q = pd.DataFrame([v for _, v in rows_q], index=[t for t, _ in rows_q], columns=[f'Q{k+1}' for k in range(5)])
        res = summarize_premium(f'industry_momentum_{lb}_1', ls, lo, factors, buckets=q.sub(factors['RF'].reindex(q.index), axis=0), direction=+1)
        res['gate'] = gate_cross_sectional(res)
        results[cell] = res

    # H6 market trend filter (SMA10 primary, SMA12)
    mkt = factors['Mkt']
    idx = (1 + mkt).cumprod()
    bh_ex = factors['Mkt-RF']
    for cell, w in (('H6a', 10), ('H6b', 12)):
        signal = (idx.shift(1) > idx.rolling(w).mean().shift(1)).astype(float)
        signal = signal.where(idx.rolling(w).count().shift(1) == w)
        strat = signal * mkt + (1 - signal) * factors['RF']
        strat_ex = strat - factors['RF']
        d = pd.concat([strat_ex, bh_ex, mkt, strat], axis=1, keys=['sx', 'bx', 'm', 's']).dropna()
        alpha = hac_alpha(d['sx'], d[['bx']].rename(columns={'bx': 'Mkt-RF'}))
        wins = sum(1 for name, a, b in ERAS if sharpe(d['sx'][a:b]) >= sharpe(d['bx'][a:b]))
        res = dict(trial=f'market_trend_sma{w}', months=int(len(d)), start=str(d.index[0].date()), end=str(d.index[-1].date()),
                   alpha=alpha, sharpe=sharpe(d['sx']), bh_sharpe=sharpe(d['bx']), max_dd=max_drawdown(d['s']), bh_max_dd=max_drawdown(d['m']),
                   cagr=float((1 + d['s']).prod() ** (12 / len(d)) - 1), bh_cagr=float((1 + d['m']).prod() ** (12 / len(d)) - 1),
                   time_invested=float(signal.reindex(d.index).mean()), eras_sharpe_wins=int(wins),
                   eras={name: dict(sharpe=sharpe(d['sx'][a:b]), bh_sharpe=sharpe(d['bx'][a:b])) for name, a, b in ERAS},
                   post2000_alpha=hac_alpha(d['sx'][POST2000[0]:POST2000[1]], d[['bx']][POST2000[0]:POST2000[1]].rename(columns={'bx': 'Mkt-RF'})),
                   boot=stationary_bootstrap(d['sx'] - d['bx']))
        res['gate'] = gate_timing(res)
        results[cell] = res

    # H7 volatility-managed market exposure
    daily = fr.load('ff3_daily', 'main')
    daily.columns = [c.strip() for c in daily.columns]
    rv = (daily['Mkt-RF'] ** 2).groupby(daily.index.to_period('M')).sum()
    rv.index = rv.index.to_timestamp(how='end').normalize()
    rv = rv.reindex(factors.index)
    target = rv.expanding(min_periods=60).median().shift(1)
    raw_w = target / rv.shift(1)
    for cell, cap in (('H7a', 1.0), ('H7b', 1.5)):
        w = raw_w.clip(upper=cap)
        strat_ex = (w * bh_ex).dropna()
        d = pd.concat([strat_ex, bh_ex, mkt, strat_ex + factors['RF']], axis=1, keys=['sx', 'bx', 'm', 's']).dropna()
        alpha = hac_alpha(d['sx'], d[['bx']].rename(columns={'bx': 'Mkt-RF'}))
        wins = sum(1 for name, a, b in ERAS if sharpe(d['sx'][a:b]) >= sharpe(d['bx'][a:b]))
        res = dict(trial=f'vol_managed_market_cap{cap}', months=int(len(d)), start=str(d.index[0].date()), end=str(d.index[-1].date()),
                   alpha=alpha, sharpe=sharpe(d['sx']), bh_sharpe=sharpe(d['bx']), max_dd=max_drawdown(d['s']), bh_max_dd=max_drawdown(d['m']),
                   cagr=float((1 + d['s']).prod() ** (12 / len(d)) - 1), bh_cagr=float((1 + d['m']).prod() ** (12 / len(d)) - 1),
                   mean_weight=float(w.reindex(d.index).mean()), weight_quantiles=[float(v) for v in w.reindex(d.index).quantile([.05, .5, .95])],
                   eras_sharpe_wins=int(wins), eras={name: dict(sharpe=sharpe(d['sx'][a:b]), bh_sharpe=sharpe(d['bx'][a:b])) for name, a, b in ERAS},
                   post2000_alpha=hac_alpha(d['sx'][POST2000[0]:POST2000[1]], d[['bx']][POST2000[0]:POST2000[1]].rename(columns={'bx': 'Mkt-RF'})),
                   boot=stationary_bootstrap(d['sx'] - d['bx']))
        res['gate'] = gate_timing(res)
        results[cell] = res

    # FDR across the seven primary trials (H1-H4, H5a, H6a, H7a)
    primary = ['H1', 'H2', 'H3', 'H4', 'H5a', 'H6a', 'H7a']
    tvals = {k: (results[k]['ls']['t'] if 'ls' in results[k] else results[k]['alpha']['t']) for k in primary}
    pvals = {k: float(2 * (1 - stats.norm.cdf(abs(t)))) for k, t in tvals.items()}
    order = sorted(primary, key=lambda k: pvals[k])
    m = len(order)
    bh_pass = {}
    thresh_hit = 0
    for i, k in enumerate(order, 1):
        if pvals[k] <= 0.05 * i / m:
            thresh_hit = i
    for i, k in enumerate(order, 1):
        bh_pass[k] = i <= thresh_hit
    results['multiplicity'] = dict(primary_trials=primary, hac_t=tvals, p_two_sided=pvals, bh_fdr_0_05_pass=bh_pass,
                                   bonferroni_neighbourhoods=dict(H5=2, H6=2, H7=2), cumulative_hypotheses_after=398)

    meta = dict(experiment='E050', stamp=stamp, seed=SEED, boot_draws=BOOT_DRAWS, block_months=BLOCK_MONTHS, hac_lags=HAC_LAGS,
                development_end_exclusive='2018-01-01', french_manifest_files={r['key']: r['sha256'] for r in manifest['files']},
                crsp_vintage=sorted({r['crsp_vintage'] for r in manifest['files']}), source_hash=hashlib.sha256((ROOT / 'research/phase6_factor_screen.py').read_bytes()).hexdigest())
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=meta, results=results), indent=1, default=float), encoding='utf8')

    rows = []
    for k, r in results.items():
        if k == 'multiplicity':
            continue
        if 'ls' in r:
            rows.append(dict(experiment='E050', trial_id=k, trial=r['trial'], months=r['months'], ls_mean_monthly=r['ls']['mean'], ls_t=r['ls']['t'], ls_sharpe=r['ls']['sharpe'],
                             ls_boot_ci_lo=r['ls']['boot']['mean_ci'][0], ls_boot_ci_hi=r['ls']['boot']['mean_ci'][1], eras_positive=r['gate']['eras_positive'],
                             spearman=r.get('monotonicity', {}).get('spearman'), lo_mean_monthly=r['lo']['mean'], lo_t=r['lo']['t'], lo_ff3_alpha=r['lo']['ff3']['alpha'], lo_ff3_t=r['lo']['ff3']['t'],
                             ls_post2000_t=r['ls']['post2000']['t'], classification=r['gate']['classification']))
        else:
            rows.append(dict(experiment='E050', trial_id=k, trial=r['trial'], months=r['months'], ls_mean_monthly=None, ls_t=r['alpha']['t'], ls_sharpe=r['sharpe'],
                             ls_boot_ci_lo=r['boot']['mean_ci'][0], ls_boot_ci_hi=r['boot']['mean_ci'][1], eras_positive=r['eras_sharpe_wins'], spearman=None,
                             lo_mean_monthly=r['cagr'] - r['bh_cagr'], lo_t=None, lo_ff3_alpha=r['alpha']['alpha'], lo_ff3_t=r['alpha']['t'], ls_post2000_t=r['post2000_alpha']['t'],
                             classification=r['gate']['classification']))
    tab = pd.DataFrame(rows)
    tab.to_csv(out_dir / 'tables.csv', index=False)
    diag = ROOT / 'PHASE6_SIGNAL_DIAGNOSTICS.csv'
    tab.assign(run=stamp).to_csv(diag, mode='a', header=not diag.exists(), index=False)
    reg = ROOT / 'PHASE6_EXPERIMENT_REGISTRY.csv'
    fam = dict(H1='A momentum', H2='E short-term reversal', H3='D low volatility', H4='D low volatility', H5a='F industry relative strength', H5b='F industry relative strength',
               H6a='C trend (market filter)', H6b='C trend (market filter)', H7a='G volatility-managed exposure', H7b='G volatility-managed exposure')
    base = 388
    with reg.open('a', newline='', encoding='utf8') as f:
        w = csv.writer(f)
        if reg.stat().st_size == 0:
            w.writerow(['experiment', 'run', 'trial_id', 'family', 'architecture', 'neighbourhood_cell', 'data', 'segment', 'cumulative_hypotheses', 'classification'])
        for i, r in enumerate(rows, 1):
            w.writerow(['E050', stamp, r['trial_id'], fam[r['trial_id']], r['trial'], r['trial_id'][-1] if r['trial_id'][-1].isalpha() else 'primary',
                        'French library 202607 (VW)', 'development 1963-07..2017-12', base + i, r['classification']])
    (out_dir / 'summary.md').write_text('```\n' + tab.to_string(index=False) + '\n```\n', encoding='utf8')
    print(tab.to_string())
    print(json.dumps(results['multiplicity'], indent=1))
    print('OUT', out_dir.name)
    return out_dir


if __name__ == '__main__':
    run()
