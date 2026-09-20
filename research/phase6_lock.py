"""Phase 6 equity chronological lock and programmatic read firewall.

Segments were fixed on 2026-09-09 (PHASE6_EQUITY_DATA_LOCK.md) before any equity or factor
result was inspected. Validation and holdout rows are only returned when a verified unlock file
exists; the unlock file must name a decision document and carry its SHA256 and an explicit human
authorisation flag. Development access never depends on an unlock file.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

SEGMENTS = {
    'development': ('1900-01-01', '2018-01-01'),
    'validation': ('2018-01-01', '2022-01-01'),
    'holdout': ('2022-01-01', '2026-09-01'),
}
STOCK_DEV_START = pd.Timestamp('1990-01-01')     # stock-level (Norgate Platinum history start)
FRENCH_DEV_START = pd.Timestamp('1963-07-01')    # family-level (French library, five-factor start)
DEV_END_EXCLUSIVE = pd.Timestamp(SEGMENTS['development'][1])

UNLOCK_FILES = {
    'validation': ROOT / 'PHASE6_VALIDATION_UNLOCK.json',
    'holdout': ROOT / 'PHASE6_HOLDOUT_UNLOCK.json',
}
UNLOCK_REQUIRED_KEYS = ('frozen_candidate_hash', 'decision_document', 'decision_document_sha256',
                        'human_authorised', 'authorised_on')


class LockError(RuntimeError):
    """Raised when locked data is requested without a verified unlock."""


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bounds(segment):
    if segment not in SEGMENTS:
        raise LockError(f'unknown segment {segment!r}; expected one of {sorted(SEGMENTS)}')
    start, end = SEGMENTS[segment]
    return pd.Timestamp(start), pd.Timestamp(end)


def unlock_status(segment, unlock_files=None):
    """Return dict(open=bool, reason=str). Development is always open."""
    files = UNLOCK_FILES if unlock_files is None else unlock_files
    if segment == 'development':
        return dict(open=True, reason='development segment')
    if segment not in files:
        return dict(open=False, reason=f'no unlock mechanism for {segment!r}')
    path = Path(files[segment])
    if not path.exists():
        return dict(open=False, reason=f'{path.name} absent')
    try:
        unlock = json.loads(path.read_text(encoding='utf8'))
    except (ValueError, OSError) as exc:
        return dict(open=False, reason=f'{path.name} unreadable: {exc}')
    missing = [k for k in UNLOCK_REQUIRED_KEYS if k not in unlock]
    if missing:
        return dict(open=False, reason=f'{path.name} missing keys {missing}')
    if unlock['human_authorised'] is not True:
        return dict(open=False, reason='human_authorised is not true')
    doc = path.parent / unlock['decision_document']
    if not doc.exists():
        return dict(open=False, reason=f'decision document {doc.name} absent')
    if sha256_file(doc) != unlock['decision_document_sha256']:
        return dict(open=False, reason='decision document hash mismatch')
    if segment == 'holdout':
        val = unlock_status('validation', files)
        if not val['open']:
            return dict(open=False, reason=f'validation not unlocked ({val["reason"]})')
    return dict(open=True, reason='unlock file verified', unlock=unlock)


def enforce(frame, segment='development', unlock_files=None):
    """Return the rows of `frame` (DatetimeIndex) inside `segment`; raise LockError if locked."""
    status = unlock_status(segment, unlock_files)
    if not status['open']:
        raise LockError(f'{segment} segment is locked: {status["reason"]}')
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise LockError('a DatetimeIndex is required for lock enforcement')
    start, end = bounds(segment)
    out = frame[(frame.index >= start) & (frame.index < end)]
    if len(out):
        assert out.index.max() < end and out.index.min() >= start
    return out


def assert_development(index):
    """Raise if any timestamp lies at or beyond the development end."""
    idx = pd.DatetimeIndex(index)
    if len(idx) and idx.max() >= DEV_END_EXCLUSIVE:
        raise LockError(f'development-only object contains {idx.max()} >= {DEV_END_EXCLUSIVE.date()}')
    return True


def describe():
    return dict(segments={k: dict(start=v[0], end_exclusive=v[1]) for k, v in SEGMENTS.items()},
                stock_dev_start=str(STOCK_DEV_START.date()), french_dev_start=str(FRENCH_DEV_START.date()),
                validation=unlock_status('validation')['reason'], holdout=unlock_status('holdout')['reason'])


if __name__ == '__main__':
    print(json.dumps(describe(), indent=2))
