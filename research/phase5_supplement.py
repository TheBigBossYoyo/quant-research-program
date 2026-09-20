"""Acquire official daily 1h kline archives for hours missing from monthly archives (Phase 4 supplement rule).

Reads the missing timestamps recorded by the replication integrity output, downloads each affected day's
official daily archive plus its .CHECKSUM into data/raw/phase4/daily_gap_supplements, verifies, and logs.
Merging is done by phase4_run.merge_supplements (absent hours only; conflicts fail). No strategy returns.
"""
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from core import ROOT
from phase4_engine import guard_path

FOLDER = ROOT / 'data/raw/phase4/daily_gap_supplements'


def get(url):
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=(15, 60))
            if r.status_code == 404: return None
            if r.status_code in (418, 429): raise RuntimeError('Rate limited; stop')
            r.raise_for_status(); return r.content
        except (requests.Timeout, requests.ConnectionError):
            if attempt == 2: raise
            time.sleep(1 + attempt)


def main(run_name):
    source = ROOT / 'reports' / run_name; rows = []
    for meta_path in sorted(source.glob('*/data_integrity.json')):
        meta = json.loads(meta_path.read_text()); sym = meta['symbol']; days = sorted({t[:10] for t in meta.get('missing_timestamps', [])})
        for day in days:
            name = f'{sym}-1h-{day}.zip'; guard_path(name); url = f'https://data.binance.vision/data/futures/um/daily/klines/{sym}/1h/{name}'; p = FOLDER / name
            if p.exists() and p.with_name(name + '.CHECKSUM').exists():
                rows.append(dict(symbol=sym, day=day, url=url, cached=True, sha256=hashlib.sha256(p.read_bytes()).hexdigest(), file=str(p.relative_to(ROOT)))); continue
            raw = get(url); check = get(url + '.CHECKSUM')
            if raw is None or check is None:
                rows.append(dict(symbol=sym, day=day, url=url, status='MISSING_ON_SOURCE')); continue
            sha = hashlib.sha256(raw).hexdigest()
            if sha != check.decode().split()[0]: raise ValueError('Checksum ' + url)
            p.write_bytes(raw); p.with_name(name + '.CHECKSUM').write_bytes(check)
            rows.append(dict(symbol=sym, day=day, url=url, retrieved_utc=datetime.now(timezone.utc).isoformat(), status=200, sha256=sha, file=str(p.relative_to(ROOT))))
            print(sym, day, sha[:12], flush=True)
    log = ROOT / 'data/metadata' / f'phase5_daily_gap_supplement_acquisition_{datetime.now(timezone.utc):%Y%m%dT%H%M%S}.json'; log.write_text(json.dumps(rows, indent=2))
    print('SUPPLEMENTS', len(rows), 'missing on source', sum(r.get('status') == 'MISSING_ON_SOURCE' for r in rows), log)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else (ROOT / 'reports/PHASE5_ACTIVE_REPLICATION.txt').read_text().strip())
