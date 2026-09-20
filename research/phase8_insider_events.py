"""Phase 8 Stage 1: build the insider open-market purchase event table from the SEC data sets (frozen rules, no returns).

Implements PHASE8_EVENT_RULES.md sections 2-5 and PHASE8_DATA_AUDIT.md D1-D6, D8. Prices are used only for the
price-plausibility filter and the mapping check (unadjusted close on/before the transaction date), never for returns.
Outputs: data/derived/phase8/rows_p.parquet (filtered rows), events.parquet (issuer-filing-day events with cell flags),
audit.json (counts). Usage (from research/): PYTHONUTF8=1 python phase8_insider_events.py
"""
from datetime import datetime, timezone
import io
import json
import re
import zipfile

import numpy as np
import pandas as pd

import phase6_eodhd_panel as pnl
from phase6_lock import ROOT, assert_development

RAW = ROOT / 'data/raw/phase8/sec_insider'
DERIVED = ROOT / 'data/derived/phase8'
QUARTERS = [f'{y}q{q}' for y in range(2006, 2018) for q in (1, 2, 3, 4)]
SEC_TITLE_OK = re.compile(r'(common|ordinary|class [abc]\b|capital stock|shares of beneficial interest)')
SEC_TITLE_BAD = re.compile(r'(preferred|warrant|unit|note|debenture|right|option|convertible|restricted|deposit|adr|preference)')
MIN_VALUE = 10_000.0
PRICE_BAND = (0.80, 1.20)
CLUSTER_DAYS = 30
BURNIN_YEARS = 3
DEV_START = pd.Timestamp('2009-01-01')


def read_tsv(z, name):
    return pd.read_csv(io.BytesIO(z.read(name)), sep='\t', dtype=str, encoding='latin1', quoting=3, on_bad_lines='skip')


def load_quarters():
    subs, owners, trans = [], [], []
    for q in QUARTERS:
        z = zipfile.ZipFile(RAW / f'{q}_form345.zip')
        names = set(z.namelist())
        assert {'SUBMISSION.tsv', 'REPORTINGOWNER.tsv', 'NONDERIV_TRANS.tsv'} <= names, q
        s = read_tsv(z, 'SUBMISSION.tsv'); s['quarter'] = q
        t = read_tsv(z, 'NONDERIV_TRANS.tsv'); t = t[t['TRANS_CODE'] == 'P']
        o = read_tsv(z, 'REPORTINGOWNER.tsv')
        subs.append(s[['ACCESSION_NUMBER', 'FILING_DATE', 'PERIOD_OF_REPORT', 'DATE_OF_ORIG_SUB', 'DOCUMENT_TYPE', 'ISSUERCIK', 'ISSUERNAME', 'ISSUERTRADINGSYMBOL', 'quarter']])
        owners.append(o[['ACCESSION_NUMBER', 'RPTOWNERCIK', 'RPTOWNERNAME', 'RPTOWNER_RELATIONSHIP']])
        trans.append(t[['ACCESSION_NUMBER', 'NONDERIV_TRANS_SK', 'SECURITY_TITLE', 'TRANS_DATE', 'TRANS_FORM_TYPE', 'TRANS_CODE', 'EQUITY_SWAP_INVOLVED', 'TRANS_TIMELINESS',
                        'TRANS_SHARES', 'TRANS_PRICEPERSHARE', 'TRANS_ACQUIRED_DISP_CD', 'DIRECT_INDIRECT_OWNERSHIP']])
        print(q, len(s), len(t), flush=True)
    return pd.concat(subs, ignore_index=True), pd.concat(owners, ignore_index=True), pd.concat(trans, ignore_index=True)


def norm_symbol(s):
    if not isinstance(s, str):
        return None
    s = s.strip().upper().replace('.', '-')
    for suf in ('-OB', '-PK', '-OTC', '-OQ', '-NB'):
        if s.endswith(suf):
            s = s[: -len(suf)]
    return s or None


def business_days(a, b):
    return np.busday_count(a.values.astype('datetime64[D]'), b.values.astype('datetime64[D]'))


def main():
    DERIVED.mkdir(parents=True, exist_ok=True)
    subs, owners, trans = load_quarters()
    audit = dict(quarters=len(QUARTERS), submissions=int(len(subs)), code_p_rows=int(len(trans)))
    audit['document_types'] = subs['DOCUMENT_TYPE'].value_counts().to_dict()
    # row filters
    df = trans.merge(subs, on='ACCESSION_NUMBER', how='inner')
    df['FILING_DATE'] = pd.to_datetime(df['FILING_DATE'], format='%d-%b-%Y', errors='coerce')
    df['TRANS_DATE'] = pd.to_datetime(df['TRANS_DATE'], format='%d-%b-%Y', errors='coerce')
    df['shares'] = pd.to_numeric(df['TRANS_SHARES'], errors='coerce'); df['price'] = pd.to_numeric(df['TRANS_PRICEPERSHARE'], errors='coerce')
    steps = {}
    steps['0_code_p_joined'] = len(df)
    df = df[df['DOCUMENT_TYPE'] == '4']; steps['1_original_form4'] = len(df)
    df = df[(df['TRANS_ACQUIRED_DISP_CD'] == 'A') & (df['TRANS_FORM_TYPE'].fillna('4') == '4')]; steps['2_acquired_form4_trans'] = len(df)
    title = df['SECURITY_TITLE'].fillna('').str.lower()
    df = df[title.str.contains(SEC_TITLE_OK) & ~title.str.contains(SEC_TITLE_BAD)]; steps['3_common_equity_title'] = len(df)
    df = df[(df['shares'] > 0) & (df['price'] > 0)]; steps['4_positive_shares_price'] = len(df)
    df = df[df['EQUITY_SWAP_INVOLVED'].fillna('0').isin(['0', 'false', 'False'])]; steps['5_no_swap'] = len(df)
    df = df[df['FILING_DATE'].notna() & df['TRANS_DATE'].notna()]
    df['delay_bdays'] = business_days(df['TRANS_DATE'], df['FILING_DATE'])
    neg = int((df['delay_bdays'] < 0).sum()); df = df[df['delay_bdays'] >= 0]; steps['6_nonnegative_delay'] = len(df); audit['negative_delay_rows'] = neg
    df['value'] = df['shares'] * df['price']
    df = df[df['value'] >= MIN_VALUE]; steps['7_value_ge_10k'] = len(df)
    # duplicates
    n0 = len(df)
    df = df.drop_duplicates(['ACCESSION_NUMBER', 'TRANS_DATE', 'shares', 'price', 'SECURITY_TITLE', 'DIRECT_INDIRECT_OWNERSHIP'])
    audit['within_accession_duplicates'] = n0 - len(df)
    # owners: one row per accession-owner; attach relationship
    own = owners.drop_duplicates(['ACCESSION_NUMBER', 'RPTOWNERCIK'])
    rel = own.groupby('ACCESSION_NUMBER').agg(owner_ciks=('RPTOWNERCIK', lambda x: '|'.join(sorted(set(x)))), n_owners_filing=('RPTOWNERCIK', 'nunique'),
                                             relationships=('RPTOWNER_RELATIONSHIP', lambda x: '|'.join(sorted(set(x.fillna('')))))).reset_index()
    df = df.merge(rel, on='ACCESSION_NUMBER', how='left')
    df['owner_cik'] = df['owner_ciks'].str.split('|').str[0]   # a Form 4 has one reporting owner in almost all cases; joint filings keep the first
    n0 = len(df)
    df = df.sort_values('FILING_DATE').drop_duplicates(['ISSUERCIK', 'owner_cik', 'TRANS_DATE', 'shares', 'price'], keep='first')
    audit['cross_accession_duplicates'] = n0 - len(df); steps['8_after_duplicates'] = len(df)
    # amendments diagnostic: originals later amended (4/A with same issuer, owner, DATE_OF_ORIG_SUB = original filing date)
    amend = subs[subs['DOCUMENT_TYPE'] == '4/A'].copy(); amend['DATE_OF_ORIG_SUB'] = pd.to_datetime(amend['DATE_OF_ORIG_SUB'], format='%d-%b-%Y', errors='coerce')
    amend = amend.merge(own[['ACCESSION_NUMBER', 'RPTOWNERCIK']], on='ACCESSION_NUMBER', how='left')
    key_amend = set(zip(amend['ISSUERCIK'], amend['RPTOWNERCIK'], amend['DATE_OF_ORIG_SUB']))
    df['later_amended'] = [((i, o, d) in key_amend) for i, o, d in zip(df['ISSUERCIK'], df['owner_cik'], df['FILING_DATE'])]
    audit['originals_later_amended'] = int(df['later_amended'].sum())
    # mapping to EODHD codes and price plausibility
    close = pnl.load_panel('close')
    assert_development(close.index)
    summary = pnl.load_summary(); have = set(close.columns)
    tick = json.load(open(ROOT / 'data/metadata/company_tickers.json', encoding='utf8')) if (ROOT / 'data/metadata/company_tickers.json').exists() else {}
    cik2sym = {str(int(v['cik_str'])): v['ticker'].upper().replace('.', '-') for v in tick.values()} if tick else {}
    df['sym'] = df['ISSUERTRADINGSYMBOL'].map(norm_symbol)
    df['cik_int'] = df['ISSUERCIK'].str.lstrip('0')

    def priced_close(code, d):
        if code not in have:
            return np.nan
        s = close[code].loc[:d].dropna()
        if s.empty or (d - s.index[-1]).days > 7:
            return np.nan
        return float(s.iloc[-1])

    codes, closes, route = [], [], []
    cache = {}
    for sym, cik, d in zip(df['sym'], df['cik_int'], df['TRANS_DATE']):
        cands = []
        if sym:
            cands += [sym, sym + '_old', sym + '_old1', sym + '_old2']
        if cik in cik2sym:
            cands.append(cik2sym[cik])
        found, c_found, r_found = None, np.nan, 'unmapped'
        for k, c in enumerate(cands):
            key = (c, d)
            if key not in cache:
                cache[key] = priced_close(c, d)
            if np.isfinite(cache[key]):
                found, c_found, r_found = c, cache[key], ('symbol' if k == 0 else ('old_variant' if k < 4 or (sym and k < 4) else 'cik')) if sym else 'cik'
                break
        codes.append(found); closes.append(c_found); route.append(r_found)
    df['code'] = codes; df['close_ref'] = closes; df['map_route'] = route
    audit['mapping_by_year'] = {int(y): dict(rows=int(len(g)), mapped=int(g['code'].notna().sum()), mapped_share=float(g['code'].notna().mean())) for y, g in df.groupby(df['FILING_DATE'].dt.year)}
    df = df[df['code'].notna()]; steps['9_mapped'] = len(df)
    ratio = df['price'] / df['close_ref']
    ok = (ratio >= PRICE_BAND[0]) & (ratio <= PRICE_BAND[1])
    audit['price_plausibility_pass_share'] = float(ok.mean()); df = df[ok]; steps['10_price_plausible'] = len(df)
    audit['filter_steps'] = steps
    df['timely'] = df['delay_bdays'] <= 2
    df['is_officer'] = df['relationships'].fillna('').str.contains('Officer'); df['is_director'] = df['relationships'].fillna('').str.contains('Director')
    df['is_tenpct'] = df['relationships'].fillna('').str.contains('TenPercent')
    df.to_parquet(DERIVED / 'rows_p.parquet', index=False)
    # events: issuer-filing-day
    ev = df.groupby(['ISSUERCIK', 'code', 'FILING_DATE']).agg(n_rows=('value', 'size'), n_owners=('owner_cik', 'nunique'), value=('value', 'sum'),
                                                          first_trans=('TRANS_DATE', 'min'), max_delay=('delay_bdays', 'max'), timely=('timely', 'all'),
                                                          officer=('is_officer', 'any'), director=('is_director', 'any'), tenpct=('is_tenpct', 'any'),
                                                          direct=('DIRECT_INDIRECT_OWNERSHIP', lambda x: (x == 'D').any()), later_amended=('later_amended', 'any'),
                                                          owners=('owner_cik', lambda x: '|'.join(sorted(set(x))))).reset_index()
    ev = ev.sort_values(['ISSUERCIK', 'FILING_DATE']).reset_index(drop=True)
    # cluster: >= 2 distinct owners with included purchases of the issuer in the 30 days ending on FILING_DATE
    cluster = []
    for cik, g in ev.groupby('ISSUERCIK'):
        dates, owners_l = g['FILING_DATE'].to_numpy(), g['owners'].tolist()
        for i in range(len(g)):
            window = set()
            j = i
            while j >= 0 and (dates[i] - dates[j]) <= np.timedelta64(CLUSTER_DAYS, 'D'):
                window |= set(owners_l[j].split('|')); j -= 1
            cluster.append(len(window) >= 2)
    ev['cluster'] = pd.Series(cluster, index=ev.index) if len(cluster) == len(ev) else False
    # opportunistic (CMP adapted): per owner-issuer, prior distinct purchase years >= 3; routine if same-month purchase in each of the 3 preceding years
    rows_sorted = df.sort_values('TRANS_DATE')
    hist = {}
    opp_flag = {}
    for (cik, owner), g in rows_sorted.groupby(['ISSUERCIK', 'owner_cik']):
        ym = sorted(set(zip(g['TRANS_DATE'].dt.year, g['TRANS_DATE'].dt.month)))
        hist[(cik, owner)] = ym
    ev_opp = []
    for cik, code, fd, owners_s, ft in zip(ev['ISSUERCIK'], ev['code'], ev['FILING_DATE'], ev['owners'], ev['first_trans']):
        flag = False
        for o in owners_s.split('|'):
            ym = [x for x in hist.get((cik, o), []) if x < (ft.year, ft.month)]
            years = {y for y, m in ym}
            if len(years) >= BURNIN_YEARS:
                routine = all((ft.year - k, ft.month) in set(ym) for k in (1, 2, 3))
                if not routine:
                    flag = True
        ev_opp.append(flag)
    ev['opportunistic'] = ev_opp
    ev['director_only'] = ev['director'] & ~ev['officer']
    ev = ev[ev['FILING_DATE'] >= DEV_START - pd.DateOffset(years=BURNIN_YEARS)]
    audit['events_total'] = int(len(ev))
    audit['events_by_year'] = {int(y): dict(n=int(len(g)), cluster=int(g['cluster'].sum()), opportunistic=int(g['opportunistic'].sum()), officer=int(g['officer'].sum()),
                                            director_only=int(g['director_only'].sum()), timely_share=float(g['timely'].mean()), median_value=float(g['value'].median()))
                               for y, g in ev.groupby(ev['FILING_DATE'].dt.year)}
    ev.to_parquet(DERIVED / 'events.parquet', index=False)
    audit['built_utc'] = datetime.now(timezone.utc).isoformat()
    (DERIVED / 'audit.json').write_text(json.dumps(audit, indent=1, default=str), encoding='utf8')
    print(json.dumps({k: v for k, v in audit.items() if k not in ('mapping_by_year', 'events_by_year')}, indent=1, default=str))
    print('events by year', {y: (v['n'], v['cluster'], v['opportunistic']) for y, v in audit['events_by_year'].items()})
    print('mapping by year', {y: round(v['mapped_share'], 2) for y, v in audit['mapping_by_year'].items()})


if __name__ == '__main__':
    main()
