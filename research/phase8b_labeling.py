"""Phase 8B human-labelling package: stratified sample of candidate filings, passages with context, frozen classifier split,
retrieval-audit sample, package verification. Everything here happens BEFORE any label exists and shows the labeller
nothing dated after the filing (no price, return, market cap, or current ticker).

Main sample (phase8b_config.json labels.sample): population = candidates whose search-index form is 8-K with a known CIK;
strata S1 (any authorisation-language expression matched) / S2 (other); per stratum, filing years 2004-2017 allocated in
proportion to counts with a floor per year; one candidate per issuer per year; seeded order per cell, first k eligible
after fetching are kept. Classifier split: one third HOLDOUT per year x stratum cell, drawn from the seeded order, with
every row of the same CIK forced into the partition of that CIK's first assigned row (no issuer straddles the split).
Retrieval-audit sample (labels.retrieval_audit): complement population = accessions matched by an audit expression and
by no target expression, form 8-K, CIK known; strata B1 (non-earnings items 8.01/7.01 without 2.02) / B2 (rest).
Usage (from research/): PYTHONUTF8=1 python phase8b_labeling.py package|draw_complement|audit_package|verify
"""
from datetime import datetime, timezone
import hashlib
import json
import re
import sys
import zipfile

import numpy as np
import pandas as pd

from phase6_lock import ROOT
import phase8b_edgar as ed
from phase8b_lock import guard_dates

CONFIG = ed.CONFIG['labels']
OUT = ROOT / 'research/phase8b'
TEXTS = OUT / 'labeling_texts'
DERIVED = ed.DERIVED
KEY_RE = re.compile(r'(repurchas|buy[\s-]?back|purchase\s+(of\s+)?up\s+to|tender\s+offer|dutch\s+auction)', re.I)
AUTH_RE = re.compile(r'(authoriz|approv|increas|expand|additional|new\s+(share|stock|repurchase)|replac|extend|renew)', re.I)
NON_EARNINGS_ITEMS = ('8.01', '7.01')
EARNINGS_ITEM = '2.02'


def passages(text, ctx=400, max_windows=4, max_chars=2600):
    """Keyword windows with `ctx` characters of context each side; windows mentioning authorisation words come first."""
    if not text:
        return ''
    spans = []
    for m in KEY_RE.finditer(text):
        a, b = max(0, m.start() - ctx), min(len(text), m.end() + ctx)
        if spans and a <= spans[-1][1]:
            spans[-1] = (spans[-1][0], b)
        else:
            spans.append((a, b))
    if not spans:
        return ''
    scored = sorted(range(len(spans)), key=lambda i: (0 if AUTH_RE.search(text[spans[i][0]:spans[i][1]]) else 1, i))
    picked = sorted(scored[:max_windows])
    out = ' [...] '.join(('' if a == 0 else '...') + text[a:b] + ('' if b == len(text) else '...') for a, b in (spans[i] for i in picked))
    return out[:max_chars]


def filing_texts(accession):
    """(8-K body text, concatenated EX-99 text, header, filing) for one stored filing, or None."""
    f = ed.load_filing(accession)
    if f is None:
        return None
    body = ' '.join(d['text'] for d in f['documents'] if d['type'].upper().startswith('8-K'))
    ex = ' '.join(d['text'] for d in f['documents'] if d['type'].upper().startswith('EX-99'))
    return body, ex, f['header'], f


def allocate(counts, total, floor):
    """Quota per year: floor each, remainder proportional to counts (largest-remainder rounding), capped at availability."""
    years = list(counts.index)
    base = {y: min(int(counts[y]), floor) for y in years}
    left = total - sum(base.values())
    avail = {y: int(counts[y]) - base[y] for y in years}
    if left > 0 and sum(avail.values()) > 0:
        w = np.array([avail[y] for y in years], dtype=float); w = w / w.sum()
        raw = w * left; add = np.floor(raw).astype(int); rem = left - add.sum()
        for i in np.argsort(-(raw - add))[:rem]:
            add[i] += 1
        for y, k in zip(years, add):
            base[y] += min(int(k), avail[y])
    return base


def population(cand):
    """Labelling population: search-index form 8-K (amendments excluded), CIK known."""
    return cand[(cand['forms'] == '8-K') & cand['cik'].notna()].copy()


def ordered_cells(pop, strata, seed, one_per_issuer=True, oversample=3):
    """Seeded per-cell order. `strata`: list of (name, mask, total, floor). Returns rows with stratum, cell_quota, cell_rank."""
    rng = np.random.default_rng(seed)
    picks = []
    for name, mask, total, floor in strata:
        s = pop[mask]
        quota = allocate(s.groupby('year').size(), total, floor)
        for y, k in quota.items():
            g = s[s['year'] == y]
            order = g.iloc[rng.permutation(len(g))]
            if one_per_issuer:
                order = order.drop_duplicates('cik', keep='first')
            take = order.head(k * oversample).copy(); take['stratum'] = name; take['cell_quota'] = k; take['cell_rank'] = np.arange(len(take))
            picks.append(take)
    return pd.concat(picks).reset_index(drop=True)


def sample_candidates(cand, seed=CONFIG['sample']['seed'], cfg=CONFIG['sample'], oversample=1):
    """Stratified seeded sample of the main labelling population (S1 authorisation language / S2 other)."""
    c = cand[cand['cik'].notna()].copy()
    strata = [('S1', c['auth_match'].astype(bool), cfg['stratum_S1_auth'], cfg['year_floor_S1']), ('S2', ~c['auth_match'].astype(bool), cfg['stratum_S2_other'], cfg['year_floor_S2'])]
    return ordered_cells(c, strata, seed, cfg.get('one_per_issuer_year', True), oversample)


def fetch_and_check(accession, cik):
    """Fetch one filing if needed; return True when it is a non-amended 8-K with an acceptance time and text."""
    ed.fetch_submission(cik, accession)
    f = ed.load_filing(accession)
    return bool(f is not None and f['header'].get('form') == '8-K' and f['header'].get('acceptance') and any(d['chars'] > 0 for d in f['documents']))


def first_eligible(ordered):
    """Per cell, in seeded order, keep the first `cell_quota` rows that are eligible after fetching."""
    kept, why = [], dict(ok=0, ineligible_after_fetch=0)
    for (y, s), g in ordered.groupby(['year', 'stratum'], sort=True):
        k = int(g['cell_quota'].iloc[0]); n = 0
        for _, r in g.sort_values('cell_rank').iterrows():
            if n >= k:
                break
            if fetch_and_check(r['accession'], r['cik']):
                kept.append(r); n += 1; why['ok'] += 1
            else:
                why['ineligible_after_fetch'] += 1
        print('cell', y, s, n, '/', k, flush=True)
    return pd.DataFrame(kept).reset_index(drop=True), why


def assign_split(sample, seed=CONFIG['split']['seed']):
    """One third HOLDOUT inside every year x stratum cell (positions 2, 5, 8, ... of a seeded shuffle); every row of a
    CIK already assigned in an earlier cell (cells visited in sorted year, stratum order) inherits that partition."""
    rng = np.random.default_rng(seed + 1)
    labels = pd.Series('DEV', index=sample.index); assigned = {}
    for _, g in sample.groupby(['year', 'stratum'], sort=True):
        idx = g.index.to_numpy()[rng.permutation(len(g))]
        hold = set(idx[2::3])
        for i in idx:
            cik = int(sample.at[i, 'cik'])
            part = assigned.get(cik, 'HOLDOUT' if i in hold else 'DEV')
            labels.loc[i] = part; assigned.setdefault(cik, part)
    return labels


def _row(rec, texts):
    body, ex, h, f = texts
    acc = rec['accession']
    return dict(event_id=f"E8B-{int(rec['cik']):010d}-{acc}", accession=acc, cik=int(rec['cik']), company_name=h.get('company') or rec.get('display_name', ''),
                form=h.get('form'), filing_date=str(pd.Timestamp(rec['file_date']).date()), acceptance_datetime_et=h.get('acceptance'),
                items_8k='|'.join(h.get('items') or []), sic=h.get('sic'), documents='|'.join(f"{d['type']}:{d['chars']}" for d in f['documents']),
                passage_8k_body=passages(body), passage_exhibits=passages(ex), full_text_path=f'labeling_texts/{acc}.txt', human_label='', human_notes='')


def _write_text(acc, texts):
    body, ex, h, f = texts
    TEXTS.mkdir(parents=True, exist_ok=True)
    parts = [f"ACCESSION {acc}  FORM {h.get('form')}  FILED {h.get('filed')}  ACCEPTED {h.get('acceptance')} ET  COMPANY {h.get('company')}  ITEMS {h.get('items')}", '']
    for d in f['documents']:
        parts += [f"===== {d['type']} {d['filename'] or ''} {d['description'] or ''} =====", d['text'], '']
    (TEXTS / f'{acc}.txt').write_text('\n'.join(parts), encoding='utf8')


def _hash_record(path, stage):
    b = path.read_bytes()
    rec = dict(file=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b), frozen_utc=datetime.now(timezone.utc).isoformat(), stage=stage)
    with open(OUT / 'PHASE8B_FREEZE_HASHES.jsonl', 'a', encoding='utf8') as fh:
        fh.write(json.dumps(rec) + '\n')
    return rec


def package():
    cand = pd.read_parquet(DERIVED / 'candidates.parquet')
    guard_dates(cand['file_date'], 'candidates')
    pop = population(cand)
    sample, why = first_eligible(sample_candidates(pop, oversample=3))
    sample['split'] = assign_split(sample)
    rows = []
    for _, r in sample.iterrows():
        t = filing_texts(r['accession'])
        rows.append(_row(r, t)); _write_text(r['accession'], t)
    csv = pd.DataFrame(rows)
    csv = csv.iloc[np.random.default_rng(CONFIG['sample']['seed'] + 2).permutation(len(csv))].reset_index(drop=True)
    csv.to_csv(OUT / 'phase8b_labeling_candidates.csv', index=False, encoding='utf8')
    split = sample[['accession', 'cik', 'year', 'stratum', 'split', 'matched']].copy()
    split['event_id'] = [f"E8B-{int(c):010d}-{a}" for c, a in zip(split['cik'], split['accession'])]
    split = split.sort_values('accession').reset_index(drop=True)
    split.to_csv(OUT / 'phase8b_label_split.csv', index=False)
    cs = split[['event_id', 'accession', 'cik', 'year', 'stratum']].copy(); cs['classifier_partition'] = split['split'].map({'DEV': 'DEVELOPMENT', 'HOLDOUT': 'HOLDOUT'})
    cs.to_csv(OUT / 'phase8b_classifier_split.csv', index=False)
    pop_counts = pop.groupby(np.where(pop['auth_match'], 'S1', 'S2')).size().to_dict()
    ciks_both = int(sum(1 for _, g in split.groupby('cik') if g['split'].nunique() > 1))
    meta = dict(built_utc=datetime.now(timezone.utc).isoformat(), n_candidates=int(len(cand)), fetch_eligibility=why, n_population=int(len(pop)), n_sample=int(len(sample)),
                population_definition='search-index form 8-K, CIK known; the search index lists 8-K/A separately and those are excluded',
                population_by_stratum=pop_counts, sample_by_stratum=sample['stratum'].value_counts().to_dict(),
                stratum_weights={s: pop_counts[s] / int((sample['stratum'] == s).sum()) for s in pop_counts},
                split_counts={f'{k[0]}|{k[1]}': int(v) for k, v in sample.groupby(['stratum', 'split']).size().items()},
                split_by_year={str(y): {p: int(n) for p, n in g['split'].value_counts().items()} for y, g in sample.groupby('year')},
                distinct_ciks=int(split['cik'].nunique()), ciks_with_multiple_rows=int((split.groupby('cik').size() > 1).sum()), ciks_straddling_partitions=ciks_both,
                empty_snippet_rows=int(((csv['passage_8k_body'] == '') & (csv['passage_exhibits'] == '')).sum()),
                by_year=sample.groupby(['year', 'stratum']).size().unstack(fill_value=0).to_dict(), seed=CONFIG['sample']['seed'], split_seed=CONFIG['split']['seed'])
    (OUT / 'phase8b_labeling_meta.json').write_text(json.dumps(meta, indent=1, default=str), encoding='utf8')
    for name in ('phase8b_labeling_candidates.csv', 'phase8b_label_split.csv', 'phase8b_classifier_split.csv', 'phase8b_labeling_guide.md', 'phase8b_labeling_meta.json'):
        print(_hash_record(OUT / name, 'labelling package v2 (no label exists)'))
    print(json.dumps({k: v for k, v in meta.items() if k not in ('by_year', 'split_by_year')}, indent=1, default=str))
    return csv, split


def complement_population():
    comp = pd.read_parquet(DERIVED / 'complement.parquet')
    comp = comp[comp['cik'].notna() & (comp['forms'] == '8-K')].copy()
    items = comp['items'].fillna('')
    non_earn = items.apply(lambda s: any(i in s.split('|') for i in NON_EARNINGS_ITEMS) and EARNINGS_ITEM not in s.split('|'))
    comp['audit_stratum'] = np.where(non_earn, 'B1', 'B2')
    return comp


def draw_complement_sample(cfg=CONFIG['retrieval_audit']):
    comp = complement_population()
    strata = [('B1', comp['audit_stratum'] == 'B1', cfg['stratum_B1_non_earnings'], cfg['year_floor_B1']), ('B2', comp['audit_stratum'] == 'B2', cfg['stratum_B2_other'], cfg['year_floor_B2'])]
    ordered = ordered_cells(comp, strata, cfg['seed'] + 3, True, 3)
    ordered.to_parquet(DERIVED / 'complement_sample_ordered.parquet', index=False)
    return ordered, comp


def audit_package():
    """Retrieval-recall audit sample (part b), packaged like the labelling sample; population and strata documented in meta."""
    ordered, comp = draw_complement_sample()
    sample, why = first_eligible(ordered)
    rows = []
    for _, r in sample.iterrows():
        t = filing_texts(r['accession'])
        rows.append(_row(r, t)); _write_text(r['accession'], t)
    csv = pd.DataFrame(rows)
    csv = csv.iloc[np.random.default_rng(CONFIG['retrieval_audit']['seed'] + 4).permutation(len(csv))].reset_index(drop=True)
    csv.to_csv(OUT / 'phase8b_retrieval_audit_candidates.csv', index=False, encoding='utf8')
    strata = sample[['accession', 'cik', 'year', 'stratum', 'complement_matched', 'items']].copy()
    strata['event_id'] = [f"E8B-{int(c):010d}-{a}" for c, a in zip(strata['cik'], strata['accession'])]
    strata.sort_values('accession').to_csv(OUT / 'phase8b_retrieval_audit_strata.csv', index=False)
    pop_counts = comp['audit_stratum'].value_counts().to_dict()
    meta = dict(built_utc=datetime.now(timezone.utc).isoformat(), population_definition='complement accessions (matched by an audit expression, by no target expression), search-index form 8-K, CIK known',
                population_total=int(len(comp)), population_by_stratum=pop_counts, population_by_year_stratum=comp.groupby(['year', 'audit_stratum']).size().unstack(fill_value=0).to_dict(),
                sample_by_stratum=sample['stratum'].value_counts().to_dict(), sample_by_year_stratum=sample.groupby(['year', 'stratum']).size().unstack(fill_value=0).to_dict(),
                stratum_weights={s: pop_counts[s] / int((sample['stratum'] == s).sum()) for s in pop_counts}, fetch_eligibility=why,
                empty_snippet_rows=int(((csv['passage_8k_body'] == '') & (csv['passage_exhibits'] == '')).sum()), seed=CONFIG['retrieval_audit']['seed'])
    (OUT / 'phase8b_retrieval_audit_meta.json').write_text(json.dumps(meta, indent=1, default=str), encoding='utf8')
    for name in ('phase8b_retrieval_audit_candidates.csv', 'phase8b_retrieval_audit_strata.csv', 'phase8b_retrieval_audit_meta.json'):
        print(_hash_record(OUT / name, 'retrieval-recall audit package v2 (no label exists)'))
    print(json.dumps({k: v for k, v in meta.items() if 'year' not in k}, indent=1, default=str))
    return csv


def verify_package(zip_name='phase8b_labeling_package.zip'):
    """Check every full_text_path resolves; count empty snippets; zip guide + CSVs + referenced texts. Returns the report."""
    report = dict(verified_utc=datetime.now(timezone.utc).isoformat())
    files = []
    for name in ('phase8b_labeling_candidates.csv', 'phase8b_retrieval_audit_candidates.csv'):
        df = pd.read_csv(OUT / name, dtype=str).fillna('')
        missing = [p for p in df['full_text_path'] if not (OUT / p).exists()]
        report[name] = dict(rows=int(len(df)), empty_snippet_rows=int(((df['passage_8k_body'] == '') & (df['passage_exhibits'] == '')).sum()),
                            referenced_texts=int(df['full_text_path'].nunique()), missing_texts=len(missing), missing_list=missing[:20],
                            forbidden_columns_present=[c for c in df.columns if 'ticker' in c.lower() or 'return' in c.lower() or 'price' in c.lower()])
        files += [OUT / p for p in df['full_text_path'].unique()]
    report['missing_total'] = sum(report[n]['missing_texts'] for n in ('phase8b_labeling_candidates.csv', 'phase8b_retrieval_audit_candidates.csv'))
    zpath = OUT / zip_name
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in ('phase8b_labeling_guide.md', 'phase8b_labeling_candidates.csv', 'phase8b_retrieval_audit_candidates.csv', 'PHASE8B_RETRIEVAL_AUDIT_DESIGN.md'):
            if (OUT / name).exists():
                z.write(OUT / name, name)
        for p in sorted(set(files)):
            if p.exists():
                z.write(p, f'labeling_texts/{p.name}')
        z.writestr('README.txt', 'Phase 8B human-labelling package. Fill human_label (A-J) in both CSVs per phase8b_labeling_guide.md. Full texts: labeling_texts/<accession>.txt. Do not look up prices, returns or later filings.\n')
    report['zip'] = dict(file=zpath.relative_to(ROOT).as_posix(), bytes=zpath.stat().st_size, members=len(set(files)) + 5)
    (OUT / 'phase8b_package_verification.json').write_text(json.dumps(report, indent=1), encoding='utf8')
    print(json.dumps(report, indent=1))
    return report


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'package':
        package()
    elif mode == 'draw_complement':
        o, c = draw_complement_sample(); print(len(o), c['audit_stratum'].value_counts().to_dict())
    elif mode == 'audit_package':
        audit_package()
    elif mode == 'verify':
        verify_package()
    else:
        print('usage: package|draw_complement|audit_package|verify')
