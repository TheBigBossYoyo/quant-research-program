"""Phase 8B filing table, point-in-time ticker mapping, causal schedule and event integrity (frozen rules, sections 4, 6, 7).

`build_filing_table()` reads every stored candidate filing, parses the header, computes the entry/exit sessions from the
acceptance time (phase8b_timing), maps the issuer CIK to an EODHD code point-in-time (insider SUBMISSION symbols, then
the current SEC map), checks that the code is priced in the 5 sessions before entry and records integrity flags. No
return is computed here. `dedup_events()` turns classifier-labelled filings into events: A/B only, no amendments, one
event per issuer per 60 calendar days (later references merged and counted).
"""
from datetime import datetime, timezone
import io
import json
import zipfile

import numpy as np
import pandas as pd

from phase6_lock import ROOT
import phase6_e051_run as run
import phase8_insider_events as p8
import phase8b_edgar as ed
import phase8b_lock as lk
import phase8b_timing as tm

DERIVED = ed.DERIVED
INSIDER = ROOT / 'data/raw/phase8/sec_insider'
CFG = ed.CONFIG
MAP_WINDOW_DAYS = 400
PRICE_CHECK_SESSIONS = CFG['universe']['price_check_sessions_before_entry']
VARIANTS = CFG['universe']['code_variants']
REPEAT_DAYS = CFG['events']['repeat_reference_days']


# ---------------------------------------------------------------- point-in-time CIK -> symbol
def load_submission_symbols(cache=DERIVED / 'cik_symbols.parquet'):
    """(cik, symbol, filing_date) triples from the insider SUBMISSION tables 2006Q1..2017Q4 (cached)."""
    if cache.exists():
        return pd.read_parquet(cache)
    parts = []
    for q in p8.QUARTERS:
        z = zipfile.ZipFile(INSIDER / f'{q}_form345.zip')
        s = pd.read_csv(io.BytesIO(z.read('SUBMISSION.tsv')), sep='\t', dtype=str, encoding='latin1', quoting=3, on_bad_lines='skip', usecols=['ISSUERCIK', 'ISSUERTRADINGSYMBOL', 'FILING_DATE'])
        s['sym'] = s['ISSUERTRADINGSYMBOL'].map(p8.norm_symbol); s = s[s['sym'].notna()]
        s['date'] = pd.to_datetime(s['FILING_DATE'], format='%d-%b-%Y', errors='coerce'); s['cik'] = pd.to_numeric(s['ISSUERCIK'], errors='coerce')
        parts.append(s.dropna(subset=['date', 'cik'])[['cik', 'sym', 'date']].drop_duplicates())
    out = pd.concat(parts, ignore_index=True); out['cik'] = out['cik'].astype(int)
    out = out.sort_values(['cik', 'date']).reset_index(drop=True)
    lk.guard_dates(out['date'], 'submission symbols')
    cache.parent.mkdir(parents=True, exist_ok=True); out.to_parquet(cache, index=False)
    return out


def pit_symbols(cik, date, symtab):
    """Candidate symbols in priority order with their route: latest prior within 400 days, else earliest later within 400 days."""
    s = symtab[symtab['cik'] == cik]
    if s.empty:
        return []
    prior = s[(s['date'] <= date) & (s['date'] >= date - pd.Timedelta(days=MAP_WINDOW_DAYS))]
    if len(prior):
        syms = list(dict.fromkeys(prior.sort_values('date', ascending=False)['sym']))
        return [(x, 'insider_submission_prior_400d') for x in syms[:2]]
    later = s[(s['date'] > date) & (s['date'] <= date + pd.Timedelta(days=MAP_WINDOW_DAYS))]
    if len(later):
        syms = list(dict.fromkeys(later.sort_values('date')['sym']))
        return [(x, 'insider_submission_backfill_400d') for x in syms[:2]]
    return []


def current_symbol(cik, current_map):
    return current_map.get(int(cik))


def load_current_map():
    tick = json.load(open(ROOT / 'data/metadata/company_tickers.json', encoding='utf8'))
    return {int(v['cik_str']): v['ticker'].upper().replace('.', '-') for v in tick.values()}


def priced(code, close, sessions, entry_idx):
    """True when `code` has a finite unadjusted close in the PRICE_CHECK_SESSIONS sessions before the entry session."""
    if code not in close.columns or entry_idx <= 0:
        return False
    lo = max(0, entry_idx - PRICE_CHECK_SESSIONS)
    seg = close[code].to_numpy(dtype=float)[lo:entry_idx]
    return bool(np.isfinite(seg).any())


def map_code(cik, accept_date, entry_idx, symtab, current_map, close, sessions):
    """Return (code, route) or (None, 'unmapped'); routes per phase8b_config.json universe.mapping_routes."""
    cands = pit_symbols(cik, accept_date, symtab)
    cur = current_symbol(cik, current_map)
    if cur:
        cands.append((cur, 'company_tickers_current'))
    for sym, route in cands:
        for v in VARIANTS:
            code = sym + v
            if priced(code, close, sessions, entry_idx):
                return code, route
    return None, 'unmapped'


# ---------------------------------------------------------------- filing table
def spy_sessions():
    frames = run.load_etf_frames()
    spy = frames['SPY']
    return tm.sessions_from_open(spy['open'])


def build_filing_table(accessions=None, hold=tm.HOLD_PRIMARY):
    """One row per stored candidate filing with header fields, schedule, mapping and integrity flags (no returns)."""
    cand = pd.read_parquet(DERIVED / 'candidates.parquet')
    if accessions is not None:
        cand = cand[cand['accession'].isin(accessions)]
    sessions = spy_sessions()
    close = lk.load_panel('close')
    close = close.reindex(sessions)
    symtab = load_submission_symbols(); current_map = load_current_map()
    rows = []
    for i, r in enumerate(cand.itertuples(index=False)):
        f = ed.load_filing(r.accession)
        if f is None:
            rows.append(dict(accession=r.accession, fetched=False)); continue
        h = f['header']
        row = dict(accession=r.accession, fetched=True, cik=int(h['cik']) if h.get('cik') else (int(r.cik) if r.cik else None), company=h.get('company'), form=h.get('form'),
                   filed=h.get('filed'), acceptance=h.get('acceptance'), items='|'.join(h.get('items') or []), sic=h.get('sic_code'), n_docs=len(f['documents']),
                   chars=sum(d['chars'] for d in f['documents']), truncated=f.get('truncated', False), auth_match=bool(r.auth_match), matched=r.matched,
                   is_amendment=(h.get('form') or '').endswith('/A'), acceptance_missing=not h.get('acceptance'))
        if h.get('filed'):
            lk.guard_filed_date(h['filed'])
        if h.get('acceptance'):
            acc = tm.parse_acceptance(h['acceptance'])
            e, cat = tm.entry_session(acc, sessions)
            row.update(accept_et=acc.replace(tzinfo=None), timing=tm.timing_category(acc), entry_category=cat, entry=e)
            if e is not None:
                x, trunc = tm.exit_session(e, sessions, hold)
                row.update(exit=x, exit_truncated=trunc, entry_idx=int(sessions.get_loc(e)), exit_idx=int(sessions.get_loc(x)))
                row['entry_before_filed'] = bool(h.get('filed') and e < tm.parse_filed(h['filed']))
                code, route = map_code(row['cik'], pd.Timestamp(acc.date()), row['entry_idx'], symtab, current_map, close, sessions) if row['cik'] else (None, 'no_cik')
                row.update(code=code, map_route=route)
        rows.append(row)
        if i % 5000 == 0:
            print('filing table', i, len(cand), flush=True)
    df = pd.DataFrame(rows)
    for c in ('entry', 'exit', 'accept_et'):
        if c in df.columns:
            lk.guard_dates(df[c].dropna(), f'filing table {c}')
    df.to_parquet(DERIVED / 'filings_table.parquet', index=False)
    integrity = dict(built_utc=datetime.now(timezone.utc).isoformat(), n=int(len(df)), fetched=int(df['fetched'].sum()),
                     forms=df['form'].value_counts(dropna=False).to_dict(), amendments=int(df['is_amendment'].fillna(False).sum()),
                     acceptance_missing=int(df['acceptance_missing'].fillna(True).sum()), entry_before_filed=int(df.get('entry_before_filed', pd.Series(dtype=bool)).fillna(False).sum()),
                     timing=df['timing'].value_counts(dropna=False).to_dict() if 'timing' in df else {}, entry_category=df['entry_category'].value_counts(dropna=False).to_dict() if 'entry_category' in df else {},
                     map_routes=df['map_route'].value_counts(dropna=False).to_dict() if 'map_route' in df else {},
                     map_by_year={int(y): float(g['code'].notna().mean()) for y, g in df.dropna(subset=['entry']).groupby(df['entry'].dt.year)} if 'entry' in df else {},
                     truncated_downloads=int(df['truncated'].fillna(False).sum()))
    (DERIVED / 'filings_integrity.json').write_text(json.dumps(integrity, indent=1, default=str), encoding='utf8')
    return df, integrity


# ---------------------------------------------------------------- events from labelled filings
def dedup_events(filings, label_col='pred', positives=('A', 'B'), repeat_days=REPEAT_DAYS):
    """Events = A/B filings that are not amendments, have an entry session and a mapped code; one per issuer per
    `repeat_days` (a later A/B filing within the window after the kept event is a repeated reference).
    Returns (events, counts)."""
    f = filings.copy()
    counts = dict(labelled_positive=int(f[label_col].isin(positives).sum()))
    f = f[f[label_col].isin(positives)]
    counts['amendments_dropped'] = int(f['is_amendment'].fillna(False).sum()); f = f[~f['is_amendment'].fillna(False)]
    counts['no_entry_dropped'] = int(f['entry'].isna().sum()); f = f[f['entry'].notna()]
    counts['unmapped_dropped'] = int(f['code'].isna().sum()); f = f[f['code'].notna()]
    f = f.sort_values(['cik', 'accept_et', 'accession'])
    keep, repeated = [], 0
    for cik, g in f.groupby('cik', sort=False):
        last = None
        for idx, r in g.iterrows():
            t = pd.Timestamp(r['accept_et'])
            if last is not None and (t - last).days < repeat_days:
                repeated += 1; continue
            keep.append(idx); last = t
    ev = f.loc[keep].copy()
    counts['repeated_references_merged'] = repeated
    ev['event_id'] = [f'E8B-{int(c):010d}-{a}' for c, a in zip(ev['cik'], ev['accession'])]
    ev = ev.sort_values(['entry', 'accession']).reset_index(drop=True)
    counts['events'] = int(len(ev))
    lk.guard_dates(ev['entry'], 'events'); lk.guard_dates(ev['exit'], 'events exit')
    return ev, counts


if __name__ == '__main__':
    df, integ = build_filing_table()
    print(json.dumps(integ, indent=1, default=str))
