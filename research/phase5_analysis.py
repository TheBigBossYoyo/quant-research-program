"""E048: Branch A analysis - cohort-2 replication statistics, cross-cohort meta-analysis, temporal/regime,
long-short, crash windows, concentration, Monte Carlo and the preregistered gate. No strategy changes.
"""
import json
import hashlib
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from core import ROOT
from phase4_data import freeze_check
from phase4_run import read_hourly
from phase4_stats import stats, factor_fit, bootstrap_meta, montecarlo, allocation, portfolio, remove_diagnostics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DAYS = pd.date_range('2021-01-01', '2025-01-01', inclusive='left', freq='D', tz='UTC')
DAYS1 = pd.date_range('2022-01-01', '2025-01-01', inclusive='left', freq='D', tz='UTC')
CRASHES = {'2021-05 crash': ('2021-05-01', '2021-07-20'), '2021-11..2022-06 bear': ('2021-11-10', '2022-06-30'), '2022-11 FTX': ('2022-11-01', '2022-12-31'), '2024-08 unwind': ('2024-08-01', '2024-08-15'), '2022 calendar': ('2022-01-01', '2022-12-31')}
HALVES = [(f'{y}H{h}', f'{y}-{"01" if h == 1 else "07"}-01', f'{y}-{"06-30" if h == 1 else "12-31"}') for y in [2021, 2022, 2023, 2024] for h in [1, 2]]


def table(df):
    def f(x):
        return f'{x:.4g}' if isinstance(x, (float, np.floating)) else str(x)
    return '| ' + ' | '.join(map(str, df.columns)) + ' |\n|' + '|'.join(['---'] * len(df.columns)) + '|\n' + ''.join('| ' + ' | '.join(f(x) for x in row) + ' |\n' for row in df.itertuples(index=False, name=None))


def portfolio_trades(source, assets, start, case='stress', prefix='trend'):
    rows = []; daily = []
    for sym in assets:
        pp = pd.read_csv(source / sym / f'{prefix}_{case}_path.csv', index_col=0, parse_dates=True); tt = pd.read_csv(source / sym / f'{prefix}_{case}_trades.csv', parse_dates=['entry_time', 'exit_time'])
        denom = pp.equity.resample('D').last().shift(1).fillna(10000.); scale = (start / len(assets) / denom).reindex(pp.index.normalize()).to_numpy()
        for row in tt.to_dict('records'):
            v = pp.long_pnl if row['side'] > 0 else pp.short_pnl; mask = (pp.index >= row['entry_time']) & (pp.index <= row['exit_time'])
            c = pd.Series(np.where(mask, v.to_numpy() * scale, 0.), index=pp.index).resample('D').sum().reindex(start.index).fillna(0.)
            rows.append(dict(asset=sym, side=row['side'], pnl=float(c.sum()), entry_time=row['entry_time'], exit_time=row['exit_time'])); daily.append(c.to_numpy())
    return pd.DataFrame(rows), np.array(daily)


def main():
    freeze_check(); spec = json.loads((ROOT / 'PHASE5_COHORT2.json').read_text(encoding='utf-8')); assets = spec['assets']; new = spec['overlap']['new_names']; overlap = spec['overlap']['overlapping']
    cohort1 = json.loads((ROOT / 'PHASE4_UNIVERSE.json').read_text())['assets']
    source = ROOT / 'reports' / (ROOT / 'reports/PHASE5_ACTIVE_REPLICATION.txt').read_text().strip(); src1 = ROOT / 'reports' / (ROOT / 'reports/PHASE4_ACTIVE_REPLICATION.txt').read_text().strip()
    if not (source / 'results.json').exists(): raise ValueError('E047 incomplete')
    out = ROOT / 'reports' / ('E048_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')); out.mkdir(exist_ok=False); (out / 'charts').mkdir(); (ROOT / 'reports/PHASE5_ACTIVE_ANALYSIS.txt').write_text(out.name)
    M = pd.read_csv(source / 'metrics.csv'); d = pd.read_csv(source / 'daily_panel.csv'); d['date'] = pd.to_datetime(d.date, utc=True)
    M1 = pd.read_csv(src1 / 'metrics.csv'); d1 = pd.read_csv(src1 / 'daily_panel.csv'); d1['date'] = pd.to_datetime(d1.date, utc=True)
    def panel(case='stress', col='ret', names=None, dd=d, comp=None):
        x = dd[(dd.case == case) & ((dd.component == comp) if comp else True)] if 'component' in dd.columns else dd[dd.case == case]
        return x.pivot(index='date', columns='asset', values=col).reindex(columns=names or assets).fillna(0.)
    B = pd.DataFrame({s: pd.read_csv(source / s / 'underlying_daily.csv', index_col=0, parse_dates=True).iloc[:, 0] for s in assets}); B.index = pd.to_datetime(B.index, utc=True)
    btc, _ = read_hourly('BTCUSDT', 'klines'); bclose = btc.close.resample('D').last(); btc_r = bclose.pct_change(fill_method=None).reindex(DAYS).fillna(0.)
    bvol = btc_r.rolling(30).std().shift(1) * np.sqrt(365); btrend = np.sign(bclose - bclose.rolling(200).mean()).shift(1).reindex(DAYS)
    market = B[assets].mean(1)
    # 1. per-asset factor regressions: PRIMARY two-factor (underlying + BTC), secondary Phase-4 five-factor
    R = panel(); rows = []; adj = {}; mats = {}
    for s in assets:
        X2 = pd.DataFrame(dict(underlying=B[s], BTC=btc_r), index=DAYS); X5 = pd.DataFrame(dict(underlying=B[s], BTC=btc_r, market=market, volatility=bvol, trend_state=btrend), index=DAYS)
        m2, a2 = factor_fit(R[s], X2); m5, _ = factor_fit(R[s], X5); u, _ = factor_fit(R[s], X2[['underlying']]); adj[s] = a2; mats[s] = X2
        rows.append(dict(asset=s, alpha2=m2['alpha_annual'], alpha2_ci_low=m2['alpha_ci95_low'], alpha2_ci_high=m2['alpha_ci95_high'], beta_underlying=m2['beta']['underlying'], beta_btc=m2['beta']['BTC'], r2_two_factor=m2['r_squared'],
                         alpha5=m5['alpha_annual'], alpha5_ci_low=m5['alpha_ci95_low'], alpha5_ci_high=m5['alpha_ci95_high'], alpha_univariate=u['alpha_annual'], beta_univariate=u['beta']['underlying'], factor_adjusted_sharpe2=m2['factor_adjusted_sharpe']))
    F = pd.DataFrame(rows); S = M[M.case == 'stress'].merge(F, on='asset'); S['new_name'] = S.asset.isin(new)
    S.to_csv(ROOT / 'PHASE5_REPLICATION_RESULTS.csv', index=False); S.to_csv(out / 'replication_results.csv', index=False)
    meta = bootstrap_meta(R, pd.DataFrame(adj), factor_matrices=mats); (out / 'meta_cohort2.json').write_text(json.dumps(meta, indent=2))
    Rn = R[new]; meta_new = bootstrap_meta(Rn, pd.DataFrame({s: adj[s] for s in new}), factor_matrices={s: mats[s] for s in new}); (out / 'meta_new_names.json').write_text(json.dumps(meta_new, indent=2))
    # 2. portfolios (equal-weight primary, inverse-vol secondary), stress cases
    ports = {}; prow = []
    for case in ['base', 'stress', 'slippage_1_5', 'slippage_2', 'asset_conservative', 'delay1', 'adverse_funding', 'vol_scaled']:
        Rc = panel(case); Gc = panel(case, 'gross')
        for method in (['equal', 'inverse_vol'] if case == 'stress' else ['equal']):
            pr, trn = portfolio(Rc, allocation(Rc, method), Gc, .0014); ports[case + '__' + method] = pr; m = stats(pr)
            u, _ = factor_fit(pr, pd.DataFrame(dict(BTC=btc_r, market=market), index=DAYS)); m.update(case=case, weighting=method, alpha_btc_market=u['alpha_annual'], alpha_ci_low=u['alpha_ci95_low'], alpha_ci_high=u['alpha_ci95_high'], beta_btc=u['beta']['BTC'], beta_market=u['beta']['market'],
                                                                                              gross_exposure=float((allocation(Rc, method) * Gc).sum(1).mean()), net_exposure=float((allocation(Rc, method) * panel(case, 'net')).sum(1).mean()), annual_turnover=float(((allocation(Rc, method) * panel(case, 'turnover')).sum(1) + trn).sum() * 365 / len(DAYS)),
                                                                                              positive_asset_fraction=float((M[(M.case == case)].total_net_return > 0).mean()), median_asset_sharpe=float(M[M.case == case].sharpe.median()))
            for y in [2021, 2022, 2023, 2024]: m[f'ret_{y}'] = float((1 + pr[pr.index.year == y]).prod() - 1)
            prow.append(m)
    P = pd.DataFrame(prow); P.to_csv(out / 'portfolios.csv', index=False); pd.DataFrame(ports).to_csv(out / 'portfolio_daily.csv'); key = 'stress__equal'; pp = ports[key]
    # 3. concentration and Monte Carlo (portfolio and per asset)
    ep = (1 + pp).cumprod() * 10000; start = ep.shift(1).fillna(10000.); pt, td = portfolio_trades(source, assets, start); pt.to_csv(out / 'portfolio_trade_contributions.csv', index=False)
    pos = float(pt.pnl[pt.pnl > 0].sum()); conc = remove_diagnostics(pp); conc.update(top1_trade_share=float(pt.pnl.nlargest(1).sum() / pos), top5_trade_share=float(pt.pnl.nlargest(5).sum() / pos), top10_trade_share=float(pt.pnl.nlargest(10).sum() / pos), trades=len(pt))
    for n in [1, 5]:
        ids = pt.nlargest(n, 'pnl').index.to_numpy(); conc[f'remove_best{n}_trade_contributions'] = stats(pp - pd.Series(td[ids].sum(0), index=DAYS) / start)
    q = ep.diff(); q.iloc[0] = ep.iloc[0] - 10000; qs = q.groupby(q.index.to_period('Q')).sum(); conc['top_quarter_share'] = float(qs.max() / qs[qs > 0].sum()); conc['quarter_pnl'] = {str(k): float(v) for k, v in qs.items()}
    conc_assets = {s: remove_diagnostics(R[s], pd.read_csv(source / s / 'trend_stress_trades.csv', parse_dates=['entry_time', 'exit_time'])) for s in assets}
    mc = {key: montecarlo(pp), 'stress__inverse_vol': montecarlo(ports['stress__inverse_vol'])}; mc.update({s: montecarlo(R[s]) for s in assets})
    (out / 'concentration.json').write_text(json.dumps(dict(portfolio=conc, assets=conc_assets), indent=2, default=float)); (out / 'monte_carlo.json').write_text(json.dumps(mc, indent=2))
    # 4. temporal / regime analysis (calendar half-years, BTC trend state), long/short, crashes
    G = panel('stress', 'gross'); N = panel('stress', 'net'); L = panel('stress', 'long_ret'); Sh = panel('stress', 'short_ret'); TO = panel('stress', 'turnover'); W = allocation(R)
    pl = (W * L).sum(1); ps = (W * Sh).sum(1); pg = (W * G).sum(1); pn = (W * N).sum(1); pto = (W * TO).sum(1); mkt = market
    def seg(mask, label):
        r = pp[mask]; e = (1 + r).cumprod(); dd = float((e / e.cummax().clip(lower=1) - 1).min()); ub = (1 + mkt[mask]).cumprod(); udd = float((ub / ub.cummax().clip(lower=1) - 1).min())
        beta = float(np.cov(r, btc_r[mask])[0, 1] / btc_r[mask].var()) if btc_r[mask].var() > 0 else np.nan
        return dict(period=label, days=int(mask.sum()), underlying_ew_return=float(ub.iloc[-1] - 1), underlying_ew_drawdown=udd, btc_return=float((1 + btc_r[mask]).prod() - 1), strategy_return=float(e.iloc[-1] - 1), strategy_sharpe=float(r.mean() / r.std() * np.sqrt(365)) if r.std() > 0 else np.nan,
                    strategy_drawdown=dd, worst_day=float(r.min()), avg_gross=float(pg[mask].mean()), avg_net=float(pn[mask].mean()), peak_gross=float(pg[mask].max()), long_contribution=float(pl[mask].sum()), short_contribution=float(ps[mask].sum()), turnover=float(pto[mask].sum()), btc_beta=beta,
                    trend_prevalence=float(G[mask].mean().mean()), positive_assets=int((R[mask].sum() > 0).sum()))
    T = pd.DataFrame([seg((pp.index >= pd.Timestamp(a, tz='UTC')) & (pp.index <= pd.Timestamp(b, tz='UTC')), lab) for lab, a, b in HALVES] + [seg(btrend.reindex(DAYS).fillna(0) > 0, 'BTC above lagged 200d SMA'), seg(btrend.reindex(DAYS).fillna(0) < 0, 'BTC below lagged 200d SMA')])
    C = pd.DataFrame([seg((pp.index >= pd.Timestamp(a, tz='UTC')) & (pp.index <= pd.Timestamp(b, tz='UTC')), lab) for lab, (a, b) in CRASHES.items()])
    T.to_csv(out / 'temporal_regimes.csv', index=False); C.to_csv(out / 'crash_windows.csv', index=False)
    ls_assets = M[M.case == 'stress'][['asset', 'long_pnl_usdt', 'short_pnl_usdt', 'total_net_return', 'sharpe']].copy(); ls_assets['long_share_of_gross_pnl'] = ls_assets.long_pnl_usdt / (ls_assets.long_pnl_usdt.abs() + ls_assets.short_pnl_usdt.abs())
    short_only = ps; long_only = pl; full_noshort = pp - ps
    ls = dict(portfolio_long_contribution=float(pl.sum()), portfolio_short_contribution=float(ps.sum()), short_side_sharpe=float(ps.mean() / ps.std() * np.sqrt(365)), long_side_sharpe=float(pl.mean() / pl.std() * np.sqrt(365)),
              short_side_expectancy_annual=float(ps.mean() * 365), drawdown_full=stats(pp)['max_dd'], drawdown_without_short_contribution=stats(full_noshort)['max_dd'], sharpe_without_short_contribution=stats(full_noshort)['sharpe'],
              short_contribution_by_year={y: float(ps[ps.index.year == y].sum()) for y in [2021, 2022, 2023, 2024]}, long_contribution_by_year={y: float(pl[pl.index.year == y].sum()) for y in [2021, 2022, 2023, 2024]},
              assets_with_positive_short_pnl=int((ls_assets.short_pnl_usdt > 0).sum()), assets_with_positive_long_pnl=int((ls_assets.long_pnl_usdt > 0).sum()))
    (out / 'long_short.json').write_text(json.dumps(ls, indent=2)); ls_assets.to_csv(out / 'long_short_assets.csv', index=False)
    # 5. cross-cohort meta-analysis (cohort 1 trend-only 2022-2024 from E044; cohort 2 cells)
    R1 = panel('stress', 'ret', cohort1, d1, 'trend').reindex(DAYS1); p1, _ = portfolio(R1, allocation(R1), panel('stress', 'gross', cohort1, d1, 'trend').reindex(DAYS1), .0014)
    B1 = pd.DataFrame({s: pd.read_csv(src1 / s / 'underlying_daily.csv', index_col=0, parse_dates=True).iloc[:, 0] for s in cohort1}); B1.index = pd.to_datetime(B1.index, utc=True)
    adj1 = {}; mats1 = {}; a1rows = []
    for s in cohort1:
        X = pd.DataFrame(dict(underlying=B1[s], BTC=btc_r.reindex(DAYS1)), index=DAYS1); m, a = factor_fit(R1[s], X); adj1[s] = a; mats1[s] = X; a1rows.append(dict(asset=s, alpha2=m['alpha_annual'], sharpe=float(R1[s].mean() / R1[s].std() * np.sqrt(365)), ret=float((1 + R1[s]).prod() - 1)))
    A1 = pd.DataFrame(a1rows); meta1 = bootstrap_meta(R1, pd.DataFrame(adj1), factor_matrices=mats1)
    def cell(Rx, Fx_alpha, label, port):
        sh = Rx.mean() / Rx.std() * np.sqrt(365); ret = (1 + Rx).prod() - 1; ms = stats(port)
        return dict(cell=label, assets=Rx.shape[1], days=len(Rx), positive_net_fraction=float((ret > 0).mean()), positive_sharpe_fraction=float((sh > 0).mean()), median_sharpe=float(sh.median()), median_alpha2=float(np.median(Fx_alpha)), positive_alpha_fraction=float((np.asarray(Fx_alpha) > 0).mean()),
                    portfolio_sharpe=ms['sharpe'], portfolio_cagr=ms['cagr'], portfolio_max_dd=ms['max_dd'], portfolio_return=ms['total_net_return'])
    R2_22 = R.reindex(DAYS1); p2_22, _ = portfolio(R2_22, allocation(R2_22), G.reindex(DAYS1), .0014); Rn22 = R2_22[new]; pn22, _ = portfolio(Rn22, allocation(Rn22), G.reindex(DAYS1)[new], .0014)
    R21 = R[R.index.year == 2021]; p21 = pp[pp.index.year == 2021]; Rnew = R[new]; pnew, _ = portfolio(Rnew, allocation(Rnew), G[new], .0014); Rov = R[overlap]; pov, _ = portfolio(Rov, allocation(Rov), G[overlap], .0014)
    alpha_year = {}
    for y in [2021, 2022, 2023, 2024]:
        alpha_year[y] = [factor_fit(R[s][R.index.year == y], mats[s][mats[s].index.year == y])[0]['alpha_annual'] for s in assets]
    cells = pd.DataFrame([cell(R1, A1.alpha2, 'Cohort 1 (Phase 4, 12 names) trend-only 2022-2024', p1), cell(R, F.alpha2, 'Cohort 2 (12 names) 2021-2024', pp), cell(Rnew, F.set_index('asset').loc[new].alpha2, 'Cohort 2 NEW names (7) 2021-2024', pnew),
                          cell(Rov, F.set_index('asset').loc[overlap].alpha2, 'Cohort 2 overlapping names (5) 2021-2024', pov), cell(R21, alpha_year[2021], 'Cohort 2 calendar 2021 (new regime)', p21), cell(R2_22, [factor_fit(R2_22[s], mats[s].reindex(DAYS1))[0]['alpha_annual'] for s in assets], 'Cohort 2 2022-2024 (same window as cohort 1)', p2_22),
                          cell(Rn22, [factor_fit(Rn22[s], mats[s].reindex(DAYS1))[0]['alpha_annual'] for s in new], 'Cohort 2 NEW names 2022-2024', pn22)])
    g = np.random.default_rng(20260909); n = len(DAYS1); c1 = p1.to_numpy(); c2 = p2_22.to_numpy(); boot = {'cohort1_sharpe_ci': [], 'cohort2_sharpe_ci': [], 'difference_ci': []}
    sh1 = []; sh2 = []; dif = []
    for j in range(2000):
        st = g.integers(0, n, int(np.ceil(n / 30))); idx = ((st[:, None] + np.arange(30)) % n).ravel()[:n]; a = c1[idx]; b = c2[idx]
        sh1.append(a.mean() / a.std() * np.sqrt(365)); sh2.append(b.mean() / b.std() * np.sqrt(365)); dif.append(sh2[-1] - sh1[-1])
    boot = dict(cohort1_portfolio_sharpe_ci95=np.quantile(sh1, [.025, .975]).tolist(), cohort2_portfolio_sharpe_ci95_2022_2024=np.quantile(sh2, [.025, .975]).tolist(), difference_ci95=np.quantile(dif, [.025, .975]).tolist(), portfolio_correlation_2022_2024=float(p1.corr(p2_22)),
                monthly_return_correlation=float(p1.resample('ME').apply(lambda z: (1 + z).prod() - 1).corr(p2_22.resample('ME').apply(lambda z: (1 + z).prod() - 1))), new_names_vs_cohort1_portfolio_correlation=float(p1.corr(pn22)),
                cohort_year_signs={f'c1_{y}': float((1 + p1[p1.index.year == y]).prod() - 1) for y in [2022, 2023, 2024]} | {f'c2_{y}': float((1 + pp[pp.index.year == y]).prod() - 1) for y in [2021, 2022, 2023, 2024]},
                median_alpha2_by_year_cohort2={y: float(np.median(v)) for y, v in alpha_year.items()}, heterogeneity_between_cohorts=dict(median_sharpe_c1=float(cells.median_sharpe.iloc[0]), median_sharpe_c2=float(cells.median_sharpe.iloc[1]), median_sharpe_new=float(cells.median_sharpe.iloc[2])))
    (out / 'cross_cohort.json').write_text(json.dumps(dict(cells=cells.to_dict('records'), bootstrap=boot, meta_cohort1=meta1, meta_cohort2=meta, meta_new_names=meta_new), indent=2, default=float)); cells.to_csv(out / 'cross_cohort_cells.csv', index=False)
    # 6. gates
    lower = min(v['median_alpha_ci95'][0] for k, v in meta.items() if k in ['14', '30', '60']); stress = P[(P.case == 'stress') & (P.weighting == 'equal')].iloc[0]; cons = P[(P.case == 'asset_conservative')].iloc[0]; vs = P[P.case == 'vol_scaled'].iloc[0]
    positive = float((S.total_net_return > 0).mean()); newS = S[S.new_name]
    gates = dict(G1_assets=len(assets) >= 8, G2_positive_fraction=positive >= 2 / 3, G3_positive_sharpe_fraction=float((S.sharpe > 0).mean()) >= 2 / 3, G4_median_sharpe=float(S.sharpe.median()) >= .3, G5_median_alpha2=float(S.alpha2.median()) > 0, G6_common_block_lower_alpha=lower > 0,
                 G7_new_names=(float((newS.total_net_return > 0).mean()) >= .5) and (float(newS.sharpe.median()) > 0), G8_2021_positive=stress.ret_2021 > 0, G9_years=sum(stress[f'ret_{y}'] > 0 for y in [2021, 2022, 2023, 2024]) >= 3,
                 G10_conservative=(cons.total_net_return > 0) and (cons.positive_asset_fraction >= .5), G11_vol_scaled=vs.total_net_return > 0, G12_remove_best_year=conc['remove_best_year']['total_net_return'] > 0, G13_concentration=(conc['top5_trade_share'] < .5) and (stress.top_year_positive_pnl_share < .6),
                 G14_drawdown=stress.max_dd > -.4, G15_overlap=spec['overlap']['overlap_share'] <= .5, G16_no_defects=bool(abs(float(td.sum()) - float((R.mul(start / len(assets), axis=0)).sum().sum())) < 1e-6))
    gates = {k: bool(v) for k, v in gates.items()}
    core = ['G1_assets', 'G2_positive_fraction', 'G3_positive_sharpe_fraction', 'G4_median_sharpe', 'G5_median_alpha2', 'G6_common_block_lower_alpha', 'G7_new_names', 'G8_2021_positive', 'G9_years', 'G10_conservative', 'G11_vol_scaled', 'G15_overlap', 'G16_no_defects']
    if S.total_net_return.median() <= 0 and positive <= .5: verdict = 'TREND_REPLICATION_FAILURE'
    elif positive < 2 / 3 or not gates['G7_new_names']: verdict = 'TREND_MIXED_REPLICATION'
    elif all(gates.values()): verdict = 'TREND_VALIDATION_ELIGIBLE'
    elif all(gates[k] for k in core): verdict = 'TREND_CROSS_COHORT_RESEARCH_PROMISING'
    else: verdict = 'TREND_CROSS_COHORT_WEAK_SIGNAL'
    decision = 'OPEN_2025_ONCE_AFTER_FINAL_FREEZE' if verdict == 'TREND_VALIDATION_ELIGIBLE' else 'DO_NOT_OPEN_2025'
    summary = dict(experiment_id=out.name, source=source.name, classification=verdict, decision=decision, gates=gates, positive_fraction=positive, positive_sharpe_fraction=float((S.sharpe > 0).mean()), median_sharpe=float(S.sharpe.median()), median_cagr=float(S.cagr.median()), median_drawdown=float(S.max_dd.median()),
                   median_alpha2=float(S.alpha2.median()), median_alpha5=float(S.alpha5.median()), median_alpha_univariate=float(S.alpha_univariate.median()), positive_alpha2_fraction=float((S.alpha2 > 0).mean()), common_block_lower_alpha2=lower, meta_cohort2=meta, new_names=dict(positive_fraction=float((newS.total_net_return > 0).mean()), median_sharpe=float(newS.sharpe.median()), median_alpha2=float(newS.alpha2.median())),
                   primary_portfolio=stress.to_dict(), concentration=conc, long_short=ls, cross_cohort=boot, trend_spec_sha256=(ROOT / 'PHASE5_TREND_FROZEN_SPEC.sha256').read_text().strip(), cohort_sha256=spec and (ROOT / 'PHASE5_COHORT2.sha256').read_text().strip(),
                   source_hashes={str(q.relative_to(ROOT)): hashlib.sha256(q.read_bytes()).hexdigest() for q in sorted((ROOT / 'research').glob('*.py'))}, validation_2025='LOCKED', holdout_2026='UNTOUCHED')
    (out / 'results.json').write_text(json.dumps(summary, indent=2, default=lambda x: x.item() if hasattr(x, 'item') else str(x)))
    # 7. documents
    def save(name): plt.tight_layout(); plt.savefig(out / 'charts' / (name + '.png'), bbox_inches='tight'); plt.close()
    (1 + R).cumprod().plot(figsize=(11, 6), logy=True); plt.title('Cohort 2: frozen slow trend, net, by asset'); save('equity_by_asset')
    pd.DataFrame({'cohort 2 (2021-24)': (1 + pp).cumprod(), 'cohort 1 (2022-24)': (1 + p1).cumprod().reindex(DAYS), 'cohort-2 underlyings EW': (1 + mkt).cumprod()}).plot(figsize=(11, 5), logy=True); plt.title('Equal-weight trend portfolios vs underlyings'); save('portfolios')
    T.set_index('period')[['strategy_return', 'underlying_ew_return']].iloc[:8].plot.bar(figsize=(10, 4)); plt.axhline(0, color='k', lw=.6); plt.title('Half-year returns: strategy vs underlyings'); save('half_years')
    pd.DataFrame({'long': pl.cumsum(), 'short': ps.cumsum()}).plot(figsize=(10, 4)); plt.title('Cumulative long vs short contribution (fraction of capital)'); save('long_short')
    md = ['# PHASE5_CROSS_COHORT_ANALYSIS', '', f'Branch A analysis {out.name} of replication {source.name}; cohort 1 trend-only sleeves from {src1.name}. Frozen slow-trend rule, stress costs (9.05 bps + funding), one sleeve per asset, equal-weight cohort portfolios net of 14 bps allocation-transfer estimates. Classification: **{verdict}**; decision: **{decision}**.', '',
          '## Per-asset results, cohort 2 (2021-2024)', '', table(S[['asset', 'new_name', 'total_net_return', 'cagr', 'sharpe', 'sortino', 'max_dd', 'trades', 'win_rate', 'profit_factor', 'expectancy', 'gross_exposure', 'net_exposure', 'max_gross', 'annual_turnover', 'beta_underlying', 'beta_btc', 'alpha2', 'alpha2_ci_low', 'alpha2_ci_high', 'alpha_univariate', 'alpha5', 'top5_trade_positive_pnl_share', 'top_year_positive_pnl_share']]),
          '## Cohort cells (the replication unit)', '', table(cells), '', '## Cohort-level dependence-aware statistics', '', '```', json.dumps(dict(cohort2_common_block=meta, new_names_common_block=meta_new, cohort1_common_block=meta1, cohort_portfolio_bootstrap=boot), indent=1, default=float), '```', '',
          '## Portfolios and stress cases', '', table(P[['case', 'weighting', 'total_net_return', 'cagr', 'sharpe', 'sortino', 'max_dd', 'drawdown_duration_days', 'expected_shortfall_95', 'gross_exposure', 'net_exposure', 'annual_turnover', 'alpha_btc_market', 'alpha_ci_low', 'alpha_ci_high', 'beta_btc', 'positive_asset_fraction', 'median_asset_sharpe', 'ret_2021', 'ret_2022', 'ret_2023', 'ret_2024', 'top_year_positive_pnl_share']]), '',
          '## Gates', '', table(pd.DataFrame([dict(gate=k, passed=bool(v)) for k, v in gates.items()])), '', '## Concentration (primary portfolio)', '', '```', json.dumps({k: v for k, v in conc.items() if k != 'quarter_pnl'}, indent=1, default=float), '```', '', 'Quarter P&L (USDT per 10,000): ' + json.dumps(conc['quarter_pnl']), '', '## Monte Carlo (primary portfolio)', '', '```', json.dumps(mc[key], indent=1), '```']
    (ROOT / 'PHASE5_CROSS_COHORT_ANALYSIS.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    (ROOT / 'PHASE5_TEMPORAL_CONCENTRATION.md').write_text('# PHASE5_TEMPORAL_CONCENTRATION\n\nPreregistered calendar half-years and lagged BTC 200-day trend state; cohort-2 equal-weight trend portfolio (stress costs). Trend prevalence = mean absolute sleeve exposure. Long/short contributions are fractions of portfolio capital.\n\n' + table(T) + '\n## Crash / bear windows (fixed in PHASE5_PLAN.md)\n\n' + table(C) + '\n## Quarterly P&L concentration\n\n' + json.dumps(conc['quarter_pnl']) + f"\n\nTop quarter share of positive quarterly P&L: {conc['top_quarter_share']:.1%}; top year share {stress.top_year_positive_pnl_share:.1%}; top-5 trades {conc['top5_trade_share']:.1%}.\n", encoding='utf-8')
    (ROOT / 'PHASE5_LONG_SHORT_ANALYSIS.md').write_text('# PHASE5_LONG_SHORT_ANALYSIS\n\nCohort-2 equal-weight trend portfolio, stress costs. Long/short P&L from the ledger episode accounting (fees and funding assigned to the side that paid them).\n\n```\n' + json.dumps(ls, indent=1) + '\n```\n\n## Per asset (USDT per 10,000 sleeve capital)\n\n' + table(ls_assets), encoding='utf-8')
    print('FINAL', json.dumps(dict(classification=verdict, decision=decision, positive=positive, median_sharpe=summary['median_sharpe'], median_alpha2=summary['median_alpha2'], lower=lower, gates=gates), default=str)); print('OUTPUT', out)


if __name__ == '__main__':
    main()
