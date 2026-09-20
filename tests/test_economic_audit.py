import unittest,sys
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from economic_audit import translate_gbp,accrual_reference

class EconomicTests(unittest.TestCase):
    def test_dollar_per_pound_direction(self):
        self.assertEqual(translate_gbp(pd.Series([500.]),pd.Series([1.25])).iloc[0],400.)
    def test_yield_accrual_uses_previous_day(self):
        idx=pd.date_range('2022-01-01',periods=3,tz='UTC')
        s=pd.Series([1.,2.,99.],index=idx)
        r=accrual_reference(s,idx[1:])
        self.assertAlmostEqual(r.iloc[0],.01/365.25)
        self.assertAlmostEqual(r.iloc[1],.02/365.25)

if __name__=='__main__':unittest.main()
