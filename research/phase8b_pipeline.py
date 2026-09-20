"""Phase 8B Amendment 3: build the frozen event list from the frozen v1.8 classifier. No returns are computed here.

Runs only after the 'classifier gate passed' record exists AND every file in PHASE8B_PIPELINE_FROZEN.json still
matches its frozen hash. This module is plumbing: it applies the already-frozen classifier to the full candidate pool
and hands `dedup_events` the predictions. It contains no classification logic and no threshold.

  classify -> data/derived/phase8b/classified_v18.parquet (both passes over every corpus row; v1.7 output preserved)
  events   -> data/derived/phase8b/filings_table.parquet + events.parquet + phase8b_events_integrity.json

Usage (from research/): PYTHONUTF8=1 python phase8b_pipeline.py classify|events|all
"""
from datetime import datetime, timezone
import hashlib
import json
import sys

import pandas as pd

from phase6_lock import ROOT
import phase8b_classifier as clf
import phase8b_corpus as cp
import phase8b_edgar as ed
import phase8b_events as evs
import phase8b_lock as lk
import phase8b_price_integrity as pi

OUT = ROOT / 'research/phase8b'
DERIVED = ed.DERIVED
FROZEN = OUT / 'PHASE8B_PIPELINE_FROZEN.json'
HASH_LOG = OUT / 'PHASE8B_FREEZE_HASHES.jsonl'


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def require_frozen():
    """Refuse to run unless the gate was recorded and the whole pipeline still matches its permanent freeze."""
    log = HASH_LOG.read_text(encoding='utf8')
    if 'classifier gate passed' not in log:
        raise RuntimeError('pipeline refused: no "classifier gate passed" record')
    spec = json.loads(FROZEN.read_text(encoding='utf8'))
    drift = {f: (h, sha(f)) for f, h in spec['files'].items() if sha(f) != h}
    if drift:
        raise RuntimeError(f'pipeline refused: frozen files changed since the freeze: {sorted(drift)}')
    return spec


def log(rec):
    rec.setdefault('frozen_utc', datetime.now(timezone.utc).isoformat())
    with open(HASH_LOG, 'a', encoding='utf8') as fh:
        fh.write(json.dumps(rec) + '\n')


def classify():
    require_frozen()
    df = cp.load()
    lk.guard_dates(pd.to_datetime(df['filed'], format='%Y%m%d'), 'corpus filed dates')
    out = clf.classify_frame(df)
    out['classifier_version'] = clf.VERSION
    out['classifier_sha'] = sha('research/phase8b_classifier.py')
    path = DERIVED / 'classified_v18.parquet'
    out.to_parquet(path, index=False)
    rep = dict(built_utc=datetime.now(timezone.utc).isoformat(), classifier_version=clf.VERSION,
               n_rows=int(len(out)), n_8k=int((out['form'] == '8-K').sum()),
               p1_labels=out['p1_label'].value_counts().to_dict(),
               p1_positives=int(out['p1_primary'].sum()),
               p1_positives_by_year=out[out['p1_primary']].groupby('year').size().to_dict(),
               p2_positives=int(out['p2_primary'].sum()),
               p2_rejects_share_of_p1_positives=float(1 - out[out['p1_primary']]['p2_primary'].mean()))
    (OUT / 'phase8b_classified_v18_summary.json').write_text(json.dumps(rep, indent=1, default=str), encoding='utf8')
    print(json.dumps(rep, indent=1, default=str))
    return out


def events():
    require_frozen()
    cls = pd.read_parquet(DERIVED / 'classified_v18.parquet')
    if set(cls['classifier_sha']) != {sha('research/phase8b_classifier.py')}:
        raise RuntimeError('events refused: classified_v18.parquet was built with a different classifier')
    table_path = DERIVED / 'filings_table.parquet'
    if table_path.exists():
        filings = pd.read_parquet(table_path)
        print(f'filing table reused ({len(filings)} rows)')
    else:
        filings, integ = evs.build_filing_table()
        print(json.dumps(integ, indent=1, default=str))
    pred = cls.set_index('accession')['p1_label']
    filings = filings.copy()
    filings['pred'] = filings['accession'].map(pred)
    unscored = int(filings['pred'].isna().sum())
    filings['pred'] = filings['pred'].fillna('UNSCORED')
    ev, counts = evs.dedup_events(filings, label_col='pred', positives=('A', 'B'))
    # Amendment 4: drop events whose traded price path is corrupt inside the holding window (Phase 6 I3 thresholds)
    import phase8b_backtest as bt
    U = bt.p8.load_universe(); ao, _, _, _ = bt.p8.daily_benchmarks(U); cal = U['cal']
    ev = ev.assign(entry_idx=cal.searchsorted(ev['entry'].to_numpy()))
    ev['exit_idx'] = (ev['entry_idx'] + 252).clip(upper=len(cal) - 1)
    ev, pi_report, dropped = pi.screen_events(ev, ao, cal)
    counts['price_integrity_dropped'] = pi_report['events_dropped']
    (OUT / 'phase8b_price_integrity.json').write_text(json.dumps(pi_report, indent=1, default=str), encoding='utf8')
    if len(dropped):
        dropped.to_csv(OUT / 'phase8b_price_integrity_dropped.csv', index=False, encoding='utf8')
    print(json.dumps(pi_report, indent=1, default=str))
    ev.to_parquet(DERIVED / 'events.parquet', index=False)
    integrity = dict(built_utc=datetime.now(timezone.utc).isoformat(), classifier_version=clf.VERSION,
                     classifier_sha256=sha('research/phase8b_classifier.py'),
                     filings_rows=int(len(filings)), filings_without_a_prediction=unscored,
                     counts=counts, events=int(len(ev)), price_integrity=pi_report,
                     events_by_year=ev.groupby(ev['entry'].dt.year).size().to_dict(),
                     events_2013_2017=int(((ev['entry'].dt.year >= 2013) & (ev['entry'].dt.year <= 2017)).sum()),
                     entry_min=str(ev['entry'].min()), entry_max=str(ev['entry'].max()),
                     unique_issuers=int(ev['cik'].nunique()),
                     label_mix=ev['pred'].value_counts().to_dict())
    (OUT / 'phase8b_events_integrity.json').write_text(json.dumps(integrity, indent=1, default=str), encoding='utf8')
    for name, p in (('events', DERIVED / 'events.parquet'), ('filings table', table_path),
                    ('classified', DERIVED / 'classified_v18.parquet')):
        log(dict(file=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                 stage=f'FINAL Phase 8B {name} from the permanently frozen v1.8 pipeline (no return computed yet)'))
    log(dict(file='research/phase8b/phase8b_events_integrity.json',
             sha256=hashlib.sha256((OUT / 'phase8b_events_integrity.json').read_bytes()).hexdigest(),
             stage='FINAL Phase 8B event-list integrity report'))
    print(json.dumps(integrity, indent=1, default=str))
    return ev, integrity


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'all':
        classify(); events()
    else:
        {'classify': classify, 'events': events}.get(mode, lambda: print('usage: classify|events|all'))()
