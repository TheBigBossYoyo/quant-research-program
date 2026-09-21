# PHASE8B_REPURCHASE_EVENT_STUDY — E062

Run `E062_20260920T214738` — **recovered from immutable persisted outputs; nothing was recomputed**. `results.json` sha256 `5812e0b5ba782b42c4dfbdcc27051f9444bfdc9fc789a6c016512a20356f7d84`, hashed 2026-09-20T21:49:41.977193+00:00. Classifier v1.8 `4a0c6b54a9a7b49cc8df04e8…`; event list `dd0dc6c85765a6326ad9321a…`.

Development data only. Validation 2018-2021 and holdout 2022-01..2026-08 were not accessed.

Abnormal return against the equal-weight buy-and-hold benchmark, entry at the first open at least 60 minutes
after EDGAR acceptance. t-statistics are two-way clustered, by calendar month and by issuer CIK.

## Primary cell (NEW+INCREASED)

| horizon | window | mean abnormal return | t (month) | t (CIK) |
| --- | --- | --- | --- | --- |
| +5 | w2013_2017 | -0.55% | -0.64 | -0.63 |
| +5 | w2004_2012 | -5.46% | -1.62 | -2.70 |
| +5 | w2004_2017 | -3.58% | -1.75 | -2.74 |
| +21 | w2013_2017 | -0.36% | -0.38 | -0.37 |
| +21 | w2004_2012 | -5.78% | -1.57 | -2.82 |
| +21 | w2004_2017 | -3.71% | -1.65 | -2.82 |
| +63 | w2013_2017 | 0.72% | 0.65 | 0.68 |
| +63 | w2004_2012 | -5.59% | -1.51 | -2.75 |
| +63 | w2004_2017 | -3.17% | -1.37 | -2.41 |
| +126 | w2013_2017 | 2.21% | 1.87 | 1.90 |
| +126 | w2004_2012 | -6.28% | -1.44 | -2.85 |
| +126 | w2004_2017 | -3.03% | -1.11 | -2.10 |
| +252 | w2013_2017 | 4.21% | 2.97 | 3.00 |
| +252 | w2004_2012 | -5.64% | -1.19 | -2.26 |
| +252 | w2004_2017 | -1.87% | -0.63 | -1.13 |

## G11 reading

G11 requires the +252 abnormal return to be > 0 in 2013-2017 with **both** cluster t >= 2.0, **and** > 0 over 2004-2017.

- 2013-2017: 4.21%, t 2.97 / 3.00 → this clause **passes**.
- 2004-2012: -5.64% → negative.
- 2004-2017 full window: -1.87% → **negative, so G11 FAILS**.

The short horizons carry the same message: +5 and +21 sessions are negative or near zero over the full window.
An effect that is positive only inside the gate window and negative over the longer span is a window, not a
mechanism.

Machine-readable: `phase8b_repurchase_event_study.csv`.

