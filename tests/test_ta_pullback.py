import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from ta_pullback import state_machine

class PullbackTests(unittest.TestCase):
    def test_state_machine_requires_pullback_then_trigger_and_exits_on_regime_flip(self):
        idx=pd.date_range('2022-01-01',periods=10,freq='h',tz='UTC')
        reg=pd.Series([1,1,1,1,1,1,-1,-1,-1,-1],index=idx,dtype=float)
        pb=pd.Series([False,True,False,False,False,False,False,True,False,False],index=idx)
        tg=pd.Series([True,False,False,True,True,False,False,False,True,False],index=idx)
        s=state_machine(reg,pb,tg).tolist()
        self.assertEqual(s[:6],[0,0,0,1,1,1])   # trigger at bar0 without prior pullback ignored; armed at bar1; entered at bar3; held
        self.assertEqual(s[6],0)                 # regime flip exits and disarms
        self.assertEqual(s[7],0);self.assertEqual(s[8],-1)  # new short regime: pullback at bar7, trigger at bar8 -> short
    def test_no_entry_when_regime_zero(self):
        idx=pd.date_range('2022-01-01',periods=4,freq='h',tz='UTC');reg=pd.Series([0.,0.,np.nan,0.],index=idx)
        s=state_machine(reg,pd.Series([True]*4,index=idx),pd.Series([True]*4,index=idx));self.assertEqual(s.tolist(),[0,0,0,0])

if __name__=='__main__':unittest.main()
