"""Phase 9B Stage 0 — low-friction external mechanism screen for analyst-consensus-revision drift.

Executes PHASE9B_STAGE0_PREREGISTRATION.md exactly once. Everything below is frozen by that document;
this file contains no choices that were not written down and hashed first.

Refuses to run unless the preregistration and the source file both still match the SHA256 values
recorded in reports/phase9b/PHASE9B_STAGE0_FREEZE.json.

Date lock: every observation dated 2018-01-01 or later is dropped immediately after the date column is
parsed and before the `ret` column is used for anything, then re-checked by the repository firewall
research/phase6_lock.enforce(..., segment='development'). Our validation (2018-2021) and holdout
(2022-01..2026-08) are never read.

Usage (from research/):
    PYTHONUTF8=1 python phase9b_stage0.py
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm

from phase6_lock import enforce

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / 'reports/phase9b/PHASE9B_STAGE0_FREEZE.json'
PORTS = ROOT / 'data/raw/phase9b/PredictorPortsFull_202510.csv'
PREREG = ROOT / 'PHASE9B_STAGE0_PREREGISTRATION.md'

SIGNALS = ('AnalystRevision', 'REV6')
PRIMARY = 'AnalystRevision'
LONG_PORT = '05'
QUANTILE_PORTS = ('01', '02', '03', '04', '05')
LOCK_END = pd.Timestamp('2018-01-01')

WINDOWS = {
    'EARLY_1990_2004': ('1990-01-01', '2004-12-31'),
    'MODERN_2005_2017': ('2005-01-01', '2017-12-31'),
    'RECENT_2010_2017': ('2010-01-01', '2017-12-31'),
}
DECISION_WINDOW = 'MODERN_2005_2017'
RECENT_WINDOW = 'RECENT_2010_2017'


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def verify_freeze():
    freeze = json.loads(FREEZE.read_text(encoding='utf8'))
    for key, path in (('preregistration_sha256', PREREG), ('source_sha256', PORTS)):
        actual = sha256_file(path)
        if actual != freeze[key]:
            raise RuntimeError(f'{path.name} sha256 {actual} != frozen {freeze[key]}; refusing to run')
    return freeze


def nw_lag(n):
    """Newey-West (1994) automatic bandwidth, frozen in the preregistration: floor(4*(T/100)**(2/9))."""
    return int(np.floor(4.0 * (n / 100.0) ** (2.0 / 9.0)))


def nw_tstat(series):
    y = np.asarray(series, dtype=float)
    n = y.size
    if n < 3:
        return float('nan'), 0
    lag = nw_lag(n)
    fit = sm.OLS(y, np.ones((n, 1))).fit(cov_type='HAC',
                                         cov_kwds={'maxlags': lag, 'use_correction': False})
    return float(fit.tvalues[0]), lag


def describe(series, label):
    y = pd.Series(series).dropna()
    n = int(y.size)
    if n == 0:
        return dict(label=label, n=0)
    mean_m = float(y.mean())
    sd_m = float(y.std(ddof=1))
    ann_mean = 12.0 * mean_m
    ann_vol = np.sqrt(12.0) * sd_m
    t, lag = nw_tstat(y)
    return dict(
        label=label,
        n=n,
        mean_monthly=mean_m,
        ann_mean=ann_mean,
        ann_vol=float(ann_vol),
        sharpe=float(ann_mean / ann_vol) if ann_vol > 0 else float('nan'),
        nw_t=t,
        nw_lag=lag,
        cumulative_return=float((1.0 + y).prod() - 1.0),
    )


def load_ports():
    frame = pd.read_csv(PORTS, usecols=['signalname', 'port', 'date', 'ret', 'Nlong'])
    frame['date'] = pd.to_datetime(frame['date'])

    # LAYER 1 of the date lock: drop everything from 2018-01-01 before `ret` is used at all.
    frame = frame[frame['date'] < LOCK_END].copy()
    if len(frame) and frame['date'].max() >= LOCK_END:
        raise RuntimeError('date lock failed: observations on or after 2018-01-01 survived the filter')

    frame = frame[frame['signalname'].isin(SIGNALS)].copy()
    frame['port'] = frame['port'].astype(str).str.zfill(2)

    # LAYER 2: the repository firewall. Development bound is [1900-01-01, 2018-01-01).
    indexed = frame.set_index('date').sort_index()
    indexed = enforce(indexed, segment='development')
    if len(indexed) and indexed.index.max() >= LOCK_END:
        raise RuntimeError('lock firewall failed')
    return indexed.reset_index()


def build_series(frame, signal):
    sub = frame[frame['signalname'] == signal]
    ls = sub[sub['port'] == 'LS'].set_index('date')['ret'].sort_index()
    long_leg = sub[sub['port'] == LONG_PORT].set_index('date')['ret'].sort_index()

    q = sub[sub['port'].isin(QUANTILE_PORTS)].copy()
    q = q.dropna(subset=['ret', 'Nlong'])
    q = q[q['Nlong'] > 0]
    q['wret'] = q['ret'] * q['Nlong']
    grouped = q.groupby('date')[['wret', 'Nlong']].sum()
    ewcov = (grouped['wret'] / grouped['Nlong']).sort_index()
    ewcov.name = 'EWCOV'
    return ls, long_leg, ewcov


def market_vw():
    """CRSP value-weighted total market return, Mkt-RF + RF, from the Phase 6 French library."""
    import phase6_french
    ff = phase6_french.load('ff3_monthly', block='block0', segment='development')
    mkt = (ff['Mkt-RF'] + ff['RF']).sort_index()
    mkt = mkt[mkt.index < LOCK_END]
    mkt.name = 'MKT_VW'
    return mkt


def window_slice(series, window):
    lo, hi = WINDOWS[window]
    return series[(series.index >= pd.Timestamp(lo)) & (series.index <= pd.Timestamp(hi))]


def main():
    freeze = verify_freeze()
    frame = load_ports()
    mkt = market_vw()

    rows = []
    store = {}
    for signal in SIGNALS:
        ls, long_leg, ewcov = build_series(frame, signal)
        store[signal] = dict(ls=ls, long_leg=long_leg, ewcov=ewcov)
        for window in WINDOWS:
            rec = describe(window_slice(ls, window), f'{signal}|LS|{window}')
            rec.update(signal=signal, series='LS', window=window, benchmark='')
            rows.append(rec)

        for window in (DECISION_WINDOW, RECENT_WINDOW):
            lw = window_slice(long_leg, window)
            rec = describe(lw, f'{signal}|LONG|{window}')
            rec.update(signal=signal, series='LONG', window=window, benchmark='')
            rows.append(rec)

            for bname, bench in (('EWCOV_B1', ewcov), ('MKT_VW_B2', mkt)):
                pair = pd.concat([lw.rename('long'), bench.rename('bench')], axis=1, join='inner')
                rec = describe(pair['bench'], f'{signal}|BENCH_{bname}|{window}')
                rec.update(signal=signal, series=f'BENCH_{bname}', window=window, benchmark=bname)
                rows.append(rec)
                rec = describe(pair['long'] - pair['bench'], f'{signal}|EXCESS_{bname}|{window}')
                rec.update(signal=signal, series=f'EXCESS_{bname}', window=window, benchmark=bname,
                           months_matched=int(len(pair)), months_long_leg=int(len(lw)))
                rows.append(rec)

    results = pd.DataFrame(rows)
    cols = ['signal', 'series', 'window', 'benchmark', 'n', 'mean_monthly', 'ann_mean', 'ann_vol',
            'sharpe', 'nw_t', 'nw_lag', 'cumulative_return', 'months_matched', 'months_long_leg']
    for c in cols:
        if c not in results.columns:
            results[c] = np.nan
    results = results[cols]
    (ROOT / 'PHASE9B_STAGE0_RESULTS.csv').write_text(results.to_csv(index=False), encoding='utf8')

    def get(signal, series, window, field='ann_mean'):
        sel = results[(results['signal'] == signal) & (results['series'] == series)
                      & (results['window'] == window)]
        return float(sel.iloc[0][field]) if len(sel) else float('nan')

    c1 = get(PRIMARY, 'LS', DECISION_WINDOW) > 0
    c2 = get(PRIMARY, 'LS', DECISION_WINDOW, 'nw_t') >= 2.0
    c3 = get(PRIMARY, 'LS', RECENT_WINDOW) > 0
    c4 = get('REV6', 'LS', DECISION_WINDOW) > 0
    c5_modern = get(PRIMARY, 'EXCESS_EWCOV_B1', DECISION_WINDOW) > 0
    c5_recent = get(PRIMARY, 'EXCESS_EWCOV_B1', RECENT_WINDOW) > 0
    c5 = bool(c5_modern and c5_recent)
    long_leg_observable = np.isfinite(get(PRIMARY, 'EXCESS_EWCOV_B1', DECISION_WINDOW))

    if not c1:
        decision = 'REJECT_ANALYST_REVISION_MECHANISM'
    elif not c2:
        decision = 'AMBIGUOUS_ANALYST_REVISION_EVIDENCE'
    elif not long_leg_observable:
        decision = ('MECHANISM_SUPPORTED_LONG_ONLY_RELEVANCE_UNRESOLVED'
                    if (c3 and c4) else 'AMBIGUOUS_ANALYST_REVISION_EVIDENCE')
    elif c3 and c4 and c5:
        decision = 'MECHANISM_SUPPORTED_BUT_PIT_DATA_LICENSE_BLOCKED'
    else:
        decision = 'AMBIGUOUS_ANALYST_REVISION_EVIDENCE'

    b2_modern = get(PRIMARY, 'EXCESS_MKT_VW_B2', DECISION_WINDOW)
    b2_recent = get(PRIMARY, 'EXCESS_MKT_VW_B2', RECENT_WINDOW)
    b1_b2_split = bool(c5 and (b2_modern <= 0 or b2_recent <= 0))

    early = get(PRIMARY, 'LS', 'EARLY_1990_2004')
    modern = get(PRIMARY, 'LS', DECISION_WINDOW)
    ratio = (modern / early) if early > 0 else float('nan')

    out = dict(
        run_utc=datetime.now(timezone.utc).isoformat(),
        preregistration_sha256=freeze['preregistration_sha256'],
        source_sha256=freeze['source_sha256'],
        conditions=dict(c1_primary_ls_modern_positive=bool(c1),
                        c2_primary_ls_modern_nw_t_ge_2=bool(c2),
                        c3_primary_ls_recent_positive=bool(c3),
                        c4_rev6_ls_modern_positive=bool(c4),
                        c5_primary_long_leg_excess_b1_positive_both=c5,
                        c5_modern=bool(c5_modern), c5_recent=bool(c5_recent)),
        long_leg_gate_observable=bool(long_leg_observable),
        decay=dict(early_ann_mean=early, modern_ann_mean=modern, modern_over_early=ratio),
        secondary_b2=dict(excess_modern=b2_modern, excess_recent=b2_recent,
                          beats_b1_but_not_b2=b1_b2_split),
        decision=decision,
        cells_added=0,
        cumulative_ledger=490,
    )
    (ROOT / 'reports/phase9b/PHASE9B_STAGE0_RUN.json').write_text(json.dumps(out, indent=1),
                                                                  encoding='utf8')
    print(json.dumps(out, indent=1))
    print()
    print(results.to_string(index=False))


if __name__ == '__main__':
    main()
