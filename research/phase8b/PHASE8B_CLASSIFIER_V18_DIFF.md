# PHASE8B_CLASSIFIER_V18_DIFF — every change from the frozen v1.7, and why

Required by Amendment 3 A3.6. Written before the fresh 15-case set was drawn.

v1.7 is preserved byte-identical in `frozen_v1.7/` (hashes match the `classifier frozen (Amendment 2; version 1.7 ...)`
records in `PHASE8B_FREEZE_HASHES.jsonl`). The v1.7 verdict **CLASSIFIER_VALIDATION_FAILED_AS_MEASURED (33/38 = 86.8%)**
is unchanged and is not restated anywhere by this repair.

All repairs were developed and inspected **on the development pool only**
(`int(sha256(accession),16) % 5 == 0`, 15,608 8-K rows). The 60 frozen reference labels were not consulted while
choosing or tuning any rule, and no rule is keyed to a filing, an accession or a gold id — `tests/test_phase8b_repair_v18.py`
asserts this mechanically against the source.

---

## 1. Changes that implement the five approved repairs

| # | Repair | Change in `phase8b_classifier.py` |
| --- | --- | --- |
| A | `new` read semantically | New `PLACE_NEW` + `NEW_PROGRAMME` and the helper `has_newness()`. Newness now requires the word "new" to govern programme vocabulary within 60 characters, after capitalised place names ("New York", "New Jersey", "Newark") have been stripped. Place words are excluded from `PLACE_NEW` so a title-case headline ("Announces **New** Share Repurchase Program") still counts. Both `\bnew\b` tests in `sentence_role` and the newness cues in `pass2` now go through it. |
| B | forward-looking language is never an event | New `FLS` + `fls_boilerplate()`, applied at the top of `sentence_role`. It fires **only when the boilerplate marker precedes the repurchase words**, i.e. the repurchase words are items inside the legal list. A safe-harbour paragraph glued *after* a genuine announcement does not demote it. |
| C | extension/renewal without added capacity → RENEWAL | Follows from repair A: the renewal branch is no longer skipped because a place name matched `\bnew\b`. `RENEW_CUE` additionally recognises `reaffirm*`, `reactivat*` and "second/third/… year of" as continuation language. An extension that *also* adds capacity still reaches `AUTH_INCREASE`, which is tested. |
| D | a release headline announcing a programme is evidence of a new authorisation | New `HEADLINE_ANNOUNCE`; in `pass1`, an `AUTH_WEAK` sentence demoted by the earnings-release guard is restored to `AUTH_NEW` when the release headline itself announces the programme and the sentence is not flagged as finished, renewed, or old news. |
| E | "authority" / "authorized amount" are authorisation terminology | `AUTH_VERB` gains the increase-of-authority forms; `AUTH_CAPACITY_INCREASE` lets "approved an increase in the Company's authority to repurchase" reach `AUTH_INCREASE` **even with no dollar figure in the sentence**. The display instrument's blindness to "authority" is fixed structurally — see section 4. |

## 2. Preserved distinctions that v1.7 did not actually honour, now implemented

Amendment 3 lists these as distinctions that must survive the repair. Two of them were not in fact honoured by v1.7,
so they are implemented here as general rules:

- **replacement of a prior/completed programme by a newly approved one = NEW.** `REPLACEMENT` + `replaces_prior`
  suspends the `HARD_PAST` / `PAST_CUE` demotion when the sentence both approves something with explicit newness and
  replaces/supersedes a prior programme. It requires *both* cues, so "as previously announced" alone still demotes.
- **increase of the authorisation itself = INCREASED** even without a quoted size (repair E above).
- **"in addition to the existing/remaining authorization" = INCREASED.** `ADDED_CAPACITY` (the phrase "in addition to"
  only) may override a past cue, but only when it sits within 120 characters of the authorisation verb
  (`added_capacity_near`). The proximity requirement exists because a glued slide deck paired an unrelated
  "additional $200 million" with a distant "authorized" in dev-pool inspection.

## 3. Guards added after reading dev-pool cases the repairs newly turned positive

Each removes a false-positive category, not a filing:

- **Rule 10b5-1 trading plans** (`TRADING_PLAN`): adopting a pre-arranged trading plan is an *execution* mechanism and
  authorises nothing. The guard does **not** fire when the same sentence is itself a board authorisation of an amount.
- **restricted-stock buybacks from insiders** (`RESTRICTED_BUYBACK`): repurchasing restricted stock from an officer is
  not an issuer programme.
- **debt repurchase programmes** added to `NOT_OWN_EQUITY`.
- **"at that time"** added to `HARD_PAST` as a past marker.

## 4. Instrument change (new file `research/phase8b_display.py`)

The v1.7 lexical ranker `gold_snippet.minimal_snippet` — which caused the validity defect — is **not used** for any
future validation set. It is archived as `frozen_v1.7/gold_snippet_v1.7_DEFECTIVE.py`.

The replacement does not rank anything. It locates the classifier's own evidence sentence in the filing and returns
that sentence with one neighbour each side, in document order. Matching is done on normalised text (cp1252 quote
bytes, typographic punctuation and non-alphanumerics folded), and accepts a truncated evidence prefix because the
corpus clips sentences at 700 characters. `assert_evidence_visible` is the A3.4 preflight; a case that fails it cannot
enter a validation sample. Because the passage is anchored on the evidence rather than chosen by vocabulary, the
"authority" blindness that hid the decisive sentence in the first run cannot recur for any vocabulary.

## 5. Measured effect on the development pool (no human label exists there)

`phase8b_v18_dev_effect.json`:

| | v1.7 | v1.8 |
| --- | --- | --- |
| predicted positives (A/B) | 1,464 (9.380%) | 1,533 (9.822%) |

76 filings gained the positive class, 7 lost it, 215 labels changed in total. The seven losses were each read and are
all intended: four are Rule 10b5-1 execution plans, one is repair A refusing `\bnew\b` in "consider new opportunities",
one is repair C correctly reading a pure extension as RENEWAL, and one is a recap sentence demoted by "at that time".

An earlier, looser version of these repairs produced +166 positives; reading a random sample of them showed roughly a
third were false positives (remaining-balance statements, execution reports, completed programmes), which would have
*diluted* precision. Those rules — a document-level renewal override and a document-level "headline announced a
programme" fallback — were **deleted** rather than kept, because false positives are the primary risk under A3.9. The
cost is accepted: a filing whose only announcement sentence carries no authorisation verb remains a false negative.

**These development-pool counts are not a precision estimate.** The dev pool has no human labels; cases were read by
the agent, not labelled. The only precision measurement that counts is the fresh 15-case blind set under A3.8.

## 6. Known limitations deliberately left unrepaired

- An explicit old date in the sentence still wins over every positive cue ("approved a new $300m program … completed
  **in December**" reads as PAST_AUTH). Conservative, pre-existing v1.7 behaviour.
- "The Board approved a new $100m program; repurchases may be made **under a** Rule 10b5-1 **plan**" is demoted by the
  pre-existing generic "under a … plan" past cue. Pre-existing in v1.7, in the false-negative direction, and left
  alone rather than risk a broad change to that guard. A regression test pins v1.8 to v1.7's behaviour here.
- Recap lists ("board of directors approved a share repurchase program for $750 million" inside a list of past-year
  accomplishments) have no clean general form and were not given a rule, exactly as Addendum 1 stated.

## 7. Verification

`python -m unittest discover -s tests` → **327 tests, OK**. 30 of them are new
(`tests/test_phase8b_repair_v18.py`): repairs A/B/C/E, every preserved distinction, the display contract, and a
mechanical check that the classifier source names no accession, no gold id and no issuer from the reference set.
No pre-existing test was weakened or deleted; the four that initially failed did so because of a temporary internal
role split (`AUTH_NEW_SIZE`), which was removed rather than have the tests rewritten.
