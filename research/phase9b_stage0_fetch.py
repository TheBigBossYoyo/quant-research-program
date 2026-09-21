"""Phase 9B Stage 0 — acquisition and SCHEMA-ONLY manifest of the OSAP portfolio file.

This module downloads the Open Source Asset Pricing (Chen and Zimmermann) published predictor
portfolio return file and records a structural manifest: sha256, byte size, column names, row count,
the distinct `port` labels available for the two frozen signals, and the min/max date present.

It deliberately emits NO return statistic of any kind — no mean, no sum, no quantile, no sample of
`ret` values. That is the point: the Stage 0 preregistration is written and hashed from this
manifest, so no knowledge of the return observations can influence the frozen design.

Usage (from research/):
    python phase9b_stage0_fetch.py download    # fetch to data/raw/phase9b/ (gitignored)
    python phase9b_stage0_fetch.py manifest    # write the schema-only manifest
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import urllib.request

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/phase9b'
MANIFEST = ROOT / 'reports/phase9b/PHASE9B_STAGE0_SOURCE_MANIFEST.json'

# October 2025 release, linked from https://www.openassetpricing.com/data/ :
# "All 212 predictor portfolio sort csvs in a single file (still following OPs)"
OSAP_FILE_ID = '1g7w-yQ6Cg2qbMEkER9Q3vgns4JszXQo6'
OSAP_URL = f'https://drive.usercontent.google.com/download?id={OSAP_FILE_ID}&export=download&confirm=t'
OSAP_LOCAL = RAW / 'PredictorPortsFull_202510.csv'

SIGNALS = ('AnalystRevision', 'REV6')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def download():
    RAW.mkdir(parents=True, exist_ok=True)
    tmp = OSAP_LOCAL.with_suffix('.part')
    req = urllib.request.Request(OSAP_URL, headers={'User-Agent': 'phase9b-stage0/1.0'})
    with urllib.request.urlopen(req, timeout=600) as resp, open(tmp, 'wb') as out:
        total = 0
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
            total += len(chunk)
    tmp.replace(OSAP_LOCAL)
    print(json.dumps(dict(path=str(OSAP_LOCAL.relative_to(ROOT)), bytes=total,
                          sha256=sha256_file(OSAP_LOCAL))))


def manifest():
    """Structural description only. No return value is read, printed or aggregated."""
    head = pd.read_csv(OSAP_LOCAL, nrows=5)
    cols = list(head.columns)
    usecols = [c for c in cols if c in ('signalname', 'port', 'date')]
    frame = pd.read_csv(OSAP_LOCAL, usecols=usecols)
    frame['date'] = pd.to_datetime(frame['date'])

    per_signal = {}
    for sig in SIGNALS:
        sub = frame[frame['signalname'] == sig]
        ports = sorted(sub['port'].astype(str).unique())
        counts = {p: int((sub['port'].astype(str) == p).sum()) for p in ports}
        per_signal[sig] = dict(
            present=bool(len(sub)),
            rows=int(len(sub)),
            ports=ports,
            rows_per_port=counts,
            date_min=str(sub['date'].min().date()) if len(sub) else None,
            date_max=str(sub['date'].max().date()) if len(sub) else None,
            rows_before_2018=int((sub['date'] < pd.Timestamp('2018-01-01')).sum()),
        )

    out = dict(
        retrieved_utc=datetime.now(timezone.utc).isoformat(),
        source='Open Source Asset Pricing (Chen and Zimmermann), October 2025 release',
        source_page='https://www.openassetpricing.com/data/',
        url=OSAP_URL,
        local_path=str(OSAP_LOCAL.relative_to(ROOT)),
        bytes=OSAP_LOCAL.stat().st_size,
        sha256=sha256_file(OSAP_LOCAL),
        columns=cols,
        total_rows=int(len(frame)),
        distinct_signals=int(frame['signalname'].nunique()),
        signals=per_signal,
        note='Schema-only manifest. No return observation was read, printed or aggregated to produce '
             'this file; only signalname, port and date columns were loaded.',
    )
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(out, indent=1), encoding='utf8')
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'manifest'
    if mode == 'download':
        download()
    elif mode == 'manifest':
        manifest()
    else:
        raise SystemExit(f'unknown mode {mode!r}')
