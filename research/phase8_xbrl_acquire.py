"""Phase 8 ENV: SEC companyfacts (XBRL) for issuers with insider-purchase events, for the E060 conditioning layer.

For each issuer CIK in data/derived/phase8/events.parquet (filing date >= 2009) the companyfacts JSON is fetched once
from data.sec.gov (free; declared User-Agent; <= 8 requests per second) and stored gzip-compressed under
data/raw/phase8/companyfacts/CIK##########.json.gz with SHA256 in data/metadata/phase8_xbrl_acquisition_<stamp>.jsonl.
Only the concepts needed by the preregistered rule are later read (OperatingIncomeLoss, Assets, dei
EntityCommonStockSharesOutstanding) with their `filed` dates as timestamps. Files contain facts after 2017; loaders truncate.
Usage (from research/): PYTHONUTF8=1 python phase8_xbrl_acquire.py
"""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
import hashlib
import json
import threading
import time

import pandas as pd
import requests

from phase6_lock import ROOT

RAW = ROOT / 'data/raw/phase8/companyfacts'
META = ROOT / 'data/metadata'
UA = {'User-Agent': os.environ.get('SEC_USER_AGENT', 'Quant research program (set SEC_USER_AGENT to your contact e-mail)'), 'Accept-Encoding': 'gzip, deflate'}
_lock = threading.Lock(); _last = [0.0]
MIN_INTERVAL = 0.13


def throttle():
    with _lock:
        wait = max(0.0, MIN_INTERVAL - (time.monotonic() - _last[0])); _last[0] = time.monotonic() + wait
    if wait:
        time.sleep(wait)


def fetch(cik):
    dest = RAW / f'CIK{int(cik):010d}.json.gz'
    if dest.exists():
        return dict(cik=cik, status='cached', file=dest.relative_to(ROOT).as_posix())
    url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json'
    for attempt in range(3):
        throttle()
        try:
            r = requests.get(url, headers=UA, timeout=60)
        except requests.RequestException:
            time.sleep(2); continue
        if r.status_code == 200:
            body = r.content
            with gzip.open(dest, 'wb') as fh:
                fh.write(body)
            return dict(cik=cik, status='ok', bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), file=dest.relative_to(ROOT).as_posix())
        if r.status_code in (403, 429, 503):
            time.sleep(3 * (attempt + 1)); continue
        return dict(cik=cik, status=f'http{r.status_code}')
    return dict(cik=cik, status='failed')


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    ev = pd.read_parquet(ROOT / 'data/derived/phase8/events.parquet')
    ciks = sorted(set(ev[ev['FILING_DATE'] >= '2009-01-01']['ISSUERCIK'].astype(int)))
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    ok = err = 0
    with ThreadPoolExecutor(max_workers=4) as pool, open(META / f'phase8_xbrl_acquisition_{stamp}.jsonl', 'a', encoding='utf8') as log:
        futs = [pool.submit(fetch, c) for c in ciks]
        for i, f in enumerate(as_completed(futs), 1):
            rec = f.result(); rec['logged_utc'] = datetime.now(timezone.utc).isoformat(); log.write(json.dumps(rec) + '\n')
            ok += rec['status'] in ('ok', 'cached'); err += rec['status'] not in ('ok', 'cached')
            if i % 250 == 0:
                log.flush(); print(i, len(ciks), 'ok', ok, 'err', err, flush=True)
    print('done', len(ciks), 'ok', ok, 'err', err)


if __name__ == '__main__':
    main()
