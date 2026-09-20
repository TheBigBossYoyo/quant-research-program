"""Acquire EODHD raw snapshots for the Phase 6 EODHD screening stage (resumable, hashed, token-safe).

Targets: every US ticker typed "Common Stock" in the active and delisted exchange lists (all venues,
because a failed company's last venue is often PINK/OTC after an exchange delisting; excluding those
venues would reintroduce survivorship bias) plus every code in the S&P 500/400/600 historical
constituent lists. Per ticker one EOD call (full history from 1985-01-01; the stock-level development
window starts 1990 and needs 252 days of warm-up) and, in the `splits` mode, one splits call for
tickers with enough post-1989 rows to matter.

Raw files are gzip-compressed vendor CSV under data/raw/phase6/eodhd/eod and .../splits; nothing is
parsed, filtered or truncated here. The manifest (data/metadata/phase6_eodhd_eod_manifest.jsonl) is
append-only and records SHA256 of the uncompressed body, byte count, row count, first/last date.

Usage (from research/):  PYTHONUTF8=1 python phase6_eodhd_acquire.py targets|eod|splits [--workers 8]
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import argparse
import gzip
import json
import re
import sys
import time
import zlib

import phase6_eodhd as e
from phase6_lock import ROOT

EOD_DIR = e.RAW / 'eod'
SPLIT_DIR = e.RAW / 'splits'
TARGETS = e.META / 'phase6_eodhd_targets.json'
EOD_MANIFEST = e.META / 'phase6_eodhd_eod_manifest.jsonl'
SPLIT_MANIFEST = e.META / 'phase6_eodhd_splits_manifest.jsonl'
PROGRESS = e.META / 'phase6_eodhd_progress.txt'
EOD_FROM = '1985-01-01'
SPLIT_MIN_ROWS_POST_1989 = 252
_SAFE = re.compile(r'^[A-Za-z0-9._\-]+$')
INDICES = ('GSPC', 'MID', 'SML')


def safe_name(code):
    if not _SAFE.match(code) or code in ('.', '..'):
        raise ValueError(f'unsafe code {code!r}')
    return code


def build_targets():
    act = json.loads((e.RAW / 'symbols/active_US.json').read_text(encoding='utf8'))
    dl = json.loads((e.RAW / 'symbols/delisted_US.json').read_text(encoding='utf8'))
    rows = {}
    for status, lst in (('active', act), ('delisted', dl)):
        for x in lst:
            if x.get('Type') == 'Common Stock' and _SAFE.match(x['Code']):
                rows[x['Code']] = dict(code=x['Code'], name=x.get('Name'), exchange=x.get('Exchange'),
                                       status=status, isin=x.get('Isin'), source='symbol_list')
    for idx in INDICES:
        comp = json.loads((e.RAW / 'constituents' / f'comp_{idx}.json').read_text(encoding='utf8'))
        for v in comp['HistoricalTickerComponents'].values():
            c = v['Code']
            if c not in rows and _SAFE.match(c):
                rows[c] = dict(code=c, name=v.get('Name'), exchange=None, status='constituent_only',
                               isin=None, source=f'constituents_{idx}')
    out = dict(built_utc=datetime.now(timezone.utc).isoformat(), n=len(rows), eod_from=EOD_FROM,
               targets=sorted(rows.values(), key=lambda r: r['code']))
    TARGETS.write_text(json.dumps(out, indent=0), encoding='utf8')
    return out


def load_manifest(path):
    """Merge the main manifest with any shard manifests (<stem>_shard<k>of<m>.jsonl); 'ok' records win."""
    done = {}
    files = ([path] if path.exists() else []) + sorted(path.parent.glob(path.stem + '_shard*.jsonl'))
    for f in files:
        for line in f.read_text(encoding='utf8').splitlines():
            if line.strip():
                rec = json.loads(line)
                if rec['code'] not in done or rec['status'] == 'ok':
                    done[rec['code']] = rec
    return done


def in_shard(code, shard):
    if shard is None:
        return True
    k, m = shard
    return zlib.crc32(code.encode('utf8')) % m == k


def csv_stats(text):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) <= 1:
        return 0, None, None
    return len(lines) - 1, lines[1].split(',')[0], lines[-1].split(',')[0]


def fetch_one(client, code, kind):
    name = safe_name(code)
    if kind == 'eod':
        path, params = f'eod/{name}.US', {'from': EOD_FROM, 'period': 'd', 'order': 'a'}
        out = EOD_DIR / f'{name}.csv.gz'
    else:
        path, params = f'splits/{name}.US', {'from': EOD_FROM}
        out = SPLIT_DIR / f'{name}.csv.gz'
    rec = dict(code=code, kind=kind, fetched_utc=datetime.now(timezone.utc).isoformat())
    try:
        text, _ = client.get(path, params=params, fmt='csv', group=kind)
    except e.EodhdError as exc:
        msg = str(exc)
        rec.update(status='error', error=msg[:200])
        return rec
    body = text.encode('utf8')
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out, 'wb') as fh:
        fh.write(body)
    rows, first, last = csv_stats(text)
    rec.update(status='ok', file=str(out.relative_to(ROOT)).replace('\\', '/'), sha256=e.sha256_bytes(body),
               bytes=len(body), rows=rows, first=first, last=last)
    return rec


def run(kind, workers, shard=None):
    targets = json.loads(TARGETS.read_text(encoding='utf8'))['targets']
    manifest_path = EOD_MANIFEST if kind == 'eod' else SPLIT_MANIFEST
    done = load_manifest(manifest_path)
    if shard is not None:
        targets = [t for t in targets if in_shard(t['code'], shard)]
        manifest_path = manifest_path.with_name(f'{manifest_path.stem}_shard{shard[0]}of{shard[1]}.jsonl')
        progress = PROGRESS.with_name(f'{PROGRESS.stem}_shard{shard[0]}of{shard[1]}.txt')
    else:
        progress = PROGRESS
    if kind == 'splits':
        eod = load_manifest(EOD_MANIFEST)
        superset = ROOT / 'data/derived/phase6/eodhd/superset.json'
        keep = set(json.loads(superset.read_text(encoding='utf8'))['codes']) if superset.exists() else None
        todo = [t['code'] for t in targets if t['code'] not in done and eod.get(t['code'], {}).get('status') == 'ok'
                and (keep is None or t['code'] in keep)
                and (eod[t['code']].get('last') or '0000') >= '1990-01-01'
                and eod[t['code']].get('rows', 0) >= SPLIT_MIN_ROWS_POST_1989]
    else:
        todo = [t['code'] for t in targets if done.get(t['code'], {}).get('status') != 'ok']
    client = e.Client()
    started = time.time()
    n_ok = n_err = 0
    with ThreadPoolExecutor(max_workers=workers) as pool, open(manifest_path, 'a', encoding='utf8') as mf:
        futures = {pool.submit(fetch_one, client, code, kind): code for code in todo}
        for i, fut in enumerate(as_completed(futures), 1):
            rec = fut.result()
            mf.write(json.dumps(rec) + '\n')
            if rec['status'] == 'ok':
                n_ok += 1
            else:
                n_err += 1
            if i % 250 == 0 or i == len(todo):
                mf.flush()
                msg = (f'{kind} {i}/{len(todo)} ok={n_ok} err={n_err} calls={client.calls} '
                       f'elapsed={time.time() - started:.0f}s')
                progress.write_text(msg + '\n', encoding='utf8')
                print(msg, flush=True)
    return n_ok, n_err


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['targets', 'eod', 'splits'])
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--shard', default=None, help='k/m: process only codes with crc32 %% m == k')
    a = ap.parse_args()
    shard = tuple(int(x) for x in a.shard.split('/')) if a.shard else None
    if a.mode == 'targets':
        t = build_targets()
        from collections import Counter
        print('targets', t['n'], Counter((r['status'], r['exchange']) for r in t['targets']).most_common(12))
    else:
        print(run(a.mode, a.workers, shard))
