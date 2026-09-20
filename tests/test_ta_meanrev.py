import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from ta_meanrev import mr_target

class MeanRevTests(unittest.TestCase):
    def test_entry_exit_time_stop_and_regime_gate(self):
        idx=pd.date_range('2022-01-01',periods=12,freq='h',tz='UTC');z=pd.Series([0,-2.1,-1,-.5,.1,0,2.2,1,1,1,1,1],index=idx,dtype=float)
        reg=pd.Series([True]*12,index=idx);t=mr_target(z,2.,reg,time_stop=3).tolist()
        self.assertEqual(t[:5],[0,1,1,1,0])            # long at z<=-2, exit when z crosses >=0 at bar4
        self.assertEqual(t[6:10],[-1,-1,-1,0])         # short at z>=2, time stop after 3 bars
        reg2=reg.copy();reg2.iloc[1]=False;self.assertEqual(mr_target(z,2.,reg2,3).tolist()[1],0)   # no entry outside regime
        reg3=reg.copy();reg3.iloc[2]=False;self.assertEqual(mr_target(z,2.,reg3,3).tolist()[2],0)   # regime end exits

if __name__=='__main__':unittest.main()
