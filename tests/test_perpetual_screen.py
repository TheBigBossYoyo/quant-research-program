import sys,unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from perpetual_screen import signed_ledger

class PerpetualTests(unittest.TestCase):
    def data(self,values):
        i=pd.date_range('2022-01-01',periods=len(values),freq='h',tz='UTC')
        return pd.DataFrame(dict(future=values,mark=values),index=i)
    def test_short_accounting_and_positive_funding_credit(self):
        p=self.data([100.,90.,90.]);s=pd.Series(-1,index=p.index);f=pd.Series([0.,1.,0.],index=p.index)
        r=signed_ledger(p,s,f,fee=0)
        self.assertAlmostEqual(r.nav.iloc[-1],527.5)
    def test_long_funding_debit(self):
        p=self.data([100.,100.,100.]);s=pd.Series(1,index=p.index);f=pd.Series([0.,1.,0.],index=p.index)
        self.assertAlmostEqual(signed_ledger(p,s,f,fee=0).nav.iloc[-1],497.5)
    def test_flat_roundtrip_fees(self):
        p=self.data([100.,100.,100.]);s=pd.Series(1,index=p.index);f=pd.Series(0.,index=p.index)
        r=signed_ledger(p,s,f,fee=.001)
        self.assertAlmostEqual(r.nav.iloc[-1],500-r.turnover_notional.sum()*.001)
    def test_flip_charges_both_legs(self):
        p=self.data([100.]*4);s=pd.Series([1,-1,-1,-1],index=p.index);f=pd.Series(0.,index=p.index)
        r=signed_ledger(p,s,f,fee=0)
        self.assertEqual(r.turnover_notional.iloc[1],500.)
        self.assertEqual(r.nav.iloc[-1],500.)
    def test_no_fill_on_zero_volume_observation(self):
        p=self.data([100.]*4);p['tradable']=[False,True,True,True]
        s=pd.Series(1,index=p.index);f=pd.Series(0.,index=p.index)
        r=signed_ledger(p,s,f,fee=0)
        self.assertEqual(r.turnover_notional.iloc[0],0.)
        self.assertGreater(r.turnover_notional.iloc[1],0.)

if __name__=='__main__':unittest.main()
