# PHASE8B_DEVELOPMENT_DECISION — E062 repurchase-authorisation announcements

Decided 2026-09-20 on the corrected development run `reports/E062_20260920T214738`.
Classifier v1.8, frozen and hash-verified unchanged throughout the return stage.

## Decision: **REPURCHASE_SIGNAL_REJECTED_IN_DEVELOPMENT**

The classifier passed its gate. The **strategy** did not.

## The two things that must not be confused

1. **Classifier gate: PASS.** 15/15 on the fresh blind post-repair set (Amendment 3). The repaired classifier
   identifies new and increased issuer repurchase authorisations reliably.
2. **Economic gate: FAIL.** A reliable event detector is not an edge. The events it finds do not carry abnormal
   return after costs and factor exposure.

## Result (2013-2017, the preregistered gate window; 910 events, 2,378 total)

| | value |
| --- | --- |
| net CAGR | **14.94%** |
| equal-weight eligible universe | 8.25% |
| SPY | **15.22%** |
| excess vs EW | +6.03%/yr, t **5.18**, 5/5 years positive |
| CAPM alpha vs SPY | **-0.91%/yr, t -0.56** |
| FF5+MOM alpha | **-0.38%/yr, t -0.24** |
| max drawdown | -17.4% (SPY -8.5%) |
| turnover | 2.43x one-way |
| deflated Sharpe prob | 0.902 (10 trials) |

**Gates: G1, G2, G3, G5, G6, G7, G8, G9, G10, G12 pass. G4 (alpha) and G11 (event study) FAIL.**

- **G4 fails decisively.** The +6%/yr excess over the equal-weight universe is the entire result, and it is fully
  explained by factor exposure: alpha is *negative* against both CAPM and FF5+MOM, with t-statistics near zero. The
  strategy also simply **loses to SPY** over the gate window (14.94% vs 15.22%) while carrying twice its drawdown.
- **G11 fails.** The 252-session abnormal return is +4.21% (t 2.97 / 3.00) in 2013-2017 but **-5.64%** in 2004-2012 and
  **-1.87%** over the full 2004-2017 window, which the gate requires to be positive. An effect that is negative over
  the longer span is not a mechanism; it is a window.

This is the same failure mode as the Phase 8 insider-purchase cell: a large, highly significant excess over an
equal-weight universe that turns out to be market, size and value exposure of the kind of company that announces
buybacks, not alpha.

## Note on 2004-2012

2004-2012 shows positive CAPM alpha (+4.82%, t 2.05) and FF6 alpha (+3.48%, t 2.23), while 2013-2017 shows none. Taken
with the negative 2004-2012 *event-level* abnormal return, this is not treated as evidence for the strategy: the two
disagree in sign, the gate window is the recent one by design, and a pre-2013 alpha that vanishes afterwards is the
signature of a decayed or arbitraged effect. It is recorded, not promoted.

## Data-integrity defect found and corrected before this decision

The first run (`reports/E062_SUPERSEDED_DATA_DEFECT_20260920T213315`, retained unmodified) reported a **+737%** 2012
excess produced by one position, `SFD_old`, whose vendor series oscillates between ~$0.17 and ~$22 on adjacent
sessions. The re-equalising book harvested that oscillation. 5.83% of panel codes show the same pathology.

The screen added in Amendment 4 reuses the **existing Phase 6 I3 thresholds** and reads prices only — never an event
return. It removed **43 of 7,849 events (0.55%)** across 33 codes and several years. Its effect on the concentration
gate was decisive (best-year share 0.90 → 0.18, top-ticker share 0.37 → 0.011, G8 FAIL → PASS) and its effect on the
headline was negligible (excess 6.09% → 6.03%). **The defect was inflating the result, so its removal cannot be a
case of repairing data until the answer improves.** G4 and G11 fail in both runs.

## What would change this verdict

Nothing available. A positive FF5+MOM alpha in 2013-2017 would be needed, and the measured value is negative with
t ≈ 0. No cost case, hold length or sub-cell rescues it: the automated and stress cost cases give the same picture
(alpha -1.5% and -2.2%), and the diagnostics (A-only, B-only, 126-session, 20-slot, PIT S&P 1500) were preregistered
as diagnostics, not as alternative primaries, and are not searched for a survivor.

## Consequences

- E062 is **rejected in development**. Cumulative hypotheses/cells **490**.
- The EDGAR event family (insider purchases, quality conditioning, SUE, repurchase authorisations) is now closed on
  its own evidence.
- **Validation 2018-2021 is NOT opened. Holdout 2022-01..2026-08 is NOT read.** A rejected candidate never consumes
  locked data.
- No live, paper or shadow trading. No purchase.
- The classifier and the whole event pipeline stay frozen; nothing was changed in response to a return, and the
  frozen-hash check was re-verified after the return stage (no drift).
