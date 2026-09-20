"""Phase 8B Amendment 2: classify the universe with both passes, report their agreement, freeze, draw the blinded 60-case
human gold set. No returns, no prices. Order of operations is enforced:
  freeze   -> records SHA-256 of phase8b_classifier.py and phase8b_corpus.py as 'classifier frozen'
  classify -> both passes over every corpus row (pass 2 never sees pass-1 output); writes classified.parquet + agreement report
  draw     -> refuses unless the frozen hashes match the current files and classified.parquet was built with them;
              samples strata P/N/H from the non-development pool only; writes the human CSV (no prediction, no stratum)
              and a sealed key file that the labelling UI never serves before all labels are saved.
Usage (from research/): PYTHONUTF8=1 python phase8b_gold.py freeze|classify|draw
"""
from datetime import datetime, timezone
import hashlib
import json
import re
import sys

import numpy as np
import pandas as pd

from phase6_lock import ROOT
import phase8b_classifier as clf
import phase8b_corpus as cp
import phase8b_edgar as ed
from phase8b_lock import guard_dates

CFG = ed.CONFIG['amendment2']
G = CFG['gold']
OUT = ROOT / 'research/phase8b'
GOLD_DIR = OUT / 'gold'
DERIVED = ed.DERIVED
HASH_LOG = OUT / 'PHASE8B_FREEZE_HASHES.jsonl'
CLASSIFIER_FILES = ['research/phase8b_classifier.py', 'research/phase8b_corpus.py']
GENERIC_CUE = re.compile(r'(authoriz|approv|increas|additional|\bnew\b|expand|extend|renew|complet|accelerated|tender)', re.I)


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def log(rec):
    rec['frozen_utc'] = datetime.now(timezone.utc).isoformat()
    with open(HASH_LOG, 'a', encoding='utf8') as fh:
        fh.write(json.dumps(rec) + '\n')


def frozen_hashes():
    recs = [json.loads(l) for l in HASH_LOG.read_text(encoding='utf8').splitlines() if l.strip()]
    out = {}
    for r in recs:
        if r.get('stage', '').startswith('classifier frozen'):
            out[r['file']] = r['sha256']
    return out


def is_frozen():
    fz = frozen_hashes()
    return bool(fz) and all(fz.get(f) == sha(f) for f in CLASSIFIER_FILES)


def freeze():
    for f in CLASSIFIER_FILES:
        log(dict(file=f, sha256=sha(f), stage=f'classifier frozen (Amendment 2; version {clf.VERSION}; developed on the development pool only; no human label exists)'))
    print('frozen', {f: sha(f)[:16] for f in CLASSIFIER_FILES})


def classify():
    if not is_frozen():
        raise RuntimeError('classify refused: classifier files are not frozen with their current hashes (run freeze first)')
    df = cp.load()
    guard_dates(pd.to_datetime(df['filed'], format='%Y%m%d'), 'corpus filed dates')
    out = clf.classify_frame(df)
    out['classifier_sha'] = sha(CLASSIFIER_FILES[0])
    out.to_parquet(DERIVED / 'classified.parquet', index=False)
    rep = agreement_report(out)
    (OUT / 'phase8b_pass_agreement.json').write_text(json.dumps(rep, indent=1, default=str), encoding='utf8')
    print(json.dumps(rep, indent=1, default=str))
    return out


def agreement_report(out):
    f = out[out['form'] == '8-K']
    pos = f[f['p1_primary']]
    rep = dict(built_utc=datetime.now(timezone.utc).isoformat(), classifier_version=clf.VERSION, n_filings=int(len(f)), p1_labels=f['p1_label'].value_counts().to_dict(),
               p1_positives=int(len(pos)), p2_positives=int(f['p2_primary'].sum()), p2_rejects_share_of_p1_positives=float(1 - pos['p2_primary'].mean()) if len(pos) else None,
               p2_only=int((f['p2_primary'] & ~f['p1_primary']).sum()), agreement_primary_overall=float((f['p1_primary'] == f['p2_primary']).mean()),
               p1_positives_by_year=pos.groupby('year').size().to_dict(),
               by_pool={k: dict(p1_positives=int(g['p1_primary'].sum()), p2_rejects=float(1 - g[g['p1_primary']]['p2_primary'].mean())) for k, g in f.groupby(f['dev_pool'].map({True: 'development', False: 'gold_pool'}))})
    negs = f[(~f['p1_primary']) & (~f['p2_primary']) & (f['p1_label'] != 'UNCLASSIFIED')]
    rep['negative_margin_median'] = float(negs['p1_margin'].median()) if len(negs) else 1.0
    rep['corpus_coverage'] = 'all fetched candidate filings at build time (the download of 2013-2017 may still be running; recomputed when complete)'
    rep['instability_flag'] = bool(rep['p2_rejects_share_of_p1_positives'] is not None and rep['p2_rejects_share_of_p1_positives'] > CFG['instability_rule']['pass2_rejects_share_of_pass1_positives_max'])
    return rep


def context_for(accession, evidence, key_chars=G['context_chars_key'], wide_chars=G['context_chars_wide']):
    """Key passage and wider context chosen by the same generic procedure for every stratum (blind to the prediction):
    up to three repurchase sentences ranked by generic cue words, each with its neighbours, in document order; the wider
    context is the filing text around the first of them."""
    f = ed.load_filing(accession)
    docs = [d for d in f['documents'] if d['type'].upper().startswith(('8-K', 'EX-99'))]
    best = None
    for d in docs:
        sents = cp.sentences(d['text'])
        hits = [i for i, s in enumerate(sents) if cp.KEY.search(s)]
        if not hits:
            continue
        ranked = sorted(hits, key=lambda i: (0 if (evidence and evidence[:80] in sents[i]) else 1, 0 if GENERIC_CUE.search(sents[i]) else 1, i))[:3]
        score = (0 if any(evidence and evidence[:80] in sents[i] for i in ranked) else 1, 0 if any(GENERIC_CUE.search(sents[i]) for i in ranked) else 1)
        if best is None or score < best[0]:
            best = (score, d, sents, sorted(ranked))
    if best is None:
        text = docs[0]['text'] if docs else ''
        return text[:key_chars], text[:wide_chars], (docs[0]['type'] if docs else '')
    _, d, sents, ranked = best
    keep = sorted({j for i in ranked for j in (i - 1, i, i + 1) if 0 <= j < len(sents)})
    parts, prev = [], None
    for j in keep:
        if prev is not None and j != prev + 1:
            parts.append('[...]')
        parts.append(sents[j][:key_chars]); prev = j
    key = ' '.join(parts)
    pos = d['text'].find(sents[ranked[0]][:60])
    a = max(0, pos - wide_chars // 3); wide = ('...' if a else '') + d['text'][a:a + wide_chars] + '...'
    return key[:key_chars * 3], wide, d['type']


def sample_one_per_cik(frame, n, rng, used):
    order = frame.iloc[rng.permutation(len(frame))]
    picks = []
    for _, r in order.iterrows():
        if r['cik'] in used or pd.isna(r['cik']):
            continue
        picks.append(r); used.add(r['cik'])
        if len(picks) == n:
            break
    return picks


def draw(write=True):
    if not is_frozen():
        raise RuntimeError('draw refused: classifier files are not frozen with their current hashes')
    out = pd.read_parquet(DERIVED / 'classified.parquet')
    if set(out['classifier_sha']) != {sha(CLASSIFIER_FILES[0])}:
        raise RuntimeError('draw refused: classified.parquet was built with a different classifier version')
    if (GOLD_DIR / 'phase8b_gold_candidates.csv').exists() and write:
        raise RuntimeError('draw refused: a gold set already exists; it is drawn once')
    gold, pool, pos, neg, low = select_gold(out)
    human, key = [], []
    for _, r in gold.iterrows():
        kp, wide, doc = context_for(r['accession'], r['p1_evidence'] if r['p1_primary'] else '')
        human.append(dict(gold_id=r['gold_id'], company=r['company'], filing_date=f"{r['filed'][:4]}-{r['filed'][4:6]}-{r['filed'][6:8]}", form=r['form'], items_8k=r['items'],
                          source_document=doc, key_passage=kp, wider_context=wide, human_label='', human_notes=''))
        key.append(dict(gold_id=r['gold_id'], accession=r['accession'], cik=int(r['cik']), year=int(r['year']), stratum=r['stratum'], p1_label=r['p1_label'], p1_primary=bool(r['p1_primary']),
                        p1_margin=float(r['p1_margin']), p1_rule=r['p1_rule'], p1_evidence=r['p1_evidence'], p2_primary=bool(r['p2_primary']), p2_score=float(r['p2_score'])))
    return finish_draw(pd.DataFrame(human), pd.DataFrame(key), gold, pool, pos, neg, low, write)


def select_gold(out, seed=None):
    """Strata P (recent/early), N, H from the non-development pool; one case per CIK; seeded; returns the shuffled gold frame."""
    pool = out[(~out['dev_pool']) & (out['form'] == '8-K') & out['cik'].notna()].copy()
    rng = np.random.default_rng(G['seed'] if seed is None else seed); used = set(); rows = []
    pos = pool[pool['p1_primary']]
    for name, frame, n in (('P_recent', pos[pos['year'] >= 2013], G['P_recent_2013_2017']), ('P_early', pos[pos['year'] <= 2012], G['P_early_2004_2012'])):
        rows += [dict(r, stratum=name) for r in sample_one_per_cik(frame, n, rng, used)]
    neg = pool[(~pool['p1_primary']) & (~pool['p2_primary']) & (pool['p1_label'] != 'UNCLASSIFIED')]
    neg = neg[neg['p1_margin'] >= neg['p1_margin'].median()]
    rows += [dict(r, stratum='N_obvious') for r in sample_one_per_cik(neg, G['stratum_N_obvious_negative'], rng, used)]
    half = G['H_pass_disagreement'] // 2
    rows += [dict(r, stratum='H_p1_only') for r in sample_one_per_cik(pool[pool['p1_primary'] & ~pool['p2_primary']], half, rng, used)]
    rows += [dict(r, stratum='H_p2_only') for r in sample_one_per_cik(pool[~pool['p1_primary'] & pool['p2_primary']], G['H_pass_disagreement'] - half, rng, used)]
    low = pool[(pool['p1_label'] == 'UNCLASSIFIED') | (pool['p1_primary'] & (pool['p1_margin'] <= 1.0))]
    rows += [dict(r, stratum='H_low_margin') for r in sample_one_per_cik(low, G['H_low_margin_or_unclassified'], rng, used)]
    gold = pd.DataFrame(rows)
    gold = gold.iloc[rng.permutation(len(gold))].reset_index(drop=True)
    gold['gold_id'] = [f'G{i + 1:03d}' for i in range(len(gold))]
    return gold, pool, pos, neg, low


def stratum_for(row, quotas, negative_margin_min):
    """Stratum a classified filing can fill, or None. Stratum P is served first for every predicted positive, so P is an
    unbiased random sample of all pass-1 positives (including low-margin ones and those pass 2 rejects)."""
    if row['p1_primary']:
        p = 'P_recent' if row['year'] >= 2013 else 'P_early'
        if quotas[p] > 0:
            return p
        if not row['p2_primary'] and quotas['H_p1_only'] > 0:
            return 'H_p1_only'
        if row['p1_margin'] <= 1.0 and quotas['H_low_margin'] > 0:
            return 'H_low_margin'
        return None
    if row['p2_primary']:
        return 'H_p2_only' if quotas['H_p2_only'] > 0 else None
    if row['p1_label'] == 'UNCLASSIFIED':
        return 'H_low_margin' if quotas['H_low_margin'] > 0 else None
    if row['p1_margin'] >= negative_margin_min and quotas['N_obvious'] > 0:
        return 'N_obvious'
    return None


def walk_draw(write=True, max_walk=8000, fetch=True):
    """Sequential seeded walk over the gold-pool candidate list (all years), fetching on demand, classifying each filing
    with the frozen passes and filling the strata until every quota is met. Equivalent to simple random sampling from the
    fully classified universe, without waiting for the complete download (implementation note A2.3a)."""
    if not is_frozen():
        raise RuntimeError('draw refused: classifier files are not frozen with their current hashes')
    if (GOLD_DIR / 'phase8b_gold_candidates.csv').exists() and write:
        raise RuntimeError('draw refused: a gold set already exists; it is drawn once')
    cand = pd.read_parquet(DERIVED / 'candidates.parquet')
    pool = cand[(cand['forms'] == '8-K') & cand['cik'].notna()].copy()
    pool = pool[~pool['accession'].map(cp.in_dev_pool)]
    rng = np.random.default_rng(G['seed'])
    order = pool.iloc[rng.permutation(len(pool))]
    half = G['H_pass_disagreement'] // 2
    quotas = dict(P_recent=G['P_recent_2013_2017'], P_early=G['P_early_2004_2012'], N_obvious=G['stratum_N_obvious_negative'], H_p1_only=half, H_p2_only=G['H_pass_disagreement'] - half,
                  H_low_margin=G['H_low_margin_or_unclassified'])
    agreement = json.loads((OUT / 'phase8b_pass_agreement.json').read_text(encoding='utf8'))
    neg_margin_min = float(agreement['negative_margin_median'])
    used, rows, walked, fetched_now, positives_seen = set(), [], 0, 0, 0
    for acc, cik in zip(order['accession'], order['cik']):
        if not any(quotas.values()) or walked >= max_walk:
            break
        walked += 1
        path = ed.FILINGS / acc[11:13] / f'{acc}.json.gz'
        if not path.exists():
            if not fetch:
                continue
            ed.fetch_submission(cik, acc); fetched_now += 1
            if not path.exists():
                continue
        rec = cp.build_record(path)
        if not rec or rec['form'] != '8-K' or rec['cik'] is None or rec['cik'] in used:
            continue
        p1, p2 = clf.pass1(rec), clf.pass2(rec)
        row = dict(accession=acc, cik=rec['cik'], company=rec['company'], filed=rec['filed'], year=rec['year'], form=rec['form'], items=rec['items'], dev_pool=False, p1_label=p1['label'],
                   p1_primary=p1['label'] in ('A', 'B'), p1_margin=p1['margin'], p1_rule=p1['rule'], p1_evidence=p1['evidence'][:500], p2_primary=p2['primary'], p2_score=p2['score'])
        positives_seen += int(row['p1_primary'])
        s = stratum_for(row, quotas, neg_margin_min)
        if s:
            quotas[s] -= 1; used.add(rec['cik']); rows.append(dict(row, stratum=s))
    gold = pd.DataFrame(rows)
    gold = gold.iloc[rng.permutation(len(gold))].reset_index(drop=True)
    gold['gold_id'] = [f'G{i + 1:03d}' for i in range(len(gold))]
    human, key = [], []
    for _, r in gold.iterrows():
        kp, wide, doc = context_for(r['accession'], r['p1_evidence'] if r['p1_primary'] else '')
        human.append(dict(gold_id=r['gold_id'], company=r['company'], filing_date=f"{r['filed'][:4]}-{r['filed'][4:6]}-{r['filed'][6:8]}", form=r['form'], items_8k=r['items'],
                          source_document=doc, key_passage=kp, wider_context=wide, human_label='', human_notes=''))
        key.append(dict(gold_id=r['gold_id'], accession=r['accession'], cik=int(r['cik']), year=int(r['year']), stratum=r['stratum'], p1_label=r['p1_label'], p1_primary=bool(r['p1_primary']),
                        p1_margin=float(r['p1_margin']), p1_rule=r['p1_rule'], p1_evidence=r['p1_evidence'], p2_primary=bool(r['p2_primary']), p2_score=float(r['p2_score'])))
    human, key = pd.DataFrame(human), pd.DataFrame(key)
    meta = dict(drawn_utc=datetime.now(timezone.utc).isoformat(), method='sequential seeded walk (A2.3a)', seed=G['seed'], classifier_version=clf.VERSION, n=int(len(gold)), strata=key['stratum'].value_counts().to_dict(),
                unfilled_quotas={k: v for k, v in quotas.items() if v}, gold_pool_size=int(len(pool)), walked=walked, fetched_on_demand=fetched_now, pass1_positives_seen_in_walk=positives_seen,
                negative_margin_min=neg_margin_min)
    if write:
        GOLD_DIR.mkdir(parents=True, exist_ok=True)
        human.to_csv(GOLD_DIR / 'phase8b_gold_candidates.csv', index=False, encoding='utf8')
        key.to_csv(GOLD_DIR / 'phase8b_gold_key_SEALED.csv', index=False, encoding='utf8')
        (GOLD_DIR / 'phase8b_gold_meta.json').write_text(json.dumps(meta, indent=1), encoding='utf8')
        for name in ('phase8b_gold_candidates.csv', 'phase8b_gold_key_SEALED.csv', 'phase8b_gold_meta.json'):
            p = GOLD_DIR / name
            log(dict(file=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), stage='gold set drawn (blinded; no human label exists)'))
    print(json.dumps(meta, indent=1))
    return human, key, meta


def finish_draw(human, key, gold, pool, pos, neg, low, write):
    meta = dict(drawn_utc=datetime.now(timezone.utc).isoformat(), seed=G['seed'], classifier_version=clf.VERSION, n=int(len(gold)), strata=key['stratum'].value_counts().to_dict(),
                pool_sizes=dict(gold_pool=int(len(pool)), p1_positives_recent=int((pos['year'] >= 2013).sum()), p1_positives_early=int((pos['year'] <= 2012).sum()), obvious_negatives=int(len(neg)),
                                p1_only=int((pool['p1_primary'] & ~pool['p2_primary']).sum()), p2_only=int((~pool['p1_primary'] & pool['p2_primary']).sum()), low_margin=int(len(low))))
    if write:
        GOLD_DIR.mkdir(parents=True, exist_ok=True)
        human.to_csv(GOLD_DIR / 'phase8b_gold_candidates.csv', index=False, encoding='utf8')
        key.to_csv(GOLD_DIR / 'phase8b_gold_key_SEALED.csv', index=False, encoding='utf8')
        (GOLD_DIR / 'phase8b_gold_meta.json').write_text(json.dumps(meta, indent=1), encoding='utf8')
        for name in ('phase8b_gold_candidates.csv', 'phase8b_gold_key_SEALED.csv', 'phase8b_gold_meta.json'):
            p = GOLD_DIR / name
            log(dict(file=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), stage='gold set drawn (blinded; no human label exists)'))
    print(json.dumps(meta, indent=1))
    return human, key, meta


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    {'freeze': freeze, 'classify': classify, 'draw': draw, 'walk_draw': walk_draw}.get(mode, lambda: print('usage: freeze|classify|draw|walk_draw'))()
