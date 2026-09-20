# PHASE8B_REPOSITORY_AUDIT - state of the repository before any Phase 8B work (2026-09-12)

Scope: inspection only. Nothing was modified before this document was written. Test suite at the start of Phase 8B:
`PYTHONUTF8=1 python -m unittest discover -s tests -v` -> 163 tests, OK (8.1 s).

## 1. Where Phase 8 code lives
Flat modules under `research/` (imported with `research/` as the working directory, as every test does via `sys.path.insert`):

| Module | Role | Reusable for 8B |
| --- | --- | --- |
| `phase8_sec_acquire.py` | hashed download of SEC insider data sets, declared User-Agent, refuses quarters after 2017Q4 | pattern reused (UA, hash log, dev-only assert) |
| `phase8_insider_events.py` | Form 4 row filters, issuer-to-ticker mapping (`ISSUERTRADINGSYMBOL` -> EODHD code with `_old` variants, `company_tickers.json` fallback), issuer-filing-day events | `norm_symbol`, mapping route; the SUBMISSION table is the point-in-time CIK->symbol source for 8B |
| `phase8_insider_backtest.py` | event study with month-cluster bootstrap, buy-and-hold EW-of-members benchmark, SPY, slot portfolio with costs and delisting, monthly stats, Phase 8 gates, BH-FDR, deflated Sharpe | `event_returns`, `bench_bh`, `car_stats`, `simulate_slots` (operational sensitivity only), `window_stats`, `ended_map`, `monthly_from_equity` |
| `phase8_repurchase_fts.py` | EDGAR full-text search scan, fixed 5-phrase query, 8-K, 2009-01..2017-12; 33,388 document hits = 27,367 accessions | superseded by the broad Phase 8B retrieval (section 6) |
| `phase8_xbrl_acquire.py` / `phase8_quality_conditioning.py` / `phase8_sue_falsification.py` | companyfacts per issuer; loaders truncate at `filed <= 2017-12-31` | companyfacts used only for the retrieval-recall audit and for shares outstanding, through a new read-time-locked loader |
| `phase8_redteam.py` | contributor removal, factor regressions | pattern |

Frozen Phase 8 documents: PHASE8_PREREGISTRATION.md (+ .sha256 covering EVENT_RULES, COST_RULES, PROMOTION_GATE, DATA_AUDIT). The E059 entry there (section 5) froze: ">= 200 hand-labelled 8-K filings with precision/recall reported first; long hold 252 days; same gates. Stopped if precision < 0.8." PHASE8_REPURCHASE_CLASSIFIER.md records that E059 stopped at the classifier stage with no return computed.

**Conflict check (task item 13):** the repository already contains an explicitly frozen 252-session holding period for the repurchase cell (PHASE8_PREREGISTRATION.md section 5, hashed 2026-09-12 before any Phase 8 return). It agrees with the Phase 8B rule; no change. The Phase 8 precision stop threshold was 0.80; Phase 8B raises the classifier gate to 0.90 (stricter, fixed before any label exists). Both are reported.

## 2. Canonical universe
`phase6_stock_universe.py`: Tier 2 LIQ1000 (history >= 252 priced days, unadjusted close >= USD 5, 63-day median dollar volume >= USD 1m, top 1000 by that median, no missing close in 21 sessions, no zero-volume day in 5, integrity rules I1-I5), evaluated at month-end signal dates; Tier 1 = PIT S&P 1500 from 2012-04-30 (`PIT_FIRST_SIGNAL`). Phase 8 applied eligibility "at the last month-end signal date on or before the entry day" (`phase8_insider_backtest.prepare_events`). Same rule for 8B. Coverage: survivorship-safe from 1998 (PHASE6_EODHD_COVERAGE_AUDIT.md).

## 3. Canonical cost model
PHASE6_COST_MODEL.md (Trading 212 facts verified 2026-09-09) instantiated for events in PHASE8_COST_RULES.md: MANUAL_USD 5/5.3 bps (10/10.3 for liquidity ranks 501-1000), AUTOMATED 20/20.3 (25/25.3), STRESS 30/31 (45/46); execution at the adjusted open; `COSTS` dict in `phase8_insider_backtest.py`. Reused unchanged.

## 4. Delistings
`phase6_stock_universe.delisting_haircut(info, venue, mode)`: a series that ends inside the hold is closed at the last vendor price; distress proxy (126-day drop <= -50% or last close < USD 1) applies a Shumway haircut of -30% (NYSE/AMEX/ARCA) or -55% (other); sensitivities all100 and all30. `ended_map` in the Phase 8 backtest builds the per-code info. Reused unchanged.

## 5. SEC `acceptanceDateTime`
Phase 8 used FILING_DATE (structured data set field) and entered at the first open strictly after it; the ten-filing hand reconciliation (PHASE8_SEC_DATA_AUDIT.md D7) read `<ACCEPTANCE-DATETIME>` from EDGAR by hand, format `YYYYMMDDHHMMSS` in US Eastern local time. No parser exists in the code base. Verified today on 0001193125-15-054256: the full-submission `.txt` header carries `<ACCEPTANCE-DATETIME>20150219162634`, `FILED AS OF DATE`, `CONFORMED SUBMISSION TYPE`, `ITEM INFORMATION` lines. Phase 8B parses this header (new module, tested) and converts with the America/New_York zone (DST handled by the zone database).

## 6. Existing candidate pool and its limits
`data/raw/phase8/fts/hits_<month>.json.gz`: metadata only (accession:document id, CIKs, display name, file date, 8-K items, description) - no filing text, no acceptance time. Hits are per document (5,552 accessions have 2+ matching documents). The phrase set was narrow (five phrases). Consequence: Phase 8B needs (a) a broader retrieval and (b) the filing text, which must be fetched from EDGAR (free, public domain, pre-2018 filings only). The task statement's assumption that local SEC data suffice does not hold for the text; the fetch is not a data purchase and is logged and hashed like every acquisition in this repository.

## 7. Benchmarks and factor data on disk
- ETFs (EODHD, `data/raw/phase6/eodhd/etf`): SPY, IVV, RSP, IJH, IJR, IWM, MDY, QQQ, USMV, SPLV, QUAL, MTUM, VBR, DVY, HDV, SCHD, SDY, VIG, AGG, BND, IEF, TLT, SHY, TIP, LQD, GLD, DBC, EEM, EFA, CSPX.LSE. Loaded through `phase6_e051_run.load_etf_frames` (lock-enforced).
- French library (`phase6_french.py` FILES, vintage 202607): FF3 daily/monthly, FF5 daily/monthly, momentum factor daily/monthly, short-term reversal, size/value/OP/INV/beta/variance portfolios. `load_ff3()` returns monthly Mkt-RF, SMB, HML, RF. FF5 + MOM loaders exist in `phase6_french.py`.
- Equal-weight eligible universe: monthly from `phase6_stock_engine.equal_weight_benchmark` (with delisting bookings); daily buy-and-hold EW-of-members from `phase8_insider_backtest.bench_bh`.
- No low-volatility or quality factor beyond RMW/CMA (FF5) and the USMV/SPLV/QUAL ETFs (from 2011-2013 only).

## 8. Experiment ledger
Three places: `EXPERIMENTS.md` (prose entries with preregistration and result blocks), `PHASE6_EXPERIMENT_REGISTRY.csv` (one row per cell: experiment, run, trial_id, family, architecture, neighbourhood_cell, data, segment, cumulative_hypotheses, classification; last row 488), and `RESEARCH_JOURNAL.md`. STATUS.md and PLAN.md carry the resume state. E059 is registered as row 487 "NOT RUN". Phase 8B registers its single primary cell as E062 (cumulative 489) and marks E059 as superseded by E062.

## 9. Could existing code access 2018+ data?
| Store | 2018+ content on disk | Read path | Risk |
| --- | --- | --- | --- |
| EODHD panels `data/derived/phase6/eodhd/panel_*.parquet` | yes, through 2026-09-11 (vendor cache) | `phase6_eodhd_panel.load_panel` -> `phase6_lock.enforce` truncates at 2018-01-01; locked segments raise `LockError` without an unlock file | low; a direct `pd.read_parquet` of the cache would bypass the lock. Phase 8B adds a second guard (`phase8b_lock`) that raises on any date >= 2018-01-01 inside every 8B return, price, calendar and event object, and never reads the cache directly. |
| ETF CSVs `data/raw/phase6/eodhd/etf` | yes | `load_etf_frames` truncates at DEV_END | same treatment |
| `data/raw/phase8/companyfacts/*.json.gz` | yes: facts filed through 2023+ are inside the files (checked: AMD file has `filed` 2021-2023) | Phase 8 loaders filter `filed <= 2017-12-31` at read time | Phase 8B uses a dedicated loader that drops `filed >= 2018-01-01` before returning anything and is tested. |
| `data/raw/phase8/fts`, `sec_insider` | no (scan and quarters end 2017-12) | - | none |
| `data/metadata/company_tickers.json` | current (2026-09-12) CIK->ticker map | fallback mapping only | non-PIT symbol names; a wrong current symbol maps to no priced code (checked against prices) or, rarely, to a re-used symbol; route counted and reported |
| SEC EDGAR network | any filing | Phase 8B fetcher refuses accessions whose filing date is >= 2018-01-01 and never queries the search index beyond 2017-12-31 | guard tested |

No defect found in the lock. One engineering note: `phase8_insider_backtest.simulate_slots` is a capped slot portfolio; the Phase 8B primary construction (hold every qualifying event, equal-weight re-equalisation on membership-change days) is new code with its own tests.

## 10. Decision
Reuse: lock, panels, universe, delisting rule, cost cases, event-study statistics, EW/SPY/FF benchmarks, ledger conventions. New: EDGAR text fetcher with header parsing, acceptance-time execution calendar, broad retrieval, dedup/event identity, labelling package, retrieval-recall audit, classifier development/evaluation harness, hold-all portfolio accounting. No economic rule is changed by this audit.
