import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase6_eodhd as e  # noqa: E402
import phase6_eodhd_acquire as acq  # noqa: E402

FAKE = 'faketoken1234567890abc'


class FakeResponse:
    def __init__(self, status, body, url):
        self.status_code, self.content, self.url = status, body, url


class FakeSession:
    def __init__(self, responses):
        self.responses, self.calls = list(responses), []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, dict(params)))
        status, body = self.responses.pop(0)
        return FakeResponse(status, body, url + '?api_token=' + params['api_token'] + '&fmt=' + params.get('fmt', ''))


class ClientTests(unittest.TestCase):
    def make(self, responses, tmp):
        with mock.patch.dict('os.environ', {e.TOKEN_ENV: FAKE}):
            return e.Client(log_path=Path(tmp) / 'log.jsonl', session=FakeSession(responses), sleep=lambda s: None)

    def test_token_never_written_to_log_or_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = self.make([(200, b'{"a": 1}'), (403, b'Forbidden')], tmp)
            out, saved = c.get('user', group='t')
            self.assertEqual(out, {'a': 1})
            self.assertIsNone(saved)
            with self.assertRaises(e.EodhdError) as ctx:
                c.get('fundamentals/X', group='t')
            self.assertNotIn(FAKE, str(ctx.exception))
            log = (Path(tmp) / 'log.jsonl').read_text(encoding='utf8')
            self.assertNotIn(FAKE, log)
            self.assertIn('api_token=REDACTED', log)
            self.assertEqual(len(log.strip().splitlines()), 2)

    def test_retries_on_429_then_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = self.make([(429, b'slow down'), (200, b'[1,2]')], tmp)
            out, _ = c.get('eod/AAPL.US', group='t')
            self.assertEqual(out, [1, 2])
            self.assertEqual(c.calls, 2)

    def test_raw_snapshot_is_written_verbatim_with_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = self.make([(200, b'{"k": [1]}')], tmp)
            with mock.patch.object(e, 'RAW', Path(tmp) / 'raw'), mock.patch.object(e, 'ROOT', Path(tmp)):
                out, saved = c.get('x', group='g', raw_path='f.json')
                self.assertEqual(saved.read_bytes(), b'{"k": [1]}')
            rec = json.loads((Path(tmp) / 'log.jsonl').read_text().strip())
            self.assertEqual(rec['sha256'], e.sha256_bytes(b'{"k": [1]}'))

    def test_verify_subscription_drops_personal_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = json.dumps(dict(name='N', email='E', subscriptionType='monthly', dailyRateLimit=100000,
                                   inviteToken='abc', extraLimit=0)).encode()
            c = self.make([(200, body)], tmp)
            info = e.verify_subscription(c)
            self.assertNotIn('name', info)
            self.assertNotIn('email', info)
            self.assertEqual(info['dailyRateLimit'], 100000)

    def test_redact(self):
        self.assertEqual(e.redact('https://x/api/eod/A?api_token=SECRET&fmt=json'), 'https://x/api/eod/A?api_token=REDACTED&fmt=json')


class AcquireTests(unittest.TestCase):
    def test_fetch_one_writes_gzip_csv_and_stats(self):
        csv = 'Date,Open,High,Low,Close,Adjusted_close,Volume\n1997-12-31,1,1,1,1,1,10\n1998-01-02,1,1,1,1,1,10\n'
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict('os.environ', {e.TOKEN_ENV: FAKE}):
            c = e.Client(log_path=Path(tmp) / 'log.jsonl', session=FakeSession([(200, csv.encode())]), sleep=lambda s: None)
            with mock.patch.object(acq, 'EOD_DIR', Path(tmp) / 'eod'), mock.patch.object(acq, 'ROOT', Path(tmp)):
                rec = acq.fetch_one(c, 'ENRNQ', 'eod')
                self.assertEqual((rec['status'], rec['rows'], rec['first'], rec['last']), ('ok', 2, '1997-12-31', '1998-01-02'))
                self.assertEqual(gzip.open(Path(tmp) / 'eod/ENRNQ.csv.gz', 'rt').read(), csv)
            self.assertEqual(c.session.calls[0][1]['from'], acq.EOD_FROM)

    def test_unsafe_codes_rejected(self):
        for bad in ('..', 'A/B', 'A B', ''):
            with self.assertRaises(ValueError):
                acq.safe_name(bad)
        self.assertEqual(acq.safe_name('BSC_old'), 'BSC_old')
        self.assertEqual(acq.safe_name('LEN-N'), 'LEN-N')

    def test_error_record_has_no_token(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict('os.environ', {e.TOKEN_ENV: FAKE}):
            c = e.Client(log_path=Path(tmp) / 'log.jsonl', session=FakeSession([(404, b'Not found')]), sleep=lambda s: None)
            rec = acq.fetch_one(c, 'ZZZZ', 'eod')
            self.assertEqual(rec['status'], 'error')
            self.assertNotIn(FAKE, json.dumps(rec))


if __name__ == '__main__':
    unittest.main()
