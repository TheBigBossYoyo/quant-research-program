# E051 first attempt - ABORTED (2026-09-12 00:10 UTC) - data-integrity defect, no results.json written

Aborted after 9 of 24 trials because the Tier 2 top-N portfolios were selecting vendor data errors: the highest 12-1 momentum
scores among "eligible" names were 424,999x (ALT: adjusted close 0.003 -> 127), 11,970x (IPSI), 5,694x (HKT: unadjusted close
0.80 -> 5,181 in a day), 9,999,999x (GTCH: placeholder price 1,000,000 with a split factor of 0), 1,200,047x (ADD). Trial statistics
were nearly identical across N = 10/20/30/50 (net Sharpe 0.38, t 1.64-1.66), which is what a few corrupted names dominating
every variant looks like. The nine logged lines are retained here and are NOT evidence about any strategy.

Fix (preregistered before the valid run; PHASE6_EODHD_COVERAGE_AUDIT.md section 3.8): integrity rules I1-I5 applied
symmetrically to strategies and benchmarks; panels rebuilt; run repeated as E051_<stamp>.
