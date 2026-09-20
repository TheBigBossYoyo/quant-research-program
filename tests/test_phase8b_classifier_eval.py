import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase8b_classifier_eval as ce  # noqa: E402


class MetricTests(unittest.TestCase):
    def test_binary_metrics_raw(self):
        y = ['A', 'B', 'D', 'I', 'A', 'C']; p = ['A', 'D', 'A', 'I', 'B', 'C']
        m = ce.binary_metrics(y, p)
        self.assertEqual((m['tp'], m['fp'], m['fn'], m['tn']), (2, 1, 1, 2))
        self.assertAlmostEqual(m['precision'], 2 / 3); self.assertAlmostEqual(m['recall'], 2 / 3); self.assertAlmostEqual(m['f1'], 2 / 3)

    def test_j_is_valid_but_never_positive(self):
        self.assertIn('J', ce.CLASSES); self.assertNotIn('J', ce.POSITIVE)
        m = ce.binary_metrics(['J', 'A'], ['A', 'A'])
        self.assertEqual((m['tp'], m['fp']), (1, 1))

    def test_binary_metrics_weighted(self):
        y = ['A', 'D']; p = ['A', 'A']
        m = ce.binary_metrics(y, p, weights=[1.0, 3.0])
        self.assertAlmostEqual(m['precision'], 0.25)

    def test_wilson(self):
        lo, hi = ce.wilson(25, 25)
        self.assertGreater(lo, 0.86); self.assertAlmostEqual(hi, 1.0, places=6)
        lo2, _ = ce.wilson(23, 25)
        self.assertTrue(0.74 < lo2 < 0.76)

    def test_confusion_and_per_class(self):
        y = ['A', 'B', 'D']; p = ['A', 'UNCLASSIFIED', 'D']
        cm = ce.confusion(y, p)
        self.assertEqual(cm.loc['B', 'UNCLASSIFIED'], 1); self.assertEqual(cm.values.sum(), 3)
        pc = ce.per_class(y, p)
        self.assertEqual(pc['A']['support'], 1); self.assertEqual(pc['B']['recall'], 0.0)

    def test_gate_logic(self):
        raw = dict(tp=25, fp=0, fn=10, tn=50, precision=1.0, recall=25 / 35); wt = dict(precision=1.0)
        g = ce.gate_check(raw, wt)
        self.assertTrue(g['passed']); self.assertFalse(g['recall_flag_investigate'])
        raw2 = dict(tp=10, fp=0, fn=0, tn=50, precision=1.0, recall=1.0)
        self.assertFalse(ce.gate_check(raw2, wt)['passed'])                      # too few predicted positives
        raw3 = dict(tp=22, fp=3, fn=0, tn=50, precision=0.88, recall=1.0)
        self.assertFalse(ce.gate_check(raw3, dict(precision=0.88))['passed'])     # precision below 0.90
        raw4 = dict(tp=23, fp=2, fn=60, tn=50, precision=0.92, recall=23 / 83)
        g4 = ce.gate_check(raw4, dict(precision=0.92))
        self.assertTrue(g4['passed']); self.assertTrue(g4['recall_flag_investigate'])


class LabelLoadingTests(unittest.TestCase):
    def test_load_labels_rejects_unknown_letters(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            pd.DataFrame(dict(accession=['x1', 'x2'], human_label=['A', 'Z'], human_notes=['', ''])).to_csv(d / 'lab.csv', index=False)
            pd.DataFrame(dict(accession=['x1', 'x2'], stratum=['S1', 'S1'], split=['DEV', 'HOLDOUT'], year=[2015, 2016])).to_csv(d / 'split.csv', index=False)
            with self.assertRaises(ValueError):
                ce.load_labels(d / 'lab.csv', d / 'split.csv')
            pd.DataFrame(dict(accession=['x1', 'x2'], human_label=[' a ', ''], human_notes=['', ''])).to_csv(d / 'lab.csv', index=False)
            df = ce.load_labels(d / 'lab.csv', d / 'split.csv')
            self.assertEqual(list(df['human_label']), ['A', ''])
            self.assertEqual(len(ce.labelled(df, 'DEV')), 1); self.assertEqual(len(ce.labelled(df, 'HOLDOUT')), 0)

    def test_holdout_labels_blanked_for_development_reads(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            pd.DataFrame(dict(accession=['x1', 'x2'], human_label=['A', 'B'], human_notes=['n1', 'n2'])).to_csv(d / 'lab.csv', index=False)
            pd.DataFrame(dict(accession=['x1', 'x2'], stratum=['S1', 'S1'], split=['DEV', 'HOLDOUT'], year=[2015, 2016])).to_csv(d / 'split.csv', index=False)
            df = ce.load_labels(d / 'lab.csv', d / 'split.csv')
            self.assertEqual(list(df['human_label']), ['A', '']); self.assertEqual(list(df['human_notes']), ['n1', ''])
            self.assertEqual(len(ce.labelled(df, 'HOLDOUT')), 0)
            full = ce.load_labels(d / 'lab.csv', d / 'split.csv', _allow_holdout=True)
            self.assertEqual(list(full['human_label']), ['A', 'B'])

    def test_holdout_refused_unless_classifier_hash_matches(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / 'h.jsonl'; log.write_text(json.dumps(dict(stage='preregistration')) + '\n', encoding='utf8')
            clf = ce.ROOT / 'research' / '_tmp_phase8b_clf_for_test.py'
            clf.write_text('def classify(a):\n    return "A"\n', encoding='utf8')
            try:
                rel = 'research/_tmp_phase8b_clf_for_test.py'
                self.assertFalse(ce.classifier_frozen(log, [rel]))
                with self.assertRaises(RuntimeError):
                    ce.evaluate_holdout(lambda a: 'A', {'S1': 1.0}, [rel], hash_log=log)
                # a freeze record with a stale hash does not unlock
                log.write_text(json.dumps(dict(stage='classifier frozen (code hash)', file=rel, sha256='0' * 64)) + '\n', encoding='utf8')
                self.assertFalse(ce.classifier_frozen(log, [rel]))
                # matching hash unlocks; a second evaluation is refused
                log.write_text(json.dumps(dict(stage='classifier frozen (code hash)', file=rel, sha256=ce.sha256_file(clf))) + '\n', encoding='utf8')
                self.assertTrue(ce.classifier_frozen(log, [rel]))
                log.write_text(log.read_text(encoding='utf8') + json.dumps(dict(stage='holdout evaluated')) + '\n', encoding='utf8')
                with self.assertRaises(RuntimeError):
                    ce.evaluate_holdout(lambda a: 'A', {'S1': 1.0}, [rel], hash_log=log)
                # editing the classifier after the freeze re-locks it
                clf.write_text('def classify(a):\n    return "B"\n', encoding='utf8')
                self.assertFalse(ce.classifier_frozen(log, [rel]))
            finally:
                clf.unlink()


if __name__ == '__main__':
    unittest.main()
