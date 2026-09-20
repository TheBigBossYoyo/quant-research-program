# PHASE8B_DECISION - status at the end of the 2026-09-12 session

## Research status: **STOPPED AT THE HUMAN-LABEL GATE (E062 undecided; no return computed)**

This is not one of the five terminal labels of the preregistration (section 15); none can be assigned yet because the classifier-validation gate has not been reached. The branch stops here deliberately: the frozen rule requires genuine human labels, and none exist.

## What exists (all frozen and hashed in PHASE8B_FREEZE_HASHES.jsonl)
| Item | State |
| --- | --- |
| Repository audit | PHASE8B_REPOSITORY_AUDIT.md: Phase 8 engine, universe, costs, delisting rule and lock reused; companyfacts files hold post-2017 facts (read-time filter added); no lock defect found |
| Preregistration | PHASE8B_PREREGISTRATION.md + phase8b_config.json, hashed before any candidate text was read |
| Stage 1 retrieval | 24 target + 6 audit expressions, 8-K, 2004-01..2017-12, per expression per month: 110,355 candidate accessions (107,134 8-K, 3,221 8-K/A), 129,569 complement accessions; PHASE8B_RETRIEVAL_REPORT.md |
| Full-submission text | fetched for the 300 sampled filings; the fetch of the remaining pool runs detached and resumes from cache |
| Labelling package | phase8b_labeling_candidates.csv (240 filings: 160 stratum S1 authorisation-language, 80 S2; 15-19 per year 2004-2017; one per issuer-year; passages + full text under labeling_texts/), phase8b_labeling_guide.md, phase8b_label_split.csv (DEV 168 / HOLDOUT 72, drawn before any label), phase8b_labeling_meta.json (stratum weights S1 311.8, S2 715.6) |
| Retrieval-recall audit | (a) XBRL cross-check (PHASE8B_RETRIEVAL_RECALL_AUDIT.md): 658 authorised-amount/share increases in 10-Q/10-K filings 2011-2017 across 4,473 issuers; 77.2% have a candidate 8-K of the same CIK in the prior 120 days (85.3% for dollar amounts, 66.4% for share counts; 69-81% by year) - a lower bound on 8-K retrieval recall since many issuers disclose only in the 10-Q; (b) phase8b_retrieval_audit_candidates.csv, 60 complement filings for human labels |
| Causal timing | phase8b_timing.py (08:30 ET cutoff, next session otherwise, XNYS-verified sessions, DST, 252/126 holds) with 23 tests |
| Event integrity | phase8b_events.py (amendments excluded, 60-day repeated-reference merge, PIT CIK->symbol mapping, price check before entry) with 11 tests |
| Portfolio accounting | phase8b_portfolio.py (hold-all, re-equalise on membership change, costs per side, delisting haircut, cash floor, turnover) with 10 tests |
| Classifier harness | phase8b_classifier_eval.py: HOLDOUT labels blanked for development reads; HOLDOUT scored once, only when the classifier files match their frozen hashes |
| Return stage | phase8b_backtest.py: event study, hold-all portfolio, EW/SPY/CAPM/FF3/FF5+MOM, G1-G12 gates, DSR; refuses to run without a "classifier gate passed" record |
| Ledger | EXPERIMENTS.md (E062 preregistered), PHASE6_EXPERIMENT_REGISTRY.csv row 489, RESEARCH_JOURNAL.md, PLAN.md, STATUS.md |

## Package v2 (2026-09-12, after the user's independent audit; Amendment 1 of the preregistration; still no label)
Label J (self-tender / Dutch-auction offer) added outside A/B; current ticker hint removed from the human view; classifier split re-drawn with the CIK rule (DEVELOPMENT 167 / HOLDOUT 73; PHASE8B_CLASSIFIER_SPLIT.md); retrieval-audit sample redesigned as B1/B2 item strata (60 + 30 rows; PHASE8B_RETRIEVAL_AUDIT_DESIGN.md states the estimator and that 90 rows bound the miss rate rather than measure recall precisely); every full_text_path verified and zipped (phase8b_labeling_package.zip, phase8b_package_verification.json).

## What the user must do for the branch to continue (no money involved)
1. Open `research/phase8b/phase8b_labeling_candidates.csv` and type one letter A-J into `human_label` for all 240 rows, following `phase8b_labeling_guide.md` (full texts in `research/phase8b/labeling_texts/` or in `phase8b_labeling_package.zip`). Do not look up prices or later filings.
2. Do the same for `research/phase8b/phase8b_retrieval_audit_candidates.csv` (90 rows).
3. Say so in a new session. The next session develops the classifier on DEV rows only, freezes and hashes it, evaluates HOLDOUT once, and only then runs the preregistered return stage.

## What must not happen
- No Claude-generated labels as ground truth. No rule chosen after seeing returns. No holding period other than 252 (126 as a sensitivity). No opening of 2018-2021 or 2022-2026 under any outcome of this branch.

## Distinctions kept for the final label
Economic rejection (gates fail on true events), classifier failure (precision < 0.90 on HOLDOUT), data insufficiency (too few A/B events after mapping and eligibility: G10), engineering failure (a defect found in the pipeline, repaired and rerun with the first run retained), or a surviving candidate (all gates and the red team pass -> validation request, not access).
