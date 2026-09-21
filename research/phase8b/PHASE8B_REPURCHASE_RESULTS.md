# PHASE8B_REPURCHASE_RESULTS — E062 development run

Run `E062_20260920T214738` — **recovered from immutable persisted outputs; nothing was recomputed**. `results.json` sha256 `5812e0b5ba782b42c4dfbdcc27051f9444bfdc9fc789a6c016512a20356f7d84`, hashed 2026-09-20T21:49:41.977193+00:00. Classifier v1.8 `4a0c6b54a9a7b49cc8df04e8…`; event list `dd0dc6c85765a6326ad9321a…`.

Development data only. Validation 2018-2021 and holdout 2022-01..2026-08 were not accessed.

Events: 7806 classified events → 2378 eligible (1205 NEW, 1173 INCREASED); 910 entries in the 2013-2017 gate window.

## Primary cell: NEW+INCREASED (AB), MANUAL_USD costs

| window | net CAGR | EW univ | SPY | excess vs EW | NW t | yrs+ | CAPM a | t | FF3 a | t | FF5+MOM a | t | Sharpe | maxDD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **2013-2017 (gate)** | 14.94% | 8.25% | 15.22% | 6.03% | 5.18 | 5/5 | -0.91% | -0.56 | -0.43% | -0.28 | -0.38% | -0.24 | 1.27 | -17.35% |
| 2004-2012 (early) | 10.30% | 3.49% | 5.05% | 6.20% | 3.84 | 9/9 | 4.82% | 2.05 | 3.77% | 2.13 | 3.48% | 2.23 | 0.51 | -54.36% |
| 2004-2017 (full) | 11.92% | 5.14% | 8.53% | 6.14% | 5.47 | 14/14 | 2.35% | 1.35 | 1.75% | 1.36 | 1.51% | 1.36 | 0.67 | -54.36% |

Turnover 2.43x one-way; cumulative cost paid 11.81% of starting equity; deflated Sharpe probability 0.90 with N=10 trials.

## Preregistered gates

| gate | result |
| --- | --- |
| G1_excess | PASS |
| G2_t | PASS |
| G3_years | PASS |
| G4_alpha | **FAIL** |
| G5_dd | PASS |
| G6_turnover | PASS |
| G7_automated | PASS |
| G8_concentration | PASS |
| G9_early | PASS |
| G10_sample | PASS |
| G11_event_study | **FAIL** |
| G12_dsr | PASS |

## Other preregistered cells (MANUAL_USD, 2013-2017)

| cell | n | net CAGR | excess vs EW | NW t | CAPM a | t | FF3 a | t | FF5+MOM a | t | Sharpe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_only | 1205 | 11.86% | 3.36% | 2.16 | -3.80% | -1.61 | -3.19% | -1.41 | -2.64% | -1.24 | 0.98 |
| B_only | 1173 | 17.08% | 7.89% | 6.92 | 0.89% | 0.75 | 1.17% | 1.15 | 0.39% | 0.29 | 1.44 |
| pit_sp1500 | 765 | 16.85% | 7.72% | 7.22 | 0.47% | 0.33 | 1.08% | 0.72 | 0.76% | 0.40 | 1.40 |

Only AB carries gates: the preregistration names one primary hypothesis and lists the rest as diagnostics.
NEW alone has a strongly negative CAPM alpha; INCREASED alone is the better half but its alpha is +0.89% with
t 0.75, far below the G4 requirement of +2% with t >= 1.5.

## Calendar-year excess vs the equal-weight universe (AB, primary)

| year | excess |
| --- | --- |
| 2004 | 6.66% |
| 2005 | 2.60% |
| 2006 | 2.57% |
| 2007 | 0.73% |
| 2008 | 11.21% |
| 2009 | 15.76% |
| 2010 | 4.80% |
| 2011 | 8.42% |
| 2012 | 3.09% |
| 2013 | 5.28% |
| 2014 | 9.13% |
| 2015 | 2.87% |
| 2016 | 4.40% |
| 2017 | 7.97% |

## Concentration (G8) — PASS

best-year share 0.1844 (max 0.5); top-5 events 0.0268 (max 0.25); top ticker 0.0107 (max 0.1); top SIC2 0.1363 (max 0.3).

## Factor loadings (AB, 2013-2017)

CAPM beta 1.06. FF3 loadings {"mkt": 0.98, "smb": 0.277, "hml": 0.08}. FF5+MOM loadings {"mkt": 0.958, "smb": 0.353, "hml": 0.051, "rmw": 0.228, "cma": -0.124, "mom": -0.098}.

Machine-readable: `phase8b_repurchase_portfolios.csv`, `phase8b_repurchase_run_manifest.json`.

