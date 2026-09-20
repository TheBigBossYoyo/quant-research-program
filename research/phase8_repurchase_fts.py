"""Phase 8 E059 step 1: EDGAR full-text search scan of 8-K filings for repurchase-authorisation language (feasibility, no returns).

Queries efts.sec.gov month by month (2009-01..2017-12) for 8-K filings matching a fixed phrase set and stores every hit's
metadata (accession, CIK, display name, file date, items) under data/raw/phase8/fts/hits_<YYYY-MM>.json.gz. Hit counts per
month go to data/derived/phase8/fts_counts.json. The phrase set is fixed here before any classification or return.
Usage (from research/): PYTHONUTF8=1 python phase8_repurchase_fts.py
"""
import os
from datetime import datetime, timezone
import gzip
import json
import time

import pandas as pd
import requests

from phase6_lock import ROOT

RAW = ROOT / 'data/raw/phase8/fts'; DERIVED = ROOT / 'data/derived/phase8'
UA = {'User-Agent': os.environ.get('SEC_USER_AGENT', 'Quant research program (set SEC_USER_AGENT to your contact e-mail)')}
QUERY = '"share repurchase program" OR "stock repurchase program" OR "repurchase authorization" OR "buyback program" OR "repurchase of up to"'
PAGE = 100


def month_hits(start, end):
    out = []; frm = 0
    while True:
        params = dict(q=QUERY, forms='8-K', dateRange='custom', startdt=start, enddt=end, **({'from': frm} if frm else {}))
        for attempt in range(3):
            r = requests.get('https://efts.sec.gov/LATEST/search-index', params=params, headers=UA, timeout=60)
            if r.status_code == 200:
                break
            time.sleep(3)
        j = r.json(); hits = j.get('hits', {}).get('hits', [])
        total = j.get('hits', {}).get('total', {}).get('value', 0)
        out += [dict(id=h.get('_id'), **{k: h['_source'].get(k) for k in ('ciks', 'display_names', 'file_date', 'items', 'form', 'file_num', 'period_ending', 'file_description')}) for h in hits]
        frm += PAGE; time.sleep(0.15)
        if not hits or frm >= total or frm >= 10000:
            break
    return total, out


def main():
    RAW.mkdir(parents=True, exist_ok=True); DERIVED.mkdir(parents=True, exist_ok=True)
    counts = {}
    for p in pd.period_range('2009-01', '2017-12', freq='M'):
        start, end = str(p.start_time.date()), str(p.end_time.date())
        total, hits = month_hits(start, end)
        counts[str(p)] = dict(total=int(total), fetched=len(hits))
        with gzip.open(RAW / f'hits_{p}.json.gz', 'wt', encoding='utf8') as fh:
            json.dump(hits, fh)
        print(p, total, len(hits), flush=True)
    json.dump(dict(query=QUERY, built_utc=datetime.now(timezone.utc).isoformat(), counts=counts), open(DERIVED / 'fts_counts.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
