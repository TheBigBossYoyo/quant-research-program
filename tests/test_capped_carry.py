import sys,unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from capped_carry import ledger

class CapTests(unittest.TestCase):
    def sample(self):
        idx=pd.date_range('2022-01-01',periods=8,freq='h',tz='UTC')
        p=pd.DataFrame(dict(spot=[100,130,130,130,130,130,130,130],future=[100,130,130,130,130,130,130,130],mark=[100,130,130,130,130,130,130,130],tradable=True),index=idx)
        f=pd.DataFrame(dict(mark_used=[],rate=[]),index=pd.DatetimeIndex([],tz='UTC'))
        return p,f
    def test_delayed_trim(self):
        p,f=self.sample();r,d=ledger(p,f,0,0)
        self.assertEqual(r.q.iloc[0],r.q.iloc[1]);self.assertLess(r.q.iloc[2],r.q.iloc[1])
        self.assertLessEqual(r.gross.iloc[2],.8)
    def test_no_future_position_change(self):
        p,f=self.sample();a,_=ledger(p,f);p.iloc[5:,:3]=500.;b,_=ledger(p,f)
        pd.testing.assert_series_equal(a.q.iloc[:5],b.q.iloc[:5])
    def test_no_fill_on_missing_observation(self):
        p,f=self.sample();p.loc[p.index[2],'tradable']=False;r,_=ledger(p,f)
        self.assertEqual(r.q.iloc[2],r.q.iloc[1]);self.assertLess(r.q.iloc[3],r.q.iloc[2])
    def test_collateral_veto(self):
        p,f=self.sample();p.loc[p.index[2],'mark']=500.;r,d=ledger(p,f)
        self.assertTrue(d['collateral_halt']);self.assertEqual(r.q.iloc[3],0.)
    def test_mandatory_flatten_survives_outage_and_price_recovery(self):
        p,f=self.sample()
        p.loc[p.index[1],'mark']=500.
        p.loc[p.index[2],'tradable']=False
        r,d=ledger(p,f)
        self.assertTrue(d['collateral_halt'])
        self.assertEqual(r.q.iloc[2],r.q.iloc[1])
        self.assertEqual(r.q.iloc[3],0.)

if __name__=='__main__':unittest.main()
