# Phase 8B gold validation: 60 cases, about one hour

1. Double-click `START_PHASE8B_GOLD_LABELER.bat` (repository root). A black window stays open and your browser opens `http://127.0.0.1:8766/`. Do not open the HTML file directly.
2. Each screen shows one filing: company, date, 8-K items, and only the 1-3 decisive sentences (median about 320 characters), with cue words of every category highlighted alike and amounts in bold. "Show the full extracted passage" and "Show wider context" (key W) are collapsed by default. If the decisive sentence alone could not separate NEW from INCREASED or RENEWAL, one extra neighbouring sentence is shown in grey. The snippet is computed from the stored passage only and never from any model output; the frozen 60-case file is not modified. Each category card carries its definition and a "Why?" example.
3. Press a key (or click):

| Key | Label | Meaning |
| --- | --- | --- |
| 1 / N | NEW | new authorisation to repurchase the company's own common stock, first disclosed here |
| 2 / I | INCREASED | existing programme enlarged with additional dollars or shares |
| 3 / R | RENEWAL | extended in time or re-approved, no increase |
| 4 / U | ROUTINE | shares bought, amount remaining, or a restatement of earlier news |
| 5 / S | ASR | accelerated share repurchase entered or settled under an existing authorisation |
| 6 / H | COMPLETED_HISTORICAL | programme completed, expired or terminated, or only a past/background mention |
| 7 / X | IRRELEVANT | not the company's own common stock (debt, preferred, warrants, options, funds, other company) |
| 8 / A | AMBIGUOUS | the passage does not let you decide whether something new or increased was authorised |
| 9 / T | SELF_TENDER | newly announced tender offer / Dutch auction for the company's own shares (kept out of NEW / INCREASED) |

4. Every label is written to disk before the next case appears (`research/phase8b/gold/phase8b_gold_candidates_LABELED.csv`; backups in `gold/backups/`). Close any time; reopening resumes at the first unlabeled case. Left arrow = previous, right arrow = next unlabeled, Ctrl+Z = undo.
5. Nothing about any model is shown, before or after a label: no prediction, confidence, rationale or stratum. The key file (`phase8b_gold_key_SEALED.csv`) is never read by the app; please do not open it until the evaluation has run.
6. When all 60 are done, tell Claude. `research/phase8b_gold_eval.py` then applies the frozen rule (Amendment 2): precision of NEW + INCREASED on the 38 randomly sampled predicted positives: >= 95% and no repeated error pattern = PASS; 90% to < 95% = BORDERLINE (at most 10-15 more targeted cases); < 90% = FAIL; two or more routine updates or two same-rule errors among the predicted positives = FAIL or repair. No repurchase-event return is computed before a PASS.

Set composition (not shown per case): 38 predicted NEW/INCREASED (19 from 2013-2017, 19 from 2004-2012), 10 obvious non-signals, 12 hard cases (pass disagreements, low-margin and unclassified filings), in random order. The earlier 240 + 90 labelling package is superseded and does not need to be labelled.
