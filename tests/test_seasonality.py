import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from seasonality_leadlag import session_signal,funding_hour_signal,US_SESSION
from core import simulate

class SeasonalityTests(unittest.TestCase):
    def test_session_signal_positions_bars_inside_window_after_delay(self):
        idx=pd.date_range('2022-01-01',periods=288,freq='5min',tz='UTC');s=session_signal(idx,US_SESSION,delay=2)
        d=pd.DataFrame(dict(open=100.,close=100.,high=100.,low=100.,volume=1.,quote_volume=1.,taker_base=.5,trades=1.),index=idx)
        b=simulate(d,s,0);held=b.position[b.position>0].index
        self.assertEqual(held.min().strftime('%H:%M'),'13:30');self.assertEqual(held.max().strftime('%H:%M'),'19:55');self.assertEqual(len(held),78)
        m=session_signal(idx,US_SESSION,delay=2,invert=True);self.assertTrue(((s+m)==1).all())
    def test_funding_hour_signal(self):
        idx=pd.date_range('2022-01-01',periods=576,freq='5min',tz='UTC');s=funding_hour_signal(idx,delay=2)
        d=pd.DataFrame(dict(open=100.,close=100.,high=100.,low=100.,volume=1.,quote_volume=1.,taker_base=.5,trades=1.),index=idx)
        held=simulate(d,s,0).position;held=held[held>0].index
        self.assertEqual(sorted(set(held.hour)),[7,15,23]);self.assertEqual(len(held),71)  # 2 days x 36 bars minus terminal liquidation bar

if __name__=='__main__':unittest.main()
