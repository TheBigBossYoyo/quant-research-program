# Research journal

## Continuation — Claude Code handoff, E012 flow preregistration

Resumed from disk: STATUS/PLAN/EXPERIMENTS/journal read, protocol read in full, 33 tests pass, 119 hypotheses on record, no candidate, validation/final closed. State on disk matched the handoff message.

Before writing any flow code, noticed that E001 already recorded one-bar spot flow ICs: negative at 5m–4h (reversal), positive at daily, but the spot screen traded only the continuation direction long/cash. That is prior evidence, not a result of this branch, and it argues that the perpetual flow test must register both directions and must be judged against taker costs, since a reversal capture with taker orders is structurally a paid-spread trade. Preregistered E012 as 18 IC cells / 36 directional hypotheses with a statistical Stage-1 gate before any ledger run, to keep the branch from becoming a parameter sweep. Cumulative count becomes 155 regardless of how many cells advance.

## Continuation — economic audit and risk-control correction

Previous turn classified as progress: verified E008/results/source snapshot on disk. AGENTS and full protocol hashes match the already-read checkpoint; no new agent instructions appeared. Account-specific values still unavailable, but calling all research blocked was too broad. Corrected that framing and executed E009 independently.

A collateral halt could be overwritten by an ordinary trim after an untradable observation and recovered mark. Reproduced in a failing regression, fixed with a latched halt, verified28 tests and identical historical return ledgers. This is a real safety correction even though the historical path did not trigger it. Intrahour margin survival and production recovery remain unproved.

FRED historical USD/GBP and three-month Treasury yield references show an economic weakness: carry2.11% versus4.26% rate-accrual opportunity-cost proxy, and conditional GBP volatility9.29%/DD17.72%. Do not claim the proxy is a realizable return or USD neutrality is GBP neutrality. ETH carry is now lower priority and rejected for promotion; a positive mean against0USDT cash does not establish a compelling capital allocation.

Next independent branch: a bounded directional-perpetual screen on existing development data with actual signed inventory/funding accounting and published futures transaction costs. This is a distinct market/cost model, not a silent reinterpretation of failed spot tests. No need for user credentials to falsify it; maintain account-dependent gates and locked validation/final data.

Executed that branch as E010/E011. Corrected a new zero-volume-fill defect before accepting screen results; first run retained as superseded.36 configurations plus six baselines across three costs: all24 hourly/four-hour configurations negative at base cost, daily ETH momentum48 sole cheap survivor. Its39% stressed DD, weak Sharpe, failed uncertainty and loss of nearly all return with one extra-day delay reject promotion. No2025/2026 data used.33 tests pass. Total hypotheses119. Next distinct mechanism is aggressive-flow information from existing perpetual taker volumes; do not invent an optimized regime to rescue this trailing-return family.

E012 executed after 40 tests passed (seven new flow tests: imbalance formula, prefix invariance, forward-return alignment, causal trailing-quantile rule, complete-bucket invalidation, bootstrap sign/seed). Result: the hourly aggressive-flow reversal is statistically robust (four Bonferroni-surviving cells, negative every year, both assets, consistent with the E001 spot ICs) but economically empty for a taker: the predictable move is on the order of one basis point against a 14 bps round trip, and even fee-only ledgers lost 41–57% a year with 80–92% drawdowns. Interpretation: this is the compensation passive liquidity providers earn for absorbing aggressive flow, which a retail taker on Binance cannot collect; queue-position or maker-fill claims would need book data we do not have and could not verify. Rejected, cumulative 159. Nothing about this should be retuned.

Next distinct mechanism chosen on priority, not on any peek at results: positioning state from funding and basis (E013). It is the one direction in CLAUDE.md's list that uses only data already on disk, has a plausible counterparty (leveraged longs paying for exposure), and naturally operates at 8-hour/daily frequency where turnover costs are not automatically fatal. Cross-asset lead-lag between BTC and ETH and intraday/funding-time seasonality remain queued behind it; cross-sectional relative value needs a broader survivorship-aware universe and is deferred until public acquisition is justified.

E013 executed: all 16 funding/basis cells carry the contrarian sign but none survives the multiplicity-adjusted gate on 3285 eight-hour or 1093 daily observations. That is what a small true effect looks like in a two-asset sample, and also what noise looks like; the preregistered rule says reject, so it is rejected (191 cumulative). The fade to zero in 2024 for both assets is a warning against reading the 2022–2023 sign as a stable mechanism.

Program-level observation after E001–E013: on two mega-cap assets, every short-horizon effect is cost-dominated and every daily effect is under-powered. Two-asset timing ideas still queued (BTC/ETH lead-lag, intraday/funding-time seasonality) share the same structural problem: they need either a round trip per hour at 14 bps or a daily sample of about 1100 observations. Lead-lag between the two most liquid contracts has the weakest prior of all. The highest-value move is to widen the universe with a survivorship-aware public archive so that cross-sectional mechanisms (relative momentum/reversal, funding-dispersion carry, cross-sectional positioning) can be tested with N × T observations and market-neutral construction. Verified 2026-09-08 that data.binance.vision answers public GET requests from this environment; no credentials involved.

E014 preregistered before the universe download finished, so no hypothesis choice can be influenced by the new data. The liquidity threshold (20M USDT trailing median quote volume), quintile width, weekly cadence and one-day latency were fixed here. The eight hypotheses are counted now (cumulative 199) regardless of which pass the Stage-1 gate. Costs are widened to 7/14/28 bps because alt perpetual spreads are wider than BTC/ETH and uncalibrated; if a result depends on the base case only, that is a weakness, not a finding.

E014 executed on the 393-symbol survivorship-aware universe: no feature passed the 0.05/4 gate at 147 weeks. The failure mode is power, not sign instability: 30-day cross-sectional reversal is negative in every year and 7-day relative flow continuation positive in every year, with the flow IC growing to +0.05 at a four-week horizon. Funding dispersion flipped sign across years and is the weakest. The equal-weight alt baseline lost 18% a year with 78% drawdown, a reminder that long-only alt exposure is not a benchmark anyone should want.

Decision: extend the development sample backward to 2020 for the same cells rather than touch any parameter, and count the rerun (207 cumulative). I considered lowering the liquidity threshold or rebalancing daily to gain observations; both are retunes that manufacture significance and were not preregistered, so they are not done. A data defect (taker volume above total volume on two dates) was quarantined at the field level rather than dropped, so price-based cells are unaffected and the flow cell loses only the affected symbol-weeks.

E016 produced the first survivor of a cheap screen with real economics: cross-sectional continuation of 7-day relative taker flow on the perpetual universe, 35% stressed CAGR, Sharpe 1.3, 26% drawdown, insensitive to an extra day of delay. The E015 audit rejects it for promotion under the preregistered 207-trial bound, and I am not softening that bound after the fact. Hostile reading of the same numbers: the 2020 IC of 0.17 against 0.005 in 2021 and 2023, 59x annual turnover, gross drifting to 1.46x, and a 28 bps case whose ordinary interval reaches zero. The mechanism is plausible (relative aggressive demand across coins persists for weeks, unlike the single-asset hourly reversal in E012), but a first survivor after 207 trials is exactly where a false positive would appear. Preregistered E017 to attack it from seven directions and to test two slower-rebalance variants openly counted as hypotheses. Validation remains closed; no capital.

E017 is the most informative result of the session. The placebo proves the flow rank carries genuine cross-sectional information (0 of 200 permutations come close), yet the economics collapse under every other cut: post-2020 the excess return is not distinguishable from zero, ten names carry more than the entire price P&L, the short leg loses steadily, and liquid names lost money in 2020 while illiquid ones drove the +174%. That combination — real signal, unstable and concentrated payoff — is what an attention effect in a thin 2020 alt universe should look like, and it is not a strategy. The 14-day variant coming within a hair of the 209-trial bound is exactly the kind of near-miss that invites retuning; it is recorded and left alone.

Lesson for the gates: the E017 items (start-year robustness, name concentration, placebo, legs, liquidity split) caught what the bootstrap bound alone would have described only as "insufficient evidence". They are now mandatory for every future survivor. Next: risk and attention characteristics on the same universe (E018), a different economic family, before considering anything outside crypto perpetuals.

E018 gave a textbook illustration of why rank statistics are not returns: the low-volatility rank effect is the strongest IC of the whole program (t -4.5) and the corresponding spread portfolio loses money, because shorting the high-volatility quintile means being short the coins that occasionally multiply. Recorded and rejected without touching the construction. The cross-sectional characteristic space on this universe is now essentially exhausted; combining insignificant characteristics with a model would be fitting noise. E019 turns the universe into a timing information set for BTC (aggregate funding, breadth), which is the last cheap distinct crypto mechanism I can see with data on disk. If it fails, the next branch is outside crypto: slower Trading 212-compatible ETF mechanisms, which need a new survivorship-aware data path and are a larger investment.

E019 rejected: aggregate funding and breadth tell BTC nothing at a weekly horizon. That closes the crypto search on the data available: eleven economic families, 219 counted hypotheses, one survivor that died under hostile audit. Continuing to mine the same panel would be exactly the behaviour the protocol forbids. Moving to the Trading 212 ETF branch, but only after checking (ENV004) that the account constraints are verifiable from official pages and that a free, adequately survivorship-aware daily data path exists; if either fails, the honest conclusion is that no qualifying strategy has been found with the resources available.

ETF branch opened. This is deliberately classical (trend and momentum on broad ETFs, monthly) because the account is long-only and unlevered and the capital is small; the point is not to find something exotic but to test whether the best-documented slow mechanisms survive realistic Trading 212 economics on a GBP account. Power is the known problem: ten development years at monthly cadence. The validation split for this branch (2020–2024) is set before any return is seen and includes the COVID crash and the 2022 bond drawdown, so a candidate that only works in the calm 2010s will fail there. yfinance is the only workable free path; its lack of checksums is mitigated by hashing every raw file at retrieval.

E020 rejected at the cheap screen: on 2009–2019 the classical trend and momentum rules on GBP ETFs lag equal weight on every metric, and the preregistered rule does not let a failed development candidate peek at 2020–2024. Honest note: the development decade is the single worst environment for trend rules; a different split would likely have flattered them, which is exactly why the split was fixed first.

Before writing the exhaustion conclusion I am running the three cheap crypto items I had deprioritized on priors (session/funding-hour seasonality, BTC/ETH lead-lag, 90-day cross-sectional momentum), each preregistered and counted, so that the conclusion rests on tests rather than on my expectations. If all three fail, condition B of the continuation contract is met for the data and venues available: further search would be duplicative or a disguised sweep.

E021–E023 rejected as expected, and now on evidence rather than prior. The recurring pattern of the whole program is worth stating plainly: the statistically robust effects on Binance (hourly flow and cross-asset reversal, cross-sectional flow rank, the low-volatility rank) are all either liquidity-provision premia that a taker cannot collect, or rank effects whose dollar payoff is concentrated in tails, thin years and a few names. The slow, executable mechanisms (carry, ETF trend/momentum) are real but do not beat the relevant passive or cash alternatives after costs and opportunity cost. I am concluding the session under condition B and leaving an explicit list of what new data or facts would reopen the search.

## Phase 3 close — 2026-09-09

Ten experiments in one day, and the shape of the answer is the same as in the earlier phases with one difference: the slow-trend and compression-breakout mechanisms on BTC/ETH perpetuals are real, low-beta and complementary, and their combination is the first thing in this project with development Sharpe above one, positive alpha over buy-and-hold and a tolerable drawdown. It still fails the preregistered gates, mostly because the search that found it was wide and the sample is five years of mostly rising prices. I have written that down rather than talked myself into it. Relative strength on liquid names, regime-gated mean reversion, pullbacks, every indicator ablation and a regularized stack all rejected. The honest next step is not another crypto family; it is either a further independent development regime for the frozen E040 rule or a different asset class with auditable data.

## E035 — 2026-09-09

The unselected version answers the question E034 left open: most of what made the best slow-trend cells look strong was picking them. Averaged over the whole preregistered neighbourhood, the rule is a Sharpe-one, low-beta trend exposure that a simple volatility-managed long position matches in six of eight cells, with alpha indistinguishable from zero in six of eight. That is a useful negative and it is recorded as WEAK_SIGNAL. The pullback, RSI and multi-timeframe-trigger ideas were rejected outright in E033. Next: relative strength restricted to liquid names with an absolute overlay (E036), then regime-conditioned mean reversion at 1h–4h.

## E034 — 2026-09-09

The slow-trend cells have real alpha over buy-and-hold with low beta, and they do not survive the honest multiplicity correction: the spread of outcomes across the 120 cells is wide enough that the best one is roughly what luck would deliver. Both statements are true at once, and the way through is not to argue about N but to remove the selection: E035 uses the whole preregistered neighbourhood as one unselected rule. If that rule clears the gates, it is frozen and validated once on 2025; if not, the family is a documented weak, low-beta trend component and nothing more.

## E032 — 2026-09-09

The first Phase 3 family produced what the microstructure branches never did: many configurations that clear stressed costs with Sharpe above one and drawdowns half those of buy-and-hold, with plateaus and low overfitting probability. Two facts keep this honest. Buy-and-hold on these windows has Sharpe 0.9–1.2, so a slow-trend rule on a bull-biased asset can look excellent while adding no alpha, only better timing of the same beta; and the walk-forward efficiency of parameter selection is mostly below 0.6. The preregistered audit (E034) asks the only question that matters: is there an intercept over buy-and-hold, and does the deflated Sharpe survive when the trial variance is measured rather than assumed? Supertrend added nothing over moving averages, which is what one expects from two smoothings of the same state.

## Phase 3 start — 2026-09-09

Audit of what was executed versus mentioned: the classical systematic architectures (MA trend systems with stops and sizing, Supertrend, Donchian breakouts, pullback-with-trend, multi-timeframe, regime-conditioned mean reversion, liquid relative strength) were never run as architectures; Phase 1 only used a 20-bar SMA displacement as a baseline and trailing-return signs, and Phase 2 was microstructure. PHASE3_RESEARCH_MAP.md records this. The statistical change is real and must not become a loophole: hypotheses are still counted, architectures are FDR-controlled within a family and deflated by the trial count, and parameters are judged by plateaus, PBO and walk-forward rather than by counting EMA(199) against EMA(200). Longer history matters for trend systems, so spot hourly bars from 2017 and perpetual hourly bars from 2020 are being acquired before anything is run.

## Phase 2 close — 2026-09-08

Implied volatility was the last free information set with adequate length, and it behaves like everything else: the minute-scale shock effect is real-looking and worth four basis points, the daily premium effects are large and unmeasurable on eighteen months. Phase 2 therefore ends where the mandate says it may: the new information was created, it revealed predictors the old data could not see, and none of them survives execution. The honest reopening conditions are narrow and written in the conclusion report: longer option history, a liquidation feed, or an account that can earn maker rebates or trade at institutional fees — none of which is a research decision I can take.

## Closing the taker microstructure frontier; opening volatility information — 2026-09-08

I wrote the cost arithmetic into the registry so that the closure does not rest on my judgement: at 30 minutes a taker needs an IC near 0.2 and the best measured is 0.06. The only remaining microstructure question is E030's optimistic fill bound, running now. The next information set is options-implied volatility, which Binance publishes as a per-second index; it is causally timestamped, cheap (about half a gigabyte), and carries information no prior data had. Preregistered as E031 before any of it is analysed.

## E027 and E029 — 2026-09-08

The passive test is the most instructive Phase 2 result: under a fill rule that requires the price to trade through the order, the depth-cushion signal halves adverse selection and still loses seven basis points per fill, on a five to six percent fill rate. That is what liquidity provision looks like without queue priority. The positioning ratios add nothing beyond the taker ratio, which is the same reversal already measured three ways. One bounding test remains (optimistic touch fills, E030) to close the passive route on evidence rather than argument; then the microstructure frontier is exhausted for taker-executable horizons, and I will state the arithmetic reason in the registry.

## E028 result — 2026-09-08

Spot/perpetual synchronization is a dead information layer for this account: basis dislocations are corrected within a fraction of a basis point and spot flow only echoes the reversal already seen in perpetual flow. Every microstructure predictor so far shares one property — real, stable, tiny. The remaining on-disk information not yet used is the positioning content of the metrics feed (top-trader and global long/short account ratios, taker buy/sell ratio), tested next at 15–60 minutes (E029). bookTicker touch-level state is deprioritized with a written reason: the 1% depth imbalance already carries the largest microstructure IC and yields at most two basis points at executable horizons; the touch-level version decays faster, so at 28 GB of download its expected information gain is below any other option.

## E026 and the next expansion — 2026-09-08

E026 confirms the pattern: the depth cushion predicts direction for hours (IC about 0.05 at two hours) with a payoff of one or two basis points. E027 (passive trade-through capture) is the last legitimate test of that layer. Independently of its result, the next information set is synchronized spot trades: ENV006 downloads spot aggTrades for the same 194 days so basis dislocation and cross-venue flow can be tested at second-level alignment (E028, preregistered now so that nothing about it is chosen after E027's result).

## E024 result — 2026-09-08

The new information set is informative and still not tradeable with taker orders: displayed-depth imbalance within 1% is the strongest short-horizon predictor found in the whole project (IC 0.06 at 30 minutes, significant after correction in both assets, stable in sign), yet the extreme decile earns about one basis point where a taker round trip costs twelve. That is the same shape as Phase 1's flow reversal at a different information layer: the market prices these states to within the fee. Two counted follow-ups: extend the horizon where the IC was still rising (E026), and test whether passive orders with an explicitly adverse trade-through fill rule can collect the drift (E027). If both fail, the microstructure branch closes and the next information set is synchronized spot/perpetual trades.

## Phase 2 start — 2026-09-08

Read CLAUDE_PHASE2.md (the conclusion file it names as RESEARCH_CONCLUSION_20260908.md is reports/RESEARCH_CONCLUSION_2026-09-08.md on disk; same document). 62 tests pass; state matches the Phase 1 close. Inventoried the public microstructure archives before designing anything: bookTicker is the richest feed but covers only 2023-05→2024-03 at 50 GB per symbol, and its information (touch-level imbalance, microprice) pays off at horizons this project cannot execute; the spread it reveals (one tick, 0.015 bps) matters only as a cost input. The feeds that add genuinely new information at retail-executable horizons are bookDepth (displayed liquidity within ±1–5%, every 30 s), aggTrades (trade sizes and aggressor side at the trade level) and metrics (5-minute open interest and positioning ratios, archive ends 2024-03-03). E024 is built on those three with a deterministic every-third-day sample to bound the download to about 15 GB. The economic gate at Stage A (extreme decile ≥ 12.1 bps) is the lesson of E012 written into the design: a real IC below taker cost is not a candidate.

## 2026-09-08 — baseline and preregistration

Read root AGENTS.md, searched ancestor and descendant agent instructions (no overrides found), read full protocol and START_CODEX.md. Only these three user files existed. No Git repository. Python 3.14.3 and numpy/pandas/scipy/requests available. Preserve original files. No broker credentials inspected or required. No order endpoints will be called.

Working plan: see PLAN.md. Research capital approximately EUR500 is not allocated to trading. Paper capital is an accounting choice; tiny live and production capital remain zero. Research runs use unlevered spot long/cash only; 15x is an absolute policy ceiling, not an operational target. No strategy is eligible for paper or live.

### Universe and data choices made before observing results

BTCUSDT and ETHUSDT are fixed, recognizable crypto test assets selected for exchange-native data and plausible liquidity, not observed backtest performance. This is a conditional two-survivor universe, not evidence for the entire crypto market and not a point-in-time cross-sectional selection. Liquidity must be measured before capital feasibility claims. USDT access and account jurisdiction remain unverified; environment timezone does not prove residency. Avoid derivatives/shorts until account eligibility, historical funding, borrow and margin constraints can be validated. Trading 212 equities/ETFs remain a slower-horizon alternative, but broker-compatible historical quotes/corporate actions and account instrument access are unresolved. True HFT rejected for local-PC/retail-API infrastructure.

Use 2022–2024 development, 2025 chronological validation, 2026-01-01 through 2026-08-31 final locked test. Final data will not be downloaded; this also avoids outcome inspection through integrity summaries. Freeze architecture and promotion gates before any final access. First-stage screening is exploratory, not a mature strategy backtest.

### Bounded hypothesis shortlist

H1 momentum: delayed investor reaction and trend persistence; counterparties rebalance or realize gains. Test trailing 3/12/48-bar returns, long above zero, at 5/15/60/240/1440-minute resolution. Failure: reversal/chop, turnover costs, bull-only beta. Capacity limited by spread/depth; first screen restricts to BTC/ETH, no capacity assertion.

H2 reversal: temporary selling pressure from liquidity demand followed by normalization; counterparties urgent sellers. Same grid, long below zero. Failure: persistent crashes and informed selling. Holding periods from one bar to multi-day depending on signal persistence; record observed turnover and holding duration rather than assuming.

H3 aggressive trade-flow imbalance: continuation after net aggressive buying (taker-buy base volume / base volume). Cheap directional and IC diagnostic; OHLCV flow aggregates cannot establish queue priority or achievable seconds-level alpha. Failure: adverse selection and price impact already incorporated before signal is available. One prior completed bar as signal, same five timeframes.

H4 volatility conditioning / scaling: reduce exposure after elevated backward-looking volatility. Start as benchmark/risk comparison; not alpha by itself. No optimized regime classifier.

H5 relative value, funding/basis carry and cross-sectional residuals: deferred, not empirically rejected, because two surviving spot assets and no financing/shorting specification are insufficient. Equity factors/overnight effects likewise deferred pending corporate-action-safe history and brokerage quote compatibility. ML/ensembles require independently surviving simple signals first.

First search budget: 30 return-sign configurations + 5 flow configurations per asset = 70 signal-asset screens; both directions explicitly registered, no silent asset removal. Add buy/hold and 20-bar moving-average baselines. Use next-next bar open (one full bar execution delay after completed signal bar), nonoverlapping realized bar returns for portfolio accounting, fees on entries/exits, and terminal liquidation. Costs 10/12/24 bps each side: published regular-user 10 bps commission; extra 0/2/4 bps are uncalibrated spread/slippage scenarios, with doubled commission in stress. Optimistic is a fee-only lower bound, not a realistic fill claim. No fee discount or maker fill assumption.

Advance only candidates positive net in development under stress, with positive net in at least two of three development calendar years, and positive incremental risk-adjusted evidence over simple exposure benchmarks. Apply uncertainty and multiplicity correction before promotion. Validation will never be used to silently retune a failed candidate.

### Access issue

Initial requests GET to data-api.binance.vision failed with Windows socket permission error 10013 in sandbox. No dataset downloaded and no API response established at that point. Prepare auditable public-only downloader and request minimum network escalation.

### 2026-09-08 — acquisition and first adversarial code audit

All 96 registered archives downloaded and matched official checksums after approved public-only networking. A BTC July-2025 download timed out; resumed from verified cache with bounded connection retries, never retries on 429/418. Both assets' development history contains 315632 observed rows, sixteen missing bars on 2023-03-24 and fourteen zero-volume bars. No forward-fill of signals. The first screen/audit output is superseded: aggregate completeness was incorrectly used to erase an earlier executable bucket open. Separate execution-open fields correct that noncausal outage treatment. A regression test enforces it. Retain original artifacts and rerun rather than silently replacing results. Validation remained unopened; final test not acquired.

Development audit specification (registered before results): 4000 circular daily block-bootstrap samples, block length fourteen days, seed 20260908 plus candidate index. Estimate mean return and intercept versus buyhold within each resample; require positive one-sided lower bounds with Bonferroni 70-trial correction and positive extra-delay stress return before opening validation. Extreme bootstrap quantiles are approximate, and three development years cannot establish stationarity. No claim of successful walk-forward or final OOS evidence is permitted.

### User clarification and next branch

Latest checkpoint: E004–E007 completed. Monthly full resets fail doubled costs. Continuous carry reduces turnover, but BTC's separate futures wallet fails an additional20% rally despite positive combined returns. ETH2.65%base/2.59%stress indicative CAGR and adjusted mean evidence are research-promising, not eligibility. Gross drifts above1x; enforce a causal cap before architecture freeze. No validation opened.

User cannot locate fee/margin values. Reassured that no keys or repeated manual search are needed. Kept facts UNVERIFIED and completed independent E008 development sizing diagnostic instead: 80% initial gross, causal reductions and collateral veto, with no transfers. About 2.11% base / 2.07% stressed indicative CAGR and observed gross below 0.853x. No actual exposure reduction occurred in this history; do not overstate historical evidence for circuit-breaker execution. Account-dependent validation still gated. Read LATEST_RESEARCH_SUMMARY.md and STATUS.md for current verdict; prior checkpoints are historical.

E004 intended exact settlement marks/maintenance before a backtest; public funding lacks2005 marks per asset. E005–E007 therefore explicitly remain indicative diagnostics with audited hourly mark proxies, not verified execution/maintenance backtests. This relaxation supports falsification/research prioritization only. All archive gaps were separately repaired through public REST. Never use these diagnostics to claim capital eligibility.

User-specific ETH spot/perpetual fees and maintenance-tier values requested, no keys. Enabled-products confirmation does not establish commission/margin numbers. The next dependent validation gate remains pending these facts. Latest carry checkpoint supersedes the initial report's earlier access-information blocker.

User states residence Tunisia, every Binance product enabled, Trading 212 main account Invest in GBP with UK account detail. This is user-reported access, not independent regulatory/account verification. No credentials requested. UK account country/entity and Tunisia residence must not be conflated. Research can proceed on Binance derivatives; no real capital authorized.

E004 preregistration: investigate spot-long/perpetual-short carry from persistent demand for leveraged long exposure. Counterparty pays funding for leveraged directional exposure; failure mechanisms are negative funding, basis widening, venue/USDT risk, fees, fragmented collateral and liquidation despite aggregate delta neutrality. First cheap test: BTCUSDT/ETHUSDT realized funding history 2022–2024 only and current public futures filters. Measure funding persistence, monthly sign stability and whether gross carry covers two-legged current taker costs. Funding-only yield is **not strategy return**: it excludes basis PnL and margin mechanics. Fully funded conceptual capital = spot notional plus equally large futures cash collateral, zero borrow; gross initial exposure 1x combined capital. No leverage uplift. Before any backtest, require exact mark-price/basis alignment and account-specific margin tiers. Authenticated leverageBracket is a USER_DATA endpoint; values remain UNVERIFIED without a read-only user snapshot. Official USDT futures fee table retrieved 2026-09-08 shows regular maker/taker 2/5 bps; use taker, no BNB discount. Source: https://www.binance.com/en-NG/fee/futureFee. Funding/carry candidates add two hypotheses to cumulative 78 (80 total).


## Phase 4 checkpoint � 2026-09-09
E042 original reproduction and approved accounting audit complete;114 tests pass. Signals unchanged; corrected equal-weight daily Sharpe BTC1.26914/ETH1.14293 versus original1.26935/1.14365. Original files preserved. Strategy/config frozen before replication. Next: historical universe preregistration, acquire pre2025 hourly/mark data, integrity audit, replication and predefined inference.2025 LOCKED;2026 UNTOUCHED. No extra economic hypothesis counted for accounting diagnostics. FROZEN_E040_HASH=2707309704de29e394b5a2b511840cd5b058e3980e28c4a19e937be69fadb2ec


Phase4 E043: all12 assets and discovery comparators pass the data gate with disclosed gaps/proxies;121 tests pass. SOL non4h funding handled by hourly event accounting without changing4h signals/orders/trailing updates. Superseded pre-event freeze retained. Final frozen hash 9928aa464bd7f88bb44e76566f01593d87786ff048043620c514c20a96142ca0. E044 preregistered: one replication hypothesis, cumulative385 once run; seven cost/delay/funding cases are diagnostics, not additional hypotheses.2025 LOCKED;2026 UNTOUCHED.


## 2026-09-09 - Phase 4 continuation: supplementation before conclusions
Resumed from STATUS.md at the unresolved supplemental-data stage. Verified on disk: exact reproduction of original E040 (E042), corrected BTC/ETH Sharpe 1.26914/1.14293, frozen hashes, 12-asset universe hash, 1,126 monthly archives plus 20 daily supplements all checksum-verified, 121 tests passing at handoff. Found that supplementation code had not been written, no corrected rerun existed, and the analysis script could not even compile. Chronology matters for pre-registration: the gap finding and the supplement downloads both preceded any replication outcome, so supplementation is a data decision, not a performance decision. The first pass was preserved rather than deleted. The mechanism behind the surprisingly large first-pass distortion is instructive: full-window moving averages propagate a five-day hole for up to 250 bars, and an all-NaN ensemble was treated as flat, so four assets were silently under-invested in the trend sleeve for two to five months of 2022. That is a data-handling artefact of the discovery engine on incomplete inputs, not a property of the frozen rule; it is now impossible on these inputs because no gaps remain. Lesson recorded for future loaders: an incomplete-bar policy must be tested against indicator warm-up lengths, not only against the execution bar.


## Phase4 completed - E045_20260909T140237
Classification: CROSS_ASSET_WEAK_SIGNAL; decision: DO_NOT_OPEN_2025.12 assets,2022-2024; positive fraction 66.7%; median Sharpe 0.702; median factor alpha 53.63%. Primary portfolio Sharpe 0.869, DD -24.1%. E042 accounting audit, E043 universe/data, E044 one frozen replication hypothesis (cumulative385), E045 diagnostics (no additional hypotheses). Sources/config/universe/data hashes and seeds retained.2025 LOCKED;2026 UNTOUCHED. See PHASE4_CONCLUSION.md.


## 2026-09-09 - Phase 4 conclusion
The frozen rule went to twelve names it had never seen and came back with its sign intact on eight, a diversified low-beta portfolio that made money in 2022, and a breakout leg that had evaporated. The one statistic built to respect that twelve coins in one regime are one sample says the median effect could be zero; two other gates pass by a hair. That is what a real but modest effect looks like on three years of data, and it is also exactly what timed beta looks like, and the sample cannot tell them apart. The preregistered answer is CROSS_ASSET_WEAK_SIGNAL and 2025 stays shut. Two lessons worth keeping: a conditional factor intercept with state regressors is not an excess return and should not be preregistered as the headline alpha again; and the EUR 500 budget is not a rounding problem but a structural one for any multi-sleeve fractional-sizing rule on lot-quantised perpetuals. Nothing was tuned, no asset was dropped, and the strategy that failed to pass is preserved exactly so that a future regime can be tested against it rather than around it.


## 2026-09-09 - Phase 5 Branch A: the independent cohort
The frozen slow-trend rule was sent to twelve older, less liquid perpetuals chosen as of end-2020 and to a year (2021) nobody had used. It kept its risk-adjusted sign on ten of twelve, made +87% in 2021 and was net short and profitable through the May-2021 crash and the 2022 bear, and still failed: five of twelve sleeves finished with a net loss, the median sleeve lost a third of its capital, and the cohort-level portfolio spent three of four years going nowhere after a single rally. The lesson is about compounding, not direction: a 0.3 Sharpe sleeve with 80-95% drawdowns at 0.75 gross exposure has negative geometric growth, so a gate written on net returns and a gate written on Sharpe give opposite answers, and the preregistered one (net) governs. The mechanism is not dead as a description of prices; it is dead as a stand-alone 1x sleeve on this class of asset, and it is not independent evidence for E040: cohort 2 over 2022-2024 is 0.88 correlated with cohort 1 and roughly half as good. 2025 stays locked. Anything that scales exposure by volatility or trades fewer, more liquid names is a new architecture, which is exactly what Branch B is for and why its outputs are barred from the validation decision.


## 2026-09-09 - Phase 5 Branch B and close
The capital question turned out to be an engineering question with a clean answer: pool the capital, hold one position per asset, let sub-minimum resizes wait, and five liquid contracts trade the frozen score at 500 USDT with no measurable loss of fidelity. The first simulator quietly rebalanced to equity drift every four hours and doubled the turnover; the amendment is recorded and the run repeated. Volatility targeting halves the drawdown and the turnover and is obviously the next architecture, and it is exactly the kind of thing one must not test on the window one has just looked at. What Branch B cannot do is manufacture an edge: the reference portfolio it tracks is the Phase 4 window on the Phase 4 winners, and the same rule failed on an older cohort a few hours earlier. So the phase closes where the evidence puts it: an executable implementation of a phenomenon that did not replicate, a locked validation set, a frozen benchmark, and two honest options left, a different market class or a stop.



## 2026-09-09 - Phase 6 opens: market class changes to US equities/ETFs

Crypto discovery is closed (388 hypotheses, no validation candidate, E040 frozen, slow trend failed the independent cohort). Phase 6 asks a different question on a much richer information set: hundreds of securities, six decades, many industries. The first day went to the two things that decide whether the answer can be trusted at all: data and execution. Trading 212 facts were re-verified from the official pages: Invest is long-only and unlevered, fractional orders of every type are supported, the FX fee is 0.15 percent each way on conversion, a USD sub-balance avoids it in the app but the public API executes only in the primary currency and cannot use multi-currency balances, and the primary currency cannot be changed after opening. So any automated path pays 30 bps of FX per round trip on top of spreads, which is the strongest argument for monthly, low-turnover signals.

The provider audit had one clean outcome and one measurement worth keeping. Norgate Platinum is the only product inside EUR 50/month that supplies delisted securities since 1950, vendor-maintained historical index membership (Russell 3000 from 1990, S&P 500 from 1957), unadjusted prices, turnover and GICS, and an EULA that permits personal backtesting; it costs USD 630 a year (EUR 45/month equivalent) and needs a human to subscribe and install the updater. Tiingo, often cited as a cheap survivorship-safe source, was measured from its own ticker file: only 49 US stocks with an end date before 2010 and 514 before 2015, so it is survivorship-biased exactly where the dot-com and 2008 evidence lives. EODHD carries delisted names but no membership history before 2012. Nothing was bought.

Because the purchase is a human decision, the day's remaining work was made independent of it: a chronological lock with a programmatic firewall (development before 2018, validation 2018-2021, holdout 2022 onward, both locked behind human-created unlock files whose decision documents are hash-checked), a preregistered point-in-time universe with a conservative delisting-return rule (Norgate gives no delisting returns, so distress-proxy delistings get the Shumway haircuts and a full-loss sensitivity), a cost model with three preregistered cases, and the Kenneth French library, which is survivorship-free and free of charge, acquired with hashes for family-level screening. E050 is preregistered on it with fixed gates and a FACTOR_EVIDENCE cap: it can tell us which families deserve paid stock-level compute, and it cannot produce a portfolio.



## 2026-09-09 - E050 result and the shape of the equity problem

The free, survivorship-free evidence says what the literature says, with one qualification that matters for us. Cross-sectional momentum and industry momentum rank returns almost perfectly over fifty-four years, in every era, in large caps more than small, and the long-only top bucket carries a real alpha over the market with almost no beta. Reversal is a beta exposure that could not pay its own turnover; low volatility is an alpha only for someone who can lever the low-beta quintile, which this account cannot; the trend filter and volatility scaling do what Phase 5 already taught, which is to change the drawdown rather than the return. The qualification is the calendar: after 2000 the momentum premiums are positive but statistically silent (t below one), the 2009 crash took a year of long/short returns in one stroke, and the premium lives in bull regimes and dies in recoveries. So the stock-level question after the purchase is not "does momentum exist" but "does a liquid, long-only, monthly top-N version of it pay Trading 212's costs in the 2000-2017 window, and what does it do in a 2009". Everything that could be preregistered for that question has been: the universe, the delisting haircut, the cost cases, the eras, the position-count neighbourhood, the overlays that may only be applied to survivors. The one thing that cannot be done by the agent is the subscription.



## 2026-09-11 - The EODHD screening stage: what USD 50 a month actually buys

The user chose the cheap route first: EODHD's All-World EOD feed plus its marketplace constituents product, as a screen for the USD 346.50 Norgate question. The first hour was spent finding out what the constituents product measures rather than what it advertises. The S&P 400 and 600 histories begin on 2012-04-04 in both directions. The S&P 500 file looks deeper (start dates back to 1957) but has exactly one removal before April 2012 (Lehman), so anything before 2012 is a list of the companies that were still members in 2012, which is survivorship by construction. The honest point-in-time sample inside the development lock is therefore 69 months. Delisted names are there, with `_old` suffixes for reused tickers, but Enron's history starts in December 1997 and Bear Stearns' in January 1999 and ends on 2008-03-14, the Friday before the weekend that destroyed it. So the vendor's delisted depth is a question to be measured, not assumed, and the audit rule for the start of the survivorship-safe window (the year in which delisted names hold at least three quarters of their 2003-2007 share of the top-1000 by dollar volume) was written down before the download finished.

The rest of the day went to making the purchase decision impossible to steer. The gate document was written and hashed before any stock-level number existed: 24 preregistered trials, a survivor rule that insists on a positive 2010-2017 result and non-negative 2015-2017 excess (a family that only worked before 2010 is REJECTED_DECAY no matter how large its full-sample t), stress costs, drawdown relative to SPY, BH-FDR and deflated Sharpe across the 24, feasibility at EUR 500, and a corroboration requirement on the clean 69-month point-in-time universe. Sector-ETF survivors alone cannot trigger the purchase because Norgate adds nothing to ETF-level data. The engine trades at the open after the signal close, books delistings at the last vendor price with the Shumway haircuts, and was tested on synthetic panels for causality before it saw a real price. The 50,891-ticker download (every common stock, every venue, because failed companies end their lives on the pink sheets) was slower than the rate limit and was restarted in three shards.



## 2026-09-12 - E051: the momentum family meets the modern era at stock level

The first attempt lasted nine trials before it was killed: the top of every momentum ranking was a vendor error (a placeholder price of one million, a split factor of zero, a penny stock quoted at five thousand dollars for a day), and the identical Sharpe across N=10, 20, 30, 50 gave it away. The fix was five mechanical integrity rules written down before the rerun, tested on synthetic panels, and applied to benchmarks and strategies alike. The valid run then said something consistent and dull. Among the thousand most liquid US stocks, a monthly top-30 momentum portfolio at Trading 212 costs made 220 percent in 1999 and nothing afterwards: 2000-2017 at minus seven percent a year against SPY's plus six, an 88 percent drawdown, negative excess in the last three development years, a technology loading of one, and 71 percent of its lifetime return from a single year. Residual momentum, vol-scaled momentum, six- and nine-month lookbacks, ten to fifty names, a tighter liquidity cap, a higher price floor, the point-in-time S&P 1500 from 2012, nine sector ETFs: every cut tells the same story, and the optimistic cost case does not change it. The rejection cannot be blamed on costs, on the universe tail, on the delisting rule or on the engine; the benchmarks reconcile with SPY and the cleanest point-in-time replication agrees.

This is the stock-level face of what E050 already showed on survivorship-free data: a six-decade premium that went statistically silent after 2000. Norgate would buy 1990-1997, where it worked, and cannot buy 2000-2017, where a EUR 500 account has to live. So the frozen gate answers DO_NOT_BUY_NORGATE, and it would have answered the same under the un-amended data check for a worse reason. The purchase gate did its job in the other direction too: it was written before any number existed, the one amendment was made before results and both hashes are kept, and the twenty-eight cells are all in the ledger. Nothing was retuned to make momentum look better, and nothing was retuned to make it look worse.



## 2026-09-12 - Phase 6B: everything the price feed can still ask, asked with the modern window first

The user changed the question: not whether a factor existed, but whether anything low-turnover and long-only can plausibly pay a EUR 500 account through Trading 212 today. So every family was screened on 2010-2017 before anything else. The free, survivorship-free French buckets answered quickly: dividend yield, five-year reversal, low beta and low variance all beat the market over 2000-2017 by one to five points a year and all lost to it over 2010-2017. Profitability, investment and net issuance kept a positive sign after 2010, worth a third to a half of a percent a year, which would require a USD 60-a-month fundamentals feed to test at stock level; for a thousand euros that is five euros of expected excess against six hundred and fifty of data, and the arithmetic ends the discussion without a purchase. The live factor ETFs told the same story in deployable form: dividend and value funds track the index, minimum-volatility funds lag it by a point with two-thirds of its beta.

The allocation overlays were the interesting part, because they are what a cautious small account would actually do: hold the index, step into Treasuries when the twelve-month return turns negative or when volatility spikes. Over 2004-2017 and over 1994-2017 they match or beat the index with a third of its drawdown, and the red team explains why that is not alpha: the whole excess sits in 2000-2002 and 2008, every start year from 2009 onward loses one to five points a year to the index, the nine-month lookback loses two points to the twelve, and the volatility rule needs the bond rally to work at all. That is E050's WEAK_SIGNAL again, now with a deployable form and a price tag. The honest label is a risk overlay for someone who values the worst case more than the average, and the one-shot validation window (which contains March 2020, the crash monthly rules miss) is not spent on it. Phase 6B closes with the ledger at 455 and no candidate.



## 2026-09-12 - Phase 7A: the last month of paid data, spent on what only it could answer

The constituent record was the one thing in the subscription no free source offers, so it went first. With effective dates only, the tradable part of the index effect is what happens after a name enters or leaves, and on 2012-2017 that is negative for every class: additions give back five percent in six months, promotions drift down, and stocks deleted for cause keep falling for a year. The one number that looked like a strategy, a 38 percent annual excess from buying deletions, was a single year of distressed energy names; five of six years were losses and the median deleted stock was down twelve percent six months later. Then the price-derived mechanisms: 52-week-high proximity is a weak cousin of the closed momentum family and changes sign on the point-in-time universe; the overnight and intraday decompositions show the published effects with the sign reversed, which turns out to be the volatility effect seen from underneath; abnormal volume and beta carry nothing; low liquidity inside the liquid universe is a small-cap tilt that fades after 2010.

That left low realized risk, in three definitions, with a real gross decile spread over the equal-weight universe after 2010. The portfolio stage removed it: concentrated to thirty or fifty names the lowest-risk stocks earn less than the low-risk decile, and after bookings and even three basis points of cost the excess is zero. Against the index fund it is the same object the program has now met four times, a portfolio with half the beta, two-thirds of the drawdown, more return through bear markets and less through bull markets. That is a preference about risk, not evidence of alpha, and it is recorded as such. The phase closes with the ledger at 479, nothing promoted, and a recommendation to cancel both subscriptions: everything they could give is on disk, hashed, and already asked.



## 2026-09-12 - Phase 7B: choosing the next information source instead of the next indicator

Seven phases and 479 cells have said the same thing in different words: prices alone, however they are cut, do not pay a small long-only account after 2010. So this phase ran no backtest and asked a different question: which information that this program has never seen is (a) still documented to work after 2010, (b) dated to the minute so the causal question is clean, (c) informative on the long side, and (d) free or nearly free. The earnings channel, the user's first priority, has the cleanest free data imaginable, the SEC's own XBRL facts and 8-K timestamps, but the recent literature is blunt: the drift after announcements is gone in large stocks since 2006 and lately in microcaps too, and the analyst revisions that might still carry information have no point-in-time history at any retail price. The winner was the least glamorous option: the SEC's own filings. Insider purchases and buyback authorisations are private information and management signals, filed under a two-day rule with acceptance timestamps, structured in free quarterly datasets back to 2006 and 2009, and informative precisely on the side a Trading 212 account can hold. The modern evidence is modest and horizon-dependent, which is a research question rather than a marketing claim, and the design can be preregistered so that a null is an acceptable answer. Nothing was bought, nothing locked was opened, and the subscriptions still get cancelled.



## 2026-09-12 - Phase 8: the insiders' trades, read causally

The first genuinely new information source of the program came from the SEC's own structured filings, and the rules were written down and hashed before a single event return existed: originals only, code P, common equity, prices within a fifth of the tape, at least ten thousand dollars, entry at the open of the day after EDGAR's filing date, six-month holds in twenty equal slots, manual USD-balance costs as the base case. Ten random filings were checked against the actual documents on EDGAR and all ten reconciled to the line. Two backtest runs then died before interpretation on their own defects, a one-month benchmark offset and a month-label bug; both are kept in the reports folder with their post-mortems, and the third run is the one that counts. What it says is simple. After a purchase filing and a next-day-open entry, the bought stocks earn nothing abnormal against the equal-weight liquid universe at any horizon, and the one cell that beats that universe in 2013-2017, purchases by directors who are not officers, does so with a market beta of 1.2, a value tilt and a negative three-factor alpha: insiders buying beaten-down smaller stocks in a window when beaten-down smaller stocks recovered. Conditioning on profitability or on the absence of share issuance did not help, and the earnings-surprise decile test on the same free data reproduced the literature's verdict that the drift is gone. The repurchase branch stopped where its own rule said it must, at an unvalidated classifier, with the candidate filings inventoried for another day. The gate answer is FAIL, the family is closed, the locked years stay locked, and the ledger stands at 488.


## 2026-09-12 - Phase 8B: the buyback question, rebuilt as two problems instead of one

The Phase 8 repurchase cell had stopped for an honest reason: nobody had read the filings. This session kept that discipline and turned it into infrastructure. The economic claim was written down and hashed before a single candidate was opened: a new or enlarged authorisation, disclosed by 8-K, bought at the first open at least an hour after EDGAR accepted the filing, held for a year, weighed against the equal-weight liquid universe and against the styles that a buyback announcer usually carries. The trap the insider cell fell into, a raw excess that was beta, size and value in disguise, is now a gate (G4 needs alpha after FF5 and momentum) rather than a red-team afterthought.

The detection problem was split in two. Retrieval was made deliberately greedy: twenty-four expressions, each queried month by month over 2004-2017, gave 110,355 candidate accessions where the Phase 8 five-phrase net had found 27,367 over 2009-2017; the price of that recall is that half of the pool is noise (warrant agreements that "purchase up to", credit agreements, funds), which is the classifier's job, not the search's. Whether the search itself misses real announcements is asked separately, once with the XBRL authorised-amount series and once with sixty human-labelled filings from the complement, so that classifier precision is never mistaken for system recall.

The classification problem was handed to a human on purpose. Two hundred and forty filings were drawn with a seed across fourteen years and two strata, one per issuer-year, and split into development and holdout before any label existed; the holdout labels are blanked for every development read and can be scored exactly once, by a script that first checks the classifier files against their frozen hashes. A precision floor of 0.90 on the new-or-increased class was fixed in advance, with a minimum count of predicted positives so that a perfect score on five filings cannot pass. Nothing about returns exists yet: the return stage refuses to run without a recorded classifier-gate pass, the full-text fetch of the candidate pool is still running, and the branch stops here until a person labels the two CSV files. A code review found two guard gaps (a header without a filing date slipped past the lock; holdout scoring was not tied to the frozen code) and both were closed before this entry was written.


## 2026-09-20 - Phase 8B: sixty labels instead of three hundred

The owner will label sixty filings, not three hundred and thirty, so the validation was rebuilt around what sixty labels can honestly say. They cannot train anything; they can test one thing well: whether the filings the machine would trade are what it says they are. So all sixty became a sealed exam rather than a split, and thirty-eight of them are a plain random sample of predicted new-or-increased authorisations, half from the 2013-2017 gate window. Precision on those thirty-eight is the gate (thirty-seven right to pass, thirty-five or thirty-six for a short targeted extension, fewer to fail), with the exact binomial interval printed beside it and explicitly not used as the criterion, because no sixty-case design can push a lower bound above ninety percent. Recall gets no such measurement: twenty-two non-positive cases are a sanity check, and the amendment says so before any label exists.

The classifier was written without any human label, from reading a fifth of the corpus set aside by a hash of the accession number, and the exam is drawn only from the other four fifths. Reading found the traps one by one: plans that "authorize" in the present tense, authorisations "in February 2008" restated in November, "available under the program authorized in fiscal 2007", odd-lot offers, note repurchases booked at a gain, a Federal Home Loan Bank buying back members' stock. A second pass built on a different idea (the headline and lead of the release, the item codes, a bag of cues) never sees the first pass's answers; it accepts about four fifths of the first pass's positives, mostly declining authorisations buried deep inside earnings releases, and the rule written beforehand says more than one fifth would have meant repairing the classifier rather than asking the human for more labels.

The remaining download of 2013-2017 filings slowed to a crawl, so the exam is drawn by walking a seeded random order of the candidate list, fetching on demand and filling each stratum as cases appear, which is the same thing as sampling after a complete download. The labelling page shows a paragraph, nine keys and a progress bar, and nothing about any model, before or after a label. Returns stay locked behind the result.


## 2026-09-20 - Phase 8B: repairing the ruler before re-measuring

Thirty-three of thirty-eight is a failure, and it stays one. What the same day's audit also showed is that the exam had been printed wrong: in thirteen of those thirty-eight cases the page did not contain the sentence the machine had keyed on, and four of the five disagreements were in that thirteen. SEACOR is the clean example. The machine read "increased the Company's authority to repurchase SEACOR common stock from $30.5 million up to $100.0 million" and said INCREASED; the labeller was shown "During the fourth quarter, the Company purchased 1,047,664 shares" and reasonably said ROUTINE. The snippet chooser did not know the word "authority" was authorisation vocabulary, so it picked a different sentence, and the disagreement that followed was scored against the classifier. That is a broken instrument, not evidence.

So the ruler was rebuilt first. The new display does not choose anything. It finds the classifier's own evidence sentence in the filing and shows it with one sentence on each side, and a preflight refuses to let a case into a validation sample at all unless that sentence is provably present in what the human will read. All fifteen fresh cases pass it, checked twice, the second time through the actual web page rather than the function that builds it. The old ranker is archived under a filename that says it was defective, because the point of keeping it is that someone can see what went wrong.

Only then the classifier. The five approved repairs are small and dull: "New York" in a glued press-release header must not mean a new programme; a forward-looking-statements list that happens to contain the words "share repurchase authorization" is a lawyer's paragraph, not an announcement; an extension with no new money is a renewal; a release headline that announces a programme is evidence for the authorisation sentence beneath it; "authority" is authorisation language. Three distinctions the amendment asked to be preserved turned out never to have been implemented at all, so they were written: a new programme replacing a completed one is new, an increase of the authorisation itself is an increase even when the sentence quotes no dollar figure, and "in addition to" means added capacity.

The instructive part was what had to be thrown away. A first pass at these repairs moved a hundred and sixty-six development filings into the positive class, and reading a random twenty of them showed roughly a third were wrong: remaining-balance statements, daily buyback reports, completed programmes, a slide deck whose "additional $200 million" sat four hundred characters from an unrelated "authorized". Two of the new rules were doing that work - a document-level renewal override and a fallback that trusted a headline when no sentence carried an authorisation verb - and both were deleted rather than tuned, because the thing being measured is precision and a rule that adds a third-rate positive is worse than no rule. Guards went in for the categories the reading exposed: Rule 10b5-1 trading plans are a way of executing a buyback, not a decision to have one; repurchasing restricted stock from an officer is not a programme. The final version moves seventy-six filings in and seven out, and the seven were each read and are each intended. None of this touched the sixty frozen labels, and a test now greps the classifier source for accession numbers, gold ids and the names of the reference-set companies, so the claim that nothing was memorised is checkable rather than asserted.

The adjudication log is the uncomfortable part and is kept separate on purpose. Three of the entered labels are wrong against their own passages, including one that is simply not about share repurchases: an option granted to initial purchasers to buy twenty million dollars of additional convertible notes to cover over-allotments, entered as INCREASED. That one was displayed correctly, so it is a reading error, not an instrument error, and saying so matters more than being polite about it. Correcting the two that fall in the measured stratum would move the first run from 33/38 to 35/38 - ninety-two percent, still short of the ninety-five the rule demanded. The defect did not hide a pass. Both numbers are written down, the counterfactual is labelled diagnostic in the file, in the JSON and in the test suite, and the gate record that would let returns run was not written and does not exist.

Fifteen fresh filings are now drawn from the eighty percent no human has seen, excluding every accession and every issuer that appeared in the first round, eight from the gate window and seven from before it. The rule for reading them was fixed before they were drawn and is in code: fifteen right passes, fourteen stops and asks, thirteen fails, and there is no version of this where the answer is to request another sixty labels. Nothing about returns has moved. The 2018-2021 validation and the 2022-2026 holdout have still never been opened, and a passing classifier would authorise development use only - the right to compute a number, not a belief that the number will be good.


## 2026-09-20 - Phase 8B: the classifier was the easy part

Fifteen out of fifteen. The repaired classifier read fifteen filings it had never seen, drawn from the four fifths of
the corpus no human had looked at, and every one of them was what it said it was. Zero false positives, the error mode
that sank the first attempt absent, and the second independent pass agreeing on fourteen of the fifteen. The labels
were frozen and hashed before the scoring script was allowed to read them, the classifier hashes were checked against
the ledger from before the cases were drawn, and the thresholds were the ones written down two hours earlier. The
first result stays exactly where it was, 33 out of 38, and was never pooled into this one.

Then the strategy was tested, and it failed.

The shape of the failure is worth stating precisely, because the headline number looks like a discovery. Buying every
new or increased buyback authorisation at the first open after EDGAR accepts the filing and holding a year beat the
equal-weight liquid universe by six percentage points a year over 2013-2017, five years out of five, with a t
statistic above five. It also lost to SPY - 14.94 against 15.22 - while carrying twice the drawdown, and its alpha
against the market was minus nine tenths of a percent, and against the five-factor model with momentum minus four
tenths, both with t statistics indistinguishable from zero. The six points are not skill. They are the market, size
and value exposure of the kind of company that announces a buyback. This is the second time this program has found
that exact object: the insider-purchase cell in Phase 8 failed the same way, and the gate that catches it exists
because of that earlier failure. It worked.

The event study says the same thing from the other direction. The 252-session abnormal return is positive in the gate
window and negative before it, minus five and a half percent over 2004-2012 and minus one point nine over the full
span. An effect that changes sign when you look at more of it is a window, not a mechanism.

There was one genuine scare along the way. The first run reported a 2012 excess of seven hundred and thirty-seven
percent. That is not a finding, it is a bug, and the right response to a number like that is to go and look. It was a
single position: Smithfield Foods, on a vendor series that oscillates between about seventeen cents and about
twenty-two dollars on adjacent sessions, minus ninety-nine percent one day and plus thirteen thousand the next. A book
that re-equalises to 1/N on every entry and exit will buy that low and trim that high over and over, and it booked a
thirty-fold gain on a position whose quoted price had fallen ninety-nine percent. The cause was structural rather than
particular: Phase 8B checks whether a stock is eligible at the signal date before entry and then never looks at the
price path again for the next two hundred and fifty-two sessions. Just under six percent of the panel carries the same
pathology, which matches the vendor ticker-reuse damage Phase 6 measured independently.

The screen written for it reuses Phase 6's existing extreme-day thresholds rather than any number chosen for this
occasion, reads the price series only and never an event's return, and throws out the whole event rather than
truncating the hold. It removed forty-three events out of seven thousand eight hundred and forty-nine. The honest
detail is the direction: the defect was inflating the result, so cleaning it made the concentration gate go from
failing badly to passing comfortably and moved the headline excess from 6.09 to 6.03. A data repair that makes your
strategy look worse where it matters and only fixes a gate you were failing is not motivated reasoning. Both runs fail
G4 and G11, the broken one is kept on disk with none of its numbers treated as results, and every permanently frozen
file was re-hashed after the return stage to prove the classifier had not been touched while returns were visible.

So the branch closes, and with it the EDGAR event family: insider purchases, quality conditioning, earnings drift and
now repurchase authorisations, each rejected on its own evidence. Four hundred and ninety cells, no candidate. The
2018-2021 validation window and the 2022-2026 holdout have still never been opened, which is the only part of this
that was ever going to be hard to undo. A rejected candidate does not get to spend them.

## Phase 9A — the analyst-revision family is not dead, it is unlicensed (2026-09-21)

The question this phase had to answer was narrow and it turned out to have a clean answer, which is rare
here. Can we obtain, for a stock on a historical date, what the analyst consensus actually said on that
date — not today's estimate for an old quarter, not the last number before the print, not a surprise.
The test reduces to one thing: does the schema carry an observation date that is a different field from
the fiscal period, and can you query it.

The first provider audited passed on the first look, which was not what the previous eight phases had
trained me to expect. Nasdaq Data Link's ZACKS/EEH returns, from an endpoint that needs no API key at
all, a primary key of m_ticker, per_end_date, obs_date, per_type, with obs_date also listed as a filter.
The documentation defines obs_date as the date on which contributed estimates were changed and the
consensus was revised. That is not a marketing claim about history, it is the row being written when the
consensus moves. EPS mean, median, high, low, standard deviation, analyst count, and separate counts of
estimates revised up and down. Back to 1979. Twenty-three thousand issuers, listed and delisted, which is
the one number in this audit that no free source was willing to state. A companion table carries CIK, so
the join to the SEC identifiers this repository already uses is a join and not a research project.

Then the Nasdaq FAQ, four scrolls down a page about Okta activation and billing addresses: an individual
may subscribe to fewer than three years of Zacks history, because the agreement restricts deeper history
to institutions. Full history may only be licensed to institutions and businesses and not to individuals.

So the right data exists, is exactly the right shape, and is not for sale to us. The workaround is to
register as a business, which is a statement about who I am rather than a technical step, and I am not
going to recommend that. Three years supports forward paper trading and nothing else; it cannot hold a
development window, a validation window and a holdout.

Everything cheaper fails on structure rather than on price, which is the useful part. EODHD's
calendar/trends, the obvious candidate at twenty dollars a month, returned 403 on our token — /api/user
returned 200 in the same run, so it is an entitlement boundary and I stopped there per the brief. The
documentation disqualifies it anyway, and does so in its own words: date is the fiscal period end, the
horizon label repeats across many dates because the file keeps the history, and the worked example is
annotated with the date it was read and the note that the estimate fields move as analysts publish. The
history it advertises is history of target periods. There is no observation field anywhere in the
payload and no date filter on the endpoint, so the question cannot even be asked, and immutability cannot
be demonstrated because nothing records when a row was written.

Alpha Vantage was more interesting and is the one place I had to test rather than read. Its
EARNINGS_ESTIMATES has no observation date either, but the past-period rows are not live. IBM's
2017-06-30 quarter still reads 2.75 current, 2.75 at seven days, 2.75 at thirty, 2.77 at sixty, 3.17 at
ninety. If that row were being recomputed today every one of those would be identical, because nobody
revises a quarter reported nine years ago. The spread across the lags is the settling pattern of a
consensus walking into a print, preserved. So the row was frozen and kept, which makes it genuinely
partial point-in-time rather than a current snapshot. It still fails, for three reasons that stack: the
anchor date is not in the schema so every feature inherits an unverifiable timing assumption, there is
one snapshot per fiscal period taken at the end of the estimation window so it can only be read after the
print, and history starts 2017-06. Useful to have established properly rather than dismissed.

FMP saved me the work by conceding it: their own August guidance says a current consensus response should
not be described as the pre-announcement estimate unless the record was actually observed before the
announcement, lists reconstructing historical knowledge from a current response as the canonical error,
and tells you to use a source that explicitly supports point-in-time vintages. Finnhub has exactly two
tiers now, zero and three and a half thousand a month. Intrinio sells the same Zacks data and every
estimate feed is Enterprise; their individual plan at a hundred and fifty carries no estimates at all.
Polygon's Benzinga sets are ninety-nine a month and are ratings, not consensus. There is no price point
between free and institutional at which this data becomes buyable, and that is a licence structure, not a
gap in my searching.

The part I did not expect to find was Chen and Zimmermann. Their open-source cross-section publishes
twenty-one analyst-category signals built from IBES, including AnalystRevision, which is literally FY1
mean estimate this month over last month, and REV6. The firm-level panel is keyed on CRSP permno and we
have no legitimate permno-to-ticker map, so it cannot produce anything tradable here. But the long-short
portfolio return series need no identifier mapping at all, and restricted to 2017 and earlier they answer
the question that should be answered before anyone discusses money: was this mechanism still alive in the
development era. Those portfolios are decile, long-short, CRSP-universe and costless, so they are an upper
bound on what a long-only top-N retail book could capture. If the upper bound is already gone by
2010-2017, no purchase at any price rescues the retail version and the family closes on evidence instead
of on budget. That is Stage 0 of the 9B draft and I did not run it, because this phase was an audit.

The distinction I want on record is the one this phase changes. The analyst-revision family is not
rejected. It is blocked. Phase 7B guessed at that in one line; it is now a verified, quotable licence
restriction with the exact product, table and column names attached. Nothing was bought, no account was
created, no cell was added, the ledger stays at 490, and the multiplicity burden is unchanged because
nothing was evaluated against a return. 358 tests pass. Validation and holdout have still never been
opened.

## Phase 9B Stage 0 — the sort still points the right way and that is all it does (2026-09-21)

Before running anything I had to withdraw a claim from my own draft. I had written that the published
OSAP long-short portfolios were an upper bound on what a long-only retail book could capture. That is
not true and it is not subtly untrue. A long-short return is the long leg minus the short leg, the short
leg can have either sign, and so the spread bounds the long side in neither direction. A spread can be
large because the short leg collapsed while the long leg did nothing, which is the case that matters
here, because we can only go long. The correct description is narrower and duller: a low-friction
external mechanism screen on someone else's implementation, useful for asking whether analyst-revision
sorting still separated returns, and not a backtest of anything we could trade. The long leg had to be
tested on its own rather than inferred, which is what §5 of the preregistration does.

The freeze was written before any return was touched, and the part I am most comfortable with is that
the long-leg question was settled from counts alone. The published file carries Nlong and Nshort per
row. For AnalystRevision the LS row's Nlong matches port 05 exactly — 502 pre-2018 months, median 673,
min 171, max 4063 — and its Nshort matches port 01. So LS = port 05 minus port 01 and port 05 is the
long leg, established without reading a single return, which is the only honest way to fix a gate that
depends on knowing which end of the sort you are standing at.

The same counts turned up a structural wart worth recording. AnalystRevision's interior quintiles are
empty in 361 of 502 months. That is what a discrete signal does: the mean-estimate ratio piles at
exactly 1.0 whenever no analyst moved, the interior breakpoints collapse, and everything lands in the
extreme bins. It means a simple average across the five ports is not the universe return, so the
benchmark had to be Nlong-weighted across whatever ports exist that month. Getting that wrong would
have manufactured a benchmark rather than derived one.

Then the first run produced a monthly mean of 0.826 and a cumulative return of 3.5e+31, and I stopped.
Two defects, both mine, both mechanical. OSAP quotes returns in percent; the French loader already
divides by 100. And OSAP stamps each month with the last trading day — 2005-04-29, 2005-07-29,
2005-12-30 — while French stamps the calendar month end, so an exact-timestamp join had silently kept
111 of 156 months and I had not noticed because nothing printed the match count. The first run is on
disk, superseded, and none of its numbers is quoted; its "+10.29%/yr long-leg excess over the market"
was an artefact of subtracting a decimal from a percent and is worth naming explicitly so nobody
rediscovers it as a result.

What made the repair legitimate rather than a second look was writing down, before re-running, why it
could not matter: C1, C3, C4 and C5 are signs, which survive division by 100, C2 is a t-statistic, which
is scale-invariant, and C5's two sides come from the same file at the same scale on the same dates. The
script now asserts that against the stored flags and raises if any gate flips. It did not flip. All five
identical, 156 of 156 months matched.

And the result is the flat, unsatisfying kind. AnalystRevision's spread went from 9.92%/yr with a t of
6.5 in 1990-2004 to 2.39%/yr with a t of 1.28 in 2005-2017 — a quarter of its former strength, Sharpe
1.66 down to 0.37, and over thirteen years of monthly data indistinguishable from zero. C1 passes, C2
fails, and the rule I froze says that combination is ambiguous no matter what else holds. It holds a
lot else: 2010-2017 still positive, REV6 strong at 7.04%/yr with a t of 2.48, long-leg excess over the
equal-weighted universe positive in both windows. None of it counts, by design, because I wrote the rule
so that a weak primary could not be carried over the line by its corroborators.

REV6 is the temptation and it is worth saying so plainly. It is the better signal by every number in the
table and it would have been easy to reframe the phase around it. It was frozen as corroboration and it
stays corroboration. Its long leg also loses to the value-weighted market in 2010-2017, so elevating it
would have bought a different headline and the same economics.

Which is the actual finding. The preregistered warning fired: beats_b1_but_not_b2 is true. The long leg
beat the equal-weighted covered universe by 0.82%/yr and then 0.39%/yr, with t-statistics of 0.79 and
0.34 — statistically it is the average covered stock — and against the value-weighted market it managed
+0.82%/yr and then -0.95%/yr, at eighteen to twenty-one percent volatility against the market's twelve
to fourteen. That is the third time this programme has produced that exact object. The Phase 8
insider-purchase cell did it, E062 did it, and now the published long leg of a sort built from data we
cannot buy does it. All of this gross, costless, equal-weighted, microcaps included, in someone else's
implementation. Our version would be strictly worse.

So the family is not rejected and is not supported. It is data-blocked by licence and the free evidence
came back inconclusive, which is the least quotable of the three outcomes and the one the numbers
actually produced. Nothing bought, nothing promoted, no additional analyst signal inspected, no
threshold moved after the fact. 376 tests, 490 cells, and validation and holdout still never opened.

## Phase 10A — the free panel starts one settlement date too late (2026-09-22)

The first thing worth getting right was the distinction the brief insisted on, because the free data is
asymmetric in exactly the way that punishes carelessness. Short interest is the outstanding position,
reported twice a month under Rule 4560. Short-sale volume is the daily flow of short-marked executions.
NYSE's public FTP makes the trap concrete: /ShortData/ holds six directories and every one of them is
shvol — NYSE, ARCA, Amex, Chicago, National, Texas. Volume, in bulk, free, going back years. Nobody
publishes the positions that cheaply. A researcher in a hurry substitutes one for the other and has a
different paper.

The NYSE free short-interest tree does exist, at /NYSEGroupConsolidatedShortInterest/, from 2015-08, and
the files are twenty kilobytes each, which is the answer before you open one. It is a market-level
summary: four rows, NYSE, ARCA, MKT, GROUP, with total current short interest and a count of securities
holding a position. No issuers. The one elegant thing about it is the timing convention — the file named
20150811 contains settlement date 07/31/2015, so the filename is the publication date and the settlement
date sits inside. Perfect point-in-time structure wrapped around data with no cross-section in it.

FINRA was the surprise. api.finra.org answers with no key, no registration, no account, and
consolidatedShortInterest returns issue-level rows with everything this family needs: current and
previous short position, days to cover, a revision flag, a split flag, market class. On settlement date
2017-12-29 the record-total header says 15,495 issues, consolidated across NYSE, NNM, ARCA, SC, AMEX,
BZX and OTC. I checked survivorship the only way that means anything, by asking for names that are gone:
TWTR returns 37,978,572 shares short, CELG returns a row, RTN returns a row. The historical files keep
the dead tickers even though Nasdaq's lookup page does not.

And then the coverage. My first scan tested calendar 15ths and told me the data started in late 2018,
which was wrong — 2018-01-15 was the MLK holiday, 2018-04-15 and 2018-07-15 were Sundays, and FINRA
settles on the preceding business day. Rescanning on actual settlement dates moved the boundary to
2017-12-29. That is the whole finding in one date. The free, correctly structured, venue-consolidated,
survivorship-safe US short-interest panel begins on the last settlement date of 2017, and our
development window ends on 2018-01-01. One observation. Everything else it holds is validation and
holdout.

The paid side is the mirror image. NYSE Group Short Interest goes back to January 1988 and its client
specification is the best-structured thing I have read in three phases of data audits: CUSIP rather than
ticker, Free_Float at the settlement date, Change_In_Short_Interest_Position already computed,
Revision_Indicator, Split_Indicator, and a published calendar mapping every settlement date to a release
date with the file landing at 2:00pm ET. Causality fully determined. Two problems. It covers NYSE,
American and Arca only, so every Nasdaq-listed issuer is missing and you would need Nasdaq's separate
product as well. And the phrase "short interest" appears zero times in both of NYSE's public pricing
guides; the governing line is a flat fee per product per organisation on an enterprise-wide basis, which
is a licence written for firms. Nasdaq's bulk file is "subscribe for SFTP" with no figure, and its own
Publication Schedule and Data Fields links 404 — a vendor whose documentation has rotted is a risk worth
writing down.

I did not download the NYSE issue-level samples. They sit on the public FTP, 734KB each, and the two
sample settlement dates are 2026-04-15 and 2026-04-30, both inside the holdout. The specification gave
me the schema without opening them, which is the point of reading specifications.

The literature screen produced one correction I care about. The brief nominated change in short interest
as the primary signal. The evidence does not support that ordering: the change looks informative for
distressed firms, a one-month change has been found to carry no marginal power once the demeaned ratio
is controlled for, and the open-source replication corpus contains three short-interest level predictors
and no change predictor at all. So the 10B draft inverts it — level primary, change corroborating — and
says plainly that if the inversion is not accepted the phase should not run, because it would be leading
with the weaker and unreplicated form.

The genuinely encouraging result is Boehmer, Huszar and Jordan: the low-short-interest long side is
larger in absolute value than the heavily-shorted short side. Almost everything this programme has
looked at is a short-side story that dies under a long-only mandate, and this one is documented as the
opposite shape. That is the only reason the family was worth an audit.

The discouraging result is the one that matters more. Asquith, Pathak and Ritter measure the effect at
215 basis points a month equally weighted and 39 basis points value-weighted, insignificant. Every
short-interest portfolio in the open-source corpus is equal-weighted. Chen and Welch put the post-2005
large-cap median at seven basis points a month. This is the fourth time in a row I am looking at a
candidate whose entire case rests on beating an equal-weighted universe, after the Phase 8 insider cell,
E062, and the Phase 9B analyst-revision long leg. The pattern is no longer a coincidence and it should
probably be treated as a prior rather than a finding.

So: partial, not sufficient and not absent. And the useful next move costs nothing, because the OSAP file
is already on disk from Phase 9B and contains ShortInterest with 539 pre-2018 months, Sign = -1, meaning
the long leg is the low-short-interest side. Whether that leg beat a value-weighted market in 2005-2017
is answerable for free, and it decides whether any quote is worth requesting. I did not run it; Phase 10A
computes no returns. One note for whoever writes that preregistration: Sign = -1 means the long leg
should be port 01, not port 05, and that has to be proved from the Nlong and Nshort counts before any
return is read, exactly as it was for AnalystRevision. Assuming it would be a way to read a sign
backwards and call it a result.

490 cells, unchanged. 376 tests. Nothing bought. Validation and holdout still never opened.

## Phase 10B Stage 0 — stopped at the timing audit, and a sign error caught on the way (2026-09-23)

The instruction was to resolve the causal timing before preregistering anything, and to do it without
touching the return column. That turned out to be the right order, because the audit killed the stage.

The chain took four files to trace and none of it is ambiguous. CompustatShortInterest.py sets
time_avail_m with one line — datadate.to_period('M').to_timestamp() — which is the calendar month of
the settlement date with no lag applied at all. The field is named availability and holds observation.
The monthly collapse then takes the first record in the month, which is the mid-month settlement, as
SignalDoc says. ShortInterest.py carries that key straight through to yyyymm. And then
01_PortfolioFunction.R does the thing that matters: yyyymm := yyyymm + 1, join onto crspret, whose
yyyymm is the return month. So the return printed at month m belongs to month m and was earned on a
signal measured around the 15th of month m-1. The return period opens on the 1st of month m. Everything
rests on whether the mid-month figure was public by then.

The modern answer is yes. Nasdaq's own report key says FINRA compiles the data and provides it for
publication on the 8th business day after the settlement date, and running that against the XNYS
calendar for all 336 months from 1990 to 2017 gives publication before the return month every single
time. But the margin is a median of five days, and every February it is exactly one day — settlement on
the 15th, publication on the 28th, return period starting on the 1st of March. That is not the kind of
margin you want to be relying on.

And the modern answer only applies to the modern regime, which is the whole point of the warning I was
given. FINRA Notice 07-24 introduced a fixed publication calendar in September 2007, for the first time.
Notice 08-13 consolidated collection across NASDAQ, Amex, NYSE, ARCA and OTC in May 2008 and put every
venue on one uniform date. Before September 2007 there was no such thing, and Asquith, Pathak and Ritter
say so in the Journal of Financial Economics, describing precisely that era: press release dates vary
month to month because the exchanges have no required release date, the data are sometimes published as
early as the 19th and sometimes as late as the first of the next month, and Nasdaq has traditionally
released a few days later than NYSE and Amex.

The first of the next month is the day the OSAP return period opens. So in some months the signal was
not public when the holding period began, and for Nasdaq names it could be several days late. Thirty-two
of the 156 months in the 2005-2017 decision window sit in that regime, a fifth of it, and all 180 months
of the early window do. There is no release-date record to identify and drop the bad months with.

I called it FAIL rather than UNRESOLVED deliberately. Unresolved would mean I could not work out the
mapping; I worked it out. There is positive documentary evidence from a JFE paper covering the era that
publication sometimes fell on or after the first day of the return month. What is unknown is the
frequency, not the existence. And the SignalDoc assumption that started all this — bi-weekly with a
four day lag — matches no regime at all: the reporting deadline is two business days, publication is
eight business days now and was unscheduled before 2007. That was the weak link and it was worth pulling.

None of this is a criticism of Chen and Zimmermann. A four-day lag is a defensible modelling choice for
a modern sample and a generous one for an older sample. Our causal bar is stricter than theirs, which is
a statement about us, not about them.

The other thing the audit produced was a correction to my own work. I had written, in the 10B draft, in
STATUS, in PLAN and in memory, that Sign = -1 puts the long leg at port 01. It does not. OSAP multiplies
the signal by Sign before sorting and then names the legs by port number, longportname = max(port$port),
so port 05 is always the long leg regardless of sign. For ShortInterest that means port 05 holds the
lowest raw short interest, which is the long-only reading we actually want — the economics were right
and the label was wrong. The counts settle it without a single return: LS.Nlong equals port 05's Nlong
in 539 of 539 pre-2018 months, and LS.Nshort equals port 01's Nlong in 539 of 539. This is exactly the
error the mechanical proof was specified to catch, and it would have inverted the entire screen if the
timing audit had passed and nobody had checked. All four documents are corrected.

What survives is narrow: a Stage 0 restricted to 2008-2017, entirely inside the consolidated
eight-business-day regime, where the timing is verifiably causal. It costs the early window, so no decay
comparison, and 36 months of the decision window, so less power, and it needs a preregistration written
from scratch rather than an amendment. It also still carries the February one-day margin, the
possibility that a missing mid-month observation silently promotes a month-end one published ten days
into the return month, and Nasdaq's stated practice of retroactively split-adjusting all historical data
on its website, which means the archive is restated rather than immutable.

Not executed. No preregistration written. 490 cells, nothing bought, no vendor contacted, validation and
holdout still never opened.

## Phase 11A COMMODITY_HEDGING_PRESSURE_STAGE0 — closed at the mechanism gate (2026-09-26)

The idea is the oldest one in commodity finance. Producers hedge by selling futures, somebody has to take the other
side, and when hedging demand is heavy the speculator is paid for the insurance. The positioning data are free, weekly
and go back decades, and a long-only investor could in principle hold the commodities where producers are most net
short. That was enough to justify a Stage 0.

The literature took most of it away before any data mattered. The famous relationship is contemporaneous, and a
signal we can trade has to survive the three-day wait until Friday's release. In the form most people mean by hedging
pressure, last week's hedger positions, it predicts nothing: in Kang, Rouwenhorst and Tang's own table, the lagged
weekly slope is -0.07 with t = -0.43. What survives is a slow, specialised variable, the 52-week average, which they
call the insurance premium: t = 3.35 on Legacy data. That is a real result, but it is not a result about COT
positioning in general. Their Legacy hedger category includes swap dealers. When they rerun it on the Disaggregated
producer category, the one that actually corresponds to the mechanism, the coefficient falls from 0.85 (t 2.64) to
0.58 (t 1.61) once expected-return controls are added.

Maréchal's replication is where I nearly got it wrong. The flattened text of his slides lists six panel columns under
three period headings, and both the earlier source note and my own first draft read them one way. The text coordinates
say otherwise: each heading spans two columns. So the 0.25 (t 1.34) I had called pre-2004 is actually post-2004 without
controls, the pre-2004 panel is significant (t 2.26 to 2.36), and the famous -0.37 (t -0.76) is the one post-2004 column
with controls and commodity fixed effects. His Fama-MacBeth table says something different again. The full period is
significant, and the two sub-periods estimated separately are not: 0.92 before 2004 and 1.84 after. And his own summary
has two halves: the Fama-MacBeth results are robust to financialization, and the panel shows the insurance price falling
after it. The accurate statement is narrower than the one I first wrote. No post-2004 estimate in either method is
significant, and the only within-commodity post-2004 estimate is insignificant. That still does not establish a robust
modern effect, and it is what the record now says. Section 15 of the audit lists this correction with the others (the
KRT sample runs to 2014, not 2012, and its controls are basis, past return and idiosyncratic risk, not "momentum").

Every one of those numbers is a costless long-short cross-section over twenty-odd futures, aligned to Tuesday
positions that are not public until Friday. Nobody reports the long leg, nobody measures it after the release, and nobody
trades it through a London-listed ETC that holds physical gold instead of a futures position, or through a WisdomTree oil
product whose index changed underneath it in August 2020. Everything we would add pushes the same way: later
information, more basis, more cost, less power. The ex-ante power calculation, done from published magnitudes rather
than any data, puts the realistic test at roughly 5 to 25 percent under modern attenuation. A null would be weakly
informative, and a pass would be one more lucky draw in a 490-cell search.

The pattern from Phases 8 to 10 repeats in a new asset class. The documented effect is a long-short spread, and the
long-only leg that a small book could hold is either unreported or much weaker.

Two workstreams were stopped rather than finished, and the audit says so in plain words. The archived release
schedules came back rate-limited and incomplete: 2008 and 2025 are unusable, 2009 is nearly empty, no release map was
built, and what was recovered are tentative schedules, not a record of releases. The product agent was interrupted:
the partial metadata is kept under an INTERRUPTED_UNVERIFIED_ARTIFACT label, its CSV is malformed and deliberately
unrepaired, and no mapping from CFTC contracts to products was certified. Neither could have changed the answer. A
perfect release map only confirms that we would see the signal no earlier than the papers did, and a perfect product
list only removes a friction.

One hygiene change is prospective. The papers downloaded for this phase stay on this machine and out of git, and
SOURCES.txt carries the references and the table locations instead. Earlier phases' committed papers are left as they
are.

The tempting continuations all belong to the same family: the position-change premium that partly survives the
release, managed-money positioning, a different smoothing window, positioning conditioned on carry. Each would be the
failed mechanism plus one more free choice made after reading the results. They are written down as excluded.

0 cells. 490 cumulative. No commodity return of any date loaded. Equity validation and holdout still never opened.

## Phase 11B NATIVE_BLOCKCHAIN_FUNDAMENTALS_STAGE0 — closed at the mechanism gate (2026-09-26)

The appeal of on-chain data is its transparency. Every Bitcoin transaction and every stablecoin mint is public and
timestamped, so perhaps a patient retail investor could see demand forming before it reached the price. After 388
crypto cells built from exchange data, that seemed worth one careful look at a genuinely different information source.
The brief allowed three kinds of variable: network activity, stablecoin supply and exchange reserves. It asked one
question. Does any of them deserve a strategy cell? None does. The reasons differ, and the record now keeps them
apart.

Exchange reserves stop at the label audit, before the evidence matters. The mechanism is plausible: coins moved onto an
exchange are coins someone may sell. But every measure of it depends on knowing which addresses belong to an exchange,
and that knowledge is discovered over time and written back into history. Glassnode's own documentation says a metric
has no point-in-time history before its PIT tracking was switched on, which for most metrics was July 2025. Coin
Metrics says its standard flows change "when new entity addresses are discovered later". Its flow definition uses
"addresses currently known to belong to the entity". Exchange proof-of-reserve address lists begin in November 2022.
Everything published on reserves applies today's labels to earlier years. That branch is PIT_LABEL_BLOCKED, and it
would be blocked however good the published results looked.

Network activity is a different kind of failure. The raw counts are among the cleanest data in the whole programme:
Bitcoin transactions can be rebuilt from raw blocks without any label. The evidence is what is missing. The one
full-text Bitcoin-level predictive test I could read, in Liu and Tsyvinski's working paper, has an R-squared of zero at
every horizon from one to seven days. Their published version calls network factors exposures and keeps "forecast" for
momentum and attention. The positive results are weekly long-short sorts across hundreds of small coins, gross of
costs. The most careful recent test (Sakkas and Urquhart) removes the activity-based factors once the market is in the
model. There is a real semantic problem too: addresses are not users, and batching, inscriptions, Runes, Lightning,
custody and rollups all change what a count means. I first recorded that as a data block and have downgraded it to a
documented risk. The decision rests on the evidence.

Stablecoin supply needed the most careful correction. In the first pass I let a true statement about the *economic*
aggregate stand for the whole mechanism. Three objects need separating:
- the mint and burn events of a fixed contract;
- that contract's total supply;
- the circulating aggregate across issuers, chains, bridges and treasuries.

The first two can be rebuilt from the chain without any label. They need care — USDT's issue, redeem and destroy
functions emit no Transfer event, so the obvious log replay would be silently wrong — but no label. The aggregate's
difficulties (treasury inventory, chain swaps, bridges, double counting) are problems of definition, not of wallet
labels leaking from the future. So the label-free construction is judged on its evidence, and the evidence is weak. Wei
finds no subsequent return effect, only volume. Ante, Fiedler and Strehle's event study shows markets falling the week
before issuance and no significant raw returns in the next day. Their USDC and GUSD subsamples are insignificant, and
the authors themselves suggest that demand triggers the issuance. The transfer study's effects depend on whether sender
and receiver are exchanges, treasuries or unknown, so it is label evidence, not aggregate evidence. Kristoufek and Lyons
and Viswanath-Natraj find supply responding to prices, including on the Griffin-Shams window. The plausible chain runs
from crypto demand or stress to a mint, not from a mint to predictable appreciation. MECHANISM_TOO_WEAK, not
PIT_LABEL_BLOCKED.

That gives the phase its logic. One attractive branch is independently blocked by labels. The two branches that are
label-free and reconstructable do not have strong enough prior evidence. So the programme outcome is
MECHANISM_TOO_WEAK. The decision code encodes that ordering, and a test checks the recorded decision against it. The
sentence of record is narrow on purpose: no native on-chain mechanism meeting the programme's causal, reproducible,
long-only and small-capital constraints had strong enough prior evidence for Stage 1. It does not say on-chain
information is useless.

One factual dispute was settled by measurement rather than by either side's say-so. The finalization brief said Coin
Metrics' exchange-flow entries are not flagged for Community access. One sub-audit said flows were Pro-only; another
said they were free. Metadata requests and zero-row probes show all three are partly right. The daily BTC/ETH series are
flagged and accessible (HTTP 200, no rows requested). The hourly series is refused ("forbidden"). The flow product
family is professional. The record says exactly that and classifies the flows as vendor-transformed and label-dependent.
Access never mattered to the decision, because the accessible series is the restated one.

Two things from the plumbing are worth keeping. A Bitcoin day can be closed exactly: median-time-past never decreases,
so once the block six deep has an MTP past midnight, no block stamped the previous day can ever appear. And the venue
facts moved: Binance stopped taking new EU/EEA spot business on 1 July 2026, so the fee the crypto phases assumed is not
available to a European resident. At the licensed venues' retail fees, weekly switching would cost between a sixth and
nearly half of the position a year.

Process notes. Six sub-audits ran in parallel, and their search-engine summaries produced at least two false
statements: Chainalysis labels in Makarov and Schoar, and network metrics in Yae and Tian's abstract. Both were caught
against primary text. Yae and Tian is kept only as general out-of-sample caution about attention and volume. Every
decisive number was re-read in full text or the official abstract. Captures of ETP product pages that might carry prices
were quarantined unread. The zero-of-33 "qualifying rows" count is kept as a summary, not as the reason for the
decision.

0 cells. 490 cumulative. No price, return or on-chain metric value loaded. Old crypto holdout, equity validation and
equity holdout still closed.


## Phase 11C TREASURY_TERM_PREMIA_STAGE0 — closed at the real-time evidence gate (2026-09-27)

Treasury duration timing looked like a good fit for this account: unlevered, long-only, monthly, cheap instruments, and
a mechanism with some of the most famous in-sample results in empirical finance. When the curve pays well for holding
duration, hold duration; when it does not, stay short. The question was whether that survives the conditions we would
actually trade under. It does not, at least not on the evidence that exists.

The in-sample case is not in doubt. Cochrane and Piazzesi's tent-shaped factor explains a third or more of one-year
excess returns on unsmoothed Fama-Bliss data, the loadings recur in every subsample, and Bauer and Hamilton, who
dismantle most of the other bond-predictability claims with a proper bootstrap, explicitly concur that the core factor
is stable. Rebonato and Nyholm's recent paper argues it is not an overfitting artefact. I accept all of that.

The trouble starts when an investor has to estimate the coefficients as the data arrive. Cochrane and Piazzesi's own
real-time check already earned only about half the full-sample trading profit. Gargano, Pettenuzzo and Timmermann's
2019 paper, the strongest positive study, is also the clearest witness against the simple version. In their Table 3,
the constant-coefficient CP regression has a monthly out-of-sample R-squared of -1.58% to 0.73% over 1990-2011. In
Table 5, a long-only investor using it gains nothing measurable. Their large certainty-equivalent gains come from
stochastic-volatility and time-varying-parameter machinery, a macro factor built from revised data, and portfolio
weights between -2 and 3. Hodrick and Tomunen find CP loses to historical averages out of sample. Sarno, Schneider and
Wagner call their own result the bond-market Goyal-Welch. Thornton and Valente, whose full text I still could not
obtain, reached the same verdict for a dynamic allocator.

The simple forward spread does a little better, and it deserves to be stated precisely because it is the one thing
that nearly survived. In the same GPT table, the Fama-Bliss spread in a long-only bond-versus-bill allocation earns
0.46% and 0.67% a year of certainty equivalent for the four- and five-year bonds, and nothing at two and three years.
That is recursive and out of sample. It is also gross of costs, ends in 2011, comes from one study, and is contradicted
at the annual horizon. Two switches a year through a converting Trading 212 path would cost 80 basis points. And
there is nowhere left to test it: 1990-2011 is the literature's own window, this programme has already read Treasury
ETF returns for most of 2004-2019, and what remains overlaps the locked 2018-2026 windows and the 2022 bond crash
everyone remembers. At the literature's best R-squared, a long-only test over the remaining fifteen years would have
roughly a one-in-four chance of detecting a true effect. A cell spent there would most likely end ambiguous.

The data work, by contrast, came out cleaner than expected, and I measured it rather than trusting the sub-audit. H.15
constant-maturity yields are par yields, not zero-coupon yields, so they cannot produce canonical CP forwards. But they
are genuinely point-in-time: comparing ALFRED vintages from 2005, 2010 and 2018 with today's, blind and by exact string
equality, found between zero and three revised dates per tenor across 55 years, the largest 10 basis points. Two
exceptions matter. The 20-year history before 1993 and the 30-year's 2002-2006 gap were filled in after the fact, so a
naive download of those tenors is not real-time. FRED also archived month-end observations one to six days late in
2006-2011, so a backtest has to gate on the first vintage containing the date, not on the evening the Fed posted it.
GSW's smoothed curve is both a revised vintage and, per Cochrane and Piazzesi's 2008 table, destructive of the tent
signal. ACM term premia are re-estimated on the full sample with no public vintages: a value dated 2005 in today's file
is not something anyone knew in 2005.

So the decision is REAL_TIME_OOS_EVIDENCE_TOO_WEAK, not MECHANISM_TOO_WEAK and not PIT_DATA_BLOCKED. The binding class
has free, point-in-time data, and the mechanism has strong in-sample support; what is missing is real-time, long-only,
after-cost evidence, and the independent data to produce it. I froze the one construction that would be tested if
outside evidence reopens the question (10-year minus 1-year CMT, expanding-window sign rule, 7-10 year versus 1-3 year,
against a fixed 50/50 blend, with a bond-momentum duplication check), so that a reopening cannot become a search.

Process notes. Five sub-audits ran in parallel. Each decisive number above was re-read in the local full text. The data
sub-agent's provisional classification was superseded by measurement, and two of its series-start claims were wrong.
One file labelled Thornton-Valente turned out to be a different Thornton paper. The ETF sub-agent saw a few incidental
quotes and discarded them unrecorded.

0 cells. 490 cumulative. No return series loaded, no yield-curve signal computed. Equity validation, equity holdout and
old crypto holdouts still closed.
