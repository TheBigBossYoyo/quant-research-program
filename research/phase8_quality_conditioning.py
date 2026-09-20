"""Phase 8 E060: quality conditioning of the insider-purchase events with point-in-time XBRL facts (two preregistered cells).

Q1 PROFITABLE: the issuer's latest operating profitability (OperatingIncomeLoss over the trailing four quarters, or the
annual value, divided by total Assets) from a 10-K/10-Q FILED strictly before the entry date is above the median of the
same measure across all Tier 2 eligible issuers with XBRL facts at that date (median computed monthly, causally).
Q2 NO_ISSUANCE: dei EntityCommonStockSharesOutstanding from the latest filing before entry is not more than 5 percent
above the value reported in a filing about one year earlier (365-455 days before). Both applied to C1 ANY events; the
portfolio and gates are those of E058. Usage (from research/): PYTHONUTF8=1 python phase8_quality_conditioning.py E058_<stamp>
"""
from datetime import datetime, timezone
import gzip
import json
import sys

import numpy as np
import pandas as pd
from scipy import stats as sps

import phase8_insider_backtest as bt
import phase6_e051_run as run
from phase6_lock import ROOT

CF = ROOT / 'data/raw/phase8/companyfacts'
DEV_END = pd.Timestamp('2017-12-31')


def facts_for(cik):
    p = CF / f'CIK{int(cik):010d}.json.gz'
    if not p.exists():
        return None
    with gzip.open(p, 'rt', encoding='utf8') as fh:
        j = json.load(fh)
    out = {}
    gaap = j.get('facts', {}).get('us-gaap', {}); dei = j.get('facts', {}).get('dei', {})
    for key, src, unit in (('op', gaap.get('OperatingIncomeLoss', {}), 'USD'), ('assets', gaap.get('Assets', {}), 'USD'), ('shares', dei.get('EntityCommonStockSharesOutstanding', {}), 'shares')):
        rows = [r for r in src.get('units', {}).get(unit, []) if r.get('filed') and r['filed'] <= '2017-12-31']
        df = pd.DataFrame(rows)
        if df.empty:
            out[key] = df; continue
        df['filed'] = pd.to_datetime(df['filed']); df['end'] = pd.to_datetime(df['end']); df['start'] = pd.to_datetime(df.get('start'), errors='coerce')
        out[key] = df.sort_values('filed')
    return out


def profitability_at(f, date):
    """Operating income over the trailing year (annual 10-K value with a ~365-day duration, or four consecutive quarterly
    values) from filings before `date`, divided by the latest Assets filed before `date`."""
    op = f['op']; assets = f['assets']
    if op.empty or assets.empty:
        return np.nan
    op = op[op['filed'] < date]; assets = assets[assets['filed'] < date]
    if op.empty or assets.empty:
        return np.nan
    dur = (op['end'] - op['start']).dt.days
    annual = op[(dur > 350) & (dur < 380)]
    val = np.nan
    if not annual.empty:
        val = float(annual.iloc[-1]['val'])
        latest_end = annual.iloc[-1]['end']
    else:
        latest_end = None
    quarterly = op[(dur > 80) & (dur < 100)].drop_duplicates('end', keep='last').sort_values('end')
    if len(quarterly) >= 4 and (latest_end is None or quarterly.iloc[-1]['end'] > latest_end):
        val = float(quarterly['val'].iloc[-4:].sum())
    a = float(assets.iloc[-1]['val'])
    return val / a if a and a > 0 and np.isfinite(val) else np.nan


def issuance_at(f, date):
    sh = f['shares']
    if sh.empty:
        return np.nan
    sh = sh[sh['filed'] < date]
    if len(sh) < 2:
        return np.nan
    latest = sh.iloc[-1]
    prior = sh[(latest['filed'] - sh['filed']).dt.days.between(365, 455)]
    if prior.empty:
        return np.nan
    return float(latest['val'] / prior.iloc[-1]['val'] - 1.0)


def main(run_name):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E060_{stamp}'; out_dir.mkdir(parents=True)
    U = bt.load_universe()
    ev = pd.read_parquet(ROOT / 'reports' / run_name / 'events_used.parquet')
    ao, _, spy_ao, _ = bt.daily_benchmarks(U)
    ended_info = bt.ended_map(U); venue = bt.su.load_last_venue()
    cal = U['cal']
    # per-event conditioning variables
    cache = {}
    prof, iss = [], []
    for cik, entry in zip(ev['ISSUERCIK'], ev['entry']):
        if cik not in cache:
            cache[cik] = facts_for(cik)
        f = cache[cik]
        prof.append(profitability_at(f, entry) if f else np.nan); iss.append(issuance_at(f, entry) if f else np.nan)
    ev['op_assets'] = prof; ev['issuance_1y'] = iss
    # monthly cross-sectional median of profitability across eligible issuers with facts (causal, uses only facts filed before the month-end)
    tick = json.load(open(ROOT / 'data/metadata/company_tickers.json', encoding='utf8'))
    sym2cik = {v['ticker'].upper().replace('.', '-'): int(v['cik_str']) for v in tick.values()}
    medians = {}
    for t in U['sig']:
        if t < pd.Timestamp('2008-06-30'):
            continue
        members = [c for c in U['elig'].columns[U['elig'].loc[t].to_numpy()] if c in sym2cik]
        vals = []
        for c in members:
            cik = sym2cik[c]
            if cik not in cache:
                cache[cik] = facts_for(cik)
            f = cache[cik]
            if f:
                v = profitability_at(f, t + pd.Timedelta(days=1))
                if np.isfinite(v):
                    vals.append(v)
        medians[t] = float(np.median(vals)) if len(vals) >= 100 else np.nan
    med = pd.Series(medians)
    ev['median_at_sig'] = ev['sig_date'].map(med)
    ev['Q1_profitable'] = (ev['op_assets'] > ev['median_at_sig'])
    ev['Q2_no_issuance'] = ev['issuance_1y'] <= 0.05
    coverage = dict(events=int(len(ev)), with_profitability=int(ev['op_assets'].notna().sum()), with_issuance=int(ev['issuance_1y'].notna().sum()),
                    q1=int(ev['Q1_profitable'].sum()), q2=int(ev['Q2_no_issuance'].sum()), median_months=int(med.notna().sum()))
    print(coverage, flush=True)
    # benchmarks and portfolios as in E058
    haircut = lambda info, v: bt.su.delisting_haircut(info, v, 'base')
    b = bt.se.equal_weight_benchmark(U['elig'], U['ret'], ended=U['ended'], venue=venue, haircut=haircut)
    bench_m = b['net'][b['n_held'] > 0]; bench_m.index = (pd.DatetimeIndex(bench_m.index).to_period('M') + 1).to_timestamp('M')
    _, etf_ret, _ = run.etf_monthly(run.load_etf_frames(), ['SPY'], U['sig'], U['ex'])
    spy_m = etf_ret['SPY'].copy(); spy_m.index = (pd.DatetimeIndex(U['sig'][:len(spy_m)]).to_period('M') + 1).to_timestamp('M')
    rf = run.load_ff3()['RF']
    results = {}
    for cell, mask in (('Q1_PROFITABLE', ev['Q1_profitable']), ('Q2_NO_ISSUANCE', ev['Q2_no_issuance']), ('Q1Q2_BOTH_diag', ev['Q1_profitable'] & ev['Q2_no_issuance']),
                       ('Q1_UNPROFITABLE_diag', ev['op_assets'].notna() & ~ev['Q1_profitable'])):
        sel = ev[mask.fillna(False)]
        res = dict(n_events=int(len(sel)), n_2013=int((sel['entry'].dt.year >= 2013).sum()))
        for cc in ('MANUAL_USD', 'AUTOMATED'):
            sim = bt.simulate_slots(sel, ao, cal, ended_info, venue, cost_case=cc)
            m = bt.monthly_from_equity(sim['equity'], cal)
            res[cc] = dict(windows=bt.window_stats(m, bench_m, spy_m, rf), n_trades=int(len(sim['trades'])))
            if cc == 'MANUAL_USD':
                res['gates'] = bt.gates(res[cc]['windows'], res[cc]['windows'], sim['trades'], res['n_2013'])
                tr = sim['trades']
        res['gates'] = bt.gates(res['MANUAL_USD']['windows'], res['AUTOMATED']['windows'], tr, res['n_2013'])
        w = res['MANUAL_USD']['windows'].get('w2013_2017', {}); e9 = res['MANUAL_USD']['windows'].get('w2009_2012', {})
        print(f"{cell:22} n {len(sel):5} | 2009-12 {e9.get('excess_ann', np.nan)*100:6.2f}% t {e9.get('excess_t', np.nan):5.2f} | 2013-17 excess {w.get('excess_ann', np.nan)*100:6.2f}% t {w.get('excess_t', np.nan):5.2f} yrs+ {w.get('years_positive', 0)}/5 | net CAGR {w.get('net_cagr', np.nan)*100:5.1f} vs EW {w.get('bench_cagr', np.nan)*100:5.1f} vs SPY {w.get('spy_cagr', np.nan)*100:5.1f} | alpha t {w.get('alpha_t', np.nan):5.2f} | fails {[k for k, v in res['gates']['checks'].items() if not v]}", flush=True)
        results[cell] = res
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=dict(experiment='E060', stamp=stamp, base_run=run_name, coverage=coverage), results=results), indent=1, default=float), encoding='utf8')
    ev.to_parquet(out_dir / 'events_conditioned.parquet', index=False)
    print(out_dir)


if __name__ == '__main__':
    main(sys.argv[1])
