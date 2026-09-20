"""Phase 8B Amendment 4: traded-price-path integrity screen. No classifier logic, no thresholds of its own.

The Phase 8B universe checks eligibility only at the signal date BEFORE entry, so a vendor series that becomes corrupt
DURING the 252-session hold is never re-examined. `SFD_old` oscillated between roughly $0.17 and $22 on adjacent
sessions from November 2012 and the re-equalising book harvested the oscillation (PHASE8B_DATA_DEFECT_AMENDMENT4.md).

This module re-uses the EXISTING Phase 6 I3 thresholds (`EXTREME_DAY_UP` = +200%, `EXTREME_DAY_DOWN` = -75%) and
applies them to the adjusted-open path a position is actually traded on. It looks only at prices: never at an event's
return, sign or contribution.
"""
import numpy as np
import pandas as pd

from phase6_stock_universe import EXTREME_DAY_UP, EXTREME_DAY_DOWN

UP = EXTREME_DAY_UP          # +2.0  (+200%)
DOWN = EXTREME_DAY_DOWN      # -0.75 (-75%)


def unclean_matrix(ao):
    """Boolean frame (sessions x codes): True where the adjusted-open return is implausible for a real security."""
    a = ao.to_numpy(dtype=float)
    with np.errstate(invalid='ignore', divide='ignore'):
        r = a[1:] / a[:-1] - 1.0
    bad = (r > UP) | (r < DOWN)
    out = np.zeros_like(a, dtype=bool)
    out[1:] = bad                     # the return is attributed to the later session
    out[:-1] |= bad                   # and to the earlier one, so both ends of a jump are unclean
    return pd.DataFrame(out, index=ao.index, columns=ao.columns)


def screen_events(events, ao, cal):
    """Drop every event whose own code has an unclean session inside [entry_idx, exit_idx].

    Returns (kept_events, report). Pure: reads prices and event indices only."""
    unclean = unclean_matrix(ao)
    cols = {c: i for i, c in enumerate(ao.columns)}
    U = unclean.to_numpy()
    n = len(cal)
    keep, dropped = [], []
    for idx, r in events.iterrows():
        code = r['code']
        j = cols.get(code)
        if j is None:
            keep.append(idx); continue                      # no price column: the portfolio skips it as no-price
        a = int(r['entry_idx']); b = min(int(r['exit_idx']), n - 1)
        if a <= b and U[a:b + 1, j].any():
            dropped.append(dict(event_id=r.get('event_id'), code=code, entry=str(cal[a].date()), exit=str(cal[b].date()),
                                unclean_sessions=int(U[a:b + 1, j].sum())))
        else:
            keep.append(idx)
    kept = events.loc[keep].copy()
    drop_df = pd.DataFrame(dropped)
    report = dict(threshold_up=UP, threshold_down=DOWN, source='phase6_stock_universe I3 (unchanged)',
                  events_in=int(len(events)), events_kept=int(len(kept)), events_dropped=int(len(drop_df)),
                  dropped_share=float(len(drop_df) / len(events)) if len(events) else 0.0,
                  dropped_by_year=(drop_df.assign(y=pd.to_datetime(drop_df['entry']).dt.year).groupby('y').size().to_dict()
                                   if len(drop_df) else {}),
                  distinct_codes_dropped=int(drop_df['code'].nunique()) if len(drop_df) else 0,
                  note='screen reads the adjusted-open path only; it never sees an event return')
    return kept, report, drop_df
