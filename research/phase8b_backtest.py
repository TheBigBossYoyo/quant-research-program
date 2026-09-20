"""Phase 8B E062 return stage (runs ONLY after the classifier holdout gate is recorded as passed): event study, hold-all
calendar-time portfolio, benchmarks, factor diagnostics, frozen gates. Frozen rules: research/phase8b/PHASE8B_PREREGISTRATION.md.

Inputs: data/derived/phase8b/events.parquet (A/B events after dedup, with entry_idx/exit_idx on the SPY session calendar
and mapped codes), the Phase 6 development panels (lock-enforced), the Phase 8 universe machinery. Every date object is
guarded by phase8b_lock. The script refuses to run unless PHASE8B_FREEZE_HASHES.jsonl carries a 'classifier gate passed'
record. Usage (from research/): PYTHONUTF8=1 python phase8b_backtest.py
"""
from datetime import datetime, timezone
import hashlib
import json

import numpy as np
import pandas as pd
from scipy import stats as sps

import phase6_e051_run as run
import phase6_french as fr
import phase6_stock_engine as se
import phase6_stock_universe as su
from phase6_factor_screen import hac_mean, hac_alpha, sharpe, max_drawdown
from phase6_lock import ROOT
import phase8_insider_backtest as p8
import phase8b_edgar as ed
import phase8b_lock as lk
import phase8b_portfolio as pf
import phase8b_timing as tm

CFG = ed.CONFIG
OUT = ROOT / 'research/phase8b'
DERIVED = ed.DERIVED
HORIZONS = tuple(CFG['event_study']['horizons'])
HAC = CFG['benchmarks']['hac_lags']
G = CFG['gates']
WINDOWS = {'w2004_2012': ('2004-01-01', '2012-12-31'), 'w2013_2017': ('2013-01-01', '2017-12-31'), 'w2004_2017': ('2004-01-01', '2017-12-31')}
SEED = CFG['event_study']['bootstrap']['seed']
DRAWS = CFG['event_study']['bootstrap']['draws']


def gate_recorded(stage_prefix='classifier gate passed'):
    recs = [json.loads(l) for l in (OUT / 'PHASE8B_FREEZE_HASHES.jsonl').read_text(encoding='utf8').splitlines() if l.strip()]
    return any(r.get('stage', '').startswith(stage_prefix) for r in recs)


def load_factors():
    ff5 = fr.load('ff5_monthly', 'main'); ff5.columns = [c.strip() for c in ff5.columns]
    mom = fr.load('mom_factor_monthly', 'main'); mom.columns = [c.strip() for c in mom.columns]
    f = ff5.join(mom, how='inner'); f.index = f.index.to_period('M')
    lk.guard_dates(f.index.to_timestamp(), 'factors')
    return f


def cluster_stats(x, clusters, draws=DRAWS, seed=SEED):
    """Mean with a one-way cluster bootstrap CI (clusters resampled with replacement)."""
    x = np.asarray(x, dtype=float); clusters = np.asarray(clusters)
    ok = np.isfinite(x); x, clusters = x[ok], clusters[ok]
    if len(x) < 10:
        return dict(n=int(len(x)), mean=np.nan)
    groups = {c: x[clusters == c] for c in np.unique(clusters)}
    keys = list(groups); rng = np.random.default_rng(seed); means = []
    for _ in range(draws):
        pick = rng.integers(len(keys), size=len(keys))
        means.append(np.concatenate([groups[keys[p]] for p in pick]).mean())
    sd = float(np.std(means, ddof=1))
    return dict(n=int(len(x)), n_clusters=len(keys), mean=float(x.mean()), median=float(np.median(x)), ci=[float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))],
                t=float(x.mean() / sd) if sd > 0 else np.nan, share_positive=float((x > 0).mean()))


def event_study(ev, U, ao, ao_np, spy_ao_np, ended_info, venue):
    cal = U['cal']; study = {}
    for h in HORIZONS:
        rs, _ = p8.event_returns(ev, ao, cal, ended_info, venue, h)
        ew_b, spy_b = p8.bench_bh(ev, ao_np, ao.columns, U['elig'], cal, spy_ao_np, h)
        ar_ew, ar_spy = rs - ew_b, rs - spy_b
        months = ev['entry'].dt.to_period('M').astype(str).to_numpy(); ciks = ev['cik'].to_numpy()
        block = {}
        for w, (a, b) in WINDOWS.items():
            m = (ev['entry'] >= a) & (ev['entry'] <= b)
            block[w] = dict(raw=cluster_stats(rs[m], months[m]), ar_ew_month=cluster_stats(ar_ew[m], months[m]), ar_ew_cik=cluster_stats(ar_ew[m], ciks[m]),
                            ar_spy_month=cluster_stats(ar_spy[m], months[m]), ar_spy_cik=cluster_stats(ar_spy[m], ciks[m]))
        block['by_year'] = {int(y): dict(n=int(g.sum()), ar_ew=float(np.nanmean(ar_ew[g.to_numpy()])) if g.sum() else np.nan) for y, g in ((y, ev['entry'].dt.year == y) for y in sorted(ev['entry'].dt.year.unique()))}
        study[f'h{h}'] = block
        print(f'h{h}', {w: (round(block[w]['ar_ew_month']['mean'], 4), round(block[w]['ar_ew_month']['t'], 2), round(block[w]['ar_ew_cik']['t'], 2)) for w in WINDOWS}, flush=True)
    return study


def window_stats(net, bench, spy, factors):
    out = {}
    net = net.dropna(); idx = net.index; per = pd.DatetimeIndex(idx).to_period('M')
    f = factors.reindex(per); rf = f['RF'].to_numpy()          # French loader returns decimals (as in Phase 8)
    ex = (net - bench.reindex(idx)).dropna(); exs = (net - spy.reindex(idx)).dropna()
    for w, (a, b) in WINDOWS.items():
        x = ex[a:b]
        if len(x) < 12:
            continue
        nw = net[a:b]; sw = spy.reindex(idx)[a:b]; sel = (idx >= a) & (idx <= b); rw = rf[sel]; fw = f[sel]
        capm = hac_alpha(nw - rw, pd.DataFrame({'m': sw - rw}, index=nw.index), lags=HAC)
        ff3 = hac_alpha(nw - rw, pd.DataFrame({k: fw[k].to_numpy() for k in ('Mkt-RF', 'SMB', 'HML')}, index=nw.index), lags=HAC)
        ff6 = hac_alpha(nw - rw, pd.DataFrame({k: fw[k].to_numpy() for k in ('Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA', 'Mom')}, index=nw.index), lags=HAC)
        yearly = x.groupby(x.index.year).sum()
        out[w] = dict(months=int(len(x)), excess_ann=float(x.mean() * 12), excess_t=hac_mean(x, lags=HAC)['t'], excess_spy_ann=float(exs[a:b].mean() * 12),
                      net_cagr=se.ann_stats(nw)['cagr'], bench_cagr=se.ann_stats(bench.reindex(idx)[a:b])['cagr'], spy_cagr=se.ann_stats(sw)['cagr'],
                      net_sharpe=sharpe(nw - rw), spy_sharpe=sharpe(sw - rw), max_dd=max_drawdown(nw), spy_max_dd=max_drawdown(sw),
                      capm_alpha_ann=float(capm['alpha'] * 12), capm_t=capm['t'], beta=capm['betas'][0],
                      ff3_alpha_ann=float(ff3['alpha'] * 12), ff3_t=ff3['t'], ff3_betas=dict(zip(('mkt', 'smb', 'hml'), ff3['betas'])),
                      ff6_alpha_ann=float(ff6['alpha'] * 12), ff6_t=ff6['t'], ff6_betas=dict(zip(('mkt', 'smb', 'hml', 'rmw', 'cma', 'mom'), ff6['betas'])),
                      years_positive=int((yearly > 0).sum()), years=int(len(yearly)), yearly_excess={int(k): float(v) for k, v in yearly.items()})
    return out


def gates(ws, ws_auto, trades, ev, study, n_2013, n_total, turnover, dsr_prob):
    g = ws.get('w2013_2017', {}); e = ws.get('w2004_2012', {}); f = ws.get('w2004_2017', {})
    total_ex = sum(f.get('yearly_excess', {}).values()) if f else np.nan; best_year = max(f.get('yearly_excess', {}).values()) if f else np.nan
    pos = trades['pnl'].clip(lower=0) if len(trades) else pd.Series(dtype=float)          # gross gains (winning legs only) throughout
    gains = float(pos.sum()) if len(trades) else 0.0
    top5 = float(pos.nlargest(5).sum() / gains) if gains > 0 else np.nan
    top_ticker = float(pos.groupby(trades['code']).sum().max() / gains) if gains > 0 else np.nan
    sic = trades.merge(ev[['event_id', 'sic']], on='event_id', how='left'); sic['sic2'] = sic['sic'].astype(str).str[:2]
    top_sic = float(sic['pnl'].clip(lower=0).groupby(sic['sic2']).sum().max() / gains) if gains > 0 else np.nan
    h = study['h252']['w2013_2017']; hf = study['h252']['w2004_2017']
    checks = dict(G1_excess=g.get('excess_ann', np.nan) >= G['G1_excess_ann_min'], G2_t=g.get('excess_t', np.nan) >= G['G2_nw_t_min'], G3_years=g.get('years_positive', 0) >= G['G3_years_positive_min'],
                  G4_alpha=(g.get('capm_alpha_ann', np.nan) >= G['G4_capm_alpha_min'] and g.get('capm_t', np.nan) >= G['G4_capm_t_min'] and g.get('ff6_alpha_ann', np.nan) >= G['G4_ff5mom_alpha_min'] and g.get('ff6_t', np.nan) >= G['G4_ff5mom_t_min']),
                  G5_dd=f.get('max_dd', np.nan) >= f.get('spy_max_dd', np.nan) - G['G5_dd_tolerance'], G6_turnover=turnover <= G['G6_turnover_max'],
                  G7_automated=ws_auto.get('w2013_2017', {}).get('excess_ann', np.nan) > G['G7_automated_excess_min'],
                  G8_concentration=((best_year / total_ex <= G['G8_best_year_share_max']) if total_ex > 0 else False) and top5 <= G['G8_top5_events_share_max'] and top_ticker <= G['G8_top_ticker_share_max'] and top_sic <= G['G8_top_sic2_share_max'],
                  G9_early=e.get('excess_ann', np.nan) >= G['G9_early_excess_min'] or (g.get('excess_ann', np.nan) >= G['G1_excess_ann_min'] and g.get('excess_t', np.nan) >= G['G2_nw_t_min']),
                  G10_sample=n_2013 >= G['G10_events_2013_2017_min'] and n_total >= G['G10_events_total_min'],
                  G11_event_study=h['ar_ew_month']['mean'] > 0 and min(h['ar_ew_month']['t'], h['ar_ew_cik']['t']) >= G['G11_h252_cluster_t_min'] and hf['ar_ew_month']['mean'] > 0,
                  G12_dsr=dsr_prob >= G['G12_dsr_prob_min'])
    return dict(checks={k: bool(v) for k, v in checks.items()}, best_year_share=float(best_year / total_ex) if total_ex else np.nan, top5_share=top5, top_ticker_share=top_ticker, top_sic2_share=top_sic)


def main():
    if not gate_recorded():
        raise RuntimeError('return stage refused: no "classifier gate passed" record in PHASE8B_FREEZE_HASHES.jsonl')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'); out_dir = ROOT / 'reports' / f'E062_{stamp}'; out_dir.mkdir(parents=True)
    U = p8.load_universe()
    for k in ('cal', 'sig', 'ex'):
        lk.guard_dates(U[k], k)
    ev = pd.read_parquet(DERIVED / 'events.parquet')
    lk.guard_frame(ev, 'events', date_columns=('entry', 'exit', 'accept_et'))
    cal = U['cal']
    # align event sessions to the universe calendar (both are the vendor session set)
    ev['entry_idx'] = cal.searchsorted(ev['entry'].to_numpy())
    if not (cal[ev['entry_idx'].clip(upper=len(cal) - 1)] == ev['entry']).all():
        raise RuntimeError('event entry sessions are not all on the universe calendar (calendar mismatch)')
    ev['exit_idx'] = np.minimum(ev['entry_idx'] + tm.HOLD_PRIMARY, len(cal) - 1)
    ev = ev[(ev['entry'] >= CFG['locks']['entry_first']) & (ev['entry'] <= CFG['locks']['entry_last'])].copy()
    # eligibility at the last month-end signal date STRICTLY BEFORE the entry session: a signal date's features use that
    # day's close, which is not known at that day's open (causal reading of section 7; same as Phase 8)
    sig = U['sig']; sidx = sig.searchsorted(ev['entry'].to_numpy(), side='left') - 1
    ev = ev[sidx >= 0].copy(); sidx = sidx[sidx >= 0]; ev['sig_date'] = sig[sidx]
    el, rk, pit = U['elig'], U['rank'], U['pit']
    ev['eligible'] = [bool(el.at[t, c]) if c in el.columns and t in el.index else False for t, c in zip(ev['sig_date'], ev['code'])]
    ev['rank'] = [float(rk.at[t, c]) if c in rk.columns and t in rk.index else np.nan for t, c in zip(ev['sig_date'], ev['code'])]
    ev['pit'] = [bool(pit.at[t, c]) if c in pit.columns and t in pit.index else False for t, c in zip(ev['sig_date'], ev['code'])]
    counts = dict(events_all=int(len(ev)), eligible=int(ev['eligible'].sum()), pit=int(ev['pit'].sum()), by_year={int(y): int(len(g)) for y, g in ev[ev['eligible']].groupby(ev['entry'].dt.year)},
                  by_label=ev[ev['eligible']]['pred'].value_counts().to_dict())
    ev = ev[ev['eligible']].copy(); print('events', counts, flush=True)
    ao, _, spy_ao, _ = p8.daily_benchmarks(U); ao_np = ao.to_numpy(dtype=float); spy_ao_np = spy_ao.to_numpy(dtype=float)
    ended_info = p8.ended_map(U); venue = su.load_last_venue(); factors = load_factors()
    # ---- event study first
    study = dict(primary=event_study(ev, U, ao, ao_np, spy_ao_np, ended_info, venue))
    for name, m in (('A_only', ev['pred'] == 'A'), ('B_only', ev['pred'] == 'B'), ('pit_sp1500', ev['pit'])):
        sub = ev[m]
        study[name] = event_study(sub, U, ao, ao_np, spy_ao_np, ended_info, venue) if len(sub) >= 30 else dict(n=int(len(sub)))
    # ---- benchmarks (monthly)
    haircut = lambda info, v: su.delisting_haircut(info, v, 'base')
    b = se.equal_weight_benchmark(U['elig'], U['ret'], ended=U['ended'], venue=venue, haircut=haircut)
    bench_m = b['net'][b['n_held'] > 0]; bench_m.index = (pd.DatetimeIndex(bench_m.index).to_period('M') + 1).to_timestamp('M')
    _, etf_ret, _ = run.etf_monthly(run.load_etf_frames(), ['SPY'], U['sig'], U['ex'])
    spy_m = etf_ret['SPY'].copy(); spy_m.index = (pd.DatetimeIndex(U['sig'][:len(spy_m)]).to_period('M') + 1).to_timestamp('M')
    # ---- portfolios
    results, rows, monthly_out = {}, [], {}
    variants = [('primary', dict(cost_case='MANUAL_USD')), ('automated', dict(cost_case='AUTOMATED')), ('stress', dict(cost_case='STRESS')),
                ('delay1', dict(cost_case='MANUAL_USD', delay=1)), ('all100', dict(cost_case='MANUAL_USD', haircut_mode='all100')), ('all30', dict(cost_case='MANUAL_USD', haircut_mode='all30'))]
    subsets = {'AB': ev, 'A_only': ev[ev['pred'] == 'A'], 'B_only': ev[ev['pred'] == 'B'], 'pit_sp1500': ev[ev['pit']]}
    for sname, sel in subsets.items():
        if len(sel) < 30:
            continue
        results[sname] = dict(n_events=int(len(sel)), n_2013=int((sel['entry'].dt.year >= 2013).sum()))
        for vname, kw in variants:
            if sname != 'AB' and vname != 'primary':
                continue
            sim = pf.simulate_hold_all(sel, ao, cal, ended_info, venue, **kw)
            m = pf.monthly_from_equity(sim['equity'], cal); ws = window_stats(m, bench_m, spy_m, factors)
            results[sname][vname] = dict(windows=ws, turnover=sim['turnover'], counters=sim['counters'], cost_paid=sim['cost_paid'])
            if vname == 'primary':
                results[sname]['trades'] = sim['trades']; monthly_out[sname] = m
            for w, v in ws.items():
                rows.append(dict(subset=sname, variant=vname, window=w, **{k: vv for k, vv in v.items() if k not in ('yearly_excess', 'ff3_betas', 'ff6_betas')}, turnover=sim['turnover']['oneway_total']))
    # 126-session secondary (AB, primary costs)
    sel = ev.copy(); sel['exit_idx'] = np.minimum(sel['entry_idx'] + tm.HOLD_SECONDARY, len(cal) - 1)
    sim = pf.simulate_hold_all(sel, ao, cal, ended_info, venue, cost_case='MANUAL_USD'); m126 = pf.monthly_from_equity(sim['equity'], cal)
    results['AB']['h126'] = dict(windows=window_stats(m126, bench_m, spy_m, factors), turnover=sim['turnover'])
    # operational 20-slot sensitivity (Phase 8 engine)
    slot = p8.simulate_slots(ev.assign(value=1.0), ao, cal, ended_info, venue, horizon=tm.HOLD_PRIMARY, slots=20, cost_case='MANUAL_USD')
    results['AB']['slots20'] = dict(windows=window_stats(p8.monthly_from_equity(slot['equity'], cal), bench_m, spy_m, factors), skipped_full=slot['skipped_full'])
    # ---- gates and multiplicity (one primary hypothesis)
    prim = results['AB']['primary']; auto = results['AB']['automated']; net = monthly_out['AB']['2013-01-01':'2017-12-31']
    p8_sr = [0.89, 0.6, 0.3, 0.5, 0.7]   # placeholder replaced below by the recorded Phase 8 cell Sharpes if present
    try:
        p8res = json.loads((ROOT / 'reports/E058_20260912T185148/results.json').read_text(encoding='utf8'))
        p8_sr = [p8res['portfolios'][c]['primary|MANUAL_USD']['windows']['w2013_2017']['net_sharpe'] for c in p8res['portfolios']]
    except (OSError, KeyError):
        pass
    srs = p8_sr + [prim['windows']['w2013_2017']['net_sharpe']]
    dsr_prob, sr0 = run.deflated_sharpe(prim['windows']['w2013_2017']['net_sharpe'], len(net), G['G12_n_trials'], float(np.nanvar(srs, ddof=1)), float(sps.skew(net)), float(sps.kurtosis(net, fisher=False)))
    results['AB']['dsr'] = dict(prob=dsr_prob, sr0_annual=sr0, n_trials=G['G12_n_trials'])
    results['AB']['gates'] = gates(prim['windows'], auto['windows'], results['AB']['trades'], ev, study['primary'], results['AB']['n_2013'], results['AB']['n_events'], prim['turnover']['oneway_total'], dsr_prob)
    results['AB']['pass_G1_G12'] = bool(all(results['AB']['gates']['checks'].values()))
    w = prim['windows'].get('w2013_2017', {})
    print(f"AB primary 2013-17: excess {w.get('excess_ann', np.nan)*100:.2f}% t {w.get('excess_t', np.nan):.2f} yrs+ {w.get('years_positive')}/5 | CAGR {w.get('net_cagr', np.nan)*100:.1f} vs EW {w.get('bench_cagr', np.nan)*100:.1f} vs SPY {w.get('spy_cagr', np.nan)*100:.1f} | CAPM a {w.get('capm_alpha_ann', np.nan)*100:.1f}% t {w.get('capm_t', np.nan):.2f} | FF6 a {w.get('ff6_alpha_ann', np.nan)*100:.1f}% t {w.get('ff6_t', np.nan):.2f} | to {prim['turnover']['oneway_total']:.2f} | DSR {dsr_prob:.3f} | fails {[k for k, v in results['AB']['gates']['checks'].items() if not v]}", flush=True)
    # ---- persist
    for sname in results:
        if 'trades' in results[sname]:
            results[sname]['trades'].to_csv(out_dir / f'trades_{sname}.csv', index=False); results[sname] = {k: v for k, v in results[sname].items() if k != 'trades'}
    hashes = (OUT / 'PHASE8B_FREEZE_HASHES.jsonl').read_text(encoding='utf8')
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=dict(experiment='E062', stamp=stamp, counts=counts, freeze_hashes=hashes, code_sha256=hashlib.sha256((ROOT / 'research/phase8b_backtest.py').read_bytes()).hexdigest()),
                                                          event_study=study, portfolios=results), indent=1, default=float), encoding='utf8')
    pd.DataFrame(rows).to_csv(out_dir / 'portfolios.csv', index=False)
    pd.DataFrame(monthly_out).to_csv(out_dir / 'monthly_net.csv'); bench_m.to_csv(out_dir / 'bench_monthly.csv'); spy_m.to_csv(out_dir / 'spy_monthly.csv')
    ev.to_parquet(out_dir / 'events_used.parquet', index=False)
    print(out_dir)


if __name__ == '__main__':
    main()
