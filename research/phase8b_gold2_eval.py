"""Phase 8B Amendment 3 (A3.8): score the frozen v1.8 classifier against the FRESH 15-case blind validation set.

Written and hashed BEFORE any fresh label existed. The decision rule is not a parameter of this script.

Measured quantity (A3.9): precision on the primary tradable superclass NEW + INCREASED -
    "when the repaired classifier says a filing is a new or increased issuer share-repurchase authorisation,
     how often is that actually true?"
All 15 cases are predicted positives, so the headline is simply how many the human calls NEW or INCREASED.

    15 / 15  -> PASS for DEVELOPMENT use, provided no systematic semantic error is present
    14 / 15  -> BORDERLINE: report the single error and STOP for a user decision; a new systematic failure mode -> FAIL
    <= 13/15 -> FAIL

n = 15 is deliberately small. The Clopper-Pearson interval is printed as uncertainty information and is NOT a
criterion. The original 60 cases are NEVER pooled into this estimate; they are reported separately, marked as seen.
NEW-vs-INCREASED subclass confusion is reported but does not affect the verdict (the preregistered strategy trades the
A/B superclass and does not distinguish them).

A PASS appends the 'classifier gate passed' record that phase8b_backtest.py requires; nothing else does.
Refuses to run until every one of the 15 rows is labelled.

Usage (from research/): PYTHONUTF8=1 python phase8b_gold2_eval.py
"""
from datetime import datetime, timezone
import hashlib
import json

import pandas as pd
from scipy import stats as sps

from phase6_lock import ROOT
import phase8b_edgar as ed
import phase8b_gold2 as g2

CFG = ed.CONFIG['amendment2']
HUMAN = list(CFG['human_labels'])
POS_HUMAN = set(CFG['primary_positive_human'])            # {'NEW', 'INCREASED'}
OUT = ROOT / 'research/phase8b'
GOLD2 = OUT / 'gold2'
LABELED = GOLD2 / 'phase8b_gold2_reference_FROZEN.csv'      # frozen and hashed before evaluation; never the live working file
KEY = GOLD2 / 'phase8b_gold2_key_SEALED.csv'
REFERENCE_KIND = 'FRESH_BLIND_TO_CLASSIFIER_AI_ASSISTED_HUMAN_ADJUDICATION'
REFERENCE_NOTE = ("Labels entered by the human owner while blind to the repaired classifier's predictions, with the "
                  'classifier evidence sentence visible (A3.4). The owner consulted an independent LLM to interpret '
                  'filing passages. This is NOT unaided independent human annotation.')

PASS_MIN = 15               # A3.8, frozen
BORDERLINE_MIN = 14
N_EXPECTED = 15


def clopper_pearson(k, n, alpha=0.05):
    if n == 0:
        return (float('nan'), float('nan'))
    lo = 0.0 if k == 0 else float(sps.beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(sps.beta.ppf(1 - alpha / 2, k + 1, n - k))
    return (lo, hi)


def load():
    lab = pd.read_csv(LABELED, dtype=str).fillna('')
    key = pd.read_csv(KEY, dtype=str).fillna('')
    df = lab.merge(key, on='gold2_id', how='inner', validate='one_to_one')
    if len(df) != N_EXPECTED:
        raise RuntimeError(f'expected {N_EXPECTED} fresh cases, found {len(df)}')
    df['human_label'] = df['human_label'].str.strip().str.upper()
    bad = df[~df['human_label'].isin(HUMAN)]
    if len(bad):
        raise RuntimeError(f"{len(bad)} fresh rows are unlabelled or carry an invalid label "
                           f"({sorted(set(bad['gold2_id']))}); evaluation refused until all {N_EXPECTED} are labelled")
    df['human_primary'] = df['human_label'].isin(POS_HUMAN)
    if not (df['p1_label'].isin(['A', 'B'])).all():
        raise RuntimeError('the fresh set must contain only predicted positives')
    return df


def systematic(df):
    """With n = 15 a 'systematic' pattern is a repeat of a known confusion mode, not a count threshold."""
    fp = df[~df['human_primary']]
    routine = int((fp['human_label'] == 'ROUTINE').sum())
    by_rule = fp.groupby('p1_rule').size().to_dict()
    modes = fp['human_label'].value_counts().to_dict()
    repeated = {r: int(n) for r, n in by_rule.items() if n >= 2}
    flag = bool(routine >= 2 or repeated)
    return dict(flag=flag, n_false_positives=int(len(fp)), routine_labelled_as_positive=routine,
                false_positive_labels=modes, false_positives_by_rule={k: int(v) for k, v in by_rule.items()},
                repeated_rule_false_positives=repeated,
                note='a single non-systematic error is BORDERLINE under A3.8 and stops for a user decision')


def verdict(correct, n, syst):
    if n != N_EXPECTED:
        return 'INVALID'
    if correct >= PASS_MIN:
        return 'FAIL' if syst['flag'] else 'PASS'
    if correct >= BORDERLINE_MIN:
        return 'FAIL' if syst['flag'] else 'BORDERLINE'
    return 'FAIL'


def prior_run_reference():
    """The original 60 cases, reported SEPARATELY and marked as seen. Never pooled into the fresh estimate."""
    p = OUT / 'phase8b_gold_validation.json'
    if not p.exists():
        return None
    old = json.loads(p.read_text(encoding='utf8'))
    return dict(status='SEEN - reported separately, never pooled (A3.8)',
                frozen_v17_verdict='CLASSIFIER_VALIDATION_FAILED_AS_MEASURED',
                frozen_v17_stratum_P=f"{old['headline_stratum_P']['correct']}/{old['headline_stratum_P']['n']}",
                frozen_v17_precision=old['headline_stratum_P']['precision'])


def evaluate(df):
    n = int(len(df)); correct = int(df['human_primary'].sum())
    lo, hi = clopper_pearson(correct, n)
    syst = systematic(df)
    v = verdict(correct, n, syst)
    sub = pd.crosstab(df[df['human_primary']]['human_label'], df[df['human_primary']]['p1_label'])
    errors = df[~df['human_primary']][['gold2_id', 'accession', 'stratum', 'human_label', 'p1_label', 'p1_rule',
                                       'p1_margin', 'p1_evidence', 'human_notes']].to_dict('records')
    return dict(
        evaluated_utc=datetime.now(timezone.utc).isoformat(), amendment=3, reference_kind=REFERENCE_KIND,
        reference_sha256=hashlib.sha256(LABELED.read_bytes()).hexdigest(), reference_note=REFERENCE_NOTE,
        classifier_version='1.8', classifier_sha256={f: g2.sha(f) for f in g2.CLASSIFIER_FILES},
        headline=dict(measure='precision on the NEW+INCREASED superclass (A3.9)', correct=correct, n=n,
                      precision=correct / n, ci95_clopper_pearson=[lo, hi],
                      ci_note='uncertainty information only; NOT a criterion (A3.8)'),
        by_period={k: dict(correct=int(g['human_primary'].sum()), n=int(len(g))) for k, g in df.groupby('stratum')},
        verdict=v, systematic=syst, errors=errors,
        subclass_new_vs_increased=sub.to_dict(),
        subclass_note='reported only; the preregistered strategy trades the A/B superclass and does not separate them',
        human_label_counts=df['human_label'].value_counts().to_dict(),
        pass2_agreement=dict(n_pass2_positive=int((df['p2_primary'].str.lower() == 'true').sum()),
                             of_which_reference_positive=int(((df['p2_primary'].str.lower() == 'true') & df['human_primary']).sum())),
        prior_run=prior_run_reference(),
        returns_status='LOCKED unless the verdict is PASS; validation 2018-2021 and holdout 2022-2026 untouched')


def write_report(rep):
    (OUT / 'phase8b_gold2_validation.json').write_text(json.dumps(rep, indent=1, default=str), encoding='utf8')
    h = rep['headline']
    lines = [
        '# PHASE8B_GOLD2_VALIDATION - repaired classifier v1.8 against the fresh 15-case blind set (Amendment 3)', '',
        f"Evaluated {rep['evaluated_utc']}. Reference: **{rep['reference_kind']}** (sha256 {rep['reference_sha256']}).",
        'Every case is a predicted positive drawn blind from the never-shown pool; the labeller saw the classifier\'s own',
        'evidence sentence with one sentence each side (A3.4), so this measurement is not affected by the display defect',
        'that invalidated the first run as an estimate of the repaired classifier.', '',
        f"## Verdict: **{rep['verdict']}**", '',
        f"Headline (NEW+INCREASED superclass precision): {h['correct']} / {h['n']} = {h['precision']:.3f}; "
        f"exact 95% interval [{h['ci95_clopper_pearson'][0]:.3f}, {h['ci95_clopper_pearson'][1]:.3f}] "
        f"(uncertainty information, not a criterion).",
        f"By period: {json.dumps({k: [v['correct'], v['n']] for k, v in rep['by_period'].items()})}.",
        f"Human labels: {json.dumps(rep['human_label_counts'])}.",
        f"Systematic-error check: {json.dumps(rep['systematic'])}.", '',
        '## Errors', '']
    lines += ([f"- {e['gold2_id']} ({e['accession']}, {e['stratum']}): human {e['human_label']}, pass 1 "
               f"{e['p1_label']} via `{e['p1_rule']}` (margin {e['p1_margin']}): {e['p1_evidence'][:240]}"
               for e in rep['errors']] or ['- none'])
    lines += ['', '## Prior run (seen; reported separately, never pooled)', '',
              f"- {json.dumps(rep['prior_run'])}", '',
              f"Returns: {rep['returns_status']}.", '']
    (OUT / 'PHASE8B_GOLD2_VALIDATION.md').write_text('\n'.join(lines) + '\n', encoding='utf8')


def main():
    rep = evaluate(load())
    write_report(rep)
    stage = ('classifier gate passed (Amendment 3 fresh 15-case validation: PASS; DEVELOPMENT use only)'
             if rep['verdict'] == 'PASS' else
             f"fresh 15-case validation verdict {rep['verdict']} (return stage stays locked)")
    p = OUT / 'phase8b_gold2_validation.json'
    with open(OUT / 'PHASE8B_FREEZE_HASHES.jsonl', 'a', encoding='utf8') as fh:
        fh.write(json.dumps(dict(file=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                                 frozen_utc=rep['evaluated_utc'], stage=stage)) + '\n')
    print(rep['verdict'], rep['headline'])
    if rep['verdict'] == 'BORDERLINE':
        print('\nBORDERLINE under A3.8: inspect the single error and ASK THE USER before any further step.')
    return rep


if __name__ == '__main__':
    main()
