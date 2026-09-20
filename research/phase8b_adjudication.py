"""Phase 8B Amendment 3 (A3.5): adjudication log for the frozen 60-case reference set. DIAGNOSTIC ONLY.

The frozen reference file is never modified. This module records, separately and explicitly, the human-entered labels
that are objectively inconsistent with their own filing text, with the exact passage, the reason and the cause. It also
records the disagreements where the entered label was CORRECT and the v1.7 classifier was wrong, so the log is a
complete audit of all nine v1.7 disagreements rather than a selection of the convenient ones.

The counterfactual precision printed at the end is NOT a verdict and may never restate the frozen result. The frozen
verdict on classifier v1.7 remains CLASSIFIER_VALIDATION_FAILED_AS_MEASURED (33/38 = 86.8%).

Usage (from research/): PYTHONUTF8=1 python phase8b_adjudication.py
"""
from datetime import date
import csv
import json

import pandas as pd

from phase6_lock import ROOT
import phase8b_corpus as cp
import phase8b_display as disp
import phase8b_edgar as ed

OUT = ROOT / 'research/phase8b'
GOLD = OUT / 'gold'
LOG = OUT / 'PHASE8B_GOLD_ADJUDICATION_LOG.csv'
ADJUDICATED = date(2026, 9, 20).isoformat()

# cause vocabulary (A3.5)
HIDDEN = 'hidden evidence / UI defect'
HUMAN_SEMANTIC = 'genuine human semantic error (decisive sentence WAS displayed)'
NO_ERROR = 'no error in the entered label (classifier v1.7 was wrong)'

# One entry per v1.7 disagreement. `adjudicated` differs from `entered` only where the entered label contradicts the
# filing text itself. Decisions are stated against the passage, never against a desired precision number.
ADJUDICATIONS = [
    dict(gold_id='G053', accession='0000950133-07-001624', entered='INCREASED', adjudicated='IRRELEVANT', changed=True, cause=HUMAN_SEMANTIC,
         anchor='option to purchase up to an additional $20,000,000 in aggregate principal amount of notes',
         reason='The only repurchase-related sentence in the filing grants the Initial Purchasers an over-allotment option on CONVERTIBLE NOTES, not an issuer authorisation to repurchase its own shares. An underwriter/initial-purchaser over-allotment option is IRRELEVANT under the frozen label definitions. The decisive sentence was displayed to the labeller, so this is not a display defect; "additional" and "purchase" appear to have been read as an issuer repurchase increase. Classifier v1.7 was correct here (label I, not_own_equity).'),
    dict(gold_id='G015', accession='0000067215-16-000056', entered='RENEWAL', adjudicated='INCREASED', changed=True, cause=HIDDEN,
         anchor='authorized an additional $50 million to repurchase shares',
         reason='The press release is headlined "ANNOUNCES INCREASE IN STOCK REPURCHASE PROGRAM" and states that the Board "authorized an additional $50 million", taking the authorisation from $50m to $100m ("the Company now has up to $100 million authorized"). Explicit additional capacity is INCREASED under the preserved distinctions; the six-month term extension is secondary. The labeller was shown only the term-extension sentences, so the entered RENEWAL reflects the display defect, not a judgement on this evidence. Classifier v1.7 was correct here (label B).'),
    dict(gold_id='G049', accession='0000859598-13-000023', entered='ROUTINE', adjudicated='INCREASED', changed=True, cause=HIDDEN,
         anchor="increased the Company's authority to repurchase SEACOR common stock from $30.5 million up to $100.0 million",
         reason='The 8-K item text states that the Board "approved an increase in the Company\'s authority to repurchase its common stock" and the exhibit gives the amounts ($30.5m -> $100.0m). That is explicit additional capacity = INCREASED. The labeller was shown only "During the fourth quarter, the Company purchased 1,047,664 shares", a quarterly-activity sentence that correctly reads as ROUTINE in isolation. The v1.7 snippet ranker did not treat "authority" as authorisation vocabulary (repair E). Classifier v1.7 was correct here (label B).'),
    dict(gold_id='G009', accession='0000763563-10-000130', entered='RENEWAL', adjudicated='RENEWAL', changed=False, cause=NO_ERROR,
         anchor='approved the extension of the current stock repurchase plan',
         reason='Entered label correct. "Extends Share Repurchase Plan" / "approved the extension of the current stock repurchase plan until November 16, 2011" with no added capacity is RENEWAL. Classifier v1.7 error: the case-insensitive newness test matched "New York" in the glued release header (repair A) and so skipped the renewal branch (repair C).'),
    dict(gold_id='G016', accession='0001000623-14-000090', entered='COMPLETED_HISTORICAL', adjudicated='COMPLETED_HISTORICAL', changed=False, cause=NO_ERROR,
         anchor='Currently, there is no authorization for additional share repurchases.',
         reason='Entered label correct, and the filing says so explicitly: "Currently, there is no authorization for additional share repurchases." The $50m buyback was completed in Q1 2014. Classifier v1.7 error: it fired on a forward-looking-statements sentence listing "capital allocation strategy" (repair B).'),
    dict(gold_id='G052', accession='0000950134-08-000530', entered='COMPLETED_HISTORICAL', adjudicated='COMPLETED_HISTORICAL', changed=False, cause=NO_ERROR,
         anchor="board of directors approved a share repurchase program for $750 million",
         reason='Entered label correct. The passage is an annual recap exhibit: the $750m programme was authorised "In 2007" and $207.8m had already been repurchased under it by 2007-09-30; the filing is dated 2008-01-14. Historical recap, not an announcement. Classifier v1.7 error: an undated recap sentence read as a fresh authorisation. No clean general repair was adopted for recap lists.'),
    dict(gold_id='G002', accession='0001144204-08-046405', entered='NEW', adjudicated='NEW', changed=False, cause=NO_ERROR,
         anchor='Share Repurchase Authorization CACI’s Board of Directors has approved a share repurchase program for up to $20 million',
         reason='Entered label correct: an earnings release with an explicit "Share Repurchase Authorization" heading announcing a $20m programme. Classifier v1.7 error: the quarterly-boilerplate guard demoted the undated authorisation sentence to UNCLASSIFIED (repair D).'),
    dict(gold_id='G046', accession='0001299933-07-006311', entered='NEW', adjudicated='NEW', changed=False, cause=NO_ERROR,
         anchor='the Board authorized the Company to repurchase up to 100,000 shares',
         reason='Entered label correct: an explicit board authorisation of up to 100,000 shares (~3.6% of shares outstanding) over the next two years. Classifier v1.7 error: same quarterly-boilerplate demotion to UNCLASSIFIED (repair D).'),
    dict(gold_id='G012', accession='0000950134-04-016104', entered='NEW', adjudicated='NEW', changed=False, cause=NO_ERROR,
         anchor='announcing, among other things, a stock repurchase program to purchase up to $30 million',
         reason='Entered label correct: the 8-K item and the release headline ("Announces $30 Million Stock Repurchase Program") announce a new programme. Classifier v1.7 error: pass 1 read only the execution-timing sentence and returned ROUTINE (repair D).'),
]


def exact_passage(accession, anchor, width=1):
    """The anchor sentence from the filing itself, with `width` neighbouring sentences each side (document order)."""
    f = ed.load_filing(accession)
    key = disp.normalize(anchor)[:120]
    for d in f['documents']:
        if not d['type'].upper().startswith(('8-K', 'EX-99')):
            continue
        sents = cp.sentences(d['text'])
        for i, s in enumerate(sents):
            if key in disp.normalize(s):
                lo, hi = max(0, i - width), min(len(sents), i + width + 1)
                return ' '.join(sents[lo:hi])[:1200], d['type']
    return '', ''


def build():
    ref = pd.read_csv(GOLD / 'phase8b_gold_reference_FROZEN.csv', dtype=str).fillna('')
    key = pd.read_csv(GOLD / 'phase8b_gold_key_SEALED.csv', dtype=str).fillna('')
    ref = ref.merge(key, on='gold_id', validate='one_to_one')
    rows = []
    for a in ADJUDICATIONS:
        r = ref[ref['gold_id'] == a['gold_id']]
        if len(r) != 1:
            raise RuntimeError(f"{a['gold_id']} not found exactly once in the frozen reference")
        r = r.iloc[0]
        if r['human_label'].strip().upper() != a['entered']:
            raise RuntimeError(f"{a['gold_id']}: frozen entered label {r['human_label']!r} != {a['entered']!r}; refusing to write a log that misquotes the frozen file")
        if r['accession'] != a['accession']:
            raise RuntimeError(f"{a['gold_id']}: accession mismatch against the sealed key")
        passage, doc = exact_passage(a['accession'], a['anchor'])
        if not passage:
            raise RuntimeError(f"{a['gold_id']}: anchor sentence not found in the filing text")
        rows.append(dict(gold_id=a['gold_id'], accession=a['accession'], company=r['company'], filing_date=r['filing_date'],
                         original_entered_label=a['entered'], corrected_adjudicated_label=a['adjudicated'], label_changed=a['changed'],
                         classifier_v17_label=r['p1_label'], classifier_v17_rule=r['p1_rule'], stratum=r['stratum'],
                         source_document=doc, exact_passage=passage, reason=a['reason'], cause=a['cause'], adjudicated_date=ADJUDICATED))
    return pd.DataFrame(rows)


def counterfactual(df):
    """DIAGNOSTIC ONLY. What stratum-P precision would have been had the three objectively erroneous labels been
    entered correctly. This is NOT a verdict, NOT a re-run of the frozen rule, and NEVER replaces 33/38 = 86.8%."""
    ref = pd.read_csv(GOLD / 'phase8b_gold_reference_FROZEN.csv', dtype=str).fillna('')
    key = pd.read_csv(GOLD / 'phase8b_gold_key_SEALED.csv', dtype=str).fillna('')
    m = ref.merge(key, on='gold_id', validate='one_to_one')
    fix = {r['gold_id']: r['corrected_adjudicated_label'] for _, r in df[df['label_changed']].iterrows()}
    m['adj'] = [fix.get(g, h.strip().upper()) for g, h in zip(m['gold_id'], m['human_label'])]
    P = m[m['stratum'].str.startswith('P_')]
    frozen = int(P['human_label'].str.strip().str.upper().isin(['NEW', 'INCREASED']).sum())
    adj = int(P['adj'].isin(['NEW', 'INCREASED']).sum())
    return dict(frozen_verdict='CLASSIFIER_VALIDATION_FAILED_AS_MEASURED', frozen_stratum_P=f'{frozen}/{len(P)}', frozen_precision=round(frozen / len(P), 4),
                counterfactual_stratum_P=f'{adj}/{len(P)}', counterfactual_precision=round(adj / len(P), 4),
                labels_corrected_in_stratum_P=int(sum(1 for g in fix if g in set(P['gold_id']))),
                status='DIAGNOSTIC ONLY - does not restate the frozen verdict, is not a PASS, and is not used by any gate')


if __name__ == '__main__':
    df = build()
    df.to_csv(LOG, index=False, encoding='utf8', quoting=csv.QUOTE_ALL)
    cf = counterfactual(df)
    (OUT / 'phase8b_adjudication_counterfactual.json').write_text(json.dumps(cf, indent=1), encoding='utf8')
    print(df[['gold_id', 'original_entered_label', 'corrected_adjudicated_label', 'label_changed', 'cause']].to_string(index=False))
    print()
    print(json.dumps(cf, indent=1))
