import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from micro_screen import day_features,forward_returns,LATENCY,STEP

def seconds(n=86400,seed=0):
    rng=np.random.default_rng(seed);price=100+np.cumsum(rng.normal(0,.01,n))
    return pd.DataFrame(dict(second=np.arange(n),trades=1,buy_qty=rng.uniform(0,2,n),sell_qty=rng.uniform(0,2,n),buy_notional=1.,sell_notional=1.,
        first_price=price,last_price=price,max_notional=rng.uniform(1,10,n),max_notional_signed=rng.uniform(1,10,n)*rng.choice([-1,1],n)))

class MicroScreenTests(unittest.TestCase):
    def test_features_use_only_past_seconds_and_snapshots_at_or_before_t(self):
        day=pd.Timestamp('2024-03-05');sec=seconds();ts=pd.to_datetime([day+pd.Timedelta(seconds=s) for s in range(0,86400,30)])
        depth=pd.DataFrame({-1:np.ones(len(ts)),1:np.ones(len(ts))*3,-2:2.,2:4.,-3:3.,3:5.,-4:4.,4:6.,-5:5.,5:7.},index=ts)
        f=day_features(sec,depth,None,day)
        t=f.index[10];self.assertAlmostEqual(f.net_flow_60.loc[t],(sec.buy_qty-sec.sell_qty).iloc[t-60:t].sum())
        self.assertAlmostEqual(f.depth_imb.loc[t],(1-3)/4);self.assertAlmostEqual(f.price.loc[t],sec.last_price.iloc[t-1])
        later=sec.copy();later.iloc[t:,:]=later.iloc[t:,:]*0+999;later['second']=sec.second
        g=day_features(later,depth,None,day);self.assertAlmostEqual(g.net_flow_60.loc[t],f.net_flow_60.loc[t]);self.assertAlmostEqual(g.sweep.loc[t],f.sweep.loc[t])
        # snapshot strictly after t must not be used: shift all snapshots 1 s later and check the one at t is excluded
        depth2=depth.copy();depth2.index=depth.index+pd.Timedelta(seconds=1);depth2.iloc[:,:]=depth2.iloc[:,:]*10
        h=day_features(sec,depth2,None,day);t2=f.index[0]  # t=60: snapshot at 31 s (shifted) is latest <= t
        self.assertAlmostEqual(h.depth_imb.loc[t2],(10-30)/40)
    def test_snapshot_age_limit_yields_nan(self):
        day=pd.Timestamp('2024-03-05');sec=seconds();ts=pd.to_datetime([day]);depth=pd.DataFrame({k:[1.] for k in [-5,-4,-3,-2,-1,1,2,3,4,5]},index=ts)
        f=day_features(sec,depth,None,day);self.assertFalse(np.isnan(f.depth_imb.iloc[0]));self.assertTrue(np.isnan(f.depth_imb.iloc[3]))
    def test_forward_return_alignment_and_end_of_day(self):
        sec=seconds();t=np.array([100,86400-STEP]);r=forward_returns(sec,t,300)
        self.assertAlmostEqual(r[0],sec.first_price.iloc[100+LATENCY+300]/sec.first_price.iloc[100+LATENCY]-1);self.assertTrue(np.isnan(r[1]))
        sec2=sec.copy();sec2.loc[100+LATENCY,'first_price']=np.nan  # no trade in that second: next available trade is used
        self.assertAlmostEqual(forward_returns(sec2,t,300)[0],sec.first_price.iloc[100+LATENCY+300]/sec.first_price.iloc[100+LATENCY+1]-1)
    def test_oi_price_uses_rows_at_or_before_t(self):
        day=pd.Timestamp('2024-03-01');sec=seconds();ts=pd.to_datetime([day+pd.Timedelta(seconds=300*i) for i in range(288)])
        m=pd.DataFrame(dict(sum_open_interest=np.linspace(100,200,288)),index=ts)
        f=day_features(sec,None,m,day);t=1200  # rows at 0,300,600,900,1200 available; prev = row at 300
        expected=(m.sum_open_interest.iloc[4]-m.sum_open_interest.iloc[1])/m.sum_open_interest.iloc[1]*np.sign(sec.last_price.iloc[t-1]-sec.last_price.iloc[t-1-900])
        self.assertAlmostEqual(f.oi_price.loc[t],expected);self.assertTrue(np.isnan(f.oi_price.loc[600]))

if __name__=='__main__':unittest.main()
