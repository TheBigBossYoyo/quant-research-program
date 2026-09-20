import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from core import signal, simulate, metrics, aggregate, config

def frame(prices):
    a=np.asarray(prices,dtype=float)
    return pd.DataFrame(dict(open=a,close=a,high=a,low=a,volume=1.,quote_volume=a,
                             taker_base=.6,trades=1.),index=pd.date_range('2022-01-01',periods=len(a),freq='5min',tz='UTC'))

class CoreTests(unittest.TestCase):
    def test_exact_roundtrip_fees(self):
        d=frame([100]*8); b=simulate(d,signal(d,'buyhold',0),10)
        self.assertAlmostEqual((1+b.net).prod(),.999/1.001)
        self.assertEqual(b.turnover.sum(),2)
    def test_known_pnl(self):
        d=frame([100,100,100,110,120,130])
        b=simulate(d,signal(d,'buyhold',0),10)
        self.assertAlmostEqual((1+b.net).prod(),1.3*.999/1.001)
        self.assertEqual(metrics(b,5)['trades'],1)
    def test_delay(self):
        d=frame([100,200,200,200,200,200]); s=pd.Series(1.,index=d.index)
        self.assertEqual(simulate(d,s,0).gross.sum(),0.)
        self.assertEqual(simulate(d,s,0).position.iloc[:2].sum(),0.)
    def test_prefix_invariance(self):
        d=frame(np.arange(100.,200.)); changed=d.copy(); changed.iloc[70:]*=3
        for f,n in [('momentum',12),('reversal',12),('flow',1),('sma',20)]:
            pd.testing.assert_series_equal(signal(d,f,n).iloc[:70],signal(changed,f,n).iloc[:70])
            pd.testing.assert_series_equal(simulate(d,signal(d,f,n),12).position.iloc[:70],simulate(changed,signal(changed,f,n),12).position.iloc[:70])
    def test_missing_bar_no_fill_and_gap_loss(self):
        d=frame([100,100,100,np.nan,50,50]); s=pd.Series(1.,index=d.index)
        b=simulate(d,s,0)
        self.assertEqual(b.turnover.iloc[3],0.)
        self.assertAlmostEqual((1+b.net).prod(),.5)
    def test_aggregation_gap_not_hidden(self):
        d=frame([100,np.nan,100,100,100,100])
        self.assertTrue(np.isnan(aggregate(d,15).open.iloc[0]))
    def test_zero_volume_prevents_fill(self):
        d=frame([100]*8); d.loc[d.index[2],'volume']=0
        b=simulate(d,signal(d,'buyhold',0),10)
        self.assertEqual(b.turnover.iloc[2],0.)
        self.assertEqual(b.turnover.iloc[3],1.)
    def test_later_outage_does_not_erase_earlier_fill(self):
        d=frame([100]*18); altered=d.copy(); altered.iloc[8]=np.nan
        a=aggregate(d,15); bad=aggregate(altered,15)
        self.assertTrue(np.isnan(bad.open.iloc[2]))
        self.assertEqual(bad.execution_open.iloc[2],100.)
        for x in [a,bad]:
            b=simulate(x,signal(x,'buyhold',0),10)
            self.assertEqual(b.position.iloc[2],1.)
    def test_no_short_or_leverage(self):
        d=frame([100,101,99,104,90,91,92,88,80,100])
        b=simulate(d,signal(d,'reversal',1),12)
        self.assertTrue(b.position.between(0,1).all())
        self.assertFalse(config()['live_trading'])
    def test_missing_signal_history(self):
        d=frame([100,101,np.nan,102,103,104,105])
        self.assertTrue(signal(d,'momentum',3).iloc[4:6].isna().all())
    def test_invalid_delay(self):
        d=frame([100]*8)
        with self.assertRaises(ValueError): simulate(d,signal(d,'buyhold',0),10,delay=1)

if __name__=='__main__': unittest.main()
