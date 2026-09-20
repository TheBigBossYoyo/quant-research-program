import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase8b_lock as lk  # noqa: E402


class Phase8BLockTests(unittest.TestCase):
    def test_guard_accepts_development_dates(self):
        self.assertTrue(lk.guard_dates(pd.date_range('2004-01-02', '2017-12-29', freq='B'), 'x'))

    def test_guard_raises_on_first_locked_day(self):
        with self.assertRaises(lk.Phase8BLockError):
            lk.guard_dates(pd.DatetimeIndex(['2017-12-29', '2018-01-01']), 'x')

    def test_guard_raises_on_holdout(self):
        with self.assertRaises(lk.Phase8BLockError):
            lk.guard_dates(['2022-03-01'], 'x')

    def test_guard_handles_tz_aware_eastern(self):
        ok = pd.DatetimeIndex(['2017-12-29 23:59:00']).tz_localize('America/New_York')
        self.assertTrue(lk.guard_dates(ok, 'x'))
        bad = pd.DatetimeIndex(['2018-01-01 00:00:01']).tz_localize('America/New_York')
        with self.assertRaises(lk.Phase8BLockError):
            lk.guard_dates(bad, 'x')

    def test_guard_ignores_nat_and_accepts_empty(self):
        self.assertTrue(lk.guard_dates([pd.NaT, '2010-01-01'], 'x'))
        self.assertTrue(lk.guard_dates([], 'x'))

    def test_guard_frame_checks_index_and_columns(self):
        df = pd.DataFrame({'entry': pd.to_datetime(['2016-01-04', '2018-01-02'])}, index=pd.to_datetime(['2016-01-04', '2016-01-05']))
        with self.assertRaises(lk.Phase8BLockError):
            lk.guard_frame(df, 'ev', date_columns=('entry',))
        df2 = df.iloc[:1]
        self.assertIs(lk.guard_frame(df2, 'ev', date_columns=('entry',)), df2)

    def test_filed_date_guard(self):
        self.assertEqual(lk.guard_filed_date('20171229'), '20171229')
        self.assertEqual(lk.guard_filed_date('2017-12-29'), '20171229')
        for bad in ('20180101', '2018-06-30', '20250101'):
            with self.assertRaises(lk.Phase8BLockError):
                lk.guard_filed_date(bad)
        with self.assertRaises(lk.Phase8BLockError):
            lk.guard_filed_date('garbage')

    def test_companyfacts_loader_drops_post_2017_facts_at_read_time(self):
        with tempfile.TemporaryDirectory() as d:
            raw = dict(cik=1, entityName='X', facts={'us-gaap': {'StockRepurchaseProgramAuthorizedAmount1': dict(label='l', units={'USD': [
                dict(end='2016-12-31', val=1, filed='2017-02-01', form='10-K'),
                dict(end='2017-12-31', val=2, filed='2018-02-01', form='10-K'),
                dict(end='2019-12-31', val=3, filed='2020-02-01', form='10-K'),
            ]})}, 'dei': {'Only2018': dict(label='l', units={'shares': [dict(end='2018-03-31', val=5, filed='2018-05-01')]})}})
            with gzip.open(Path(d) / 'CIK0000000001.json.gz', 'wt', encoding='utf8') as fh:
                json.dump(raw, fh)
            out = lk.companyfacts_dev(1, root=d)
            rows = out['facts']['us-gaap']['StockRepurchaseProgramAuthorizedAmount1']['units']['USD']
            self.assertEqual([r['val'] for r in rows], [1])
            self.assertNotIn('Only2018', out['facts']['dei'])
            self.assertIsNone(lk.companyfacts_dev(2, root=d))


if __name__ == '__main__':
    unittest.main()
