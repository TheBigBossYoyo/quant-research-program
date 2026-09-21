"""Phase 9B Stage 0 regression tests: date lock, frozen HAC rule, benchmark construction.

These guard the three places where Stage 0 could silently violate its own preregistration:
leaking a post-2017 observation, drifting the Newey-West lag, or mis-weighting the EWCOV benchmark
when AnalystRevision's interior quintiles are unpopulated.
"""
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))

import phase9b_stage0 as s0  # noqa: E402


class TestFrozenHacRule(unittest.TestCase):
    def test_matches_preregistered_formula(self):
        for n in (50, 96, 120, 156, 180, 400, 1000):
            self.assertEqual(s0.nw_lag(n), int(np.floor(4.0 * (n / 100.0) ** (2.0 / 9.0))))

    def test_preregistered_window_lags(self):
        # Values stated in PHASE9B_STAGE0_PREREGISTRATION.md section 4.
        self.assertEqual(s0.nw_lag(180), 4)   # EARLY 1990-2004
        self.assertEqual(s0.nw_lag(156), 4)   # MODERN 2005-2017
        self.assertEqual(s0.nw_lag(96), 3)    # RECENT 2010-2017

    def test_lag_is_a_function_of_sample_size_only(self):
        rng = np.random.default_rng(0)
        a = pd.Series(rng.normal(size=156))
        b = pd.Series(rng.normal(loc=5.0, scale=9.0, size=156))
        self.assertEqual(s0.nw_tstat(a)[1], s0.nw_tstat(b)[1])


class TestWindows(unittest.TestCase):
    def test_no_window_reaches_2018(self):
        for _, (lo, hi) in s0.WINDOWS.items():
            self.assertLess(pd.Timestamp(hi), s0.LOCK_END)
            self.assertLess(pd.Timestamp(lo), pd.Timestamp(hi))

    def test_decision_window_is_modern(self):
        self.assertEqual(s0.DECISION_WINDOW, 'MODERN_2005_2017')
        self.assertEqual(s0.WINDOWS[s0.DECISION_WINDOW], ('2005-01-01', '2017-12-31'))

    def test_window_slice_excludes_out_of_range(self):
        idx = pd.date_range('2003-01-31', '2019-12-31', freq='ME')
        ser = pd.Series(np.arange(len(idx), dtype=float), index=idx)
        got = s0.window_slice(ser, 'MODERN_2005_2017')
        self.assertGreaterEqual(got.index.min(), pd.Timestamp('2005-01-01'))
        self.assertLess(got.index.max(), s0.LOCK_END)


class TestEwcovBenchmark(unittest.TestCase):
    def _frame(self, rows):
        return pd.DataFrame(rows, columns=['signalname', 'port', 'date', 'ret', 'Nlong'])

    def test_count_weighted_not_simple_mean(self):
        """A month with unpopulated interior bins must weight by Nlong, not average the ports."""
        d = pd.Timestamp('2010-01-31')
        frame = self._frame([
            ('AnalystRevision', '01', d, -0.10, 100),
            ('AnalystRevision', '05', d, 0.10, 900),
            ('AnalystRevision', 'LS', d, 0.20, 900),
        ])
        _, _, ewcov = s0.build_series(frame, 'AnalystRevision')
        # count-weighted: (-0.10*100 + 0.10*900) / 1000 = 0.08; a simple mean would give 0.00
        self.assertAlmostEqual(float(ewcov.loc[d]), 0.08, places=12)

    def test_ls_port_is_excluded_from_the_benchmark(self):
        d = pd.Timestamp('2010-02-28')
        frame = self._frame([
            ('AnalystRevision', '01', d, 0.00, 500),
            ('AnalystRevision', '05', d, 0.04, 500),
            ('AnalystRevision', 'LS', d, 99.0, 500),
        ])
        _, _, ewcov = s0.build_series(frame, 'AnalystRevision')
        self.assertAlmostEqual(float(ewcov.loc[d]), 0.02, places=12)

    def test_long_leg_is_port_05(self):
        d = pd.Timestamp('2010-03-31')
        frame = self._frame([
            ('REV6', '01', d, -0.05, 10),
            ('REV6', '05', d, 0.07, 10),
            ('REV6', 'LS', d, 0.12, 10),
        ])
        _, long_leg, _ = s0.build_series(frame, 'REV6')
        self.assertAlmostEqual(float(long_leg.loc[d]), 0.07, places=12)
        self.assertEqual(s0.LONG_PORT, '05')

    def test_zero_count_ports_are_dropped(self):
        d = pd.Timestamp('2010-04-30')
        frame = self._frame([
            ('REV6', '01', d, 1.0, 0),
            ('REV6', '05', d, 0.03, 50),
        ])
        _, _, ewcov = s0.build_series(frame, 'REV6')
        self.assertAlmostEqual(float(ewcov.loc[d]), 0.03, places=12)


class TestDescribe(unittest.TestCase):
    def test_annualisation_convention(self):
        ser = pd.Series([0.01] * 120)
        rec = s0.describe(ser, 'x')
        self.assertEqual(rec['n'], 120)
        self.assertAlmostEqual(rec['ann_mean'], 0.12, places=12)
        self.assertAlmostEqual(rec['ann_vol'], 0.0, places=12)

    def test_vol_uses_sample_sd_and_sqrt12(self):
        rng = np.random.default_rng(7)
        ser = pd.Series(rng.normal(scale=0.05, size=240))
        rec = s0.describe(ser, 'x')
        self.assertAlmostEqual(rec['ann_vol'], np.sqrt(12.0) * ser.std(ddof=1), places=12)


if __name__ == '__main__':
    unittest.main()
