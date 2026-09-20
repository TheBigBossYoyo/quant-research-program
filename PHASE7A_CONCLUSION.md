# PHASE7A_CONCLUSION - Zero-additional-cost EODHD alpha search (2026-09-12)

# Outcome: **EODHD_OPPORTUNITY_SET_EXHAUSTED**

# Subscription recommendation: **CANCEL BOTH EODHD SUBSCRIPTIONS BEFORE RENEWAL**

## 1. What was run (preregistered in PHASE7A_PLAN.md and EXPERIMENTS.md before any computation; development data only; validation 2018-2021 and holdout 2022-01..2026-08 untouched; nothing purchased)

| Stage | Experiment | Cells | Outcome |
| --- | --- | --- | --- |
| 1 cross-sectional screen (gross, Tier 2 LIQ1000 1998-2017 and Tier 1 PIT S&P 1500 2012-2017) | E055: 52-week-high proximity, overnight persistence, intraday reversal, abnormal volume, liquidity level, 21-day range, idiosyncratic volatility, beta, MAX | 9 | 6 rejected at the gate (52-week high: +2.0%/yr 2010-2017 but t 0.8 and negative on Tier 1; overnight and intraday: strong WRONG-SIGN results, t -3 to -6; abnormal volume: nothing; low liquidity: +1.3%/yr 2010-2017, below the +2% bar; beta: nothing). 3 pass: low range, low idiosyncratic volatility, low MAX (one family in three definitions), top-decile gross excess vs the EW universe +4.4 to +5.4%/yr in 2010-2017, t 1.8-1.9 |
| 2 index events (PIT constituents 2012-04..2017-12, effective dates) | E056: 445 outside additions, 134 promotions, 151 discretionary deletions/demotions, 240 merger deletions; CARs and three long-only calendar-time portfolios | 3 (+ event tables) | every event class underperforms the EW PIT universe afterwards: outside additions -5.5% at 6 months (t -4.5), promotions -3.0% (t -1.8), discretionary deletions -27.7% mean / -12.6% median (t -3.9) and -37% at 12 months (no reversal). Buying deletions shows +38%/yr "excess" with t 0.8 because of one year (2016 +283%), negative in 5 of 6 years. All three portfolios REJECTED |
| 3 portfolio stage (E051 engine, costs, delisting rules, gates S0-S6, multiplicity over 24 Phase 7A trials) | E057: low-risk top-30/50, monthly/quarterly, three signal definitions, plus a Tier 1 replication | 12 (+1) | all REJECTED: net excess vs the EW universe -0.4 to -4.3%/yr (optimistic costs: +0.1 to +0.9%/yr, t <= 0.2); alpha vs SPY t 0.95-1.29; 2010-2017 net CAGR 12.1-13.5% vs SPY 14.4%; BH-FDR passes none; Tier 1 replication 12.4% vs EW 14.9% vs SPY 14.4% |

Cumulative ledger: 479 cells (455 + 24).

## 2. What the data say, mechanism by mechanism

- Index membership changes: the S&P 500/400/600 point-in-time record supports only post-event studies (no announcement dates). Post-inclusion returns are negative, post-deletion returns are strongly negative and do not revert within a year, promotions are flat to negative. There is no long-only trade in any of it; the exploitable directions would be short or avoidance, and avoidance of recently added names is worth about half a percent a year on a diversified portfolio.
- Price-location (52-week high): a weak positive gross tilt on the liquid universe (+2%/yr 2010-2017, t 0.8) that is negative on the point-in-time S&P 1500; below the preregistered bar and, as a close cousin of the closed momentum family, not pursued.
- Overnight/intraday structure: the liquid-universe deciles sorted on trailing 12-month overnight return show the OPPOSITE of the published effect (high-overnight names lose 9-10%/yr vs the universe, t -2 to -3); the low-intraday decile loses 19%/yr (t -6). Both are recorded as wrong-sign rejections; sign flipping after the fact is not allowed by the plan. The pattern is consistent with these deciles being dominated by speculative gap-up names, which the volatility family then identifies from the other side.
- Low realized risk (range, idiosyncratic volatility, MAX): the only family with a positive modern gross decile spread against the equal-weight liquid universe. At portfolio scale (30-50 names, monthly or quarterly) the effect shrinks to zero even at 3 bps costs: the lowest-risk names earn less than the low-risk decile, delisting bookings cut a little more, and the net portfolio returns index-like CAGR with half the beta and two-thirds of the drawdown. Against the deployable alternative, SPY, it wins over 2000-2017 (7.9-8.6% vs 5.6%, the 2000-2002 and 2008 bear markets) and loses over 2010-2017 (12.1-13.5% vs 14.4%). This is the fourth time this program has reached the same object (E050 H3/H4, E052 F3/F4, E052b USMV/SPLV, E057): a risk reducer, not a return engine.
- Liquidity and beta conditioning: within the top-1000 liquid names, lower liquidity earns +3.5%/yr over 2000-2017 (t 3.1) but only +1.3%/yr in 2010-2017 and +5%/yr on the point-in-time S&P 1500 in 2012-2017 (small-cap tilt); beta conditioning has no modern signal. Neither meets the bar; both are recorded.
- Volatility/range states as timing signals: covered by E053 (vol-managed allocation, Phase 6B) and by the range signal above; no new evidence.
- Combinations: none possible; no two independent survivors exist.

## 3. Why the outcome is EXHAUSTED and not NEW_DATA_SOURCE_JUSTIFIED

Every mechanism the current data can support has been screened with modern-evidence gates and rejected. The only families with a positive 2010-2017 family-level sign that remain untested at stock level (profitability, investment, net issuance; Phase 6B) need fundamentals, and their family-level modern excess (+0.3 to +0.5%/yr) is not material for a EUR 500-1,000 account; that assessment (PHASE6B_CONCLUSION.md section 4) stands. No dataset within the policy would change the 2010-2017 verdict on price-derived families, because those results were computed on the full liquid universe with clean point-in-time membership where it exists.

## 4. Cancellation recommendation and reasoning

Cancel both "EOD Historical Data - All World" (USD 19.99/month) and "Indices Historical Constituents Data API" (USD 29.99/month) before renewal.
- Everything the research program can use is on disk and hashed: 50,890 stock histories, 18,972 splits files, dividends endpoint verified, 43 ETF histories, the three constituent histories, all through 2026-09-11. The EULA permits retention for personal, non-commercial analysis.
- The constituents product has no remaining research use: its point-in-time record starts in April 2012, which is already exploited, and its per-request cost was the only reason to keep it for a month.
- The EOD feed would be needed again only to refresh prices for a promoted candidate's validation or holdout run. No candidate exists. If one ever does, a single month of the USD 19.99 plan refreshes everything (one call per ticker; the acquisition scripts are resumable).
- Renewal cost of USD 50/month equals 5-10 percent a year of the intended EUR 500-1,000 trading capital, with no evidence-based path to spending it.

## 5. Where the program stands

Phases 1-5 (crypto), 6 (equity momentum on EODHD), 6B (distinct families and overlays) and 7A (constituent events, price-location, overnight structure, volatility states, liquidity, beta) have all closed without a validation candidate. 479 cells; validation and holdout never read; no live or paper trading. The best deployable structures found are risk overlays and low-volatility tilts that trade expected return for drawdown; none is a research candidate. Further search on the same data would be duplicative; a new mechanism would need a new economic rationale and, most likely, data the policy does not cover.

## 6. Reproduction

From research/ with PYTHONUTF8=1: phase7a_xs_screen.py --t2-start 1998 (E055), phase7a_index_events.py (E056), phase7a_lowrisk_portfolio.py --t2-start 1998 (E057). Reports: reports/E055_20260912T133139, E056_20260912T133249, E057_20260912T133643. Tests: python -m unittest discover -s tests (163).
