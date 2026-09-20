"""EODHD REST client for the Phase 6 EODHD screening stage (token-safe, hashed raw snapshots).

Token policy: read from the EODHD_API_TOKEN environment variable, falling back to the Windows
per-user environment registry key (the shell that launched this session predates the variable).
The token is never printed, logged, written to disk or included in any saved URL; every persisted
request record carries the URL with the token replaced by the literal string REDACTED.

Raw responses are written unmodified under data/raw/phase6/eodhd/<group>/ with SHA256 recorded in
an append-only acquisition log (data/metadata/phase6_eodhd_acquisition_<stamp>.jsonl). Nothing here
truncates by date: raw files may contain rows after 2017-12-31; only loaders in
phase6_eodhd_panel.py return rows, and they go through phase6_lock.enforce.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import sys
import threading
import time

import requests

from phase6_lock import ROOT

BASE = 'https://eodhd.com/api'
RAW = ROOT / 'data/raw/phase6/eodhd'
META = ROOT / 'data/metadata'
TOKEN_ENV = 'EODHD_API_TOKEN'
_TOKEN_RE = re.compile(r'api_token=[^&\s]+')
DEFAULT_TIMEOUT = 60
MAX_RETRIES = 4
RETRY_STATUS = {429, 500, 502, 503, 504}
MIN_INTERVAL_S = 0.2   # per process; three shard processes stay under the documented 1000/min ceiling


class EodhdError(RuntimeError):
    pass


def get_token():
    tok = os.environ.get(TOKEN_ENV)
    if not tok and sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
                tok, _ = winreg.QueryValueEx(key, TOKEN_ENV)
        except OSError:
            tok = None
    if not tok:
        raise EodhdError(f'{TOKEN_ENV} is not available in the process or user environment')
    return tok.strip()


def redact(url):
    return _TOKEN_RE.sub('api_token=REDACTED', str(url))


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


class Client:
    """Thin client with rate limiting, retries and a redacted request log."""

    def __init__(self, log_path=None, session=None, sleep=time.sleep):
        self.token = get_token()
        self.session = session or requests.Session()
        self.sleep = sleep
        self.calls = 0
        self.last_call = 0.0
        self._lock = threading.Lock()   # rate limiter and log are shared across worker threads
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
        META.mkdir(parents=True, exist_ok=True)
        self.log_path = Path(log_path) if log_path else META / f'phase6_eodhd_acquisition_{stamp}.jsonl'

    def _log(self, record):
        record = dict(record, logged_utc=datetime.now(timezone.utc).isoformat())
        assert self.token not in json.dumps(record), 'token would be logged'
        with self._lock, open(self.log_path, 'a', encoding='utf8') as fh:
            fh.write(json.dumps(record) + '\n')

    def _throttle(self):
        with self._lock:
            wait = max(0.0, MIN_INTERVAL_S - (time.monotonic() - self.last_call))
            self.last_call = time.monotonic() + wait
        if wait:
            self.sleep(wait)

    def get(self, path, params=None, fmt='json', raw_path=None, group='misc', timeout=DEFAULT_TIMEOUT):
        """GET BASE/path with the token; returns (parsed_json_or_text, saved_path_or_None)."""
        params = dict(params or {})
        params['api_token'] = self.token
        if fmt:
            params['fmt'] = fmt
        url = f'{BASE}/{path.lstrip("/")}'
        last_exc = None
        for attempt in range(MAX_RETRIES + 1):
            self._throttle()
            try:
                resp = self.session.get(url, params=params, timeout=timeout)
            except requests.RequestException as exc:   # network-level failure
                last_exc = exc
                self.sleep(2.0 * (attempt + 1))
                continue
            with self._lock:
                self.calls += 1
            if resp.status_code in RETRY_STATUS and attempt < MAX_RETRIES:
                self.sleep(3.0 * (attempt + 1))
                continue
            body = resp.content
            record = dict(url=redact(resp.url), status=resp.status_code, bytes=len(body),
                          sha256=sha256_bytes(body), group=group, attempt=attempt)
            if resp.status_code != 200:
                record['error_head'] = body[:300].decode('utf8', 'replace')
                self._log(record)
                raise EodhdError(f'HTTP {resp.status_code} for {redact(resp.url)}: {record["error_head"]}')
            saved = None
            if raw_path is not None:
                saved = RAW / group / raw_path
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_bytes(body)
                record['saved'] = str(saved.relative_to(ROOT)).replace('\\', '/')
            self._log(record)
            if fmt == 'json':
                try:
                    return json.loads(body.decode('utf8')), saved
                except ValueError as exc:
                    raise EodhdError(f'non-JSON body for {redact(resp.url)}: {body[:200]!r}') from exc
            return body.decode('utf8'), saved
        raise EodhdError(f'giving up on {redact(url)}: {last_exc}')


def verify_subscription(client):
    """Return the /api/user record with personal fields removed (never persisted with the name/email)."""
    user, _ = client.get('user', group='user')
    keep = {k: user.get(k) for k in ('subscriptionType', 'paymentMethod', 'apiRequests', 'apiRequestsDate',
                                     'dailyRateLimit', 'extraLimit', 'subscriptionMode', 'expireDate')}
    keep['other_keys'] = sorted(k for k in user if k not in keep and k not in ('name', 'email', 'inviteToken',
                                                                                'inviteTokenClicked'))
    return keep


if __name__ == '__main__':
    c = Client()
    print(json.dumps(verify_subscription(c), indent=1))
