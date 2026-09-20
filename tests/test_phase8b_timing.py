import sys
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase8b_timing as tm  # noqa: E402
import phase8b_lock as lk  # noqa: E402

ET = ZoneInfo('America/New_York')


def sessions():
    """Reference NYSE sessions 2004-2017 from exchange_calendars (includes special closures)."""
    return tm.xnys_sessions('2004-01-01', '2017-12-31')


class AcceptanceParsingTests(unittest.TestCase):
    def test_parse_acceptance_is_eastern(self):
        a = tm.parse_acceptance('20150219162634')
        self.assertEqual((a.year, a.month, a.day, a.hour, a.minute, a.second), (2015, 2, 19, 16, 26, 34))
        self.assertEqual(a.utcoffset().total_seconds(), -5 * 3600)   # EST in February

    def test_parse_acceptance_dst(self):
        a = tm.parse_acceptance('20150715083000')
        self.assertEqual(a.utcoffset().total_seconds(), -4 * 3600)   # EDT in July
        self.assertEqual(a.astimezone(ZoneInfo('UTC')).hour, 12)

    def test_parse_acceptance_rejects_bad_input(self):
        for bad in ('2015021916', '20150219162634x', '', None):
            with self.assertRaises(ValueError):
                tm.parse_acceptance(bad)

    def test_parse_filed(self):
        self.assertEqual(tm.parse_filed('20150219'), pd.Timestamp('2015-02-19'))


class EntrySessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = sessions()

    def acc(self, s):
        return tm.parse_acceptance(s)

    def test_pre_market_before_cutoff_enters_same_day_open(self):
        e, cat = tm.entry_session(self.acc('20150219083000'), self.s)   # Thursday 08:30:00 exactly
        self.assertEqual(e, pd.Timestamp('2015-02-19')); self.assertEqual(cat, 'same_day_open')

    def test_pre_market_after_cutoff_enters_next_session(self):
        e, cat = tm.entry_session(self.acc('20150219083001'), self.s)
        self.assertEqual(e, pd.Timestamp('2015-02-20')); self.assertEqual(cat, 'next_session_open')

    def test_intraday_filing_enters_next_session_never_same_session(self):
        e, _ = tm.entry_session(self.acc('20150219120000'), self.s)
        self.assertEqual(e, pd.Timestamp('2015-02-20'))

    def test_after_hours_enters_next_session(self):
        e, _ = tm.entry_session(self.acc('20150219162634'), self.s)
        self.assertEqual(e, pd.Timestamp('2015-02-20'))

    def test_friday_after_hours_enters_monday(self):
        e, _ = tm.entry_session(self.acc('20150220170000'), self.s)   # Friday
        self.assertEqual(e, pd.Timestamp('2015-02-23'))

    def test_friday_late_evening_filing_dated_next_business_day_still_monday(self):
        # EDGAR assigns filings accepted after 17:30 ET the next business day's filing date; the open used is still Monday's.
        e, _ = tm.entry_session(self.acc('20150220213000'), self.s)
        self.assertEqual(e, pd.Timestamp('2015-02-23'))

    def test_weekend_filing_enters_monday(self):
        e, cat = tm.entry_session(self.acc('20150221100000'), self.s)   # Saturday
        self.assertEqual(e, pd.Timestamp('2015-02-23')); self.assertEqual(cat, 'non_session_day')

    def test_holiday_filing_enters_next_session(self):
        # Presidents' Day 2015-02-16 (Monday) is closed
        self.assertNotIn(pd.Timestamp('2015-02-16'), self.s)
        e, cat = tm.entry_session(self.acc('20150216080000'), self.s)
        self.assertEqual(e, pd.Timestamp('2015-02-17')); self.assertEqual(cat, 'non_session_day')

    def test_day_before_holiday_after_hours_skips_holiday(self):
        e, _ = tm.entry_session(self.acc('20150213170000'), self.s)   # Friday before Presidents' Day
        self.assertEqual(e, pd.Timestamp('2015-02-17'))

    def test_hurricane_sandy_closure_is_not_a_session(self):
        self.assertNotIn(pd.Timestamp('2012-10-29'), self.s); self.assertNotIn(pd.Timestamp('2012-10-30'), self.s)
        e, _ = tm.entry_session(self.acc('20121026170000'), self.s)   # Friday before the closure
        self.assertEqual(e, pd.Timestamp('2012-10-31'))

    def test_dst_transition_morning_still_uses_local_clock(self):
        # 2015-03-09 (Monday after the spring-forward Sunday): 08:29:59 local is before the cutoff
        e, _ = tm.entry_session(self.acc('20150309082959'), self.s)
        self.assertEqual(e, pd.Timestamp('2015-03-09'))

    def test_delay_sensitivity_adds_one_session(self):
        e0, _ = tm.entry_session(self.acc('20150219120000'), self.s, delay=0)
        e1, _ = tm.entry_session(self.acc('20150219120000'), self.s, delay=1)
        self.assertEqual(self.s.get_loc(e1) - self.s.get_loc(e0), 1)

    def test_no_session_left_returns_none(self):
        e, _ = tm.entry_session(self.acc('20171229170000'), self.s)
        self.assertIsNone(e)

    def test_naive_datetime_rejected(self):
        with self.assertRaises(ValueError):
            tm.entry_session(datetime(2015, 2, 19, 12, 0, 0), self.s)


class ExitAndScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = sessions()

    def test_exit_is_hold_sessions_after_entry(self):
        x, trunc = tm.exit_session(pd.Timestamp('2015-02-20'), self.s, 252)
        self.assertEqual(self.s.get_loc(x) - self.s.get_loc(pd.Timestamp('2015-02-20')), 252); self.assertFalse(trunc)

    def test_exit_truncated_at_last_development_session(self):
        x, trunc = tm.exit_session(pd.Timestamp('2017-06-01'), self.s, 252)
        self.assertEqual(x, pd.Timestamp('2017-12-29')); self.assertTrue(trunc)

    def test_schedule_frame_and_lock(self):
        acc = [tm.parse_acceptance('20150219162634'), tm.parse_acceptance('20171228170000')]
        df = tm.schedule(acc, self.s, hold=252)
        self.assertEqual(df.loc[0, 'entry'], pd.Timestamp('2015-02-20')); self.assertEqual(df.loc[0, 'timing'], 'after_close')
        self.assertEqual(df.loc[1, 'entry'], pd.Timestamp('2017-12-29')); self.assertTrue(df.loc[1, 'truncated'])
        self.assertTrue(lk.guard_dates(df['exit'], 'x'))

    def test_sessions_from_open_matches_xnys(self):
        # a vendor open series with NaN on the Sandy closure yields the same sessions as the reference calendar
        ref = self.s[(self.s >= '2012-10-01') & (self.s <= '2012-11-30')]
        idx = pd.date_range('2012-10-01', '2012-11-30', freq='B')
        op = pd.Series(100.0, index=idx)
        op[~idx.isin(ref)] = np.nan
        self.assertTrue(tm.sessions_from_open(op).equals(ref))

    def test_sessions_from_open_refuses_locked_dates(self):
        op = pd.Series(1.0, index=pd.date_range('2017-12-20', '2018-01-05', freq='B'))
        with self.assertRaises(lk.Phase8BLockError):
            tm.sessions_from_open(op)

    def test_timing_categories(self):
        self.assertEqual(tm.timing_category(tm.parse_acceptance('20150219060000')), 'pre_open_by_0830')
        self.assertEqual(tm.timing_category(tm.parse_acceptance('20150219090000')), 'pre_open_after_0830')
        self.assertEqual(tm.timing_category(tm.parse_acceptance('20150219120000')), 'intraday')
        self.assertEqual(tm.timing_category(tm.parse_acceptance('20150219160000')), 'after_close')


if __name__ == '__main__':
    unittest.main()
