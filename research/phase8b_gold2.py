"""Phase 8B Amendment 3 (A3.6-A3.7): freeze the repaired classifier v1.8 and draw the FRESH 15-case blind validation set.

Order of operations is enforced, exactly as in Amendment 2:
  freeze -> records SHA-256 of phase8b_classifier.py, phase8b_corpus.py and phase8b_display.py as
            'classifier frozen (Amendment 3; version 1.8 ...)'. No classifier change is permitted afterwards.
  draw   -> refuses unless the frozen hashes match the files on disk; walks the candidate list in seeded random order,
            fetching on demand, classifying with the frozen v1.8 passes, and fills two quotas of predicted positives
            (8 from 2013-2017, 7 from 2004-2012), one per issuer.

Excluded from the fresh pool: the development pool, all 60 original gold accessions AND their CIKs, the superseded
v1.5 premature draw, and the 240-row / 90-row labelling packages that were distributed to the human.

Every drawn case must pass the A3.4 preflight `classifier_evidence_visible == True`: the default visible passage is
built by phase8b_display around the classifier's own evidence sentence (that sentence plus one neighbour each side).
A case that fails the assertion is skipped and counted, never shown.

The human CSV carries text only - no predicted label, margin, rule, stratum or score. Those live in the sealed key.
No prices, no returns, no locked data.

Usage (from research/): PYTHONUTF8=1 python phase8b_gold2.py freeze|draw|preflight
"""
from datetime import datetime, timezone
import hashlib
import json
import sys

import numpy as np
import pandas as pd

from phase6_lock import ROOT
import phase8b_classifier as clf
import phase8b_corpus as cp
import phase8b_display as disp
import phase8b_edgar as ed
from phase8b_lock import guard_filed_date

OUT = ROOT / 'research/phase8b'
GOLD2 = OUT / 'gold2'
HASH_LOG = OUT / 'PHASE8B_FREEZE_HASHES.jsonl'
CLASSIFIER_FILES = ['research/phase8b_classifier.py', 'research/phase8b_corpus.py', 'research/phase8b_display.py']
FREEZE_STAGE = 'classifier frozen (Amendment 3; version 1.8; repaired on the development pool only; the v1.7 FAIL stands)'

SEED = 20260923                      # A3.7: 20260920 + 3
N_RECENT = 8                         # 2013-2017
N_EARLY = 7                          # 2004-2012
RECENT_FROM = 2013
MAX_WALK = 40000


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def log(rec):
    rec.setdefault('frozen_utc', datetime.now(timezone.utc).isoformat())
    with open(HASH_LOG, 'a', encoding='utf8') as fh:
        fh.write(json.dumps(rec) + '\n')


def frozen_hashes():
    out = {}
    for line in HASH_LOG.read_text(encoding='utf8').splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get('stage', '').startswith('classifier frozen (Amendment 3'):
            out[r['file']] = r['sha256']
    return out


def is_frozen():
    fz = frozen_hashes()
    return bool(fz) and all(fz.get(f) == sha(f) for f in CLASSIFIER_FILES)


def freeze():
    if clf.VERSION != '1.8':
        raise RuntimeError(f'expected classifier version 1.8, found {clf.VERSION}')
    for f in CLASSIFIER_FILES:
        log(dict(file=f, sha256=sha(f), stage=FREEZE_STAGE))
    print('frozen (Amendment 3):')
    for f in CLASSIFIER_FILES:
        print(f'  {f}  {sha(f)}')


# ------------------------------------------------------------------ exclusions
def excluded():
    """(accessions, ciks) that may not appear in the fresh set: everything a human has already been shown, plus the
    original gold issuers."""
    acc, cik = set(), set()
    k = pd.read_csv(OUT / 'gold/phase8b_gold_key_SEALED.csv', dtype=str)
    acc |= set(k['accession']); cik |= {int(c) for c in k['cik']}
    sup = OUT / 'gold/superseded_v1.5_premature/phase8b_gold_key_SEALED.csv'
    if sup.exists():
        s = pd.read_csv(sup, dtype=str)
        acc |= set(s['accession']); cik |= {int(c) for c in s['cik']}
    for name in ('phase8b_labeling_candidates.csv', 'phase8b_retrieval_audit_candidates.csv'):
        p = OUT / name
        if p.exists():
            acc |= set(pd.read_csv(p, dtype=str)['accession'])
    return acc, cik


def draw(write=True, max_walk=MAX_WALK, fetch=True):
    if not is_frozen():
        raise RuntimeError('draw refused: classifier files are not frozen with their current hashes (run freeze first)')
    if (GOLD2 / 'phase8b_gold2_candidates.csv').exists() and write:
        raise RuntimeError('draw refused: a fresh validation set already exists; it is drawn once')
    ex_acc, ex_cik = excluded()
    cand = pd.read_parquet(ed.DERIVED / 'candidates.parquet')
    pool = cand[(cand['forms'] == '8-K') & cand['cik'].notna()].copy()
    pool = pool[~pool['accession'].isin(ex_acc)]
    pool = pool[~pool['accession'].map(cp.in_dev_pool)]
    rng = np.random.default_rng(SEED)
    order = pool.iloc[rng.permutation(len(pool))]
    quotas = {'P_recent': N_RECENT, 'P_early': N_EARLY}
    used, rows = set(ex_cik), []
    walked = fetched = positives = skipped_invisible = 0
    for acc, cik in zip(order['accession'], order['cik']):
        if not any(quotas.values()) or walked >= max_walk:
            break
        walked += 1
        path = ed.FILINGS / acc[11:13] / f'{acc}.json.gz'
        if not path.exists():
            if not fetch:
                continue
            ed.fetch_submission(cik, acc); fetched += 1
            if not path.exists():
                continue
        rec = cp.build_record(path)
        if not rec or rec['form'] != '8-K' or rec['cik'] is None or rec['cik'] in used:
            continue
        guard_filed_date(rec['filed'])
        p1 = clf.pass1(rec)
        if p1['label'] not in ('A', 'B'):
            continue
        positives += 1
        stratum = 'P_recent' if rec['year'] >= RECENT_FROM else 'P_early'
        if quotas[stratum] <= 0:
            continue
        built = disp.evidence_passage(acc, p1['evidence'])
        if not built['visible']:                      # A3.4: never show a case whose evidence we cannot display
            skipped_invisible += 1
            continue
        disp.assert_evidence_visible(acc, p1['evidence'], built=built)
        p2 = clf.pass2(rec)
        quotas[stratum] -= 1; used.add(rec['cik'])
        rows.append(dict(accession=acc, cik=rec['cik'], company=rec['company'], filed=rec['filed'], year=rec['year'],
                         form=rec['form'], items=rec['items'], stratum=stratum, p1_label=p1['label'],
                         p1_margin=p1['margin'], p1_rule=p1['rule'], p1_evidence=p1['evidence'],
                         p2_primary=p2['primary'], p2_score=p2['score'], source_document=built['document'],
                         key_passage=built['passage'], wider_context=built['wider_context'],
                         n_sentences=len(built['sentences'])))
    if any(quotas.values()):
        raise RuntimeError(f'draw incomplete: unfilled quotas {quotas} after walking {walked} candidates')
    g = pd.DataFrame(rows)
    g = g.iloc[rng.permutation(len(g))].reset_index(drop=True)
    g['gold2_id'] = [f'F{i + 1:03d}' for i in range(len(g))]

    human = g[['gold2_id', 'company', 'form', 'items', 'source_document', 'key_passage', 'wider_context']].copy()
    human.insert(2, 'filing_date', [f'{d[:4]}-{d[4:6]}-{d[6:8]}' for d in g['filed']])
    human = human.rename(columns={'items': 'items_8k'})
    human['human_label'] = ''
    human['human_notes'] = ''
    key = g[['gold2_id', 'accession', 'cik', 'year', 'stratum', 'p1_label', 'p1_margin', 'p1_rule', 'p1_evidence',
             'p2_primary', 'p2_score', 'n_sentences']].copy()
    meta = dict(drawn_utc=datetime.now(timezone.utc).isoformat(), amendment=3, method='sequential seeded walk (A2.3a) over the non-development, never-shown pool',
                seed=SEED, classifier_version=clf.VERSION, classifier_sha256={f: sha(f) for f in CLASSIFIER_FILES},
                n=int(len(g)), strata=key['stratum'].value_counts().to_dict(), pool_size=int(len(pool)),
                excluded_accessions=len(ex_acc), excluded_ciks=len(ex_cik), walked=walked, fetched_on_demand=fetched,
                pass1_positives_seen=positives, skipped_evidence_not_visible=skipped_invisible,
                preflight='classifier_evidence_visible == True for every drawn case (A3.4)')
    if write:
        GOLD2.mkdir(parents=True, exist_ok=True)
        human.to_csv(GOLD2 / 'phase8b_gold2_candidates.csv', index=False, encoding='utf8')
        key.to_csv(GOLD2 / 'phase8b_gold2_key_SEALED.csv', index=False, encoding='utf8')
        (GOLD2 / 'phase8b_gold2_meta.json').write_text(json.dumps(meta, indent=1), encoding='utf8')
        for name in ('phase8b_gold2_candidates.csv', 'phase8b_gold2_key_SEALED.csv', 'phase8b_gold2_meta.json'):
            p = GOLD2 / name
            log(dict(file=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                     stage='fresh 15-case validation set drawn (Amendment 3; blinded; no human label exists)'))
    print(json.dumps(meta, indent=1))
    return human, key, meta


def preflight():
    """Re-verify A3.4 on the written set: every case's stored passage must contain the classifier evidence verbatim."""
    human = pd.read_csv(GOLD2 / 'phase8b_gold2_candidates.csv', dtype=str).fillna('')
    key = pd.read_csv(GOLD2 / 'phase8b_gold2_key_SEALED.csv', dtype=str).fillna('')
    df = human.merge(key, on='gold2_id', validate='one_to_one')
    checks = []
    for _, r in df.iterrows():
        vis = disp.contains(r['key_passage'], r['p1_evidence'])
        checks.append(dict(gold2_id=r['gold2_id'], classifier_evidence_visible=bool(vis),
                           passage_chars=len(r['key_passage']), sentences=int(r['n_sentences'])))
        assert vis, f"classifier_evidence_visible == False for {r['gold2_id']} (A3.4 refuses this case)"
    leak = [c for c in human.columns if c in ('p1_label', 'p1_rule', 'p1_margin', 'stratum', 'p2_primary', 'p2_score', 'p1_evidence')]
    assert not leak, f'human CSV leaks classifier output: {leak}'
    rep = dict(checked_utc=datetime.now(timezone.utc).isoformat(), n=len(checks), all_visible=all(c['classifier_evidence_visible'] for c in checks),
               human_csv_columns=list(human.columns), prediction_columns_in_human_csv=leak, cases=checks)
    (OUT / 'phase8b_gold2_preflight.json').write_text(json.dumps(rep, indent=1), encoding='utf8')
    print(json.dumps({k: v for k, v in rep.items() if k != 'cases'}, indent=1))
    print(f"evidence visible in {sum(c['classifier_evidence_visible'] for c in checks)} / {len(checks)} cases")
    return rep


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    {'freeze': freeze, 'draw': draw, 'preflight': preflight}.get(mode, lambda: print('usage: freeze|draw|preflight'))()
