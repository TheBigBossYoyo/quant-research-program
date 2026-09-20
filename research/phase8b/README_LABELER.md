# Phase 8B human labeler

1. Double-click `START_PHASE8B_LABELER.bat` (this folder, or the copy in the repository root). A black window stays open and your browser opens `http://127.0.0.1:8765/`.
2. Read the filing (passages first; "View full filing text" shows the whole 8-K and exhibits inside the page).
3. Click one label A-J (or press the letter key when no text box has focus). The label is written to disk before the next filing appears.
4. Progress autosaves after every click; the header shows Main / Retrieval-audit / Total completion. Notes are optional and save on blur or with the label.
5. Close the window (or the browser) whenever you want; nothing is lost.
6. Reopen later with the same .bat: it resumes at the first unlabeled filing, keeps every label and note, and lets you revisit and change earlier ones (Undo last label restores the previous value on disk).
7. Finished files (source CSVs are never modified):
   - `research/phase8b/phase8b_labeling_candidates_LABELED.csv` (main sample, 240 rows)
   - `research/phase8b/phase8b_retrieval_audit_candidates_LABELED.csv` (retrieval audit, 90 rows)
   - `research/phase8b/PHASE8B_HUMAN_LABELING_INTEGRITY.txt` (written when both are complete: row counts, valid/blank counts, hashes; no label distribution)
   - `research/phase8b/backups/` (a copy at every start and every 25 saves)

Shortcuts: A-J label, Left arrow previous, Right arrow next unlabeled, Ctrl+Z undo, Esc closes the full-text view. Shortcuts are ignored while typing in a text box.

The app shows only the CSV columns and the referenced text file. It never preselects, ranks, suggests, or counts labels by class, and it has no access to prices, returns or anything dated after the filing.
