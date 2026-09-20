@AGENTS.md

# Claude Code continuation rules

## Mission
Continue the quantitative-research program already present in this repository. This is a continuation, not a restart.

The objective is to discover the strongest evidence-supported, realistically executable quantitative strategy available under the project constraints. Do not optimize for finding *some* profitable backtest. It is acceptable for the research program to conclude that no strategy qualifies.

A failed hypothesis is NOT a reason to end the session. Treat rejection as a research result, record it, preregister the next genuinely distinct hypothesis, and continue working.

## Mandatory startup / resume procedure
At the start of every session:

1. Inspect the working directory before changing anything.
2. Read `STATUS.md` first.
3. Read `PLAN.md`.
4. Read the newest relevant entries in `EXPERIMENTS.md`.
5. Read the newest relevant entries in `RESEARCH_JOURNAL.md`.
6. Read the full quantitative research protocol referenced by `AGENTS.md` if it has not already been loaded.
7. Inspect the latest reports and code paths named in `STATUS.md`.
8. Run `python -m unittest discover -s tests -v` before substantive new research.
9. Resume from the documented `NEXT EXPERIMENT`; do not recreate prior work from memory.

Disk state and experiment artifacts are the source of truth. If this file conflicts with a newer explicit entry in `STATUS.md` about factual research state, use the newer state while preserving the behavioral rules here.

## Existing checkpoint that must NOT be repeated
At handoff, the project has already tested 119 hypotheses/configurations/architectures.

Completed and documented work includes:
- E001-E003: spot momentum/reversal/flow screening plus robustness work.
- E004-E009: funding/carry, sizing, economic and risk-control diagnostics.
- E010-E011: directional perpetual momentum/reversal screening and survivor audit.
- 33 automated tests pass at the latest checkpoint.
- Two genuine execution/risk defects were corrected and superseded runs were retained.

Do NOT rerun these experiments merely to become familiar with them.
Do NOT restart the strategy search from BTC/ETH momentum.
Do NOT retune rejected momentum/reversal lookbacks, delays, thresholds, or cost assumptions in an attempt to rescue them.
Do NOT promote ETH carry without new evidence that resolves its documented opportunity-cost and operational weaknesses.

A prior experiment may be rerun only when necessary for environment compatibility, a newly discovered code/data defect, a regression test, exact reproducibility verification, or a preregistered comparison that genuinely requires the old baseline. Such a rerun is verification, not a new hypothesis, unless the economic mechanism or architecture is genuinely new.

## Current locked-data state
Preserve the chronological research design.

At the handoff checkpoint:
- development data: 2022-2024;
- 2025 validation: unopened for strategy selection;
- 2026-01-01 through 2026-08-31 final holdout: not downloaded/inspected;
- architecture: not frozen;
- no live capital is committed;
- no broker order adapters or live-trading code exist.

Do not open validation merely because a development result looks attractive.
Do not acquire or inspect the final holdout until the protocol's architecture/candidate-set freeze is satisfied.
Never use validation or final results to silently redesign a failed candidate.

## Immediate continuation
The next registered independent branch is aggregate aggressive-flow information on perpetuals using already acquired taker-volume data and the corrected signed/funding ledger.

Start there.

Before seeing its result:
1. preregister the economic mechanism, exact feature definitions, candidate count, holding/execution rules, cost cases, falsification tests, uncertainty procedure, and advancement gates;
2. assign the next experiment ID;
3. record it in `EXPERIMENTS.md` / `RESEARCH_JOURNAL.md`;
4. implement tests for causal alignment and execution semantics;
5. run the cheapest diagnostic first;
6. only spend more compute on survivors.

Do not make the flow branch a disguised parameter sweep. OHLCV/taker-volume aggregates do not justify claims of true HFT or queue-position alpha.

## Autonomous research loop
Repeat this loop without waiting for user approval for ordinary local research actions:

1. READ STATE — confirm latest status, experiment registry, data availability, and unresolved defects.
2. SELECT ONE DISTINCT MECHANISM — choose the highest-value untested economic hypothesis supported by available or legitimately obtainable data. Prefer mechanisms with plausible persistence and executable economics.
3. PREREGISTER — mechanism, universe, features, horizon, execution timing, search budget/trial count, costs, benchmark, gates, uncertainty/robustness tests, and locked data segments.
4. IMPLEMENT AND TEST — reuse common signal/accounting/risk code; add regression tests with bug fixes; preserve causality; do not weaken tests to make a candidate pass.
5. RUN CHEAP FALSIFICATION — reject weak mechanisms early, include realistic costs, track all trials and multiplicity burden.
6. AUDIT SURVIVORS — uncertainty, delay, cost stress, parameter stability, benchmark/opportunity cost, regimes, drawdown/tails, execution feasibility.
7. DECIDE — REJECTED, RESEARCH-PROMISING, PAPER-TRADING ELIGIBLE, or the later protocol-defined stage.
8. PERSIST — append the experiment/outcome and update `RESEARCH_JOURNAL.md`, `PLAN.md`, and `STATUS.md`; preserve hashes, artifacts, reports, and superseded results.
9. CONTINUE — if rejected, immediately preregister the next distinct mechanism. If blocked by account-specific facts, continue independent work that does not depend on those facts.

## What "continue autonomously" means
Do not stop after one failed experiment, one bug fix, one report, one rejected candidate, one promising candidate, one data acquisition, or one completed research branch.

A normal negative result should lead directly into the next research loop. Status reports are checkpoints, not stopping points.

Only stop the overall run when one of these is true:

A. A genuinely hard blocker requires user action, credentials, a paid purchase, a destructive/irreversible operation, or authorization to expose capital.

B. The executable research space has been responsibly exhausted under the protocol and further search would be statistically irresponsible, duplicative, or unsupported by available data. Conclude explicitly that no qualifying strategy has been found.

C. A candidate set has survived the required development and validation gates, the architecture and selection procedure are frozen, the adversarial audits are complete, and the protocol permits the next human-controlled stage. Do not equate this with guaranteed profitability.

D. The environment itself cannot continue (for example an external quota or unrecoverable tool failure). Before stopping, save an exact resume point and the next command/experiment in `STATUS.md`.

## Do not force success
Never interpret persistence as permission to keep retuning a failed family until it becomes significant, increase leverage to manufacture return, inspect locked data early, hide failed trials, weaken costs, change gates after results, cherry-pick assets/dates, call a backtest reliable, or claim a global optimum has been proven.

The goal is the best defensible strategy discovered by a disciplined search, not a guaranteed winner.

If a first strong candidate emerges, preserve it as a frozen benchmark and continue enough independent research to determine whether a meaningfully better or diversifying candidate exists BEFORE consuming the final holdout. Track the additional multiple-testing burden.

## Research directions after the registered aggressive-flow branch
Do not follow a rigid checklist if evidence points elsewhere. Prefer genuinely distinct mechanisms over parameter variations. Examples, when justified:
- spot/perpetual or cross-asset lead-lag;
- basis/funding state information beyond the rejected simple carry architecture;
- residual/cross-sectional relative value after expanding the universe with survivorship-aware data;
- volatility/liquidity-conditioned signals;
- intraday seasonality with causal timestamps;
- execution-aware ensembles only after independent components survive;
- slower Trading 212-compatible equity/ETF mechanisms if crypto intraday economics remain poor.

ML is downstream of signal evidence, not a substitute for it.

## Account-specific blockers
Exact account fees/maintenance remain unverified at the current checkpoint. Do not repeatedly ask the user for the same unavailable values and do not invent them.

Treat these facts as promotion blockers only for analyses that truly depend on them. Continue public-data and account-independent research.

## Safety / capital boundary
No live trading is authorized. Do not submit live orders, enable live mode, request/expose secrets unnecessarily, store credentials in source files, or convert research results into capital exposure.

Paper/shadow/tiny-live stages require the protocol's gates; any real-money transition requires explicit human authorization.

## Long-context behavior
This is a long-horizon task. Do not wrap up simply because the context window is getting large.

Before compaction or a context transition:
1. finish or safely checkpoint the current atomic experiment;
2. update `STATUS.md`, `EXPERIMENTS.md`, `RESEARCH_JOURNAL.md`, and `PLAN.md`;
3. record exact commands, IDs, artifacts, failures, and next experiment;
4. continue from those files after context refresh.

Use the filesystem as durable memory.

## Communication
Do not spend the session narrating hypothetical plans. Use tools, edit files, run code, inspect outputs, and perform research.

Keep user-facing updates concise and evidence based. The reproducible state on disk is the primary work product.

At major checkpoints, include:
CURRENT BEST CANDIDATE:
WHY IT MAY WORK:
STRONGEST EVIDENCE:
BIGGEST WEAKNESS:
WHAT COULD INVALIDATE IT:
NEXT EXPERIMENT:
CURRENT VERDICT:

Then continue working unless a terminal condition above has actually been reached.
