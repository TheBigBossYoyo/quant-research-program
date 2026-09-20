"""Compare the superseded first replication pass with the supplemented rerun.

Regression logic: assets whose inputs did not change must reproduce every metric exactly;
the four supplemented assets may differ. Writes reports/<rerun>/supplement_delta.json and
appends a section to PHASE4_DATA_SUPPLEMENTATION_AUDIT.md. No strategy evaluation.
"""
import json
import sys

import numpy as np
import pandas as pd

from core import ROOT

FIRST = 'E044_20260909T092223'
SUPPLEMENTED = {'SOLUSDT', 'XRPUSDT', 'FTMUSDT', 'LTCUSDT'}
KEYS = ['asset', 'case', 'component']


def main(rerun: str) -> None:
    a = pd.read_csv(ROOT / 'reports' / FIRST / 'metrics.csv')
    b = pd.read_csv(ROOT / 'reports' / rerun / 'metrics.csv')
    num = [c for c in a.columns if c not in KEYS and pd.api.types.is_numeric_dtype(a[c]) and c in b.columns]
    m = a.merge(b, on=KEYS, suffixes=('_first', '_rerun'))
    if len(m) != len(a) or len(m) != len(b):
        raise ValueError('Row sets differ between runs')
    rows = []
    for _, r in m.iterrows():
        diffs = {}
        for c in num:
            x, y = r[c + '_first'], r[c + '_rerun']
            if pd.isna(x) and pd.isna(y):
                continue
            if pd.isna(x) != pd.isna(y) or not np.isclose(x, y, rtol=0, atol=0):
                diffs[c] = (None if pd.isna(x) else float(x), None if pd.isna(y) else float(y))
        rows.append(dict(asset=r.asset, case=r.case, component=r.component, changed=bool(diffs), diffs=diffs))
    R = pd.DataFrame(rows)
    unaffected_changed = R[(~R.asset.isin(SUPPLEMENTED)) & R.changed]
    if len(unaffected_changed):
        raise RuntimeError('Unaffected assets changed between runs: ' + str(unaffected_changed[KEYS].to_dict('records')[:5]))
    stress = m[(m.case == 'stress') & (m.component == 'equal')]
    table = [dict(asset=r.asset, supplemented=r.asset in SUPPLEMENTED, sharpe_first=float(r.sharpe_first), sharpe_rerun=float(r.sharpe_rerun),
                  return_first=float(r.total_net_return_first), return_rerun=float(r.total_net_return_rerun), max_dd_first=float(r.max_dd_first),
                  max_dd_rerun=float(r.max_dd_rerun), trades_first=int(r.trades_first), trades_rerun=int(r.trades_rerun)) for _, r in stress.iterrows()]
    sign_changes = [t['asset'] for t in table if (t['return_first'] > 0) != (t['return_rerun'] > 0)]
    out = dict(first_pass=FIRST, rerun=rerun, unaffected_assets_identical=True,
               changed_rows=int(R.changed.sum()), changed_assets=sorted(R[R.changed].asset.unique().tolist()), sign_changes=sign_changes, stress_equal=table)
    (ROOT / 'reports' / rerun / 'supplement_delta.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    md = ['', '## First pass versus supplemented rerun (stress case, equal E040)', '',
          f'First pass {FIRST}; rerun {rerun}. All metrics for the ten assets whose inputs did not change are identical to the last digit (regression check). '
          f'Rows changed: {int(R.changed.sum())} across {sorted(R[R.changed].asset.unique().tolist())}. Sign changes in total net return: {sign_changes or "none"}.', '',
          '| Asset | Supplemented | Sharpe first | Sharpe rerun | Net return first | Net return rerun | Max DD first | Max DD rerun | Trades first | Trades rerun |',
          '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for t in table:
        md.append(f"| {t['asset']} | {t['supplemented']} | {t['sharpe_first']:.4f} | {t['sharpe_rerun']:.4f} | {t['return_first']:.4f} | {t['return_rerun']:.4f} | {t['max_dd_first']:.4f} | {t['max_dd_rerun']:.4f} | {t['trades_first']} | {t['trades_rerun']} |")
    with (ROOT / 'PHASE4_DATA_SUPPLEMENTATION_AUDIT.md').open('a', encoding='utf-8') as fh:
        fh.write('\n'.join(md) + '\n')
    print('SUPPLEMENT_DELTA', json.dumps({k: v for k, v in out.items() if k != 'stress_equal'}))
    for t in table:
        print(t)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else (ROOT / 'reports/PHASE4_ACTIVE_REPLICATION.txt').read_text().strip())
