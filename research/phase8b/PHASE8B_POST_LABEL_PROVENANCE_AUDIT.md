# Phase 8B — post-label provenance audit of the fresh-15 scoring script

Requested by the user 2026-09-20, **after** the fresh-15 evaluation had already been run. This audit is therefore
**retrospective**: it does not gate the score, it tests whether the score that was produced is sound. It is recorded
here whatever the outcome.

## Timeline (append-only ledger, UTC)

| time | event |
| --- | --- |
| 18:50:31 | Amendment 3 preregistered and hashed — contains the A3.8 decision rule **text** (15/15 PASS, 14/15 BORDERLINE, ≤13 FAIL) |
| 19:18:36 | classifier v1.8 frozen: `phase8b_classifier.py`, `phase8b_corpus.py`, `phase8b_display.py` |
| 19:20:39 | fresh 15-case set drawn and hashed (candidates, sealed key, meta) |
| 19:25:35 | `phase8b_gold2_eval.py` hashed `da8e26ff…` — **after the draw**, before any label |
| 19:28:26 | commit `3e1644a` (contains that exact file) |
| ~21:17 | human labelling completed |
| 21:19:01 | labels frozen to read-only copy, `780eaa02…` |
| ~21:19 | **two provenance edits to the scoring script** (this audit's subject) |
| 21:20:22 | evaluation run → PASS 15/15 |

**Disclosure.** The eval *script* was hashed about five minutes **after** the draw, not before it. The decision *rule*
it implements was preregistered at 18:50:31, before the classifier freeze and before the draw. There is no
contamination path — the draw is determined by the frozen classifier, the seed and the exclusion lists, none of which
can see the scoring script — but the ordering is stated plainly rather than described as "frozen before the draw".

## The exact diff

Baseline reconstructed from git commit `3e1644a` (made before labelling); its SHA-256 is `da8e26ff1f98…`, matching the
19:25:35 ledger record exactly, so it is the authentic pre-label file.

```diff
--- pre-label  (da8e26ff1f980fa70193ed01c1dd4399d99047d9c9d63a518d828ee5cc48b4db)
+++ scoring    (4f9b4ba89febc3edab968822ea5d1c729b008e7fb54e16146e7f4c3151e3b0af)
@@ -37,9 +37,12 @@
-LABELED = GOLD2 / 'phase8b_gold2_candidates_LABELED.csv'
+LABELED = GOLD2 / 'phase8b_gold2_reference_FROZEN.csv'   # frozen and hashed before evaluation
-REFERENCE_KIND = 'HUMAN_ENTERED_REFERENCE_SET_WITH_VISIBLE_CLASSIFIER_EVIDENCE'
+REFERENCE_KIND = 'FRESH_BLIND_TO_CLASSIFIER_AI_ASSISTED_HUMAN_ADJUDICATION'
+REFERENCE_NOTE = ("Labels entered by the human owner while blind to the repaired classifier's predictions, with the "
+                  'classifier evidence sentence visible (A3.4). The owner consulted an independent LLM to interpret '
+                  'filing passages. This is NOT unaided independent human annotation.')
@@ -117,7 +120,7 @@
-        reference_sha256=hashlib.sha256(LABELED.read_bytes()).hexdigest(),
+        reference_sha256=hashlib.sha256(LABELED.read_bytes()).hexdigest(), reference_note=REFERENCE_NOTE,
```

Three hunks. Nothing else. (The file was also rewritten with LF line endings; that changes no byte of logic and the
diff above is line-ending insensitive.)

Both edits fall inside the two permitted categories:

1. **reading the frozen read-only label copy** — and this is provably a no-op, because
   `phase8b_gold2_candidates_LABELED.csv` and `phase8b_gold2_reference_FROZEN.csv` are **byte-identical**
   (`780eaa025d2db6d13173e750a053d4a2ba0a73ee53265bf754fd293d3de0be8a` both);
2. **provenance/reference-set description text** — a constant string and one extra field in the written report.

## Mechanical confirmation

**Constants** — identical in both versions: `PASS_MIN = 15`, `BORDERLINE_MIN = 14`, `N_EXPECTED = 15`,
`POS_HUMAN = set(CFG['primary_positive_human'])` (= {NEW, INCREASED}), `HUMAN`, `KEY`.

**Functions** — byte-identical in both versions: `clopper_pearson()`, `load()`, `systematic()`, `verdict()`,
`prior_run_reference()`, `write_report()`, `main()`. Only `evaluate()` differs, by the single added
`reference_note=` report field shown above. Every function that determines the outcome is untouched.

**End-to-end** — the pre-label script was executed against the same data (its `evaluate()` only; `main()` was not
called, so nothing was written and the ledger was not touched):

```
PRE-LABEL script : PASS 15/15 precision 1.0
CURRENT  script  : PASS 15/15 precision 1.0
fields differing (excluding timestamp and provenance text): NONE
identical: verdict, headline, systematic, errors, by_period,
           subclass_new_vs_increased, human_label_counts, reference_sha256
```

## Explicit confirmations

No post-label change affected any of the following:

| item | status | evidence |
| --- | --- | --- |
| classifier predictions | **unchanged** | sealed key hash matches its 19:20:39 draw-time record |
| extraction rules | **unchanged** | `phase8b_corpus.py` = `659f2834…`, frozen 19:18:36 |
| semantic classification rules | **unchanged** | `phase8b_classifier.py` = `4a0c6b54…`, frozen 19:18:36; 0 commits after `3e1644a` |
| NEW/INCREASED superclass mapping | **unchanged** | `POS_HUMAN` line identical; read from frozen `phase8b_config.json` |
| candidate selection | **unchanged** | `phase8b_gold2.py` unchanged; 0 commits after `3e1644a` |
| sample composition | **unchanged** | candidates / sealed key / meta all match their draw-time hashes |
| correctness definition | **unchanged** | `load()` byte-identical (`human_primary = human_label ∈ POS_HUMAN`) |
| scoring equations | **unchanged** | `clopper_pearson()`, `evaluate()` arithmetic byte-identical |
| PASS/BORDERLINE/FAIL thresholds | **unchanged** | `verdict()` byte-identical; 15 / 14 constants identical |
| subclass NEW-vs-INCREASED treatment | **unchanged** | `subclass_new_vs_increased` crosstab identical; never enters `verdict()` |
| any case-specific logic | **none exists** | no gold2 id, accession or issuer appears in either version |

## Hashes retained

| artefact | SHA-256 |
| --- | --- |
| classifier (pre-label, pre-draw) `phase8b_classifier.py` | `4a0c6b54a9a7b49cc8df04e8436d133d5801b7f220e6d76a9930a2c60ae21301` |
| corpus builder `phase8b_corpus.py` | `659f2834d98aa912076998a0a47f57506cdf511fae4e487193140d16dc71be58` |
| display module `phase8b_display.py` | `7a372efa1b062c1c73e4136d1c271e80d5451b29390ae22299cba9fa7336036f` |
| scoring script, pre-label | `da8e26ff1f980fa70193ed01c1dd4399d99047d9c9d63a518d828ee5cc48b4db` |
| scoring script, final | `4f9b4ba89febc3edab968822ea5d1c729b008e7fb54e16146e7f4c3151e3b0af` |
| fresh-15 frozen labels | `780eaa025d2db6d13173e750a053d4a2ba0a73ee53265bf754fd293d3de0be8a` |
| original 60 frozen labels (untouched) | `09e31be6e09550183e6a9dc6dd5e6ffb9411174b72de170e543634017330f73a` |

## Audit result

**PASS.** The two post-label edits are provenance-only and provably scoring-neutral: the pre-label script reproduces
the reported result exactly, field for field. The reported 15/15 PASS stands as measured.
