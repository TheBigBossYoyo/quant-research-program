import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from micro_passive import passive_fills,exit_price

class PassiveTests(unittest.TestCase):
    def sec(self):
        n=2000;last=np.full(n,100.);lo=np.full(n,100.);hi=np.full(n,100.);first=np.full(n,100.)
        lo[130]=99.9;hi[400]=100.1;lo[700]=99.7  # trade-throughs at chosen seconds
        return pd.DataFrame(dict(second=np.arange(n),first_price=first,last_price=last,low_price=lo,high_price=hi))
    def test_fill_requires_trade_through_within_window(self):
        s=self.sec();t=np.array([100,100,600,1500]);side=np.array([1,-1,1,1])
        filled,fsec,limit=passive_fills(s,t,side,wait=300,ticks=1,latency=5,tick=.1)
        self.assertTrue(filled[0]);self.assertEqual(fsec[0],130)          # bid at 100, trade at 99.9 -> filled
        self.assertTrue(filled[1]);self.assertEqual(fsec[1],400)          # ask at 100 filled when a trade prints >=100.1 at second 400 (<405)
        self.assertTrue(filled[2]);self.assertEqual(fsec[2],700)          # bid placed at 605, low 99.7 at 700
        self.assertFalse(filled[3])                                         # nothing after 1505
        f2,_,_=passive_fills(s,t,side,wait=300,ticks=2,latency=5,tick=.1);self.assertFalse(f2[0]);self.assertTrue(f2[2])  # two ticks: 99.9 not enough, 99.7 enough
        f3,_,_=passive_fills(s,t,side,wait=20,latency=5,tick=.1);self.assertFalse(f3[0])   # window too short
    def test_exit_and_no_lookback(self):
        s=self.sec();s.loc[1000,'first_price']=123.;self.assertEqual(exit_price(s,np.array([700]),300)[0],123.);self.assertTrue(np.isnan(exit_price(s,np.array([1900]),300)[0]))

if __name__=='__main__':unittest.main()
