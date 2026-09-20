# PHASE6_RED_TEAM_REPORT

## Part 1 - family-level survivors of E050 (H1 momentum 12-2, H5a industry momentum 12-1); research/phase6_redteam_e050.py; reports/E050_20260909T211001/redteam.json

Role: hostile reviewer. Every attack below is applied to the development segment only (1963-07..2017-12).

| Attack | H1 momentum (VW) | H5a industry momentum (VW) | Verdict |
| --- | --- | --- | --- |
| Microcap effect (equal-weighted vs value-weighted) | VW L/S 1.27%/mo (t 4.48) vs EW 0.95% (t 3.77): the effect is larger among large caps | VW 0.68% (t 3.64) vs EW-firm industries 0.94% (t 5.32): stronger with small firms, but VW passes on its own | Not a microcap artefact for either; industry momentum has a small-firm component to watch at stock level |
| One crisis: 2009 momentum crash | Calendar 2009 L/S sum -99.8% (arithmetic); long-only top decile -16.6% vs market; ex-2009 t rises to 6.07 | 2009 L/S -40.8%; long-only -17.8% vs market; ex-2009 t 4.35 | Survives statistically, but the crash is real and would destroy a leveraged or short-side implementation; long-only exposure loses about one sixth relative to the market in such a year |
| One crisis: 2000-2002 | ex-2000-02 t 4.33 | ex-2000-02 t 3.62 | Not dependent on the dot-com aftermath |
| One decade: rolling 120-month HAC t (annual steps, 46 windows) | min -0.20; 69% of windows above 2; 2% negative; the last five windows (ending 2013-2017) are 0.19, 0.21, 0.37, 0.43, 0.43 | min -0.34; 41% above 2; 2% negative; last five 0.12, 0.29, 0.39, 0.53, 0.35 | No decade is negative, but the most recent development decade is statistically silent for both. This is the biggest weakness |
| Worst/best 12 months share of total arithmetic L/S return | worst 12 = -37% of total; best 12 = +26% | -39% / +36% | Fat-tailed; the L/S series has an 81% (H1) / 54% (H5a) drawdown |
| Conditional on the prior 24-month market | after a negative 24-month market: t 0.57 (n 143); after positive: t 5.53 (n 511) | after bear t 0.35; after bull t 4.26 | The premium is a bull-regime phenomenon; crash risk lives in recoveries. Any deployable version needs a preregistered treatment of this (not a retrospective filter) |
| Long-only dependence on the market | top decile minus market: FF3 beta 0.05, SMB 0.39, HML -0.28, alpha t 5.0 | top-10 industries minus mean industry: beta -0.05, alpha t 4.2 | The long-only excess is not market beta; it carries a small-cap tilt (H1) and a growth tilt |
| Delisting omission | CRSP-based: stocks dropped at delist date with delisting returns per CRSP (French note) | same | Not applicable at this level; stock-level work must replicate the haircut rule |
| Survivorship | none (CRSP universe includes delisted) | none | Passed by construction of the source |
| Transaction costs, rebalance timing, universe selection, fractional rounding | not modelled | not modelled | Deferred to stock level; nothing here is a portfolio |

Assumption that, if slightly wrong, destroys the family: that the modern-era decay (2000-2017 t below 1 for both families) is noise around a persistent premium rather than the premium's disappearance. The development data cannot distinguish these. Stock-level work must show a positive post-2000 result after costs; if it does not, the family is WEAK_SIGNAL at best regardless of the 1963-1999 evidence.

## Part 2 - stock-level candidates

None exist yet (data purchase pending). This section will be written per candidate with the attack list of mandate section 56.


## Part 2 - stock-level trials of E051 (EODHD screening stage, 2026-09-12); reports/E051_20260911T233815, E051SENS_20260911T234807

Role: hostile reviewer of a NULL result. The question is no longer "is the strategy fake" but "is the rejection fake": could a real, deployable momentum premium be hidden by the data, the costs, the universe or the engine? Every attack is on development data only.

| Attack on the rejection | Evidence | Verdict |
| --- | --- | --- |
| Costs too harsh (20 bps per side plus FX) | Optimistic case (3 bps, no FX): 12-1 top-30 excess vs EW +3.5%/yr, t 0.47; best cell (vol-scaled) t 1.42; sector ETFs still negative | Costs are not the reason; the gross signal is absent after 1999 |
| Dollar-volume universe selects the speculative tail | E051SENS: rank cap 500 -> 12-1 t 0.39, vol-scaled t 1.49 with E3 +0.9%/yr and E4 +0.9%/yr; price floor USD 10 -> t 0.29 / 1.24 with E3/E4 about zero. Every variant earns its whole excess in 1998-1999 | The null does not depend on the tail; the post-2000 premium is zero on every universe cut |
| Delisting rule too punitive | all100 sensitivity changes the primary cell by 0.01 in t (few distress delistings among top-30 winners); all30 lowers every cell | The rule cannot be hiding a premium; a harsher rule makes it worse |
| Vendor data errors depress returns | First attempt was dominated by errors that INFLATED momentum scores; after I1-I5, 36 eligible name-months above +200% and 80 below -90% remain (real biotech and failure moves); benchmark CAGRs are consistent with SPY (EW top-1000 5.7% vs SPY 6.9% 1998-2017; PIT S&P 1500 EW 14.9% vs SPY 14.4% 2012-2017) | Residual errors are two-sided and small; no sign that the engine understates returns |
| Survivorship residue | EODHD's late-starting delisted histories were handled by starting Tier 2 in 1998 (rule A2); any residue would inflate, not depress, momentum | Cannot explain a null |
| Wrong benchmark | Versus SPY, the deployable alternative: 12-1 top-30 CAPM alpha -0.7%/yr (t -0.08) with beta 1.44; net CAGR 2000-2017 -7.4% vs SPY +5.6%; vol-scaled +6.4%/yr alpha, t 0.87, 2000-2017 CAGR 0.8% vs SPY 5.6% | Loses to the index fund on the modern window under either benchmark |
| Execution timing | Signal at the month-end close, fills at the next open, held open-to-open; no same-bar fills; tests assert the alignment | Not the cause |
| Sample too short or unlucky | 238 months, three eras; the 1998-1999 era is positive with t 3-6 in every cell and 2000-2017 is negative or zero in every cell; rolling 60-month excess positive in 19% of windows for the primary cell; last 36 months -11%/yr | Consistent with E050: the family-level VW premium is statistically silent after 2000 (t 0.6-0.7). A long-only concentrated version of a silent premium is negative after costs |
| Point-in-time corroboration | Tier 1 (S&P 1500, 2012-2017, 67 months, PIT_COVERAGE_GAP, SURVIVORSHIP_RESIDUAL flags): 12-1 top-30 14.5% vs EW 14.9% vs SPY 14.4%, t 0.06; residual -0.69; sector-neutral +0.88 (SECTOR_NOT_PIT) | The cleanest data agree with the null |
| Concentration / tails | Primary cell: 1999 = 71% of total net return, top-5 months 113%, worst 12 months -71%, max DD -88%; 2000-2002 -6/-39/-38%, 2008 -61%, 2009 -6% while the EW universe made +52% | Not a EUR 500 strategy under any reading |
| Sector exposure | Primary cell: XLK loading 0.99, XLP -0.56; R2 0.40; Tier 1 cell: XLV 0.66, XLY 0.74, XLP -0.79 | The long-only top-N is a sector bet, not stock selection |
| Feasibility | EUR 500 / N 30: USD 19 per position, typical trade USD 1.0 (at the Trading 212 minimum), cost USD 11/yr (1.9%); EUR 1,000: USD 39, trade USD 1.9 | Feasible only in the trivial sense; irrelevant given the null |
| Multiplicity | 24 trials: BH-FDR 0.05 passes none; deflated Sharpe probabilities 0.02-0.49 (Tier 1 0.81-0.91 on 67 months); 4 diagnostic cells add nothing | No survivor to deflate |

Assumption that, if wrong, would flip the decision: none found. The only way BUY_NORGATE becomes right is if EODHD's 1998-2017 liquid-universe prices were corrupted in a way that systematically destroys the top-momentum names' subsequent returns while leaving benchmarks intact. The integrity rules, the benchmark reconciliation against SPY, the Tier 1 replication on the point-in-time universe, and the agreement with the survivorship-free French library (post-2000 t below 1) all argue against that.

What Norgate would and would not change: it would extend the survivorship-safe window to 1990-1997 (where the French library says momentum worked) and supply point-in-time Russell membership and historical market cap. It cannot change 2000-2017, which is the window a EUR 500-1,000 account has to live in and where every cut of the data says the long-only top-N premium is zero after costs. Spending USD 346.50 to document a premium that ended in 1999 is not a research purchase.

Closing classification: Family A (stock momentum) and Family B (residual momentum) at stock level: REJECTED_DECAY (strong 1998-1999, zero 2000-2017); Family F at ETF level: REJECTED; Tier 1 sector-neutral: WEAK diagnostic only (t 0.88 on 67 months, sector labels not point-in-time).


## Part 3 - Phase 6B allocation overlays (E053 survivors G1a, G3, G4, G5); reports/E053RT_20260912T110504

Role: hostile reviewer of the only architectures that passed a Phase 6B gate. Development data only.

| Attack | Result | Verdict |
| --- | --- | --- |
| One crisis drives everything | start-year table: every start year from 2009 to 2012 underperforms SPY (G1a 9.5-11.0 vs 13.3-16.6; G3 11.8-13.7 vs 13.3-16.6); 2004-2017 outperformance exists only because 2008 is inside the window | The excess return is one event; the drawdown reduction is real but not free |
| Long history | 1994-2017 with a T-bill cash leg: absolute momentum 10.5 vs 9.4, SMA10 9.9 vs 9.4, alpha t 1.9, drawdown -17 vs -51; beats SPY in 4-5 of 24 calendar years; vol-managed 7.4 vs 8.6 | Two bear markets (2000-02, 2008) pay for 20 years of small losses; consistent with E050 H6 (WEAK_SIGNAL over 1963-2017) |
| Parameter fragility | absolute momentum 6/9/12 months: 8.7 / 6.9 / 9.1; SMA 8/10/12: 11.0 / 9.3 / 8.9; vol 21/63/126: 9.5 / 9.5 / 8.9 | The 9-month cell loses 2 points; the best SMA cell is a neighbour (selection risk); vol windows stable |
| Execution delay of one month | absolute momentum unchanged (9.4); SMA10 8.2 (from 9.3); vol 8.3 (from 9.5) | SMA and vol rules depend on prompt execution; absolute momentum does not |
| Stress costs (30 bps) | negligible (turnover 0.7-1.0x/yr) | Costs are not the issue |
| Bond-leg dependence | G3 with cash instead of IEF underperforms SPY over 1996-2017; the 2008-2017 Treasury rally is inside every IEF window | A rate-rising regime removes part of the overlay benefit; the 2022 holdout is exactly such a regime and is untouched |
| Deployability | UCITS lines exist for SPY (CSPX/VUSA) and 7-10y Treasuries; one to two switches a year; EUR 500 feasible; monthly checking is required | Deployable, but the 2020 crash (validation segment) is the known failure mode of monthly rules |
| Multiplicity | six E053 cells: BH-FDR passes only the static 60/30/10 mix (alpha from diversification) | No signal-based cell survives multiplicity |

Assumption that, if wrong, flips the reading: none flips it to a return-premium strategy. What would make the overlay worth validating is a demonstration that it adds return, not only reduces drawdown, in a window without a prolonged bear market; the data say the opposite (2009-2017). Classification RISK_OVERLAY (WEAK_SIGNAL); no validation.


## Part 4 - Phase 7A null results (E055, E056, E057); reports/E055_20260912T133139, E056_20260912T133249, E057_20260912T133643

Role: hostile reviewer of the rejections. Could a real long-only effect be hidden?

| Attack on the rejection | Evidence | Verdict |
| --- | --- | --- |
| Costs hide the low-risk premium | E057 optimistic case (3 bps): excess vs EW +0.1 to +0.9%/yr, t <= 0.2; base case -0.4 to -1.3; the gross decile (+4.9%/yr) shrinks to zero when concentrated to 30-50 names before any cost | Construction, not costs |
| Wrong benchmark | versus SPY: 2000-2017 CAGR 7.9-8.6 vs 5.6 (bear markets), 2010-2017 12.1-13.5 vs 14.4, beta 0.5, alpha t 0.95-1.29 | Loses to the index fund in the modern bull market; wins only through 2000-02 and 2008 |
| Delisting rule | base and all100 identical; all30 destroys every cell (-5 to -9%/yr) because low-risk portfolios are full of ACQUIRED names (takeover premiums, not distress) - a known limitation of that sensitivity, recorded | The base rule is the right one here; the sensitivity is uninformative for this family |
| Index events need announcement dates | true: only effective dates exist; the pre-effective run-up is unobservable and untradeable for us; post-effective returns are what a Trading 212 account can trade, and they are negative for every event class | The tradable part of the index effect is negative |
| Deletions rebound (P1 +38%/yr) | one year (2016, +283%) on distressed energy/mining names; negative in 5 of 6 years; median 6-month CAR -12.6%; 12-month CAR -37% | Lottery, not reversal |
| Overnight/intraday wrong signs are a data artefact | decile monotonicity is strong (rho -0.75 for intraday); the low-intraday/high-overnight deciles are the gap-up speculative names that the MAX/volatility screens also flag; consistent across 2000-2017 and 2010-2017 | A real property of this universe, but it is the short side of the volatility effect, not a long-only signal |
| 52-week high is momentum in disguise | +2%/yr 2010-2017 on Tier 2 (t 0.8), -2.2%/yr on Tier 1; rho 0.37 | Weak and inconsistent, and it belongs to a closed family |
| Liquidity within the top-1000 | 2000-2017 +3.5%/yr t 3.1 but 2010-2017 +1.3%/yr; the Tier 1 +5%/yr (t 2.2) is the S&P 600 vs 500 small-cap run of 2016-2017 | Below the bar; small-cap timing risk |
| Multiplicity | 24 Phase 7A trials: BH-FDR passes none; DSR 0.77-0.97 on cells that fail the economic gates anyway | No survivor to deflate |

Assumption that, if wrong, would flip the outcome: that the equal-weight top-1000-by-dollar-volume universe and SPY are the right yardsticks for a EUR 500-1,000 account. If the user's objective were "index-like return with lower drawdown" rather than "beat the index", the low-risk top-50 quarterly portfolio (net CAGR 6.8% vs SPY 6.9% 1998-2017, DD -40 vs -51, beta 0.55, 2.6x turnover, EUR 6/yr of costs at EUR 500) and USMV-type ETFs would be the deployable expression. That is a preference, not evidence of alpha.
