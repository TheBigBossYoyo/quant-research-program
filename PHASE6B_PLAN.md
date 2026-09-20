# PHASE6B_PLAN - modern-evidence screen of economically distinct families on the existing EODHD subscriptions (opened 2026-09-12)

## 0. Inherited state (not reopened)

E051 (24 trials) and E051-SENS (4 cells) rejected stock-level 12-1/6-1/9-1 momentum, residual momentum, vol-scaled momentum and sector-ETF cross-sectional momentum on 1998-2017; decision DO_NOT_BUY_NORGATE accepted. These families stay closed unless genuinely new information appears. Cumulative hypotheses 426. Crypto closed. Locks unchanged: development < 2018-01-01; validation 2018-2021 unopened; holdout 2022-01..2026-08 untouched.

## 1. Objective (restated from the user, 2026-09-12)

Find a currently relevant, low-turnover, long-only systematic strategy with plausible net profitability through Trading 212 Invest for EUR 500-1,000, using the data already paid for. Historical full-sample significance is not the objective; a family must show its effect in 2000-2017 and preferably in 2010-2017 development data before deep testing. Ranking of every candidate: (1) 2000-2017 net CAGR and net excess versus SPY, (2) rolling five-year stability and the last 36 development months, (3) realistic costs (PHASE6_COST_MODEL.md, base case 20 bps per side incl. FX; ETFs same), (4) drawdown versus SPY, (5) deployability (trades per year, UCITS availability, minimum order size).

## 2. Data actually available (verified 2026-09-12)

| Source | Available | Not available |
| --- | --- | --- |
| EODHD All-World | stock/ETF EOD (adjusted and unadjusted), splits, dividends with ex/record/payment dates (verified JNJ 2010), US ETFs back to 1993-2007 (SPY, QQQ, IWM, EFA, EEM, IEF, TLT, SHY, AGG, LQD, TIP, GLD, VNQ, DBC, DVY, SDY, VIG, VTV, VBR) | fundamentals (403), earnings calendar (403), symbol-change history (403), exchange details (403) |
| EODHD constituents | S&P 500/400/600 point-in-time from 2012-04-04 | pre-2012 membership |
| French library (free, survivorship-free) | D/P, E/P, BE/ME, OP, INV, AC, NI, BETA, VAR, RESVAR, long-term reversal 60-13, industries, factors (CRSP vintage 202607) | stock-level anything |

Consequences: quality/profitability, value on accounting ratios, accruals, net issuance and earnings-announcement effects can be screened only at the family level; if such a family passes the modern-evidence gate, the specific paid dataset that would unlock it (EODHD Fundamentals, USD 59.99/month, with filing dates) is reported under stop condition 3, not bought. Dividend yield is the one value-type signal computable causally from the price plan (trailing 12-month ex-dividend cash / price). Volatility, beta, downside risk and long-term reversal are computable from prices. ETF allocation architectures are computable from 2003-2004.

## 3. Modern-evidence gate ME (fixed before any Phase 6B result)

A family earns stock-level or portfolio-level compute only if, on the survivorship-free French value-weighted long-only bucket (or on the relevant ETF-level series), over 2000-01..2017-12:
- ME1 the long-only bucket's excess over the market has Newey-West (6) t >= 1.0 (a screening bar, not a promotion bar);
- ME2 the 2010-01..2017-12 mean excess is >= 0;
- ME3 the direction is economically motivated and stated before the run (no sign flipping after the fact);
- ME4 an implementation exists with one-way turnover <= 100 percent per year (quarterly or slower rebalance, or a rank signal that changes slowly), so that base costs stay below about 0.5 percent per year.
Families failing ME are recorded and closed for this phase. Passing ME is not evidence of a strategy; it only buys compute.

## 4. Preregistered experiments

E052 (family level, French, 1963-07..2017-12 with the 2000-2017 and 2010-2017 sub-windows as the decision windows; value-weighted; long-only bucket minus market; L/S spread reported for information):
| Trial | Family | Long-only bucket | Direction |
| --- | --- | --- | --- |
| F1 | dividend yield (value proxy computable from prices) | Hi 30 by D/P (positive-dividend firms); zero-dividend bucket reported | high yield outperforms |
| F2 | long-term reversal 60-13 | D1 (past losers over months t-60..t-13) | losers outperform |
| F3 | low beta | Lo 20 by pre-ranking beta | low beta earns near-market return with lower risk; long-only excess >= 0 required |
| F4 | low variance / low residual variance (E050 H3/H4 re-read on the modern windows only; no new trial) | Lo 20 | same |
| F5 | operating profitability (reference for a fundamentals purchase) | Hi 30 by OP | high profitability outperforms |
| F6 | book-to-market (reference) | Hi 30 by BE/ME | value outperforms |
| F7 | investment (reference) | Lo 30 by asset growth | conservative outperforms |
| F8 | accruals (reference) | Lo 30 | low accruals outperform |
| F9 | net share issuance (reference) | Lo 30 / repurchasers | low issuance outperforms |
F1-F3 can be implemented on EODHD; F5-F9 cannot without fundamentals. 9 trials (cumulative 426 -> 435). Statistics: HAC t, 2000-2017 and 2010-2017 means, rolling 60-month positive share, max drawdown of the bucket versus the market.

E053 (ETF allocation architectures on EODHD, monthly signals at the month-end close, trades at the next open, 2004-01..2017-12 where every leg exists; base cost 20 bps per side; benchmarks SPY and a 60/40 SPY/AGG quarterly-rebalanced mix). Architectures, each stated with its economic rationale:
| Trial | Architecture | Rationale | Cells |
| --- | --- | --- | --- |
| G1 | absolute (time-series) momentum: SPY if its trailing 12-month total return exceeds the 12-month T-bill return, else IEF | defensive trend following on the equity risk premium; avoids prolonged bear markets | 12-month primary; 10-month SMA switch as the neighbourhood (2 cells) |
| G2 | dual momentum (Antonacci): among SPY and EFA pick the higher trailing 12-month return, hold it only if it beats T-bills, else AGG | as G1 plus a US/international relative choice | 1 cell |
| G3 | volatility-managed equity with a bond sleeve: SPY weight = min(1, target / trailing 63-day realised vol), remainder IEF; target = expanding median of realised vol | risk parity between equity risk and duration; scales down before crashes | 1 cell |
| G4 | static defensive mix SPY 60 / IEF 30 / GLD 10 rebalanced quarterly | diversification baseline with no signal; needed to judge whether G1-G3 add anything | 1 cell |
| G5 | regime-conditioned sector allocation: when SPY is above its 10-month SMA hold SPY, otherwise hold an equal mix of XLP/XLV/XLU | defensive sectors carry lower beta and dividend support in downturns; distinct from cross-sectional momentum | 1 cell |
6 cells (cumulative 435 -> 441). Gates for RESEARCH-level interest (not promotion): 2004-2017 net CAGR >= SPY net CAGR minus 1 point AND max drawdown at least 15 points shallower than SPY AND 2010-2017 net CAGR >= 0.7 x SPY 2010-2017 CAGR AND one-way turnover <= 200 percent per year. Multiplicity: BH-FDR across the six cells on the CAPM alpha versus SPY.

E054 (conditional, stock level on EODHD Tier 2 with quarterly rebalance, only for families passing ME): low-beta / low-volatility top-N and dividend-yield top-N with N in {30, 50}; long-term reversal top-N if F2 passes. Preregistered separately before running, with the same survivor gates as E051 (S0-S6 adapted to quarterly turnover) and the E051 cost/delisting cases.

## 5. Stop conditions for Phase 6B

1. A candidate passes the E054 survivor gates (or an E053 architecture passes its gates with a deployable UCITS implementation) -> freeze, red team, PHASE6B_CONCLUSION.md, then stop for controlled validation authorisation.
2. All ME-passing families and all E053 architectures are rejected -> PHASE6B_CONCLUSION.md "EODHD opportunity set exhausted".
3. A family passes ME only at the family level and needs fundamentals -> PHASE6B_CONCLUSION.md names the dataset and the hypothesis; nothing is bought.

## 6. Ledger and locks

PHASE6_EXPERIMENT_REGISTRY.csv continues from 426. No random splits. No validation or holdout access. UCITS deployability is a reporting item (Trading 212 lists UCITS equivalents such as VUSA/CSPX for SPY; a US ETF cannot be bought by a UK/EU retail client), not a modelling change: signals are estimated on the US ETF with the longer history and the cost case is the same.
