import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from ta_engine import run_ledger,metrics,atr,supertrend,rsi,donchian,adx,ema,sma,bollinger

def bars(opens,highs=None,lows=None,closes=None):
    o=np.asarray(opens,float);h=o if highs is None else np.asarray(highs,float);l=o if lows is None else np.asarray(lows,float);c=o if closes is None else np.asarray(closes,float)
    idx=pd.date_range('2022-01-01',periods=len(o),freq='h',tz='UTC')
    return pd.DataFrame(dict(open=o,high=h,low=l,close=c,volume=1.,tradable=True),index=idx)

class LedgerTests(unittest.TestCase):
    def test_next_open_execution_and_known_pnl(self):
        b=bars([100,100,110,121,121,121]);t=pd.Series([1,1,1,0,0,0],index=b.index)  # signal at close of bar0 -> enter open bar1 (100); exit signal at close bar3 -> exit open bar4 (121)
        path,tr=run_ledger(b,t,cost=0.);self.assertEqual(len(tr),1);self.assertAlmostEqual(tr.ret.iloc[0],.21);self.assertAlmostEqual(path.equity.iloc[-1],12100.)
        self.assertEqual(path.position.iloc[0],0.);self.assertEqual(path.position.iloc[1],1.)
        path2,tr2=run_ledger(b,t,cost=.001);self.assertAlmostEqual(path2.equity.iloc[-1],10000/1.001*1.21*(1-.001),places=6)
    def test_short_and_long_only(self):
        b=bars([100,100,90,90,90]);t=pd.Series([-1,-1,0,0,0],index=b.index)
        path,tr=run_ledger(b,t,0.);self.assertAlmostEqual(tr.ret.iloc[0],.10);self.assertEqual(tr.side.iloc[0],-1)
        p2,tr2=run_ledger(b,t,0.,long_only=True);self.assertEqual(len(tr2),0);self.assertAlmostEqual(p2.equity.iloc[-1],10000.)
    def test_stop_fill_and_gap_through(self):
        # ATR=10 constant; stop 2*ATR below entry 100 -> 80. Bar 3 low 75 (open 90): fill at 80. Then a second entry gaps through: open 70 < stop -> fill at open.
        b=bars([100,100,95,90,90,100,100,70,70],highs=[100,100,95,92,90,100,100,72,70],lows=[100,100,95,75,90,100,100,60,70])
        a=pd.Series(10.,index=b.index);t=pd.Series([1,1,1,1,0,1,1,1,0],index=b.index)
        path,tr=run_ledger(b,t,0.,stop_atr=2,atr_series=a)
        self.assertEqual(tr.reason.iloc[0],'stop');self.assertAlmostEqual(tr.ret.iloc[0],-.20)
        self.assertEqual(len(tr),2);self.assertEqual(tr.reason.iloc[1],'stop');self.assertAlmostEqual(tr.ret.iloc[1],70/100-1)  # no re-entry after the stop until the target resets at bar4; re-entry at open bar6 (100), stop 80, bar7 opens 70 -> filled at 70
    def test_trailing_stop_ratchets(self):
        b=bars([100,100,120,140,140,125,125,125],highs=[100,100,120,140,145,130,125,125],lows=[100,100,120,140,140,118,125,125]);a=pd.Series(10.,index=b.index)
        t=pd.Series([1]*8,index=b.index);path,tr=run_ledger(b,t,0.,stop_atr=2,atr_series=a,trail=True)
        self.assertEqual(tr.reason.iloc[0],'stop');self.assertAlmostEqual(tr.ret.iloc[0],125/100-1)  # trail = 145-20 = 125 hit on bar5 (low 118), filled at 125
    def test_funding_sign(self):
        b=bars([100]*4);t=pd.Series([1,1,1,1],index=b.index);f=pd.Series([0,0,.5,0],index=b.index)  # 0.5 USDT per unit charged to longs at bar 2
        path,tr=run_ledger(b,t,0.,funding=f);self.assertAlmostEqual(path.equity.iloc[2],10000-100*.5)
        p2,_=run_ledger(b,-t,0.,funding=f);self.assertAlmostEqual(p2.equity.iloc[2],10000+100*.5)
    def test_untradable_bar_defers_execution(self):
        b=bars([100,100,100,110,110]);b.loc[b.index[1],'tradable']=False;t=pd.Series([1,1,1,1,1],index=b.index)
        path,tr=run_ledger(b,t,0.);self.assertEqual(path.position.iloc[1],0.);self.assertEqual(path.position.iloc[2],1.)

class IndicatorTests(unittest.TestCase):
    def test_prefix_invariance(self):
        rng=np.random.default_rng(0);n=600;c=100*np.cumprod(1+rng.normal(0,.01,n));b=bars(c,c*1.01,c*.99,c);b2=b.copy();b2.iloc[400:,:4]*=3
        for f in [lambda x:ema(x.close,50),lambda x:sma(x.close,50),lambda x:atr(x,14),lambda x:rsi(x.close,14),lambda x:adx(x,14)[0],lambda x:supertrend(x,10,3)[0],lambda x:bollinger(x.close,20,2)[2],lambda x:donchian(x,20)[0]]:
            pd.testing.assert_series_equal(f(b).iloc[:400],f(b2).iloc[:400])
    def test_supertrend_direction_tracks_trend(self):
        c=np.r_[np.linspace(100,200,300),np.linspace(200,100,300)];b=bars(c,c*1.005,c*.995,c);d,_=supertrend(b,10,3)
        self.assertEqual(d.iloc[250],1);self.assertEqual(d.iloc[-1],-1)
    def test_rsi_bounds(self):
        c=100*np.cumprod(1+np.random.default_rng(1).normal(0,.01,500));r=rsi(pd.Series(c),14).dropna();self.assertTrue(r.between(0,100).all())

if __name__=='__main__':unittest.main()
