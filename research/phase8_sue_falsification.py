"""Phase 8 E061: single falsification test of post-earnings-announcement drift on free XBRL data (development only).

SUE = (EPS_q - EPS_{q-4}) / sd of the prior eight seasonal EPS differences, from quarterly diluted EPS facts (10-Q, 80-100
day durations, first disclosure kept) in the SEC companyfacts files acquired for Phase 8; the information date is the
10-Q filing date (later than the 8-K 2.02 release, so the window is conservative post-announcement). Entry at the next
open, 63-session hold. Top SUE decile (by filing month) long-only through the E058 slot engine; top and bottom decile
abnormal returns vs the EW eligible universe. Coverage caveat: companyfacts were acquired only for issuers with insider
purchase events 2009-2017 and mapped through the current SEC ticker file, so the sample is a broad but not complete
subset of the liquid universe. Expected (Martineau 2022): no drift. Usage: PYTHONUTF8=1 python phase8_sue_falsification.py
"""
from datetime import datetime, timezone
import gzip
import json

import numpy as np
import pandas as pd

import phase8_insider_backtest as bt
import phase6_e051_run as run
from phase6_lock import ROOT

CF = ROOT / 'data/raw/phase8/companyfacts'


def eps_series(path):
    with gzip.open(path, 'rt', encoding='utf8') as fh:
        j = json.load(fh)
    src = j.get('facts', {}).get('us-gaap', {}).get('EarningsPerShareDiluted', {}).get('units', {}).get('USD/shares', [])
    df = pd.DataFrame([r for r in src if r.get('form') in ('10-Q', '10-K') and r.get('filed') and r['filed'] <= '2017-12-31' and r.get('start')])
    if df.empty:
        return None
    df['start'] = pd.to_datetime(df['start']); df['end'] = pd.to_datetime(df['end']); df['filed'] = pd.to_datetime(df['filed'])
    dur = (df['end'] - df['start']).dt.days
    q = df[(dur > 80) & (dur < 100)].sort_values('filed').drop_duplicates('end', keep='first').sort_values('end')
    return q[['end', 'val', 'filed']] if len(q) >= 12 else None


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E061_{stamp}'; out_dir.mkdir(parents=True)
    tick = json.load(open(ROOT / 'data/metadata/company_tickers.json', encoding='utf8'))
    cik2sym = {int(v['cik_str']): v['ticker'].upper().replace('.', '-') for v in tick.values()}
    events = []
    files = sorted(CF.glob('CIK*.json.gz'))
    for p in files:
        cik = int(p.stem[3:13])
        sym = cik2sym.get(cik)
        if sym is None:
            continue
        q = eps_series(p)
        if q is None:
            continue
        q = q.reset_index(drop=True)
        # seasonal differences aligned by approximate one-year lag (end date within 350-380 days)
        vals = q['val'].to_numpy(); ends = q['end'].to_numpy(); filed = q['filed'].to_numpy()
        diffs = []
        for i in range(len(q)):
            j = np.where((ends[i] - ends) > np.timedelta64(350, 'D'))[0]
            j = j[(ends[i] - ends[j]) < np.timedelta64(380, 'D')]
            d = vals[i] - vals[j[-1]] if len(j) else np.nan
            diffs.append(d)
            hist = [x for x in diffs[-9:-1] if np.isfinite(x)]
            if np.isfinite(d) and len(hist) >= 6 and np.std(hist, ddof=1) > 0:
                events.append(dict(code=sym, ISSUERCIK=cik, FILING_DATE=pd.Timestamp(filed[i]), sue=float(d / np.std(hist, ddof=1)), value=1.0, owners='', cluster=False, opportunistic=False, officer=False, director_only=False, timely=True, direct=True, later_amended=False))
    ev = pd.DataFrame(events)
    print('issuers with files', len(files), 'SUE events', len(ev), flush=True)
    U = bt.load_universe()
    ev.to_parquet(bt.DERIVED / 'events.parquet' if False else out_dir / 'sue_events_raw.parquet', index=False)
    # reuse prepare_events on a temporary path
    orig = bt.DERIVED / 'events.parquet'; tmp = orig.with_name('events_backup_e061.parquet')
    orig.rename(tmp); ev.to_parquet(orig, index=False)
    try:
        evp = bt.prepare_events(U)
    finally:
        orig.unlink(); tmp.rename(orig)
    evp = evp[evp['eligible']].copy()
    evp['month'] = evp['entry'].dt.to_period('M')
    evp['decile'] = evp.groupby('month')['sue'].transform(lambda x: pd.qcut(x.rank(method='first'), 10, labels=False) if len(x) >= 20 else np.nan)
    ao, _, spy_ao, _ = bt.daily_benchmarks(U); ao_np = ao.to_numpy(dtype=float); spy_np = spy_ao.to_numpy(dtype=float)
    ended_info = bt.ended_map(U); venue = bt.su.load_last_venue(); cal = U['cal']
    study = {}
    for name, mask in (('top_decile', evp['decile'] == 9), ('bottom_decile', evp['decile'] == 0)):
        sel = evp[mask.fillna(False)]
        rs, _ = bt.event_returns(sel, ao, cal, ended_info, venue, 63)
        ewb, _ = bt.bench_bh(sel, ao_np, ao.columns, U['elig'], cal, spy_np, 63)
        m = sel['entry'].dt.to_period('M').astype(str).to_numpy()
        study[name] = dict(all=bt.car_stats(rs - ewb, m), w2013=bt.car_stats((rs - ewb)[sel['entry'].dt.year >= 2013], m[sel['entry'].dt.year >= 2013]), n=int(len(sel)))
        print(name, study[name], flush=True)
    haircut = lambda info, v: bt.su.delisting_haircut(info, v, 'base')
    b = bt.se.equal_weight_benchmark(U['elig'], U['ret'], ended=U['ended'], venue=venue, haircut=haircut)
    bench_m = b['net'][b['n_held'] > 0]; bench_m.index = (pd.DatetimeIndex(bench_m.index).to_period('M') + 1).to_timestamp('M')
    _, etf_ret, _ = run.etf_monthly(run.load_etf_frames(), ['SPY'], U['sig'], U['ex'])
    spy_m = etf_ret['SPY'].copy(); spy_m.index = (pd.DatetimeIndex(U['sig'][:len(spy_m)]).to_period('M') + 1).to_timestamp('M')
    rf = run.load_ff3()['RF']
    top = evp[(evp['decile'] == 9).fillna(False)]
    sim = bt.simulate_slots(top, ao, cal, ended_info, venue, horizon=63, slots=20, cost_case='MANUAL_USD')
    ws = bt.window_stats(bt.monthly_from_equity(sim['equity'], cal), bench_m, spy_m, rf)
    g = bt.gates(ws, ws, sim['trades'], int((top['entry'].dt.year >= 2013).sum()))
    w = ws.get('w2013_2017', {})
    print(f"SUE top-decile portfolio: n {len(top)} | 2013-17 excess vs EW {w.get('excess_ann', np.nan)*100:.2f}% t {w.get('excess_t', np.nan):.2f} | net CAGR {w.get('net_cagr', np.nan)*100:.1f} vs EW {w.get('bench_cagr', np.nan)*100:.1f} vs SPY {w.get('spy_cagr', np.nan)*100:.1f} | alpha t {w.get('alpha_t', np.nan):.2f} | fails {[k for k, v in g['checks'].items() if not v]}", flush=True)
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=dict(experiment='E061', stamp=stamp, issuers_with_files=len(files), sue_events=int(len(ev)), eligible_events=int(len(evp))),
                                                          event_study=study, portfolio=dict(windows=ws, gates=g, n_events=int(len(top)))), indent=1, default=float), encoding='utf8')
    print(out_dir)


if __name__ == '__main__':
    main()
