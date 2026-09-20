import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from etf_screen import month_ends,available,signals,ledger,cash_monthly

def frame(n=800,cols=('A','B','C')):
    idx=pd.bdate_range('2012-01-02',periods=n);rng=np.random.default_rng(1)
    adj=pd.DataFrame(100*np.cumprod(1+rng.normal(.0003,.01,(n,len(cols))),axis=0),index=idx,columns=cols)
    return adj,adj.copy(),pd.DataFrame(1000.,index=idx,columns=cols)

class EtfTests(unittest.TestCase):
    def test_universe_entry_after_twelve_months(self):
        adj,close,vol=frame();adj.iloc[:300,1]=np.nan;me=pd.DatetimeIndex(month_ends(adj.index));av=available(adj,me)
        first=adj['B'].first_valid_index();self.assertFalse(av.loc[me[me<first+pd.DateOffset(months=12)],'B'].any());self.assertTrue(av.loc[me[me>=first+pd.DateOffset(months=13)],'B'].all())
        self.assertFalse(av.iloc[:11]['A'].any());self.assertTrue(av.iloc[13:]['A'].all())
    def test_signals_are_causal_and_long_only(self):
        adj,close,vol=frame();me=pd.DatetimeIndex(month_ends(adj.index));cash=pd.Series(0.,index=me)
        s=signals(adj,me,cash);adj2=adj.copy();adj2.iloc[600:]*=3;s2=signals(adj2,me,cash)
        cut=me[me<adj.index[600]]
        for k in s:
            pd.testing.assert_frame_equal(s[k].loc[cut],s2[k].loc[cut]);self.assertTrue((s[k]>=0).all().all());self.assertTrue((s[k].sum(axis=1)<=1+1e-9).all())
        self.assertTrue((s['M_mom12_1'].gt(0).sum(axis=1)<=3).all())
    def test_ledger_known_pnl_cost_and_deferral(self):
        idx=pd.bdate_range('2020-01-01',periods=30);adj=pd.DataFrame(dict(A=np.linspace(100,129,30)),index=idx);close=adj.copy();vol=pd.DataFrame(1000.,index=idx,columns=['A'])
        vol.iloc[6]=0.  # signal day index 5 -> delay 1 -> day 6 not executable -> day 7
        w=pd.DataFrame(dict(A=[1.]),index=[idx[5]]);cash=pd.Series(dtype=float)
        p=ledger(close,adj,vol,w,cost=.01,cash_m=cash)
        self.assertEqual(p.turnover.iloc[6],0.);self.assertEqual(p.turnover.iloc[7],1.)
        self.assertAlmostEqual(p.nav.iloc[7],10000*.99);self.assertAlmostEqual(p.nav.iloc[-1],10000*.99*adj.A.iloc[-1]/adj.A.iloc[7])
    def test_cash_uses_previous_month_rate(self):
        me=pd.DatetimeIndex(['2015-01-30','2015-02-27','2015-03-31']);rate=pd.Series([.12,.24,.36],index=pd.to_datetime(['2014-12-01','2015-01-01','2015-02-01']))
        c=cash_monthly(rate,me);self.assertAlmostEqual(c.iloc[0],.01);self.assertAlmostEqual(c.iloc[1],.02);self.assertAlmostEqual(c.iloc[2],.03)

if __name__=='__main__':unittest.main()
