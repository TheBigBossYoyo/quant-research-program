import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from ta_ensemble import fractional_ledger,ensemble_weight

def bars(o,c=None):
    o=np.asarray(o,float);c=o if c is None else np.asarray(c,float);idx=pd.date_range('2022-01-01',periods=len(o),freq='h',tz='UTC')
    return pd.DataFrame(dict(open=o,high=np.maximum(o,c),low=np.minimum(o,c),close=c,volume=1.,tradable=True),index=idx)

class EnsembleTests(unittest.TestCase):
    def test_fractional_ledger_known_pnl_and_costs(self):
        b=bars([100,100,100,110,110],[100,100,110,110,110]);w=pd.Series([.5,.5,.5,0,0],index=b.index)
        p=fractional_ledger(b,w,0.);self.assertAlmostEqual(p.equity.iloc[2],10000+50*10);self.assertAlmostEqual(p.equity.iloc[-1],10500.)  # 50 units from open bar1, +10 on bar2 close, flat from open bar4
        p2=fractional_ledger(b,w,.001);self.assertAlmostEqual(p2.turnover.iloc[1],5000.);self.assertAlmostEqual(p2.equity.iloc[1],10000-5.)
        self.assertAlmostEqual(p2.turnover.iloc[4],50*110);self.assertAlmostEqual(p2.equity.iloc[-1],10000-5+500-5.5)
    def test_long_only_clip_and_resize(self):
        b=bars([100]*5);w=pd.Series([-1,.5,1.,1.,1.],index=b.index);p=fractional_ledger(b,w,0.,long_only=True)
        self.assertEqual(p.position.iloc[1],0.);self.assertAlmostEqual(p.position.iloc[2],.5);self.assertAlmostEqual(p.position.iloc[3],1.);self.assertAlmostEqual(p.turnover.iloc[3],5000.)
    def test_ensemble_weight_bounds_and_causality(self):
        rng=np.random.default_rng(0);c=pd.Series(100*np.cumprod(1+rng.normal(0,.01,600)));w=ensemble_weight(c);self.assertTrue(w.dropna().between(-1,1).all())
        c2=c.copy();c2.iloc[500:]*=5;pd.testing.assert_series_equal(w.iloc[:500],ensemble_weight(c2).iloc[:500])

if __name__=='__main__':unittest.main()
