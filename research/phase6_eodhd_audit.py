"""Coverage audit of the EODHD snapshots (data quality only; no strategy return is computed here).

Sections
A1 constituent price coverage: for every S&P 500/400/600 membership spell that overlaps 2012-04-04..2017-12-31,
   the share of member-months with >= 15 priced trading days in the ticker's EOD series.
A2 delisted-history depth: distribution of first/last dates for delisted common stocks and the delisted share of
   the yearly top-1000 approximate-dollar-volume universe (rule for the survivorship-safe start year is fixed
   in PHASE6_EODHD_COVERAGE_AUDIT.md before this runs: first year whose delisted share >= 0.75 x the 2003-2007 mean).
A3 reconciliation list of known failures/acquisitions (PHASE6_UNIVERSE_CONSTRUCTION.md section 5) with the
   EODHD last price date versus the expected month.
A4 ticker-reuse mismatches: constituent spells whose EOD series does not cover the spell (first date > start + 30
   calendar days, or last date < min(end, 2017-12-31) - 30 days).
A5 split reconciliation on a fixed list of well-known splits (unadjusted close jump vs adjusted_close continuity).
A6 basic integrity: duplicate dates, non-positive closes, zero-volume counts.

All dates used here are at or before 2017-12-31 except the descriptive first/last dates of raw files, which
are file metadata (no return or price after the development end is read into any statistic).
Usage (from research/): PYTHONUTF8=1 python phase6_eodhd_audit.py  -> reports/PHASE6_EODHD_AUDIT_<stamp>/audit.json
"""
from datetime import datetime, timezone
import json

import numpy as np
import pandas as pd

import phase6_eodhd as e
import phase6_eodhd_acquire as acq
import phase6_eodhd_panel as pnl
from phase6_lock import ROOT, DEV_END_EXCLUSIVE

DEV_END = DEV_END_EXCLUSIVE - pd.Timedelta(days=1)
PIT_START = pd.Timestamp('2012-04-04')
RECONCILIATION = [  # (code, expected end YYYY-MM, kind)
    ('ENRNQ', '2002-01', 'failure Enron (NYSE delisting 2002-01; OTC trading continued)'),
    ('MCWEQ', '2002-07', 'failure WorldCom'), ('BSC_old', '2008-05', 'failure Bear Stearns'),
    ('LEH', '2008-09', 'failure Lehman Brothers'), ('WAMUQ', '2008-09', 'failure Washington Mutual'),
    ('CCTYQ', '2009-01', 'failure Circuit City'), ('GM_old', '2009-06', 'failure General Motors (old)'),
    ('BLIAQ', '2010-07', 'failure Blockbuster (BB Liquidating)'), ('EKDKQ', '2012-01', 'failure Eastman Kodak (old)'),
    ('RSH', '2015-02', 'failure RadioShack'), ('SUNEQ', '2016-04', 'failure SunEdison'),
    ('CPQ', '2002-05', 'acquisition Compaq'), ('G_old', '2005-10', 'acquisition Gillette'),
    ('BUD_old', '2008-11', 'acquisition Anheuser-Busch'), ('WYE', '2009-10', 'acquisition Wyeth'),
    ('BNI', '2010-02', 'acquisition Burlington Northern'), ('HNZ', '2013-06', 'acquisition Heinz'),
]
KNOWN_SPLITS = [('AAPL', '2014-06-09', 7.0), ('AAPL', '2005-02-28', 2.0), ('MSFT', '2003-02-18', 2.0),
                ('NVDA', '2007-09-11', 1.5), ('GOOGL', '2014-04-03', 2.0), ('AMZN', '1999-09-02', 2.0),
                ('WMT', '1999-04-20', 2.0), ('CSCO', '2000-03-23', 2.0), ('C', '2011-05-09', 0.1)]


def month_count(idx):
    return idx.to_period('M').value_counts()


def a1_constituents(eod):
    out = {}
    for name in acq.INDICES:
        comp = json.loads((e.RAW / 'constituents' / f'comp_{name}.json').read_text(encoding='utf8'))
        spells = []
        for v in comp['HistoricalTickerComponents'].values():
            # StartDate None = member since before the record begins (initial cohort of 2012-04-04)
            s = pd.Timestamp(v['StartDate']) if v.get('StartDate') else PIT_START
            en = pd.Timestamp(v['EndDate']) if v.get('EndDate') else DEV_END
            s2, e2 = max(s, PIT_START), min(en, DEV_END)
            if s2 > e2:
                continue
            rec = eod.get(v['Code'])
            months = pd.period_range(s2, e2, freq='M')
            covered = 0
            has_file = bool(rec and rec.get('status') == 'ok' and rec.get('rows', 0) > 0)
            if has_file:
                df = pnl.read_eod_csv(ROOT / rec['file'])
                df = df[(df.index >= s2 - pd.Timedelta(days=31)) & (df.index <= e2)]
                mc = month_count(df.index)
                covered = int(sum(1 for m in months if mc.get(m, 0) >= 15))
            spells.append(dict(code=v['Code'], start=str(s2.date()), end=str(e2.date()), months=len(months),
                               covered=covered, has_file=has_file, is_delisted=int(v.get('IsDelisted') or 0)))
        df = pd.DataFrame(spells)
        by_year = {}
        for y in range(2012, 2018):
            ys = df[(df['start'] <= f'{y}-12-31') & (df['end'] >= f'{y}-01-01')]
            by_year[y] = dict(spells=int(len(ys)), without_file=int((~ys['has_file']).sum()))
        out[name] = dict(spells=int(len(df)), member_months=int(df['months'].sum()), covered_months=int(df['covered'].sum()),
                         coverage=float(df['covered'].sum() / df['months'].sum()), spells_without_file=int((~df['has_file']).sum()),
                         delisted_spells=int(df['is_delisted'].sum()),
                         delisted_coverage=float(df.loc[df['is_delisted'] == 1, 'covered'].sum() / max(1, df.loc[df['is_delisted'] == 1, 'months'].sum())),
                         by_year=by_year, worst=df.assign(gap=df['months'] - df['covered']).nlargest(15, 'gap').to_dict('records'))
    return out


def a2_delisted_depth(summary):
    s = summary[(summary['status'] == 'ok') & (summary['rows'] > 0)].copy()
    s['first_y'] = pd.to_datetime(s['first']).dt.year
    s['last_y'] = pd.to_datetime(s['last']).dt.year
    d = s[s['list_status'] == 'delisted']
    out = dict(delisted_with_rows=int(len(d)), delisted_first_year=d['first_y'].value_counts().sort_index().to_dict(),
               delisted_last_year=d['last_y'].value_counts().sort_index().to_dict(),
               active_first_year=s[s['list_status'] == 'active']['first_y'].value_counts().sort_index().to_dict())
    # yearly top-1000 by approximate dollar volume (median over the year of adj_close x volume) and its delisted share
    codes = json.loads(pnl.SUPERSET.read_text(encoding='utf8'))['codes'] if pnl.SUPERSET.exists() else []
    eod = acq.load_manifest(acq.EOD_MANIFEST)
    status = dict(zip(summary['code'], summary['list_status']))
    yearly = {}
    for i, code in enumerate(codes):
        df = pnl.read_eod_csv(ROOT / eod[code]['file'])
        df = df[df.index <= DEV_END]
        if df.empty:
            continue
        dv = (df['adj_close'] * df['volume'])
        med = dv.groupby(df.index.year).median()
        cnt = dv.groupby(df.index.year).count()
        for y, v in med.items():
            if cnt[y] >= 120 and np.isfinite(v):
                yearly.setdefault(int(y), []).append((v, status.get(code)))
    share = {}
    for y in sorted(yearly):
        top = sorted(yearly[y], reverse=True)[:1000]
        share[y] = dict(n=len(yearly[y]), top=len(top), delisted_share=float(np.mean([st == 'delisted' for _, st in top])),
                        min_dv_top1000=float(top[-1][0]) if top else None)
    ref = np.mean([share[y]['delisted_share'] for y in range(2003, 2008) if y in share])
    start_year = next((y for y in sorted(share) if share[y]['delisted_share'] >= 0.75 * ref), None)
    out.update(top1000_delisted_share=share, reference_2003_2007=float(ref), rule='first year with delisted share >= 0.75 x ref',
               survivorship_safe_start_year=start_year)
    return out


def a3_reconciliation(eod):
    rows = []
    for code, exp, kind in RECONCILIATION:
        rec = eod.get(code)
        last = rec.get('last') if rec else None
        ok = bool(last) and abs((pd.Period(last[:7], 'M') - pd.Period(exp, 'M')).n) <= 1
        rows.append(dict(code=code, kind=kind, expected=exp, eodhd_last=last, first=rec.get('first') if rec else None,
                         within_one_month=ok, present=bool(rec and rec.get('rows', 0) > 0)))
    return dict(rows=rows, present=int(sum(r['present'] for r in rows)), within_one_month=int(sum(r['within_one_month'] for r in rows)),
                n=len(rows))


def a4_ticker_reuse(eod):
    out = {}
    for name in acq.INDICES:
        comp = json.loads((e.RAW / 'constituents' / f'comp_{name}.json').read_text(encoding='utf8'))
        bad, total = [], 0
        for v in comp['HistoricalTickerComponents'].values():
            # StartDate None = member since before the record begins (initial cohort of 2012-04-04)
            s = pd.Timestamp(v['StartDate']) if v.get('StartDate') else PIT_START
            en = pd.Timestamp(v['EndDate']) if v.get('EndDate') else DEV_END
            s2, e2 = max(s, PIT_START), min(en, DEV_END)
            if s2 > e2:
                continue
            total += 1
            rec = eod.get(v['Code'])
            if not rec or rec.get('rows', 0) == 0:
                bad.append(dict(code=v['Code'], name=v['Name'], reason='no rows', start=str(s2.date()), end=str(e2.date())))
                continue
            f, l = pd.Timestamp(rec['first']), pd.Timestamp(rec['last'])
            if f > s2 + pd.Timedelta(days=30) or l < e2 - pd.Timedelta(days=30):
                bad.append(dict(code=v['Code'], name=v['Name'], reason='series does not cover spell', first=rec['first'], last=rec['last'],
                                start=str(s2.date()), end=str(e2.date())))
        out[name] = dict(spells=total, mismatches=len(bad), share=len(bad) / max(1, total), examples=bad[:25])
    return out


def a5_splits(eod):
    rows = []
    for code, date, ratio in KNOWN_SPLITS:
        rec = eod.get(code)
        if not rec or rec.get('rows', 0) == 0:
            rows.append(dict(code=code, date=date, expected=ratio, present=False)); continue
        df = pnl.read_eod_csv(ROOT / rec['file'])
        d = pd.Timestamp(date)
        before = df[df.index < d].tail(1); after = df[df.index >= d].head(1)
        if before.empty or after.empty:
            rows.append(dict(code=code, date=date, expected=ratio, present=False)); continue
        raw_jump = float(before['close'].iloc[0] / after['close'].iloc[0])
        adj_jump = float(before['adj_close'].iloc[0] / after['adj_close'].iloc[0])
        rows.append(dict(code=code, date=date, expected=ratio, present=True, raw_close_ratio=raw_jump, adj_close_ratio=adj_jump,
                         consistent=bool(abs(raw_jump / ratio - 1) < 0.15 and abs(adj_jump - 1) < 0.15)))
    return dict(rows=rows, consistent=int(sum(1 for r in rows if r.get('consistent'))), n=len(rows))


def a6_integrity(summary):
    s = summary[(summary['status'] == 'ok') & (summary['rows'] > 0)]
    return dict(files_with_rows=int(len(s)), nonpositive_min_close=int((s['min_close'] <= 0).sum()),
                zero_volume_days_total=int(s['n_zero_volume'].sum()), errors=int((summary['status'] != 'ok').sum()),
                empty=int(((summary['status'] == 'ok') & (summary['rows'] == 0)).sum()))


def run():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'PHASE6_EODHD_AUDIT_{stamp}'
    out_dir.mkdir(parents=True)
    eod = acq.load_manifest(acq.EOD_MANIFEST)
    summary = pnl.load_summary()
    res = dict(stamp=stamp, dev_end=str(DEV_END.date()), pit_start=str(PIT_START.date()),
               a1_constituents=a1_constituents(eod), a2_delisted_depth=a2_delisted_depth(summary),
               a3_reconciliation=a3_reconciliation(eod), a4_ticker_reuse=a4_ticker_reuse(eod),
               a5_splits=a5_splits(eod), a6_integrity=a6_integrity(summary))
    (out_dir / 'audit.json').write_text(json.dumps(res, indent=1, default=str), encoding='utf8')
    print(out_dir)
    return res


if __name__ == '__main__':
    r = run()
    for k in ('a1_constituents', 'a3_reconciliation', 'a4_ticker_reuse', 'a5_splits', 'a6_integrity'):
        v = r[k]
        print(k, json.dumps({kk: (vv if not isinstance(vv, dict) else {x: y for x, y in vv.items() if x not in ('worst', 'examples', 'by_year')})
                             for kk, vv in v.items() if kk != 'rows'}, default=str)[:1500])
    d = r['a2_delisted_depth']
    print('delisted first-year', d['delisted_first_year'])
    print('top1000 delisted share', {y: round(v['delisted_share'], 3) for y, v in d['top1000_delisted_share'].items()})
    print('survivorship-safe start year', d['survivorship_safe_start_year'], 'ref', d['reference_2003_2007'])
