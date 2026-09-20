# PHASE6_PLAN - institutional US equity/ETF alpha discovery (started 2026-09-09)

## 0. State inherited from Phases 1-5

Crypto discovery is CLOSED: 388 hypotheses, no validation candidate, E040 frozen (hash 9928aa46...), slow trend failed independent cohort replication (Phase 5), crypto 2025 LOCKED, crypto 2026 UNTOUCHED. Nothing in Phase 6 reopens, modifies or combines with that branch.

## 1. Objective

Determine whether systematic US equity return streams exist that survive survivorship-safe data, point-in-time universes, realistic Trading 212 Invest execution, chronological validation, concentration analysis, hierarchical multiple-testing correction and adversarial review. Two tracks: Track A deployable long-only (Trading 212 Invest, unlevered, fractional, USD instruments); Track B RESEARCH_ONLY_MARKET_NEUTRAL long/short diagnostics that establish whether a signal ranks returns. Track B is never labelled deployable.

## 2. Data plan

- Free, survivorship-free, portfolio-level: Kenneth French library (acquired 2026-09-09, manifest data/metadata/phase6_french_manifest.json, CRSP vintage 202607). Use: family-level Stages 1-2 only; maximum classification FACTOR_EVIDENCE.
- Paid, survivorship-safe, stock-level: Norgate Data US Stocks Platinum (PHASE6_DATA_PURCHASE_RECOMMENDATION.md; awaiting user authorisation). Use: Stages 3-7, Track A portfolios, costs, capacity, small-capital simulation.
- Free ticker downloads: engineering tests only, never evidence.
- Lock: PHASE6_EQUITY_DATA_LOCK.md (development < 2018-01-01; validation 2018-2021; holdout 2022-01-01..2026-08-31), enforced by research/phase6_lock.py.

## 3. Funnel and gates (mandate section 53)

| Stage | Data | Output | Advance if |
| --- | --- | --- | --- |
| 1 Signal diagnostics | French deciles/quintiles/industries; later stock panel | HAC t-stat of the family premium, era signs, block-bootstrap CI, IC at stock level | FACTOR_EVIDENCE gates (E050 preregistration) |
| 2 Cross-sectional monotonicity | same | Spearman of bucket mean return vs rank; quintile spreads | rho >= 0.7 (decile sorts) |
| 3 Gross portfolio | stock panel | top-N long-only and L/S gross returns, turnover | positive gross alpha vs EW universe with t >= 2 |
| 4 Realistic costs | stock panel + PHASE6_COST_MODEL.md | net returns in three cost cases, net alpha per unit turnover | net positive in base and stress cases |
| 5 Temporal robustness | stock panel | eras (1990s, 2000-2009, 2010-2017), rolling 5-year windows, crisis windows, regime conditioning | positive in >= 2 of 3 stock-level eras; no single era > 60 percent of P&L |
| 6 Ensemble | survivors only | rank-average combinations that reduce dependence | improves worst-era result without lowering median |
| 7 Validation | 2018-2021, one shot per frozen set | deflated statistics | preregistered in PHASE6_PREVALIDATION_DECISION.md |

## 4. Priority order (mandate section 54) and preregistered neighbourhoods

1. Cross-sectional momentum: 12-1 primary; 6-1 and 9-1 as neighbourhood; volatility-adjusted variant as one extra architecture.
2. Residual momentum: 12-1 on residuals from a causal 36-month market+industry regression (stock level only).
3. Low volatility: 252-day realized volatility primary; downside volatility, beta, idiosyncratic volatility as neighbourhood (French VAR/RESVAR at family level).
4. Sector/industry relative strength: 12-1 and 6-1 industry momentum (French 49 industries at family level; GICS at stock level); sector-neutral stock ranking.
5. Volatility-managed exposure: previous-month realized variance scaling with a causal expanding-median target; caps 1.0 (deployable) and 1.5 (research).
6. Momentum + low-volatility rank average (Stage 6 only).
7. Quality/value: only if Norgate fundamentals pass a point-in-time gate (they are current-vintage; expect NOT to pass; then the family is not run).
8. Short-term reversal: French 1-0 deciles at family level with a break-even cost calculation; stock level only if the break-even exceeds the stress cost.
9. ML: only after transparent alpha exists; ridge/elastic-net/LightGBM against the rank-average baseline, chronological nesting.

Trend (Family C) is tested at the market level as a regime filter (10-month SMA primary, 12-month neighbourhood) and at the stock level as an absolute filter on top-N holdings. Breadth and dispersion (sections 25-26) are computed from the point-in-time eligible universe at stock level and from French industry/decile dispersion at family level.

## 5. Multiplicity accounting

Three levels: economic family (about 9), architecture within family (2-4), parameter neighbourhood (3-5 cells). Within a neighbourhood: report the full surface, no cherry-picking, Bonferroni for the cell count. Across architectures within a family: Benjamini-Hochberg FDR 0.05. Across families for the final candidate set: Deflated Sharpe with the number of families and architectures actually tried; PBO/CSCV on the stock-level candidate grid; White Reality Check / SPA against the equal-weight eligible universe. Cumulative count continues from 388; PHASE6_EXPERIMENT_REGISTRY.csv is the ledger.

## 6. Classification vocabulary (mandate section 61)

REJECTED; WEAK_SIGNAL; FACTOR_EVIDENCE (family-level or L/S evidence that the signal ranks returns, not a portfolio); PORTFOLIO_COMPONENT_CANDIDATE (stock-level Track A portfolio survives Stages 3-5); RESEARCH_PROMISING (survives Stage 6 and red team); VALIDATION_CANDIDATE (frozen, awaiting the one-shot validation); PAPER_TRADING_ELIGIBLE (passed validation and execution feasibility). French-library results cannot exceed FACTOR_EVIDENCE.

## 7. Inference

Date-clustered (HAC) standard errors on time series of portfolio returns; Fama-MacBeth for stock-level cross-sectional slopes; stationary block bootstrap (mean block 24 months) for intervals; era replication; no random splits.

## 8. Immediate sequence

1. E050: family-level diagnostics on the French library (preregistered in EXPERIMENTS.md before running). Output: PHASE6_SIGNAL_DIAGNOSTICS.csv, PHASE6_FACTOR_ANALYSIS.md, registry rows.
2. Stop for user authorisation of the Norgate purchase (mandate section 62 A) with E050 results informing which families get stock-level compute first.
3. After purchase: Norgate exporter with hashed snapshots, integrity tests (splits, dividends, known delistings, membership counts), universe construction (PHASE6_UNIVERSE_CONSTRUCTION.md), then Stages 3-7 in priority order.
4. Execution engineering only after a PORTFOLIO_COMPONENT_CANDIDATE exists (mandate section 58).

## 9. Stop conditions

Only: A purchase authorisation needed; B genuine external blocker; C major families responsibly exhausted; D a candidate reaches the next controlled validation stage.
