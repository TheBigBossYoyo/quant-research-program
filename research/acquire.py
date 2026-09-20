"""Public GET-only data acquisition. No credentials, orders, or holdout access."""
from pathlib import Path
import hashlib
import json
import time
from datetime import datetime, timezone
import requests

ROOT = Path(__file__).resolve().parents[1]

def now():
    return datetime.now(timezone.utc).isoformat()

def get(url):
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=40)
            if r.status_code in (418, 429):
                raise RuntimeError(f"Rate limited; stop without retry: {r.status_code}")
            r.raise_for_status()
            return r.content
        except (requests.ConnectionError, requests.Timeout):
            if attempt == 2:
                raise
            print('Transient connection failure; retry', attempt+1, url, flush=True)
            time.sleep(2**attempt)

def main():
    cfg = json.loads((ROOT / 'config/research.json').read_text())
    assert cfg['live_trading'] is False and cfg['final_test_locked']
    raw = ROOT / 'data/raw'
    meta = ROOT / 'data/metadata'
    raw.mkdir(parents=True, exist_ok=True)
    meta.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    manifest = meta / f'acquisition_{stamp}.jsonl'
    with manifest.open('x', encoding='utf8') as log:
        for sym in cfg['symbols']:
            for endpoint in ('exchangeInfo', 'ticker/bookTicker', 'ticker/24hr'):
                url = f'https://data-api.binance.vision/api/v3/{endpoint}?symbol={sym}'
                try:
                    content = get(url)
                    name = f'{sym}_{endpoint.replace("/", "_")}_{stamp}.json'
                    (meta / name).write_bytes(content)
                    log.write(json.dumps(dict(url=url, retrieved=now(), file=name, sha256=hashlib.sha256(content).hexdigest()))+'\n')
                except requests.RequestException as exc:
                    log.write(json.dumps(dict(url=url, retrieved=now(), error=str(exc)))+'\n')
                log.flush()
            for year in range(2022, 2026):
                for month in range(1, 13):
                    date = f'{year}-{month:02}'
                    assert date < cfg['final_test_start'][:7], 'Holdout acquisition blocked'
                    name = f'{sym}-5m-{date}.zip'
                    url = f'https://data.binance.vision/data/spot/monthly/klines/{sym}/5m/{name}'
                    path = raw / name
                    checksum_path = raw / (name + '.CHECKSUM')
                    if path.exists() and checksum_path.exists():
                        body, checksum = path.read_bytes(), checksum_path.read_bytes()
                        cached = True
                    else:
                        checksum = get(url + '.CHECKSUM')
                        body = get(url)
                        cached = False
                    digest = hashlib.sha256(body).hexdigest()
                    assert digest == checksum.decode().split()[0], f'Checksum failure {name}'
                    if not cached:
                        path.write_bytes(body)
                        checksum_path.write_bytes(checksum)
                    log.write(json.dumps(dict(url=url, retrieved=now(), file=name, sha256=digest, bytes=len(body), checksum_verified=True, cached=cached))+'\n')
                    log.flush()
                    print(name, len(body), 'verified', flush=True)
                    time.sleep(.05)

if __name__ == '__main__':
    main()
