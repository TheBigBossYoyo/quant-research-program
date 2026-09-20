import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from ta_relstrength import weights

class RelStrengthTests(unittest.TestCase):
    def test_long_short_and_long_only_overlay(self):
        idx=pd.DatetimeIndex(['2022-01-01']);syms=[f'S{i}' for i in range(20)];score=pd.DataFrame([np.arange(20.)],index=idx,columns=syms);mask=pd.DataFrame(True,index=idx,columns=syms)
        w=weights(score,mask,idx[0],.2);self.assertAlmostEqual(w.sum(),0.);self.assertAlmostEqual(w.abs().sum(),1.);self.assertEqual(w['S19'],.125)
        ov=pd.DataFrame(True,index=idx,columns=syms);ov.loc[idx[0],'S19']=False
        lo=weights(score,mask,idx[0],.2,long_only=True,overlay=ov);self.assertNotIn('S19',lo.index);self.assertEqual(len(lo),3);self.assertAlmostEqual(lo.iloc[0],.25)  # 4 slots, one failed overlay -> cash for that slot
        mask.iloc[0,:15]=False;self.assertEqual(len(weights(score,mask,idx[0],.2)),0)

if __name__=='__main__':unittest.main()
