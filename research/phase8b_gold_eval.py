"""Phase 8B Amendment 2: score the frozen pass-1 classifier against the blinded human gold set and apply the frozen rule.

Headline = primary-class precision on stratum P (the random sample of predicted A/B filings): human NEW or INCREASED /
cases. PASS >= 0.95 with no systematic pattern; BORDERLINE 0.90 to < 0.95 (at most 15 targeted extra cases, then a
final verdict on the combined predicted positives); FAIL < 0.90. Systematic pattern = two or more predicted positives
labelled ROUTINE by the human, or two or more false positives produced by the same rule -> FAIL-or-repair.
The Clopper-Pearson interval is reported as uncertainty information, not as a criterion. A PASS appends the
'classifier gate passed' record that phase8b_backtest.py requires. Refuses to run until every gold row is labelled.
Usage (from research/): PYTHONUTF8=1 python phase8b_gold_eval.py
"""
from datetime import datetime, timezone
import hashlib
import json

import pandas as pd
from scipy import stats as sps

from phase6_lock import ROOT
import phase8b_edgar as ed

CFG = ed.CONFIG['amendment2']
RULE = CFG['decision_rule']
HUMAN = list(CFG['human_labels'])
POS_HUMAN = set(CFG['primary_positive_human'])
OUT = ROOT / 'research/phase8b'
GOLD_DIR = OUT / 'gold'
LABELED = GOLD_DIR / 'phase8b_gold_reference_FROZEN.csv'      # frozen and hashed before evaluation; never the live working file
REFERENCE_KIND = 'AI_ASSISTED_HUMAN_ADJUDICATED_REFERENCE_SET'
KEY = GOLD_DIR / 'phase8b_gold_key_SEALED.csv'
P1_TO_HUMAN = {'A': 'NEW', 'B': 'INCREASED', 'C': 'RENEWAL', 'D': 'ROUTINE', 'E': 'COMPLETED_HISTORICAL', 'F': 'ASR', 'G': 'COMPLETED_HISTORICAL', 'H': 'COMPLETED_HISTORICAL',
               'I': 'IRRELEVANT', 'J': 'SELF_TENDER', 'UNCLASSIFIED': 'AMBIGUOUS'}


def clopper_pearson(k, n, alpha=0.05):
    if n == 0:
        return (float('nan'), float('nan'))
    lo = 0.0 if k == 0 else float(sps.beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(sps.beta.ppf(1 - alpha / 2, k + 1, n - k))
    return (lo, hi)


def load(labeled=LABELED, key=KEY):
    lab = pd.read_csv(labeled, dtype=str).fillna(''); k = pd.read_csv(key, dtype=str).fillna('')
    df = lab.merge(k, on='gold_id', how='inner', validate='one_to_one')
    df['human_label'] = df['human_label'].str.strip().str.upper()
    bad = df[~df['human_label'].isin(HUMAN)]
    if len(bad):
        raise RuntimeError(f'{len(bad)} gold rows are unlabelled or carry an invalid label; evaluation refused until all are labelled')
    df['p1_primary'] = df['p1_primary'].str.lower() == 'true'
    df['human_primary'] = df['human_label'].isin(POS_HUMAN)
    return df


def precision_block(frame):
    n = int(len(frame)); k = int(frame['human_primary'].sum()); amb = int((frame['human_label'] == 'AMBIGUOUS').sum())
    lo, hi = clopper_pearson(k, n)
    return dict(n=n, correct=k, precision=k / n if n else None, ci95=[lo, hi], ambiguous=amb, precision_excluding_ambiguous=(k / (n - amb)) if n - amb else None)


def systematic(frame):
    fp = frame[frame['p1_primary'] & ~frame['human_primary']]
    routine = int((fp['human_label'] == 'ROUTINE').sum())
    same_rule = fp.groupby(['p1_rule', 'human_label']).size()
    repeated = {f'{r}|{h}': int(n) for (r, h), n in same_rule.items() if n >= RULE['systematic_same_rule_false_positives']}
    by_rule = fp.groupby('p1_rule').size()
    repeated_rule = {r: int(n) for r, n in by_rule.items() if n >= RULE['systematic_same_rule_false_positives']}
    flag = routine >= RULE['systematic_routine_as_positive'] or bool(repeated_rule)
    return dict(flag=bool(flag), routine_labelled_as_positive=routine, repeated_rule_false_positives=repeated_rule, repeated_rule_and_label=repeated)


def verdict(prec, syst):
    p = prec['precision']
    if p is None:
        return 'FAIL'
    if p < RULE['borderline_min']:
        return 'FAIL'
    if syst['flag']:
        return 'FAIL_OR_REPAIR'
    if p >= RULE['pass_precision_min']:
        return 'PASS'
    return 'BORDERLINE'


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float('nan'), float('nan'))
    ph = k / n; den = 1 + z * z / n; c = (ph + z * z / (2 * n)) / den; hw = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (c - hw, c + hw)


def kappa(a, b):
    a, b = list(a), list(b); n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    cats = set(a) | set(b); pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else None


def full_metrics(df):
    """All-60 descriptive metrics (the set is enriched by design, so these are not population estimates)."""
    pred = df['p1_label'].map(P1_TO_HUMAN); y = df['human_label']
    classes = HUMAN
    per = {}
    for c in classes:
        tp = int(((pred == c) & (y == c)).sum()); fp = int(((pred == c) & (y != c)).sum()); fn = int(((pred != c) & (y == c)).sum())
        pr = tp / (tp + fp) if tp + fp else None; rc = tp / (tp + fn) if tp + fn else None
        per[c] = dict(support=int((y == c).sum()), predicted=int((pred == c).sum()), precision=pr, recall=rc, f1=(2 * pr * rc / (pr + rc)) if pr and rc else None)
    hp, pp = df['human_primary'], df['p1_primary']
    tp, fp, fn, tn = int((pp & hp).sum()), int((pp & ~hp).sum()), int((~pp & hp).sum()), int((~pp & ~hp).sum())
    prec = tp / (tp + fp) if tp + fp else None; rec = tp / (tp + fn) if tp + fn else None
    binary = dict(tp=tp, fp=fp, fn=fn, tn=tn, precision=prec, recall=rec, f1=(2 * prec * rec / (prec + rec)) if prec and rec else None, specificity=tn / (tn + fp) if tn + fp else None,
                  error_rate=(fp + fn) / len(df), precision_cp95=list(clopper_pearson(tp, tp + fp)), precision_wilson95=list(wilson(tp, tp + fp)), recall_cp95=list(clopper_pearson(tp, tp + fn)))
    p2 = df['p2_primary'].str.lower() == 'true'
    second = dict(p1_vs_p2_agreement=float((pp == p2).mean()), p1_vs_p2_kappa=kappa(pp.tolist(), p2.tolist()), p1_vs_p2_disagreements=int((pp != p2).sum()),
                  p1_vs_reference_agreement=float((pp == hp).mean()), p1_vs_reference_kappa=kappa(pp.tolist(), hp.tolist()),
                  p2_vs_reference_agreement=float((p2 == hp).mean()), p2_vs_reference_kappa=kappa(p2.tolist(), hp.tolist()),
                  p2_binary=dict(tp=int((p2 & hp).sum()), fp=int((p2 & ~hp).sum()), fn=int((~p2 & hp).sum()), tn=int((~p2 & ~hp).sum())),
                  both_passes_positive=dict(n=int((pp & p2).sum()), reference_positive=int((pp & p2 & hp).sum())),
                  p1_only_positive=dict(n=int((pp & ~p2).sum()), reference_positive=int((pp & ~p2 & hp).sum())),
                  p2_only_positive=dict(n=int((~pp & p2).sum()), reference_positive=int((~pp & p2 & hp).sum())),
                  disagreement_reference_labels=df[pp != p2]['human_label'].value_counts().to_dict())
    fp_df = df[pp & ~hp]
    confusion_modes = dict(routine_as_authorisation=int((fp_df['human_label'] == 'ROUTINE').sum()), historical_or_completed_as_authorisation=int((fp_df['human_label'] == 'COMPLETED_HISTORICAL').sum()),
                           asr_as_authorisation=int((fp_df['human_label'] == 'ASR').sum()), irrelevant_as_authorisation=int((fp_df['human_label'] == 'IRRELEVANT').sum()),
                           renewal_as_authorisation=int((fp_df['human_label'] == 'RENEWAL').sum()), tender_as_authorisation=int((fp_df['human_label'] == 'SELF_TENDER').sum()),
                           ambiguous_among_predicted_positive=int((fp_df['human_label'] == 'AMBIGUOUS').sum()))
    return dict(n=int(len(df)), accuracy_9class=float((pred == y).mean()), per_class=per, binary_tradable_all60=binary, second_pass=second, false_positive_modes=confusion_modes,
                new_vs_increased_among_true_positives=pd.crosstab(df[pp & hp]['human_label'], df[pp & hp]['p1_label']).to_dict())


def evaluate(df):
    P = df[df['stratum'].str.startswith('P_')]
    head = precision_block(P)
    syst = systematic(P)
    ext = df[df['stratum'].str.startswith('X_')]           # borderline extension cases, if any
    combined = precision_block(pd.concat([P, ext])) if len(ext) else None
    final_prec = combined or head
    pred = df['p1_label'].map(P1_TO_HUMAN)
    cm = pd.crosstab(df['human_label'], pred.rename('pass1'), dropna=False)
    tp = int((df['p1_primary'] & df['human_primary']).sum()); fp = int((df['p1_primary'] & ~df['human_primary']).sum()); fn = int((~df['p1_primary'] & df['human_primary']).sum())
    pooled = dict(n=int(len(df)), tp=tp, fp=fp, fn=fn, precision=tp / (tp + fp) if tp + fp else None, recall=tp / (tp + fn) if tp + fn else None,
                  note='pooled over all strata; the set is enriched with predicted positives and hard cases, so pooled recall and F1 are descriptive only')
    pooled['f1'] = (2 * pooled['precision'] * pooled['recall'] / (pooled['precision'] + pooled['recall'])) if pooled['precision'] and pooled['recall'] else None
    rep = dict(evaluated_utc=datetime.now(timezone.utc).isoformat(), reference_kind=REFERENCE_KIND, reference_sha256=hashlib.sha256(LABELED.read_bytes()).hexdigest(), full=full_metrics(df), headline_stratum_P=head, by_period={k: precision_block(g) for k, g in P.groupby('stratum')}, combined_with_extension=combined,
               systematic=systematic(pd.concat([P, ext])) if len(ext) else syst, verdict=verdict(final_prec, systematic(pd.concat([P, ext])) if len(ext) else syst), pooled=pooled,
               by_stratum={k: dict(n=int(len(g)), human_primary=int(g['human_primary'].sum()), p1_primary=int(g['p1_primary'].sum()), p2_primary=int((g['p2_primary'].str.lower() == 'true').sum())) for k, g in df.groupby('stratum')},
               pass2_precision_on_its_positives=precision_block(df[df['p2_primary'].str.lower() == 'true']), confusion=cm.to_dict(),
               false_positives=df[df['p1_primary'] & ~df['human_primary']][['gold_id', 'accession', 'stratum', 'human_label', 'p1_label', 'p1_rule', 'p1_margin', 'p1_evidence']].to_dict('records'),
               false_negatives=df[~df['p1_primary'] & df['human_primary']][['gold_id', 'accession', 'stratum', 'human_label', 'p1_label', 'p1_rule', 'p1_evidence']].to_dict('records'))
    return rep


def write_report(rep):
    (OUT / 'phase8b_gold_validation.json').write_text(json.dumps(rep, indent=1, default=str), encoding='utf8')
    h = rep['headline_stratum_P']
    lines = ['# PHASE8B_GOLD_VALIDATION - frozen pass-1 classifier against the 60-case reference set (Amendment 2)', '', f"Evaluated {rep['evaluated_utc']}. Reference: **{rep['reference_kind']}** (sha256 {rep['reference_sha256']}): labels entered by the human owner, who consulted an independent LLM on a substantial number of difficult cases. It is NOT a fully independent unaided human gold standard; precision below is measured against a human-entered, AI-assisted adjudicated sample.", '',
             f"## Verdict: **{rep['verdict']}**", '',
             f"Headline (stratum P, random sample of predicted NEW/INCREASED): {h['correct']} / {h['n']} = {h['precision']:.3f}; exact 95% interval [{h['ci95'][0]:.3f}, {h['ci95'][1]:.3f}] (uncertainty information, not a criterion); human AMBIGUOUS among them: {h['ambiguous']} (precision excluding them: {h['precision_excluding_ambiguous']:.3f}).",
             f"By period: {json.dumps({k: [v['correct'], v['n']] for k, v in rep['by_period'].items()})}.",
             f"Systematic-error check: {json.dumps(rep['systematic'])}.", f"Pooled 60-case figures (descriptive only): {json.dumps({k: v for k, v in rep['pooled'].items() if k != 'note'})}. {rep['pooled']['note']}.",
             f"Strata: {json.dumps(rep['by_stratum'])}.", '', '## False positives', ''] + [f"- {r['gold_id']} ({r['accession']}, {r['stratum']}): human {r['human_label']}, pass 1 {r['p1_label']} via `{r['p1_rule']}`: {r['p1_evidence'][:240]}" for r in rep['false_positives']] + \
            ['', '## False negatives', ''] + [f"- {r['gold_id']} ({r['accession']}, {r['stratum']}): human {r['human_label']}, pass 1 {r['p1_label']} via `{r['p1_rule']}`" for r in rep['false_negatives']]
    (OUT / 'PHASE8B_GOLD_VALIDATION.md').write_text('\n'.join(lines) + '\n', encoding='utf8')


def main():
    rep = evaluate(load())
    write_report(rep)
    log = OUT / 'PHASE8B_FREEZE_HASHES.jsonl'
    rec = dict(file='research/phase8b/phase8b_gold_validation.json', sha256=hashlib.sha256((OUT / 'phase8b_gold_validation.json').read_bytes()).hexdigest(), frozen_utc=rep['evaluated_utc'],
               stage=('classifier gate passed (Amendment 2 gold validation: PASS)' if rep['verdict'] == 'PASS' else f"gold validation verdict {rep['verdict']} (return stage stays locked)"))
    with open(log, 'a', encoding='utf8') as fh:
        fh.write(json.dumps(rec) + '\n')
    print(rep['verdict'], rep['headline_stratum_P'])
    return rep


if __name__ == '__main__':
    main()
