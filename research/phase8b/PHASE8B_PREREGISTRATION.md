# PHASE8B_PREREGISTRATION - repurchase-authorisation announcements (frozen 2026-09-12, before any candidate text was read, any label existed, or any return was computed)

Machine-readable twin: `research/phase8b/phase8b_config.json`. SHA256 of both files, and of every later frozen artefact (labelling guide, candidate CSV, split, classifier code and configuration), is appended to `research/phase8b/PHASE8B_FREEZE_HASHES.jsonl` with a UTC timestamp. Nothing below may change after the first label is read or the first return is computed; a defect forces a documented, hashed rerun with the first run retained. Experiment ID: **E062** (cumulative ledger 488 -> 489; it supersedes the never-run E059 row 487).

## 1. Hypothesis
**Primary:** US common stocks whose issuer discloses, through an SEC 8-K filing, a genuinely NEW share-repurchase authorisation (label A) or an INCREASE / EXPANSION of an existing authorisation (label B) earn positive abnormal returns over the following 252 US trading sessions, measured from the first market open a retail investor could use after EDGAR acceptance, relative to the equal-weight eligible universe and after realistic execution costs.

**Mechanism:** an authorisation is a credible signal of management's undervaluation judgement and of a commitment to return capital (Ikenberry, Lakonishok and Vermaelen 1995; Peyer and Vermaelen 2009 for the post-2000 sample); the long-horizon drift, not the announcement-day jump, is what a next-open retail rule can capture.

**Null:** after the announcement reaction and in the modern market (gate window 2013-2017), a next-open implementation captures nothing beyond market, size, value, profitability, investment and momentum exposure.

**What this is a test of:** post-SEC-disclosure repurchase-announcement drift. It is not a test of the first instant the market heard the news: many authorisations are first published by press release minutes to hours before the 8-K is accepted, and no independently timestamped press-release source exists in this repository. Inferred press-release times are not used.

## 2. Data (all local or free public domain; nothing purchased; nothing from 2018 onward)
| Item | Source | Use |
| --- | --- | --- |
| Candidate 8-K filings, 2004-01-01..2017-12-31 filing dates | EDGAR full-text search (efts.sec.gov), forms 8-K (which includes 8-K/A in the index; amendments are separated by the header) | Stage 1 retrieval |
| Filing text and header | EDGAR full-submission `.txt` per accession (8-K body, EX-99.* exhibits; `<ACCEPTANCE-DATETIME>`, `FILED AS OF DATE`, `CONFORMED SUBMISSION TYPE`, `ITEM INFORMATION`, SIC) | classifier input, causal time, amendment detection, sector |
| CIK -> trading symbol, point in time | SEC insider data sets SUBMISSION tables 2006Q1..2017Q4 (`ISSUERCIK`, `ISSUERTRADINGSYMBOL`, `FILING_DATE`), already on disk | ticker mapping |
| Current CIK -> ticker | `data/metadata/company_tickers.json` (2026-09-12) | fallback only, route counted |
| Prices | EODHD panels through `phase6_eodhd_panel.load_panel` (lock-enforced) plus the Phase 8B guard | universe, execution, returns |
| Benchmarks | Tier 2 EW eligible universe (Phase 6 engine), SPY (EODHD ETF file, lock-enforced) | excess, alpha |
| Factors | French library 202607: FF3, FF5, momentum (monthly) | style diagnostics |
| XBRL companyfacts (4,473 issuers on disk) | `StockRepurchaseProgramAuthorizedAmount1`, `...NumberOfSharesAuthorizedToBeRepurchased`, `dei:EntityCommonStockSharesOutstanding`, read through a loader that drops every fact with `filed >= 2018-01-01` | retrieval-recall audit; shares outstanding for size characterisation |
| Trading calendar | sessions on which SPY has a vendor open, 2004-01-02..2017-12-29, cross-checked against `exchange_calendars` XNYS | execution timing |

**Hard lock (software):** `phase8b_lock.py` raises `Phase8BLockError` if any date >= 2018-01-01 appears in a Phase 8B price, calendar, event, return or benchmark object; the fetcher refuses any accession whose header filing date is >= 2018-01-01; the search index is never queried past 2017-12-31; the companyfacts loader filters at read time. Validation 2018-2021 and holdout 2022-01..2026-08 stay closed under every outcome; promotion produces a request, never an access.

## 3. Stage 1 - candidate retrieval (high recall by design)
Each expression below is queried separately against the EDGAR full-text index (forms `8-K`, one calendar month at a time, paged at 100 with the 10,000-hit ceiling checked and the month split into halves if it is approached). A candidate is an **accession** matched by at least one expression in the target set; the set of matching expressions is recorded per accession.

Target set T (union = candidate pool):
`"repurchase program"`, `"repurchase plan"`, `"share repurchase"`, `"stock repurchase"`, `"repurchase authorization"`, `"repurchase authorisation"`, `"buyback"`, `"buy-back"`, `"buy back"`, `"repurchase of up to"`, `"repurchase up to"`, `"authorized the repurchase"`, `"authorization to repurchase"`, `"authorized to repurchase"`, `"repurchase of its common stock"`, `"repurchase of common stock"`, `"repurchase shares"`, `"repurchase of shares"`, `"purchase of up to"`, `"purchase up to"`, `"repurchase of its shares"`, `"repurchase its shares"`, `"repurchase its common stock"`, `"repurchase common stock"`.

Authorisation-language group AUTH (a subset of T, used only for sampling strata, never for classification): `"repurchase authorization"`, `"repurchase authorisation"`, `"repurchase of up to"`, `"repurchase up to"`, `"authorized the repurchase"`, `"authorization to repurchase"`, `"authorized to repurchase"`, `"purchase of up to"`, `"purchase up to"`.

Audit complement B (retrieval-recall audit only): accessions matched by `"repurchase"`, `"repurchases"`, `"repurchased"`, `"buyback"`, `"buy back"` or `"buy-back"` and by no expression in T.

For every candidate the full submission is fetched once, hashed, and stored under `data/raw/phase8b/filings/<year>/<accession>.json.gz` with the parsed header and the plain text of the 8-K body and every EX-99.* exhibit (HTML stripped; other exhibit types and graphics discarded). Filings whose header form is not `8-K` or `8-K/A` are dropped and counted.

## 4. Candidate identity and event integrity (frozen rules)
1. Unit = accession number. Several matching documents inside one accession are one candidate.
2. `8-K/A` (header `CONFORMED SUBMISSION TYPE`) is never a signal; counted.
3. A candidate whose issuer CIK cannot be mapped to a priced EODHD code (section 7) is kept for classifier work but cannot enter the event set; counted.
4. **Event** = a candidate classified A or B by the frozen classifier. Event time = `<ACCEPTANCE-DATETIME>` of that accession.
5. **Repeated references:** a second A/B classification for the same CIK accepted within 60 calendar days after a prior A/B event is a repeated reference to the same programme (press release re-filed, earnings release repeating the authorisation, proxy/other 8-K restating it); it is merged into the earlier event and counted. Beyond 60 days it is a distinct event (a genuine increase or a new programme within a year is common and is exactly the B case).
6. Routine progress updates, completions, ASR execution notices, expirations, renewals without increase and historical references are labels C-I and never events.
7. Ambiguous candidates (classifier output `UNCLASSIFIED`) are excluded from the primary event set and kept for diagnostics.
8. Stable event identifier: `E8B-<CIK 10 digits>-<accession>`.

## 5. Stage 2 - labels, human ground truth, split, classifier
**Taxonomy (frozen; C-I are non-primary forever):**
- A - NEW repurchase authorisation (a programme, or a self-tender offer for the issuer's own common stock, approved by the board and disclosed for the first time; a "new programme replacing an exhausted/expired one" is A).
- B - INCREASED / EXPANDED authorisation (additional dollars/shares added to, or a larger programme replacing, an existing one that still had capacity).
- C - renewal / extension of term or re-approval without an increase.
- D - routine progress / update on an existing programme (shares bought this quarter, remaining capacity).
- E - historical repurchases completed (past activity described, no authorisation news).
- F - accelerated share repurchase execution / ASR operational update (initiation, settlement, final share count under an existing authorisation).
- G - completed / expired programme.
- H - historical reference only (background mention, risk factor, footnote).
- I - false positive / irrelevant use of repurchase terminology (debt, preferred, units, another company's programme, mutual funds, etc.).
Rule for the labeller: label the most bullish element that is genuinely NEW in this filing; if a filing both reports progress (D) and announces an increase (B), label B. Preferred stock, debt, warrants, units and partnership units are I even when "repurchase" is used. Doubt between A/B and anything else -> the non-primary label, note "AMBIG" in `human_notes`.

**Human labels:** at least 200 candidates, target 240, drawn with seed 20260912 from the candidate pool: 160 from stratum S1 (any AUTH-group match) and 80 from stratum S2 (no AUTH match), each stratum allocated across filing years 2004-2017 in proportion to the stratum's candidate counts with a floor of 5 per year (S1) and 3 per year (S2), one candidate per issuer per year where possible. The labelling package (`phase8b_labeling_candidates.csv`, `phase8b_labeling_guide.md`) shows filing metadata, the extracted passages with 400 characters of context each side, and the full plain text file path; it shows no price, return, chart, market capitalisation or anything dated after the filing. **Claude-generated labels are not ground truth and are not used**; the only labels are those typed by a human into `human_label`.

**Split:** before any label exists, every sampled candidate is assigned to `DEV` (two thirds) or `HOLDOUT` (one third) by stratified random draw within year x stratum (seed 20260912); the assignment is written to `phase8b_label_split.csv` and hashed. Classifier development reads `DEV` labels only. The `HOLDOUT` labels are read exactly once, by the frozen evaluation script, after the classifier code and configuration are hashed.

**Classifier constraints:** deterministic, documented rules (regular expressions, phrase co-occurrence, numeric extraction, 8-K item codes, document type) over the filing text and header; no returns, prices, post-event outcomes, 2018+ information, or human notes; output one of A-I or UNCLASSIFIED; primary positive = A or B. Iteration is confined to DEV; every DEV iteration is logged with its DEV confusion matrix.

**Classifier gate (frozen):** on HOLDOUT, precision of the A-or-B prediction >= 0.90, computed with stratum weights (population count / sampled count per stratum; raw precision reported next to it), with at least 25 predicted A/B positives in HOLDOUT and a Wilson 95% lower bound (raw counts) >= 0.75. Recall, F1, per-class metrics, confusion matrix, support, every false positive and false negative are reported. Recall below 0.30 is investigated and explained, not a stop by itself. Failing the gate -> `CLASSIFIER_VALIDATION_FAILED - STOP E062`; no return is computed.

**Retrieval-recall audit (blind to returns, reported separately from classifier metrics):**
(a) XBRL cross-check: for issuers on disk whose `StockRepurchaseProgramAuthorizedAmount1` (USD) or `...NumberOfSharesAuthorizedToBeRepurchased` increases between consecutive filings with `filed <= 2017-12-31`, the share of increases for which the candidate pool holds an 8-K of that CIK in the 120 calendar days ending on the filing date. Reported with the two known biases (issuers need not file an 8-K; the tag changes for reasons other than a new programme).
(b) Human complement audit: 60 accessions drawn (seed 20260912, across years) from the audit complement B, packaged like the labelling sample in `phase8b_retrieval_audit_candidates.csv`; the share labelled A/B by the human, scaled by the complement size, estimates events the target set misses. Retrieval performance and classifier-conditional performance are always reported as two numbers; total system recall is their product, stated only when both exist.

## 6. Causal event time and execution (frozen; tested)
- Timestamp: `<ACCEPTANCE-DATETIME>` (US Eastern local time, `America/New_York` zone, DST by zone rules).
- Entry session: the first trading session whose open is at least 60 minutes after acceptance: acceptance at or before 08:30:00 ET on a trading day -> that day's open; later on a trading day, or on a weekend/holiday -> the next trading day's open. Trading days = sessions with an SPY vendor open (matches XNYS sessions incl. the 2004-2017 special closures; tested).
- Consistency check: entry date >= `FILED AS OF DATE`; violations are data errors, excluded and counted.
- Exit: the open of the 252nd session after the entry session (primary); 126 (secondary sensitivity only). Series ending earlier: Phase 6 delisting rule. Positions open at the development end close at the last development open (2017-12-29) and book the partial return.
- Sensitivity (red team): one extra session of delay.
- Entries from 2004-01-02 to 2017-12-28; no event dated 2018 or later exists in the pipeline.

## 7. Universe and mapping (frozen)
- Eligibility: Phase 6 Tier 2 LIQ1000 at the last month-end signal date on or before the entry day (identical to Phase 8). Events on ineligible names are excluded and counted. Corroboration subset: PIT S&P 1500 at that signal date (2012-04-30 onward).
- CIK -> EODHD code: (i) the `ISSUERTRADINGSYMBOL` of the issuer's most recent insider SUBMISSION filed on or before the acceptance date and within 400 days (normalised as in Phase 8); (ii) else the earliest SUBMISSION after it within 400 days (route `backfill`, needed for 2004-2005); (iii) else `company_tickers.json` (route `current`). Each candidate code (plain, `_old`, `_old1`, `_old2`) must have an unadjusted close inside the 5 sessions before the entry session; the first priced code wins; otherwise UNMAPPED. Routes counted per year.
- Market capitalisation for characterisation = last month-end close x latest `dei:EntityCommonStockSharesOutstanding` filed before that month-end (2009+); missing -> not characterised.

## 8. Primary portfolio (one construction; frozen)
Calendar-time, long-only, holds every qualifying A/B event: on a session with entries or exits, the portfolio is re-equalised so every active position has weight 1/N (N = active positions after the day's entries and exits), trades priced at that session's adjusted open; on other sessions positions are held (no rebalancing). Fully invested whenever N >= 1; cash earns 0 when N = 0. Costs per side on every traded notional (entries, exits, re-equalisation) per PHASE8_COST_RULES.md: MANUAL_USD 5/5.3 bps (10/10.3 for ranks 501-1000) primary; AUTOMATED 20/20.3 (25/25.3); STRESS 30/31 (45/46). Same issuer with an active position: the new event does not open a second position and does not extend the exit; counted. Monthly returns: first open of month to first open of the next month (Phase 8 convention). Turnover = one-way traded notional / equity, annualised, reported with the share due to re-equalisation.
Operational sensitivity (reported, never primary): Phase 8 slot engine with 20 slots, and EUR 500 / EUR 1,000 simulations (position = capital / 20, EUR 1 minimum order, ECB 1.1652).

## 9. Event study (before any portfolio statistic is read)
For A/B events with an eligible mapped code: open-to-open returns at +5, +21, +63, +126, +252 sessions minus (i) the buy-and-hold return of the EW eligible universe over the same window (members at the event's signal date), (ii) SPY. Descriptive at all horizons; inferential attention at +252 (primary) and +126 (secondary) only. Uncertainty: cluster bootstrap by entry month (1,000 draws, seed 20260912) and, separately, by issuer CIK; both CIs and t statistics reported; the gate uses the weaker of the two. Windows: 2004-2017, 2004-2012, 2013-2017; year by year.

## 10. Benchmarks and alpha
Net monthly returns versus: EW Tier 2 eligible universe (monthly engine with delisting bookings), SPY; CAPM alpha on SPY (HAC 12 lags because holds overlap twelve months); FF3 and FF5 + MOM regressions (HAC 12); exposures reported (beta, SMB, HML, RMW, CMA, MOM). Question asked of the numbers: repurchase information, or repackaged value / dip-buying / profitability / size / beta?

## 11. Development promotion gate (2013-01..2017-12 unless stated; MANUAL_USD; primary portfolio; frozen)
| Gate | Rule |
| --- | --- |
| G1 | mean net excess over the EW eligible universe >= +3 percent a year |
| G2 | Newey-West (12 lags) t of that excess >= 2.0 |
| G3 | calendar-year net excess positive in >= 4 of 5 years 2013-2017 |
| G4 | CAPM alpha vs SPY >= +2 percent a year with HAC t >= 1.5, AND FF5+MOM alpha >= +2 percent a year with HAC t >= 1.0 |
| G5 | maximum drawdown over the full window (first entry..2017-12) not deeper than SPY's over the same months by more than 15 points |
| G6 | one-way turnover <= 300 percent a year |
| G7 | AUTOMATED cost case: 2013-2017 net excess over the EW universe > 0 |
| G8 | concentration: best calendar year <= 50 percent of full-window cumulative net excess; top 5 events <= 25 percent of gross gains; top single ticker <= 10 percent; top 2-digit SIC <= 30 percent |
| G9 | 2004-2012 net excess over the EW universe >= 0 (reported; an early negative with a late positive is allowed only if G1-G4 hold; an early positive cannot rescue a failed G1-G4) |
| G10 | sample size: >= 150 entered A/B events 2013-2017 and >= 300 in 2004-2017 |
| G11 | event study: +252 abnormal return vs the EW buy-and-hold benchmark in 2013-2017 > 0 with both cluster t >= 2.0, and > 0 over 2004-2017 |
| G12 | deflated Sharpe (Bailey and Lopez de Prado) probability >= 0.90 with N = 10 trials (nine Phase 8 trials + E062; variance of the Sharpe ratios across those trials) |
| G13 | red team (section 12): no listed test turns the 2013-2017 net excess or the CAPM alpha negative |
| G14 | classifier gate (section 5) passed before any return was computed |
Multiplicity: exactly one primary hypothesis (A-or-B, 252 sessions, hold-all EW, MANUAL_USD). A-only, B-only, 126 sessions, PIT S&P 1500, 20 slots, other cost cases, +1 delay are diagnostics, never promotable. All gates must pass; no threshold changes after results.

## 12. Red team (run only if the primary passes G1-G12; falsification only, never a redesign)
Dependence on: one year; one ticker; one 2-digit SIC; top 5/10/20 contributors removed; market beta, size, value, profitability, investment, momentum (FF5+MOM); a low-volatility proxy (regression on USMV/SPLV excess where dated, else the French variance decile spread); post-crash years (2009-2010) removed; large caps (top 250 by liquidity rank) versus the rest; authorisation size terciles (dollars / market cap where extractable) - characterisation only; classification errors (rerun on holdout-verified labels only; rerun with predicted-A-only and predicted-B-only); ASR contamination (drop filings mentioning "accelerated share repurchase"); duplicates (drop any event within 120 days of the issuer's previous event); renewals (drop filings mentioning "renew", "extend", "extension"); prior 12-month underperformance versus the universe (terciles); benchmarks EW universe, SPY, RSP, IWM; one extra session of delay; MANUAL, AUTOMATED and STRESS costs; delisting all100/all30; PIT S&P 1500 subset. None of these may be used to define a new candidate.

## 13. Reporting windows
Full causal development history 2004-2017 (all statistics), 2004-2012, and prominently 2013-2017 (the gate window), plus calendar-year tables. A result carried by 2008-2010 does not pass.

## 14. Outputs (all under `research/phase8b/` or `reports/E062_<stamp>/`)
PHASE8B_REPOSITORY_AUDIT.md, PHASE8B_PREREGISTRATION.md, phase8b_config.json, PHASE8B_FREEZE_HASHES.jsonl, PHASE8B_RETRIEVAL_REPORT.md, phase8b_labeling_guide.md, phase8b_labeling_candidates.csv, phase8b_label_split.csv, phase8b_retrieval_audit_candidates.csv, PHASE8B_RETRIEVAL_RECALL_AUDIT.md, PHASE8B_CLASSIFIER_DEVELOPMENT.md, PHASE8B_CLASSIFIER_HOLDOUT.md (with confusion matrix), PHASE8B_EVENT_INTEGRITY.md, PHASE8B_TIMING_AUDIT.md, PHASE8B_EVENT_STUDY.md, PHASE8B_PORTFOLIO.md, PHASE8B_FACTOR_DIAGNOSTICS.md, PHASE8B_RED_TEAM.md, PHASE8B_DECISION.md; ledger rows in EXPERIMENTS.md, PHASE6_EXPERIMENT_REGISTRY.csv, RESEARCH_JOURNAL.md, STATUS.md, PLAN.md. Outputs after the human-label gate exist only once genuine human labels exist.

## Amendment 1 (2026-09-12, before any label existed; the original file hash is retained in PHASE8B_FREEZE_HASHES.jsonl and this amended file is hashed again)
Requested by the user after an independent audit of the labelling package; no label, no classifier rule and no return existed when it was applied.
- **Taxonomy:** label J = SELF-TENDER / DUTCH-AUCTION REPURCHASE OFFER (a newly announced issuer self-tender, fixed-price tender or modified Dutch-auction tender for the issuer's own common stock). J is economically distinct from an authorisation for future open-market or private repurchases and is NOT part of the primary A/B signal; it is never merged into A/B after any result. A filing that clearly contains both a tender and a separate new/increased general authorisation is labelled by that authorisation (A or B); otherwise J. Section 5's "self-tender ... is A" is withdrawn.
- **Human view:** the labelling CSVs carry no current (non-point-in-time) ticker symbol and no other post-filing identifier.
- **Classifier split:** in addition to the one-third HOLDOUT per year x stratum cell, every row of a CIK is placed in the partition of that CIK's first assigned row (no issuer straddles DEVELOPMENT and HOLDOUT). The mapping is `phase8b_classifier_split.csv`, hashed before any label.
- **Retrieval-recall audit (b):** the complement sample is stratified by 8-K items (B1 non-earnings 8.01/7.01 without 2.02: 60 rows; B2 other: 30 rows), year-allocated with floors, one per issuer-year; the estimator and its limits are documented in PHASE8B_RETRIEVAL_AUDIT_DESIGN.md. A positive rate inside an enriched stratum is never reported as overall retrieval recall; recall is computed with stratum weights N_s / n_s.
- **Full-text package:** every `full_text_path` is verified to resolve (phase8b_package_verification.json) and the texts are zipped with the CSVs and the guide.

## 15. Decision labels (exactly one)
`CLASSIFIER_VALIDATION_FAILED - STOP E062`; `REPURCHASE_SIGNAL_REJECTED_IN_DEVELOPMENT`; `REPURCHASE_SIGNAL_RED_TEAM_FAILURE`; `PHASE8B_DEVELOPMENT_SURVIVOR - VALIDATION AUTHORISATION REQUIRED`; or, for non-economic stops, `PHASE8B_DATA_INSUFFICIENT` / `PHASE8B_ENGINEERING_FAILURE` (defect diagnosed and repaired before any economic conclusion). A survivor is frozen (code, classifier, configuration, hashes) and a validation request is written; 2018-2021 is not opened by this program, and 2022-2026 is not opened under any outcome.
