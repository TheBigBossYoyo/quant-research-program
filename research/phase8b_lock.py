"""Phase 8B hard development lock (E062, repurchase-authorisation announcements).

Second, independent guard on top of phase6_lock: every Phase 8B price, calendar, event, return or benchmark object
passes through `guard_dates`, which raises Phase8BLockError on any timestamp at or after 2018-01-01. Prices are only
read through `load_panel` (phase6_eodhd_panel.load_panel, development segment, then guarded). Company-facts files
on disk contain facts filed after 2017; `companyfacts_dev` drops them at read time before returning anything.
EDGAR accessions are checked with `guard_filed_date` before their text is stored.
"""
import gzip
import json
from pathlib import Path

import pandas as pd

from phase6_lock import ROOT, LockError
import phase6_eodhd_panel as pnl

DEV_END_EXCLUSIVE = pd.Timestamp('2018-01-01')
LAST_DEV_OPEN = pd.Timestamp('2017-12-29')
RETRIEVAL_START = pd.Timestamp('2004-01-01')
RETRIEVAL_END = pd.Timestamp('2017-12-31')
ET = 'America/New_York'
COMPANYFACTS = ROOT / 'data/raw/phase8/companyfacts'


class Phase8BLockError(LockError):
    """Raised when a Phase 8B object carries a date at or beyond the development end."""


def _naive_index(values):
    idx = pd.DatetimeIndex(pd.to_datetime(values))
    if idx.tz is not None:
        idx = idx.tz_convert(ET).tz_localize(None)
    return idx


def guard_dates(values, what='object'):
    """Raise unless every timestamp in `values` is before 2018-01-01 (tz-aware values are read in US Eastern)."""
    idx = _naive_index(values)
    idx = idx[idx.notna()]
    if len(idx) and idx.max() >= DEV_END_EXCLUSIVE:
        raise Phase8BLockError(f'Phase 8B {what} contains {idx.max()} >= {DEV_END_EXCLUSIVE.date()} (development lock)')
    return True


def guard_frame(frame, what='frame', date_columns=()):
    """Guard a DatetimeIndex and any named date columns of a DataFrame/Series."""
    if isinstance(frame.index, pd.DatetimeIndex):
        guard_dates(frame.index, f'{what} index')
    for c in date_columns:
        if c in getattr(frame, 'columns', []):
            guard_dates(frame[c], f'{what}.{c}')
    return frame


def guard_filed_date(filed):
    """`filed` as YYYYMMDD or ISO string; raise if it is at or beyond 2018-01-01."""
    s = str(filed).strip().replace('-', '')
    if len(s) < 8 or not s[:8].isdigit():
        raise Phase8BLockError(f'unparseable filing date {filed!r}')
    if int(s[:8]) >= 20180101:
        raise Phase8BLockError(f'filing date {filed} is in a locked segment')
    return s[:8]


def load_panel(field, columns=None):
    """Lock-enforced development panel, guarded a second time."""
    panel = pnl.load_panel(field, 'development', columns=columns)
    guard_dates(panel.index, f'panel {field}')
    return panel


def companyfacts_dev(cik, root=COMPANYFACTS):
    """Company-facts JSON for one CIK with every fact whose `filed` or `end` is >= 2018-01-01 removed at read time.
    Returns None when the file is absent. The returned structure never carries a locked date (asserted)."""
    path = Path(root) / f'CIK{int(cik):010d}.json.gz'
    if not path.exists():
        return None
    with gzip.open(path, 'rt', encoding='utf8') as fh:
        raw = json.load(fh)
    out = dict(cik=raw.get('cik'), entityName=raw.get('entityName'), facts={})
    for taxonomy, tags in raw.get('facts', {}).items():
        out['facts'][taxonomy] = {}
        for tag, body in tags.items():
            units = {}
            for unit, rows in body.get('units', {}).items():
                keep = [r for r in rows if r.get('filed') and r['filed'] < '2018-01-01' and (not r.get('end') or r['end'] < '2018-01-01')]
                if keep:
                    units[unit] = keep
            if units:
                out['facts'][taxonomy][tag] = dict(label=body.get('label'), units=units)
    for tags in out['facts'].values():
        for body in tags.values():
            for rows in body['units'].values():
                guard_dates([r['filed'] for r in rows], 'companyfacts filed')
    return out


def describe():
    return dict(dev_end_exclusive=str(DEV_END_EXCLUSIVE.date()), last_dev_open=str(LAST_DEV_OPEN.date()),
                retrieval=[str(RETRIEVAL_START.date()), str(RETRIEVAL_END.date())])
