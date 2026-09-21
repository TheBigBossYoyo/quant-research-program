# PHASE8B_REPURCHASE_PROMOTION_DECISION — E062

Run `E062_20260920T214738` (immutable, hash-verified). Decided 2026-09-20, documented under the 2026-09-21
artifact-recovery audit. Nothing was recomputed to produce this memo.

## Decision: **REPURCHASE_SIGNAL_REJECTED_IN_DEVELOPMENT**

Development gate: **FAIL**. No promotion. Validation 2018-2021 is not opened; holdout 2022-01..2026-08 is not read.

## The two gates that decided it

### G4 — factor alpha (FAILED)

Preregistered 2026-09-12T20:35:36Z, verbatim:

> CAPM alpha vs SPY ≥ +2 percent a year with HAC t ≥ 1.5, **AND** FF5+MOM alpha ≥ +2 percent a year with HAC t ≥ 1.0

| measure | threshold | observed (2013-2017) | margin |
| --- | --- | --- | --- |
| CAPM alpha | ≥ +2.00%/yr | **-0.91%/yr** | −2.91 pts short |
| CAPM t | ≥ 1.5 | **-0.56** | −2.06 short |
| FF5+MOM alpha | ≥ +2.00%/yr | **-0.38%/yr** | −2.38 pts short |
| FF5+MOM t | ≥ 1.0 | **-0.24** | −1.24 short |

Not a near miss in any component, and both alphas have the wrong sign. FF3 agrees: -0.43%, t -0.28.

### G11 — event study (FAILED)

Preregistered in the **same** 2026-09-12T20:35:36Z file, verbatim:

> event study: +252 abnormal return vs the EW buy-and-hold benchmark in 2013-2017 > 0 with both cluster t ≥ 2.0,
> **and > 0 over 2004-2017**

| clause | threshold | observed | result |
| --- | --- | --- | --- |
| 2013-2017 mean | > 0 | +4.21% | pass |
| 2013-2017 cluster t (month / CIK) | both ≥ 2.0 | 2.97 / 3.00 | pass |
| **2004-2017 mean** | **> 0** | **-1.87%** | **FAIL** |

The full-window clause is the one that fails, and it was frozen eight days before any return existed. 2004-2012 alone
is -5.64%.

**G11 is not redundant with G4.** G4 is a *portfolio-level* test: it asks whether a calendar-time book of overlapping
252-session positions produces alpha after factor exposure. G11 is an *event-level* test: it asks whether the average
individual announcement is followed by abnormal return, with observations clustered by month and by issuer so that
overlapping holdings cannot manufacture significance. They can disagree in both directions — a portfolio can show
alpha from weighting and rebalancing while the average event does nothing, and an event effect can be real while a
portfolio implementation of it is swamped by costs or exposure. Here they agree on the verdict but through different
evidence: G4 says the portfolio's excess is exposure, G11 says the underlying event effect does not hold up outside
the gate window. G11 also supplies the one thing G4 cannot — a direct check on whether the effect is stable across
time, which is exactly where this candidate breaks.

## Gates that passed

G1 (excess ≥ 3%: 6.03%), G2 (NW t ≥ 2: 5.18), G3 (4/5 years: 5/5), G5 (drawdown), G6 (turnover 2.43 ≤ 3.0),
G7 (automated excess 5.37% > 0), G8 (concentration, all four sub-limits), G9 (early excess ≥ 0: 6.20%),
G10 (910 and 2,378 events), G12 (deflated Sharpe 0.902 ≥ 0.90). G14 (classifier) passed at 15/15.

Ten of twelve gates pass. The strategy is well-sampled, cheap to trade, diversified and consistent — and has no alpha.

## Why the headline number is not a result

| | 2013-2017 |
| --- | --- |
| strategy net CAGR | 14.94% |
| equal-weight eligible universe | 8.25% |
| **SPY** | **15.22%** |
| max drawdown | -17.4% (SPY -8.5%) |

+6.03%/yr over the equal-weight universe with t 5.18 is a large, highly significant number that means the strategy
holds bigger, better companies than the average of a 1000-name liquid universe. Against the index a retail account
could actually buy, it loses, with twice the drawdown. This is the second time this program has produced that exact
object — the Phase 8 insider-purchase cell failed the same way — and G4 exists because of the first time.

## Consequences

- E062 rejected in development; cumulative hypotheses/cells **490**.
- The SEC EDGAR event family (insider purchases, quality conditioning, SUE drift, repurchase authorisations) is closed
  on its own evidence.
- The classifier gate **passed** (15/15) and that result stands separately: the detector works; the events are not
  tradable. A reliable event detector is not an edge.
- No live, paper or shadow trading. No purchase. No locked data accessed.
- The classifier and the whole event pipeline remain permanently frozen; the frozen-hash check was re-verified after
  the return stage with zero drift, so no rule was changed in response to a return.
