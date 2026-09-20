"""Phase 8B compact text corpus for the two automated classification passes (Amendment 2). No returns, no prices.

One row per fetched candidate filing: header fields, the lead of the 8-K item text and of each EX-99 exhibit (document
zone used by pass 2), and the sentences that mention repurchases with one neighbour each side (sentence zone used by
pass 1). Built per filing-year folder under data/derived/phase8b/corpus/corpus_<yy>.parquet; a year is rebuilt when its
file count changed. `dev_pool` marks the development pool: int(sha256(accession), 16) % 5 == 0.
Usage (from research/): PYTHONUTF8=1 python phase8b_corpus.py [--workers 6]
"""
from concurrent.futures import ProcessPoolExecutor
import argparse
import gzip
import hashlib
import json
import re

import pandas as pd

from phase6_lock import ROOT
from phase8b_lock import guard_filed_date

FILINGS = ROOT / 'data/raw/phase8b/filings'
OUT = ROOT / 'data/derived/phase8b/corpus'
KEY = re.compile(r'(repurchas|buy[\s-]?back|bought\s+back|tender\s+offer|dutch\s+auction|purchase\s+(of\s+)?up\s+to|(purchase|acquire)\s+(shares\s+of\s+)?its\s+(own\s+)?(outstanding\s+)?(common\s+)?(stock|shares))', re.I)
SENT_SPLIT = re.compile(r'(?<=[.!?])\s+(?=["“(A-Z])')
ITEM_START = re.compile(r'Item\s+\d{1,2}(\.\d{2})?\b', re.I)
LEAD_CHARS = 1500
MAX_SENTS = 40
SENT_CHARS = 700


def in_dev_pool(accession):
    return int(hashlib.sha256(accession.encode()).hexdigest(), 16) % 5 == 0


def sentences(text):
    return [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]


def key_sentences(text, doc_type):
    sents = sentences(text)
    keep = set()
    for i, s in enumerate(sents):
        if KEY.search(s):
            keep |= {i - 1, i, i + 1}
    out = []
    for i in sorted(k for k in keep if 0 <= k < len(sents)):
        out.append(dict(doc=doc_type, i=i, hit=bool(KEY.search(sents[i])), text=sents[i][:SENT_CHARS]))
    return out


def lead_of_8k(text):
    m = ITEM_START.search(text, 400) or ITEM_START.search(text)
    start = m.start() if m else 0
    return text[start:start + LEAD_CHARS]


def build_record(path):
    with gzip.open(path, 'rt', encoding='utf8') as fh:
        f = json.load(fh)
    h = f['header']
    if not h.get('filed'):
        return None
    guard_filed_date(h['filed'])
    body = ' '.join(d['text'] for d in f['documents'] if d['type'].upper().startswith('8-K'))
    exs = [d['text'] for d in f['documents'] if d['type'].upper().startswith('EX-99')]
    ks = key_sentences(body, '8-K')
    for k, t in enumerate(exs[:4]):
        ks += key_sentences(t, f'EX-99#{k + 1}')
    acc = f['accession']
    return dict(accession=acc, cik=int(h['cik']) if h.get('cik') else None, company=h.get('company'), filed=h['filed'], year=int(h['filed'][:4]), form=h.get('form'),
                acceptance=h.get('acceptance'), items='|'.join(h.get('items') or []), sic=h.get('sic_code'), n_docs=len(f['documents']), n_ex99=len(exs),
                chars=sum(d['chars'] for d in f['documents']), lead_8k=lead_of_8k(body), lead_ex='\n'.join(t[:LEAD_CHARS] for t in exs[:2]),
                key_sents=json.dumps(ks[:MAX_SENTS]), n_key=sum(1 for s in ks if s['hit']), dev_pool=in_dev_pool(acc))


def build_year(yy, workers):
    d = FILINGS / yy
    files = sorted(d.glob('*.json.gz'))
    out = OUT / f'corpus_{yy}.parquet'; meta = OUT / f'corpus_{yy}.count'
    if out.exists() and meta.exists() and meta.read_text() == str(len(files)):
        return len(files), 'cached'
    with ProcessPoolExecutor(workers) as ex:
        recs = [r for r in ex.map(build_record, files, chunksize=200) if r]
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(recs).to_parquet(out, index=False); meta.write_text(str(len(files)))
    return len(recs), 'built'


def load(columns=None):
    parts = [pd.read_parquet(p, columns=columns) for p in sorted(OUT.glob('corpus_*.parquet'))]
    return pd.concat(parts, ignore_index=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--workers', type=int, default=6); a = ap.parse_args()
    for d in sorted(p.name for p in FILINGS.iterdir() if p.is_dir()):
        print(d, build_year(d, a.workers), flush=True)
