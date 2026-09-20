import sys,unittest,io,zipfile
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from micro_data import derive_seconds,sample_days

def zipped(rows):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w') as z:z.writestr('x.csv','agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker\n'+'\n'.join(rows)+'\n')
    return buf.getvalue()

class MicroDataTests(unittest.TestCase):
    def test_aggressor_side_and_second_bucketing(self):
        day=pd.Timestamp('2024-03-05');base=int(day.value//10**6)
        rows=[f'1,100,2,1,1,{base+10},false',f'2,101,1,2,2,{base+900},true',f'3,102,5,3,3,{base+1000},false',f'4,99,0.5,4,4,{base+86399999},true']
        b=derive_seconds(zipped(rows),day)
        self.assertEqual(len(b),86400);self.assertEqual(b.trades.iloc[0],2);self.assertEqual(b.buy_qty.iloc[0],2.);self.assertEqual(b.sell_qty.iloc[0],1.)
        self.assertEqual(b.first_price.iloc[0],100.);self.assertEqual(b.last_price.iloc[0],101.);self.assertEqual(b.max_notional.iloc[0],200.);self.assertEqual(b.max_notional_signed.iloc[0],200.)
        self.assertEqual(b.low_price.iloc[0],100.);self.assertEqual(b.high_price.iloc[0],101.);self.assertTrue(np.isnan(b.low_price.iloc[2]));self.assertEqual(b.buy_notional.iloc[1],510.);self.assertEqual(b.max_notional_signed.iloc[86399],-49.5);self.assertTrue(np.isnan(b.first_price.iloc[2]))
    def test_sample_days_deterministic(self):
        s=sample_days();self.assertEqual(s[0],pd.Timestamp('2023-06-01'));self.assertEqual((s[1]-s[0]).days,3);self.assertTrue(all(d.year<2025 for d in s));self.assertEqual(len(s),194)
    def test_rejects_non_monotonic(self):
        day=pd.Timestamp('2024-03-05');base=int(day.value//10**6)
        with self.assertRaises(AssertionError):derive_seconds(zipped([f'1,100,1,1,1,{base+500},false',f'2,100,1,2,2,{base+400},false']),day)

if __name__=='__main__':unittest.main()
