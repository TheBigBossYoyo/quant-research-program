"""Phase 8B classifier evaluation harness (frozen before any label exists; preregistration section 5).

Reads human labels from phase8b_labeling_candidates.csv joined to the frozen split, applies a classifier callable to
DEV or HOLDOUT rows, and reports precision / recall / F1 for the primary A-or-B signal (raw and stratum-weighted),
per-class metrics, the confusion matrix, support, Wilson intervals, and the frozen gate. HOLDOUT may be evaluated
only through `evaluate_holdout`, which records the evaluation in PHASE8B_FREEZE_HASHES.jsonl; the classifier code
hash must already be recorded there (asserted).
"""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from phase6_lock import ROOT
import phase8b_edgar as ed

OUT = ROOT / 'research/phase8b'
CLASSES = list('ABCDEFGHIJ')       # J (self-tender) added by Amendment 1 before any label existed; never a primary positive
POSITIVE = set(ed.CONFIG['labels']['primary_positive'])
GATE = ed.CONFIG['labels']['classifier_gate']


def wilson(k, n, z=1.96):
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n; den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den; half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (centre - half, centre + half)


def load_labels(path=OUT / 'phase8b_labeling_candidates.csv', split_path=OUT / 'phase8b_label_split.csv', _allow_holdout=False):
    """Human labels (rows with a non-empty human_label) joined to the frozen split. Raises if labels are not A-I.
    HOLDOUT rows have their label blanked unless called from `evaluate_holdout` (development code never sees them)."""
    lab = pd.read_csv(path, dtype=str).fillna('')
    split = pd.read_csv(split_path, dtype=str)
    df = lab.merge(split[['accession', 'stratum', 'split', 'year']], on='accession', how='left', validate='one_to_one')
    df['human_label'] = df['human_label'].str.strip().str.upper()
    bad = df[(df['human_label'] != '') & ~df['human_label'].isin(CLASSES)]
    if len(bad):
        raise ValueError(f'labels outside A-J: {bad[["accession", "human_label"]].to_dict("records")}')
    if not _allow_holdout:
        df.loc[df['split'] == 'HOLDOUT', ['human_label', 'human_notes']] = ''
    return df


def labelled(df, split):
    d = df[(df['split'] == split) & (df['human_label'] != '')]
    return d


def binary_metrics(y_true, y_pred, weights=None):
    """Precision/recall/F1 for A-or-B with optional per-row weights (stratum weights)."""
    t = np.asarray([x in POSITIVE for x in y_true]); p = np.asarray([x in POSITIVE for x in y_pred])
    w = np.ones(len(t)) if weights is None else np.asarray(weights, dtype=float)
    tp = float(w[t & p].sum()); fp = float(w[~t & p].sum()); fn = float(w[t & ~p].sum()); tn = float(w[~t & ~p].sum())
    prec = tp / (tp + fp) if tp + fp > 0 else float('nan'); rec = tp / (tp + fn) if tp + fn > 0 else float('nan')
    f1 = 2 * prec * rec / (prec + rec) if prec + rec > 0 and not (math.isnan(prec) or math.isnan(rec)) else float('nan')
    return dict(tp=tp, fp=fp, fn=fn, tn=tn, precision=prec, recall=rec, f1=f1, predicted_positives=int((p).sum()), true_positives_in_sample=int(t.sum()))


def confusion(y_true, y_pred):
    labels = CLASSES + ['UNCLASSIFIED']
    cm = pd.DataFrame(0, index=labels, columns=labels)
    for a, b in zip(y_true, y_pred):
        cm.loc[a if a in labels else 'UNCLASSIFIED', b if b in labels else 'UNCLASSIFIED'] += 1
    return cm


def per_class(y_true, y_pred):
    out = {}
    for k in CLASSES + ['UNCLASSIFIED']:
        t = np.asarray([x == k for x in y_true]); p = np.asarray([x == k for x in y_pred])
        tp = int((t & p).sum()); fp = int((~t & p).sum()); fn = int((t & ~p).sum())
        out[k] = dict(support=int(t.sum()), predicted=int(p.sum()), precision=tp / (tp + fp) if tp + fp else None, recall=tp / (tp + fn) if tp + fn else None)
    return out


def gate_check(raw, weighted):
    k = int(raw['tp']); n = int(raw['tp'] + raw['fp'])
    lo, hi = wilson(k, n)
    checks = dict(precision_weighted_ge_min=bool(weighted['precision'] >= GATE['precision_min']) if not math.isnan(weighted['precision']) else False,
                  predicted_positives_ge_min=n >= GATE['min_predicted_positives_holdout'], wilson_lower_ge_min=bool(lo >= GATE['wilson95_lower_min']) if not math.isnan(lo) else False)
    return dict(checks=checks, passed=all(checks.values()), wilson95=[lo, hi], recall_flag_investigate=bool(raw['recall'] < GATE['recall_investigate_below']) if not math.isnan(raw['recall']) else None)


def evaluate(df, classify, stratum_weights):
    """`classify(accession) -> label`; `stratum_weights` {stratum: population/sample}. Returns a report dict."""
    preds = [classify(a) for a in df['accession']]
    y = list(df['human_label'])
    w = [stratum_weights.get(s, 1.0) for s in df['stratum']]
    raw = binary_metrics(y, preds); wt = binary_metrics(y, preds, w)
    cm = confusion(y, preds)
    fps = df.loc[[(yy not in POSITIVE) and (pp in POSITIVE) for yy, pp in zip(y, preds)], ['accession', 'human_label']].assign(pred=[p for yy, p in zip(y, preds) if (yy not in POSITIVE) and (p in POSITIVE)])
    fns = df.loc[[(yy in POSITIVE) and (pp not in POSITIVE) for yy, pp in zip(y, preds)], ['accession', 'human_label']].assign(pred=[p for yy, p in zip(y, preds) if (yy in POSITIVE) and (p not in POSITIVE)])
    return dict(n=int(len(df)), raw=raw, weighted=wt, gate=gate_check(raw, wt), per_class=per_class(y, preds), confusion=cm.to_dict(),
                by_stratum={s: binary_metrics(list(g['human_label']), [classify(a) for a in g['accession']]) for s, g in df.groupby('stratum')},
                false_positives=fps.to_dict('records'), false_negatives=fns.to_dict('records'))


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classifier_frozen(hash_log=OUT / 'PHASE8B_FREEZE_HASHES.jsonl', classifier_files=()):
    """True when every file in `classifier_files` has a 'classifier frozen' record whose SHA256 equals its current content."""
    recs = [json.loads(l) for l in hash_log.read_text(encoding='utf8').splitlines() if l.strip()]
    frozen = {r.get('file'): r.get('sha256') for r in recs if r.get('stage', '').startswith('classifier frozen')}
    if not frozen:
        return False
    for f in classifier_files:
        rel = Path(f).resolve().relative_to(ROOT.resolve()).as_posix() if Path(f).is_absolute() else str(f).replace('\\', '/')
        if frozen.get(rel) != sha256_file(ROOT / rel):
            return False
    return True


def evaluate_holdout(classify, stratum_weights, classifier_files, hash_log=OUT / 'PHASE8B_FREEZE_HASHES.jsonl'):
    """One-shot HOLDOUT evaluation: refuses to run unless every classifier file's current SHA256 matches its
    'classifier frozen' record, refuses a second run, and logs the evaluation."""
    if not classifier_files or not classifier_frozen(hash_log, classifier_files):
        raise RuntimeError('HOLDOUT evaluation refused: classifier files are not recorded as frozen with their current hashes')
    recs = [json.loads(l) for l in hash_log.read_text(encoding='utf8').splitlines() if l.strip()]
    if any(r.get('stage') == 'holdout evaluated' for r in recs):
        raise RuntimeError('HOLDOUT was already evaluated once; a second evaluation is not permitted')
    df = labelled(load_labels(_allow_holdout=True), 'HOLDOUT')
    rep = evaluate(df, classify, stratum_weights)
    rep['evaluated_utc'] = datetime.now(timezone.utc).isoformat()
    (OUT / 'phase8b_classifier_holdout.json').write_text(json.dumps(rep, indent=1, default=float), encoding='utf8')
    with open(hash_log, 'a', encoding='utf8') as fh:
        fh.write(json.dumps(dict(file='research/phase8b/phase8b_classifier_holdout.json', sha256=hashlib.sha256((OUT / 'phase8b_classifier_holdout.json').read_bytes()).hexdigest(),
                                 frozen_utc=rep['evaluated_utc'], stage='holdout evaluated')) + '\n')
    return rep
