import sys,unittest,io,zipfile
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from spot_micro_data import parse_spot
from micro_data import derive_from_frame,derive_seconds

def zipped(text):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w') as z:z.writestr('x.csv',text)
    return buf.getvalue()

class SpotMicroTests(unittest.TestCase):
    def test_headerless_spot_matches_um_derivation(self):
        day=pd.Timestamp('2024-03-05');base=int(day.value//10**6)
        spot=f'1,100.5,2,1,1,{base+10},False,True\n2,101,1,2,2,{base+900},True,True\n'
        um='agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker\n'+f'1,100.5,2,1,1,{base+10},false\n2,101,1,2,2,{base+900},true\n'
        a=derive_from_frame(parse_spot(zipped(spot)),day);b=derive_seconds(zipped(um),day)
        pd.testing.assert_frame_equal(a,b);self.assertEqual(a.buy_qty.iloc[0],2.);self.assertEqual(a.sell_qty.iloc[0],1.)
        with_header='agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker,is_best_match\n'+spot
        pd.testing.assert_frame_equal(derive_from_frame(parse_spot(zipped(with_header)),day),b)

if __name__=='__main__':unittest.main()
