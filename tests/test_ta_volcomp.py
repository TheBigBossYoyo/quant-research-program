import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from ta_volcomp import breakout_state

class VolCompTests(unittest.TestCase):
    def test_breakout_requires_conditions_on_signal_bar(self):
        idx=pd.date_range('2022-01-01',periods=30,freq='h',tz='UTC');c=np.full(30,100.);c[25]=120.;c[28]=80.
        b=pd.DataFrame(dict(open=c,high=c,low=c,close=c,volume=1.),index=idx)
        s=breakout_state(b,20);self.assertEqual(s.iloc[25],1.);self.assertEqual(s.iloc[27],1.);self.assertEqual(s.iloc[28],-1.)
        comp=pd.Series(False,index=idx);comp.iloc[28]=True;s2=breakout_state(b,20,comp);self.assertEqual(s2.iloc[25],0.);self.assertEqual(s2.iloc[28],-1.)
        vol=pd.Series(False,index=idx);self.assertTrue((breakout_state(b,20,comp,vol)==0).all())

if __name__=='__main__':unittest.main()
