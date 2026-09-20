"""E051: stock-level momentum family screen on EODHD (Phase 6, development only, preregistered).

Trials, gates and outputs follow the E051 preregistration in EXPERIMENTS.md and the frozen
PHASE6_NORGATE_PURCHASE_GATE.md. Nothing is chosen from results: every trial in TRIALS is run and reported;
overlays are computed only for trials that pass the pre-overlay survivor rules (encoded in `survivor`).

Usage (from research/): PYTHONUTF8=1 python phase6_e051_run.py --t2-start YEAR [--boot 4000]
"""
from datetime import datetime, timezone
import argparse
import gzip
import hashlib
import json

import numpy as np
import pandas as pd
from scipy import stats as sps
import statsmodels.api as sm

import phase6_eodhd as e
import phase6_eodhd_panel as pnl
import phase6_stock_universe as su
import phase6_stock_engine as se
import phase6_french as fr
from phase6_factor_screen import hac_mean, hac_alpha, stationary_bootstrap, sharpe, max_drawdown
from phase6_lock import ROOT, enforce, assert_development, DEV_END_EXCLUSIVE

DEV_END = DEV_END_EXCLUSIVE - pd.Timedelta(days=1)
SEED = 20260911
ERAS = [('E2b', '1990-01-01', '1999-12-31'), ('E3', '2000-01-01', '2009-12-31'), ('E4', '2010-01-01', '2017-12-31')]
RECENT = ('2015-01-01', '2017-12-31')
SECTOR_ETFS = ['XLK', 'XLF', 'XLE', 'XLV', 'XLI', 'XLP', 'XLY', 'XLU', 'XLB']
MIN_SURVIVOR_MONTHS = 120
HAIRCUT_MODES = ('base', 'all100', 'all30')
COST_CASES = ('optimistic', 'base', 'stress')

# (trial_id, tier, family, architecture, lookback, skip, N, primary?)
TRIALS = (
    [(f'T2_A_mom{lb}_1_N{n}', 'LIQ1000', 'A', 'mom', lb, 1, n, (lb == 12 and n == 30))
     for lb in (12, 6, 9) for n in (10, 20, 30, 50)] +
    [(f'T2_B_resid12_1_N{n}', 'LIQ1000', 'B', 'resid', 12, 1, n, n == 30) for n in (10, 20, 30, 50)] +
    [('T2_A_volmom12_1_N30', 'LIQ1000', 'A', 'volmom', 12, 1, 30, False),
     ('T1_A_mom12_1_N30', 'PIT_SP1500', 'A', 'mom', 12, 1, 30, True),
     ('T1_B_resid12_1_N30', 'PIT_SP1500', 'B', 'resid', 12, 1, 30, True),
     ('T1_A_secneutral12_1_N30', 'PIT_SP1500', 'A', 'secneutral', 12, 1, 30, False),
     ('ETF_F_mom12_1_top3', 'SECTOR_ETF', 'F', 'mom', 12, 1, 3, True),
     ('ETF_F_mom12_1_top2', 'SECTOR_ETF', 'F', 'mom', 12, 1, 2, False),
     ('ETF_F_mom12_1_top4', 'SECTOR_ETF', 'F', 'mom', 12, 1, 4, False),
     ('ETF_F_mom6_1_top3', 'SECTOR_ETF', 'F', 'mom', 6, 1, 3, False)]
)
GATES = dict(s1_t_net_excess_ew=2.0, s2_eras_positive_min=2, s2_require_E4=True, s3_stress_positive=True,
             s4_recent_36m_nonneg=True, s4_rolling60_positive_share=0.70, s5_alpha_vs_spy_t=1.5, s5_cagr_beats_spy_2000_2017=True,
             s6_max_dd_not_deeper_than_spy_by=0.15, min_months=MIN_SURVIVOR_MONTHS, bh_fdr=0.05, dsr_min=0.90,
             f_cost_drag_share_max=0.50, f_min_trade_eur=1.0, eur_usd=1.1652)


def sha256_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_ff3():
    ff = fr.load('ff3_monthly', 'main')
    ff.columns = [c.strip() for c in ff.columns]
    ff.index = ff.index.to_period('M')
    return ff


def load_etf_frames():
    man = json.loads((e.META / 'phase6_eodhd_etf_manifest.json').read_text(encoding='utf8'))
    frames = {}
    for rec in man:
        df = pnl.read_eod_csv(ROOT / rec['file'])
        frames[rec['code']] = enforce(df, 'development')
    return frames


def etf_monthly(frames, codes, signal_dates, exec_dates):
    """Month-end adjusted closes and open-to-open holding returns for ETFs on the stock calendar."""
    close = pd.DataFrame({c: frames[c]['close'] for c in codes})
    open_ = pd.DataFrame({c: frames[c]['open'] for c in codes})
    adj = pd.DataFrame({c: frames[c]['adj_close'] for c in codes})
    ao = (open_ * adj / close)
    ret = pd.DataFrame({c: ao[c].reindex(exec_dates).pct_change().shift(-1) for c in codes}).iloc[:-1]
    mp = adj.reindex(signal_dates)
    return mp, ret, adj


def sector_labels():
    lab = {}
    for idx in ('GSPC', 'MID', 'SML'):
        comp = json.loads((e.RAW / 'constituents' / f'comp_{idx}.json').read_text(encoding='utf8'))
        for v in comp['Components'].values():
            if v.get('Sector'):
                lab.setdefault(v['Code'], v['Sector'])
    return lab


def sector_neutral_scores(mom, eligible, labels):
    lab = pd.Series(labels).reindex(mom.columns)
    out = pd.DataFrame(np.nan, index=mom.index, columns=mom.columns)
    for t in mom.index:
        s = mom.loc[t].where(eligible.loc[t])
        df = pd.DataFrame(dict(s=s, sec=lab)).dropna()
        if df.empty:
            continue
        g = df.groupby('sec')['s']
        z = (df['s'] - g.transform('mean')) / g.transform('std').replace(0, np.nan)
        out.loc[t, z.index] = z
    return out


def stats_block(net, bench, spy, rf, boot_draws):
    """All statistics for one monthly net series against the tier benchmark and SPY (monthly decimals)."""
    net = net.dropna()
    idx = net.index
    ex_ew = (net - bench.reindex(idx)).dropna()
    ex_spy = (net - spy.reindex(idx)).dropna()
    per = pd.Series(idx.to_period('M'), index=idx)
    rfm = rf.reindex(per.to_numpy()).to_numpy()
    out = dict(months=int(len(net)), start=str(idx[0].date()), end=str(idx[-1].date()), net=se.ann_stats(net),
               bench=se.ann_stats(bench.reindex(idx)), spy=se.ann_stats(spy.reindex(idx)),
               excess_ew=dict(**hac_mean(ex_ew), boot=stationary_bootstrap(ex_ew, draws=boot_draws, seed=SEED)),
               excess_spy=hac_mean(ex_spy))
    X = pd.DataFrame({'Mkt-RF': (spy.reindex(idx) - rfm)}, index=idx)
    out['capm_vs_spy'] = hac_alpha(net - rfm, X)
    out['eras'] = {}
    for name, a, b in ERAS:
        s = ex_ew[a:b]
        if len(s) >= 12:
            out['eras'][name] = dict(n=int(len(s)), mean=float(s.mean()), t=hac_mean(s)['t'], positive=bool(s.mean() > 0),
                                     net_cagr=se.ann_stats(net[a:b])['cagr'], bench_cagr=se.ann_stats(bench.reindex(idx)[a:b])['cagr'])
    rec = ex_ew[RECENT[0]:RECENT[1]]
    out['recent_36m'] = dict(n=int(len(rec)), mean=float(rec.mean()) if len(rec) else np.nan)
    roll = []
    years = sorted(set(idx.year))
    for y in years:
        w = ex_ew[:f'{y}-12-31'].tail(60)
        if len(w) == 60:
            roll.append(dict(end=y, mean=float(w.mean()), t=hac_mean(w)['t'], net_sharpe=sharpe(net[w.index])))
    out['rolling60'] = roll
    out['rolling60_positive_share'] = float(np.mean([r['mean'] > 0 for r in roll])) if roll else np.nan
    a, b = '2000-01-01', '2017-12-31'
    out['cagr_2000_2017'] = dict(net=se.ann_stats(net[a:b])['cagr'], spy=se.ann_stats(spy.reindex(idx)[a:b])['cagr'],
                                 bench=se.ann_stats(bench.reindex(idx)[a:b])['cagr'])
    yearly = net.groupby(idx.year).sum()
    tot = float(net.sum())
    out['concentration'] = dict(best_year=int(yearly.idxmax()), best_year_share=float(yearly.max() / tot) if tot > 0 else np.nan,
                                top5_month_share=float(net.nlargest(5).sum() / tot) if tot > 0 else np.nan,
                                worst_12m=float((1 + net).rolling(12).apply(np.prod).min() - 1))
    return out


def sector_betas(net, sector_rets, rf):
    idx = net.dropna().index.intersection(sector_rets.dropna().index)
    if len(idx) < 36:
        return None
    per = pd.Series(idx.to_period('M'), index=idx)
    rfm = rf.reindex(per.to_numpy()).to_numpy()
    y = (net.reindex(idx) - rfm).to_numpy()
    X = sm.add_constant(sector_rets.reindex(idx).sub(rfm, axis=0).to_numpy())
    m = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds=dict(maxlags=6))
    return dict(n=int(len(idx)), r2=float(m.rsquared), alpha_t=float(m.tvalues[0]),
                betas={c: float(b) for c, b in zip(sector_rets.columns, m.params[1:])})


def feasibility(monthly, n, capital_eur, eur_usd):
    cap = capital_eur * eur_usd
    pos = cap / n
    to = (monthly['turnover_buy'] + monthly['turnover_sell']).mean() * 12 / 2   # one-way turnover per year
    cost_year = float((monthly['cost']).mean() * 12 * cap)
    return dict(capital_eur=capital_eur, n=n, position_usd=float(pos), one_way_turnover_per_year=float(to),
                cost_usd_per_year=cost_year, cost_pct_per_year=float(monthly['cost'].mean() * 12),
                min_trade_usd=float(pos * 0.05), trades_below_1eur=bool(pos * 0.05 < 1.0 * eur_usd))


def survivor(sb, stress_sb, months):
    g = GATES
    checks = dict(
        s0_min_months=months >= g['min_months'],
        s1_t=sb['excess_ew']['t'] >= g['s1_t_net_excess_ew'],
        s2_eras=(sum(1 for v in sb['eras'].values() if v['positive']) >= g['s2_eras_positive_min']) and
                (sb['eras'].get('E4', {}).get('positive', False) or not g['s2_require_E4']),
        s3_stress=stress_sb['excess_ew']['mean'] > 0,
        s4_recent=(sb['recent_36m']['mean'] >= 0) and (sb['rolling60_positive_share'] >= g['s4_rolling60_positive_share']),
        s5_spy=(sb['capm_vs_spy']['t'] >= g['s5_alpha_vs_spy_t']) and (sb['cagr_2000_2017']['net'] > sb['cagr_2000_2017']['spy']),
        s6_dd=sb['net']['max_dd'] >= sb['spy']['max_dd'] - g['s6_max_dd_not_deeper_than_spy_by'],
    )
    decay = checks['s1_t'] and not sb['eras'].get('E4', {}).get('positive', False)
    return dict(checks={k: bool(v) for k, v in checks.items()}, passes=all(checks.values()), decay_flag=bool(decay))


def deflated_sharpe(sr_annual, n_months, n_trials, sr_var_annual, skew, kurt):
    """Bailey & Lopez de Prado (2014) deflated Sharpe ratio probability (monthly units inside)."""
    sr = sr_annual / np.sqrt(12)
    sd_sr = np.sqrt(sr_var_annual / 12)
    euler = 0.5772156649
    sr0 = sd_sr * ((1 - euler) * sps.norm.ppf(1 - 1 / n_trials) + euler * sps.norm.ppf(1 - 1 / (n_trials * np.e)))
    z = (sr - sr0) * np.sqrt(n_months - 1) / np.sqrt(1 - skew * sr + (kurt - 1) / 4 * sr ** 2)
    return float(sps.norm.cdf(z)), float(sr0 * np.sqrt(12))


def bh_fdr(pvals, q):
    p = pd.Series(pvals).dropna().sort_values()
    m = len(p)
    thresh = q * np.arange(1, m + 1) / m
    passed = p[p.to_numpy() <= thresh]
    if passed.empty:
        return set()
    cutoff = passed.iloc[-1]
    return set(p[p <= cutoff].index)


def main(t2_start_year, boot_draws):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E051_{stamp}'
    out_dir.mkdir(parents=True)
    log = []

    close = pnl.load_panel('close')
    open_ = pnl.load_panel('open')
    adj = pnl.load_panel('adj_close')
    vol = pnl.load_panel('volume')
    sf = pnl.load_panel('split_factor')
    for p in (close, open_, adj, vol, sf):
        assert_development(p.index)
    cal = su.trading_calendar(close)
    close, open_, adj, vol, sf = (x.reindex(cal) for x in (close, open_, adj, vol, sf))
    me = su.month_end_dates(cal)
    sig = me[:-1]
    ex = su.next_open_dates(cal, sig)
    assert not ex.isna().any()
    ret, ended = su.holding_returns(open_, close, adj, ex, cal, DEV_END, split_factor=sf)
    n_subst = su.holding_returns.substitutions
    sig_used = sig[:len(ret)]
    log.append(f'calendar {cal[0].date()}..{cal[-1].date()} ({len(cal)} days); signals {len(sig_used)}; tickers {close.shape[1]}')

    integrity = su.integrity_panels(close, adj, sf, sig_used)
    unclean_counts = {int(k): float(v) for k, v in integrity[0].reindex(sig_used).sum(axis=1).groupby(pd.DatetimeIndex(sig_used).year).mean().round(0).items()}
    feats = su.features_at(sig_used, close, adj, vol, sf, integrity=integrity)
    membership = su.constituent_membership(sig_used)
    elig, rank = {}, {}
    for tier in ('LIQ1000', 'PIT_SP1500'):
        E, R = [], []
        for t in sig_used:
            f = feats[t]
            if tier == 'LIQ1000':
                ok, rk = su.eligibility(f)
                if t.year < t2_start_year:
                    ok[:] = False
            else:
                ok, rk = su.eligibility(f, membership=membership.loc[t] if t in membership.index else None, liquidity_rank=False)
                if t < su.PIT_FIRST_SIGNAL:
                    ok[:] = False
            E.append(ok.rename(t)); R.append(rk.rename(t))
        elig[tier] = pd.DataFrame(E).reindex(columns=close.columns).fillna(False).astype(bool)
        rank[tier] = pd.DataFrame(R).reindex(columns=close.columns)
    counts = {tier: elig[tier].sum(axis=1).groupby(elig[tier].index.year).agg(['min', 'median', 'max']).to_dict('index') for tier in elig}
    ex_to_sig = dict(zip(ex, sig))
    n_delist = {tier: int(sum(1 for (d, c) in ended if c in elig[tier].columns and elig[tier].loc[ex_to_sig[d], c])) for tier in elig}
    extreme = {}
    for tier in elig:
        el = elig[tier].to_numpy()
        rr = ret.reindex(columns=elig[tier].columns).to_numpy()
        extreme[tier] = dict(gt_200pct=int(((rr > 2.0) & el).sum()), lt_minus90pct=int(((rr < -0.9) & el).sum()),
                             eligible_name_months=int(el.sum()))

    ff = load_ff3()
    mp = su.monthly_prices(adj, sig_used)
    scores = dict(mom12=su.momentum(mp, 12, 1), mom6=su.momentum(mp, 6, 1), mom9=su.momentum(mp, 9, 1))
    scores['volmom12'] = scores['mom12'] / su.realized_vol_12m(mp)
    ffm = ff.copy(); ffm.index = ffm.index.to_timestamp('M')
    ffa = ffm.reindex(pd.DatetimeIndex(sig_used).to_period('M').to_timestamp('M'))
    ffa.index = sig_used
    scores['resid12'] = su.residual_momentum(mp, ffa)
    labels = sector_labels()
    scores['secneutral12'] = sector_neutral_scores(scores['mom12'], elig['PIT_SP1500'], labels)
    venue = su.load_last_venue()
    haircuts = {m: (lambda info, v, m=m: su.delisting_haircut(info, v, m)) for m in HAIRCUT_MODES}

    frames = load_etf_frames()
    etf_mp, etf_ret, etf_adj = etf_monthly(frames, ['SPY'] + SECTOR_ETFS, sig_used, ex)
    spy = etf_ret['SPY'].copy(); spy.index = sig_used[:len(spy)]
    sector_rets = etf_ret[SECTOR_ETFS].copy(); sector_rets.index = sig_used[:len(sector_rets)]
    etf_scores = dict(mom12=su.momentum(etf_mp[SECTOR_ETFS], 12, 1), mom6=su.momentum(etf_mp[SECTOR_ETFS], 6, 1))
    etf_elig = etf_mp[SECTOR_ETFS].notna() & etf_mp[SECTOR_ETFS].shift(12).notna()
    etf_ret_aligned = etf_ret[SECTOR_ETFS]
    rf = ff['RF']

    benches = {}
    for tier in ('LIQ1000', 'PIT_SP1500'):
        b = se.equal_weight_benchmark(elig[tier], ret, ended=ended, venue=venue, haircut=haircuts['base'])
        benches[tier] = b['net'][b['n_held'] > 0]
    benches['SECTOR_ETF'] = se.equal_weight_benchmark(etf_elig, etf_ret_aligned)['net']
    benches['SECTOR_ETF'] = benches['SECTOR_ETF'][se.equal_weight_benchmark(etf_elig, etf_ret_aligned)['n_held'] > 0]

    results, rows, monthly_out = {}, [], {}
    for trial_id, tier, fam, arch, lb, skip, n, primary in TRIALS:
        if tier == 'SECTOR_ETF':
            sc, el, rt, rk = etf_scores[f'mom{lb}'], etf_elig, etf_ret_aligned, None
        else:
            key = {'mom': f'mom{lb}', 'resid': f'resid{lb}', 'volmom': f'volmom{lb}', 'secneutral': f'secneutral{lb}'}[arch]
            sc, el, rt, rk = scores[key], elig[tier], ret, rank[tier]
        runs = {}
        for cc in COST_CASES:
            runs[(cc, 'base')] = se.simulate(sc, el, rt, rank=rk, n=n, ended=ended if tier != 'SECTOR_ETF' else None,
                                             venue=venue, haircut=haircuts['base'], cost_case=cc)
        for hm in ('all100', 'all30'):
            runs[('base', hm)] = se.simulate(sc, el, rt, rank=rk, n=n, ended=ended if tier != 'SECTOR_ETF' else None,
                                             venue=venue, haircut=haircuts[hm], cost_case='base')
        bench = benches[tier]
        per_variant = {}
        for (cc, hm), r in runs.items():
            m = r['monthly']
            m = m[m['n_held'] > 0]
            per_variant[f'{cc}|{hm}'] = stats_block(m['net'], bench, spy, rf, boot_draws)
            rows.append(dict(trial=trial_id, tier=tier, family=fam, architecture=arch, lookback=lb, N=n, primary=primary,
                             cost_case=cc, haircut=hm, months=len(m), **{f'net_{k}': v for k, v in se.ann_stats(m['net']).items()},
                             excess_ew_mean=per_variant[f'{cc}|{hm}']['excess_ew']['mean'], excess_ew_t=per_variant[f'{cc}|{hm}']['excess_ew']['t'],
                             excess_spy_mean=per_variant[f'{cc}|{hm}']['excess_spy']['mean'], capm_alpha_t=per_variant[f'{cc}|{hm}']['capm_vs_spy']['t'],
                             turnover_oneway_yr=float((m['turnover_buy'] + m['turnover_sell']).mean() * 6), cost_yr=float(m['cost'].mean() * 12),
                             skipped=int(m['skipped'].sum()), delisted=int(m['delisted'].sum())))
        base = runs[('base', 'base')]
        mb = base['monthly']; mb = mb[mb['n_held'] > 0]
        sb = per_variant['base|base']
        sv = survivor(sb, per_variant['stress|base'], len(mb))
        contrib = base['contributions'].reindex(mb.index)
        tot = float(contrib.sum().sum())
        top_names = (contrib.sum() / tot).sort_values(ascending=False).head(10) if tot > 0 else pd.Series(dtype=float)
        results[trial_id] = dict(tier=tier, family=fam, architecture=arch, lookback=lb, N=n, primary=primary, stats=per_variant,
                                 survivor=sv, sector_betas=sector_betas(mb['net'], sector_rets, rf),
                                 top10_name_share=float(top_names.sum()) if len(top_names) else np.nan,
                                 top10_names={k: float(v) for k, v in top_names.items()},
                                 feasibility={c: feasibility(mb, n, c, GATES['eur_usd']) for c in (500, 1000)},
                                 avg_held=float(mb['n_held'].mean()))
        monthly_out[trial_id] = mb['net']
        log.append(f'{trial_id}: months {len(mb)} net Sharpe {sb["net"]["sharpe"]:.2f} excess-EW t {sb["excess_ew"]["t"]:.2f} survivor {sv["passes"]}')
        print(log[-1], flush=True)

    # multiplicity across primary-eligible trials (all 24): BH-FDR on one-sided p of net excess vs EW
    pv = {tid: 1 - sps.norm.cdf(r['stats']['base|base']['excess_ew']['t']) for tid, r in results.items()}
    bh = bh_fdr(pv, GATES['bh_fdr'])
    srs = [r['stats']['base|base']['net']['sharpe'] for r in results.values()]
    for tid, r in results.items():
        r['bh_pass'] = tid in bh
        net = monthly_out[tid]
        r['dsr'] = dict(zip(('prob', 'sr0_annual'), deflated_sharpe(r['stats']['base|base']['net']['sharpe'], len(net), len(TRIALS),
                                                                    float(np.var(srs, ddof=1)), float(sps.skew(net)), float(sps.kurtosis(net, fisher=False)))))
        r['survivor']['multiplicity_pass'] = bool(r['bh_pass'] and r['dsr']['prob'] >= GATES['dsr_min'])
        r['survivor']['final'] = bool(r['survivor']['passes'] and r['survivor']['multiplicity_pass'])

    # overlays only on final survivors
    overlays = {}
    spy_adj_me = etf_adj['SPY'].reindex(sig_used)
    sma10 = spy_adj_me.rolling(10).mean()
    trend_on = (spy_adj_me > sma10).astype(float)
    spy_daily = frames['SPY']['adj_close'].pct_change()
    rv = spy_daily.groupby(spy_daily.index.to_period('M')).var()
    rv_prev = rv.shift(1)
    target = rv.expanding(60).median().shift(1)
    volw = (target / rv_prev).clip(upper=1.0)
    volw.index = volw.index.to_timestamp('M')
    volw = volw.reindex(pd.DatetimeIndex(sig_used).to_period('M').to_timestamp('M')); volw.index = sig_used
    for tid, r in results.items():
        if not r['survivor']['final']:
            continue
        tier, arch, lb, n = r['tier'], r['architecture'], r['lookback'], r['N']
        if tier == 'SECTOR_ETF':
            sc, el, rt, rk, en = etf_scores[f'mom{lb}'], etf_elig, etf_ret_aligned, None, None
        else:
            key = {'mom': f'mom{lb}', 'resid': f'resid{lb}', 'volmom': f'volmom{lb}', 'secneutral': f'secneutral{lb}'}[arch]
            sc, el, rt, rk, en = scores[key], elig[tier], ret, rank[tier], ended
        for name, expo in (('trend_sma10', trend_on), ('volcap1', volw.fillna(1.0))):
            o = se.simulate(sc, el, rt, rank=rk, n=n, ended=en, venue=venue, haircut=haircuts['base'], cost_case='base', exposure=expo)
            m = o['monthly']; m = m[m['n_held'] > 0]
            overlays[f'{tid}|{name}'] = dict(stats=stats_block(m['net'], benches[tier], spy, rf, boot_draws), base_net=r['stats']['base|base']['net'])
            monthly_out[f'{tid}|{name}'] = m['net']

    meta = dict(experiment='E051', stamp=stamp, seed=SEED, boot_draws=boot_draws, t2_start_year=t2_start_year, gates=GATES,
                trials=[t[0] for t in TRIALS], n_trials=len(TRIALS), development_end=str(DEV_END.date()),
                panel_manifest=json.loads(pnl.BUILD_MANIFEST.read_text(encoding='utf8')),
                source_sha256={p: sha256_file(ROOT / 'research' / p) for p in ('phase6_e051_run.py', 'phase6_stock_engine.py', 'phase6_stock_universe.py', 'phase6_eodhd_panel.py')},
                gate_doc_sha256=sha256_file(ROOT / 'PHASE6_NORGATE_PURCHASE_GATE.md'),
                universe_counts=counts, delistings_booked_in_eligible=n_delist, extreme_monthly_returns=extreme, i5_substitutions=n_subst, i3_unclean_names_mean_by_year=unclean_counts, sector_labels_available=len(labels),
                signals=dict(first=str(sig_used[0].date()), last=str(sig_used[-1].date()), n=len(sig_used)), log=log)
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=meta, results=results, overlays=overlays,
                                                          benchmarks={k: se.ann_stats(v) for k, v in benches.items()}), indent=1, default=float), encoding='utf8')
    pd.DataFrame(rows).to_csv(out_dir / 'trials.csv', index=False)
    pd.DataFrame(monthly_out).to_csv(out_dir / 'monthly_net.csv')
    pd.DataFrame(benches).to_csv(out_dir / 'benchmarks_monthly.csv')
    spy.to_csv(out_dir / 'spy_monthly.csv')
    print(out_dir)
    return out_dir


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--t2-start', type=int, required=True)
    ap.add_argument('--boot', type=int, default=4000)
    a = ap.parse_args()
    main(a.t2_start, a.boot)
