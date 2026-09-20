# PHASE8_PREREGISTRATION - SEC EDGAR event-driven alpha, insider open-market purchases (frozen 2026-09-12 before any event return was computed)

Hash of this file is recorded in PHASE8_PREREGISTRATION.sha256 together with the hashes of PHASE8_EVENT_RULES.md, PHASE8_COST_RULES.md, PHASE8_PROMOTION_GATE.md and PHASE8_DATA_AUDIT.md. No threshold, filter or definition may change after the first event return is computed; a defect forces a documented rerun with the first run retained.

## 1. Core question
Can causally observable insider open-market purchases (Form 4, transaction code P) generate a practical LONG-ONLY strategy with positive net excess returns in the modern market (2013-2017 development window as the gate), after realistic retail execution costs, without a short leg, for a EUR 500-1,000 Trading 212 account?

## 2. Economic mechanism and expected direction
Insiders buying with their own money in the open market reveal private information or a credible undervaluation judgement; the literature finds purchases (not sales) informative, the effect larger for clusters of insiders, for opportunistic (non-routine) trades, and for smaller firms, with a short-horizon reaction and a debated longer drift. Direction: LONG the purchased stock after the filing. The null hypothesis is that after the announcement reaction, costs and the modern efficiency of the market, a next-day-open retail implementation captures nothing.

## 3. Data (all free, hashed)
SEC Insider Transactions Data Sets 2006Q1..2017Q4; EODHD price panels already on disk (development through 2017-12-29, lock-enforced); PIT S&P 1500 lists from 2012-04; French factors for risk diagnostics; SEC company_tickers.json (current mapping, fallback only). No 2018+ SEC file is downloaded until validation is authorised.

## 4. Rules frozen in companion documents
- PHASE8_EVENT_RULES.md: timestamp = FILING_DATE; entry at the first open strictly after FILING_DATE; primary hold 126 trading days (sensitivities 63, 252, one extra day of delay); row filter (original Form 4, code P acquired, common equity, price within 20 percent of the close, value >= USD 10,000, no swaps); duplicates; ticker mapping; event = issuer-filing-day; five cells C1 ANY, C2 CLUSTER (>= 2 owners in 30 days), C3 OPPORTUNISTIC (Cohen-Malloy-Pomorski adapted, 3-year burn-in), C4 OFFICER, C5 DIRECTOR_ONLY; diagnostics timely/late, size, direct/indirect; Tier 2 eligibility at the last month-end; PIT S&P 1500 corroboration.
- PHASE8_COST_RULES.md: MANUAL_USD primary (5/5.3 bps, 10/10.3 for ranks 501-1000), AUTOMATED (20/20.3, 25/25.3), STRESS (30/31, 45/46); 20 equal slots (10, 40 sensitivities); delisting rule as Phase 6; small-capital simulation at EUR 500 and 1,000.
- PHASE8_PROMOTION_GATE.md: G1-G10 on 2013-2017 (excess >= +3 percent a year, HAC t >= 2, 4 of 5 years, alpha vs SPY t >= 1.5, drawdown, turnover, AUTOMATED positive, concentration, early window, sample size); BH-FDR across five cells; deflated Sharpe with N = 9.
- PHASE8_DATA_AUDIT.md: D1-D9 including a ten-filing hand reconciliation against EDGAR before any return.

## 5. Experiments and trial count (cumulative ledger 479 -> 488)
- E058 insider purchases: five strategy cells (480-484). Event study horizons +5/+21/+63/+126/+252 (descriptive, dependence-aware CIs by month-cluster bootstrap), benchmarks EW eligible universe and SPY, FF3 diagnostics.
- E060 quality conditioning (only after E058 is concluded; two cells, 485-486): C1 events restricted to issuers with XBRL operating profitability (OperatingIncomeLoss / Assets, latest 10-K or 10-Q FILED before the entry date) above the eligible-universe median, and to issuers with no net share issuance (dei EntityCommonStockSharesOutstanding not up by more than 5 percent over the prior four quarters of filings). Data: SEC companyfacts API per issuer CIK, filed dates as timestamps.
- E059 repurchase announcements (one cell, 487): only after E058; classifier validated on >= 200 hand-labelled 8-K filings with precision/recall reported first; long hold 252 days; same gates. Stopped if precision < 0.8.
- E061 earnings falsification (one cell, 488): SUE from XBRL EPS (seasonal random walk, filed dates), 8-K item 2.02 timing, top decile long-only 63-day hold; expected to fail (Martineau 2022).

## 6. Outputs
PHASE8_SEC_DATA_AUDIT.md, PHASE8_INSIDER_EVENT_STUDY.md, PHASE8_INSIDER_PORTFOLIOS.csv, PHASE8_INSIDER_RESULTS.md, PHASE8_COST_ANALYSIS.md, PHASE8_SMALL_CAPITAL.md, PHASE8_RED_TEAM.md, PHASE8_VALIDATION_DECISION.md; conditional PHASE8_QUALITY_CONDITIONING.md, PHASE8_REPURCHASE_CLASSIFIER.md, PHASE8_REPURCHASE_RESULTS.md; ledgers and STATUS/PLAN/EXPERIMENTS/RESEARCH_JOURNAL.

## 7. Locks
Validation 2018-2021 and holdout 2022-01..2026-08 are not read under any development outcome. Promotion produces a request, never an access.
