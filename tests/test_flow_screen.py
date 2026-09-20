import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from flow_screen import imbalance,resample_bars,forward_return,threshold_target,following_target,block_bootstrap_ic,cell_features

def hourly(n,seed=0):
    rng=np.random.default_rng(seed)
    idx=pd.date_range('2022-01-01',periods=n,freq='h',tz='UTC')
    price=100*np.cumprod(1+rng.normal(0,.01,n))
    vol=rng.uniform(10,20,n);tb=vol*rng.uniform(.3,.7,n)
    return pd.DataFrame(dict(open=price,close=price,volume=vol,taker_base=tb),index=idx)

class FlowTests(unittest.TestCase):
    def test_imbalance_formula(self):
        v=pd.Series([10.,10.,0.,10.]);tb=pd.Series([10.,0.,0.,5.])
        r=imbalance(tb,v,1)
        self.assertEqual(r.iloc[0],1.);self.assertEqual(r.iloc[1],-1.);self.assertTrue(np.isnan(r.iloc[2]));self.assertEqual(r.iloc[3],0.)
        v=pd.Series([10.,30.]);tb=pd.Series([10.,0.])
        self.assertAlmostEqual(imbalance(tb,v,2).iloc[1],(10-30)/40)
        self.assertTrue(np.isnan(imbalance(tb,v,2).iloc[0]))
    def test_prefix_invariance(self):
        f=hourly(400);g=f.copy();g.iloc[300:,:]*=3
        for tf in [1,4]:
            a=cell_features(f,f,tf);b=cell_features(g,g,tf)
            cut=a.index[a.index<f.index[300]]
            for col in ['imb1','imb6','xv1']:
                pd.testing.assert_series_equal(a.loc[cut,col],b.loc[cut,col])
            ta=threshold_target(a.imb1,1,12);tb=threshold_target(b.imb1,1,12)
            pd.testing.assert_series_equal(ta.loc[cut],tb.loc[cut])
    def test_forward_return_alignment(self):
        idx=pd.date_range('2022-01-01',periods=6,freq='h',tz='UTC')
        o=pd.Series([100.,100.,110.,121.,133.1,50.],index=idx)
        r=forward_return(o,1)
        self.assertAlmostEqual(r.iloc[0],.10);self.assertAlmostEqual(r.iloc[1],.10);self.assertTrue(np.isnan(r.iloc[3]))
        self.assertAlmostEqual(forward_return(o,2).iloc[0],.21)
    def test_threshold_rule_causal_and_flat_middle(self):
        idx=pd.date_range('2022-01-01',periods=30,freq='h',tz='UTC')
        s=pd.Series(np.linspace(-1,1,30),index=idx)
        t=threshold_target(s,1,window=12,min_obs=8)
        self.assertTrue(t.iloc[:7].eq(0).all())
        self.assertEqual(t.iloc[29],1.)
        later=s.copy();later.iloc[20:]=-5.
        pd.testing.assert_series_equal(threshold_target(s,1,12,8).iloc[:20],threshold_target(later,1,12,8).iloc[:20])
        cyc=pd.Series(np.tile(np.arange(1.,11.),4),index=pd.date_range('2022-01-01',periods=40,freq='h',tz='UTC'))
        tc=threshold_target(cyc,1,10,10).iloc[9:]
        self.assertTrue((tc[cyc.iloc[9:]>=9]==1.).all());self.assertTrue((tc[cyc.iloc[9:]<=2]==-1.).all())
        self.assertTrue((tc[(cyc.iloc[9:]>2)&(cyc.iloc[9:]<9)]==0.).all())
        self.assertTrue(threshold_target(s,-1,12,8).iloc[29]==-1.)
    def test_following_target_direction_and_nan_flat(self):
        s=pd.Series([.5,-.2,np.nan,0.])
        self.assertEqual(list(following_target(s,-1)),[-1.,1.,0.,0.])
    def test_incomplete_bucket_invalidated(self):
        f=hourly(48);f.iloc[5,:]=np.nan
        b=resample_bars(f,4)
        self.assertTrue(np.isnan(b.volume.iloc[1]));self.assertFalse(np.isnan(b.volume.iloc[2]))
        self.assertEqual(b.open.iloc[0],f.open.iloc[0]);self.assertEqual(b.taker_base.iloc[2],f.taker_base.iloc[8:12].sum())
    def test_bootstrap_ic_sign_and_seed(self):
        rng=np.random.default_rng(1);x=rng.normal(size=3000);y=.3*x+rng.normal(size=3000)
        a=block_bootstrap_ic(x,y,block=24,samples=200,seed=5);b=block_bootstrap_ic(x,y,block=24,samples=200,seed=5)
        self.assertGreater(a['ci_lower_adjusted'],0);self.assertEqual(a['ic'],b['ic']);self.assertEqual(a['ci_lower_adjusted'],b['ci_lower_adjusted'])
        z=block_bootstrap_ic(x,rng.normal(size=3000),block=24,samples=200,seed=5)
        self.assertLess(z['ci_lower_adjusted'],0);self.assertGreater(z['ci_upper_adjusted'],0)

if __name__=='__main__':unittest.main()
