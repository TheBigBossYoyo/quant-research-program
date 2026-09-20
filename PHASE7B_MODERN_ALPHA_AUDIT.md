# PHASE7B_MODERN_ALPHA_AUDIT - modern alpha and data-source selection (2026-09-12; audit only, no backtests, no locked data read, nothing purchased)

## 0. Accepted starting point

Closed by the persisted record (479 cells, E001-E057): classical/residual/sector momentum; every price-only OHLCV mechanism on the EODHD equity data (Phases 6-7A); crypto price/microstructure (Phases 1-5); low-volatility and trend/allocation overlays as return engines; Norgate; the EODHD subscriptions unless a specific reason appears. The program needs a genuinely new information source with causal, point-in-time timestamps, modern (post-2010) economic plausibility, long-only compatibility, low turnover, and a EUR 500-1,000 entry ticket.

## 1. Method of this audit

For each information family: (a) what the published record says about post-2010 profitability, weighted towards replication studies rather than original papers; (b) whether a point-in-time, causally timestamped data set exists that a retail researcher can obtain legally at zero or low cost (facts verified on 2026-09-12, PHASE7B_DATA_SOURCE_SELECTION.md); (c) whether the informative side of the signal is the LONG side; (d) the turnover an honest implementation needs at Trading 212 costs (20 bps per side including FX under automated execution; 3-5 bps with a manually funded USD balance); (e) effort and suitability as a university-grade project. Scores are qualitative (HIGH / MEDIUM / LOW) and every LOW is a reason, not a dismissal.

## 2. Priority area A - earnings and analyst information

| Sub-family | Post-2010 evidence | Point-in-time data available to this project | Long-only fit | Turnover | Verdict |
| --- | --- | --- | --- | --- | --- |
| Earnings surprise / SUE / PEAD (drift after announcements) | Martineau (Critical Finance Review 2022, "Rest in Peace Post-Earnings Announcement Drift"): prices fully reflect surprises on the announcement day; PEAD absent in large stocks since 2006 and recently gone in microcaps. Replication databases (Chen-Zimmermann; Jensen-Kelly-Pedersen) show anomaly returns roughly halved after publication | SUE from a seasonal random walk: FREE and point-in-time from SEC XBRL company facts (filed dates from 2009; frames of about 2,700 entities per quarter verified) plus announcement timestamps from 8-K Item 2.02 acceptance times (verified in the submissions API). Analyst-consensus SUE: EODHD Fundamentals USD 59.99/month (Earnings::History has epsActual, epsEstimate, surprisePercent, reportDate) | good (buy positive surprises) | quarterly re-sort, moderate | LOW as a return engine: the drift the strategy would harvest is the part the literature says is gone. Worth one cheap falsification on the free data inside a broader event program, not a phase of its own |
| Analyst EPS revisions, target-price and recommendation revisions, revision breadth, dispersion, "earnings momentum" combinations | Post-forecast-revision drift still documented in accounting journals (Chen 2020 JBFA) but with the same post-publication decay as other characteristics; the effect is strongest in the short horizon and in less-covered names | Requires a monthly history of consensus snapshots. I/B/E/S is institutional (WRDS), not accessible. Retail vendors: EODHD Trend section is CURRENT estimates only (no history of consensus); FMP and Finnhub sell upgrade/downgrade and price-target event histories with dates (USD 29-79/month, pricing pages not machine-readable on 2026-09-12; PIT quality of consensus snapshots UNVERIFIED) | good | monthly, moderate | MEDIUM evidence, POOR data: no audited point-in-time consensus history exists at retail prices. Not selectable now; recorded as the one family where NEW_DATA_SOURCE_JUSTIFIED could apply if a vendor documents historical consensus snapshots with as-of dates within budget |
| Earnings-announcement premium (hold announcers through their announcement month; Frazzini-Lamont) | persistent in several samples through the 2010s, but it is a premium for bearing announcement risk | announcement dates FREE from EDGAR (8-K 2.02 timestamps; 10-Q filing dates) | good | very high (near-complete monthly rotation) | LOW for this account: turnover x FX cost consumes the premium under automated execution |

Conclusion for area A: the free EDGAR data make the earnings channel testable at zero cost, but the modern record says the tradable part (drift) is dead. Analyst-revision data are the genuinely missing input, and no point-in-time retail source under EUR 50/month was found.

## 3. Other genuinely distinct information families

| Family | Post-2010 evidence | Data (verified) | Long-only fit | Turnover | Verdict |
| --- | --- | --- | --- | --- | --- |
| B. Insider transactions (Form 4 purchases; clustering, opportunistic vs routine insiders) | Purchases remain informative in recent samples: a 2024 filing-date event study reports SPY-adjusted CARs of +0.5% next session and +1.0% over five sessions (t 5-6) with confidence intervals including zero by 63 sessions; the long-horizon literature (Cohen-Malloy-Pomorski 2012; Ali-Hirshleifer 2017) locates the durable part in small/mid caps and in non-routine trades; Brochet (2010) documents larger announcement returns after Sarbanes-Oxley's two-day filing rule | FREE, point-in-time: SEC Insider Transactions Data Sets (Forms 3/4/5, as-filed, 2006-2026 Q2, quarterly zips) and live Form 4 via EDGAR; filing acceptance timestamps give the causal information date | EXCELLENT: purchases (not sales) carry the information, so the long side is the informative side | low to moderate (hold 3-12 months after a purchase cluster) | HIGH: new information (private information of insiders), free PIT data, long-only by nature, modern evidence positive though modest and horizon-dependent |
| C. Fundamentals from XBRL: profitability, investment/asset growth, net issuance, accruals (quality family) | Phase 6B family-level (French, value-weighted, long-only vs market): +0.3 / +0.5 / +0.3 percent a year in 2010-2017 (profitability / investment / net issuance); positive sign but small; long/short factors larger | FREE, point-in-time: SEC Financial Statement Data Sets (all XBRL filers, 2009-2026 Q2) and company facts API with filed dates | good | very low (annual/quarterly) | MEDIUM as a conditioning layer, LOW as a stand-alone engine at this capital; the natural filter for family B (insider buying at profitable, non-issuing firms) |
| D. Corporate events from 8-K text: open-market repurchase authorisations, spin-offs, dividend initiations | buyback-announcement long-run drift persists in international and post-2000 US samples (Manconi-Peyer-Vermaelen 2019); undervaluation-index conditioning (Ikenberry-Vermaelen) strengthens it | FREE: EDGAR full-text search returns JSON with form, file date, CIK and items for 8-K filings (verified: 175 hits for "share repurchase program" in January 2015 alone); requires text classification of announcements versus executions | good (announcements are the long signal) | low (6-12 month holds) | MEDIUM-HIGH: distinct information (management signalling), free PIT data, moderate parsing effort; second event family for the same program |
| E. Short interest (FINRA/exchange semi-monthly) | robust on the SHORT side; long side (low short interest) weak and mostly a size/quality proxy | free downloads exist (history depth per venue UNVERIFIED) | poor | low | LOW for long-only |
| F. Institutional holdings (13F, 45-day lag) | crowding and "smart money" measures weak after 2010 | free (EDGAR structured 13F data since 2013) | fair | quarterly | LOW |
| G. Text of filings ("lazy prices": changes in 10-K/10-Q language; 8-K tone; earnings-call transcripts) | Cohen-Malloy-Nguyen (2020): changers underperform; effect mostly short-side; modern LLM-based headline studies find short-horizon predictability | filings FREE and point-in-time from EDGAR; transcripts paid | poor to fair (long non-changers earn market-like returns) | low | MEDIUM evidence, HIGH effort, short-side payoff: a strong second-year academic extension, not the first deployable direction |
| H. Options-implied information (skew, implied-realised spread, put-call) | robust in the literature, mostly short horizon | paid options data (OptionMetrics institutional; retail vendors expensive) | fair | high | LOW for this budget and turnover |
| I. Macro/regime and ETF-flow timing | closed as return engines (Phases 6B/7A) | - | - | - | CLOSED |
| J. Alternative data (web traffic, app usage, job postings, satellite) | some evidence, decays quickly, crowded | not legally obtainable at this budget | - | - | LOW |

## 4. Ranking on the user's criteria

| Rank | Direction | Information novelty | Modern evidence | PIT data cost | Long-only | Turnover | Effort | Project quality |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Insider purchases (B) with quality conditioning (C) | new (private information) | positive, modest, horizon-dependent | zero (SEC) | native | low-moderate | moderate | high: clean causal question, honest null possible |
| 2 | Repurchase-announcement drift (D) with (C) | new (management signalling) | positive in recent samples, smaller in US | zero (SEC FTS) | native | low | moderate-high (text) | high |
| 3 | Quality/profitability tilt (C) alone | new source, old idea | weakly positive | zero | native | very low | low | medium (likely index-like result) |
| 4 | Analyst revisions (A2) | new | decayed but present | not available PIT at retail | good | moderate | low once data exist | high, blocked by data |
| 5 | SUE/PEAD (A1) | new source, old idea | dead in large caps | zero | good | moderate | low | low expected value; one cheap falsification only |
| 6 | Filing-text changes (G) | new | mostly short side | zero | poor | low | high | high as an extension |

## 5. The single highest-value next direction

**An SEC-EDGAR event-driven, long-only research program anchored on insider purchases, with XBRL profitability/issuance as the conditioning layer and repurchase announcements as the second event family.**

Why this and not the earnings/analyst area first:
1. It is a genuinely new information set, not a transformation of prices: Form 4 purchases are private-information trades by the people who run the firm; repurchase authorisations are management signals; both are dated to the minute by EDGAR acceptance timestamps.
2. The data are free, complete for the whole research design and already legal to hold: insiders 2006-2026 Q2, financial statements 2009-2026 Q2, full-text 8-K search from 2001. Development 2009-2017, validation 2018-2021 and the 2022-2026 holdout are all covered without any purchase, and the EODHD price snapshots on disk run to 2026-09-11, so the price side of validation and holdout is also already in hand (locked, unread).
3. The informative side is the long side. Every family closed so far failed partly because the long-only account cannot hold the short leg where the anomaly lives; insider purchases and buyback announcements are the exceptions.
4. Turnover is naturally low (event-driven entries, 3-12 month holds) and the number of positions is small, which is what EUR 500-1,000 at Trading 212 can execute.
5. It is a proper research question with a possible null: "Do insider purchases still predict returns for a long-only retail investor after 2010, after costs, and after conditioning out size and quality?" The 2024 evidence says yes at five days and maybe not at three months; whether a monthly or weekly retail implementation can capture anything is exactly what the program should measure.
6. The earnings channel is not abandoned: SUE and announcement timing come for free from the same source and enter as one preregistered falsification cell and as a conditioning variable, not as the thesis.

## 6. Red team of the recommendation (what could make it worthless)

- Horizon mismatch: if the informative part of insider purchases lives in the first five sessions, a monthly rebalance captures little; a weekly rebalance under automated FX costs (30 bps round trip) may eat it. Mitigation to preregister: weekly signal check with entries only on new clusters, holding period 3-6 months, USD-balance execution assumed in the base cost case with the automated case as stress.
- Small-cap concentration: the durable part of the effect sits in small and mid caps with wider spreads; the E051 stress costs (45 bps for ranks 501-1000) must apply, and names below the liquidity floor are excluded.
- Filing-data quality: SEC extracts are "as filed" with errors; a reconciliation test against known transactions and a duplicate/amendment (Form 4/A) rule are mandatory before any return is computed.
- Crowding: insider-purchase screens are widely followed; expect a smaller premium than in 2000s samples and a faster announcement reaction; the preregistered gates must demand a positive 2013-2017 result, not a 2009-2012 one.
- Repurchase text: distinguishing new authorisations from routine progress updates and from ASR executions needs a classifier validated on a hand-labelled sample; misclassification dilutes the signal towards zero, it does not create a false positive.

## 7. Draft Phase 8 preregistration outline (NOT run; to be finalised before any computation)

- Data acquisition: SEC Insider Transactions Data Sets 2006-2026 Q2 (quarterly zips, hashed); Financial Statement Data Sets 2009-2026 Q2 (hashed); EDGAR submissions API for CIK-ticker mapping and 8-K item codes; full-text search for repurchase announcements. All acquisitions logged as ENV items; no purchase.
- Universe and prices: existing lock-enforced EODHD panels (development through 2017-12-31); CIK-to-ticker mapping validated on the S&P 1500 point-in-time lists; liquidity filters as E051.
- E058 (insider purchases): event study of open-market purchases (transaction code P) by officers/directors/10 percent owners, filed within the two-day rule; clusters (>= 2 insiders in 30 days) versus single trades; opportunistic versus routine (no purchase in the same calendar month in the prior two years); CARs at +5, +21, +63, +126, +252 sessions versus the EW eligible universe; calendar-time long-only portfolios entered at the open after the filing acceptance time, held 6 months, weekly and monthly checks; three cost cases; gates: 2013-2017 net excess vs the EW universe >= +3%/yr with HAC t >= 2, positive in >= 4 of 5 years, alpha vs SPY t >= 1.5, drawdown gate as E051; multiplicity across all Phase 8 cells.
- E059 (repurchase announcements): classifier validation on 200 hand-labelled 8-Ks; calendar-time long-only portfolio, 12-month holds; same gates.
- E060 (conditioning): E058 entries filtered by XBRL operating profitability above the eligible median and net issuance <= 0; counted as cells.
- E061 (falsification of the earnings channel on the free data): SUE deciles from XBRL with 8-K 2.02 timing; expected to fail per Martineau; one cell.
- Outcome vocabulary: PROMISING_CANDIDATE_READY_FOR_VALIDATION only after a frozen architecture passes all gates and the red team; otherwise the program records the null and the direction is closed.

## 8. Subscription decision

Nothing in the recommended direction needs a live EODHD feed: prices to 2026-09-11 for every US common stock and the point-in-time S&P lists are on disk and hashed, and the new information source is free. Recommendation unchanged: cancel both EODHD subscriptions before renewal. If Phase 8 reaches paper trading, current prices for a handful of holdings come from the broker itself; a one-month USD 19.99 re-subscription refreshes the research panel if ever needed.

## 9. Phase 7B outcome

Direction selected: EDGAR event-driven long-only program (insider purchases primary; repurchase announcements secondary; XBRL quality conditioning; earnings channel as a falsification cell). Data source selected: SEC EDGAR (free). Analyst-revision data recorded as the only family where a paid point-in-time source would be justified if one within budget is ever documented (none found on 2026-09-12). No backtest was run; no locked segment was read; nothing was purchased.
