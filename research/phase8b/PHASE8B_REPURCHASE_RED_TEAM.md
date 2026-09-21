# PHASE8B_REPURCHASE_RED_TEAM — E062

Run `E062_20260920T214738`, recovered from immutable persisted outputs. Nothing recomputed. Development data only.

G13 asks whether any listed test turns the 2013-2017 net excess or the CAPM alpha negative. The honest answer is that
**the CAPM alpha is already negative before the red team starts**, so the red team's job here is the opposite one: to
ask whether the failure is real, or an artefact that is unfairly condemning a live strategy.

## 1. Is the rejection driven by the data defect that was found?

No. The defect (an oscillating vendor series harvested by the re-equalising book, Amendment 4) **inflated** the result.
Both runs fail G4 and G11:

| | superseded run | corrected run |
| --- | --- | --- |
| 2013-2017 excess vs EW | 6.09% | 6.03% |
| 2013-2017 CAPM alpha | -0.87% (t -0.53) | -0.91% (t -0.56) |
| G4 | FAIL | FAIL |
| G8 concentration | FAIL (best-year share 0.90) | PASS (0.18) |
| G11 | FAIL | FAIL |

Cleaning the data fixed a gate the strategy was *failing* and barely moved the headline. A repair that helps the
hypothesis on one gate and leaves the two decisive ones failing is not a repair that manufactured the rejection.

## 2. Is the rejection a cost artefact?

No. Costs move the result in the wrong direction for the hypothesis but do not create the failure. The **primary**
cost case is already the most optimistic one (MANUAL_USD, 5 bps). Its 2013-2017 CAPM alpha is -0.91%. There is no
cheaper case to appeal to.

## 3. Is it an entry-timing artefact?

No. Delaying entry by a full session changes the excess from 6.03% to 5.83% and the alpha from -0.91% to -1.13%. The
result is not balanced on a one-open micro-timing assumption.

## 4. Is the benchmark unfair?

This is the objection with real force, and it cuts against the strategy rather than for it. Measured against the
equal-weight eligible universe the strategy looks strong (+6.03%/yr, t 5.18, 5/5 years). Measured against **SPY**,
which is what a retail account could actually hold instead, it **loses**: 14.94% vs 15.22%, with a drawdown of -17.4%
against SPY's -8.5%. The equal-weight benchmark flatters it because buyback announcers are larger and more profitable
than the average member of a 1000-name liquid universe. G4 exists precisely to stop an equal-weight excess from being
read as skill, and it caught this.

## 5. Could the alpha be hiding in a sub-cell?

Every preregistered sub-cell was examined and none rescues it:

| cell / variant | 2013-2017 CAPM alpha | t | verdict |
| --- | --- | --- | --- |
| NEW only | -3.80% | -1.61 | worse |
| INCREASED only | +0.89% | 0.75 | best half, still far below G4 (+2%, t 1.5) |
| PIT S&P 1500 subset | +0.47% | 0.33 | no |
| 126-session hold | +0.08% | 0.05 | no |
| 20 slots | +2.56% | 1.06 | clears the alpha level, fails the t-threshold |
| +1 session delay | -1.13% | -0.67 | no |

The 20-slot variant is the only one that reaches +2%. It fails G4's t ≥ 1.5, it concentrates 910 events into 20
positions (a different risk profile entirely), and it was preregistered as a diagnostic, not a primary. Promoting it
after seeing the primary fail would be exactly the search-until-significant behaviour the gates exist to prevent.

## 6. Is the 2004-2012 alpha evidence the effect is real?

The early window does show positive alpha: CAPM +4.82% (t 2.05), FF3 +3.77% (t 2.13), FF5+MOM +3.48% (t 2.23). Two
things stop this being support:

1. the **event-level** abnormal return over the same 2004-2012 window is **-5.64%** — the portfolio measure and the
   event measure disagree in sign, which is what one expects when a portfolio result is driven by exposure rather
   than by the events themselves;
2. an alpha that is present before 2013 and absent after it is the signature of a decayed or arbitraged effect, and
   2013-2017 is the gate window by design because it is the era a deployment would actually face.

The repurchase-announcement drift is one of the most published anomalies in the literature. Its disappearance in the
modern sub-period is the expected outcome, not a surprise.

## 7. Multiplicity

Deflated Sharpe probability 0.902 against N = 10 trials, which passes G12 — but G12 was calibrated for a *surviving*
candidate. The relevant multiplicity fact here is that E062 is the fourth EDGAR event family tested (insider
purchases, quality conditioning, SUE drift, repurchases) and the second to produce a large equal-weight excess with no
alpha. Finding the same artefact twice is evidence about the benchmark, not about buybacks.

## 8. What would overturn this rejection

A positive FF5+MOM alpha in the 2013-2017 window, at +2%/yr with t ≥ 1.0. The measured value is -0.38% with t -0.24.
Nothing in the available data, cost assumptions, holding periods or preregistered sub-cells produces it.

## Red-team verdict

The rejection **survives**. No listed test turns it into a pass, and the two objections with genuine force — the data
defect and the benchmark choice — both argue for rejection rather than against it.
