import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from micro_ledger import taker_ledger,thresholds_previous_day

class MicroLedgerTests(unittest.TestCase):
    def frame(self):
        rows=[]
        for d,day in enumerate(['2024-01-01','2024-01-04','2024-01-07']):
            for i in range(20):rows.append(dict(day=day,x=float(i+d*100),fwd_300=0.01 if i>=18 else (-0.01 if i<=1 else 0.0)))
        return pd.DataFrame(rows)
    def test_thresholds_from_previous_day_only(self):
        F=self.frame();lo,hi=thresholds_previous_day(F,'x')
        self.assertTrue(lo.iloc[:20].isna().all());self.assertAlmostEqual(hi.iloc[20],F.x.iloc[:20].quantile(.9));self.assertAlmostEqual(lo.iloc[40],F.x.iloc[20:40].quantile(.1))
    def test_ledger_direction_cost_and_busy(self):
        F=self.frame();tr,dl=taker_ledger(F,'x',300,1,cost=0.)
        self.assertEqual(tr.day.iloc[0],'2024-01-04');self.assertTrue((tr.side==1).all())  # day-2 values all exceed day-1 90th pct -> long entries
        self.assertEqual(len(tr),20//5*2);self.assertAlmostEqual(dl.loc['2024-01-01'],0.)  # busy window: one entry per 5 rows (300 s / 60 s)
        tr2,_=taker_ledger(F,'x',300,1,cost=.001);self.assertAlmostEqual(tr2.ret.iloc[0],tr.ret.iloc[0]-.002)
        tr3,_=taker_ledger(F,'x',300,-1,cost=0.);self.assertTrue((tr3.side==-1).all());self.assertAlmostEqual(tr3.ret.iloc[0],-tr.ret.iloc[0])

if __name__=='__main__':unittest.main()
