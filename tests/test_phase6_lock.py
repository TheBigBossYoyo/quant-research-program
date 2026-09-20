import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase6_lock as lock  # noqa: E402


def frame(start='2010-01-01', end='2026-08-31'):
    idx = pd.date_range(start, end, freq='D')
    return pd.DataFrame({'x': range(len(idx))}, index=idx)


class LockTests(unittest.TestCase):
    def test_development_truncates_before_2018(self):
        out = lock.enforce(frame(), 'development')
        self.assertEqual(out.index.max(), pd.Timestamp('2017-12-31'))
        self.assertTrue(lock.assert_development(out.index))

    def test_assert_development_rejects_later_dates(self):
        with self.assertRaises(lock.LockError):
            lock.assert_development(frame().index)

    def test_validation_locked_without_unlock_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = {'validation': Path(tmp) / 'V.json', 'holdout': Path(tmp) / 'H.json'}
            with self.assertRaises(lock.LockError):
                lock.enforce(frame(), 'validation', files)
            with self.assertRaises(lock.LockError):
                lock.enforce(frame(), 'holdout', files)

    def test_unlock_requires_matching_decision_document_and_human_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            doc = tmp / 'DECISION.md'
            doc.write_text('frozen decision', encoding='utf8')
            files = {'validation': tmp / 'V.json', 'holdout': tmp / 'H.json'}
            good = dict(frozen_candidate_hash='abc', decision_document='DECISION.md',
                        decision_document_sha256=lock.sha256_file(doc), human_authorised=True,
                        authorised_on='2026-09-09')
            bad = dict(good, human_authorised='yes')
            files['validation'].write_text(json.dumps(bad), encoding='utf8')
            self.assertFalse(lock.unlock_status('validation', files)['open'])
            files['validation'].write_text(json.dumps(good), encoding='utf8')
            out = lock.enforce(frame(), 'validation', files)
            self.assertEqual((out.index.min(), out.index.max()),
                             (pd.Timestamp('2018-01-01'), pd.Timestamp('2021-12-31')))
            # holdout still locked: its own file is absent
            with self.assertRaises(lock.LockError):
                lock.enforce(frame(), 'holdout', files)
            doc.write_text('edited after the fact', encoding='utf8')
            self.assertFalse(lock.unlock_status('validation', files)['open'])

    def test_repository_has_no_unlock_files(self):
        self.assertFalse(lock.unlock_status('validation')['open'])
        self.assertFalse(lock.unlock_status('holdout')['open'])

    def test_segments_are_contiguous_and_fixed(self):
        self.assertEqual(lock.SEGMENTS['development'][1], lock.SEGMENTS['validation'][0])
        self.assertEqual(lock.SEGMENTS['validation'][1], lock.SEGMENTS['holdout'][0])
        self.assertEqual(lock.SEGMENTS['holdout'][1], '2026-09-01')


if __name__ == '__main__':
    unittest.main()
