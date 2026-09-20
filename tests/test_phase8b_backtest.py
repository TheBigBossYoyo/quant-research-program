import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase8b_backtest as bt  # noqa: E402


class ClusterStatsTests(unittest.TestCase):
    def test_cluster_bootstrap_widens_with_dependence(self):
        rng = np.random.default_rng(0)
        clusters = np.repeat(np.arange(40), 25)
        shock = rng.normal(0, 1, 40)[clusters]
        x = shock + rng.normal(0, 0.1, len(clusters))
        dep = bt.cluster_stats(x, clusters, draws=300)
        iid = bt.cluster_stats(x, np.arange(len(x)), draws=300)
        self.assertGreater(dep['ci'][1] - dep['ci'][0], 2 * (iid['ci'][1] - iid['ci'][0]))
        self.assertEqual(dep['n_clusters'], 40)

    def test_small_sample_returns_nan_mean(self):
        self.assertTrue(np.isnan(bt.cluster_stats([1, 2, 3], [1, 2, 3])['mean']))


class GateTests(unittest.TestCase):
    def base(self):
        w = dict(excess_ann=0.05, excess_t=2.5, years_positive=4, capm_alpha_ann=0.04, capm_t=2.0, ff6_alpha_ann=0.03, ff6_t=1.2, max_dd=-0.3, spy_max_dd=-0.5,
                 yearly_excess={2013: 0.05, 2014: 0.05, 2015: 0.05, 2016: 0.05, 2017: 0.05})
        e = dict(excess_ann=0.01, yearly_excess={y: 0.01 for y in range(2004, 2013)})
        f = dict(max_dd=-0.4, spy_max_dd=-0.5, yearly_excess={**e['yearly_excess'], **w['yearly_excess']})
        ws = dict(w2013_2017=w, w2004_2012=e, w2004_2017=f)
        trades = pd.DataFrame(dict(event_id=[f'e{i}' for i in range(40)], code=[f'C{i}' for i in range(40)], pnl=np.full(40, 0.01)))
        ev = pd.DataFrame(dict(event_id=[f'e{i}' for i in range(40)], sic=[str(1000 + 100 * i) for i in range(40)]))   # 40 distinct 2-digit SICs
        study = dict(h252=dict(w2013_2017=dict(ar_ew_month=dict(mean=0.05, t=2.5), ar_ew_cik=dict(mean=0.05, t=2.2)), w2004_2017=dict(ar_ew_month=dict(mean=0.03, t=2.0))))
        return ws, trades, ev, study

    def test_all_pass(self):
        ws, tr, ev, st = self.base()
        g = bt.gates(ws, dict(w2013_2017=dict(excess_ann=0.01)), tr, ev, st, 200, 400, 1.5, 0.95)
        self.assertTrue(all(g['checks'].values()), g['checks'])

    def test_individual_failures(self):
        ws, tr, ev, st = self.base()
        auto = dict(w2013_2017=dict(excess_ann=0.01))
        self.assertFalse(bt.gates(ws, dict(w2013_2017=dict(excess_ann=-0.01)), tr, ev, st, 200, 400, 1.5, 0.95)['checks']['G7_automated'])
        self.assertFalse(bt.gates(ws, auto, tr, ev, st, 100, 400, 1.5, 0.95)['checks']['G10_sample'])
        self.assertFalse(bt.gates(ws, auto, tr, ev, st, 200, 400, 3.5, 0.95)['checks']['G6_turnover'])
        self.assertFalse(bt.gates(ws, auto, tr, ev, st, 200, 400, 1.5, 0.5)['checks']['G12_dsr'])
        st2 = dict(h252=dict(w2013_2017=dict(ar_ew_month=dict(mean=0.05, t=2.5), ar_ew_cik=dict(mean=0.05, t=1.5)), w2004_2017=dict(ar_ew_month=dict(mean=0.03, t=2.0))))
        self.assertFalse(bt.gates(ws, auto, tr, ev, st2, 200, 400, 1.5, 0.95)['checks']['G11_event_study'])   # weaker cluster t decides
        ws2 = {**ws, 'w2013_2017': {**ws['w2013_2017'], 'ff6_alpha_ann': 0.01}}
        self.assertFalse(bt.gates(ws2, auto, tr, ev, st, 200, 400, 1.5, 0.95)['checks']['G4_alpha'])          # style-controlled alpha required
        tr2 = tr.copy(); tr2.loc[0, 'pnl'] = 1.0
        g = bt.gates(ws, auto, tr2, ev, st, 200, 400, 1.5, 0.95)
        self.assertFalse(g['checks']['G8_concentration']); self.assertGreater(g['top_ticker_share'], 0.5)

    def test_early_window_rule(self):
        ws, tr, ev, st = self.base(); auto = dict(w2013_2017=dict(excess_ann=0.01))
        ws['w2004_2012']['excess_ann'] = -0.02
        self.assertTrue(bt.gates(ws, auto, tr, ev, st, 200, 400, 1.5, 0.95)['checks']['G9_early'])     # late window carries
        ws['w2013_2017']['excess_t'] = 1.0
        self.assertFalse(bt.gates(ws, auto, tr, ev, st, 200, 400, 1.5, 0.95)['checks']['G9_early'])


class RefusalTests(unittest.TestCase):
    def test_gate_record_detection(self):
        self.assertFalse(bt.gate_recorded())      # no classifier gate has passed in the repository at this point


if __name__ == '__main__':
    unittest.main()
