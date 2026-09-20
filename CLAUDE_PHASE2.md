# CLAUDE_PHASE2.md — Information-Frontier Research Mandate

## Purpose

This file extends the existing quantitative research mandate after the first research program responsibly exhausted the currently tested OHLCV/funding/slow-factor search space.

This is NOT a restart.

At the Phase 2 handoff:
- 243 counted hypotheses/configurations/architectures have been tested;
- fourteen economic families have been explored across crypto and ETF branches;
- no strategy qualifies for promotion;
- 62 automated tests pass at research close;
- 2025 validation remains unopened;
- the 2026-01-01 through 2026-08-31 final holdout has never been downloaded or inspected;
- no paper/live trading or capital exposure has occurred;
- no credentials were used.

The Phase 1 conclusion is valid and must be preserved:
**No strategy currently passes under the existing information set.**

Phase 2 may reopen research only by materially changing the information set, market structure evidence, universe, or data quality in a way that can answer questions the prior data could not.

---

# 1. PRIMARY MISSION

Expand the information frontier and search for genuinely new, economically plausible alpha.

The first priority is:

**BTC/ETH perpetual microstructure research using order-book and/or trade-level data.**

The motivation is NOT to rescue the rejected hourly taker-flow reversal by using maker orders.

The prior aggregate hourly reversal edge was approximately one basis point and was already too small relative to realistic transaction costs.

Therefore, new microstructure data must be used to discover and test **new conditional signals** that could plausibly predict short-horizon returns, execution quality, fill probability, adverse selection, or temporary price pressure.

The objective is:

> Determine whether higher-resolution market-state information creates a tradeable edge that was invisible in the aggregate OHLCV/funding data.

If it does not, reject the branch and continue to the next genuinely distinct information expansion.

---

# 2. DO NOT REPEAT PHASE 1

Do NOT:
- rerun the 243 completed hypotheses just to become familiar with them;
- reopen rejected momentum/reversal grids;
- retune the cross-sectional flow family to rescue its 2020 dependence;
- retune carry to beat the short-rate reference;
- retry ETF momentum/trend on the same development information;
- repackage an old signal with a new parameter and call it a new mechanism;
- use 2025 validation as new development data;
- download or inspect the 2026 final holdout;
- weaken multiplicity corrections or cost assumptions because Phase 1 found no winner.

Prior work is evidence, not a suggestion.

Use `RESEARCH_CONCLUSION_20260908.md`, `STATUS.md`, `EXPERIMENTS.md`, `RESEARCH_JOURNAL.md`, `PLAN.md`, reports, experiment outputs, and existing tests as the source of truth.

New trial counts begin at **244** and are added to the cumulative research burden.

---

# 3. MANDATORY PHASE-2 STARTUP

Before substantive new research:

1. Inspect the repository.
2. Read the root `CLAUDE.md`, `AGENTS.md`, and any applicable instruction files.
3. Read:
   - `RESEARCH_CONCLUSION_20260908.md`
   - `STATUS.md`
   - `PLAN.md`
   - latest relevant entries of `EXPERIMENTS.md`
   - latest relevant entries of `RESEARCH_JOURNAL.md`
4. Inspect the latest reports and code named by those files.
5. Run:
   `python -m unittest discover -s tests -v`
6. Verify the latest test count and repo state.
7. Create a Phase 2 preregistration section before observing any new return results.

Do not treat this handoff text as more authoritative than newer factual state already persisted on disk.

---

# 4. DATA-ACQUISITION PRINCIPLE

Acquire new data only when it answers a specific preregistered research question.

Prefer:
1. free exchange-native historical data;
2. free official APIs;
3. open institutional-quality data;
4. paid data only when free data cannot answer a high-value question.

Recurring paid data/software budget remains:
**EUR 50/month maximum total.**

Before recommending or using a paid feed:
- identify the exact deficiency in free data;
- explain what hypothesis cannot be tested without it;
- quantify the expected informational benefit;
- compare the cheapest adequate alternatives;
- document why the expected benefit justifies the cost.

Do not subscribe or purchase automatically.

---

# 5. FIRST INFORMATION-FRONTIER BRANCH — MICROSTRUCTURE

## 5.1 Candidate data

Investigate the best legitimately obtainable high-resolution BTCUSDT and ETHUSDT perpetual data, such as:
- bookTicker;
- partial/full depth snapshots;
- depth updates;
- aggregate trades;
- individual trades where available;
- quote changes;
- best bid/ask history;
- spread;
- displayed depth;
- trade aggressor side;
- order-book imbalance;
- microprice inputs;
- short-horizon realized volatility.

Do not claim queue position, hidden liquidity, cancellation intent, or executable passive fills unless the available data genuinely supports those claims.

## 5.2 Data-integrity requirements

Document:
- source;
- timestamps and timestamp semantics;
- exchange vs local receive time where relevant;
- snapshot/update reconstruction rules;
- dropped sequence numbers;
- duplicate messages;
- book resets;
- crossed/locked books;
- symbol/filter changes;
- missing intervals;
- clock alignment between trades and book updates;
- whether historical data represents full event streams or sampled snapshots.

Never silently forward-fill book states through unknown gaps.

If order-book reconstruction cannot be trusted, stop that specific implementation and use only analyses supported by the available data.

## 5.3 Candidate microstructure mechanisms

Preregister bounded, economically interpretable families before testing.

Examples include:
- best-level or multi-level order-book imbalance;
- microprice deviation from mid;
- aggressive trade imbalance conditioned on displayed liquidity;
- signed flow relative to resting depth;
- spread-state transitions;
- temporary price pressure after aggressive sweeps;
- replenishment / resilience after liquidity shocks where observable;
- short-term lead-lag between trade flow and quote movement;
- volatility-conditioned flow;
- liquidity-conditioned reversal/continuation;
- cross-asset BTC/ETH microstructure lead-lag;
- basis or perp/spot microstructure dislocation if synchronized data exists.

These are examples, not a mandatory grid.

Do NOT brute-force thousands of arbitrary combinations.

---

# 6. EXECUTION-AWARE RESEARCH FROM THE START

For every short-horizon candidate, distinguish:

A. predictive edge;
B. gross trading edge;
C. executable edge;
D. capacity.

A statistically significant mid-price forecast is NOT automatically a strategy.

Model:
- bid/ask crossing;
- maker/taker fees;
- fill probability;
- queue uncertainty if passive;
- adverse selection;
- partial fills;
- missed fills;
- latency;
- signal decay;
- minimum notional;
- price/quantity precision;
- order amendments/cancellations;
- rate limits.

For passive strategies:
- never assume every resting order fills;
- never assume favorable fills without modeling conditional adverse selection;
- compare optimistic/base/stressed fill assumptions;
- use deliberately conservative fills if exact queue position is unavailable;
- reject any strategy whose profitability depends on an implausibly high fill rate.

For aggressive strategies:
- cross the spread explicitly;
- include fees and slippage;
- reject signals whose edge is not materially larger than execution uncertainty.

---

# 7. RESEARCH HORIZONS

The user's preference for seconds/minutes remains a preference, not a requirement.

Investigate horizons that the available data and local retail infrastructure can realistically support.

Explicitly classify each branch as:
- true HFT — almost certainly infeasible here;
- retail-accessible low-latency systematic trading;
- short-horizon intraday systematic trading;
- slower systematic trading.

Reject alpha that requires exchange colocation, nanosecond/microsecond reaction, exact queue priority, or infrastructure that this project cannot operate.

---

# 8. PREREGISTRATION STANDARD

Before each new branch, record:

- experiment ID;
- cumulative hypothesis count;
- economic mechanism;
- who may be providing the other side;
- why the edge may persist;
- exact universe;
- exact data;
- sample dates;
- target;
- features;
- forecast horizon;
- execution delay;
- order type assumption;
- cost assumptions;
- fill model;
- number of candidate variants;
- benchmark;
- advancement gate;
- rejection gate;
- uncertainty test;
- multiplicity treatment;
- parameter-stability test;
- latency/delay stress;
- data segments that remain locked.

Do not modify gates after seeing the result.

If a genuine implementation defect is found:
- reproduce it with a failing test;
- fix it;
- rerun affected work;
- preserve the superseded artifacts;
- do NOT count the rerun as a new hypothesis unless the economic specification changed.

---

# 9. CHEAP-FIRST MICROSTRUCTURE PIPELINE

Use progressive falsification.

## Stage A — signal diagnostics
Measure, as appropriate:
- information coefficient;
- conditional forward return;
- monotonicity by feature quantile;
- signal decay;
- hit rate;
- turnover;
- spread state;
- liquidity state;
- time-of-day stability;
- regime stability.

Use causal features only.

## Stage B — simple executable ledger
Only for signals that survive Stage A:
- explicit bid/ask;
- real fees;
- fixed predeclared delay;
- conservative fill assumptions;
- no leverage initially;
- bounded position size.

## Stage C — uncertainty / multiplicity
Use appropriate:
- block bootstrap;
- confidence intervals;
- multiple-testing correction;
- trial-count-aware Sharpe deflation;
- placebo/randomization tests where useful.

## Stage D — hostile execution audit
Try:
- added latency;
- random latency;
- missed fills;
- lower maker fill rates;
- higher adverse selection;
- spread widening;
- fee increases;
- reduced depth;
- stale-book events;
- signal perturbation;
- parameter neighbors.

Do not optimize to the hostile audit.

---

# 10. PROMOTION STANDARD FOR MICROSTRUCTURE

Do not promote a short-horizon candidate because it has a high gross Sharpe.

Require evidence that:
- predictive signal is statistically credible;
- effect survives realistic execution;
- edge exceeds cost-model uncertainty by a meaningful margin;
- delay does not destroy it;
- performance is not concentrated in one month/regime/event;
- no narrow parameter spike;
- no hidden reliance on impossible fills;
- capacity is adequate for at least the intended small account;
- tail and drawdown risk are acceptable;
- the economic mechanism is plausible.

If edge is only a few basis points and cost uncertainty is comparable, treat the result as unresolved or rejected.

---

# 11. VALIDATION LOCK

The original chronological lock remains in force.

Do NOT analyze 2025 validation until:
- a candidate architecture is frozen;
- feature construction is frozen;
- execution model is frozen;
- candidate selection process is frozen;
- development-side uncertainty/multiplicity audits pass;
- there is a written preregistered validation gate.

Do NOT download or inspect the 2026 final holdout until the protocol explicitly allows it after validation and architecture freeze.

A Phase 2 candidate can be very exciting and still be development-only.

---

# 12. WHAT TO DO IF MICROSTRUCTURE FAILS

A failed microstructure branch is NOT the end of Phase 2.

Record it, then change the information set again.

Possible next expansions, when justified:

### A. broader crypto cross-section with better history
Acquire additional pre-2020 or post-2024 development regimes without touching locked 2025/2026 candidate-validation segments.

Goal:
determine whether the relative-flow effect was genuinely a transient 2020 phenomenon or an effect requiring broader regime coverage.

### B. synchronized spot/perpetual microstructure
Test transient basis, lead-lag, flow migration, and liquidity imbalance across venues/instruments.

### C. options / volatility information
Only if legitimately accessible, data-quality adequate, and executable for the account.

Possible information:
- implied volatility;
- skew;
- term structure;
- realized/implied dislocations.

Do not assume options execution is accessible.

### D. alternative markets / Trading 212-compatible slower alpha
Only with corporate-action-safe, checksum-grade or otherwise auditable history.

Potential families:
- cross-sectional equity/ETF residuals;
- medium-term trend;
- overnight/intraday effects;
- factor combinations;
- volatility-managed allocation;
- relative-value baskets.

### E. external information
Only if causally timestamped and economically justified:
- macro releases;
- futures positioning;
- liquidations;
- open interest;
- exchange inflows/outflows;
- news/sentiment;
- on-chain data.

Avoid weak alternative-data storytelling.

---

# 13. ML POLICY

Do not begin with deep learning.

First demonstrate that the new information set contains stable predictive structure using transparent diagnostics.

Then compare:
1. simple thresholds / ranks;
2. regularized linear/logistic models;
3. trees / gradient boosting;
4. more complex temporal models only if the simpler models leave stable residual predictive information.

Use nested chronological validation for model selection.

Track every major model/feature family as part of the hypothesis search burden.

Complexity must materially improve executable OOS economics, not just development fit.

---

# 14. AUTONOMOUS CONTINUATION LOOP

Repeat without asking the user to choose ordinary research decisions:

1. READ STATE.
2. IDENTIFY the highest-information-gain untested mechanism.
3. PREREGISTER.
4. ACQUIRE only required data.
5. VALIDATE data integrity.
6. IMPLEMENT causal diagnostics.
7. TEST.
8. FALSIFY cheaply.
9. AUDIT survivors aggressively.
10. RECORD every result.
11. UPDATE:
    - `STATUS.md`
    - `PLAN.md`
    - `EXPERIMENTS.md`
    - `RESEARCH_JOURNAL.md`
12. CONTINUE to the next distinct mechanism after rejection.

Do not stop after one failed family.
Do not stop after one promising result.
Do not stop after one report.
Do not stop merely to summarize progress.

Progress updates are checkpoints, not completion.

---

# 15. STOP CONDITIONS

Phase 2 may stop only when:

A. A genuine blocker requires user action, credentials, payment, destructive permission, or real-capital authorization.

B. The newly accessible information frontier has been responsibly exhausted and further testing would be duplicative, statistically irresponsible, or unsupported by available data.

C. A candidate/candidate set survives the protocol-defined development and validation gates, architecture is frozen, adversarial audits are complete, and the project is ready for the next human-controlled stage.

D. The environment/quota prevents further execution. Before stopping, persist the exact resume state and next action.

"No candidate qualifies" remains a valid scientific outcome.

---

# 16. NEVER FORCE A WINNER

The instruction to continue autonomously does NOT permit:
- endless parameter mining;
- hidden trial resets;
- uncounted feature searches;
- early validation access;
- early final-holdout access;
- cost-model weakening;
- impossible execution;
- leverage inflation;
- cherry-picking;
- survivorship-biased universe changes;
- silently deleting bad periods;
- promoting a candidate because "something has to win."

The purpose of Phase 2 is to create NEW INFORMATION, not more attempts on the same information.

---

# 17. CAPITAL / SAFETY

No live trading is authorized.

Do not submit orders or enable capital exposure.

Do not request secrets unless a future protocol stage genuinely requires them.

Read-only account facts may be requested only when a candidate reaches a gate that depends on them.

Initial research examples may model approximately EUR500/USDT500 scale, but actual committed capital remains zero.

15x leverage remains an absolute ceiling, not a target.

Microstructure research should initially use no leverage unless there is a compelling reason to test otherwise.

---

# 18. REQUIRED MAJOR-CHECKPOINT REPORT

At important milestones, update the durable files and report:

CURRENT PHASE:
CUMULATIVE HYPOTHESES TESTED:
CURRENT BEST CANDIDATE:
NEW INFORMATION SET:
WHY IT MAY WORK:
STRONGEST EVIDENCE:
BIGGEST WEAKNESS:
EXECUTION FEASIBILITY:
WHAT COULD INVALIDATE IT:
LOCKED DATA STATUS:
NEXT EXPERIMENT:
CURRENT VERDICT:

Then continue working unless a valid stop condition has actually been reached.

---

# 19. FIRST ACTION

Begin immediately.

1. Read the Phase 1 conclusion and current durable state.
2. Run the existing tests.
3. Create the first Phase 2 preregistration starting at hypothesis/trial count 244.
4. Determine which free Binance order-book/trade-level datasets are sufficiently complete and reconstructible for BTCUSDT/ETHUSDT perpetual microstructure research.
5. Document the data-quality limitations before testing returns.
6. Acquire only the minimum data needed for a bounded first diagnostic.
7. Test one or a few high-value microstructure mechanisms with a strict search budget.
8. Reject weak ideas early.
9. Audit survivors with execution realism from the beginning.
10. Continue autonomously through distinct information-frontier branches.

Do not touch 2025 validation.
Do not download or inspect the 2026 final holdout.
Do not declare victory early.

Find new information, then try to destroy every edge it appears to reveal.
