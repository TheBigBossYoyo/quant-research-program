import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase8b_events as ev  # noqa: E402
import phase8b_lock as lk  # noqa: E402


def sessions():
    return pd.DatetimeIndex(pd.bdate_range('2014-01-01', '2016-12-30'))


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.s = sessions()
        self.close = pd.DataFrame({'ABC': 10.0, 'ABC_old': np.nan, 'XYZ': 20.0}, index=self.s)
        self.close.loc[self.s >= '2015-06-01', 'XYZ'] = np.nan          # XYZ delisted mid-2015
        self.close.loc[self.s < '2015-01-01', 'ABC'] = np.nan; self.close.loc[self.s < '2015-01-01', 'ABC_old'] = 10.0   # ABC traded as ABC_old before 2015
        self.symtab = pd.DataFrame(dict(cik=[1, 1, 2], sym=['ABC', 'ABC', 'XYZ'], date=pd.to_datetime(['2014-03-01', '2015-03-01', '2014-06-01'])))
        self.current = {1: 'ABC', 3: 'NEW'}

    def idx(self, d):
        return int(self.s.get_loc(pd.Timestamp(d)))

    def test_prior_submission_symbol_wins(self):
        code, route = ev.map_code(1, pd.Timestamp('2015-05-01'), self.idx('2015-05-04'), self.symtab, self.current, self.close, self.s)
        self.assertEqual((code, route), ('ABC', 'insider_submission_prior_400d'))

    def test_old_variant_used_when_plain_code_unpriced(self):
        code, route = ev.map_code(1, pd.Timestamp('2014-06-01'), self.idx('2014-06-02'), self.symtab, self.current, self.close, self.s)
        self.assertEqual((code, route), ('ABC_old', 'insider_submission_prior_400d'))

    def test_backfill_route_before_first_submission(self):
        symtab = self.symtab[self.symtab['cik'] == 2]
        code, route = ev.map_code(2, pd.Timestamp('2014-02-01'), self.idx('2014-02-03'), symtab, {}, self.close, self.s)
        self.assertEqual((code, route), ('XYZ', 'insider_submission_backfill_400d'))

    def test_prior_beyond_400_days_not_used(self):
        symtab = pd.DataFrame(dict(cik=[2], sym=['XYZ'], date=pd.to_datetime(['2014-01-02'])))
        code, route = ev.map_code(2, pd.Timestamp('2015-04-01'), self.idx('2015-04-02'), symtab, {}, self.close, self.s)
        self.assertEqual((code, route), (None, 'unmapped'))

    def test_current_map_fallback_only_when_priced(self):
        code, route = ev.map_code(3, pd.Timestamp('2015-05-01'), self.idx('2015-05-04'), self.symtab, self.current, self.close, self.s)
        self.assertEqual((code, route), (None, 'unmapped'))
        cur = {3: 'ABC'}
        code, route = ev.map_code(3, pd.Timestamp('2015-05-01'), self.idx('2015-05-04'), self.symtab, cur, self.close, self.s)
        self.assertEqual((code, route), ('ABC', 'company_tickers_current'))

    def test_delisted_code_is_not_priced_at_entry(self):
        code, route = ev.map_code(2, pd.Timestamp('2015-09-01'), self.idx('2015-09-02'), self.symtab, {}, self.close, self.s)
        self.assertEqual((code, route), (None, 'unmapped'))

    def test_price_check_uses_only_sessions_before_entry(self):
        close = pd.DataFrame({'Q': np.nan}, index=self.s)
        i = self.idx('2015-03-02')
        close.iloc[i, 0] = 5.0                    # priced only on the entry day itself -> not usable
        self.assertFalse(ev.priced('Q', close, self.s, i))
        close.iloc[i - 1, 0] = 5.0
        self.assertTrue(ev.priced('Q', close, self.s, i))


class DedupTests(unittest.TestCase):
    def frame(self):
        s = sessions()
        rows = [
            dict(accession='a1', cik=1, pred='A', is_amendment=False, accept_et=pd.Timestamp('2015-02-10 16:00'), entry=pd.Timestamp('2015-02-11'), exit=pd.Timestamp('2016-02-10'), code='ABC'),
            dict(accession='a2', cik=1, pred='D', is_amendment=False, accept_et=pd.Timestamp('2015-02-20 16:00'), entry=pd.Timestamp('2015-02-23'), exit=pd.Timestamp('2016-02-22'), code='ABC'),
            dict(accession='a3', cik=1, pred='B', is_amendment=False, accept_et=pd.Timestamp('2015-03-30 16:00'), entry=pd.Timestamp('2015-03-31'), exit=pd.Timestamp('2016-03-30'), code='ABC'),   # 48 days later -> repeat
            dict(accession='a4', cik=1, pred='B', is_amendment=False, accept_et=pd.Timestamp('2015-04-15 16:00'), entry=pd.Timestamp('2015-04-16'), exit=pd.Timestamp('2016-04-15'), code='ABC'),   # 64 days after a1 -> new event
            dict(accession='a5', cik=1, pred='A', is_amendment=True, accept_et=pd.Timestamp('2015-08-01 16:00'), entry=pd.Timestamp('2015-08-03'), exit=pd.Timestamp('2016-08-02'), code='ABC'),
            dict(accession='a6', cik=2, pred='A', is_amendment=False, accept_et=pd.Timestamp('2015-02-10 16:00'), entry=pd.Timestamp('2015-02-11'), exit=pd.Timestamp('2016-02-10'), code=None),
            dict(accession='a7', cik=3, pred='A', is_amendment=False, accept_et=pd.Timestamp('2015-02-10 16:00'), entry=pd.NaT, exit=pd.NaT, code='Q'),
            dict(accession='a8', cik=4, pred='UNCLASSIFIED', is_amendment=False, accept_et=pd.Timestamp('2015-02-10 16:00'), entry=pd.Timestamp('2015-02-11'), exit=pd.Timestamp('2016-02-10'), code='R'),
        ]
        return pd.DataFrame(rows)

    def test_dedup_rules(self):
        events, counts = ev.dedup_events(self.frame())
        self.assertEqual(list(events['accession']), ['a1', 'a4'])
        self.assertEqual(counts['labelled_positive'], 6); self.assertEqual(counts['amendments_dropped'], 1)
        self.assertEqual(counts['no_entry_dropped'], 1); self.assertEqual(counts['unmapped_dropped'], 1)
        self.assertEqual(counts['repeated_references_merged'], 1); self.assertEqual(counts['events'], 2)
        self.assertEqual(events.loc[0, 'event_id'], 'E8B-0000000001-a1')

    def test_repeat_window_boundary(self):
        f = self.frame(); f.loc[f['accession'] == 'a3', 'accept_et'] = pd.Timestamp('2015-04-11 16:00')   # exactly 60 days after a1 -> distinct
        events, counts = ev.dedup_events(f)
        self.assertIn('a3', list(events['accession'])); self.assertNotIn('a4', list(events['accession']))   # a4 now within 60 days of a3

    def test_locked_event_dates_raise(self):
        f = self.frame(); f.loc[f['accession'] == 'a1', 'exit'] = pd.Timestamp('2018-01-02')
        with self.assertRaises(lk.Phase8BLockError):
            ev.dedup_events(f)

    def test_non_primary_labels_never_become_events(self):
        f = self.frame(); f['pred'] = 'D'
        events, counts = ev.dedup_events(f)
        self.assertEqual(len(events), 0); self.assertEqual(counts['labelled_positive'], 0)


if __name__ == '__main__':
    unittest.main()
