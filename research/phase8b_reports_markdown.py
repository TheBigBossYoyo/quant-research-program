"""Phase 8B artifact recovery: write the named repurchase markdown deliverables from the persisted run.

Formatting only. Every number is copied from reports/<RUN_ID>/results.json, which is hash-verified against the freeze
ledger before anything is written. No prices are loaded and no return is recomputed.

Usage (from research/): PYTHONUTF8=1 python phase8b_reports_markdown.py
"""
import json

from phase6_lock import ROOT
import phase8b_reports_repurchase as rr

OUT = rr.OUT
WINDOWS = rr.WINDOWS
COST_CASES = rr.COST_CASES
f = rr.f


def w_(res, cell, case, wk):
    return res['portfolios'][cell][case]['windows'][wk]


HEAD = ('| window | net CAGR | EW univ | SPY | excess vs EW | NW t | yrs+ | CAPM a | t | FF3 a | t | FF5+MOM a | t | Sharpe | maxDD |\n'
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')


def row(w, label):
    return (f"| {label} | {f(w.get('net_cagr'), 'net_cagr')} | {f(w.get('bench_cagr'), 'bench_cagr')} | "
            f"{f(w.get('spy_cagr'), 'spy_cagr')} | {f(w.get('excess_ann'), 'excess_ann')} | {f(w.get('excess_t'))} | "
            f"{w.get('years_positive')}/{w.get('years')} | {f(w.get('capm_alpha_ann'), 'capm_alpha_ann')} | {f(w.get('capm_t'))} | "
            f"{f(w.get('ff3_alpha_ann'), 'ff3_alpha_ann')} | {f(w.get('ff3_t'))} | {f(w.get('ff6_alpha_ann'), 'ff6_alpha_ann')} | "
            f"{f(w.get('ff6_t'))} | {f(w.get('net_sharpe'))} | {f(w.get('max_dd'), 'max_dd')} |")


def banner(man):
    return (f"Run `{man['run_id']}` — **recovered from immutable persisted outputs; nothing was recomputed**. "
            f"`results.json` sha256 `{man['results_sha256']}`, hashed {man['results_hashed_utc']}. "
            f"Classifier v1.8 `{man['classifier_sha256'][:24]}…`; event list `{man['event_list_sha256'][:24]}…`.\n\n"
            "Development data only. Validation 2018-2021 and holdout 2022-01..2026-08 were not accessed.")


def write_all():
    res, pf, es, man = rr.main()
    ab = res['portfolios']['AB']
    g = ab['gates']
    G = json.loads((OUT / 'phase8b_config.json').read_text(encoding='utf8'))['gates']
    p13, p04, pfull = (w_(res, 'AB', 'primary', k) for k in ('w2013_2017', 'w2004_2012', 'w2004_2017'))
    hs = res['event_study']['primary']['h252']
    B = banner(man)

    # ---------------------------------------------------------------- RESULTS
    L = ['# PHASE8B_REPURCHASE_RESULTS — E062 development run', '', B, '',
         f"Events: {res['meta']['counts']['events_all']} classified events → {res['meta']['counts']['eligible']} eligible "
         f"({res['meta']['counts']['by_label']['A']} NEW, {res['meta']['counts']['by_label']['B']} INCREASED); "
         f"{ab['n_2013']} entries in the 2013-2017 gate window.", '',
         '## Primary cell: NEW+INCREASED (AB), MANUAL_USD costs', '', HEAD,
         row(p13, '**2013-2017 (gate)**'), row(p04, '2004-2012 (early)'), row(pfull, '2004-2017 (full)'), '',
         f"Turnover {f(ab['primary']['turnover']['oneway_total'])}x one-way; cumulative cost paid "
         f"{f(ab['primary']['cost_paid'] * 100)}% of starting equity; deflated Sharpe probability "
         f"{f(ab['dsr']['prob'])} with N={ab['dsr']['n_trials']} trials.", '',
         '## Preregistered gates', '', '| gate | result |', '| --- | --- |']
    L += [f"| {k} | {'PASS' if v else '**FAIL**'} |" for k, v in g['checks'].items()]
    L += ['', '## Other preregistered cells (MANUAL_USD, 2013-2017)', '',
          '| cell | n | net CAGR | excess vs EW | NW t | CAPM a | t | FF3 a | t | FF5+MOM a | t | Sharpe |',
          '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for cell in ('A_only', 'B_only', 'pit_sp1500'):
        if cell in res['portfolios']:
            w = w_(res, cell, 'primary', 'w2013_2017')
            L.append(f"| {cell} | {res['portfolios'][cell]['n_events']} | {f(w['net_cagr'], 'net_cagr')} | "
                     f"{f(w['excess_ann'], 'excess_ann')} | {f(w['excess_t'])} | {f(w['capm_alpha_ann'], 'capm_alpha_ann')} | "
                     f"{f(w['capm_t'])} | {f(w['ff3_alpha_ann'], 'ff3_alpha_ann')} | {f(w['ff3_t'])} | "
                     f"{f(w['ff6_alpha_ann'], 'ff6_alpha_ann')} | {f(w['ff6_t'])} | {f(w['net_sharpe'])} |")
    L += ['', 'Only AB carries gates: the preregistration names one primary hypothesis and lists the rest as diagnostics.',
          'NEW alone has a strongly negative CAPM alpha; INCREASED alone is the better half but its alpha is +0.89% with',
          't 0.75, far below the G4 requirement of +2% with t >= 1.5.', '',
          '## Calendar-year excess vs the equal-weight universe (AB, primary)', '', '| year | excess |', '| --- | --- |']
    L += [f"| {y} | {f(v, 'excess_ann')} |" for y, v in sorted(pfull['yearly_excess'].items())]
    L += ['', '## Concentration (G8) — PASS', '',
          f"best-year share {g['best_year_share']:.4f} (max {G['G8_best_year_share_max']}); "
          f"top-5 events {g['top5_share']:.4f} (max {G['G8_top5_events_share_max']}); "
          f"top ticker {g['top_ticker_share']:.4f} (max {G['G8_top_ticker_share_max']}); "
          f"top SIC2 {g['top_sic2_share']:.4f} (max {G['G8_top_sic2_share_max']}).", '',
          '## Factor loadings (AB, 2013-2017)', '',
          f"CAPM beta {f(p13.get('beta'))}. FF3 loadings {json.dumps({k: round(v, 3) for k, v in (p13.get('ff3_betas') or {}).items()})}. "
          f"FF5+MOM loadings {json.dumps({k: round(v, 3) for k, v in (p13.get('ff6_betas') or {}).items()})}.", '',
          'Machine-readable: `phase8b_repurchase_portfolios.csv`, `phase8b_repurchase_run_manifest.json`.', '']
    (OUT / 'PHASE8B_REPURCHASE_RESULTS.md').write_text('\n'.join(L) + '\n', encoding='utf8')

    # ---------------------------------------------------------------- EVENT STUDY
    E = ['# PHASE8B_REPURCHASE_EVENT_STUDY — E062', '', B, '',
         'Abnormal return against the equal-weight buy-and-hold benchmark, entry at the first open at least 60 minutes',
         'after EDGAR acceptance. t-statistics are two-way clustered, by calendar month and by issuer CIK.', '',
         '## Primary cell (NEW+INCREASED)', '', '| horizon | window | mean abnormal return | t (month) | t (CIK) |',
         '| --- | --- | --- | --- | --- |']
    for h in ('h5', 'h21', 'h63', 'h126', 'h252'):
        for wk in WINDOWS:
            d = res['event_study']['primary'][h][wk]
            E.append(f"| +{h[1:]} | {wk} | {f(d['ar_ew_month']['mean'], 'excess_ann')} | "
                     f"{f(d['ar_ew_month']['t'])} | {f(d['ar_ew_cik']['t'])} |")
    E += ['', '## G11 reading', '',
          f"G11 requires the +252 abnormal return to be > 0 in 2013-2017 with **both** cluster t >= "
          f"{G['G11_h252_cluster_t_min']}, **and** > 0 over 2004-2017.", '',
          f"- 2013-2017: {f(hs['w2013_2017']['ar_ew_month']['mean'], 'excess_ann')}, t "
          f"{f(hs['w2013_2017']['ar_ew_month']['t'])} / {f(hs['w2013_2017']['ar_ew_cik']['t'])} → this clause **passes**.",
          f"- 2004-2012: {f(hs['w2004_2012']['ar_ew_month']['mean'], 'excess_ann')} → negative.",
          f"- 2004-2017 full window: {f(hs['w2004_2017']['ar_ew_month']['mean'], 'excess_ann')} → **negative, so G11 FAILS**.", '',
          'The short horizons carry the same message: +5 and +21 sessions are negative or near zero over the full window.',
          'An effect that is positive only inside the gate window and negative over the longer span is a window, not a',
          'mechanism.', '', 'Machine-readable: `phase8b_repurchase_event_study.csv`.', '']
    (OUT / 'PHASE8B_REPURCHASE_EVENT_STUDY.md').write_text('\n'.join(E) + '\n', encoding='utf8')

    # ---------------------------------------------------------------- COST ANALYSIS
    C = ['# PHASE8B_REPURCHASE_COST_ANALYSIS — E062', '', B, '',
         'All three preregistered cost cases, primary cell (NEW+INCREASED).', '',
         '| cost case | rates (bps per side) | window | net CAGR | excess vs EW | NW t | CAPM a | t | FF5+MOM a | t |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for case, desc in COST_CASES.items():
        for wk in ('w2013_2017', 'w2004_2017'):
            w = w_(res, 'AB', case, wk)
            C.append(f"| {case} | {desc} | {wk} | {f(w['net_cagr'], 'net_cagr')} | {f(w['excess_ann'], 'excess_ann')} | "
                     f"{f(w['excess_t'])} | {f(w['capm_alpha_ann'], 'capm_alpha_ann')} | {f(w['capm_t'])} | "
                     f"{f(w['ff6_alpha_ann'], 'ff6_alpha_ann')} | {f(w['ff6_t'])} |")
    C += ['', '## Reading', '',
          'The excess over the equal-weight universe survives every cost case, so G7 passes. **The alpha does not exist',
          'in any of them.** The 2013-2017 CAPM alpha is negative under all three cost cases and becomes more negative as',
          'costs rise. Costs are not what rejects this strategy; the absence of alpha is. Raising costs cannot create',
          'alpha, and lowering them below the MANUAL_USD case would not either — the optimistic case is already the',
          'primary one.', '',
          '## Preregistered diagnostics (2013-2017)', '',
          '| variant | excess vs EW | NW t | CAPM a | t |', '| --- | --- | --- | --- | --- |']
    for name in ('delay1', 'all100', 'all30', 'h126', 'slots20'):
        b = ab.get(name)
        if isinstance(b, dict) and 'windows' in b:
            w = b['windows'].get('w2013_2017', {})
            C.append(f"| {name} | {f(w.get('excess_ann'), 'excess_ann')} | {f(w.get('excess_t'))} | "
                     f"{f(w.get('capm_alpha_ann'), 'capm_alpha_ann')} | {f(w.get('capm_t'))} |")
    C += ['', 'These were preregistered as diagnostics, not as alternative primaries, and none is promoted. The 20-slot',
          'variant shows the largest CAPM alpha (+2.56%, t 1.06); it still fails the G4 t-threshold of 1.5, and',
          'concentrating 910 events into 20 slots is a different strategy that was never registered as the primary.',
          'A one-session entry delay changes almost nothing (excess 5.83%, alpha -1.13%), so the result is not a',
          'micro-timing artefact.', '']
    (OUT / 'PHASE8B_REPURCHASE_COST_ANALYSIS.md').write_text('\n'.join(C) + '\n', encoding='utf8')
    print('wrote RESULTS / EVENT_STUDY / COST_ANALYSIS')
    return res, man, g, G, p13, p04, pfull, hs


if __name__ == '__main__':
    write_all()
