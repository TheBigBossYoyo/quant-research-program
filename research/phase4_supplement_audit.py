"""Data-supplementation audit table: official daily archives filling documented monthly gaps.

Reads only persisted metadata and integrity outputs; computes no strategy returns. Writes
PHASE4_DATA_SUPPLEMENTATION_AUDIT.md and reports/E043_universe/supplementation_audit.json.
"""
import hashlib
import json
from pathlib import Path

from core import ROOT

META = ROOT / 'data/metadata/phase4_daily_gap_supplement_acquisition.json'
PRE = ROOT / 'reports/E043_universe/superseded_pre_supplement/data_integrity.json'
POST = ROOT / 'reports/E043_universe/data_integrity.json'
FIRST_PASS = 'E044_20260909T092223'


def verified_sha(rel: str) -> str:
    p = ROOT / rel.replace('\\', '/')
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    listed = p.with_name(p.name + '.CHECKSUM').read_text().split()[0]
    if digest != listed:
        raise ValueError('Checksum mismatch ' + rel)
    return digest


def main() -> None:
    meta = json.loads(META.read_text())
    pre = {r['symbol']: r for r in json.loads(PRE.read_text())}
    post = {r['symbol']: r for r in json.loads(POST.read_text())}
    rows = []
    for m in meta:
        sym = m['symbol']
        sha = verified_sha(m['file'])
        if sha != m['sha256']:
            raise ValueError('Metadata hash mismatch ' + m['file'])
        before = pre[sym]
        after = post[sym]
        missing_before = [t for t in before['missing_timestamps'] if t.startswith(m['day'])]
        added = [t for t in after.get('supplemented_days', []) if t == m['day']]
        rows.append(dict(asset=sym, missing_period=f"{m['day']} 00:00-23:00 UTC ({len(missing_before)} hours)",
                         original_source_status=f"monthly archive {sym}-1h-{m['day'][:7]}.zip verified but lacks the day",
                         supplemental_source=m['url'], sha256=sha,
                         hours_before=len(missing_before), day_supplemented=bool(added),
                         treatment='official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change'))
    if any(not r['day_supplemented'] or r['hours_before'] != 24 for r in rows):
        raise RuntimeError('Supplement audit inconsistent with integrity outputs')
    summary = {s: dict(missing_hours_before=pre[s]['missing_hours'], incomplete_4h_bars_before=pre[s]['incomplete_4h_bars'],
                       missing_hours_after=post[s]['missing_hours'], incomplete_4h_bars_after=post[s]['incomplete_4h_bars'],
                       supplemented_hours=post[s].get('supplemented_hours', 0), non_4h_funding_events=post[s]['non_4h_funding_events'],
                       funding_mark_fallbacks=post[s]['funding_mark_fallbacks']) for s in post}
    out = dict(first_pass=FIRST_PASS, supplement_files=len(rows), rows=rows, per_asset=summary,
               post_integrity_sha256=hashlib.sha256(POST.read_bytes()).hexdigest(),
               pre_integrity_sha256=hashlib.sha256(PRE.read_bytes()).hexdigest())
    (ROOT / 'reports/E043_universe/supplementation_audit.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    md = ['# Phase 4 data supplementation audit', '',
          'Purpose: data integrity only. Twenty official Binance daily 1h kline archives fill the 120 hours missing from each of four monthly archives. '
          'Merging adds rows only where the monthly archive has none; any overlapping hour must be byte-identical or the loader fails. '
          'No forward fill, no synthetic rows, no signal, sizing, cost, funding or universe change. '
          f'The first pass ({FIRST_PASS}) is retained unchanged and labelled superseded.', '',
          '| Asset | Missing period | Original source status | Supplemental source | Hash/checksum | Treatment |',
          '| --- | --- | --- | --- | --- | --- |']
    for r in rows:
        md.append(f"| {r['asset']} | {r['missing_period']} | {r['original_source_status']} | {r['supplemental_source']} | {r['sha256']} | {r['treatment']} |")
    md += ['', '## Integrity before and after (all fourteen histories)', '',
           '| Asset | Missing hours before | Incomplete 4h bars before | Missing hours after | Incomplete 4h bars after | Supplemented hours | Non-4h funding events | Funding mark fallbacks |',
           '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for s, v in summary.items():
        md.append(f"| {s} | {v['missing_hours_before']} | {v['incomplete_4h_bars_before']} | {v['missing_hours_after']} | {v['incomplete_4h_bars_after']} | {v['supplemented_hours']} | {v['non_4h_funding_events']} | {v['funding_mark_fallbacks']} |")
    md += ['', 'Mark-price monthly archives were complete on the supplemented days, so no mark supplement was needed. '
           'Remaining incomplete 4h bars (MATICUSDT: the mandated 08:00 UTC exit bar) are contract administration, not gaps. '
           'Non-4h funding events exist only for SOLUSDT and are settled at their hourly boundary by the frozen event accounting. '
           'Funding mark fallbacks are hourly settlements whose mark open is absent from the mark archive and use the labelled trade-open proxy; adverse funding stress covers them.', '']
    (ROOT / 'PHASE4_DATA_SUPPLEMENTATION_AUDIT.md').write_text('\n'.join(md), encoding='utf-8')
    print('SUPPLEMENT_AUDIT', len(rows), 'files;', {s: v['missing_hours_after'] for s, v in summary.items()})


if __name__ == '__main__':
    main()
