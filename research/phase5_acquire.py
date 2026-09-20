"""ENV009: bounded official-archive acquisition for cohort 2 (hourly klines + markPriceKlines, listing..2024-12).

Reuses phase4_data.one (checksum verification, caching, 2025/2026 firewall). No strategy returns.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import pandas as pd

from core import ROOT
from phase4_data import freeze_check, one


def main():
    freeze_check()
    spec = json.loads((ROOT / 'PHASE5_COHORT2.json').read_text(encoding='utf-8'))
    elig = pd.read_csv(ROOT / 'reports/E046_cohort2/eligibility.csv').set_index('asset')
    jobs = []
    for sym in spec['assets']:
        start = pd.Timestamp(elig.loc[sym, 'start']).strftime('%Y-%m')
        for month in pd.period_range(start, '2024-12', freq='M').astype(str):
            jobs.append((sym, month, 'klines')); jobs.append((sym, month, 'markPriceKlines'))
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'); log = ROOT / 'data/metadata' / f'phase5_acquisition_{stamp}.jsonl'
    missing = []
    with log.open('x') as fh, ThreadPoolExecutor(6) as pool:
        for n, res in enumerate(pool.map(one, jobs), 1):
            fh.write(json.dumps(res) + '\n'); fh.flush()
            if res.get('missing'): missing.append(res)
            if n % 100 == 0: print('ARCHIVES', n, '/', len(jobs), flush=True)
    print('COMPLETE', log, 'missing', len(missing), [(m['symbol'], m['month'], m['kind']) for m in missing][:20], flush=True)


if __name__ == '__main__':
    main()
