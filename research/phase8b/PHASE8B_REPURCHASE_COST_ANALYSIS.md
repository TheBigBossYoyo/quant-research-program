# PHASE8B_REPURCHASE_COST_ANALYSIS — E062

Run `E062_20260920T214738` — **recovered from immutable persisted outputs; nothing was recomputed**. `results.json` sha256 `5812e0b5ba782b42c4dfbdcc27051f9444bfdc9fc789a6c016512a20356f7d84`, hashed 2026-09-20T21:49:41.977193+00:00. Classifier v1.8 `4a0c6b54a9a7b49cc8df04e8…`; event list `dd0dc6c85765a6326ad9321a…`.

Development data only. Validation 2018-2021 and holdout 2022-01..2026-08 were not accessed.

All three preregistered cost cases, primary cell (NEW+INCREASED).

| cost case | rates (bps per side) | window | net CAGR | excess vs EW | NW t | CAPM a | t | FF5+MOM a | t |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| primary | MANUAL_USD 5/5.3 bps (10/10.3 far) | w2013_2017 | 14.94% | 6.03% | 5.18 | -0.91% | -0.56 | -0.38% | -0.24 |
| primary | MANUAL_USD 5/5.3 bps (10/10.3 far) | w2004_2017 | 11.92% | 6.14% | 5.47 | 2.35% | 1.35 | 1.51% | 1.36 |
| automated | AUTOMATED 20/20.3 bps (25/25.3 far) | w2013_2017 | 14.19% | 5.37% | 4.58 | -1.54% | -0.94 | -1.02% | -0.63 |
| automated | AUTOMATED 20/20.3 bps (25/25.3 far) | w2004_2017 | 11.08% | 5.38% | 4.87 | 1.59% | 0.92 | 0.75% | 0.67 |
| stress | STRESS 30/31 bps (45/46 far) | w2013_2017 | 13.41% | 4.67% | 3.96 | -2.21% | -1.34 | -1.69% | -1.04 |
| stress | STRESS 30/31 bps (45/46 far) | w2004_2017 | 10.23% | 4.61% | 4.23 | 0.82% | 0.48 | -0.03% | -0.03 |

## Reading

The excess over the equal-weight universe survives every cost case, so G7 passes. **The alpha does not exist
in any of them.** The 2013-2017 CAPM alpha is negative under all three cost cases and becomes more negative as
costs rise. Costs are not what rejects this strategy; the absence of alpha is. Raising costs cannot create
alpha, and lowering them below the MANUAL_USD case would not either — the optimistic case is already the
primary one.

## Preregistered diagnostics (2013-2017)

| variant | excess vs EW | NW t | CAPM a | t |
| --- | --- | --- | --- | --- |
| delay1 | 5.83% | 5.04 | -1.13% | -0.67 |
| all100 | 6.03% | 5.18 | -0.91% | -0.56 |
| all30 | 5.33% | 4.58 | -1.71% | -1.05 |
| h126 | 6.72% | 5.21 | 0.08% | 0.05 |
| slots20 | 9.18% | 3.47 | 2.56% | 1.06 |

These were preregistered as diagnostics, not as alternative primaries, and none is promoted. The 20-slot
variant shows the largest CAPM alpha (+2.56%, t 1.06); it still fails the G4 t-threshold of 1.5, and
concentrating 910 events into 20 slots is a different strategy that was never registered as the primary.
A one-session entry delay changes almost nothing (excess 5.83%, alpha -1.13%), so the result is not a
micro-timing artefact.

