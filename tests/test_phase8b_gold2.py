"""Phase 8B Amendment 3: tests for the fresh 15-case draw, the A3.4 preflight and the A3.8 decision rule.

No human label is consulted; the decision rule is exercised on synthetic frames.
"""
import csv
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

import phase8b_display as disp
import phase8b_gold2 as g2
import phase8b_gold2_eval as ev

GOLD2 = ROOT / 'research/phase8b/gold2'


class FreshSetIntegrityTests(unittest.TestCase):
    """Properties of the drawn set that A3.7 fixes in advance."""

    @classmethod
    def setUpClass(cls):
        cls.human = pd.read_csv(GOLD2 / 'phase8b_gold2_candidates.csv', dtype=str).fillna('')
        cls.key = pd.read_csv(GOLD2 / 'phase8b_gold2_key_SEALED.csv', dtype=str).fillna('')
        cls.meta = json.loads((GOLD2 / 'phase8b_gold2_meta.json').read_text(encoding='utf8'))

    def test_exactly_fifteen_cases(self):
        self.assertEqual(len(self.human), 15)
        self.assertEqual(len(self.key), 15)

    def test_temporal_balance_8_recent_7_early(self):
        self.assertEqual(self.meta['strata'], {'P_recent': 8, 'P_early': 7})

    def test_all_cases_are_predicted_positives(self):
        self.assertTrue(self.key['p1_label'].isin(['A', 'B']).all())

    def test_one_case_per_issuer(self):
        self.assertEqual(self.key['cik'].nunique(), 15)

    def test_no_case_overlaps_anything_a_human_has_seen(self):
        ex_acc, ex_cik = g2.excluded()
        self.assertFalse(set(self.key['accession']) & ex_acc)
        self.assertFalse({int(c) for c in self.key['cik']} & ex_cik)

    def test_no_case_comes_from_the_development_pool(self):
        import phase8b_corpus as cp
        self.assertFalse(any(cp.in_dev_pool(a) for a in self.key['accession']))

    def test_human_csv_carries_no_prediction(self):
        forbidden = {'p1_label', 'p1_rule', 'p1_margin', 'p1_evidence', 'p2_primary', 'p2_score', 'stratum',
                     'accession', 'cik'}
        self.assertFalse(forbidden & set(self.human.columns))

    def test_labels_start_empty(self):
        self.assertTrue((self.human['human_label'].str.strip() == '').all())

    def test_every_case_is_inside_the_development_lock(self):
        self.assertTrue((self.key['year'].astype(int) <= 2017).all())


class PreflightTests(unittest.TestCase):
    """A3.4: the default visible passage always contains the classifier evidence verbatim."""

    def test_preflight_passes_on_the_drawn_set(self):
        rep = g2.preflight()
        self.assertTrue(rep['all_visible'])
        self.assertEqual(rep['n'], 15)
        self.assertEqual(rep['prediction_columns_in_human_csv'], [])

    def test_what_the_labeler_serves_contains_the_evidence(self):
        """`configure()` mutates labeler_app module globals, so everything it touches is snapshotted and restored:
        otherwise this test would break the pre-existing labeler tests in the same process."""
        sys.path.insert(0, str(ROOT / 'research/phase8b/labeler'))
        import labeler_app as la
        import gold2_labeler as g2l
        saved = {name: getattr(la, name) for name in ('VALID', 'DATASETS', 'ID_COL', 'EXTRA_REQUIRED', 'HTML_PATH',
                                                      'REPORT_NAME', 'BACKUP_EVERY')}
        saved_row = la.App.row
        ws = Path(tempfile.mkdtemp())
        try:
            shutil.copy2(GOLD2 / 'phase8b_gold2_candidates.csv', ws)
            g2l.configure()
            app = la.App(ws)
            key = pd.read_csv(GOLD2 / 'phase8b_gold2_key_SEALED.csv', dtype=str).set_index('gold2_id')
            for i in range(15):
                row = app.row('gold2', i)
                shown = ' '.join(row['snippet']['sentences'])
                evidence = key.loc[row['row']['gold2_id'], 'p1_evidence']
                self.assertTrue(disp.contains(shown, evidence), row['row']['gold2_id'])
        finally:
            for name, value in saved.items():
                setattr(la, name, value)
            la.App.row = saved_row
            shutil.rmtree(ws, ignore_errors=True)

    def test_the_defective_v17_ranker_is_not_used_by_the_fresh_labeler(self):
        src = (ROOT / 'research/phase8b/labeler/gold2_labeler.py').read_text(encoding='utf8')
        self.assertNotIn('gold_snippet', src)
        self.assertNotIn('minimal_snippet', src)


class DecisionRuleTests(unittest.TestCase):
    """A3.8, exercised on synthetic label vectors. Frozen before any fresh label existed."""

    @staticmethod
    def frame(n_correct, n=15, wrong_label='COMPLETED_HISTORICAL', rules=None):
        rules = rules or ['auth_new'] * n
        rows = []
        for i in range(n):
            primary = i < n_correct
            rows.append(dict(gold2_id=f'F{i + 1:03d}', accession=f'{i:010d}-00-000000', stratum='P_recent',
                             human_label='NEW' if primary else wrong_label, human_primary=primary,
                             p1_label='A', p1_rule=rules[i], p1_margin='2.0', p1_evidence='x', human_notes='',
                             p2_primary='True'))
        return pd.DataFrame(rows)

    def test_fifteen_of_fifteen_passes(self):
        df = self.frame(15)
        self.assertEqual(ev.verdict(15, 15, ev.systematic(df)), 'PASS')

    def test_fourteen_of_fifteen_is_borderline(self):
        df = self.frame(14)
        self.assertEqual(ev.verdict(14, 15, ev.systematic(df)), 'BORDERLINE')

    def test_thirteen_of_fifteen_fails(self):
        df = self.frame(13)
        self.assertEqual(ev.verdict(13, 15, ev.systematic(df)), 'FAIL')

    def test_two_routine_false_positives_fail_even_at_thirteen(self):
        df = self.frame(13, wrong_label='ROUTINE')
        syst = ev.systematic(df)
        self.assertTrue(syst['flag'])
        self.assertEqual(ev.verdict(13, 15, syst), 'FAIL')

    def test_two_false_positives_from_the_same_rule_flag_systematic(self):
        df = self.frame(13)
        self.assertTrue(ev.systematic(df)['flag'])

    def test_a_single_error_is_not_systematic(self):
        self.assertFalse(ev.systematic(self.frame(14))['flag'])

    def test_the_original_sixty_are_never_pooled(self):
        prior = ev.prior_run_reference()
        if prior is not None:
            self.assertIn('SEEN', prior['status'])
            self.assertEqual(prior['frozen_v17_verdict'], 'CLASSIFIER_VALIDATION_FAILED_AS_MEASURED')

    def test_pass_threshold_is_not_configurable_downward(self):
        self.assertEqual(ev.PASS_MIN, 15)
        self.assertEqual(ev.BORDERLINE_MIN, 14)


class ReturnLockTests(unittest.TestCase):
    """A3.10: returns stay locked until a PASS is recorded."""

    def test_the_gate_record_is_a_pass_and_is_development_only(self):
        """The gate passed 15/15 on 2026-09-20. The record must say PASS and must scope it to DEVELOPMENT use."""
        import json
        recs = [json.loads(l) for l in (ROOT / 'research/phase8b/PHASE8B_FREEZE_HASHES.jsonl').read_text(encoding='utf8').splitlines() if l.strip()]
        gate = [r for r in recs if r.get('stage', '').startswith('classifier gate passed')]
        self.assertEqual(len(gate), 1)
        self.assertIn('PASS', gate[0]['stage'])
        self.assertIn('DEVELOPMENT use only', gate[0]['stage'])

    def test_the_recorded_pass_matches_the_written_result(self):
        import json
        rep = json.loads((ROOT / 'research/phase8b/phase8b_gold2_validation.json').read_text(encoding='utf8'))
        self.assertEqual(rep['verdict'], 'PASS')
        self.assertEqual(rep['headline']['correct'], 15)
        self.assertEqual(rep['headline']['n'], 15)
        self.assertEqual(rep['reference_kind'], 'FRESH_BLIND_TO_CLASSIFIER_AI_ASSISTED_HUMAN_ADJUDICATION')

    def test_the_v17_failure_record_is_still_present(self):
        log = (ROOT / 'research/phase8b/PHASE8B_FREEZE_HASHES.jsonl').read_text(encoding='utf8')
        self.assertIn('gold validation verdict FAIL', log)

    def test_the_frozen_v17_reference_file_is_unchanged(self):
        import hashlib
        p = ROOT / 'research/phase8b/gold/phase8b_gold_reference_FROZEN.csv'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),
                         '09e31be6e09550183e6a9dc6dd5e6ffb9411174b72de170e543634017330f73a')

    def test_the_archived_v17_classifier_matches_its_ledger_hash(self):
        import hashlib
        p = ROOT / 'research/phase8b/frozen_v1.7/phase8b_classifier_v1.7.py'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),
                         'bae6374e0e1a03507d5f74dcb2218fb6ca2e8fe3b98225f930633a087899e153')


class AdjudicationLogTests(unittest.TestCase):
    """A3.5: the log is complete, quotes the frozen file correctly, and is diagnostic only."""

    @classmethod
    def setUpClass(cls):
        cls.log = pd.read_csv(ROOT / 'research/phase8b/PHASE8B_GOLD_ADJUDICATION_LOG.csv', dtype=str).fillna('')
        cls.cf = json.loads((ROOT / 'research/phase8b/phase8b_adjudication_counterfactual.json').read_text(encoding='utf8'))

    def test_every_v17_disagreement_is_recorded(self):
        self.assertEqual(len(self.log), 9)

    def test_required_columns_present(self):
        for c in ('gold_id', 'original_entered_label', 'corrected_adjudicated_label', 'exact_passage', 'reason',
                  'cause', 'adjudicated_date'):
            self.assertIn(c, self.log.columns)

    def test_the_over_allotment_case_is_corrected_to_irrelevant(self):
        r = self.log[self.log['gold_id'] == 'G053'].iloc[0]
        self.assertEqual(r['original_entered_label'], 'INCREASED')
        self.assertEqual(r['corrected_adjudicated_label'], 'IRRELEVANT')

    def test_entered_labels_quote_the_frozen_file(self):
        ref = pd.read_csv(ROOT / 'research/phase8b/gold/phase8b_gold_reference_FROZEN.csv', dtype=str).fillna('')
        ref = ref.set_index('gold_id')['human_label'].str.strip().str.upper()
        for _, r in self.log.iterrows():
            self.assertEqual(r['original_entered_label'], ref[r['gold_id']], r['gold_id'])

    def test_the_counterfactual_is_not_a_pass_and_says_so(self):
        self.assertIn('DIAGNOSTIC ONLY', self.cf['status'])
        self.assertEqual(self.cf['frozen_verdict'], 'CLASSIFIER_VALIDATION_FAILED_AS_MEASURED')
        self.assertLess(self.cf['counterfactual_precision'], 0.95)


if __name__ == '__main__':
    unittest.main()
