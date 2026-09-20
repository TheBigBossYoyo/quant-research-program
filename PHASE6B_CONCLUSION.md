# PHASE6B_CONCLUSION - modern-evidence screen of distinct families on the existing EODHD subscriptions (2026-09-12)

Stop condition reached: **2 - the currently accessible EODHD opportunity set has been responsibly exhausted for return-premium strategies**, with a documented note under condition 3 (fundamentals) that does not justify a purchase for this account size. No candidate is promoted to controlled validation. E051's null result is untouched (PHASE6_CONCLUSION.md); DO_NOT_BUY_NORGATE stands.

## 1. What was run (all preregistered in EXPERIMENTS.md before results; development data only; holdout untouched)

| Experiment | Question | Cells | Outcome |
| --- | --- | --- | --- |
| E052 (French library, survivorship-free, VW long-only bucket minus market, decision windows 2000-2017 and 2010-2017) | which economically distinct families still show a modern long-only excess | 10 (F1 dividend yield, F2 long-term reversal, F3 low beta, F4a/b low variance, F5 profitability, F6 value, F7 investment, F8 accruals, F9 net issuance) | every price-computable family (F1-F4) has a NEGATIVE 2010-2017 excess; only fundamentals-based F5/F7/F9 pass the (low) ME screen, with +0.26 / +0.47 / +0.28 percent a year in 2010-2017 |
| E052b (live factor ETFs vs SPY, buy-and-hold, own histories to 2017) | deployable proxies of the same families | 11 diagnostic cells | dividend and value ETFs track SPY (excess -0.4 to +0.6 pts CAGR); USMV/SPLV: CAGR 0.5-1 pt below SPY with beta 0.6-0.7 (risk reduction, not return); MTUM +4 pts over 53 months (closed family, reference only) |
| E053 (ETF allocation on EODHD, 2004-2017, next-open execution, 20 bps per side) | regime-conditioned and defensive allocations | 6 (absolute momentum SPY/IEF, SMA10 SPY/IEF, dual momentum SPY/EFA/AGG, vol-managed SPY/IEF, static 60/30/10, defensive-sector regime) | four pass the research-interest gate (G1a, G3, G4, G5); all four have LOWER CAGR than SPY in 2010-2017 and negative excess in 2015-2017; BH-FDR passes only the static 60/30/10 mix (alpha t 2.83), which is diversification, not a signal |
| E053-RT (red team of E053) | long history 1994-2017 with a cash leg, neighbourhood, one-month delay, stress costs, start-year table | diagnostics | absolute momentum and SMA10 replicate the drawdown benefit over 24 years (alpha t 1.9, drawdown -17 vs -51 percent) but beat SPY in only 4-5 of 24 calendar years; every start year from 2009 onward underperforms SPY by 1.5-5 points a year; the 9-month lookback loses 2 points versus 12 (fragile); vol-managed with cash (no bond rally) underperforms SPY (7.4 vs 8.6) |
| E053b (multi-asset defensive trend, GTAA 5 and 8 sleeves, 2006-2017) | diversified time-series trend | 2 | rejected: CAGR 5.3-5.8 vs SPY 8.1; 2010-2017 4-5 vs 14.4 |

Cumulative hypotheses/cells: 455 (398 + E051 24 + E051-SENS 4 + E052 10 + E053 6 + E052b 11 + E053b 2).

## 2. Ranking of every candidate on the user's criteria (development, base costs)

| Rank | Candidate | Window | Net CAGR vs SPY | 2010-2017 CAGR vs SPY | Last 36 months excess | Max DD vs SPY | Alpha t vs SPY | One-way turnover | Deployable form | Classification |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | G3 vol-managed SPY with IEF remainder (63-day RV, expanding-median target, cap 1) | 2007-2017 | 9.3 vs 8.0 | 12.5 vs 14.4 | -2.0 pts | -17 vs -51 | 2.01 | 0.7x/yr | CSPX/VUSA + IBTM-type UCITS Treasury ETF, monthly | RISK_OVERLAY (WEAK_SIGNAL); loses to SPY from any start >= 2009; needs the 2008-2017 bond rally (cash version 7.4 vs 8.6) |
| 2 | G1a absolute momentum: SPY if 12-month return beats T-bills, else IEF | 2005-2017 (1994-2017 with cash) | 9.4 vs 8.6 (10.5 vs 9.4) | 11.1 vs 14.4 | -5.7 pts | -17 vs -51 | 1.22 (1.92) | 0.7x/yr | same | RISK_OVERLAY (WEAK_SIGNAL); beats SPY in 4 of 24 years; the benefit is 2000-2002 and 2008 |
| 3 | G5 SPY above SMA10 else XLP/XLV/XLU | 2004-2017 | 8.9 vs 8.9 | 12.3 vs 14.4 | -1.7 pts | -35 vs -51 | 1.47 | 1.0x/yr | UCITS sector ETFs exist (thin) | RISK_OVERLAY (weaker) |
| 4 | G4 static SPY 60 / IEF 30 / GLD 10, quarterly | 2004-2017 | 7.9 vs 8.6 | 10.4 vs 14.4 | -4.9 pts | -29 vs -51 | 2.83 (BH pass) | 0.1x/yr | three UCITS ETFs | DIVERSIFICATION_BASELINE, not a strategy |
| 5 | USMV / SPLV low-volatility ETFs | 2011-2017 | 14.7 / 13.3 vs 15.7 / 13.8 | same | 0 / -1 pts | -5 vs -8 / -12 | 1.9 / 2.4 | buy-and-hold | UCITS min-vol ETFs (MVOL etc.) | RISK_REDUCTION, no excess return |
| 6 | Dividend / value ETFs (DVY, SDY, VIG, HDV, SCHD, VTV, VBR) | 2004-2017 | -0.9 to +1.0 pts | -1.2 to +0.7 pts | -1.9 to +0.5 | mixed | -0.05 to 1.59 | buy-and-hold | UCITS equivalents exist | NO_EXCESS |
| 7 | G1b SMA10 SPY/IEF, G2 dual momentum, GTAA 5/8 | 2004-2017 | 10.0 / 8.2 / 5.3-5.8 vs 8.1-8.9 | 9.1 / 7.4 / 4-5 vs 14.4 | -5 to -10 | -18 / -19 / -10 | 1.73 / 0.88 / 1.4-2.0 | 1-1.4x/yr | - | REJECTED (2010-2017 gate) |
| 8 | Stock-level families (E052 F1-F4: dividend yield, long-term reversal, low beta, low variance) | family level 2000-2017 | +1.1 to +4.9 pts excess 2000-2017 | -0.2 to -1.7 pts 2010-2017 | - | - | t 0.6-1.3 | quarterly feasible | - | ME_FAIL: no stock-level compute (preregistered) |
| 9 | Fundamentals families (E052 F5 profitability, F7 investment, F9 net issuance) | family level | +1.3 / +2.7 / +1.6 pts 2000-2017 | +0.3 / +0.5 / +0.3 pts 2010-2017 | - | - | t 1.4 / 1.9 / 1.3 | annual feasible | needs EODHD Fundamentals (USD 59.99/month) | ME_PASS at family level only; see section 4 |

## 3. Verdict

No candidate shows plausible net profitability ABOVE the deployable alternative (an S&P 500 UCITS ETF held outright) in 2010-2017 on any data cut available. The architectures that pass the research-interest gate are drawdown overlays: they hold the index most of the time, step aside in prolonged bear markets, and pay for it with 1.5-5 points a year in bull markets. Over 1994-2017 that trade was roughly neutral in CAGR and strongly positive in Sharpe and drawdown; over 2009-2017 it was a loss. That is the same conclusion as E050 H6/H7 (WEAK_SIGNAL) reached on six decades of index data. Opening the one-shot validation window (2018-2021, which contains the March 2020 crash that monthly rules famously missed) on an overlay with no modern excess return would waste the window; it is not done.

Best defensible deployable structure for a EUR 500-1,000 Trading 212 account, if the user values drawdown control over expected return: an S&P 500 UCITS ETF with the G3 or G1a bond-switch overlay, checked once a month (one or two trades a year on average, FX cost negligible). Classification RISK_OVERLAY / WEAK_SIGNAL. It is not a research candidate for validation and it is not "alpha"; the honest expectation is index-like return with a smaller worst case, and underperformance in long bull markets.

## 4. Stop-condition-3 note (specific paid dataset)

EODHD Fundamentals (USD 59.99/month, quarterly statements with filing dates) would allow stock-level tests of operating profitability, asset growth and net share issuance, the only families with a positive 2010-2017 family-level excess (+0.3 to +0.5 percent a year, t 0.3-0.4 in that window; +1.3 to +2.7 percent over 2000-2017). For EUR 1,000 that is EUR 3-5 a year of expected excess before costs against EUR 650 a year of data. The hypothesis is legitimate; the purchase is not justified for this account size. Nothing was bought.

## 5. What would reopen Phase 6

- A data source within the policy that supplies point-in-time fundamentals or earnings-announcement dates at negligible cost (none found on 2026-09-12).
- A genuinely new mechanism with an economic rationale not covered by E050-E053 (the ledger has 455 cells; the closed families are stock momentum in all tested forms, sector-ETF momentum, dividend yield, long-term reversal, low beta/variance at stock level, and every allocation overlay above).
- The user choosing to run the RISK_OVERLAY as a personal allocation policy outside the research program (no validation claim attaches to it).

## 6. Reproduction

From research/ with PYTHONUTF8=1: phase6b_family_screen.py (E052), phase6b_factor_etfs.py (E052b), phase6b_etf_allocation.py (E053), phase6b_etf_redteam.py (E053-RT), the E053b cell script recorded in EXPERIMENTS.md. Reports: reports/E052_20260912T110300, E052B_20260912T110511, E053_20260912T110306, E053RT_20260912T110504, E053B_20260912T110621.
