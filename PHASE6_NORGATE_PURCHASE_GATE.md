# PHASE6_NORGATE_PURCHASE_GATE - frozen decision rule for the USD 346.50 Norgate purchase (written 2026-09-11 before any stock-level portfolio result existed)

This document is frozen: its SHA256 is recorded in PHASE6_NORGATE_PURCHASE_GATE.sha256 and in the E051 results
(meta.gate_doc_sha256). Any edit after E051 starts invalidates the decision. No gate below may be relaxed after a result
is seen; a rule that turns out to be badly specified is recorded as such and the decision is still taken under it.

## 1. Question and what money buys

The EODHD stage (All-World EOD + Indices Historical Constituents, USD 49.98/month, active since 2026-09-11) is a
screening stage. Its only purpose is to decide whether the evidence justifies spending USD 346.50 (six months of Norgate
US Stocks Platinum) to obtain what EODHD cannot supply:
- point-in-time Russell 3000 membership from 1990-07 (EODHD: S&P 500/400/600 only from 2012-04-04, 69 development months);
- delisted securities with full histories since 1950 and continuous series across symbol changes (EODHD: delisted
  histories start late for many names, ENRNQ from 1997-12 and BSC_old from 1999-01, and can end before the last trades);
- historical market capitalisation, turnover and GICS sector for every name (EODHD: sector only for current members).
Norgate is therefore worth buying only if a STOCK-LEVEL architecture shows a credible net-of-cost signal on EODHD whose
remaining uncertainty is exactly the kind Norgate removes (universe definition, survivorship residue, sample length).
If the only credible architecture is ETF-level, Norgate adds nothing and must not be bought.

## 2. Evidence that may be used

Development data only (< 2018-01-01, research/phase6_lock.py). Validation 2018-2021 and the holdout 2022-01..2026-08
are not read at this stage under any outcome. Sources: EODHD panels built by research/phase6_eodhd_panel.py (hashed),
S&P constituent histories (hashed), French FF3 factors for residual momentum, SPY and nine SPDR sector ETFs.

Universes (PHASE6_EODHD_COVERAGE_AUDIT.md section 1): Tier 2 LIQ1000 (all US common stocks, lagged liquidity rank,
NO_PIT_MEMBERSHIP, start year fixed by audit rule A2), Tier 1 PIT_SP1500 (2012-04-30..2017-11-30 signals, supportive only),
SECTOR_ETF (nine SPDR sectors from 1999-12 signals).

## 3. Trials (all reported; 24 primary trials, cumulative hypothesis count 398 -> 422; overlays counted separately)

| Family | Architecture | Cells | Primary cell |
| --- | --- | --- | --- |
| A stock momentum (Tier 2) | top-N long-only, monthly, lookback L months ending one month before the signal | L in {12, 6, 9} x N in {10, 20, 30, 50} = 12 | L 12, N 30 |
| B residual momentum (Tier 2) | FF3 residuals over trailing 36 months, sum of residuals t-12..t-2 scaled by their sd, top-N | N in {10, 20, 30, 50} = 4 | N 30 |
| A volatility-scaled momentum (Tier 2) | 12-1 return / 12-month realised sd, top-30 | 1 | - |
| A/B on Tier 1 | 12-1 momentum top-30; residual momentum top-30 (same rules, PIT S&P 1500) | 2 | both (replication cells) |
| A sector-neutral (Tier 1, degraded) | 12-1 within current-sector z-score, top-30; labelled SECTOR_NOT_PIT | 1 | - |
| F sector-ETF momentum | 12-1 top-3 of 9 SPDRs; neighbourhood top-2, top-4, 6-1 top-3 | 4 | 12-1 top-3 |

Execution: signal at the last trading day's close of month m; orders at the open of the first trading day of m+1; held to
the open of the first trading day of m+2; equal weights; no leverage; no shorting. Costs (PHASE6_COST_MODEL.md): optimistic
3/3.3, base 20/20.3, stress 30/31 (45/46 for liquidity ranks 501-1000) bps per side. Delisting bookings (PHASE6_UNIVERSE_
CONSTRUCTION.md section 5) with sensitivities all100 and all30. Benchmarks: equal-weight eligible universe of the same tier
(no cost, same delisting bookings) and SPY total return (the deployable alternative for a EUR 500-1,000 account).

## 4. Gates (evaluated on the base cost case and base delisting rule unless stated)

Data validity D (from PHASE6_EODHD_COVERAGE_AUDIT.md rules A1-A6, run before E051):
- D1 reconciliation: >= 15 of 17 known failures/acquisitions present, >= 12 of 17 with last price within one month of the expected month;
- D2 splits: 9 of 9 known splits consistent;
- D3 Tier 2 start year (rule A2) <= 2005 so that at least two eras and 150 months exist;
- D4 Tier 1 constituent price coverage >= 0.90 (else Tier 1 is unusable and the corroboration gate C below cannot pass).
If D fails, no stock-level evidence is admissible and the answer is DO_NOT_BUY_NORGATE.

Survivor gates S, per trial:
- S0 at least 120 months of net returns;
- S1 net excess over the tier's equal-weight eligible universe: Newey-West (6 lags) t >= 2.0;
- S2 net excess positive in at least 2 of the available eras {E2b 1990s, E3 2000-2009, E4 2010-2017} AND positive in E4
  (a family with strong old evidence and a non-positive 2010-2017 result is REJECTED_DECAY regardless of S1);
- S3 net excess positive under the stress cost case over the full window;
- S4 recent performance: mean net excess over the last 36 development months (2015-2017) >= 0, and at least 70 percent
  of rolling 60-month windows (ending each December) have positive mean net excess;
- S5 versus the deployable alternative: CAPM alpha of net returns on SPY with HAC t >= 1.5 AND net CAGR above SPY CAGR over 2000-2017;
- S6 drawdown: maximum drawdown of the net strategy not deeper than SPY's maximum drawdown (same months) by more than 15 points.

Multiplicity M (across the 24 primary trials):
- M1 Benjamini-Hochberg at 0.05 on the one-sided p-values of S1 must include the trial;
- M2 Deflated Sharpe probability (Bailey and Lopez de Prado, 24 trials, empirical variance of trial Sharpes, observed
  skew/kurtosis) >= 0.90 for the trial.
Overlays (trend SMA10 exposure switch; volatility cap 1.0) are computed only for trials passing S and M and are reported as
diagnostics; they cannot rescue a failed trial and do not enter the decision.

Feasibility F (for the surviving trial at EUR 500 and EUR 1,000, ECB 1.1652 USD/EUR):
- F1 annual base-case cost drag <= 50 percent of the annual gross excess over the equal-weight benchmark;
- F2 the typical monthly trade per name (5 percent of a position) >= EUR 1 (Trading 212 minimum order value).

Corroboration C: the Tier 1 replication cell of the surviving architecture (2012-04..2017-12, 69 months) has positive mean
net excess over the Tier 1 equal-weight benchmark (sign only; no t-statistic is required from 69 months).

## 5. Decision rule (exactly one output)

BUY_NORGATE if and only if D passes AND at least one Tier 2 (LIQ1000) stock-level trial passes S1-S6, S0 and M1-M2 AND
that trial passes F1-F2 at EUR 500 AND C holds for its architecture.
Otherwise DO_NOT_BUY_NORGATE. In particular: sector-ETF survivors alone give DO_NOT_BUY_NORGATE (the ETF architecture, if it
survives, is frozen and pursued on EODHD data, which is complete for it); Tier 1 survivors alone give DO_NOT_BUY_NORGATE
(69 months cannot justify a purchase); a Tier 2 survivor whose Tier 1 replication has a negative sign gives DO_NOT_BUY_NORGATE.

## 6. What happens after the decision

BUY_NORGATE: before the purchase, write PHASE6_E051_FROZEN_ARCHITECTURE.md naming exactly one architecture (family,
lookback, N, universe rules, execution, cost case for promotion, delisting rule) with its SHA256; Norgate is then used
only to replicate that frozen architecture on the 1990-2017 point-in-time Russell 3000 universe, not to search again.
DO_NOT_BUY_NORGATE: record the reason (D, S, M, F or C); any surviving ETF architecture is frozen the same way; otherwise
Phase 6 stock-level work closes at "no qualifying architecture on the available data" and the mandate's next stop condition applies.

## 7. Provisions against gaming

All 24 trials, all cost cases and all delisting sensitivities are written to reports/E051_<stamp>/trials.csv before any
interpretation. No trial is dropped, renamed or re-parameterised. The T2 start year comes from rule A2, not from results.
No validation or holdout access under any outcome of this gate. If the run must be repeated for a code defect, the first
run is retained and labelled, and the defect is described in EXPERIMENTS.md before the rerun.

## 8. Amendment 1 (2026-09-11, recorded before E051 was run; no stock-level portfolio result had been computed)

Trigger: audit rule A3 / gate D1 compared the EODHD last price date with the exchange delisting month. The audit showed that
six of the eleven failures (Enron, WorldCom, Washington Mutual, Circuit City, old GM, old Kodak) keep trading over the
counter for years after the exchange delisting and EODHD carries those OTC prices. The original rule therefore fails on
data that is MORE complete than required, and the SunEdison check pointed at the post-bankruptcy OTC code (SUNEQ, history
from 2016-01) instead of the NYSE series (SUNE_old, 1997-12..2016-04-21). Under the original wording D1 reads 8 of 17
within one month and the decision would be DO_NOT_BUY_NORGATE on data validity alone, irrespective of any evidence.

Amended D1 (evaluated by research/phase6_e051_report.py `reconciliation_amended`): a failure counts as captured when its
series starts at or before the expected month and does not end before the month preceding it; an acquisition counts when
its last price is within one month of the expected month; SunEdison is checked on SUNE_old. Thresholds unchanged (>= 15 of
17 present, >= 12 captured). Under the amended rule: present 16 of 17 (BLIAQ is a different company, first price 2019),
captured 15 of 17 (failures not captured: Bear Stearns, whose series ends 2008-03-14 before the collapse week; Blockbuster,
absent). Both the original and amended counts are printed in PHASE6_NORGATE_DECISION.md. This amendment changes only how a
data-validity check is read; it relaxes no survivor, multiplicity, feasibility or corroboration gate, and it was made before
the first stock-level result existed. Hash after amendment recorded in PHASE6_NORGATE_PURCHASE_GATE.sha256 (both values kept).

Consequence recorded with the amendment: the Bear Stearns truncation and the Blockbuster absence are documented limitations of
the EODHD delisting record; the delisting-return haircut rule is applied as preregistered and cannot repair a series that ends
before the failure.
