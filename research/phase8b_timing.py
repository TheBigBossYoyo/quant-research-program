"""Phase 8B causal execution timing: EDGAR acceptance time -> first usable US market open (frozen rule, section 6).

Rule: the entry session is the first trading session whose 09:30 ET open is at least 60 minutes after the
`<ACCEPTANCE-DATETIME>` of the filing: acceptance at or before 08:30:00 ET on a trading day -> that day's open;
later on a trading day, or on a weekend/holiday -> the next trading day's open. Exit = the open of the session
`hold` sessions after entry (252 primary, 126 secondary); a hold that runs past the last development session is
truncated there and flagged. Trading sessions come from the vendor calendar (days with an SPY open), cross-checked
against exchange_calendars XNYS. Acceptance strings are US Eastern local time (EDGAR convention); the
America/New_York zone handles daylight saving.
"""
from datetime import datetime, time
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from phase8b_lock import guard_dates

ET = ZoneInfo('America/New_York')
SAME_DAY_CUTOFF = time(8, 30, 0)
MARKET_OPEN = time(9, 30, 0)
MARKET_CLOSE = time(16, 0, 0)
HOLD_PRIMARY = 252
HOLD_SECONDARY = 126


def parse_acceptance(s):
    """'YYYYMMDDHHMMSS' (EDGAR header) -> tz-aware datetime in America/New_York. Raises ValueError on bad input."""
    s = str(s).strip()
    if len(s) != 14 or not s.isdigit():
        raise ValueError(f'acceptance datetime must be 14 digits, got {s!r}')
    naive = datetime.strptime(s, '%Y%m%d%H%M%S')
    return naive.replace(tzinfo=ET)


def parse_filed(s):
    s = str(s).strip()
    if len(s) != 8 or not s.isdigit():
        raise ValueError(f'filing date must be 8 digits, got {s!r}')
    return pd.Timestamp(datetime.strptime(s, '%Y%m%d'))


def sessions_from_open(open_series):
    """Trading sessions = dates with a finite vendor open; guarded against the development lock."""
    s = pd.Series(open_series).dropna()
    idx = pd.DatetimeIndex(s.index[np.isfinite(s.to_numpy(dtype=float))]).normalize().unique().sort_values()
    guard_dates(idx, 'trading calendar')
    return idx


def xnys_sessions(start, end):
    """Reference NYSE sessions from exchange_calendars (cross-check only)."""
    import exchange_calendars as xc
    cal = xc.get_calendar('XNYS', start=str(pd.Timestamp(start).date()), end=str(pd.Timestamp(end).date()))
    return pd.DatetimeIndex(cal.sessions).tz_localize(None) if cal.sessions.tz is not None else pd.DatetimeIndex(cal.sessions)


def timing_category(accepted):
    """Descriptive bucket for the timing audit (ET clock of a tz-aware acceptance)."""
    t = accepted.astimezone(ET).time()
    if t <= SAME_DAY_CUTOFF:
        return 'pre_open_by_0830'
    if t < MARKET_OPEN:
        return 'pre_open_after_0830'
    if t < MARKET_CLOSE:
        return 'intraday'
    return 'after_close'


def entry_session(accepted, sessions, delay=0):
    """Entry session for a tz-aware acceptance datetime. Returns (Timestamp or None, category string).
    `sessions` is a sorted naive DatetimeIndex of trading days. None when no session remains in the calendar."""
    if accepted.tzinfo is None:
        raise ValueError('acceptance datetime must be tz-aware (America/New_York)')
    local = accepted.astimezone(ET)
    day = pd.Timestamp(local.date())
    pos = sessions.searchsorted(day, side='left')
    is_session = pos < len(sessions) and sessions[pos] == day
    if is_session and local.time() <= SAME_DAY_CUTOFF:
        entry_pos = pos
        category = 'same_day_open'
    else:
        entry_pos = pos + 1 if is_session else pos
        category = 'next_session_open' if is_session else 'non_session_day'
    entry_pos += delay
    if entry_pos >= len(sessions):
        return None, category
    return sessions[entry_pos], category


def exit_session(entry, sessions, hold=HOLD_PRIMARY):
    """Exit session `hold` sessions after entry; truncated at the last session (flag True) when the hold runs past it."""
    pos = sessions.get_loc(entry)
    target = pos + hold
    if target >= len(sessions):
        return sessions[-1], True
    return sessions[target], False


def schedule(accepted_list, sessions, hold=HOLD_PRIMARY, delay=0):
    """Vectorised helper: DataFrame with entry, exit, truncated, category, entry_idx, exit_idx (NaN entry when none)."""
    rows = []
    for acc in accepted_list:
        e, cat = entry_session(acc, sessions, delay)
        if e is None:
            rows.append(dict(entry=pd.NaT, exit=pd.NaT, truncated=True, category=cat, entry_idx=np.nan, exit_idx=np.nan, timing=timing_category(acc)))
            continue
        x, trunc = exit_session(e, sessions, hold)
        rows.append(dict(entry=e, exit=x, truncated=trunc, category=cat, entry_idx=int(sessions.get_loc(e)), exit_idx=int(sessions.get_loc(x)), timing=timing_category(acc)))
    out = pd.DataFrame(rows)
    if len(out):
        guard_dates(out['entry'].dropna(), 'entry sessions'); guard_dates(out['exit'].dropna(), 'exit sessions')
    return out
