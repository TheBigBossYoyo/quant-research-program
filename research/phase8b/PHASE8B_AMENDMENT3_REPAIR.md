# Phase 8B Amendment 3 — classifier and instrument REPAIR PATH (E062)

Written 2026-09-20, **before any repair code was written, before any fresh case was drawn, and before any Phase 8B
return existed**. User-authorised. Supersedes nothing in Amendments 1-2 except the re-validation procedure named in
A2.5, which this amendment specifies concretely.

This is a **classifier and measurement-instrument repair**, not a strategy rescue. No return, event study, portfolio or
benchmark has ever been computed in Phase 8B, so no repair decision here can be informed by backtest performance.

---

## A3.1 The original failure is permanent

The first frozen validation stands, unaltered and unrewritten:

```
CLASSIFIER_VALIDATION_FAILED_AS_MEASURED
stratum P precision 33/38 = 86.8%   exact 95% CI [71.9%, 95.6%]   systematic flag set
classifier v1.7   reference sha256 09e31be6e09550183e6a9dc6dd5e6ffb9411174b72de170e543634017330f73a
```

Preserved and never modified: `gold/phase8b_gold_candidates_LABELED.csv`, the read-only
`gold/phase8b_gold_reference_FROZEN.csv`, `gold/phase8b_gold_key_SEALED.csv` (the v1.7 predictions),
`PHASE8B_GOLD_VALIDATION.md` (verdict + Addendum 1), `phase8b_gold_validation.json`, and the v1.7 source itself, now
archived byte-identical to its ledger hashes in `frozen_v1.7/`.

No record will ever be written that says classifier v1.7 passed.

## A3.2 Why the measurement is treated as inconclusive **for the repaired classifier**

Not because the number was disliked. Because of four documented, pre-return facts:

1. the labelling display hid the classifier's decisive evidence sentence in 13 of 38 predicted-positive cases;
2. four of the five false positives are among those hidden-evidence cases;
3. at least one entered reference label (G053, an underwriter over-allotment option to purchase additional Units) is
   demonstrably inconsistent with its own passage — that is not an issuer share-repurchase authorisation;
4. no strategy return exists, so the repair cannot be steered by performance.

The 86.8% therefore mixes classifier error with instrument error and estimates neither cleanly. It remains the final
verdict **on v1.7**. It is not evidence for or against v1.8.

## A3.3 Approved repairs — general semantics only

Only category-level semantic repairs are permitted. **No rule may be keyed to an individual filing, accession or gold
case ID.** Repairs are developed and inspected on the development pool
(`int(sha256(accession),16) % 5 == 0`) only.

| Id | Repair |
| --- | --- |
| A | `new` must be read semantically and in context. A capitalised place name in an address or glued release header ("New York", "New Jersey", "New Hampshire", "Newark") must never imply a NEW authorisation. |
| B | Forward-looking-statement, safe-harbour and risk-factor language mentioning possible repurchases or an existing authorisation never creates an event. |
| C | Explicit extension/renewal language with no material added capacity maps to RENEWAL / EXTENSION. |
| D | A release headline explicitly announcing a share-repurchase programme may count as evidence of a new authorisation when the filing/release context supports it. |
| E | "authority", "authorized amount" and equivalent authorisation nouns must be recognised as authorisation terminology (classifier **and** display vocabulary). |

Semantic distinctions already defined, explicitly preserved and regression-tested:

- "remaining under existing authorization" → ROUTINE update/status, **not** an increase;
- "in addition to existing/remaining authorization" → INCREASED;
- explicit additional capacity → INCREASED;
- a newly approved programme replacing a completed/cancelled/prior one → NEW;
- actual quarterly repurchases → ROUTINE, unless the filing says the programme is completed;
- completed / substantially completed / expired historical programme → COMPLETED_HISTORICAL;
- underwriter over-allotment options, debt securities, preferred-stock covenants → IRRELEVANT;
- an actual accelerated share repurchase agreement or execution → ASR.

## A3.4 Instrument repair (mandatory, blocking)

For **every** future validation case the default visible passage must contain, verbatim, the sentence(s) the classifier
used as its evidence. The human is never scored against hidden evidence.

Displayed by default: **the classifier evidence sentence, one preceding sentence, and one following sentence where
available**, in document order, un-reranked.

The human stays blind to: the predicted category, the margin/confidence, the rule name, the stratum and any model
rationale. Showing the evidence *text* is required; showing the model's *interpretation* is prohibited until labelling
is complete.

Mechanical preflight, run before a case may enter a validation sample:

```
classifier_evidence_visible == True     # normalised-text containment of p1_evidence in the default passage
```

A case that fails the assertion cannot enter the validation sample. The lexical `minimal_snippet` ranker of v1.7 —
the defect's source — is not used for the fresh set; it is archived as `frozen_v1.7/gold_snippet_v1.7_DEFECTIVE.py`.

## A3.5 Adjudication log (diagnostic only)

The frozen 60 are never silently modified. Objectively erroneous entered labels are recorded separately in
`PHASE8B_GOLD_ADJUDICATION_LOG.csv` with: case id, original entered label, corrected adjudicated label, the exact
passage, the reason, the date, and the cause (hidden evidence / UI defect / accidental entry / genuine semantic
reconsideration). G053 is audited specifically.

**Adjudicated labels are diagnostic only. They may never be used to restate the original verdict as a PASS**, and any
recomputation using them is reported as a counterfactual, clearly separated from the frozen result.

## A3.6 Freeze before drawing

Before a single fresh case is drawn: the repaired classifier code, its configuration, and the repaired display builder
are frozen and hashed into `PHASE8B_FREEZE_HASHES.jsonl` as `classifier frozen (Amendment 3; version 1.8 ...)`, with a
written diff of every change from v1.7 in `PHASE8B_CLASSIFIER_V18_DIFF.md`. **No classifier change is permitted after
the fresh sample has been seen.** The draw script refuses to run unless the on-disk hashes equal the frozen hashes.

## A3.7 Fresh blind validation set (frozen design)

- exactly **15** predicted-positive cases (pass-1 label A or B under v1.8);
- drawn from the **non-development** pool only;
- **excluded**: all 60 original gold accessions and CIKs, the superseded v1.5 premature draw, the 240-row labelling
  package and the 90-row retrieval-audit package (distributed to the human, therefore treated as inspected);
- one case per issuer (CIK);
- temporal balance: **8 from 2013-2017, 7 from 2004-2012**;
- seeded (`seed = 20260920 + 3`), sequential walk over the shuffled candidate list with on-demand fetch (method A2.3a,
  as used for the original set, because the 2015-2017 download is incomplete);
- the human sees the evidence-anchored passage and the wider context; never the prediction.

## A3.8 Decision rule (frozen before the draw)

n = 15 is deliberately small; uncertainty is reported honestly and the interval is never a criterion.

| Result | Verdict |
| --- | --- |
| 15 / 15 | **PASS** for DEVELOPMENT use, provided no systematic semantic error is present |
| 14 / 15 | **BORDERLINE** — inspect the single error. A new systematic failure mode → FAIL. Genuinely ambiguous / non-systematic → report BORDERLINE and **ask the user before any further step**. |
| ≤ 13 / 15 | **FAIL** |

No automatic request for another 50-60 labels. The original 60 are **not** pooled into the fresh precision estimate;
they are reported separately as development/adjudication evidence only.

## A3.9 Primary tradable superclass

The measured quantity is precision on the superclass **NEW + INCREASED**:

> when the repaired classifier says a filing is a new or increased issuer share-repurchase authorisation, how often is
> that actually true?

False positives are the primary risk. Perfect NEW-vs-INCREASED subclass separation is **not** required for the
backtest unless the preregistered strategy treats the two differently (it does not: `events` uses the A/B superclass).
Subclass confusion is still reported separately.

## A3.10 Returns stay locked

No Phase 8B event return, event study, portfolio or benchmark may be computed until the repaired classifier is frozen,
the fresh 15 labels are complete, and A3.8 has been evaluated. `phase8b_backtest.py` continues to refuse without a
`classifier gate passed` record, and a PASS under A3.8 authorises **development** use only.

Validation 2018-2021 remains locked. Holdout 2022-01..2026-08 remains locked. `phase8b_lock.py` is unchanged.

## A3.11 Multiplicity

The repair and re-validation add one further classifier-validation attempt (v1.7 → v1.8) to the Phase 8B burden. This
is recorded and carried into any later promotion decision; it is a second look at the same classification instrument,
not an independent hypothesis, and the E062 economic hypothesis itself remains untested and single.
