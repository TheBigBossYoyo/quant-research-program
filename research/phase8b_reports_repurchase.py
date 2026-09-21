"""Phase 8B artifact recovery: build the named repurchase reports from the ALREADY PERSISTED, immutable run outputs.

This module RECOMPUTES NOTHING. It reads reports/<RUN_ID>/results.json (hash-verified against the freeze ledger) plus
the run's CSV/parquet siblings, and writes the human- and machine-readable Phase 8B deliverables. No prices are
loaded, no portfolio is simulated, no gate is re-evaluated: every number printed is copied from the persisted run.

Usage (from research/): PYTHONUTF8=1 python phase8b_reports_repurchase.py [RUN_ID]
"""
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys

import pandas as pd

from phase6_lock import ROOT

RUN_ID = 'E062_20260920T214738'
SUPERSEDED_RUN = 'E062_SUPERSEDED_DATA_DEFECT_20260920T213315'
OUT = ROOT / 'research/phase8b'
HASH_LOG = OUT / 'PHASE8B_FREEZE_HASHES.jsonl'
CELLS = {'AB': 'NEW+INCREASED combined (PRIMARY, preregistered)',
         'A_only': 'NEW only (preregistered diagnostic)',
         'B_only': 'INCREASED only (preregistered diagnostic)',
         'pit_sp1500': 'PIT S&P 1500 subset (preregistered diagnostic)'}
COST_CASES = {'primary': 'MANUAL_USD 5/5.3 bps (10/10.3 far)',
              'automated': 'AUTOMATED 20/20.3 bps (25/25.3 far)',
              'stress': 'STRESS 30/31 bps (45/46 far)'}
WINDOWS = ['w2013_2017', 'w2004_2012', 'w2004_2017']
PCT = ('net_cagr', 'bench_cagr', 'spy_cagr', 'excess_ann', 'excess_spy_ann', 'capm_alpha_ann', 'ff3_alpha_ann',
       'ff6_alpha_ann', 'max_dd', 'spy_max_dd')


def sha(path):
    p = path if hasattr(path, 'read_bytes') else ROOT / path
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ledger():
    return [json.loads(l) for l in HASH_LOG.read_text(encoding='utf8').splitlines() if l.strip()]


def verify(run_dir):
    """The persisted run must still match the hash recorded for it right after it was produced."""
    recs = {r['file']: r for r in ledger() if 'sha256' in r}
    key = f'reports/{run_dir.name}/results.json'
    if key not in recs:
        raise RuntimeError(f'{key} has no ledger record; the run is not auditably persisted')
    disk = sha(run_dir / 'results.json')
    if disk != recs[key]['sha256']:
        raise RuntimeError(f'{key} changed since it was hashed: ledger {recs[key]["sha256"]} vs disk {disk}')
    return recs[key]


def f(v, k=None, nd=2):
    if v is None or (isinstance(v, float) and v != v):
        return 'n/a'
    if isinstance(v, (int,)) and not isinstance(v, bool):
        return str(v)
    if k in PCT:
        return f'{v * 100:.2f}%'
    return f'{v:.{nd}f}'


def win_row(w, name):
    return dict(window=name, months=w.get('months'), net_cagr=w.get('net_cagr'), bench_cagr=w.get('bench_cagr'),
                spy_cagr=w.get('spy_cagr'), excess_vs_ew=w.get('excess_ann'), excess_t_nw=w.get('excess_t'),
                excess_vs_spy=w.get('excess_spy_ann'), years=w.get('years'), years_positive=w.get('years_positive'),
                capm_alpha_ann=w.get('capm_alpha_ann'), capm_t=w.get('capm_t'), beta=w.get('beta'),
                ff3_alpha_ann=w.get('ff3_alpha_ann'), ff3_t=w.get('ff3_t'),
                ff6_alpha_ann=w.get('ff6_alpha_ann'), ff6_t=w.get('ff6_t'),
                sharpe=w.get('net_sharpe'), spy_sharpe=w.get('spy_sharpe'),
                max_dd=w.get('max_dd'), spy_max_dd=w.get('spy_max_dd'))


def build_portfolio_table(res):
    rows = []
    for cell, desc in CELLS.items():
        c = res['portfolios'].get(cell)
        if not c:
            continue
        for case in COST_CASES:
            blk = c.get(case)
            if not isinstance(blk, dict) or 'windows' not in blk:
                continue
            for wk in WINDOWS:
                w = blk['windows'].get(wk)
                if not w:
                    continue
                rows.append(dict(cell=cell, cell_description=desc, cost_case=case,
                                 cost_description=COST_CASES[case], n_events=c.get('n_events'),
                                 n_events_2013_2017=c.get('n_2013'),
                                 turnover_oneway=blk.get('turnover', {}).get('oneway_total'),
                                 cost_paid_fraction=blk.get('cost_paid'), **win_row(w, wk)))
    return pd.DataFrame(rows)


def build_event_study_table(res):
    rows = []
    for cell in CELLS:
        es = res['event_study'].get(cell if cell != 'AB' else 'primary')
        if not isinstance(es, dict):
            continue
        for h, blk in es.items():
            if not isinstance(blk, dict):
                continue
            for wk, d in blk.items():
                if not isinstance(d, dict) or 'ar_ew_month' not in d:
                    continue
                rows.append(dict(cell=cell, horizon=h, window=wk, n=d.get('n'),
                                 mean_abnormal_return=d['ar_ew_month'].get('mean'),
                                 t_cluster_month=d['ar_ew_month'].get('t'),
                                 t_cluster_cik=d.get('ar_ew_cik', {}).get('t'),
                                 ci_lo=d['ar_ew_month'].get('lo'), ci_hi=d['ar_ew_month'].get('hi')))
    return pd.DataFrame(rows)


def manifest(res, run_dir, rec):
    try:
        commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception:
        commit = 'unavailable'
    frozen = json.loads((OUT / 'PHASE8B_PIPELINE_FROZEN.json').read_text(encoding='utf8'))
    cfg = json.loads((OUT / 'phase8b_config.json').read_text(encoding='utf8'))
    derived = ROOT / 'data/derived/phase8b'
    return dict(
        run_id=run_dir.name, produced_utc=res['meta'].get('stamp'), report_built_utc=datetime.now(timezone.utc).isoformat(),
        recomputed=False, source='reports/%s (immutable; hash-verified against the freeze ledger)' % run_dir.name,
        git_commit=commit,
        results_sha256=rec['sha256'], results_hashed_utc=rec['frozen_utc'],
        code_hashes=frozen['files'], config_sha256=sha('research/phase8b/phase8b_config.json'),
        classifier_sha256=frozen['files']['research/phase8b_classifier.py'], classifier_version='1.8',
        event_list_sha256=sha(derived / 'events.parquet'),
        classified_sha256=sha(derived / 'classified_v18.parquet'),
        filings_table_sha256=sha(derived / 'filings_table.parquet'),
        price_integrity_screen_sha256=sha('research/phase8b_price_integrity.py'),
        gold2_reference_sha256=sha(OUT / 'gold2/phase8b_gold2_reference_FROZEN.csv'),
        gold_v17_reference_sha256=sha(OUT / 'gold/phase8b_gold_reference_FROZEN.csv'),
        development_window=dict(entry_first=cfg['locks']['entry_first'], entry_last=cfg['locks']['entry_last'],
                                gate_window=cfg['gates']['window'], development_end_exclusive='2018-01-01'),
        locked_and_not_accessed=dict(validation='2018-01-01..2021-12-31', holdout='2022-01-01..2026-08-31'),
        frozen_parameters=dict(hold_sessions=252, weighting='equal weight, re-equalised to 1/N on entry/exit sessions only',
                               entry='first open >= 60 min after EDGAR acceptance (08:30 ET cutoff)',
                               universe='Tier 2 LIQ1000 at the last month-end signal date strictly before entry',
                               benchmarks='equal-weight eligible universe (primary) and SPY',
                               costs=COST_CASES, repeat_days=60, positives=['A', 'B'],
                               gates=cfg['gates'], multiplicity=dict(dsr_n_trials=cfg['gates']['G12_n_trials'],
                                                                     note='nine Phase 8 trials + E062')),
        counts=res['meta']['counts'],
        superseded_run=dict(run_id=SUPERSEDED_RUN, reason='price-path data-integrity defect (Amendment 4)',
                            retained=True, numbers_are_not_results=True))


def main(run_id=RUN_ID):
    run_dir = ROOT / 'reports' / run_id
    rec = verify(run_dir)
    res = json.loads((run_dir / 'results.json').read_text(encoding='utf8'))
    pf = build_portfolio_table(res)
    es = build_event_study_table(res)
    pf.to_csv(OUT / 'phase8b_repurchase_portfolios.csv', index=False, encoding='utf8')
    es.to_csv(OUT / 'phase8b_repurchase_event_study.csv', index=False, encoding='utf8')
    man = manifest(res, run_dir, rec)
    (OUT / 'phase8b_repurchase_run_manifest.json').write_text(json.dumps(man, indent=1, default=str), encoding='utf8')
    print(f'portfolios rows {len(pf)}, event-study rows {len(es)}')
    return res, pf, es, man


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else RUN_ID)
