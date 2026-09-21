# PHASE8B_REPURCHASE_PREREGISTRATION — E062, as frozen

This is a **consolidated restatement** of what was frozen, written during the 2026-09-21 artifact-recovery audit. It
adds nothing and changes nothing. The authoritative frozen sources, with their ledger hashes, are:

| source | sha256 | frozen (UTC) | stage as recorded |
| --- | --- | --- | --- |
| `PHASE8B_PREREGISTRATION.md` | `7351fe5bdaeb0ac0…` | 2026-09-12T20:35:36 | preregistration (before retrieval text, labels or returns) |
| `phase8b_config.json` | `a13090534760b512…` | 2026-09-12T20:35:36 | preregistration (before retrieval text, labels or returns) |
| `PHASE8B_PREREGISTRATION.md` (Amendment 1) | `902810698345a8a4…` | 2026-09-12T22:53:46 | label J, no ticker hint, CIK-consistent split |
| `PHASE8B_PREREGISTRATION.md` (Amendment 2) | `647f4ba0e60e4bb3…` | 2026-09-20T17:05:05 | 60-case blinded gold protocol |
| `PHASE8B_AMENDMENT3_REPAIR.md` | `a317782500adf625…` | 2026-09-20T18:50:31 | classifier repair path |
| `PHASE8B_DATA_DEFECT_AMENDMENT4.md` | `f76313581aa5…` | 2026-09-20T21:49 | price-path integrity screen |

**Every gate below, including G4 and G11, was frozen on 2026-09-12, eight days before any Phase 8B return existed.**
The first return run was produced 2026-09-20T21:33Z.

## Hypothesis

A new (label A) or increased (label B) issuer share-repurchase authorisation, disclosed by 8-K, earns positive
abnormal return over the following 252 trading sessions. Null: nothing beyond market, size, value, profitability,
investment and momentum exposure in 2013-2017.

## Frozen design

| item | value |
| --- | --- |
| universe | Tier 2 LIQ1000 at the last month-end signal date **strictly before** entry (PIT S&P 1500 corroboration from 2012-04) |
| development window | entries 2004-01-01 .. 2017-12-31; hard lock refuses any date ≥ 2018-01-01 |
| gate window | 2013-01-01 .. 2017-12-31 |
| entry | first open ≥ 60 minutes after EDGAR acceptance (08:30 ET cutoff); weekends/holidays → next session |
| holding period | 252 sessions |
| weighting | equal weight; re-equalised to 1/N only on sessions with an entry or an exit |
| one position rule | an issuer already held opens no second position and gets no extension |
| deduplication | one event per issuer per 60 calendar days; 8-K/A never a signal; UNCLASSIFIED excluded |
| benchmarks | equal-weight eligible universe (primary) **and** SPY |
| costs | MANUAL_USD 5/5.3 bps (10/10.3 far) primary; AUTOMATED 20/20.3 (25/25.3); STRESS 30/31 (45/46) |
| delisting | Phase 6 haircut rule |
| primary cell | **AB = NEW + INCREASED combined** |
| diagnostics (not primaries) | A-only, B-only, 126-session hold, PIT S&P 1500 subset, 20 slots, +1 session delay, other cost cases |
| multiplicity | deflated Sharpe with **N = 10 trials** (nine Phase 8 trials + E062) |

## Promotion gates (verbatim thresholds from the frozen config)

| gate | requirement |
| --- | --- |
| G1 | excess vs EW ≥ +3%/yr |
| G2 | Newey-West t ≥ 2.0 |
| G3 | ≥ 4 of 5 years positive |
| **G4** | **CAPM alpha vs SPY ≥ +2%/yr with HAC t ≥ 1.5, AND FF5+MOM alpha ≥ +2%/yr with HAC t ≥ 1.0** |
| G5 | max drawdown not deeper than SPY's by more than 15 points |
| G6 | one-way turnover ≤ 300%/yr |
| G7 | AUTOMATED-cost excess > 0 |
| G8 | best year ≤ 50% of excess; top-5 events ≤ 25%; top ticker ≤ 10%; top SIC2 ≤ 30% |
| G9 | 2004-2012 excess ≥ 0 (or G1+G2 carry the late window) |
| G10 | ≥ 150 events in 2013-2017 and ≥ 300 total |
| **G11** | **+252 abnormal return vs the EW buy-and-hold benchmark in 2013-2017 > 0 with both cluster t ≥ 2.0, and > 0 over 2004-2017** |
| G12 | deflated Sharpe probability ≥ 0.90 with N = 10 |
| G13 | red team: no listed test turns the 2013-2017 net excess or the CAPM alpha negative |
| G14 | classifier gate (Amendment 3: 15/15 on the fresh blind set) |

All of G1-G12 must pass for promotion. G4 and G11 are quoted verbatim above because they are the two that failed.

## Decision labels (frozen)

`CLASSIFIER_VALIDATION_FAILED - STOP E062` · `REPURCHASE_SIGNAL_REJECTED_IN_DEVELOPMENT` ·
`REPURCHASE_SIGNAL_RED_TEAM_FAILURE` · `PHASE8B_DEVELOPMENT_SURVIVOR - VALIDATION AUTHORISATION REQUIRED` ·
`PHASE8B_DATA_INSUFFICIENT` · `PHASE8B_ENGINEERING_FAILURE`

Validation 2018-2021 and holdout 2022-2026 are not opened under any outcome.
