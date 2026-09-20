"""Append section 3 (results) of PHASE6_EODHD_COVERAGE_AUDIT.md from an audit.json (no rule is changed here).
Usage (from research/): PYTHONUTF8=1 python phase6_eodhd_audit_report.py PHASE6_EODHD_AUDIT_<stamp>
"""
import json
import sys

from phase6_lock import ROOT


def main(name):
    a = json.loads((ROOT / 'reports' / name / 'audit.json').read_text(encoding='utf8'))
    L = [f'\n### 3.0 Source: reports/{name}/audit.json\n', '### 3.1 A1 constituent price coverage (2012-04..2017-12)\n',
         '| Index | Spells | Member-months | Covered | Coverage | Spells without any price file | Delisted spells | Delisted coverage | Verdict |',
         '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for k, v in a['a1_constituents'].items():
        verdict = 'PASS' if v['coverage'] >= 0.97 else ('PIT_COVERAGE_GAP' if v['coverage'] >= 0.90 else 'UNUSABLE')
        L.append(f"| {k} | {v['spells']} | {v['member_months']} | {v['covered_months']} | {v['coverage']:.4f} | {v['spells_without_file']} | {v['delisted_spells']} | {v['delisted_coverage']:.4f} | {verdict} |")
    d = a['a2_delisted_depth']
    L += ['\n### 3.2 A2 delisted-history depth\n', f"Delisted common stocks with at least one row: {d['delisted_with_rows']}.",
          'First-date year of delisted histories: ' + ', '.join(f'{k}: {v}' for k, v in sorted(d['delisted_first_year'].items())),
          '\nLast-date year of delisted histories: ' + ', '.join(f'{k}: {v}' for k, v in sorted(d['delisted_last_year'].items())),
          '\n| Year | Names with >= 120 priced days | Delisted share of top-1000 by approximate dollar volume | Min dollar volume in top 1000 |', '| --- | ---: | ---: | ---: |']
    for y, v in sorted(d['top1000_delisted_share'].items()):
        L.append(f"| {y} | {v['n']} | {v['delisted_share']:.3f} | {v['min_dv_top1000']:,.0f} |")
    L.append(f"\nReference 2003-2007 mean delisted share {d['reference_2003_2007']:.3f}; rule: first year with share >= 0.75 x reference -> "
             f"**survivorship-safe Tier 2 start year = {d['survivorship_safe_start_year']}**.")
    r = a['a3_reconciliation']
    L += ['\n### 3.3 A3 reconciliation of known failures and acquisitions\n', '| Code | Event | Expected month | EODHD first | EODHD last | Within one month |', '| --- | --- | --- | --- | --- | --- |']
    for x in r['rows']:
        L.append(f"| {x['code']} | {x['kind']} | {x['expected']} | {x['first']} | {x['eodhd_last']} | {'yes' if x['within_one_month'] else 'NO'} |")
    L.append(f"\nPresent {r['present']}/{r['n']}; within one month {r['within_one_month']}/{r['n']}.")
    L += ['\n### 3.4 A4 ticker-reuse / spell coverage mismatches\n', '| Index | Spells | Mismatches | Share |', '| --- | ---: | ---: | ---: |']
    for k, v in a['a4_ticker_reuse'].items():
        L.append(f"| {k} | {v['spells']} | {v['mismatches']} | {v['share']:.3f} |")
    ex = [x for v in a['a4_ticker_reuse'].values() for x in v['examples']][:12]
    L.append('\nExamples: ' + '; '.join(f"{x['code']} ({x['name']}, {x['reason']}, spell {x['start']}..{x['end']}, series {x.get('first')}..{x.get('last')})" for x in ex))
    s = a['a5_splits']
    L += ['\n### 3.5 A5 split reconciliation\n', '| Code | Date | Expected ratio | Unadjusted close ratio | Adjusted close ratio | Consistent |', '| --- | --- | ---: | ---: | ---: | --- |']
    for x in s['rows']:
        L.append(f"| {x['code']} | {x['date']} | {x['expected']} | {x.get('raw_close_ratio', float('nan')):.3f} | {x.get('adj_close_ratio', float('nan')):.3f} | {x.get('consistent')} |")
    L.append(f"\nConsistent {s['consistent']}/{s['n']}.")
    i = a['a6_integrity']
    L.append(f"\n### 3.6 A6 integrity\n\nFiles with rows {i['files_with_rows']}; empty {i['empty']}; request errors {i['errors']}; files with a non-positive close {i['nonpositive_min_close']}; zero-volume days in total {i['zero_volume_days_total']}.")
    with open(ROOT / 'PHASE6_EODHD_COVERAGE_AUDIT.md', 'a', encoding='utf8') as fh:
        fh.write('\n'.join(L) + '\n')
    print('appended')


if __name__ == '__main__':
    main(sys.argv[1])
