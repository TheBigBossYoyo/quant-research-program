# PHASE8B_GOLD_VALIDATION - frozen pass-1 classifier against the 60-case reference set (Amendment 2)

Evaluated 2026-09-20T18:36:32.921502+00:00. Reference: **AI_ASSISTED_HUMAN_ADJUDICATED_REFERENCE_SET** (sha256 09e31be6e09550183e6a9dc6dd5e6ffb9411174b72de170e543634017330f73a): labels entered by the human owner, who consulted an independent LLM on a substantial number of difficult cases. It is NOT a fully independent unaided human gold standard; precision below is measured against a human-entered, AI-assisted adjudicated sample.

## Verdict: **FAIL**

Headline (stratum P, random sample of predicted NEW/INCREASED): 33 / 38 = 0.868; exact 95% interval [0.719, 0.956] (uncertainty information, not a criterion); human AMBIGUOUS among them: 0 (precision excluding them: 0.868).
By period: {"P_early": [17, 19], "P_recent": [16, 19]}.
Systematic-error check: {"flag": true, "routine_labelled_as_positive": 1, "repeated_rule_false_positives": {"auth_increase": 2, "auth_new": 3}, "repeated_rule_and_label": {"auth_new|COMPLETED_HISTORICAL": 2}}.
Pooled 60-case figures (descriptive only): {"n": 60, "tp": 39, "fp": 5, "fn": 4, "precision": 0.8863636363636364, "recall": 0.9069767441860465, "f1": 0.896551724137931}. pooled over all strata; the set is enriched with predicted positives and hard cases, so pooled recall and F1 are descriptive only.
Strata: {"H_low_margin": {"n": 6, "human_primary": 5, "p1_primary": 3, "p2_primary": 3}, "H_p1_only": {"n": 3, "human_primary": 3, "p1_primary": 3, "p2_primary": 0}, "H_p2_only": {"n": 3, "human_primary": 1, "p1_primary": 0, "p2_primary": 3}, "N_obvious": {"n": 10, "human_primary": 1, "p1_primary": 0, "p2_primary": 0}, "P_early": {"n": 19, "human_primary": 17, "p1_primary": 19, "p2_primary": 17}, "P_recent": {"n": 19, "human_primary": 16, "p1_primary": 19, "p2_primary": 15}}.

## False positives

- G009 (0000763563-10-000130, P_early): human RENEWAL, pass 1 A via `auth_new`: Box 1522 Elmira, New York 14902 (607) 737-3711 For Immediate Release: November 22, 2010 Chemung Financial Extends Share Repurchase Plan Chemung Financial Corporation (OTCBB:CHMG) today announced that its Board of Directors approved the exte
- G015 (0000067215-16-000056, P_recent): human RENEWAL, pass 1 B via `auth_increase`: On February 23, 2016 , the Company issued a press release announcing that its Board of Directors had authorized an additional $50 million to repurchase shares of Dycom’s outstanding common stock.
- G016 (0001000623-14-000090, P_recent): human COMPLETED_HISTORICAL, pass 1 A via `auth_new`: Forward-looking statements include, without limitation, those regarding 2014 guidance and future performance, our capital allocation strategy, mergers and acquisitions, future market trends (including in China), future reconstituted tobacco
- G049 (0000859598-13-000023, P_recent): human ROUTINE, pass 1 B via `auth_increase`: On February 26, 2013, SEACOR's Board of Directors increased the Company's authority to repurchase SEACOR common stock from $30.5 million up to $100.0 million.
- G052 (0000950134-08-000530, P_early): human COMPLETED_HISTORICAL, pass 1 A via `auth_new`: The Companys board of directors approved a share repurchase program for $750 million of the Companys common stock.

## False negatives

- G002 (0001144204-08-046405, H_low_margin): human NEW, pass 1 UNCLASSIFIED via `auth_without_size_or_newness`
- G012 (0000950134-04-016104, H_p2_only): human NEW, pass 1 D via `activity_or_past_authorisation`
- G046 (0001299933-07-006311, H_low_margin): human NEW, pass 1 UNCLASSIFIED via `auth_without_size_or_newness`
- G053 (0000950133-07-001624, N_obvious): human INCREASED, pass 1 I via `not_own_equity`

## Addendum 1 (same day, after the single frozen evaluation): validity audit of the labelling display, error analysis, proposed repairs

**Verdict recorded under the frozen rule: FAIL** (33 / 38 = 86.8% < 90%; exact 95% interval 71.9%-95.6%; systematic flag also set: 3 false positives from rule `auth_new`, 2 from `auth_increase`). No threshold was changed. No return was computed. The 'classifier gate passed' record was NOT written, so `phase8b_backtest.py` still refuses to run.

**Reference-set limitation.** AI_ASSISTED_HUMAN_ADJUDICATED_REFERENCE_SET: all 60 labels were entered by the human owner, who consulted an independent LLM on a substantial number of difficult cases. Precision here is measured against a human-entered, AI-assisted adjudicated sample, not an independent unaided human gold standard.

**Validity defect in the labelling display (engineering, caused by the agent).** The minimal-snippet extractor added to the labelling page after the gold set was frozen ranks sentences lexically and is blind to the classifier, so it could hide the sentence the classifier acted on. Mechanical audit (normalised text match, no judgement of labels): in stratum P the classifier's evidence sentence was displayed in only 25 of 38 cases (it was present in the collapsed "full extracted passage" in 37 of 38). Reference says NEW/INCREASED in 24 of 25 cases (96%) where the sentence was displayed, and in 9 of 13 (69%) where it was not. Four of the five false positives (G015, G016, G049, G052) are cases where the decisive sentence was not displayed; e.g. G049 SEACOR ("On February 26, 2013, SEACOR's Board of Directors increased the Company's authority to repurchase SEACOR common stock from $30.5 million up to $100.0 million") was shown to the labeller only as "During the fourth quarter, the Company purchased 1,047,664 shares" because the extractor did not recognise "authority" as an authorisation word; G015 Dycom ("authorized an additional $50 million to repurchase shares") was shown as the term-extension sentences. The 86.8% figure therefore mixes classifier error with a display defect and cannot be read as a clean estimate of classifier precision in either direction. The frozen labels are not altered.

**False positives (all five are in stratum P).**
| Case | Filing | Reference | Pass 1 (rule) | What happened |
| --- | --- | --- | --- | --- |
| G009 | 0000763563-10-000130 Chemung Financial, 2010-11-23 | RENEWAL | A (auth_new) | Genuine classifier error: "approved the extension of the current stock repurchase plan" is a renewal; the case-insensitive newness test matched "New York" in the glued release header. |
| G016 | 0001000623-14-000090 Schweitzer-Mauduit, 2014-08-06 | COMPLETED_HISTORICAL | A (auth_new) | Genuine classifier error: the evidence is a forward-looking-statements sentence listing "share repurchase authorization"; legal boilerplate is not an announcement. |
| G052 | 0000950134-08-000530 Pioneer Natural Resources, 2008-01-14 | COMPLETED_HISTORICAL | A (auth_new) | Probable classifier error: "The Company's board of directors approved a share repurchase program for $750 million" sits inside a recap list of past accomplishments with no date in the sentence. |
| G015 | 0000067215-16-000056 Dycom, 2016-02-24 | RENEWAL | B (auth_increase) | Decisive sentence ("authorized an additional $50 million to repurchase shares") was not displayed; the labeller saw the term-extension sentences. Disputed by the display defect, not re-labelled. |
| G049 | 0000859598-13-000023 SEACOR, 2013-02-28 | ROUTINE | B (auth_increase) | Decisive sentence ("increased the Company's authority to repurchase ... from $30.5 million up to $100.0 million") was not displayed; the labeller saw a quarterly-purchases sentence. Disputed by the display defect, not re-labelled. |

**False negatives (four, none in stratum P).** G002 CACI 2008-08-14 and G046 Evans Bancorp 2007-11-01: undated authorisation sentences inside earnings releases, demoted to UNCLASSIFIED by the quarterly-boilerplate guard although the release headline announces the programme. G012 Odyssey HealthCare 2004-11-02: headline "Announces $30 Million Stock Repurchase Program", pass 1 read only the execution-timing sentence (ROUTINE). G053 Amerigroup 2007-04-09: reference INCREASED, but the stored passage concerns an over-allotment option on notes; this reference label looks doubtful and is left as entered.

**Main confusion mode.** Renewal/extension and historical/recap text taken as a new authorisation by rule `auth_new` (3 of 5), not routine-update or ASR confusion (routine 1, ASR 0, irrelevant 0).

**Second pass.** Pass 1 vs pass 2 agree on 48 of 60 (80%; kappa 0.54); 12 disagreements, 9 of them on cases the reference calls NEW/INCREASED, so disagreement is concentrated on the tradable class. Against the reference: pass 1 agreement 85% (kappa 0.62), pass 2 72% (kappa 0.36). Both passes positive: 35 cases, 31 reference-positive (88.6%); pass-1-only positives: 9 cases, 8 reference-positive. Agreement between the two automated passes is therefore not a substitute for the reference: requiring both would not have lifted precision.

**Repairs that correspond to general semantic distinctions (proposed, NOT applied; any repair needs a refreeze and a fresh blind re-validation per A2.5):**
1. Newness must come from the lower-case word "new" attached to the programme, never from a capitalised place name in a glued header ("New York", "New Jersey").
2. A sentence that is part of a forward-looking-statements or risk-factor list is never an authorisation event.
3. An extension/renewal verb governing the programme ("approved the extension of the ... plan") decides RENEWAL even when other sentences restate the programme size.
4. In an earnings release, a release headline that announces a repurchase programme is a freshness cue for the matching authorisation sentence (recovers G002-type misses).
5. Display: authorisation vocabulary must include "authority"; the snippet must never drop the highest-ranked authorisation sentence of the stored passage. This is an instrument fix, not a classifier change.
Not proposed: any rule keyed to the individual wording of G052 (recap lists), which has no clean general form.
