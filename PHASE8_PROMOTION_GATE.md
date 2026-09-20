# PHASE8_PROMOTION_GATE - frozen development gates for the insider-purchase family (2026-09-12, before any event return)

Gates are evaluated per strategy cell (C1-C5 of PHASE8_EVENT_RULES.md) on the PRIMARY architecture (126-day hold, 20 slots, MANUAL_USD costs) using monthly net portfolio returns. Benchmarks: the equal-weight Tier 2 eligible universe (rebalanced monthly, delisting bookings identical) and SPY total return (open-to-open on the same calendar).

Coherence check performed before freezing: with 60 monthly observations, a Newey-West t of 2 on the mean excess requires the annualised mean to be about 0.26 x the annualised tracking error; a 20-name event portfolio against an equal-weight universe has tracking error of roughly 8-14 percent a year, so the pair (+3 percent, t >= 2) is attainable only with a tracking error below about 11.6 percent or a mean above 3 percent. The thresholds are kept as drafted in Phase 7B; they are demanding by design, and overlapping six-month positions are handled by HAC(6) standard errors and by the calendar-year sign count.

| Gate | Rule (2013-01..2017-12 unless stated) |
| --- | --- |
| G1 | mean net excess over the EW eligible universe >= +3 percent a year |
| G2 | Newey-West (6 lags) t of that excess >= 2.0 |
| G3 | calendar-year net excess positive in >= 4 of the 5 years 2013-2017 |
| G4 | CAPM alpha of net returns on SPY (HAC 6) t >= 1.5 |
| G5 | maximum drawdown 2009-2017 not deeper than SPY's over the same months by more than 15 points |
| G6 | one-way turnover <= 300 percent a year |
| G7 | AUTOMATED cost case: 2013-2017 net excess over the EW universe > 0 |
| G8 | concentration: best calendar year <= 50 percent of the 2009-2017 cumulative net excess; top 5 events <= 25 percent of cumulative gross contribution; top single ticker <= 10 percent |
| G9 | 2009-2012 net excess over the EW universe >= 0 (reported; a negative early window with a positive late window is allowed only if G1-G4 hold; a positive early window cannot rescue a failed G1-G4) |
| G10 | sample size: >= 150 entered events in 2013-2017 for the cell |

Multiplicity: five genuine strategy cells (C1-C5). Benjamini-Hochberg at 0.05 on the one-sided p-values of G2 across the five; deflated Sharpe (Bailey and Lopez de Prado) with N = 9 Phase 8 trials (C1-C5, E060 two conditioning cells, E059 one cell, E061 one cell) and the empirical variance of the five cells' Sharpe ratios; a cell must pass BH and reach DSR probability >= 0.90. Event-study horizons (+5/+21/+63/+126/+252), slot counts, holding sensitivities, timely/late and size diagnostics are descriptive and are not counted as hypotheses.

Decision: a cell that passes G1-G10 and multiplicity, and survives the red team (PHASE8_RED_TEAM.md list), is frozen (signal, universe, filters, holding period, weighting, costs, hashed code and configuration) and PHASE8_VALIDATION_DECISION.md records PROMISING_CANDIDATE_READY_FOR_VALIDATION with a request for authorisation to open 2018-2021. Otherwise the cell is REJECTED; if no cell passes and E059/E060 do not rescue an independent architecture, the phase records EDGAR_EVENT_FAMILY_REJECTED. Validation is never opened automatically. Small-capital infeasibility does not reject a statistically sound cell; it is labelled RESEARCH_WORTHY_BUT_CAPITAL_LIMITED.

Provisions: all cells, cost cases, sensitivities and diagnostics are written to PHASE8_INSIDER_PORTFOLIOS.csv before interpretation; no threshold changes after results; a code defect forces a documented rerun with the first run retained.
