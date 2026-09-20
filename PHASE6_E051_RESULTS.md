# PHASE6_E051_RESULTS - stock-level momentum family on EODHD (E051_20260911T233815; development only, <= 2017-12-31)

Gate document hash at run time: 6de8989459c78c01d08bb5754b66e0d18e6b9ee23410a1bff3588abee60f19c4 (frozen value in PHASE6_NORGATE_PURCHASE_GATE.sha256). Trials 24; Tier 2 start year 1998 (audit rule A2); signals 1985-01-31..2017-10-31 (394); seed 20260911; bootstrap draws 4000. Universe counts per year (min/median/max eligible names) and delistings booked are in results.json meta.

## 1. All trials (base cost 20/20.3 bps, base delisting rule). Every preregistered cell is shown; nothing was dropped.

| Trial | Months | Net CAGR | EW bench CAGR | SPY CAGR | Net Sharpe | Max DD | Net excess vs EW (ann.) | HAC t | Boot 95% CI (ann.) | Stress excess (ann.) | Eras (sign t) | Last 36m excess (ann.) | Rolling-60 positive | CAPM alpha t vs SPY | DSR | BH | Class | Failed gates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| T2_A_mom12_1_N10 | 238 | -1.0% | 5.7% | 6.9% | 0.22 | -98% | 3.4% | 0.31 | [-19.9%, 31.9%] | 1.4% | E2b:+3.65 / E3:--0.98 / E4:--1.32 | -16.0% | 25% | -0.01 | 0.08 | N | REJECTED | s1_t,s2_eras,s4_recent,s5_spy,s6_dd |
| T2_A_mom12_1_N20 | 238 | -2.3% | 5.7% | 6.9% | 0.15 | -96% | -1.5% | -0.18 | [-17.5%, 18.1%] | -3.3% | E2b:+3.85 / E3:--1.50 / E4:--1.44 | -11.2% | 12% | -0.49 | 0.05 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy,s6_dd |
| T2_A_mom12_1_N30 | 238 | 2.2% | 5.7% | 6.9% | 0.25 | -88% | 1.8% | 0.25 | [-11.8%, 19.2%] | 0.0% | E2b:+3.29 / E3:--0.75 / E4:--1.13 | -11.0% | 19% | -0.08 | 0.10 | N | REJECTED | s1_t,s2_eras,s4_recent,s5_spy,s6_dd |
| T2_A_mom12_1_N50 | 238 | 2.7% | 5.7% | 6.9% | 0.25 | -82% | 0.5% | 0.10 | [-9.2%, 11.8%] | -1.2% | E2b:+3.00 / E3:--0.88 / E4:--0.84 | -8.8% | 19% | -0.23 | 0.10 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy,s6_dd |
| T2_A_mom6_1_N10 | 238 | -7.3% | 5.7% | 6.9% | 0.05 | -98% | -5.7% | -0.75 | [-21.4%, 12.1%] | -8.2% | E2b:+4.52 / E3:--1.77 / E4:--1.39 | -5.0% | 19% | -1.13 | 0.02 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy,s6_dd |
| T2_A_mom6_1_N20 | 238 | -2.1% | 5.7% | 6.9% | 0.15 | -93% | -2.2% | -0.39 | [-12.0%, 9.7%] | -4.6% | E2b:+4.30 / E3:--1.30 / E4:--1.00 | -6.0% | 19% | -0.67 | 0.05 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy,s6_dd |
| T2_A_mom6_1_N30 | 238 | 4.2% | 5.7% | 6.9% | 0.29 | -85% | 2.9% | 0.53 | [-7.8%, 16.3%] | 0.6% | E2b:+4.32 / E3:--0.63 / E4:--0.36 | -5.3% | 31% | 0.13 | 0.14 | N | REJECTED | s1_t,s2_eras,s4_recent,s5_spy,s6_dd |
| T2_A_mom6_1_N50 | 238 | 5.4% | 5.7% | 6.9% | 0.32 | -82% | 2.9% | 0.59 | [-6.9%, 14.8%] | 0.6% | E2b:+3.94 / E3:--0.58 / E4:--0.09 | -1.9% | 38% | 0.20 | 0.17 | N | REJECTED | s1_t,s2_eras,s4_recent,s5_spy,s6_dd |
| T2_A_mom9_1_N10 | 238 | -1.8% | 5.7% | 6.9% | 0.20 | -97% | 1.2% | 0.14 | [-17.3%, 25.9%] | -1.0% | E2b:+2.76 / E3:--1.74 / E4:--0.42 | 11.6% | 12% | -0.21 | 0.07 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy,s6_dd |
| T2_A_mom9_1_N20 | 238 | 1.5% | 5.7% | 6.9% | 0.23 | -89% | 1.7% | 0.27 | [-10.4%, 16.0%] | -0.4% | E2b:+4.67 / E3:--0.80 / E4:--0.71 | -1.9% | 25% | -0.09 | 0.09 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy,s6_dd |
| T2_A_mom9_1_N30 | 238 | 1.7% | 5.7% | 6.9% | 0.23 | -90% | 0.9% | 0.15 | [-11.2%, 16.1%] | -1.1% | E2b:+5.32 / E3:--1.18 / E4:--0.74 | -3.6% | 12% | -0.18 | 0.09 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy,s6_dd |
| T2_A_mom9_1_N50 | 238 | 4.3% | 5.7% | 6.9% | 0.29 | -85% | 2.1% | 0.39 | [-8.5%, 15.1%] | 0.2% | E2b:+4.30 / E3:--0.93 / E4:--0.18 | -1.3% | 31% | 0.07 | 0.14 | N | REJECTED | s1_t,s2_eras,s4_recent,s5_spy,s6_dd |
| T2_B_resid12_1_N10 | 238 | 3.6% | 5.7% | 6.9% | 0.28 | -76% | 0.6% | 0.11 | [-9.9%, 11.3%] | -2.1% | E2b:+2.53 / E3:--0.31 / E4:--1.07 | -6.8% | 38% | -0.27 | 0.14 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy,s6_dd |
| T2_B_resid12_1_N20 | 238 | 3.9% | 5.7% | 6.9% | 0.28 | -76% | -0.7% | -0.19 | [-9.7%, 7.8%] | -3.2% | E2b:+1.65 / E3:--1.21 / E4:+0.31 | 1.3% | 50% | -0.55 | 0.14 | N | REJECTED | s1_t,s3_stress,s4_recent,s5_spy,s6_dd |
| T2_B_resid12_1_N30 | 238 | 4.7% | 5.7% | 6.9% | 0.32 | -68% | -0.5% | -0.16 | [-7.6%, 6.1%] | -2.9% | E2b:+0.78 / E3:--0.78 / E4:+0.01 | 0.1% | 38% | -0.52 | 0.19 | N | REJECTED | s1_t,s3_stress,s4_recent,s5_spy,s6_dd |
| T2_B_resid12_1_N50 | 238 | 4.8% | 5.7% | 6.9% | 0.32 | -65% | -0.8% | -0.29 | [-5.7%, 3.9%] | -3.0% | E2b:+0.20 / E3:--0.41 / E4:--0.23 | -3.7% | 31% | -0.63 | 0.19 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy |
| T2_A_volmom12_1_N30 | 238 | 10.4% | 5.7% | 6.9% | 0.46 | -72% | 6.7% | 1.12 | [-7.5%, 23.8%] | 4.8% | E2b:+5.73 / E3:--0.08 / E4:--0.10 | -0.6% | 56% | 0.87 | 0.37 | N | REJECTED | s1_t,s2_eras,s4_recent,s5_spy,s6_dd |
| T1_A_mom12_1_N30 | 67 | 14.5% | 14.9% | 14.4% | 0.91 | -24% | 0.2% | 0.06 | [-5.2%, 5.6%] | -1.6% | E4:+0.06 | -3.2% | 0% | -0.07 | 0.81 | N | REJECTED | s0_min_months,s1_t,s2_eras,s3_stress,s4_recent,s5_spy,s6_dd |
| T1_B_resid12_1_N30 | 67 | 12.5% | 14.9% | 14.4% | 0.92 | -19% | -1.9% | -0.69 | [-6.3%, 1.9%] | -4.6% | E4:--0.69 | -1.4% | 0% | -0.54 | 0.81 | N | REJECTED | s0_min_months,s1_t,s2_eras,s3_stress,s4_recent,s5_spy |
| T1_A_secneutral12_1_N30 | 67 | 16.9% | 14.9% | 14.4% | 1.15 | -19% | 2.1% | 0.88 | [-0.8%, 5.1%] | 0.5% | E4:+0.88 | 0.6% | 100% | 0.46 | 0.91 | N | REJECTED | s0_min_months,s1_t,s2_eras,s5_spy |
| ETF_F_mom12_1_top3 | 215 | 5.4% | 7.2% | 5.2% | 0.43 | -41% | -1.7% | -1.03 | [-3.9%, 0.6%] | -2.3% | E3:--0.40 / E4:--1.29 | -3.9% | 14% | 0.52 | 0.35 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy |
| ETF_F_mom12_1_top2 | 215 | 4.6% | 7.2% | 5.2% | 0.35 | -45% | -2.2% | -1.07 | [-5.5%, 1.1%] | -2.9% | E3:--0.54 / E4:--1.24 | -5.9% | 36% | 0.08 | 0.25 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy |
| ETF_F_mom12_1_top4 | 215 | 6.0% | 7.2% | 5.2% | 0.49 | -44% | -1.2% | -0.94 | [-3.0%, 0.6%] | -1.6% | E3:--0.52 / E4:--0.72 | -2.6% | 29% | 1.06 | 0.44 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy |
| ETF_F_mom6_1_top3 | 215 | 6.5% | 7.2% | 5.2% | 0.52 | -42% | -0.8% | -0.59 | [-2.8%, 1.2%] | -1.5% | E3:+0.04 / E4:--1.41 | -2.0% | 29% | 1.26 | 0.49 | N | REJECTED | s1_t,s2_eras,s3_stress,s4_recent,s5_spy |

## 2. Primary cells and survivors in detail (cost cases and delisting sensitivities)

### T2_A_mom12_1_N30 (tier LIQ1000, avg held 30.00)

| Variant | Net CAGR | Net Sharpe | Max DD | Excess vs EW (ann.) | t | Turnover one-way/yr | Cost/yr |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| optimistic|base | 3.9% | 0.29 | -86% | 3.5% | 0.47 | - | - |
| base|base | 2.2% | 0.25 | -88% | 1.8% | 0.25 | - | - |
| stress|base | 0.4% | 0.20 | -91% | 0.0% | 0.00 | - | - |
| base|all100 | 2.2% | 0.24 | -89% | 1.8% | 0.24 | - | - |
| base|all30 | -0.7% | 0.17 | -93% | -1.0% | -0.14 | - | - |

Rolling 60-month windows (end year: annualised net excess vs EW, HAC t, net Sharpe): 2002: 27.5%, 1.24, 0.52; 2003: 16.8%, 0.83, 0.48; 2004: -3.5%, -0.27, -0.03; 2005: -6.6%, -0.78, -0.09; 2006: -5.6%, -0.68, 0.13; 2007: 3.0%, 0.32, 0.59; 2008: -3.4%, -0.30, -0.29; 2009: -10.3%, -0.80, -0.28; 2010: -13.3%, -1.12, -0.29; 2011: -12.8%, -1.08, -0.33; 2012: -16.9%, -1.72, -0.35; 2013: -8.7%, -1.02, 0.46; 2014: -2.9%, -0.51, 0.35; 2015: -7.4%, -1.03, -0.14; 2016: -5.2%, -0.75, 0.11; 2017: -6.4%, -0.93, 0.12

Concentration: best year 1999 = 71% of total net arithmetic return; top-5 months 113%; top-10 names 52% of gross contribution; worst 12 months -71.2%.
Market beta vs SPY 1.44; sector-ETF regression R2 0.40, largest loadings: XLK 0.99, XLP -0.56, XLV 0.34, XLY -0.32
Feasibility EUR 500: position USD 19, one-way turnover 4.7x/yr, cost 1.90%/yr = USD 11, typical trade USD 1.0 (below EUR 1)
Feasibility EUR 1000: position USD 39, one-way turnover 4.7x/yr, cost 1.90%/yr = USD 22, typical trade USD 1.9

### T2_B_resid12_1_N30 (tier LIQ1000, avg held 30.00)

| Variant | Net CAGR | Net Sharpe | Max DD | Excess vs EW (ann.) | t | Turnover one-way/yr | Cost/yr |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| optimistic|base | 7.0% | 0.41 | -65% | 1.7% | 0.50 | - | - |
| base|base | 4.7% | 0.32 | -68% | -0.5% | -0.16 | - | - |
| stress|base | 2.3% | 0.22 | -70% | -2.9% | -0.87 | - | - |
| base|all100 | 4.7% | 0.32 | -68% | -0.5% | -0.16 | - | - |
| base|all30 | 2.8% | 0.24 | -70% | -2.3% | -0.70 | - | - |

Rolling 60-month windows (end year: annualised net excess vs EW, HAC t, net Sharpe): 2002: 9.9%, 1.20, 0.49; 2003: 0.2%, 0.03, 0.41; 2004: 5.3%, 1.18, 0.27; 2005: 6.0%, 1.79, 0.40; 2006: -1.0%, -0.21, 0.42; 2007: -3.3%, -0.69, 0.57; 2008: -3.9%, -0.61, -0.41; 2009: -13.0%, -1.73, -0.45; 2010: -13.8%, -1.85, -0.38; 2011: -12.2%, -1.65, -0.39; 2012: -10.3%, -1.49, -0.19; 2013: -7.2%, -1.19, 0.70; 2014: -0.0%, -0.01, 0.66; 2015: -0.2%, -0.04, 0.19; 2016: 3.0%, 0.93, 0.73; 2017: 1.3%, 0.45, 0.75

Concentration: best year 1998 = 39% of total net arithmetic return; top-5 months 52%; top-10 names 30% of gross contribution; worst 12 months -61.0%.
Market beta vs SPY 1.22; sector-ETF regression R2 0.65, largest loadings: XLK 0.46, XLV 0.29, XLE 0.25, XLP -0.22
Feasibility EUR 500: position USD 19, one-way turnover 6.4x/yr, cost 2.59%/yr = USD 15, typical trade USD 1.0 (below EUR 1)
Feasibility EUR 1000: position USD 39, one-way turnover 6.4x/yr, cost 2.59%/yr = USD 30, typical trade USD 1.9

### T1_A_mom12_1_N30 (tier PIT_SP1500, avg held 30.00)

| Variant | Net CAGR | Net Sharpe | Max DD | Excess vs EW (ann.) | t | Turnover one-way/yr | Cost/yr |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| optimistic|base | 16.2% | 1.01 | -23% | 1.7% | 0.50 | - | - |
| base|base | 14.5% | 0.91 | -24% | 0.2% | 0.06 | - | - |
| stress|base | 12.5% | 0.80 | -25% | -1.6% | -0.46 | - | - |
| base|all100 | 14.5% | 0.91 | -24% | 0.2% | 0.06 | - | - |
| base|all30 | 10.6% | 0.70 | -25% | -3.2% | -0.79 | - | - |

Rolling 60-month windows (end year: annualised net excess vs EW, HAC t, net Sharpe): 2017: -0.8%, -0.22, 0.89

Concentration: best year 2013 = 42% of total net arithmetic return; top-5 months 55%; top-10 names 37% of gross contribution; worst 12 months -15.9%.
Market beta vs SPY 1.09; sector-ETF regression R2 0.60, largest loadings: XLP -0.79, XLY 0.74, XLV 0.66, XLB -0.35
Feasibility EUR 500: position USD 19, one-way turnover 4.4x/yr, cost 1.79%/yr = USD 10, typical trade USD 1.0 (below EUR 1)
Feasibility EUR 1000: position USD 39, one-way turnover 4.4x/yr, cost 1.79%/yr = USD 21, typical trade USD 1.9

### T1_B_resid12_1_N30 (tier PIT_SP1500, avg held 30.00)

| Variant | Net CAGR | Net Sharpe | Max DD | Excess vs EW (ann.) | t | Turnover one-way/yr | Cost/yr |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| optimistic|base | 15.0% | 1.08 | -16% | 0.3% | 0.12 | - | - |
| base|base | 12.5% | 0.92 | -19% | -1.9% | -0.69 | - | - |
| stress|base | 9.6% | 0.73 | -22% | -4.6% | -1.67 | - | - |
| base|all100 | 12.5% | 0.92 | -19% | -1.9% | -0.69 | - | - |
| base|all30 | 10.9% | 0.81 | -22% | -3.3% | -1.15 | - | - |

Rolling 60-month windows (end year: annualised net excess vs EW, HAC t, net Sharpe): 2017: -2.5%, -0.83, 0.94

Concentration: best year 2016 = 45% of total net arithmetic return; top-5 months 51%; top-10 names 26% of gross contribution; worst 12 months -16.4%.
Market beta vs SPY 1.06; sector-ETF regression R2 0.72, largest loadings: XLI 0.41, XLY 0.37, XLE 0.32, XLP -0.27
Feasibility EUR 500: position USD 19, one-way turnover 6.5x/yr, cost 2.61%/yr = USD 15, typical trade USD 1.0 (below EUR 1)
Feasibility EUR 1000: position USD 39, one-way turnover 6.5x/yr, cost 2.61%/yr = USD 30, typical trade USD 1.9

### ETF_F_mom12_1_top3 (tier SECTOR_ETF, avg held 3.00)

| Variant | Net CAGR | Net Sharpe | Max DD | Excess vs EW (ann.) | t | Turnover one-way/yr | Cost/yr |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| optimistic|base | 6.4% | 0.49 | -41% | -0.7% | -0.45 | - | - |
| base|base | 5.4% | 0.43 | -41% | -1.7% | -1.03 | - | - |
| stress|base | 4.8% | 0.39 | -42% | -2.3% | -1.38 | - | - |
| base|all100 | 5.4% | 0.43 | -41% | -1.7% | -1.03 | - | - |
| base|all30 | 5.4% | 0.43 | -41% | -1.7% | -1.03 | - | - |

Rolling 60-month windows (end year: annualised net excess vs EW, HAC t, net Sharpe): 2004: -0.2%, -0.08, 0.27; 2005: 3.4%, 1.43, 0.57; 2006: -0.5%, -0.17, 0.66; 2007: -1.3%, -0.45, 1.08; 2008: 2.3%, 0.63, 0.09; 2009: -1.8%, -0.45, 0.12; 2010: -3.2%, -0.86, 0.14; 2011: -2.9%, -0.78, 0.07; 2012: -3.1%, -0.91, 0.19; 2013: -5.0%, -1.38, 0.84; 2014: -1.7%, -0.71, 0.90; 2015: -2.3%, -1.02, 0.58; 2016: -2.1%, -1.05, 1.05; 2017: -1.3%, -0.56, 1.31

Concentration: best year 2003 = 22% of total net arithmetic return; top-5 months 43%; top-10 names 100% of gross contribution; worst 12 months -36.0%.
Market beta vs SPY 0.86; sector-ETF regression R2 0.82, largest loadings: XLE 0.22, XLB 0.20, XLK 0.14, XLV 0.12
Feasibility EUR 500: position USD 194, one-way turnover 2.8x/yr, cost 1.13%/yr = USD 7, typical trade USD 9.7
Feasibility EUR 1000: position USD 388, one-way turnover 2.8x/yr, cost 1.13%/yr = USD 13, typical trade USD 19.4


## 3. Overlays (survivors only)

No trial passed the survivor and multiplicity gates; no overlay was computed (preregistered rule).

## 4. Benchmarks (monthly, full window of each tier)

- LIQ1000: CAGR 5.7%, Sharpe 0.36, max DD -61%, months 238
- PIT_SP1500: CAGR 14.9%, Sharpe 1.18, max DD -14%, months 67
- SECTOR_ETF: CAGR 7.2%, Sharpe 0.56, max DD -49%, months 215

## 5. Universe

Eligible counts per year: {"LIQ1000": {"1985": {"min": 0, "median": 0.0, "max": 0}, "1986": {"min": 0, "median": 0.0, "max": 0}, "1987": {"min": 0, "median": 0.0, "max": 0}, "1988": {"min": 0, "median": 0.0, "max": 0}, "1989": {"min": 0, "median": 0.0, "max": 0}, "1990": {"min": 0, "median": 0.0, "max": 0}, "1991": {"min": 0, "median": 0.0, "max": 0}, "1992": {"min": 0, "median": 0.0, "max": 0}, "1993": {"min": 0, "median": 0.0, "max": 0}, "1994": {"min": 0, "median": 0.0, "max": 0}, "1995": {"min": 0, "median": 0.0, "max": 0}, "1996": {"min": 0, "median": 0.0, "max": 0}, "1997": {"min": 0, "median": 0.0, "max": 0}, "1998": {"min": 823, "median": 886.5, "max": 1000}, "1999": {"min": 1000, "median": 1000.0, "max": 1000}, "2000": {"min": 1000, "median": 1000.0, "max": 1000}, "2001": {"min": 1000, "median": 1000.0, "max": 1000}, "2002": {"min": 1000, "median": 1000.0, "max": 1000}, "2003": {"min": 1000, "median": 1000.0, "max": 1000}, "2004": {"min": 1000, "median": 1000.0, "max": 1000}, "2005": {"min": 1000, "median": 1000.0, "max": 1000}, "2006": {"min": 1000, "median": 1000.0, "max": 1000}, "2007": {"min": 1000, "median": 1000.0, "max": 1000}, "2008": {"min": 1000, "median": 1000.0, "max": 1000}, "2009": {"min": 1000, "median": 1000.0, "max": 1000}, "2010": {"min": 1000, "median": 1000.0, "max": 1000}, "2011": {"min": 1000, "median": 1000.0, "max": 1000}, "2012": {"min": 1000, "median": 1000.0, "max": 1000}, "2013": {"min": 1000, "median": 1000.0, "max": 1000}, "2014": {"min": 1000, "median": 1000.0, "max": 1000}, "2015": {"min": 1000, "median": 1000.0, "max": 1000}, "2016": {"min": 1000, "median": 1000.0, "max": 1000}, "2017": {"min": 1000, "median": 1000.0, "max": 1000}}, "PIT_SP1500": {"1985": {"min": 0, "median": 0.0, "max": 0}, "1986": {"min": 0, "median": 0.0, "max": 0}, "1987": {"min": 0, "median": 0.0, "max": 0}, "1988": {"min": 0, "median": 0.0, "max": 0}, "1989": {"min": 0, "median": 0.0, "max": 0}, "1990": {"min": 0, "median": 0.0, "max": 0}, "1991": {"min": 0, "median": 0.0, "max": 0}, "1992": {"min": 0, "median": 0.0, "max": 0}, "1993": {"min": 0, "median": 0.0, "max": 0}, "1994": {"min": 0, "median": 0.0, "max": 0}, "1995": {"min": 0, "median": 0.0, "max": 0}, "1996": {"min": 0, "median": 0.0, "max": 0}, "1997": {"min": 0, "median": 0.0, "max": 0}, "1998": {"min": 0, "median": 0.0, "max": 0}, "1999": {"min": 0, "median": 0.0, "max": 0}, "2000": {"min": 0, "median": 0.0, "max": 0}, "2001": {"min": 0, "median": 0.0, "max": 0}, "2002": {"min": 0, "median": 0.0, "max": 0}, "2003": {"min": 0, "median": 0.0, "max": 0}, "2004": {"min": 0, "median": 0.0, "max": 0}, "2005": {"min": 0, "median": 0.0, "max": 0}, "2006": {"min": 0, "median": 0.0, "max": 0}, "2007": {"min": 0, "median": 0.0, "max": 0}, "2008": {"min": 0, "median": 0.0, "max": 0}, "2009": {"min": 0, "median": 0.0, "max": 0}, "2010": {"min": 0, "median": 0.0, "max": 0}, "2011": {"min": 0, "median": 0.0, "max": 0}, "2012": {"min": 0, "median": 1304.5, "max": 1310}, "2013": {"min": 1313, "median": 1325.0, "max": 1341}, "2014": {"min": 1339, "median": 1347.0, "max": 1350}, "2015": {"min": 1351, "median": 1353.0, "max": 1357}, "2016": {"min": 1347, "median": 1378.5, "max": 1395}, "2017": {"min": 1391, "median": 1395.0, "max": 1401}}}

Delistings booked inside eligible sets: {"LIQ1000": 703, "PIT_SP1500": 248}; sector labels available for 1502 current constituents only (SECTOR_NOT_PIT).
