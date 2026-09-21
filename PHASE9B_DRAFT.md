# PHASE 9B — DRAFT ONLY, NOT EXECUTED, NOT PREREGISTERED

Status: **draft**. Nothing here is frozen, hashed or registered. No experiment ID is assigned. No cell
is added to `EXPERIMENTS.md`. Running any stage below requires a separate preregistration with a
frozen hash *before* any return is computed, as every prior phase in this programme has done.

This draft exists because the Phase 9A brief asked for it if a provider qualified. One did, structurally
(`ZACKS/EEH`) — but it is licence-blocked for individuals, so **Stage 1 onwards is conditional on a data
route that does not currently exist**. Stage 0 is free and is the only part that could run today.

---

## The mechanism

Sell-side analysts update earnings forecasts gradually rather than all at once, and institutional
portfolios rebalance with delay. Stocks whose consensus is being revised persistently upward may
therefore continue to outperform for weeks to months after the revisions begin.

This is the post-forecast-revision drift literature. It is one of the better-surviving anomalies in
post-publication replication work, which is why it was worth an audit — but "better-surviving" is a
relative statement and the family has decayed like the rest. Stage 0 exists to measure that decay before
anything is spent.

**What would make this different from what this programme has already rejected.** Phases 6–8 rejected
price/volume families, factor families, and SEC-event families. Every one of those used information
that is either free or mechanical. Analyst revisions are the first candidate family in this programme
whose information source is *expensive because it is genuinely proprietary* — the consensus is a
survey, not a computation. That is a real reason to expect it to be less arbitraged than a momentum
lookback, and also the reason it cannot be bought.

## Stage 0 — free prior-evidence gate (the only executable stage)

**Purpose.** Decide, without spending money and without opening locked data, whether the mechanism was
still alive in the development era.

**Data.** Open Source Asset Pricing (Chen & Zimmermann, October 2025 release), monthly long-short
portfolio returns. Free, academic citation licence. No identifier mapping required.

**Signals (fixed list, 5 — no sweep):** `AnalystRevision`, `REV6`, `ChNAnalyst`, `ForecastDispersion`,
`EarningsForecastDisparity`. These are the pre-existing academic definitions; we do not tune them,
because tuning someone else's published signal on their published returns is a multiplicity trap with
no corresponding data.

**Window.** **1990-01 to 2017-12 only.** The series extend to 2024-12; everything from **2018-01
onward must be discarded at load time** by a hard filter in code, not by discipline. Validation
2018–2021 and holdout 2022-01..2026-08 stay closed.

**What is measured.** Mean monthly long-short return and NW t-statistic in 1990–2004 versus 2005–2017;
the ratio of the two; whether the long leg alone (published separately for several of these signals)
carries the result or whether it is all in the short leg.

**Why the long leg matters more than the headline.** This programme can only trade long-only,
unlevered, on Trading 212. A long-short decile spread that is entirely short-side is worthless here.
Phase 8 and Phase 8B both produced candidates that looked significant against an equal-weight universe
and lost to SPY — the same failure would appear here as "long leg does not beat the market".

**Gate.**

| outcome | decision |
| --- | --- |
| 2005–2017 long-short mean ≤ 0, or long leg shows no excess over the market | **REJECT the family on evidence.** Record it as a mechanism result, not a budget result. No purchase discussion. |
| 2005–2017 clearly positive **and** carried by the long leg | Family is **alive but data-blocked**. Report to the user; do not proceed without a data route. |
| ambiguous | Report as ambiguous. Do not resolve it by looking at 2018+. |

**Explicit limitations to state in the output.** These are decile long-short, CRSP-universe, costless,
monthly-rebalanced portfolios built from licensed IBES data by other researchers. They are an **upper
bound**, not a backtest of anything we could trade. A positive Stage 0 is permission to keep talking,
never a candidate.

**Cells added to the ledger: 0.** Stage 0 evaluates published third-party portfolio returns to assess a
data purchase; it forms no strategy, selects no parameters and trades nothing. If any parameter choice
or signal selection were made on these series, that would change, and it would be counted.

## Stage 1 onwards — BLOCKED, specified for completeness

None of this can run without a class-A source. Written down so that if the licence position ever
changes, the design is already on record and cannot be retrofitted to a result.

**Data requirement.** `ZACKS/EEH` (`obs_date`, `per_end_date`, `per_type`, `eps_mean_est`, `eps_cnt_est`,
`eps_std_dev_est`, `eps_cnt_est_rev_up`, `eps_cnt_est_rev_down`) + `ZACKS/MT` (`comp_cik`,
`active_ticker_flag`) for the survivorship-aware CIK join to the local EODHD active+delisted panel.
`ZACKS/SEH` optional for revenue revisions.

**Precondition before any purchase — the T5 immutability test.** Pull the free `ZACKS/EEH` sample,
hash it, wait ≥ 14 days, pull again, diff. Any change to a row whose `obs_date` is in the past demotes
the product from class A and cancels the purchase. Documented `obs_date` semantics are not evidence of
immutability.

**Architecture (deliberately small and low-turnover).**

- Universe: liquid US stocks, PIT membership, delisted issuers retained, the same universe rules and
  delisting handling already fixed in Phase 6.
- Frequency: **monthly** ranking. Not event-driven on each analyst update — that would be a turnover
  and cost disaster at EUR 500–1,000 and is not what the mechanism needs.
- Signal: 30-day change in FY1 consensus EPS, scaled by price or by estimate dispersion. One primary
  definition, preregistered, plus at most two named robustness variants (60-day; revision breadth
  = (up − down)/count).
- Portfolio: **long-only**, top 20/30/50, equal weight, no leverage.
- Costs: Trading 212 base case and the 20 bps automated stress case, exactly as in Phase 6/8.
- Benchmarks: **SPY first**, equal-weight universe second. The Phase 8 and 8B failures both came from
  a candidate that beat the equal-weight universe and lost to SPY; SPY is the primary benchmark and a
  CAPM/FF5+MOM alpha gate applies, with the sign and t-threshold fixed before any return exists.
- Split: development ≤ 2017-12, validation 2018–2021 opened **only** on a development pass, holdout
  2022-01..2026-08 opened **only** after architecture freeze.
- Capital: must be feasible at EUR 500–1,000 or be explicitly classified capital-limited.

**Trial budget.** Primary definition + 2 variants × 3 portfolio sizes = **9 cells maximum**, declared
in advance, with the multiplicity burden added to the cumulative 490 and carried into the deflated
Sharpe calculation. No grid.

**If the source starts later than 2010.** Do not stretch the existing split. A new chronological split
must be preregistered from scratch, with the reduced sample size and its consequences for power stated
before any result is seen.

## What would make this draft void

- Stage 0 rejects the family → Phase 9B is abandoned and the family is closed on evidence.
- The T5 immutability test fails → the data is not point-in-time and no purchase is justified.
- The licence position does not change → Stages 1+ never run, and the family stays recorded as
  data-blocked rather than tested.
