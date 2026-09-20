# PHASE6_CONCLUSION (EODHD screening stage complete, 2026-09-12) - decision DO_NOT_BUY_NORGATE; stock-level momentum family REJECTED_DECAY

Previous interim conclusion (2026-09-09, stop for data authorisation) is superseded by this document; its content is preserved in RESEARCH_JOURNAL.md and EXPERIMENTS.md.

## 1. What was done (2026-09-11 .. 2026-09-12)

1. Verified both EODHD subscriptions through the API (research/phase6_eodhd.py; token only in the user environment, redacted in every log).
2. Audited the Indices Historical Constituents product against its marketing: S&P 400/600 point-in-time from 2012-04-04; S&P 500 removals only from 2012-04 (one 2008 row); 69 development months of point-in-time S&P 1500. Fundamentals, sector history and symbol-change history are not in the subscription (HTTP 403).
3. Acquired and hashed 50,891 US common-stock EOD histories (active and delisted, every venue), 18,972 splits files, the three constituent histories, SPY and eight index/sector ETF benchmarks (data/raw/phase6/eodhd; manifests in data/metadata/phase6_eodhd_*).
4. Coverage audit (PHASE6_EODHD_COVERAGE_AUDIT.md): delisted histories begin overwhelmingly in 1997-1999, so the preregistered rule fixed the survivorship-safe Tier 2 window at 1998-2017; constituent price coverage 0.95-0.97 (PIT_COVERAGE_GAP); 5-7 percent of constituent spells map to reused tickers (61 remapped to `_old` series, 59 dropped: SURVIVORSHIP_RESIDUAL); known failures present except Blockbuster, with Bear Stearns truncated before its collapse; splits consistent 9/9; vendor placeholder prices and zero split factors found and neutralised by integrity rules I1-I5 after an aborted first attempt.
5. Froze PHASE6_NORGATE_PURCHASE_GATE.md (hash in .sha256; Amendment 1 recorded pre-result for a mis-specified data check, both hashes kept) and the E051 preregistration before any stock-level result.
6. Ran E051: 24 preregistered trials (12 stock-momentum cells, 4 residual-momentum cells, vol-scaled momentum, three Tier 1 replication cells, four sector-ETF cells) with three cost cases and three delisting rules each; then E051-SENS (4 preregistered universe-sensitivity cells) as a red-team diagnostic.

## 2. Result

No trial passes the frozen survivor gates; BH-FDR and deflated Sharpe pass none. The primary cell (12-1 momentum, top-30, monthly, Tier 2 1998-2017) returns 2.2 percent a year net against 5.7 percent for the equal-weight eligible universe and 6.9 percent for SPY, with an 88 percent drawdown; 71 percent of its total return comes from 1999; its 2000-2017 CAGR is -7.4 percent against +5.6 percent for SPY; its net excess over the last 36 development months is -11 percent a year. Every cell, every cost case, every universe cut and the point-in-time S&P 1500 replication agree: the long-only concentrated momentum premium among liquid US stocks is strong in 1998-1999 and zero or negative after costs from 2000 to 2017. This matches the survivorship-free French evidence of E050 (post-2000 t below 1). Sector-ETF momentum underperforms an equal-weight sector basket after costs in all four cells.

Decision by the frozen rule (PHASE6_NORGATE_DECISION.md): **DO_NOT_BUY_NORGATE**. Reason: no Tier 2 stock-level trial passes S1-S6 and M1-M2 (data validity gate D passed under Amendment 1; under the original wording D1 would also have failed, giving the same decision for a different reason).

Classification: stock momentum (A) and residual momentum (B) REJECTED_DECAY at stock level; sector-ETF momentum (F) REJECTED; vol-scaled momentum WEAK diagnostic (t 1.1-1.5, all of it pre-2000); Tier 1 sector-neutral WEAK diagnostic (t 0.88, 67 months, sector labels not point-in-time). No PORTFOLIO_COMPONENT_CANDIDATE. Cumulative hypotheses 426. Validation 2018-2021 and holdout 2022-01..2026-08 never read.

## 3. Why the E050 factor evidence did not translate

The French library showed a large, monotonic, six-decade value-weighted momentum premium that became statistically silent after 2000. A EUR 500-1,000 long-only account cannot harvest the long/short spread, cannot hold the value-weighted decile, and pays about 2 percent a year in base costs at top-30 turnover. What remains for it is the long-only top-N among liquid names in the modern era, and on three separate data cuts that quantity is not positive. The family-level evidence was real; it is not deployable here.

## 4. What remains open in Phase 6 and what the user must decide

- The E050-supported stock-level families are exhausted under the mandate's no-retuning rule. Overlays (trend, volatility cap, low-volatility rank) were preregistered for survivors only; there are none.
- The EODHD subscriptions (USD 49.98 a month) have served their purpose. Their only remaining research use inside the equity data policy is ETF-level or index-level work (for example the SPY trend filter of E050 H6, which is a drawdown overlay, not a return engine). Keeping or cancelling them is the user's decision; nothing in the repository depends on them staying active (all raw snapshots are hashed on disk; the EULA permits retention for personal analysis).
- Genuinely distinct mechanisms not yet tested at stock level need data outside the budget (point-in-time fundamentals for quality/value) or are already excluded by the mandate (short-term reversal, terminated at the family level). Phase 6 stock-level discovery therefore closes at "no qualifying architecture on the available data" (mandate stop condition B for this branch); reopening requires a new mechanism with a preregistered economic rationale and a data source that passes PHASE6_DATA_PROVIDER_AUDIT.md.

## 5. Reproduction

From research/ with PYTHONUTF8=1: `python phase6_eodhd_acquire.py targets|eod|splits` (resumable, sharded), `python phase6_eodhd_panel.py summarize|select|build`, `python phase6_eodhd_audit.py`, `python phase6_eodhd_audit_report.py <audit>`, `python phase6_e051_run.py --t2-start 1998`, `python phase6_e051_report.py <run> <audit>`, `python phase6_e051_sensitivity.py --t2-start 1998`. Tests: `python -m unittest discover -s tests -v` (161).
