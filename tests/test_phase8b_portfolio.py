import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase8b_portfolio as pf  # noqa: E402
import phase8b_lock as lk  # noqa: E402

ZERO = {'ZERO': dict(buy=0.0, sell=0.0, buy_far=0.0, sell_far=0.0)}


def calendar(n=60, start='2015-01-02'):
    return pd.DatetimeIndex(pd.bdate_range(start, periods=n))


def panel(cal, **cols):
    return pd.DataFrame({k: np.asarray(v, dtype=float) for k, v in cols.items()}, index=cal)


def events(rows):
    return pd.DataFrame(rows)


class SingleEventTests(unittest.TestCase):
    def test_gross_return_equals_open_to_open(self):
        cal = calendar(); ao = panel(cal, A=np.linspace(10, 20, len(cal)))
        ev = events([dict(event_id='e1', code='A', entry_idx=5, exit_idx=15, rank=100)])
        out = pf.simulate_hold_all(ev, ao, cal, cost_case='ZERO', costs=ZERO)
        eq = out['equity']
        self.assertAlmostEqual(eq.iloc[-1] / eq.iloc[0], ao['A'].iloc[15] / ao['A'].iloc[5], places=10)
        self.assertEqual(out['counters']['entries'], 1); self.assertEqual(out['counters']['exits'], 1)
        self.assertEqual(int(out['trades'].loc[0, 'exit_idx']), 15)

    def test_costs_charged_per_side(self):
        cal = calendar(); ao = panel(cal, A=np.full(len(cal), 10.0))
        ev = events([dict(event_id='e1', code='A', entry_idx=5, exit_idx=15, rank=100)])
        out = pf.simulate_hold_all(ev, ao, cal, cost_case='MANUAL_USD')
        eq = out['equity']
        expected = (1 - 0.0005) * (1 - 0.00053)
        self.assertAlmostEqual(eq.iloc[-1], expected, places=10)
        far = pf.simulate_hold_all(events([dict(event_id='e1', code='A', entry_idx=5, exit_idx=15, rank=800)]), ao, cal, cost_case='MANUAL_USD')
        self.assertAlmostEqual(far['equity'].iloc[-1], (1 - 0.0010) * (1 - 0.00103), places=10)
        unk = pf.simulate_hold_all(events([dict(event_id='e1', code='A', entry_idx=5, exit_idx=15, rank=np.nan)]), ao, cal, cost_case='MANUAL_USD')
        self.assertAlmostEqual(unk['equity'].iloc[-1], far['equity'].iloc[-1], places=12)

    def test_delisting_haircut_and_forced_exit(self):
        cal = calendar(); a = np.full(len(cal), 10.0); a[20:] = np.nan; ao = panel(cal, A=a)
        ev = events([dict(event_id='e1', code='A', entry_idx=5, exit_idx=40, rank=100)])
        info = {'A': dict(last_idx=19, drop126=-0.6, last_close=0.5)}
        out = pf.simulate_hold_all(ev, ao, cal, ended_info=info, venue={'A': 'NASDAQ'}, cost_case='ZERO', costs=ZERO)
        self.assertEqual(out['counters']['delisted'], 1)
        self.assertAlmostEqual(out['equity'].iloc[-1], 0.45, places=10)
        self.assertTrue(bool(out['trades'].loc[0, 'delisted'])); self.assertEqual(int(out['trades'].loc[0, 'exit_idx']), 20)

    def test_no_price_at_entry_is_skipped(self):
        cal = calendar(); a = np.full(len(cal), 10.0); a[5] = np.nan; ao = panel(cal, A=a)
        ev = events([dict(event_id='e1', code='A', entry_idx=5, exit_idx=15, rank=100)])
        out = pf.simulate_hold_all(ev, ao, cal, cost_case='ZERO', costs=ZERO)
        self.assertEqual(out['counters']['skipped_noprice'], 1); self.assertEqual(out['counters']['entries'], 0)


class MultiEventTests(unittest.TestCase):
    def test_re_equalisation_on_second_entry(self):
        cal = calendar(); ao = panel(cal, A=np.full(len(cal), 10.0), B=np.full(len(cal), 5.0))
        ao.loc[cal[8:], 'A'] = 20.0                                             # A doubles before B enters
        ev = events([dict(event_id='e1', code='A', entry_idx=5, exit_idx=50, rank=100), dict(event_id='e2', code='B', entry_idx=10, exit_idx=50, rank=100)])
        out = pf.simulate_hold_all(ev, ao, cal, cost_case='ZERO', costs=ZERO)
        eq = out['equity']
        self.assertAlmostEqual(eq.loc[cal[10]], 2.0, places=10)                # equity doubled with A (series starts at the first entry)
        self.assertAlmostEqual(out['legs']['rebalance'], 1.0, places=10)       # A trimmed from 2.0 to 1.0
        self.assertAlmostEqual(out['legs']['entry'], 2.0, places=10)           # A 1.0 at entry + B 1.0
        self.assertEqual(out['counters']['rebalance_days'], 3)                 # entry A, entry B, exits
        # after the second entry both positions carry half the book: a 10% move in B alone moves equity 5%
        ao2 = ao.copy(); ao2.loc[cal[12:], 'B'] = 5.5
        eq2 = pf.simulate_hold_all(ev, ao2, cal, cost_case='ZERO', costs=ZERO)['equity']
        self.assertAlmostEqual(eq2.loc[cal[12]] / eq2.loc[cal[11]], 1.05, places=10)

    def test_same_issuer_active_opens_no_second_position(self):
        cal = calendar(); ao = panel(cal, A=np.full(len(cal), 10.0))
        ev = events([dict(event_id='e1', code='A', entry_idx=5, exit_idx=15, rank=100), dict(event_id='e2', code='A', entry_idx=10, exit_idx=30, rank=100)])
        out = pf.simulate_hold_all(ev, ao, cal, cost_case='ZERO', costs=ZERO)
        self.assertEqual(out['counters']['skipped_held'], 1); self.assertEqual(out['counters']['entries'], 1)
        self.assertEqual(int(out['trades'].loc[0, 'exit_idx']), 15)          # no extension

    def test_no_trading_on_quiet_days(self):
        cal = calendar(); rng = np.random.default_rng(0)
        ao = panel(cal, A=10 * np.cumprod(1 + rng.normal(0, 0.02, len(cal))), B=5 * np.cumprod(1 + rng.normal(0, 0.02, len(cal))))
        ev = events([dict(event_id='e1', code='A', entry_idx=5, exit_idx=40, rank=100), dict(event_id='e2', code='B', entry_idx=5, exit_idx=40, rank=100)])
        out = pf.simulate_hold_all(ev, ao, cal, cost_case='ZERO', costs=ZERO)
        self.assertEqual(out['counters']['rebalance_days'], 2)
        self.assertAlmostEqual(out['legs']['rebalance'], 0.0, places=12)
        # buy-and-hold between: equity = 0.5 * A/A0 + 0.5 * B/B0
        eq = out['equity']; k = 30
        self.assertAlmostEqual(eq.iloc[k - 5], 0.5 * ao['A'].iloc[k] / ao['A'].iloc[5] + 0.5 * ao['B'].iloc[k] / ao['B'].iloc[5], places=10)

    def test_delay_shifts_entry_and_exit(self):
        cal = calendar(); ao = panel(cal, A=np.linspace(10, 20, len(cal)))
        ev = events([dict(event_id='e1', code='A', entry_idx=5, exit_idx=15, rank=100)])
        out = pf.simulate_hold_all(ev, ao, cal, cost_case='ZERO', costs=ZERO, delay=1)
        tr = out['trades'].iloc[0]
        self.assertEqual((int(tr['entry_idx']), int(tr['exit_idx'])), (6, 16))

    def test_turnover_is_reported_one_way(self):
        cal = calendar(252); ao = panel(cal, A=np.full(252, 10.0))
        ev = events([dict(event_id='e1', code='A', entry_idx=0, exit_idx=251, rank=100)])
        out = pf.simulate_hold_all(ev, ao, cal, cost_case='ZERO', costs=ZERO)
        self.assertAlmostEqual(out['turnover']['oneway_total'], 1.0, places=6)

    def test_locked_calendar_raises(self):
        cal = pd.DatetimeIndex(pd.bdate_range('2017-12-20', periods=20)); ao = panel(cal, A=np.full(20, 10.0))
        with self.assertRaises(lk.Phase8BLockError):
            pf.simulate_hold_all(events([dict(event_id='e1', code='A', entry_idx=1, exit_idx=5, rank=100)]), ao, cal, cost_case='ZERO', costs=ZERO)


if __name__ == '__main__':
    unittest.main()
