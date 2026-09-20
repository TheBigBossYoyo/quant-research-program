"""Phase 8B EDGAR access: Stage 1 candidate retrieval (full-text search) and full-submission text acquisition.

Retrieval: each frozen expression (phase8b_config.json, retrieval.target_expressions and audit_complement_expressions)
is queried separately against efts.sec.gov, forms 8-K, one calendar month at a time (2004-01..2017-12), paged at 100;
a month approaching the 10,000-hit ceiling is split into halves. Hits (metadata only) are cached per expression and
month under data/raw/phase8b/fts/<slug>/hits_<YYYY-MM>.json.gz. Candidates = accessions matched by any target
expression; the complement = accessions matched by an audit expression and by no target expression.

Acquisition: one GET per accession of the full submission `.txt` (header + all documents), capped at 8 MB, hashed
and logged (data/metadata/phase8b_edgar_acquisition_<stamp>.jsonl). The SGML header is parsed (acceptance datetime,
filed date, form, items, SIC, company name, CIK); 8-K / 8-K/A bodies and EX-99.* exhibits are converted to plain
text; everything else is discarded. Filing dates at or beyond 2018-01-01 are refused (phase8b_lock). SEC fair-access:
declared User-Agent, a shared limiter well under 10 requests per second.
Usage (from research/): PYTHONUTF8=1 python phase8b_edgar.py scan|candidates|fetch [--workers 4]
"""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import argparse
import gzip
import hashlib
import json
import re
import threading
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

from phase6_lock import ROOT
from phase8b_lock import guard_filed_date, Phase8BLockError, RETRIEVAL_START, RETRIEVAL_END

CONFIG = json.loads((ROOT / 'research/phase8b/phase8b_config.json').read_text(encoding='utf8'))
RAW = ROOT / 'data/raw/phase8b'
FTS_DIR = RAW / 'fts'
FILINGS = RAW / 'filings'
DERIVED = ROOT / 'data/derived/phase8b'
META = ROOT / 'data/metadata'
UA = {'User-Agent': os.environ.get('SEC_USER_AGENT', 'Quant research program (set SEC_USER_AGENT to your contact e-mail)'), 'Accept-Encoding': 'gzip, deflate'}
FTS_URL = 'https://efts.sec.gov/LATEST/search-index'
PAGE = CONFIG['retrieval']['page_size']
CEILING = CONFIG['retrieval']['hit_ceiling']
MAX_BYTES = CONFIG['retrieval']['max_bytes_per_submission']
KEEP_TYPES = re.compile(r'^(8-K|8-K/A|EX-99(\.\d+)?[A-Z]?)$', re.I)
TARGET = CONFIG['retrieval']['target_expressions']
AUTH = set(CONFIG['retrieval']['auth_group'])
COMPLEMENT = CONFIG['retrieval']['audit_complement_expressions']

_lock = threading.Lock()
_last = [0.0]
MIN_INTERVAL = 0.14   # ~7 requests per second across threads


def slug(expr):
    return re.sub(r'[^a-z0-9]+', '_', expr.strip('"').lower()).strip('_')


def _throttle():
    with _lock:
        now = time.monotonic(); wait = _last[0] + MIN_INTERVAL - now
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.monotonic()


def _get(url, **kw):
    for attempt in range(5):
        _throttle()
        try:
            r = requests.get(url, headers=UA, timeout=90, **kw)
        except requests.RequestException:
            time.sleep(2 + 3 * attempt); continue
        if r.status_code == 200:
            return r
        if r.status_code in (403, 429, 500, 502, 503, 504):
            time.sleep(3 + 5 * attempt); continue
        return r
    return r


# ---------------------------------------------------------------- Stage 1: full-text search
def fts_query(expr, start, end):
    """All hits for one expression and one date range (inclusive ISO dates). Splits the range when it nears the ceiling."""
    r = _get(FTS_URL, params=dict(q=expr, forms='8-K', dateRange='custom', startdt=start, enddt=end))
    j = r.json() if r.status_code == 200 else {}
    total = int(j.get('hits', {}).get('total', {}).get('value', 0))
    if total > CEILING - 500 and start != end:
        a, b = pd.Timestamp(start), pd.Timestamp(end); mid = a + (b - a) / 2
        t1, h1 = fts_query(expr, start, str(mid.date())); t2, h2 = fts_query(expr, str((mid + pd.Timedelta(days=1)).date()), end)
        return t1 + t2, h1 + h2
    out = []; frm = 0
    while True:
        if frm:
            r = _get(FTS_URL, params=dict(q=expr, forms='8-K', dateRange='custom', startdt=start, enddt=end, **{'from': frm}))
            j = r.json() if r.status_code == 200 else {}
        hits = j.get('hits', {}).get('hits', [])
        out += [dict(id=h.get('_id'), **{k: h['_source'].get(k) for k in ('ciks', 'display_names', 'file_date', 'items', 'form', 'file_num', 'period_ending', 'file_description')}) for h in hits]
        frm += PAGE
        if not hits or frm >= total or frm >= CEILING:
            break
    return total, out


def _scan_one(expr, p):
    d = FTS_DIR / slug(expr); d.mkdir(parents=True, exist_ok=True)
    path = d / f'hits_{p}.json.gz'
    if path.exists():
        try:
            with gzip.open(path, 'rt', encoding='utf8') as fh:
                rec = json.load(fh)
            return dict(expression=expr, month=str(p), total=rec['total'], fetched=rec['fetched'])
        except (OSError, EOFError, ValueError):
            path.unlink()   # partial file from an interrupted run
    total, hits = fts_query(expr, str(p.start_time.date()), str(p.end_time.date()))
    rec = dict(expression=expr, month=str(p), total=total, fetched=len(hits), hits=hits, utc=datetime.now(timezone.utc).isoformat())
    tmp = path.with_suffix('.tmp')
    with gzip.open(tmp, 'wt', encoding='utf8') as fh:
        json.dump(rec, fh)
    tmp.replace(path)
    return dict(expression=expr, month=str(p), total=total, fetched=len(hits))


def scan(expressions=None, months=None, workers=5):
    """Query every expression x month (thread pool under the shared limiter), cache hits, return a counts DataFrame."""
    expressions = list(expressions or TARGET + COMPLEMENT)
    months = list(months or pd.period_range(RETRIEVAL_START.strftime('%Y-%m'), RETRIEVAL_END.strftime('%Y-%m'), freq='M'))
    assert max(months).end_time < pd.Timestamp('2018-01-01'), 'retrieval never queries 2018 or later'
    rows = []
    with ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(_scan_one, e, p) for e in expressions for p in months]
        for i, f in enumerate(as_completed(futs)):
            rows.append(f.result())
            if i % 200 == 0:
                print(i, len(futs), datetime.now(timezone.utc).strftime('%H:%M:%S'), flush=True)
    counts = pd.DataFrame(rows).sort_values(['expression', 'month'])
    DERIVED.mkdir(parents=True, exist_ok=True)
    counts.to_csv(DERIVED / 'fts_counts.csv', index=False)
    return counts


def _load_hits(expr):
    d = FTS_DIR / slug(expr)
    for path in sorted(d.glob('hits_*.json.gz')):
        with gzip.open(path, 'rt', encoding='utf8') as fh:
            for h in json.load(fh)['hits']:
                yield h


def build_candidates():
    """Accession-level candidate table (target set) and complement table (audit set). Both saved under data/derived/phase8b."""
    acc = {}
    for expr in TARGET + COMPLEMENT:
        for h in _load_hits(expr):
            a = h['id'].split(':')[0]
            rec = acc.setdefault(a, dict(accession=a, ciks=set(), display_names=set(), file_date=h.get('file_date'), items=set(), forms=set(), docs=set(), target=set(), complement=set()))
            rec['ciks'] |= set(h.get('ciks') or []); rec['display_names'] |= set(h.get('display_names') or []); rec['items'] |= set(h.get('items') or [])
            rec['forms'].add(h.get('form')); rec['docs'].add(h['id'].split(':', 1)[1] if ':' in h['id'] else '')
            (rec['target'] if expr in TARGET else rec['complement']).add(expr)
            if h.get('file_date') and (rec['file_date'] is None or h['file_date'] < rec['file_date']):
                rec['file_date'] = h['file_date']
    rows = []
    no_date = [a for a, r in acc.items() if not r['file_date']]
    for a in no_date:
        del acc[a]                      # a hit without a file date cannot be checked against the lock; dropped and counted
    for a, r in acc.items():
        guard_filed_date(r['file_date'])
        rows.append(dict(accession=a, cik=sorted(r['ciks'])[0] if r['ciks'] else None, n_ciks=len(r['ciks']), display_name='|'.join(sorted(r['display_names'])),
                         file_date=r['file_date'], items='|'.join(sorted(r['items'])), forms='|'.join(sorted(x for x in r['forms'] if x)), n_docs=len(r['docs']),
                         matched='|'.join(sorted(r['target'])), n_matched=len(r['target']), auth_match=bool(r['target'] & AUTH),
                         complement_matched='|'.join(sorted(r['complement'])), is_candidate=bool(r['target'])))
    df = pd.DataFrame(rows).sort_values(['file_date', 'accession']).reset_index(drop=True)
    df['file_date'] = pd.to_datetime(df['file_date'])
    df['year'] = df['file_date'].dt.year
    DERIVED.mkdir(parents=True, exist_ok=True)
    cand = df[df['is_candidate']].drop(columns=['is_candidate']); comp = df[~df['is_candidate']].drop(columns=['is_candidate', 'matched', 'n_matched', 'auth_match'])
    cand.to_parquet(DERIVED / 'candidates.parquet', index=False); comp.to_parquet(DERIVED / 'complement.parquet', index=False)
    summary = dict(built_utc=datetime.now(timezone.utc).isoformat(), candidates=int(len(cand)), complement=int(len(comp)), dropped_no_file_date=len(no_date),
                   candidates_by_year=cand.groupby('year').size().to_dict(), auth_by_year=cand.groupby('year')['auth_match'].sum().to_dict(),
                   complement_by_year=comp.groupby('year').size().to_dict(), forms=cand['forms'].value_counts().to_dict())
    (DERIVED / 'candidates_summary.json').write_text(json.dumps(summary, indent=1, default=int), encoding='utf8')
    return cand, comp


# ---------------------------------------------------------------- Stage 1b: full submission text
HEADER_RE = re.compile(r'<SEC-HEADER>(.*?)</SEC-HEADER>', re.S)
DOC_RE = re.compile(r'<DOCUMENT>(.*?)</DOCUMENT>', re.S)
TAG_RE = {k: re.compile(rf'<{k}>\s*(.*)') for k in ('TYPE', 'SEQUENCE', 'FILENAME', 'DESCRIPTION')}
TEXT_RE = re.compile(r'<TEXT>(.*?)(</TEXT>|$)', re.S)


def parse_header(raw):
    """SGML header fields. `raw` is the beginning of the full submission text."""
    m = HEADER_RE.search(raw)
    head = m.group(1) if m else raw[:20000]

    def one(pattern):
        mm = re.search(pattern, head)
        return mm.group(1).strip() if mm else None
    items = re.findall(r'ITEM INFORMATION:\s*(.+)', head)
    sic = one(r'STANDARD INDUSTRIAL CLASSIFICATION:\s*(.+)')
    sic_code = re.search(r'\[(\d{4})\]', sic) if sic else None
    return dict(acceptance=one(r'<ACCEPTANCE-DATETIME>\s*(\d{14})'), filed=one(r'FILED AS OF DATE:\s*(\d{8})'), form=one(r'CONFORMED SUBMISSION TYPE:\s*(\S+)'),
                period=one(r'CONFORMED PERIOD OF REPORT:\s*(\d{8})'), items=[i.strip() for i in items], sic=sic, sic_code=sic_code.group(1) if sic_code else None,
                company=one(r'COMPANY CONFORMED NAME:\s*(.+)'), cik=one(r'CENTRAL INDEX KEY:\s*(\d+)'), doc_count=one(r'PUBLIC DOCUMENT COUNT:\s*(\d+)'))


def html_to_text(s):
    if '<' not in s:
        return re.sub(r'\s+', ' ', s).strip()
    try:
        soup = BeautifulSoup(s, 'lxml')
        for t in soup(['script', 'style']):
            t.decompose()
        txt = soup.get_text(' ')
    except Exception:
        txt = re.sub(r'<[^>]+>', ' ', s)
    txt = txt.replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', txt).strip()


def parse_documents(raw, keep=KEEP_TYPES, max_chars=400_000):
    docs = []
    for m in DOC_RE.finditer(raw):
        block = m.group(1)
        fields = {k: (rx.search(block).group(1).strip() if rx.search(block) else None) for k, rx in TAG_RE.items()}
        if not fields['TYPE'] or not keep.match(fields['TYPE']):
            continue
        t = TEXT_RE.search(block)
        text = html_to_text(t.group(1)) if t else ''
        docs.append(dict(type=fields['TYPE'], sequence=fields['SEQUENCE'], filename=fields['FILENAME'], description=fields['DESCRIPTION'], text=text[:max_chars], chars=len(text)))
    return docs


def guard_accession_year(accession):
    """Accession numbers carry the filing year as digits 11-12 (YY); refuse 2018 and later as a second check."""
    yy = accession[11:13]
    if not yy.isdigit():
        raise Phase8BLockError(f'unparseable accession {accession!r}')
    year = 1900 + int(yy) if int(yy) >= 90 else 2000 + int(yy)
    if year >= 2018:
        raise Phase8BLockError(f'accession {accession} is from {year} (locked)')
    return year


def submission_url(cik, accession):
    return f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace("-", "")}/{accession}.txt'


def fetch_submission(cik, accession, log=None):
    """Download, parse and store one submission; returns a status string. Refuses locked filing dates."""
    year_dir = FILINGS / accession[11:13]
    dest = year_dir / f'{accession}.json.gz'
    if dest.exists():
        return 'cached'
    url = submission_url(cik, accession)
    for attempt in range(4):
        _throttle()
        try:
            r = requests.get(url, headers=UA, timeout=120, stream=True)
        except requests.RequestException:
            time.sleep(3 + 3 * attempt); continue
        if r.status_code == 200:
            break
        r.close()
        if r.status_code == 404:
            return _log(log, dict(accession=accession, url=url, status=404))
        time.sleep(3 + 5 * attempt)
    else:
        return _log(log, dict(accession=accession, url=url, status='failed'))
    buf = bytearray(); truncated = False
    for chunk in r.iter_content(65536):
        buf += chunk
        if len(buf) >= MAX_BYTES:
            truncated = True; break
    r.close()
    raw = bytes(buf).decode('latin1')
    header = parse_header(raw)
    if not header.get('filed'):
        return _log(log, dict(accession=accession, url=url, status='refused_no_filed_date', bytes=len(buf)))
    try:
        guard_filed_date(header['filed'])
        guard_accession_year(accession)
    except Phase8BLockError as exc:
        return _log(log, dict(accession=accession, url=url, status='refused_locked_date', reason=str(exc)))
    docs = parse_documents(raw)
    payload = dict(accession=accession, cik_query=str(cik), header=header, documents=docs, truncated=truncated, bytes=len(buf),
                   sha256_raw=hashlib.sha256(bytes(buf)).hexdigest(), fetched_utc=datetime.now(timezone.utc).isoformat(), url=url)
    year_dir.mkdir(parents=True, exist_ok=True)
    with gzip.open(dest, 'wt', encoding='utf8') as fh:
        json.dump(payload, fh)
    return _log(log, dict(accession=accession, url=url, status='ok', bytes=len(buf), sha256_raw=payload['sha256_raw'], truncated=truncated, n_docs=len(docs), file=dest.relative_to(ROOT).as_posix()))


def _log(log, rec):
    rec['utc'] = datetime.now(timezone.utc).isoformat()
    if log is not None:
        with _lock:
            log.write(json.dumps(rec) + '\n'); log.flush()
    return str(rec['status'])


def load_filing(accession):
    path = FILINGS / accession[11:13] / f'{accession}.json.gz'
    if not path.exists():
        return None
    with gzip.open(path, 'rt', encoding='utf8') as fh:
        return json.load(fh)


def fetch_all(table, workers=4, limit=None):
    """Fetch every (cik, accession) in `table` (DataFrame with those columns) not yet on disk."""
    todo = [(c, a) for c, a in zip(table['cik'], table['accession']) if c and not (FILINGS / a[11:13] / f'{a}.json.gz').exists()]
    if limit:
        todo = todo[:limit]
    META.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    counts = {}
    with open(META / f'phase8b_edgar_acquisition_{stamp}.jsonl', 'a', encoding='utf8') as log, ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(fetch_submission, c, a, log) for c, a in todo]
        for i, f in enumerate(as_completed(futs)):
            s = f.result(); counts[s] = counts.get(s, 0) + 1
            if i % 500 == 0:
                print(i, len(todo), counts, flush=True)
    print('done', counts, flush=True)
    return counts


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['scan', 'candidates', 'fetch', 'fetch_complement'])
    ap.add_argument('--workers', type=int, default=4); ap.add_argument('--limit', type=int, default=None)
    a = ap.parse_args()
    if a.mode == 'scan':
        c = scan(workers=a.workers); print(c.groupby('expression')['total'].sum())
    elif a.mode == 'candidates':
        cand, comp = build_candidates(); print(len(cand), len(comp)); print(cand.groupby('year').size())
    elif a.mode == 'fetch':
        cand = pd.read_parquet(DERIVED / 'candidates.parquet'); fetch_all(cand, a.workers, a.limit)
    elif a.mode == 'fetch_complement':
        comp = pd.read_parquet(DERIVED / 'complement_sample.parquet'); fetch_all(comp, a.workers, a.limit)
