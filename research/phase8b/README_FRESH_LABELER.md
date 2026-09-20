# Fresh 15-case post-repair validation — how to label

**Time: about 10-15 minutes.** No money, no downloads, nothing to install beyond Python.

## Start

Double-click **`START_PHASE8B_FRESH_LABELER.bat`** in the repository root. Your browser opens
`http://127.0.0.1:8767/`. Keep the console window open while you label. Every click is written to disk immediately, so
you can close it and reopen to resume.

Output: `research/phase8b/gold2/phase8b_gold2_candidates_LABELED.csv`.

## What changed since the 60-case round

The first round measured 33/38 = 86.8%, a **FAIL**, and that result stands permanently. But the labelling page was
also defective: in 13 of the 38 cases it did **not** show you the sentence the automated rule had actually keyed on,
and 4 of the 5 disagreements were among those cases. You were being scored against evidence you could not see.

That is fixed. In this round the passage on screen is **the sentence the rule acted on, plus one sentence before and
one after**, in document order. Nothing is ranked, scored, shortened or dropped. This was verified mechanically for
all 15 cases before the set was released (`phase8b_gold2_preflight.json`: `classifier_evidence_visible` true 15/15).

You still do **not** see the prediction, the confidence, the rule name or the category the machine chose — that stays
sealed until every label is saved. Showing you the evidence *text* is required; showing you the machine's
*interpretation* is not allowed.

## What you are deciding

All 15 filings are ones the repaired classifier calls a **new or increased issuer share-repurchase authorisation**.
The single question the study needs answered is:

> Is this filing really announcing a new or enlarged authorisation by the company to buy back its own shares?

Pick the label that fits what the passage actually says. Keys `1`-`9`; `←` back; `→` next; `Ctrl+Z` undo; `W` opens
the wider context.

| Key | Label | Use it when |
| --- | --- | --- |
| 1 | NEW | A genuinely new repurchase programme/authorisation is announced. |
| 2 | INCREASED | An existing authorisation is enlarged ("an additional $50 million", "in addition to the remaining authorization"). |
| 3 | RENEWAL / EXTENSION | The existing programme simply runs longer, is renewed or reaffirmed, with no material new amount. |
| 4 | ROUTINE UPDATE | Purchases already made, remaining capacity, quarterly progress. No new board authorisation. |
| 5 | ASR / EXECUTION | An actual execution agreement, including accelerated share repurchase transactions. |
| 6 | COMPLETED / HISTORICAL | Describes a past or completed programme, or historical repurchases. |
| 7 | IRRELEVANT | Not an issuer common-share repurchase at all: debt or notes, preferred, warrants, options, over-allotment options to underwriters, another company, a fund. |
| 8 | AMBIGUOUS | The passage genuinely is not enough to decide, even after opening the wider context. |
| 9 | SELF-TENDER | A newly announced tender offer / Dutch auction for the company's own shares. |

Two points worth keeping in mind, because they came up last time:

- An **underwriter's or initial purchaser's option to buy additional units or notes** is `7 IRRELEVANT`. It is not the
  company buying back its own shares, however much the words "additional" and "purchase" appear.
- **"Remaining under the existing authorization"** is `4 ROUTINE`; **"in addition to the existing authorization"** is
  `2 INCREASED`. The difference is whether new capacity is being granted.

Use `8 AMBIGUOUS` honestly rather than guessing. A case you cannot decide is real information about the classifier.

## After you finish

Tell Claude, or run from `research/`:

```
PYTHONUTF8=1 python phase8b_gold2_eval.py
```

The decision rule was frozen before the set was drawn and is not negotiable afterwards:

- **15/15** → PASS for development use, provided no systematic semantic error;
- **14/15** → BORDERLINE: the single error is inspected and **you are asked** before anything further happens;
- **13/15 or fewer** → FAIL.

There will be no automatic request for another 50-60 labels. The original 60 cases are not pooled into this estimate.

No strategy return will be computed unless the verdict is PASS, and a PASS authorises **development** use only.
The 2018-2021 validation window and the 2022-2026 holdout stay locked either way.
