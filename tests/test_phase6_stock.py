import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase6_stock_universe as su  # noqa: E402
import phase6_stock_engine as se  # noqa: E402


def synthetic_panel(n_days=800, seed=1, codes=('A', 'B', 'C', 'D')):
    rng = np.random.default_rng(seed)
    cal = pd.bdate_range('2010-01-01', periods=n_days)
    close = pd.DataFrame(index=cal, columns=list(codes), dtype=float)
    for c in codes:
        close[c] = 20.0 * np.exp(np.cumsum(rng.normal(0.0002, 0.01, n_days)))
    open_ = close * (1 + rng.normal(0, 0.002, close.shape))
    adj = close * 0.9   # constant dividend factor
    vol = pd.DataFrame(2e5, index=cal, columns=list(codes))
    sf = pd.DataFrame(1.0, index=cal, columns=list(codes))
    return cal, open_, close, adj, vol, sf


class UniverseTests(unittest.TestCase):
    def test_month_end_dates_and_next_open(self):
        cal = pd.bdate_range('2015-01-01', '2015-03-31')
        me = su.month_end_dates(cal)
        self.assertEqual([d.date().isoformat() for d in me], ['2015-01-30', '2015-02-27', '2015-03-31'])
        nx = su.next_open_dates(cal, me)
        self.assertEqual(nx[0], pd.Timestamp('2015-02-02'))
        self.assertTrue(pd.isna(nx[-1]))

    def test_momentum_uses_only_prices_before_signal_month(self):
        idx = pd.period_range('2010-01', '2011-12', freq='M').to_timestamp('M')
        mp = pd.DataFrame({'A': np.arange(1, 25, dtype=float)}, index=idx)
        mom = su.momentum(mp, 12, 1)
        # at month 13 (index 12): P[11]/P[0] - 1 = 12/1 - 1
        self.assertAlmostEqual(mom.iloc[12, 0], 11.0)
        self.assertTrue(np.isnan(mom.iloc[11, 0]))
        # perturbing the signal-month price must not change the signal
        mp2 = mp.copy(); mp2.iloc[12, 0] = 999.0
        self.assertAlmostEqual(su.momentum(mp2, 12, 1).iloc[12, 0], 11.0)
        # perturbing a future price must not change any earlier signal
        mp3 = mp.copy(); mp3.iloc[20, 0] = 999.0
        self.assertTrue(su.momentum(mp3, 12, 1).iloc[:20, 0].equals(mom.iloc[:20, 0]))

    def test_eligibility_filters(self):
        feat = pd.DataFrame(dict(price=[10, 4, 10, 10, 10], med_dv=[5e6, 5e6, 5e5, 5e6, np.nan],
                                 history=[300, 300, 300, 100, 300], complete=[True] * 5, no_zero=[True] * 5),
                            index=list('ABCDE'))
        ok, rank = su.eligibility(feat)
        self.assertEqual(list(ok[ok].index), ['A'])
        member = pd.Series({'A': False, 'B': True, 'C': True, 'D': True, 'E': True})
        ok2, _ = su.eligibility(feat, membership=member, liquidity_rank=False)
        self.assertEqual(list(ok2[ok2].index), ['C', 'E'])   # Tier 1: membership replaces the liquidity rank

    def test_features_are_lagged(self):
        cal, open_, close, adj, vol, sf = synthetic_panel()
        me = su.month_end_dates(cal)
        feats = su.features_at(me[-2:], close, adj, vol, sf)
        t = me[-2]
        i = cal.get_loc(t)
        f = feats[t]
        self.assertEqual(f.loc['A', 'history'], i)           # priced days strictly before t
        self.assertAlmostEqual(f.loc['A', 'price'], close.loc[t, 'A'])
        expected = (close['A'] * vol['A']).iloc[i - 62:i + 1].median()
        self.assertAlmostEqual(f.loc['A', 'med_dv'], expected)

    def test_holding_returns_are_open_to_open_after_signal(self):
        cal, open_, close, adj, vol, sf = synthetic_panel()
        me = su.month_end_dates(cal)
        ex = su.next_open_dates(cal, me[:-1])
        ret, ended = su.holding_returns(open_, close, adj, ex, cal, cal[-1])
        d0, d1 = ex[0], ex[1]
        ao = open_ * adj / close
        self.assertAlmostEqual(ret.loc[d0, 'A'], ao.loc[d1, 'A'] / ao.loc[d0, 'A'] - 1)
        self.assertTrue(d0 > me[0])
        self.assertEqual(ended, {})

    def test_delisting_inside_month_books_last_close_and_flags_distress(self):
        cal, open_, close, adj, vol, sf = synthetic_panel()
        me = su.month_end_dates(cal)
        ex = su.next_open_dates(cal, me[:-1])
        # kill ticker B ten days into the tenth holding month after a 60% collapse (>126 days of history exist)
        d0 = ex[9]
        pos = cal.get_loc(d0)
        stop = cal[pos + 10]
        for f in (open_, close, adj):
            f.loc[stop:, 'B'] = np.nan
            f.loc[cal[pos + 1]:stop, 'B'] = f.loc[cal[pos + 1]:stop, 'B'] * 0.4
        ret, ended = su.holding_returns(open_, close, adj, ex, cal, cal[-1])
        self.assertIn((d0, 'B'), ended)
        self.assertLess(ret.loc[d0, 'B'], -0.5)
        self.assertLessEqual(ended[(d0, 'B')]['drop126'], -0.5)
        self.assertAlmostEqual(su.delisting_haircut(ended[(d0, 'B')], 'NYSE'), -0.30)
        self.assertAlmostEqual(su.delisting_haircut(ended[(d0, 'B')], 'NASDAQ'), -0.55)
        self.assertAlmostEqual(su.delisting_haircut(ended[(d0, 'B')], 'NYSE', 'all100'), -1.0)
        self.assertAlmostEqual(su.delisting_haircut(dict(drop126=-0.1, last_close=20.0), 'NYSE'), 0.0)
        self.assertAlmostEqual(su.delisting_haircut(dict(drop126=-0.1, last_close=20.0), 'NYSE', 'all30'), -0.30)

    def test_residual_momentum_shape_and_causality(self):
        idx = pd.period_range('2005-01', '2011-12', freq='M').to_timestamp('M')
        rng = np.random.default_rng(3)
        mp = pd.DataFrame(np.exp(np.cumsum(rng.normal(0.005, 0.05, (len(idx), 3)), axis=0)), index=idx, columns=list('XYZ'))
        f = pd.DataFrame(rng.normal(0, 0.03, (len(idx), 3)), index=idx, columns=['Mkt-RF', 'SMB', 'HML'])
        f['RF'] = 0.001
        rm = su.residual_momentum(mp, f)
        self.assertTrue(rm.iloc[:36].isna().all().all())
        self.assertTrue(rm.iloc[36:].notna().all().all())
        mp2 = mp.copy(); mp2.iloc[40:, :] = mp2.iloc[40:, :] * 3
        self.assertTrue(np.allclose(su.residual_momentum(mp2, f).iloc[:40].fillna(0), rm.iloc[:40].fillna(0)))


class EngineTests(unittest.TestCase):
    def frames(self):
        sig = pd.DatetimeIndex(['2015-01-30', '2015-02-27', '2015-03-31'])
        ex = pd.DatetimeIndex(['2015-02-02', '2015-03-02'])
        scores = pd.DataFrame([[3, 2, 1], [1, 2, 3], [1, 1, 1]], index=sig, columns=list('ABC'), dtype=float)
        elig = pd.DataFrame(True, index=sig, columns=list('ABC'))
        ret = pd.DataFrame([[0.10, 0.00, -0.05], [0.02, 0.02, 0.02]], index=ex, columns=list('ABC'))
        return sig, ex, scores, elig, ret

    def test_top_n_selection_costs_and_turnover(self):
        sig, ex, scores, elig, ret = self.frames()
        out = se.simulate(scores, elig, ret, n=2, cost_case='base')
        m = out['monthly']
        self.assertEqual(out['holdings'][sig[0]], ['A', 'B'])
        self.assertAlmostEqual(m.loc[sig[0], 'gross'], 0.05)
        self.assertAlmostEqual(m.loc[sig[0], 'turnover_buy'], 1.0)
        self.assertAlmostEqual(m.loc[sig[0], 'cost'], 1.0 * 0.0020)
        self.assertAlmostEqual(m.loc[sig[0], 'net'], (1 - 0.002) * 1.05 - 1)
        # month 2: holdings drift to A 0.55/1.05, B 0.5/1.05; new picks C, B -> sell all A, buy C 0.5, adjust B
        drift_a, drift_b = 0.55 / 1.05, 0.50 / 1.05
        buys = 0.5 + max(0.5 - drift_b, 0)
        sells = drift_a + max(drift_b - 0.5, 0)
        self.assertAlmostEqual(m.loc[sig[1], 'turnover_buy'], buys)
        self.assertAlmostEqual(m.loc[sig[1], 'turnover_sell'], sells)
        self.assertEqual(len(m), 2)   # last signal date has no return

    def test_ineligible_and_nan_scores_are_never_selected(self):
        sig, ex, scores, elig, ret = self.frames()
        elig.loc[sig[0], 'A'] = False
        scores.loc[sig[0], 'B'] = np.nan
        out = se.simulate(scores, elig, ret, n=2)
        self.assertEqual(out['holdings'][sig[0]], ['C'])

    def test_delisting_haircut_and_exposure(self):
        sig, ex, scores, elig, ret = self.frames()
        ended = {(ex[0], 'A'): dict(drop126=-0.7, last_close=0.5)}
        out = se.simulate(scores, elig, ret, n=1, ended=ended, venue={'A': 'NASDAQ'},
                          haircut=lambda info, v: -0.55 if v == 'NASDAQ' else -0.3, cost_case='optimistic')
        self.assertAlmostEqual(out['monthly'].iloc[0]['gross'], 1.10 * 0.45 - 1)
        self.assertEqual(out['monthly'].iloc[0]['delisted'], 1)
        expo = pd.Series([0.5, 0.0, 1.0], index=sig)
        out2 = se.simulate(scores, elig, ret, n=1, cost_case='optimistic', exposure=expo)
        self.assertAlmostEqual(out2['monthly'].iloc[0]['gross'], 0.05)
        self.assertAlmostEqual(out2['monthly'].iloc[1]['gross'], 0.0)

    def test_stress_case_uses_rank_dependent_costs(self):
        sig, ex, scores, elig, ret = self.frames()
        rank = pd.DataFrame([[1, 600, 2], [1, 600, 2], [1, 1, 1]], index=sig, columns=list('ABC'), dtype=float)
        out = se.simulate(scores, elig, ret, rank=rank, n=2, cost_case='stress')
        self.assertAlmostEqual(out['monthly'].iloc[0]['cost'], 0.5 * 0.0030 + 0.5 * 0.0045)

    def test_equal_weight_benchmark_has_no_cost(self):
        sig, ex, scores, elig, ret = self.frames()
        b = se.equal_weight_benchmark(elig, ret)
        self.assertAlmostEqual(b.iloc[0]['net'], (0.10 + 0.0 - 0.05) / 3)
        self.assertAlmostEqual(b.iloc[0]['cost'], 3 * (1 / 3) * 0.0003)  # reported but not applied
        self.assertEqual(b.iloc[0]['n_held'], 3)


if __name__ == '__main__':
    unittest.main()


class PanelLockTests(unittest.TestCase):
    def test_load_panel_refuses_locked_segments_before_reading(self):
        import phase6_eodhd_panel as pnl
        from phase6_lock import LockError
        for seg in ('validation', 'holdout'):
            with self.assertRaises(LockError):
                pnl.load_panel('close', segment=seg)
        with self.assertRaises(KeyError):
            pnl.load_panel('not_a_field')


class IntegrityTests(unittest.TestCase):
    def test_extreme_day_makes_name_unclean_for_252_days(self):
        cal, open_, close, adj, vol, sf = synthetic_panel(n_days=900)
        me = su.month_end_dates(cal)
        k = 300
        close.iloc[k, 0] = close.iloc[k - 1, 0] * 5.0          # +400% day for ticker A
        close.iloc[k + 1:, 0] = close.iloc[k + 1:, 0] * 5.0
        adj = close * 0.9
        unclean, incons12 = su.integrity_panels(close, adj, sf, me)
        self.assertTrue(unclean.iloc[k, 0])
        self.assertTrue(unclean.iloc[k + 251, 0])
        self.assertFalse(unclean.iloc[k + 252, 0])
        self.assertFalse(unclean.iloc[k - 1, 0])
        self.assertFalse(unclean['B'].any())
        feats = su.features_at([me[-1]], close, adj, vol, sf, integrity=(unclean, incons12))
        self.assertTrue(feats[me[-1]].loc['B', 'clean'])

    def test_inconsistent_adjusted_month_blocks_eligibility_for_12_months(self):
        cal, open_, close, adj, vol, sf = synthetic_panel(n_days=900)
        me = su.month_end_dates(cal)
        j = cal.get_loc(me[20])
        adj.iloc[j:, 1] = adj.iloc[j:, 1] * 3.0                # adjusted series jumps without a matching close move
        unclean, incons12 = su.integrity_panels(close, adj, sf, me)
        self.assertTrue(incons12.loc[me[20], 'B'])
        self.assertTrue(incons12.loc[me[31], 'B'])
        self.assertFalse(incons12.loc[me[32], 'B'])
        self.assertFalse(incons12['A'].any())
        feats = su.features_at([me[25]], close, adj, vol, sf, integrity=(unclean, incons12))
        ok, _ = su.eligibility(feats[me[25]])
        self.assertFalse(ok['B'])

    def test_holding_month_substitution_uses_split_adjusted_return(self):
        cal, open_, close, adj, vol, sf = synthetic_panel(n_days=900)
        me = su.month_end_dates(cal)
        ex = su.next_open_dates(cal, me[:-1])
        d0, d1 = ex[5], ex[6]
        adj.loc[d1:, 'C'] = adj.loc[d1:, 'C'] * 4.0          # corrupt adjusted series inside the holding month
        ret, _ = su.holding_returns(open_, close, adj, ex, cal, cal[-1], split_factor=sf)
        expected = open_.loc[d1, 'C'] / open_.loc[d0, 'C'] - 1
        self.assertAlmostEqual(ret.loc[d0, 'C'], expected, places=6)
        self.assertEqual(su.holding_returns.substitutions, 1)

    def test_split_ratio_bounds_and_price_cap(self):
        import gzip, tempfile
        import phase6_eodhd_panel as pnl
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 's.csv.gz'
            with gzip.open(p, 'wt') as fh:
                fh.write('Date,"Stock Splits"\n2001-01-02,2.000000/1.000000\n2002-01-02,1.000000/1000000.000000\n2003-01-02,0.000000/1.000000\n')
            s = pnl.read_splits_csv(p)
            self.assertEqual(list(s.values), [2.0])
            q = Path(tmp) / 'e.csv.gz'
            with gzip.open(q, 'wt') as fh:
                fh.write('Date,Open,High,Low,Close,Adjusted_close,Volume\n2001-01-02,1,1,1,1000000,1000000,10\n2001-01-03,1,1,1,2,2,10\n2001-01-04,1,1,1,0,0.5,10\n')
            df = pnl.read_eod_csv(q)
            self.assertTrue(np.isnan(df['close'].iloc[0]) and np.isnan(df['close'].iloc[2]))
            self.assertEqual(df['close'].iloc[1], 2.0)


class Phase7ASignalTests(unittest.TestCase):
    def test_overnight_and_intraday_components_sum_to_close_to_close(self):
        import phase7a_xs_screen as xs
        cal, open_, close, adj, vol, sf = synthetic_panel(n_days=300)
        so, sc, on, intra = xs.daily_components(open_, close, sf)
        total = np.log(sc / sc.shift(1))
        self.assertTrue(np.allclose((on + intra).iloc[1:], total.iloc[1:]))

    def test_signals_use_only_data_up_to_signal_date(self):
        import phase7a_xs_screen as xs
        cal, open_, close, adj, vol, sf = synthetic_panel(n_days=600)
        me = su.month_end_dates(cal)
        t = me[-3]
        feats = su.features_at([t], close, adj, vol, sf)
        spy = pd.Series(np.random.default_rng(5).normal(0, 0.01, len(cal)), index=cal)
        a = xs.signals_at([t], cal, open_, close, adj, vol, sf, feats, spy)
        i = cal.get_loc(t)
        close2, open2, adj2 = close.copy(), open_.copy(), adj.copy()
        close2.iloc[i + 1:] *= 3.0; open2.iloc[i + 1:] *= 3.0; adj2.iloc[i + 1:] *= 3.0
        b = xs.signals_at([t], cal, open2, close2, adj2, vol, sf, feats, spy)
        for k in a:
            self.assertTrue(np.allclose(a[k].fillna(-9).to_numpy(), b[k].fillna(-9).to_numpy()), k)
        self.assertAlmostEqual(float(a['S1'].loc[t, 'A']), float(close.loc[t, 'A'] / close['A'].iloc[i - 251:i + 1].max()))
        self.assertAlmostEqual(float(a['S9'].loc[t, 'A']), float(adj['A'].pct_change().iloc[i - 20:i + 1].max()))
