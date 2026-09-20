# PHASE5_CONCLUSION - independent slow-trend replication and capital-efficient implementation research (9 September 2026)

**Branch A: TREND_REPLICATION_FAILURE. Branch B: CAPITAL_EFFICIENT_WEAK_SIGNAL (capped). Decision: DO_NOT_OPEN_2025. 2026 UNTOUCHED. E040 unchanged.**

## 1. Frozen research object

The exact slow-trend component of frozen E040 (seven equally averaged votes: sign(close - SMA150/200/250), sign(SMA100/150/200/250 - same SMA five bars earlier); 4h; resize on score change at the next scheduled open; hourly marks and funding; no stop), frozen in PHASE5_TREND_FROZEN_SPEC.md (SHA256 96b70e8c...) with the Phase 4 source hashes unchanged and verified before every run. E040 itself stays FROZEN RESEARCH BENCHMARK (hash 9928aa46...).

## 2. Branch A: second cohort

Selected as of 2020-12-31 by rules only (listed before 2020-04-01, >= 90% 2020 completeness, median 2020H2 turnover >= 20m USDT, top 12 excluding BTC/ETH): LINK, LTC, XRP, BCH, BNB, ADA, EOS, TRX, XTZ, XLM, VET, ETC (PHASE5_COHORT2.json SHA256 5ca28d27...). Overlap with Phase 4: 5 of 12 (41.7%); seven new names; underlying-basket correlation with the Phase 4 basket 0.92; no delistings before 2025. Window 2021-01-01..2024-12-31: adds calendar 2021 (never used for any strategy performance before) and seven names. 1,434 monthly kline/mark archives plus 15 daily supplements acquired and checksum-verified; the first replication pass ran on three histories with the documented Binance archive gap and was superseded under the preregistered supplement rule.

## 3. Branch A results (stress costs 9.05 bps + funding; trend only; one sleeve per asset)

| Asset | New | Net return | CAGR | Sharpe | Max DD | Trades | Two-factor alpha [95% CI] | Long P&L | Short P&L |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| LINKUSDT | no | -88.5% | -41.8% | -0.18 | -96.0% | 265 | -12% [-89%, +65%] | -3,516 | -5,337 |
| LTCUSDT | no | -86.0% | -38.8% | -0.31 | -92.1% | 232 | -18% [-82%, +46%] | -7,069 | -1,528 |
| XRPUSDT | no | -22.1% | -6.0% | 0.34 | -88.2% | 257 | +11% [-63%, +85%] | 3,627 | -5,838 |
| BCHUSDT | yes | -43.9% | -13.5% | 0.24 | -77.7% | 300 | +21% [-50%, +91%] | 1,594 | -5,987 |
| BNBUSDT | no | +372.3% | 47.4% | 0.85 | -66.6% | 247 | +32% [-39%, +102%] | 93,163 | -55,937 |
| ADAUSDT | no | +447.0% | 52.9% | 0.92 | -82.5% | 204 | +62% [-24%, +147%] | 48,848 | -4,147 |
| EOSUSDT | yes | -58.0% | -19.5% | 0.18 | -78.9% | 267 | +33% [-41%, +108%] | -3,458 | -2,339 |
| TRXUSDT | yes | -42.1% | -12.8% | 0.20 | -84.2% | 237 | -25% [-92%, +42%] | 1,035 | -5,249 |
| XTZUSDT | yes | -47.7% | -14.9% | 0.25 | -79.5% | 251 | +32% [-46%, +110%] | -3,559 | -1,207 |
| XLMUSDT | yes | +35.6% | 7.9% | 0.49 | -79.5% | 193 | +31% [-44%, +105%] | 5,321 | -1,758 |
| VETUSDT | yes | +1,387% | 96.3% | 1.17 | -52.0% | 186 | +108% [+31%, +186%] | 136,688 | 2,007 |
| ETCUSDT | yes | +225.0% | 34.2% | 0.76 | -72.5% | 217 | +46% [-35%, +127%] | 18,956 | 3,540 |

Positive net 5 of 12; positive Sharpe 10 of 12; median net return -32%; median CAGR -9%; median Sharpe 0.295; median drawdown -80%; median two-factor alpha +31%/yr (9 of 12 positive, one interval excludes zero); gross exposure 0.72-0.76, maximum hourly gross 1.25-3.71. Equal-weight cohort portfolio: +114%, CAGR 20.9%, Sharpe 0.618, DD -56.7%, years 2021 +87.4% / 2022 -6.5% / 2023 -10.6% / 2024 +36.6%; cost cases Sharpe 0.48 (adverse funding) to 0.66 (base), positive-asset fraction 0.33-0.42 in every case; extra 4h delay +138%; volatility-scaled slippage (multipliers 1.8-2.5x) +78%.

## 4. Cross-cohort evidence

| Cell | Assets | Positive net | Positive Sharpe | Median Sharpe | Median alpha | Portfolio Sharpe | Portfolio DD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Cohort 1 (Phase 4) trend-only 2022-2024 | 12 | 0.58 | 0.75 | 0.65 | +57% | 0.75 | -42% |
| Cohort 2, 2021-2024 | 12 | 0.42 | 0.83 | 0.29 | +31% | 0.62 | -57% |
| Cohort 2 new names, 2021-2024 | 7 | 0.43 | 1.00 | 0.25 | +32% | 0.67 | -47% |
| Cohort 2 overlapping names, 2021-2024 | 5 | 0.40 | 0.60 | 0.34 | +11% | 0.46 | -75% |
| Cohort 2, calendar 2021 only | 12 | 0.58 | 0.92 | 0.68 | +19% | 1.16 | -40% |
| Cohort 2, 2022-2024 (cohort-1 window) | 12 | 0.42 | 0.67 | 0.15 | +24% | 0.32 | -53% |
| Cohort 2 new names, 2022-2024 | 7 | 0.57 | 0.86 | 0.44 | +39% | 0.54 | -46% |

Dependence-aware: cohort-2 common-time-block 95% intervals, median alpha [-37%, +78%] / [-31%, +76%] / [-33%, +70%] (14/30/60-day blocks), median Sharpe [-0.42, +1.07], positive fraction [0.17, 1.00]; new names [-33%, +92%]; cohort 1 [-11%, +102%]. Cohort portfolios over 2022-2024 are 0.88 correlated; Sharpe difference (cohort 2 minus cohort 1) 95% interval [-1.08, +0.16]. Sign consistency by year: cohort 1 +/+/+ (2022-2024), cohort 2 +/-/-/+ (2021-2024). Median two-factor alpha by year (cohort 2): +19%, -41%, -11%, +32%. Heterogeneity: median Sharpe 0.65 (cohort 1) vs 0.29 (cohort 2) vs 0.25 (new names).

## 5. Temporal, long/short and crash analysis (PHASE5_TEMPORAL_CONCENTRATION.md, PHASE5_LONG_SHORT_ANALYSIS.md)

Half-years: 2021H1 +79% (long), 2021H2 +5%, 2022H1 +20% (net short, -0.37), 2022H2 -22%, 2023H1 -19%, 2023H2 +10%, 2024H1 -5%, 2024H2 +43%. BTC above its lagged 200-day average: +184% over those days; below: -25%. Answer to the mandate's question: yes, the strategy earns when the asset class trends as a whole and loses or stalls otherwise; 2021 supplies 60% of positive P&L and the top quarter (2024Q4) 32%. Long side +155% of capital lifetime, Sharpe 0.80, positive in 8 of 12 sleeves; short side -8%, Sharpe -0.05, positive in 2 of 12, but +29% in 2022; removing the short contribution changes the drawdown from -57% to -52%. Crash windows: May-2021 +40% (net -0.41), Nov-2021..Jun-2022 +23% (net -0.39), FTX +4%, Aug-2024 +2%; worst single day -16%; peak gross 1.03. Controlled in crises, not profitable across regimes.

## 6. Concentration and risk

Portfolio: top trade 3.8%, top 5 15.4%, top 10 24.9% of positive P&L; best year 2021 60.4%; remove best year +14%; remove best five trade contributions +11%. Per asset, top-5 trades 58-82% and top year 33-100%. Monte Carlo (block 14/60, permutation): median max drawdown 58-64%, 95th percentile 79-87%, P(DD > 40%) 96-100%, no ruin at 1x.

## 7. Branch A gate (PHASE5_PREVALIDATION_DECISION.md)

7 of 16 pass. Failing: positive-net fraction 0.42 (< 2/3), median Sharpe 0.295 (< 0.30), common-block alpha lower bound < 0, new-names cell (3 of 7 positive), years positive 2 of 4, conservative-cost positive fraction 0.42, top-year share 60.4% (> 60%), drawdown -57% (< -40%). Preregistered classification: TREND_REPLICATION_FAILURE (median net return <= 0 and positive fraction <= 1/2). Decision DO_NOT_OPEN_2025.

## 8. Branch B: CAPITAL_EFFICIENCY_RESEARCH (E049_20260909T153444; PHASE5_CAPITAL_SPEC.md, PHASE5_CAPITAL_UNIVERSE.md, PHASE5_CAPITAL_FEASIBILITY.md, PHASE5_CAPITAL_RESULTS.csv)

Universe by venue rules and history only: ETH, SOL, XRP, DOT, DOGE (top-N by 2021H2 liquidity; N = 2-5). New architectures: pooled capital, one position per asset, target = score x equity x scalar / N, lot rounding, minimum-notional accumulation buffer, dead-bands, 20% volatility-target overlay; 2022-2024; stress costs. The first run resized to equity drift and was superseded (spec amendment 1) before the valid run.

| Configuration (dead-band 0) | Unconstrained Sharpe | CAGR | Max DD | Turnover vs avg equity | Cost vs avg equity | Sharpe at 500 USDT | Retention | Skipped orders at 500 | TE / vol |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| N=2, 1x | 0.92 | 45% | -50% | 84x | 7.6% | 0.92 | 1.00 | 0.1% | 0.2% |
| N=5, 1x | 0.96 | 43% | -49% | 88x | 8.0% | 0.95 | 1.00 | 0.1% | 0.5% |
| N=2, 1x, vol target 20% | 1.12 | 31% | -29% | 40x | 3.6% | 1.14 | 1.02 | 0.5% | 1.4% |
| N=5, 1x, vol target 20% | 1.17 | 31% | -23% | 49x | 4.4% | 1.17 | 1.00 | 4.2% | 3.4% |
| N=5, 0.5x | 0.95 | 25% | -28% | 45x | 4.1% | 0.95 | 1.00 | 0.1% | 0.5% |

At 500 USDT every N = 2-5 configuration is operationally feasible (skipped orders <= 4.2%, tracking error <= 3.4% of volatility, Sharpe retention 0.99-1.02); minimum practical capital for this architecture is <= 500 USDT, against 12,600-31,500 USDT for the 24-sleeve E040 layout. Dead-bands of 0.10 and 0.25 are inert because a vote flip moves the score by 0.286. With vol targeting at 500 USDT, sub-minimum resizes wait 485-3,187 hours in total over three years (N=2 to N=5); at 1,000 USDT, 162-839 hours. Classification for every configuration: CAPITAL_EFFICIENT_WEAK_SIGNAL, the maximum allowed when Branch A fails; no PAPER_FEASIBILITY_CANDIDATE; no live or paper trading authorised.

## 9. Equity data feasibility

EQUITY_DATA_FEASIBILITY.md: free sources cannot satisfy survivorship and corporate-action requirements; one paid source near the EUR 50/month ceiling (Norgate or EODHD, both UNVERIFIED) might; any market-neutral equity architecture is research-only under the current Trading 212 Invest account. No purchase made; user decision required before any subscription.

## 10. Red team (PHASE5_RED_TEAM_REPORT.md)

Decisive attacks: volatility drag at 0.75 gross turns a 0.3 Sharpe into losses on 7 of 12 sleeves; cohort 2 is 0.88 correlated with cohort 1 and half as good on the shared window; 2021 is one alt-season year and 60% of the P&L; every dependence-aware interval includes zero; shorts are defence not alpha; Branch B implements an unreplicated signal on names selected by rules that happen to favour 2023-2024 winners. Researcher defence: sign transported on 10 of 12 and 7 of 7 new names, +87% in the never-used 2021 regime, controlled and net short through every crash window, robust to costs and delay, and the operational barrier to small capital is solved.

## 11. Phase 5 decision tree outcome

Branch A failed independent replication: 2025 stays locked, slow trend is downgraded from "cross-asset weak signal" to "regime description, not a validated stand-alone premium"; no rescue by optimisation. Branch B succeeded operationally but is capped: preserved as CAPITAL_EFFICIENT_WEAK_SIGNAL for a later phase, not as a validation candidate. Cumulative hypotheses: 388 (Branch A one economic hypothesis; Branch B two architectures). 124 tests pass; every run carries source, spec, cohort and universe hashes; superseded runs retained and labelled (E047_20260909T150950, E048_20260909T151232, E049_20260909T152740).

## 12. Next highest-information action

Not another crypto cohort on 2020-2024 (the shared regime is exhausted) and not any E040 or trend-parameter change. The remaining informative options, each requiring a preregistered freeze first: (a) a volatility-scaled trend architecture evaluated on a cohort and window not yet inspected, which today means waiting for 2025 to become usable only through a passed gate, so it is not available; (b) a different market class (equity/ETF or futures) with verified survivorship-safe data, budget approval pending; (c) closing the program at "no validated strategy" with E040 and the Phase 5 artefacts as the frozen benchmark set.
