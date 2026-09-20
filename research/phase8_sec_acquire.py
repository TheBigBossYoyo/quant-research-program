"""Phase 8 ENV acquisition of SEC EDGAR structured data sets (free, public domain), hashed, development period only.

Insider Transactions Data Sets (Forms 3/4/5) quarterly ZIPs 2006Q1..2017Q4 are stored under data/raw/phase8/sec_insider.
Nothing from 2018 onward is downloaded until a frozen candidate is authorised for validation (the raw archives would
otherwise sit on disk unread, as the crypto and French archives do; here the cleaner choice is not to fetch them).
Every download is logged with SHA256, byte count and URL in data/metadata/phase8_sec_acquisition_<stamp>.jsonl.
SEC fair-access policy: declared User-Agent, at most 10 requests per second (we use one at a time with a pause).
Usage (from research/): PYTHONUTF8=1 python phase8_sec_acquire.py insider [--start 2006q1 --end 2017q4]
"""
import os
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import time

import requests

from phase6_lock import ROOT

RAW = ROOT / 'data/raw/phase8'
META = ROOT / 'data/metadata'
UA = {'User-Agent': os.environ.get('SEC_USER_AGENT', 'Quant research program (set SEC_USER_AGENT to your contact e-mail)'), 'Accept-Encoding': 'gzip, deflate'}
INSIDER_URL = 'https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{q}_form345.zip'
README_URL = 'https://www.sec.gov/files/insider_transactions_readme.pdf'
DEV_LAST_QUARTER = '2017q4'
PAUSE_S = 0.5


def quarters(start, end):
    y0, q0 = int(start[:4]), int(start[-1]); y1, q1 = int(end[:4]), int(end[-1])
    out = []
    y, q = y0, q0
    while (y, q) <= (y1, q1):
        out.append(f'{y}q{q}')
        q += 1
        if q == 5:
            y, q = y + 1, 1
    return out


def fetch(url, dest, log):
    if dest.exists():
        body = dest.read_bytes()
        log.write(json.dumps(dict(url=url, file=dest.relative_to(ROOT).as_posix(), bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                                  status='cached', logged_utc=datetime.now(timezone.utc).isoformat())) + '\n')
        return 'cached'
    r = requests.get(url, headers=UA, timeout=300)
    rec = dict(url=url, status=r.status_code, logged_utc=datetime.now(timezone.utc).isoformat())
    if r.status_code == 200:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        rec.update(file=dest.relative_to(ROOT).as_posix(), bytes=len(r.content), sha256=hashlib.sha256(r.content).hexdigest())
    log.write(json.dumps(rec) + '\n'); log.flush()
    time.sleep(PAUSE_S)
    return r.status_code


def main(kind, start, end):
    assert end <= DEV_LAST_QUARTER, 'validation/holdout quarters are not acquired without authorisation'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    META.mkdir(parents=True, exist_ok=True)
    with open(META / f'phase8_sec_acquisition_{stamp}.jsonl', 'a', encoding='utf8') as log:
        if kind == 'insider':
            print('readme', fetch(README_URL, RAW / 'sec_insider' / 'insider_transactions_readme.pdf', log))
            for q in quarters(start, end):
                print(q, fetch(INSIDER_URL.format(q=q), RAW / 'sec_insider' / f'{q}_form345.zip', log), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('kind', choices=['insider']); ap.add_argument('--start', default='2006q1'); ap.add_argument('--end', default=DEV_LAST_QUARTER)
    a = ap.parse_args(); main(a.kind, a.start, a.end)
