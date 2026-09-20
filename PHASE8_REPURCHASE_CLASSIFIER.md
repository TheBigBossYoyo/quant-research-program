# PHASE8_REPURCHASE_CLASSIFIER - E059 status: STOPPED AT THE CLASSIFIER STAGE (2026-09-12)

## What was done (no return computed)
- EDGAR full-text search (efts.sec.gov) scanned month by month for 8-K filings 2009-01..2017-12 matching the fixed phrase set `"share repurchase program" OR "stock repurchase program" OR "repurchase authorization" OR "buyback program" OR "repurchase of up to"`: 33,388 hits, all metadata (accession id, CIK, display name, file date, 8-K items) stored under data/raw/phase8/fts/hits_<month>.json.gz; monthly counts in data/derived/phase8/fts_counts.json (maximum 729 in one month, inside the search cap).
- The hit set is the candidate pool for a classifier that must separate NEW or INCREASED authorisations from progress updates, completions, accelerated-repurchase execution updates, historical references and incidental uses of "repurchase".

## Why E059 stops here
The frozen rule (PHASE8_PREREGISTRATION.md section 5; user instruction) requires at least 200 hand-labelled filings and a reported precision/recall before any return test, and says to stop rather than backtest noisy labels. Hand-labelling 200 filings means reading 200 8-K documents and exhibits; this was not completed in the present session, and no keyword rule was substituted for it. The pool and the phrase set are preserved so that a future session can label the sample (seeded selection: 200 hits drawn with seed 20260912 across years), report precision/recall, and only then run the preregistered 252-session long-only calendar-time test.

## Consequence for the phase outcome
E059 contributes no evidence for or against the repurchase family. The Phase 8 decision rests on E058 (and E060 where run).
