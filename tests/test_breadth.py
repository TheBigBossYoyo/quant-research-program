import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from breadth_timing import aggregate_features,btc_forward

class BreadthTests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(7);self.days=pd.date_range('2022-01-01',periods=120,freq='D',tz='UTC');syms=[f'S{i}' for i in range(12)]+['BTCUSDT']
        close=pd.DataFrame(100*np.cumprod(1+rng.normal(0,.03,(120,13)),axis=0),index=self.days,columns=syms)
        self.panels=dict(close=close,open=close.copy())
        self.feat=dict(fund7=pd.DataFrame(rng.normal(0,.001,(120,13)),index=self.days,columns=syms))
        self.elig=pd.DataFrame(True,index=self.days,columns=syms)
    def test_aggregates_use_only_eligible_names_and_are_bounded(self):
        a=aggregate_features(self.panels,self.feat,self.elig)
        self.assertTrue(a.breadth30.dropna().between(0,1).all());self.assertTrue(a.breadth30.iloc[:30].isna().all())
        e2=self.elig.copy();e2.iloc[:,:2]=False;b=aggregate_features(self.panels,self.feat,e2)
        self.assertFalse(np.allclose(a.agg_fund7.iloc[40:],b.agg_fund7.iloc[40:]))
        self.assertAlmostEqual(b.agg_fund7.iloc[40],self.feat["fund7"].iloc[40,2:].mean())
        e3=self.elig.copy();e3.iloc[:,:5]=False;e3.iloc[:,5:9]=False  # 4 names left -> NaN
        self.assertTrue(aggregate_features(self.panels,self.feat,e3).agg_fund7.isna().all())
    def test_prefix_invariance_and_target_alignment(self):
        a=aggregate_features(self.panels,self.feat,self.elig)
        p2=dict(close=self.panels['close'].copy(),open=self.panels['open'].copy());p2['close'].iloc[80:]*=4
        b=aggregate_features(p2,self.feat,self.elig)
        pd.testing.assert_series_equal(a.breadth30.iloc[:80],b.breadth30.iloc[:80])
        o=self.panels['open'];f=btc_forward(o)
        self.assertAlmostEqual(f.iloc[0],o['BTCUSDT'].iloc[9]/o['BTCUSDT'].iloc[2]-1)

if __name__=='__main__':unittest.main()
