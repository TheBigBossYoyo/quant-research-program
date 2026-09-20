import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from cross_sectional_hostile import placebo_weights,build_weights
from universe import rebalance_days
from cross_sectional_screen import xs_ledger

class HostileTests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(3);self.days=pd.date_range('2022-01-01',periods=30,freq='D',tz='UTC');syms=[f'S{i}' for i in range(20)]
        self.score=pd.DataFrame(rng.normal(size=(30,20)),index=self.days,columns=syms)
        self.elig=pd.DataFrame(True,index=self.days,columns=syms);self.elig.iloc[:,15:]=False
        self.rb=rebalance_days(self.days,self.days[0],7)
    def test_placebo_permutes_only_within_day_and_eligible(self):
        w=placebo_weights(self.score,self.elig,self.rb,seed=1);d=self.rb[0]
        self.assertAlmostEqual(w[d].sum(),0.);self.assertAlmostEqual(w[d].abs().sum(),1.)
        self.assertTrue(all(s in self.elig.columns[:15] for s in w[d].index))
        a=placebo_weights(self.score,self.elig,self.rb,seed=1)[d];b=placebo_weights(self.score,self.elig,self.rb,seed=2)[d]
        self.assertFalse(a.equals(b))
        real=build_weights(self.score,self.elig,self.rb)[d];self.assertEqual(len(real),len(a))
    def test_slower_rebalance_reduces_turnover(self):
        opens=pd.DataFrame(100.,index=self.days,columns=self.score.columns);opens+=np.cumsum(np.random.default_rng(0).normal(0,1,opens.shape),axis=0)
        fund=pd.DataFrame(0.,index=self.days,columns=self.score.columns)
        w7=build_weights(self.score,self.elig,self.rb);w14=build_weights(self.score,self.elig,rebalance_days(self.days,self.days[0],14))
        t7=xs_ledger(opens,fund,w7,.001).turnover_notional.sum();t14=xs_ledger(opens,fund,w14,.001).turnover_notional.sum()
        self.assertLess(t14,t7);self.assertEqual(len(w14),3)

if __name__=='__main__':unittest.main()
