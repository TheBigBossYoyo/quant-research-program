"""Render E051 results into PHASE6_E051_RESULTS.md, PHASE6_NORGATE_DECISION.md and registry rows.

The decision is computed mechanically from results.json with the rules of PHASE6_NORGATE_PURCHASE_GATE.md
(sections 4-5) and the audit outcome recorded in the audit JSON. Nothing here re-runs a backtest.
Usage (from research/): PYTHONUTF8=1 python phase6_e051_report.py E051_<stamp> PHASE6_EODHD_AUDIT_<stamp>
"""
import csv
import json
import sys

import pandas as pd

from phase6_lock import ROOT

CUMULATIVE_BEFORE = 398


def pct(x, d=2):
    return 'nan' if x is None or (isinstance(x, float) and x != x) else f'{100 * x:.{d}f}%'


def f2(x):
    return 'nan' if x is None or (isinstance(x, float) and x != x) else f'{x:.2f}'


def reconciliation_amended(audit):
    """Amendment 1 (pre-result, 2026-09-11): a failure is captured if its series starts at or before the expected month
    and does not end before the month preceding it (OTC continuation after an exchange delisting is more complete data,
    not a defect); an acquisition must end within one month of the expected month. SunEdison is checked on SUNE_old
    (the NYSE series) instead of the post-bankruptcy OTC code. Both the original and the amended counts are reported."""
    import phase6_eodhd_acquire as acq
    eod = acq.load_manifest(acq.EOD_MANIFEST)
    rows = []
    for r in audit['a3_reconciliation']['rows']:
        code = 'SUNE_old' if r['code'] == 'SUNEQ' else r['code']
        rec = eod.get(code, {})
        first, last = rec.get('first'), rec.get('last')
        exp = pd.Period(r['expected'], 'M')
        present = bool(rec.get('rows', 0) > 0 and first and pd.Period(first[:7], 'M') <= exp)
        if r['kind'].startswith('failure'):
            ok = present and pd.Period(last[:7], 'M') >= exp - 1
        else:
            ok = present and abs((pd.Period(last[:7], 'M') - exp).n) <= 1
        rows.append(dict(code=code, kind=r['kind'], expected=r['expected'], first=first, last=last, present=present, captured=bool(ok)))
    return dict(rows=rows, present=int(sum(x['present'] for x in rows)), captured=int(sum(x['captured'] for x in rows)), n=len(rows),
                original_present=audit['a3_reconciliation']['present'], original_within_one_month=audit['a3_reconciliation']['within_one_month'])


def data_gate(audit):
    a3 = audit['a3_reconciliation']; a5 = audit['a5_splits']; a2 = audit['a2_delisted_depth']; a1 = audit['a1_constituents']
    t2 = a2.get('survivorship_safe_start_year')
    am = reconciliation_amended(audit)
    checks = dict(D1_reconciliation=(am['present'] >= 15 and am['captured'] >= 12),
                  D1_original_rule=(a3['present'] >= 15 and a3['within_one_month'] >= 12),
                  D2_splits=(a5['consistent'] == 9), D3_t2_start=(t2 is not None and t2 <= 2005),
                  D4_tier1_coverage=all(v['coverage'] >= 0.90 for v in a1.values()))
    decisive = {k: v for k, v in checks.items() if k != 'D1_original_rule'}
    return dict(checks=checks, passes=all(decisive.values()), t2_start_year=t2, reconciliation_amended=am,
                tier1_coverage={k: v['coverage'] for k, v in a1.items()})


def decide(res, audit):
    D = data_gate(audit)
    results = res['results']
    t2_survivors = [tid for tid, r in results.items() if r['tier'] == 'LIQ1000' and r['survivor'].get('final')]
    etf_survivors = [tid for tid, r in results.items() if r['tier'] == 'SECTOR_ETF' and r['survivor'].get('final')]
    t1_survivors = [tid for tid, r in results.items() if r['tier'] == 'PIT_SP1500' and r['survivor'].get('final')]
    qualifying, notes = [], []
    for tid in t2_survivors:
        r = results[tid]
        f = r['feasibility']['500']
        sb = r['stats']['base|base']
        gross_ex = sb['excess_ew']['mean'] * 12 + f['cost_pct_per_year']
        f1 = f['cost_pct_per_year'] <= 0.5 * gross_ex if gross_ex > 0 else False
        f2_ = not f['trades_below_1eur']
        rep = f'T1_{r["family"]}_{ {"mom": "mom12_1", "resid": "resid12_1"}.get(r["architecture"], r["architecture"]) }_N30'
        c = results.get(rep, {}).get('stats', {}).get('base|base', {}).get('excess_ew', {}).get('mean')
        cpass = c is not None and c > 0
        notes.append(dict(trial=tid, F1=f1, F2=f2_, C_cell=rep, C_mean=c, C=cpass))
        if f1 and f2_ and cpass:
            qualifying.append(tid)
    buy = D['passes'] and len(qualifying) > 0
    reason = []
    if not D['passes']:
        reason.append('data validity gate D failed: ' + ', '.join(k for k, v in D['checks'].items() if not v))
    if not t2_survivors:
        reason.append('no Tier 2 stock-level trial passed the survivor and multiplicity gates')
    elif not qualifying:
        reason.append('Tier 2 survivors failed feasibility or Tier 1 corroboration: ' + json.dumps(notes))
    return dict(decision='BUY_NORGATE' if buy else 'DO_NOT_BUY_NORGATE', data_gate=D, t2_survivors=t2_survivors,
                etf_survivors=etf_survivors, t1_survivors=t1_survivors, qualifying=qualifying, feasibility_notes=notes, reason=reason)


def trial_table(res):
    rows = []
    for tid, r in res['results'].items():
        sb = r['stats']['base|base']; ss = r['stats']['stress|base']; so = r['stats']['optimistic|base']
        eras = ' / '.join(f"{k}:{'+' if v['positive'] else '-'}{f2(v['t'])}" for k, v in sb['eras'].items())
        chk = r['survivor']['checks']
        fails = ','.join(k for k, v in chk.items() if not v)
        rows.append(f"| {tid} | {sb['months']} | {pct(sb['net']['cagr'],1)} | {pct(sb['bench']['cagr'],1)} | {pct(sb['spy']['cagr'],1)} | "
                    f"{f2(sb['net']['sharpe'])} | {pct(sb['net']['max_dd'],0)} | {pct(sb['excess_ew']['mean']*12,1)} | {f2(sb['excess_ew']['t'])} | "
                    f"[{pct(sb['excess_ew']['boot']['mean_ci'][0]*12,1)}, {pct(sb['excess_ew']['boot']['mean_ci'][1]*12,1)}] | {pct(ss['excess_ew']['mean']*12,1)} | "
                    f"{eras} | {pct(sb['recent_36m']['mean']*12,1)} | {pct(sb['rolling60_positive_share'],0)} | {f2(sb['capm_vs_spy']['t'])} | "
                    f"{r.get('dsr',{}).get('prob','nan') if isinstance(r.get('dsr',{}).get('prob'), str) else f2(r.get('dsr',{}).get('prob'))} | {'Y' if r.get('bh_pass') else 'N'} | "
                    f"{'SURVIVOR' if r['survivor'].get('final') else ('REJECTED_DECAY' if r['survivor'].get('decay_flag') else 'REJECTED')} | {fails or '-'} |")
    head = ('| Trial | Months | Net CAGR | EW bench CAGR | SPY CAGR | Net Sharpe | Max DD | Net excess vs EW (ann.) | HAC t | Boot 95% CI (ann.) | '
            'Stress excess (ann.) | Eras (sign t) | Last 36m excess (ann.) | Rolling-60 positive | CAPM alpha t vs SPY | DSR | BH | Class | Failed gates |\n'
            '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | --- |\n')
    return head + '\n'.join(rows)


def detail_tables(res):
    out = []
    for tid, r in res['results'].items():
        if not r['primary'] and not r['survivor'].get('final'):
            continue
        sb = r['stats']['base|base']
        out.append(f"### {tid} (tier {r['tier']}, avg held {f2(r['avg_held'])})\n")
        out.append('| Variant | Net CAGR | Net Sharpe | Max DD | Excess vs EW (ann.) | t | Turnover one-way/yr | Cost/yr |\n| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
        for k, v in r['stats'].items():
            out.append(f"| {k} | {pct(v['net']['cagr'],1)} | {f2(v['net']['sharpe'])} | {pct(v['net']['max_dd'],0)} | {pct(v['excess_ew']['mean']*12,1)} | {f2(v['excess_ew']['t'])} | - | - |")
        out.append('')
        out.append('Rolling 60-month windows (end year: annualised net excess vs EW, HAC t, net Sharpe): ' +
                   '; '.join(f"{w['end']}: {pct(w['mean']*12,1)}, {f2(w['t'])}, {f2(w['net_sharpe'])}" for w in sb['rolling60']))
        c = sb['concentration']
        out.append(f"\nConcentration: best year {c['best_year']} = {pct(c['best_year_share'],0)} of total net arithmetic return; top-5 months {pct(c['top5_month_share'],0)}; "
                   f"top-10 names {pct(r['top10_name_share'],0)} of gross contribution; worst 12 months {pct(c['worst_12m'],1)}.")
        sbeta = r.get('sector_betas')
        if sbeta:
            out.append(f"Market beta vs SPY {f2(sb['capm_vs_spy']['betas'][0])}; sector-ETF regression R2 {f2(sbeta['r2'])}, largest loadings: " +
                       ', '.join(f'{k} {f2(v)}' for k, v in sorted(sbeta['betas'].items(), key=lambda kv: -abs(kv[1]))[:4]))
        for cap, f in r['feasibility'].items():
            out.append(f"Feasibility EUR {cap}: position USD {f['position_usd']:.0f}, one-way turnover {f['one_way_turnover_per_year']:.1f}x/yr, "
                       f"cost {pct(f['cost_pct_per_year'],2)}/yr = USD {f['cost_usd_per_year']:.0f}, typical trade USD {f['min_trade_usd']:.1f}{' (below EUR 1)' if f['trades_below_1eur'] else ''}")
        out.append('')
    return '\n'.join(out)


def overlay_table(res):
    if not res['overlays']:
        return 'No trial passed the survivor and multiplicity gates; no overlay was computed (preregistered rule).'
    rows = ['| Survivor | Overlay | Net CAGR (base -> overlay) | Net Sharpe | Max DD | Excess vs EW t |', '| --- | --- | --- | --- | --- | --- |']
    for k, v in res['overlays'].items():
        tid, name = k.split('|')
        s = v['stats']; b = v['base_net']
        rows.append(f"| {tid} | {name} | {pct(b['cagr'],1)} -> {pct(s['net']['cagr'],1)} | {f2(b['sharpe'])} -> {f2(s['net']['sharpe'])} | {pct(b['max_dd'],0)} -> {pct(s['net']['max_dd'],0)} | {f2(s['excess_ew']['t'])} |")
    return '\n'.join(rows)


def write_registry(res, stamp):
    path = ROOT / 'PHASE6_EXPERIMENT_REGISTRY.csv'
    n = CUMULATIVE_BEFORE
    rows = []
    for tid, r in res['results'].items():
        n += 1
        cls = 'SURVIVOR' if r['survivor'].get('final') else ('REJECTED_DECAY' if r['survivor'].get('decay_flag') else 'REJECTED')
        rows.append(['E051', stamp, tid, r['family'], r['architecture'], f"L{r['lookback']}_N{r['N']}", f"EODHD {r['tier']}", 'development', n, cls])
    with open(path, 'a', newline='', encoding='utf8') as fh:
        csv.writer(fh).writerows(rows)
    return n


def main(run, audit_name):
    res = json.loads((ROOT / 'reports' / run / 'results.json').read_text(encoding='utf8'))
    audit = json.loads((ROOT / 'reports' / audit_name / 'audit.json').read_text(encoding='utf8'))
    dec = decide(res, audit)
    meta = res['meta']
    md = [f"# PHASE6_E051_RESULTS - stock-level momentum family on EODHD ({run}; development only, <= {meta['development_end']})\n",
          f"Gate document hash at run time: {meta['gate_doc_sha256']} (frozen value in PHASE6_NORGATE_PURCHASE_GATE.sha256). Trials {meta['n_trials']}; "
          f"Tier 2 start year {meta['t2_start_year']} (audit rule A2); signals {meta['signals']['first']}..{meta['signals']['last']} ({meta['signals']['n']}); "
          f"seed {meta['seed']}; bootstrap draws {meta['boot_draws']}. Universe counts per year (min/median/max eligible names) and delistings booked are in results.json meta.\n",
          '## 1. All trials (base cost 20/20.3 bps, base delisting rule). Every preregistered cell is shown; nothing was dropped.\n',
          trial_table(res), '\n## 2. Primary cells and survivors in detail (cost cases and delisting sensitivities)\n', detail_tables(res),
          '\n## 3. Overlays (survivors only)\n', overlay_table(res),
          '\n## 4. Benchmarks (monthly, full window of each tier)\n',
          '\n'.join(f"- {k}: CAGR {pct(v['cagr'],1)}, Sharpe {f2(v['sharpe'])}, max DD {pct(v['max_dd'],0)}, months {v['n']}" for k, v in res['benchmarks'].items()),
          f"\n## 5. Universe\n\nEligible counts per year: {json.dumps(meta['universe_counts'])}\n\nDelistings booked inside eligible sets: {json.dumps(meta['delistings_booked_in_eligible'])}; "
          f"sector labels available for {meta['sector_labels_available']} current constituents only (SECTOR_NOT_PIT).\n"]
    (ROOT / 'PHASE6_E051_RESULTS.md').write_text('\n'.join(md), encoding='utf8')
    dmd = [f"# PHASE6_NORGATE_DECISION ({run})\n", f"# **{dec['decision']}**\n",
           'Computed mechanically by research/phase6_e051_report.py from the frozen rules of PHASE6_NORGATE_PURCHASE_GATE.md.\n',
           f"Data validity gate D: {'PASS' if dec['data_gate']['passes'] else 'FAIL'} {json.dumps(dec['data_gate']['checks'])}; Tier 2 start year {dec['data_gate']['t2_start_year']}; "
           f"Tier 1 coverage {json.dumps({k: round(v, 3) for k, v in dec['data_gate']['tier1_coverage'].items()})}.\n",
           f"Tier 2 survivors (S0-S6 + M1-M2): {dec['t2_survivors'] or 'none'}. Tier 1 survivors: {dec['t1_survivors'] or 'none'}. Sector-ETF survivors: {dec['etf_survivors'] or 'none'}.\n",
           f"Feasibility/corroboration notes: {json.dumps(dec['feasibility_notes'])}\n", f"Qualifying stock-level trials: {dec['qualifying'] or 'none'}.\n",
           'Reasons: ' + ('; '.join(dec['reason']) if dec['reason'] else 'all gate conditions satisfied by a Tier 2 stock-level trial.') + '\n']
    (ROOT / 'PHASE6_NORGATE_DECISION.md').write_text('\n'.join(dmd), encoding='utf8')
    n = write_registry(res, meta['stamp'])
    print(dec['decision'], 'cumulative hypotheses', n)
    return dec


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
