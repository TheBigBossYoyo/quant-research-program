"""Phase 8B retrieval-recall audit (a): XBRL cross-check of the candidate pool (blind to returns; preregistration section 5).

For every issuer with a companyfacts file on disk, the authorised repurchase amount (us-gaap
StockRepurchaseProgramAuthorizedAmount1, USD) and the authorised share count
(StockRepurchaseProgramNumberOfSharesAuthorizedToBeRepurchased, shares) are read through the read-time-locked loader
(facts filed >= 2018-01-01 are never returned). An "authorisation increase" is a filing whose reported authorised
amount exceeds the previous filing's by more than 1 percent. The audit asks whether the candidate pool contains an
8-K of the same CIK filed in the 120 calendar days ending on that 10-Q/10-K filing date. The result is an
approximate recall of the 8-K retrieval for authorisation changes, with two known biases: an issuer need not file an
8-K for an authorisation, and the tag can change for reasons other than a new programme (restatements, tag switches).
Usage (from research/): PYTHONUTF8=1 python phase8b_xbrl_audit.py
"""
from datetime import datetime, timezone
import json
from pathlib import Path

import numpy as np
import pandas as pd

import phase8b_edgar as ed
import phase8b_lock as lk

TAGS = {'usd': ('StockRepurchaseProgramAuthorizedAmount1', 'USD'), 'shares': ('StockRepurchaseProgramNumberOfSharesAuthorizedToBeRepurchased', 'shares')}
WINDOW_DAYS = ed.CONFIG['labels']['retrieval_audit']['xbrl_window_days']
MIN_INCREASE = 0.01


def authorisation_series(facts, tag, unit):
    rows = facts.get('facts', {}).get('us-gaap', {}).get(tag, {}).get('units', {}).get(unit, [])
    if not rows:
        return pd.DataFrame(columns=['filed', 'end', 'val', 'accn'])
    df = pd.DataFrame(rows)[['filed', 'end', 'val', 'accn']]
    df['filed'] = pd.to_datetime(df['filed']); df['end'] = pd.to_datetime(df['end'])
    df = df.sort_values(['filed', 'end']).drop_duplicates('accn', keep='last')
    # one value per filing: the latest period end reported in that filing
    df = df.sort_values(['filed', 'end']).groupby('filed', as_index=False).last()
    return df.sort_values('filed').reset_index(drop=True)


def increases(series, min_increase=MIN_INCREASE):
    """Filings where the authorised amount rose versus the previous filing (first observation is not an increase)."""
    if len(series) < 2:
        return series.iloc[0:0]
    prev = series['val'].shift(1)
    up = (series['val'] > prev * (1 + min_increase)) & prev.notna() & (prev > 0)
    return series[up]


def candidate_dates_by_cik(cand):
    return {int(c): np.sort(g['file_date'].to_numpy(dtype='datetime64[D]')) for c, g in cand.dropna(subset=['cik']).groupby(cand['cik'].astype(float).astype(int))}


def has_candidate(cand_dates, cik, filed, window=WINDOW_DAYS):
    d = cand_dates.get(int(cik))
    if d is None or len(d) == 0:
        return False
    lo = np.datetime64((filed - pd.Timedelta(days=window)).date()); hi = np.datetime64(filed.date())
    return bool(((d >= lo) & (d <= hi)).any())


def run_audit(companyfacts_dir=lk.COMPANYFACTS, candidates=None):
    cand = pd.read_parquet(ed.DERIVED / 'candidates.parquet') if candidates is None else candidates
    lk.guard_dates(cand['file_date'], 'candidates')
    cand_dates = candidate_dates_by_cik(cand)
    rows = []
    files = sorted(Path(companyfacts_dir).glob('CIK*.json.gz'))
    for i, path in enumerate(files):
        cik = int(path.stem[3:13])
        facts = lk.companyfacts_dev(cik, companyfacts_dir)
        if facts is None:
            continue
        for kind, (tag, unit) in TAGS.items():
            s = authorisation_series(facts, tag, unit)
            for _, r in increases(s).iterrows():
                rows.append(dict(cik=cik, kind=kind, filed=r['filed'], val=r['val'], hit=has_candidate(cand_dates, cik, r['filed'])))
        if i % 1000 == 0:
            print('xbrl audit', i, len(files), flush=True)
    df = pd.DataFrame(rows)
    if len(df):
        lk.guard_dates(df['filed'], 'xbrl increases')
        df['year'] = df['filed'].dt.year
    summary = dict(built_utc=datetime.now(timezone.utc).isoformat(), issuers_scanned=len(files), n_increases=int(len(df)),
                   recall_overall=float(df['hit'].mean()) if len(df) else None,
                   recall_by_kind={k: dict(n=int(len(g)), recall=float(g['hit'].mean())) for k, g in df.groupby('kind')} if len(df) else {},
                   recall_by_year={int(y): dict(n=int(len(g)), recall=float(g['hit'].mean())) for y, g in df.groupby('year')} if len(df) else {},
                   window_days=WINDOW_DAYS, min_increase=MIN_INCREASE)
    ed.DERIVED.mkdir(parents=True, exist_ok=True)
    df.to_parquet(ed.DERIVED / 'xbrl_audit_increases.parquet', index=False)
    (ed.DERIVED / 'xbrl_audit_summary.json').write_text(json.dumps(summary, indent=1, default=str), encoding='utf8')
    return df, summary


if __name__ == '__main__':
    _, s = run_audit()
    print(json.dumps(s, indent=1, default=str))
