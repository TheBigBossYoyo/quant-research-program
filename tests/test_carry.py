import sys
from pathlib import Path
import unittest
import io
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from carry_backtest import rounded_quantity,paired_pnl,parse_price_csv,run_case

class CarryTests(unittest.TestCase):
    def test_equal_price_change_cancels(self):
        p,b,f=paired_pnl(2,100,140,101,141,3,0,0)
        self.assertEqual(p,3);self.assertEqual(b,0)
    def test_basis_widening_loses(self):
        p,b,f=paired_pnl(2,100,110,101,115,0,0,0)
        self.assertEqual(p,-8)
    def test_funding_negative_debit(self):
        self.assertEqual(paired_pnl(1,100,100,100,100,-2,0,0)[0],-2)
    def test_four_notional_fee_legs(self):
        p,b,f=paired_pnl(1,100,110,100,110,0,.001,.0005)
        self.assertAlmostEqual(f,.315);self.assertAlmostEqual(p,-.315)
    def test_rounding_respects_budget(self):
        self.assertEqual(rounded_quantity(250,78450,.001),.003)
        self.assertLessEqual(rounded_quantity(250,78450,.001)*78450,250)
    def test_archive_header_and_no_header_same(self):
        row='1640995200000,100,101,99,100,0,1640998799999,0,3600,0,0,0\n'
        header='open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n'
        a=parse_price_csv(io.StringIO(row));b=parse_price_csv(io.StringIO(header+row))
        self.assertEqual(a.open.iloc[0],b.open.iloc[0]);self.assertEqual(len(a),len(b))
    def test_complete_cash_carry_path(self):
        idx=pd.date_range('2022-01-01',periods=24,freq='h',tz='UTC')
        px=pd.DataFrame(dict(spot=100.,future=100.,mark=100.,mark_high=100.,spot_volume=1.,future_volume=1.),index=idx)
        funding=pd.DataFrame(dict(scheduled=pd.Series([],dtype='datetime64[ns, UTC]'),mark_used=[],rate=[],mark=[]),index=pd.DatetimeIndex([],tz='UTC'))
        r=run_case(px,funding,.001,20,.0012,.0007)
        self.assertAlmostEqual(r['ending_equity_usdt'],499.05)
        self.assertFalse(r['necessary_solvency_breach'])
        px.loc[idx[10],'mark_high']=400.
        self.assertTrue(run_case(px,funding,.001,20,.0012,.0007)['necessary_solvency_breach'])

if __name__=='__main__':unittest.main()
