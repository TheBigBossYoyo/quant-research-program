# PHASE 9B STAGE 0 — AMENDMENT 1: two unit/alignment defects in run 1

Written 2026-09-21, **after** run 1 produced output and **before** any corrected run.
Run 1 is retained unchanged at `reports/phase9b/superseded_run1/`. None of its numbers is treated as
a result.

No frozen rule, window, signal, threshold, benchmark definition or HAC lag is changed by this
amendment. Only two implementation defects are repaired.

---

## D1 — unit mismatch between the two sources

**Defect.** The OSAP `ret` column is denominated in **percent per month**. The Kenneth French factors
are converted to **decimal** by `research/phase6_french.load(..., returns=True)`, which divides by 100.
Run 1 combined them without conversion.

**Evidence that OSAP is in percent** — three independent checks, none of which required looking at a
Stage 0 gate:

1. `SignalDoc.csv` records the original paper's monthly return for `AnalystRevision` as `0.4606`.
   Run 1's EARLY mean monthly was `0.826`. Both are percent-scale; as decimals they would be 46% and
   83% per month.
2. Run 1's `EWCOV` (the EW average covered stock, from OSAP) gave a 2005-2017 mean monthly of `0.799`
   and the French value-weighted market gave `0.008168`. Read as percent and decimal respectively,
   those are **9.59%/yr and 9.80%/yr** — two independent estimates of the average US stock over the
   same period, agreeing closely. Read on a common scale they differ by a factor of 100.
3. Run 1's `cumulative_return`, computed as `prod(1+r)−1` on percent-scale inputs, returned values
   such as `3.5e+31`, which is arithmetically impossible for a monthly equity series.

**What it corrupted in run 1:**

- every `cumulative_return` value (descriptive output, used in no gate);
- the **B2** secondary diagnostic, which subtracted a decimal market return from a percent long-leg
  return. Run 1's "AnalystRevision long-leg excess over the market, +10.29%/yr" is **not a result** and
  must not be quoted.

**What it could not corrupt:** `ann_mean`, `ann_vol`, `sharpe` and `nw_t` computed *within* the OSAP
series, because those are either consistently percent-scaled or scale-invariant.

**Repair.** Convert OSAP returns to decimal at load time, immediately after the date lock and before
any series is built: `ret = ret / 100.0`. The French series stays decimal. One scale throughout.

## D2 — benchmark date alignment

**Defect.** OSAP stamps each month with the **last trading day** (2005-04-29, 2005-07-29, 2005-12-30);
the French library stamps the **calendar month end** (2005-04-30, 2005-07-31, 2005-12-31). Run 1 joined
them on the exact timestamp, so months whose last trading day was not the calendar month end were
silently dropped: **111 of 156** months matched in 2005-2017 and **67 of 96** in 2010-2017.

**What it corrupted:** the B2 diagnostic only — it was computed on a ~70% subsample chosen by a
calendar artefact.

**What it could not corrupt:** the B1 gate benchmark, which is built from the same file with the same
timestamps, so it matched 156/156 and 96/96 in run 1.

**Repair.** Join the long leg to each benchmark on the **year-month period** rather than the exact
timestamp, and report `months_matched` in the output so any future shortfall is visible rather than
silent.

## Stated before the corrected run: the frozen decision cannot change

This is the claim that makes the repair legitimate rather than a second look at the data. It is
recorded here, in a committed document, before the corrected run is executed.

| gate | input | affected by D1? | affected by D2? |
| --- | --- | --- | --- |
| C1 `AnalystRevision` LS 2005-2017 mean > 0 | OSAP only | no — dividing by 100 preserves sign | no |
| C2 `AnalystRevision` LS 2005-2017 NW t ≥ 2.0 | OSAP only | no — the t-statistic is **scale-invariant** | no |
| C3 `AnalystRevision` LS 2010-2017 mean > 0 | OSAP only | no — sign preserved | no |
| C4 `REV6` LS 2005-2017 mean > 0 | OSAP only | no — sign preserved | no |
| C5 `AnalystRevision` long-leg excess over **B1** > 0 in both windows | OSAP only, both legs same scale and same timestamps | no — both sides divided by 100 | no — B1 matched 156/156 and 96/96 |

Every gate therefore returns exactly what run 1 returned, and the Stage 0 classification stays
`AMBIGUOUS_ANALYST_REVISION_EVIDENCE`. The corrected run is expected to reproduce all five condition
flags identically; the execution script asserts this against run 1's stored flags and **fails loudly if
any gate flips**, which would mean this amendment's reasoning was wrong and the result would have to be
reported as changed rather than confirmed.

What the corrected run *does* change is the honesty of the reported numbers: correct cumulative
returns, and a B2 diagnostic that compares like with like on the full sample. On the corrected scale
the B2 comparison is expected to be far less flattering than run 1's corrupted `+10.29%/yr`, because
the long leg's annualized mean (`10.41%/yr` on the percent scale of run 1) sits only slightly above the
value-weighted market's `9.80%/yr`. That expectation is written down here before it is computed.

## Ledger

Still **0 cells**, cumulative **490**. A defect repair is not a hypothesis. Run 1 is retained on disk
as superseded, as Phase 8B Amendment 4 retained its defective run.
