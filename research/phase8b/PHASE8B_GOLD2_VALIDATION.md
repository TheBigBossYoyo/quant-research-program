# PHASE8B_GOLD2_VALIDATION - repaired classifier v1.8 against the fresh 15-case blind set (Amendment 3)

Evaluated 2026-09-20T21:20:22.048726+00:00. Reference: **FRESH_BLIND_TO_CLASSIFIER_AI_ASSISTED_HUMAN_ADJUDICATION** (sha256 780eaa025d2db6d13173e750a053d4a2ba0a73ee53265bf754fd293d3de0be8a).
Every case is a predicted positive drawn blind from the never-shown pool; the labeller saw the classifier's own
evidence sentence with one sentence each side (A3.4), so this measurement is not affected by the display defect
that invalidated the first run as an estimate of the repaired classifier.

## Verdict: **PASS**

Headline (NEW+INCREASED superclass precision): 15 / 15 = 1.000; exact 95% interval [0.782, 1.000] (uncertainty information, not a criterion).
By period: {"P_early": [7, 7], "P_recent": [8, 8]}.
Human labels: {"NEW": 11, "INCREASED": 4}.
Systematic-error check: {"flag": false, "n_false_positives": 0, "routine_labelled_as_positive": 0, "false_positive_labels": {}, "false_positives_by_rule": {}, "repeated_rule_false_positives": {}, "note": "a single non-systematic error is BORDERLINE under A3.8 and stops for a user decision"}.

## Errors

- none

## Prior run (seen; reported separately, never pooled)

- {"status": "SEEN - reported separately, never pooled (A3.8)", "frozen_v17_verdict": "CLASSIFIER_VALIDATION_FAILED_AS_MEASURED", "frozen_v17_stratum_P": "33/38", "frozen_v17_precision": 0.868421052631579}

Returns: LOCKED unless the verdict is PASS; validation 2018-2021 and holdout 2022-2026 untouched.

