"""Phase 8B pre-gate reports from derived artefacts (no returns): retrieval report, timing audit, event-integrity report,
retrieval-recall audit (XBRL part). Usage (from research/): PYTHONUTF8=1 python phase8b_reports.py
"""
import json
from datetime import datetime, timezone

import pandas as pd

from phase6_lock import ROOT
import phase8b_edgar as ed

OUT = ROOT / 'research/phase8b'
DERIVED = ed.DERIVED


def md_table(df, floatfmt='{:.3f}'):
    cols = list(df.columns)
    lines = ['| ' + ' | '.join(str(c) for c in cols) + ' |', '| ' + ' | '.join('---' for _ in cols) + ' |']
    for _, r in df.iterrows():
        lines.append('| ' + ' | '.join(floatfmt.format(v) if isinstance(v, float) else str(v) for v in r.tolist()) + ' |')
    return '\n'.join(lines)


def retrieval_report():
    counts = pd.read_csv(DERIVED / 'fts_counts.csv')
    summary = json.loads((DERIVED / 'candidates_summary.json').read_text(encoding='utf8'))
    cand = pd.read_parquet(DERIVED / 'candidates.parquet'); comp = pd.read_parquet(DERIVED / 'complement.parquet')
    per_expr = counts.groupby('expression')['total'].sum().sort_values(ascending=False).reset_index().rename(columns={'total': 'document_hits_2004_2017'})
    ceiling = counts[counts['total'] >= ed.CEILING - 500]
    by_year = pd.DataFrame(dict(candidates=cand.groupby('year').size(), auth_language=cand.groupby('year')['auth_match'].sum(), complement=comp.groupby('year').size())).fillna(0).astype(int).reset_index().rename(columns={'index': 'year'})
    expr_cov = pd.Series({e: int(cand['matched'].str.contains(e, regex=False).sum()) for e in ed.TARGET}).sort_values(ascending=False)
    only = {e: int(((cand['matched'] == e)).sum()) for e in ed.TARGET}
    old = set()
    import gzip, glob
    for f in glob.glob(str(ROOT / 'data/raw/phase8/fts/hits_*.json.gz')):
        with gzip.open(f, 'rt', encoding='utf8') as fh:
            old |= {h['id'].split(':')[0] for h in json.load(fh)}
    new_set = set(cand['accession']); old_in_window = {a for a in old}
    text = [f"# PHASE8B_RETRIEVAL_REPORT - Stage 1 candidate retrieval (EDGAR full-text search, 8-K, 2004-01..2017-12), built {datetime.now(timezone.utc).isoformat()}", '',
            'Expressions are the frozen target set T and audit complement B of PHASE8B_PREREGISTRATION.md section 3; every expression was queried separately per calendar month.',
            f"Documents matched per expression (a filing can carry several matching documents):", '', md_table(per_expr), '',
            f"Months at the 10,000-hit ceiling (split automatically): {len(ceiling)}", '',
            f"**Candidates (accessions matched by >= 1 target expression): {summary['candidates']:,}. Complement (audit expressions only): {summary['complement']:,}.**", '',
            'By filing year:', '', md_table(by_year), '',
            'Accessions covered by each target expression (a candidate can match several):', '', md_table(expr_cov.reset_index().rename(columns={'index': 'expression', 0: 'accessions'})), '',
            'Accessions matched by exactly one target expression (marginal contribution):', '', md_table(pd.Series(only).sort_values(ascending=False).reset_index().rename(columns={'index': 'expression', 0: 'accessions_only'})), '',
            f"Comparison with the Phase 8 five-phrase pool (2009-2017, 27,367 accessions): {len(old_in_window & new_set):,} of them are in the new candidate set; {len(old_in_window - new_set):,} are not (they would need the header to confirm the form; the new set is a superset by construction of the expressions).", '',
            f"Forms seen in the search index for candidates: {summary['forms']}", '']
    (OUT / 'PHASE8B_RETRIEVAL_REPORT.md').write_text('\n'.join(text), encoding='utf8')
    return '\n'.join(text)


def timing_and_integrity():
    integ = json.loads((DERIVED / 'filings_integrity.json').read_text(encoding='utf8'))
    df = pd.read_parquet(DERIVED / 'filings_table.parquet')
    f = df[df['fetched']]
    timing = f['timing'].value_counts(dropna=False); cat = f['entry_category'].value_counts(dropna=False)
    hours = pd.to_datetime(f['accept_et']).dt.hour.value_counts().sort_index()
    text = [f"# PHASE8B_TIMING_AUDIT - acceptance times and causal entry sessions for every fetched candidate filing (no returns), built {integ['built_utc']}", '',
            f"Fetched filings: {integ['fetched']:,} of {integ['n']:,} candidates. Acceptance timestamp missing: {integ['acceptance_missing']:,}. Entry session before the header filing date (data error, excluded): {integ['entry_before_filed']:,}. Truncated downloads (> 8 MB): {integ['truncated_downloads']:,}.", '',
            'Acceptance clock (US Eastern):', '', md_table(timing.rename_axis('bucket').reset_index().rename(columns={'count': 'filings'})), '',
            'Entry rule outcome (same-day open only when accepted by 08:30 ET on a session day):', '', md_table(cat.rename_axis('entry_category').reset_index().rename(columns={'count': 'filings'})), '',
            'Acceptance hour histogram:', '', md_table(hours.rename_axis('hour_et').reset_index().rename(columns={'count': 'filings'})), '',
            'Rule: entry = first session open >= 60 minutes after acceptance; exit = open 252 sessions later (126 secondary); truncated at 2017-12-29. Tests: tests/test_phase8b_timing.py (weekend, holiday, Sandy closure, DST, cutoff boundary, delay).', '']
    (OUT / 'PHASE8B_TIMING_AUDIT.md').write_text('\n'.join(text), encoding='utf8')
    routes = pd.Series(integ['map_routes']); byy = pd.Series(integ['map_by_year'])
    text2 = [f"# PHASE8B_EVENT_INTEGRITY - candidate-level integrity before classification (built {integ['built_utc']})", '',
             f"Header forms: {integ['forms']}. Amendments (8-K/A) flagged and excluded from any signal: {integ['amendments']:,}.", '',
             'Ticker mapping routes (point-in-time insider SUBMISSION symbol first, current SEC map last; every code must be priced in the 5 sessions before entry):', '',
             md_table(routes.rename_axis('route').reset_index().rename(columns={0: 'filings'})), '',
             'Share of fetched filings with a priced code, by entry year:', '', md_table(byy.rename_axis('year').reset_index().rename(columns={0: 'mapped_share'})), '',
             'Event rules applied after classification (phase8b_events.dedup_events, tested): A/B only; no amendments; one event per issuer per 60 calendar days (later references merged and counted); UNCLASSIFIED never enters; same-issuer active positions open no second position.', '']
    (OUT / 'PHASE8B_EVENT_INTEGRITY.md').write_text('\n'.join(text2), encoding='utf8')
    return '\n'.join(text)


def xbrl_recall_report():
    s = json.loads((DERIVED / 'xbrl_audit_summary.json').read_text(encoding='utf8'))
    byy = pd.DataFrame(s['recall_by_year']).T.reset_index().rename(columns={'index': 'year'}) if s['recall_by_year'] else pd.DataFrame()
    text = [f"# PHASE8B_RETRIEVAL_RECALL_AUDIT - part (a): XBRL cross-check (built {s['built_utc']}; blind to returns)", '',
            f"Issuers scanned: {s['issuers_scanned']:,} (companyfacts on disk, facts filed >= 2018 removed at read time). Authorisation increases detected (amount or share count up > {s['min_increase']:.0%} versus the previous filing): {s['n_increases']:,}.", '',
            f"**Share with a candidate 8-K of the same CIK in the {s['window_days']} calendar days ending on the 10-Q/10-K filing date: {s['recall_overall']:.3f}**" if s['recall_overall'] is not None else 'No increases found.', '',
            f"By kind: {s['recall_by_kind']}", '', 'By year:', '', md_table(byy) if len(byy) else '', '',
            'Interpretation limits (preregistered): an issuer need not file an 8-K for an authorisation (many disclose in the 10-Q itself), and the XBRL tag changes for reasons other than a new programme; this number is a lower bound on 8-K retrieval recall for authorisation changes that were also announced by 8-K, and an upper bound on what an 8-K-only pipeline can see. Part (b), the human-labelled complement sample, is reported in PHASE8B_CLASSIFIER_HOLDOUT.md once labels exist; total system recall = retrieval recall x classifier recall.', '']
    (OUT / 'PHASE8B_RETRIEVAL_RECALL_AUDIT.md').write_text('\n'.join(text), encoding='utf8')
    return '\n'.join(text)


if __name__ == '__main__':
    import sys
    which = sys.argv[1:] or ['retrieval', 'timing', 'xbrl']
    if 'retrieval' in which:
        print(retrieval_report()[:1500])
    if 'timing' in which:
        print(timing_and_integrity()[:1500])
    if 'xbrl' in which:
        print(xbrl_recall_report()[:1500])
