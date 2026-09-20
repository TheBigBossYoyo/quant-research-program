"""Build and load the EODHD stock panel for Phase 6 (lock-enforced loader; derived cache is never read directly).

Pipeline
1. `summarize()` - one pass over every gzip CSV in the EOD manifest: rows, first/last date, the maximum
   over history of the 63-day rolling median of approximate dollar volume (adjusted_close x split-adjusted
   volume; the dividend factor makes this a slight under-estimate for old high-yield names, which only
   matters for the coarse pre-screen below), the minimum and maximum unadjusted close, and a flag for
   S&P 500/400/600 history membership. Written to data/derived/phase6/eodhd/summary.parquet.
2. `select_superset()` - mechanical, preregistered pre-screen: keep a ticker if it was ever in the S&P
   1500 constituent history, or if its maximum 63-day median approximate dollar volume >= USD 0.5m
   (the lower bound of the liquidity neighbourhood in PHASE6_UNIVERSE_CONSTRUCTION.md) and it has >= 60
   rows. This is a data-volume decision: a ticker that never reaches half the liquidity floor can never
   enter any eligible set or any benchmark. Nothing about returns is used.
3. `build_panels()` - wide daily panels (DatetimeIndex x ticker) for open and close (unadjusted), adjusted_close
   (split + dividend), volume (split-adjusted), and cumulative split factor from the splits files, as
   float32 parquet under data/derived/phase6/eodhd/panel_<field>.parquet. The cache spans all dates on
   disk (through 2026); it is a cache of raw vendor rows, hashed in the build manifest.
4. `load_panel(field, segment)` - the only read path for research code: reads the cache and returns rows
   through phase6_lock.enforce, so development access stops at 2017-12-31 and locked segments raise.

Usage (from research/):  PYTHONUTF8=1 python phase6_eodhd_panel.py summarize|select|build
"""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import io
import json
import sys

import numpy as np
import pandas as pd

import phase6_eodhd as e
import phase6_eodhd_acquire as acq
from phase6_lock import ROOT, enforce, unlock_status, LockError

DERIVED = ROOT / 'data/derived/phase6/eodhd'
SUMMARY = DERIVED / 'summary.parquet'
SUPERSET = DERIVED / 'superset.json'
BUILD_MANIFEST = DERIVED / 'panel_manifest.json'
FIELDS = ('open', 'close', 'adj_close', 'volume', 'split_factor')
LIQ_WINDOW = 63
PRESCREEN_DOLLAR_VOLUME = 0.5e6
PRESCREEN_MIN_ROWS = 60
PANEL_START = pd.Timestamp('1985-01-01')
PRICE_CAP = 500000.0          # I2: placeholder prices
SPLIT_RATIO_BOUNDS = (1 / 50, 50)   # I1: vendor split errors


def read_eod_csv(path):
    with gzip.open(path, 'rt', encoding='utf8') as fh:
        df = pd.read_csv(fh)
    if df.empty or 'Date' not in df.columns:
        return pd.DataFrame(columns=['open', 'close', 'adj_close', 'volume'], index=pd.DatetimeIndex([], name='date'), dtype=float)
    df = df.rename(columns={'Date': 'date', 'Open': 'open', 'Close': 'close', 'Adjusted_close': 'adj_close', 'Volume': 'volume'})
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).drop_duplicates('date', keep='last').set_index('date').sort_index()
    df = df[['open', 'close', 'adj_close', 'volume']].astype(float)
    # integrity rule (fixed before any result): non-positive prices are vendor errors, treated as missing
    bad = (df['close'] <= 0) | (df['adj_close'] <= 0) | (df['open'] <= 0) | (df['close'] >= PRICE_CAP) | (df['adj_close'] >= PRICE_CAP) | (df['open'] >= PRICE_CAP)
    df.loc[bad, ['open', 'close', 'adj_close']] = np.nan
    return df


def read_splits_csv(path):
    with gzip.open(path, 'rt', encoding='utf8') as fh:
        df = pd.read_csv(fh)
    out = []
    for _, r in df.iterrows():
        try:
            num, den = str(r.iloc[1]).split('/')
            ratio = float(num) / float(den)
        except (ValueError, ZeroDivisionError):
            continue
        if SPLIT_RATIO_BOUNDS[0] <= ratio <= SPLIT_RATIO_BOUNDS[1]:
            out.append((pd.Timestamp(r.iloc[0]), ratio))
    if not out:
        return pd.Series(dtype=float, index=pd.DatetimeIndex([]))
    return pd.Series(dict(out), dtype=float).sort_index()


def constituent_codes():
    codes = set()
    for idx in acq.INDICES:
        comp = json.loads((e.RAW / 'constituents' / f'comp_{idx}.json').read_text(encoding='utf8'))
        codes |= {v['Code'] for v in comp['HistoricalTickerComponents'].values()}
    return codes


def summarize():
    manifest = acq.load_manifest(acq.EOD_MANIFEST)
    targets = {t['code']: t for t in json.loads(acq.TARGETS.read_text(encoding='utf8'))['targets']}
    sp = constituent_codes()
    recs = []
    for i, (code, rec) in enumerate(sorted(manifest.items())):
        t = targets.get(code, {})
        row = dict(code=code, status=rec['status'], rows=rec.get('rows', 0), first=rec.get('first'), last=rec.get('last'),
                   exchange=t.get('exchange'), list_status=t.get('status'), name=t.get('name'), sp1500_history=code in sp,
                   max_med_dv=np.nan, min_close=np.nan, max_close=np.nan, n_zero_volume=0)
        if rec['status'] == 'ok' and rec.get('rows', 0) > 0:
            df = read_eod_csv(ROOT / rec['file'])
            if len(df):
                dv = (df['adj_close'] * df['volume']).rolling(LIQ_WINDOW, min_periods=LIQ_WINDOW).median()
                row.update(max_med_dv=float(dv.max()) if dv.notna().any() else np.nan,
                           min_close=float(df['close'].min()), max_close=float(df['close'].max()),
                           n_zero_volume=int((df['volume'] <= 0).sum()), rows=int(len(df)),
                           first=str(df.index[0].date()), last=str(df.index[-1].date()))
        recs.append(row)
        if i % 5000 == 0:
            print('summarize', i, len(manifest), flush=True)
    out = pd.DataFrame(recs)
    DERIVED.mkdir(parents=True, exist_ok=True)
    out.to_parquet(SUMMARY, index=False)
    return out


def select_superset():
    s = pd.read_parquet(SUMMARY)
    ok = s['status'] == 'ok'
    keep = ok & (s['sp1500_history'] | ((s['max_med_dv'] >= PRESCREEN_DOLLAR_VOLUME) & (s['rows'] >= PRESCREEN_MIN_ROWS)))
    codes = sorted(s.loc[keep, 'code'])
    payload = dict(built_utc=datetime.now(timezone.utc).isoformat(), rule=dict(sp1500_history=True,
                   max_med_dv_ge=PRESCREEN_DOLLAR_VOLUME, min_rows=PRESCREEN_MIN_ROWS, window=LIQ_WINDOW),
                   n_summary=int(len(s)), n_ok=int(ok.sum()), n_keep=len(codes), codes=codes)
    SUPERSET.write_text(json.dumps(payload, indent=0), encoding='utf8')
    return payload


def build_panels():
    codes = json.loads(SUPERSET.read_text(encoding='utf8'))['codes']
    eod = acq.load_manifest(acq.EOD_MANIFEST)
    splits = acq.load_manifest(acq.SPLIT_MANIFEST)
    series = {f: {} for f in FIELDS}
    for i, code in enumerate(codes):
        df = read_eod_csv(ROOT / eod[code]['file'])
        df = df[df.index >= PANEL_START]
        if df.empty:
            continue
        for f in ('open', 'close', 'adj_close', 'volume'):
            series[f][code] = df[f]
        sf = pd.Series(1.0, index=df.index)
        srec = splits.get(code)
        if srec and srec.get('status') == 'ok' and srec.get('rows', 0) > 0:
            sp = read_splits_csv(ROOT / srec['file'])
            sp = sp[sp.index >= df.index[0]]
            if len(sp):
                # cumulative factor such that close / split_factor is split-adjusted to the latest basis;
                # a split on date d applies to all closes strictly before d.
                total = float(np.prod(sp.values))
                cum = pd.Series(total, index=df.index)
                running = 1.0
                for d, ratio in sp.items():
                    cum[df.index >= d] = total / (running * ratio)
                    running *= ratio
                sf = cum
        series['split_factor'][code] = sf
        if i % 1000 == 0:
            print('build', i, len(codes), flush=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    manifest = dict(built_utc=datetime.now(timezone.utc).isoformat(), n_codes=len(codes), fields={})
    for f in FIELDS:
        panel = pd.DataFrame(series[f]).sort_index().astype('float32')
        panel.index.name = 'date'
        path = DERIVED / f'panel_{f}.parquet'
        panel.to_parquet(path)
        manifest['fields'][f] = dict(file=str(path.relative_to(ROOT)).replace('\\', '/'), shape=list(panel.shape),
                                     first=str(panel.index[0].date()), last=str(panel.index[-1].date()),
                                     sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        print('wrote', f, panel.shape, flush=True)
    BUILD_MANIFEST.write_text(json.dumps(manifest, indent=1), encoding='utf8')
    return manifest


def load_panel(field, segment='development', unlock_files=None, columns=None):
    """Lock-enforced read of one wide daily panel. Raises LockError for locked segments."""
    if field not in FIELDS:
        raise KeyError(field)
    status = unlock_status(segment, unlock_files)
    if not status['open']:
        raise LockError(f'{segment} segment is locked: {status["reason"]}')
    panel = pd.read_parquet(DERIVED / f'panel_{field}.parquet', columns=columns)
    panel.index = pd.DatetimeIndex(panel.index)
    return enforce(panel, segment, unlock_files)


def load_summary():
    """Per-ticker descriptive summary (no returns, no dates after the lock are needed by callers)."""
    return pd.read_parquet(SUMMARY)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'summarize':
        s = summarize()
        print(s['status'].value_counts().to_dict(), 'rows>0', int((s['rows'] > 0).sum()))
    elif mode == 'select':
        p = select_superset()
        print({k: v for k, v in p.items() if k != 'codes'})
    elif mode == 'build':
        print(json.dumps(build_panels(), indent=1))
    else:
        print('usage: summarize|select|build')
