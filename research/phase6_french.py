"""Kenneth French data library: manifest, block parser and locked loader (Phase 6, family level).

Files were downloaded on 2026-09-09 from https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/
into data/raw/phase6/french and are never modified; `build_manifest` records SHA256, size and the
CRSP vintage stated in each file header. `load` returns one block of one file, converted from percent
to decimal returns, restricted to the requested lock segment through research/phase6_lock.py.

The library is CRSP-derived and survivorship-free at the portfolio level; it cannot support stock-level
portfolio construction, costs or capacity. Results built on it are capped at FACTOR_EVIDENCE.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import io
import json
import re
import zipfile
import numpy as np
import pandas as pd

from phase6_lock import ROOT, FRENCH_DEV_START, enforce

BASE_URL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/'
FOLDER = ROOT / 'data/raw/phase6/french'
MANIFEST = ROOT / 'data/metadata/phase6_french_manifest.json'
FILES = {
    'mom10_daily': '10_Portfolios_Prior_12_2_Daily_CSV.zip',
    'mom10_monthly': '10_Portfolios_Prior_12_2_CSV.zip',
    'strev10_daily': '10_Portfolios_Prior_1_0_Daily_CSV.zip',
    'strev10_monthly': '10_Portfolios_Prior_1_0_CSV.zip',
    'var_monthly': 'Portfolios_Formed_on_VAR_CSV.zip',
    'resvar_monthly': 'Portfolios_Formed_on_RESVAR_CSV.zip',
    'ind49_daily': '49_Industry_Portfolios_daily_CSV.zip',
    'ind49_monthly': '49_Industry_Portfolios_CSV.zip',
    'ind10_daily': '10_Industry_Portfolios_daily_CSV.zip',
    'ind10_monthly': '10_Industry_Portfolios_CSV.zip',
    'ff3_daily': 'F-F_Research_Data_Factors_daily_CSV.zip',
    'ff3_monthly': 'F-F_Research_Data_Factors_CSV.zip',
    'ff5_daily': 'F-F_Research_Data_5_Factors_2x3_daily_CSV.zip',
    'ff5_monthly': 'F-F_Research_Data_5_Factors_2x3_CSV.zip',
    'mom_factor_daily': 'F-F_Momentum_Factor_daily_CSV.zip',
    'mom_factor_monthly': 'F-F_Momentum_Factor_CSV.zip',
    'strev_factor_daily': 'F-F_ST_Reversal_Factor_daily_CSV.zip',
    'strev_factor_monthly': 'F-F_ST_Reversal_Factor_CSV.zip',
    'size_monthly': 'Portfolios_Formed_on_ME_CSV.zip',
    # added 2026-09-12 for the Phase 6B modern-evidence screen (E052)
    'dp_monthly': 'Portfolios_Formed_on_D-P_CSV.zip',
    'ltrev10_monthly': '10_Portfolios_Prior_60_13_CSV.zip',
    'beta_monthly': 'Portfolios_Formed_on_BETA_CSV.zip',
    'op_monthly': 'Portfolios_Formed_on_OP_CSV.zip',
    'beme_monthly': 'Portfolios_Formed_on_BE-ME_CSV.zip',
    'ep_monthly': 'Portfolios_Formed_on_E-P_CSV.zip',
    'inv_monthly': 'Portfolios_Formed_on_INV_CSV.zip',
    'ac_monthly': 'Portfolios_Formed_on_AC_CSV.zip',
    'ni_monthly': 'Portfolios_Formed_on_NI_CSV.zip',
}
MISSING_CODES = (-99.99, -999.0)
_DATA_ROW = re.compile(r'^\s*(\d{4}|\d{6}|\d{8})\s*,')


def read_text(key):
    path = FOLDER / FILES[key]
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        assert len(names) == 1, names
        return z.read(names[0]).decode('latin1')


def vintage(text):
    m = re.search(r'(\d{6}) CRSP database', text)
    return m.group(1) if m else None


def _parse_date(token):
    token = token.strip()
    if len(token) == 8:
        return pd.Timestamp(token)
    if len(token) == 6:
        return pd.Timestamp(token[:4] + '-' + token[4:] + '-01') + pd.offsets.MonthEnd(0)
    if len(token) == 4:
        return pd.Timestamp(token + '-12-31')
    raise ValueError(token)


def parse_blocks(text):
    """Split a French CSV into named blocks -> DataFrame (raw percent values, NaN for missing codes)."""
    lines = text.splitlines()
    blocks, i, n = {}, 0, 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(','):
            prev = lines[i - 1].strip() if i > 0 else ''
            name = prev if prev and not _DATA_ROW.match(lines[i - 1]) else f'block{n}'
            cols = [c.strip() for c in line.split(',')[1:]]
            rows, i = [], i + 1
            while i < len(lines) and _DATA_ROW.match(lines[i]):
                parts = lines[i].split(',')
                vals = [float(p) if p.strip() else np.nan for p in parts[1:1 + len(cols)]]
                rows.append((_parse_date(parts[0]), vals))
                i += 1
            if rows:
                idx = pd.DatetimeIndex([r[0] for r in rows], name='date')
                df = pd.DataFrame([r[1] for r in rows], index=idx, columns=cols).astype(float)
                for code in MISSING_CODES:
                    df = df.mask(np.isclose(df, code))
                assert df.index.is_monotonic_increasing and df.index.is_unique, name
                blocks[name if name not in blocks else f'{name} #{n}'] = df
                n += 1
            continue
        i += 1
    return blocks


def build_manifest():
    FOLDER.mkdir(parents=True, exist_ok=True)
    records = []
    for key, fname in FILES.items():
        path = FOLDER / fname
        body = path.read_bytes()
        text = read_text(key)
        blocks = parse_blocks(text)
        records.append(dict(key=key, file=str(path.relative_to(ROOT)).replace('\\', '/'), url=BASE_URL + fname,
                            sha256=hashlib.sha256(body).hexdigest(), bytes=len(body), crsp_vintage=vintage(text),
                            file_mtime_utc=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                            blocks={k: dict(rows=len(v), cols=len(v.columns), first=str(v.index[0].date()),
                                            last=str(v.index[-1].date())) for k, v in blocks.items()}))
    manifest = dict(source='Kenneth R. French Data Library (CRSP-derived, survivorship-free portfolio returns)',
                    retrieved_utc='2026-09-09T20:59:00+00:00 (curl; file mtimes recorded per file)',
                    manifest_written_utc=datetime.now(timezone.utc).isoformat(), files=records,
                    note='Raw archives contain dates after the development end; loaders truncate through phase6_lock.enforce.')
    MANIFEST.write_text(json.dumps(manifest, indent=1), encoding='utf8')
    return manifest


def verify_manifest():
    m = json.loads(MANIFEST.read_text(encoding='utf8'))
    for rec in m['files']:
        assert hashlib.sha256((ROOT / rec['file']).read_bytes()).hexdigest() == rec['sha256'], rec['file']
    return m


def block_names(key):
    return list(parse_blocks(read_text(key)).keys())


# Semantic block kinds: French block titles vary ("Value Weight Returns", "Aerage Value Weighted ...").
KIND_RULES = {
    'vw_monthly': (('value', 'weight', 'monthly'), ('annual', 'average of', 'number', 'size')),
    'ew_monthly': (('equal', 'weight', 'monthly'), ('annual', 'average of', 'number', 'size')),
    'vw_daily': (('value', 'weight', 'daily'), ('annual', 'average of', 'number', 'size')),
    'ew_daily': (('equal', 'weight', 'daily'), ('annual', 'average of', 'number', 'size')),
    'nfirms': (('number of firms',), ()),
    'main': (('block0',), ()),
}


def select_block(blocks, block):
    """Return the block name for an exact name, a semantic kind (KIND_RULES) or a substring."""
    if block is None:
        return next(iter(blocks))
    if block in blocks:
        return block
    if block in KIND_RULES:
        need, forbid = KIND_RULES[block]
        matches = [k for k in blocks if all(t in k.lower() for t in need) and not any(t in k.lower() for t in forbid)]
    else:
        matches = [k for k in blocks if block.lower() in k.lower()]
    if len(matches) != 1:
        raise KeyError(f'{block!r} matched {matches} in {list(blocks)}')
    return matches[0]


def load(key, block=None, segment='development', returns=True, start=None, unlock_files=None):
    """Load one block of one file as decimal returns inside `segment`.

    block: exact block name, a semantic kind ('vw_monthly', 'ew_monthly', 'vw_daily', 'ew_daily',
    'nfirms', 'main'), a substring (unique match), or None for the first block. The lock is checked
    before any data is parsed.
    """
    from phase6_lock import unlock_status, LockError
    status = unlock_status(segment, unlock_files)
    if not status['open']:
        raise LockError(f'{segment} segment is locked: {status["reason"]}')
    blocks = parse_blocks(read_text(key))
    name = select_block(blocks, block)
    df = blocks[name]
    if returns:
        df = df / 100.0
    df = enforce(df, segment, unlock_files)
    start = FRENCH_DEV_START if start is None else pd.Timestamp(start)
    return df[df.index >= start]


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'manifest':
        m = build_manifest()
        for r in m['files']:
            print(r['key'], r['crsp_vintage'], r['sha256'][:12], {k: (v['first'], v['last']) for k, v in r['blocks'].items()})
    else:
        print('usage: python phase6_french.py manifest')
