# Phase 8B human-labelling guide (repurchase announcements in SEC 8-K filings)

You are labelling SEC 8-K filings (2004-2017) that mention share repurchases. For each row in `phase8b_labeling_candidates.csv`
type ONE letter (A-J) into `human_label`; optional free text goes into `human_notes`. Nothing else in the file should be edited.
Save as CSV (UTF-8). The file shows the filing date, the company, the 8-K items, and text passages; it deliberately shows
**no stock price, return or later information**, and you should not look any up while labelling. The labels are ground truth
for a classifier that is developed and validated afterwards; the classifier is never allowed to see your notes.

## The question for every filing
"What is the most bullish thing about share repurchases that is genuinely NEW in this filing?" Label that.
A filing that reports quarterly progress AND announces a bigger programme is B, not D. A filing that only describes a programme
announced earlier (even a large one) is D, E, G or H depending on what it says. When in doubt between A/B and any other label,
choose the other label and write `AMBIG` in the notes: false positives hurt the research more than false negatives.

## Labels
| Label | Meaning | Typical wording |
| --- | --- | --- |
| **A** | NEW repurchase authorisation for the company's own common stock (a programme for future open-market or privately negotiated repurchases), disclosed for the first time. Includes a new programme replacing one that was exhausted or expired. Self-tender offers are NOT A (see J). | "the Board of Directors authorized a share repurchase program of up to $100 million"; "approved a new stock repurchase plan"; "authorized the repurchase of up to 2,000,000 shares" |
| **B** | INCREASE / EXPANSION of an existing authorisation that still had capacity: more dollars or shares added, or a larger programme replacing the current one before it was exhausted. | "increased the repurchase authorization by $50 million"; "expanded the existing program to $500 million"; "authorized an additional 1 million shares" |
| **C** | Renewal / extension of an existing programme's term, or re-approval, WITHOUT an increase in size. | "extended the program through December 2015"; "renewed the authorization for the remaining $40 million" |
| **D** | Routine progress / update on an existing programme: shares bought this quarter, amount remaining, "we continue to repurchase". Common in earnings releases. | "During the quarter the Company repurchased 1.2 million shares for $30 million; $120 million remains under the authorization" |
| **E** | Historical repurchases completed, described as past activity, no authorisation news. | "Since 2010 the Company has returned $2 billion through repurchases" |
| **F** | Accelerated share repurchase (ASR) execution or operational update under an existing authorisation: entering an ASR agreement, initial delivery, final settlement, share count. | "entered into an accelerated share repurchase agreement with Bank X to repurchase $200 million"; "final settlement of the ASR" |
| **G** | Programme completed / expired / terminated; nothing new authorised. | "the Company completed its $100 million repurchase program" |
| **H** | Historical reference only: background mention, risk factor, footnote, capital-allocation boilerplate. | "the Company may use cash for dividends and share repurchases" |
| **I** | False positive / irrelevant use of the words: debt or note repurchase, preferred stock, warrants, units, partnership or fund units, another company's programme, mutual-fund redemptions, employee-plan share withholding, merger-related repurchase of a target's shares. | "repurchase of the 6.5% Senior Notes"; "the Fund may repurchase its shares quarterly" |
| **J** | SELF-TENDER / DUTCH-AUCTION REPURCHASE OFFER: a newly announced issuer self-tender, fixed-price tender offer, or modified Dutch-auction tender offer for the issuer's own common stock (commencement, terms, pricing range). J is economically distinct from a board authorisation for future open-market or private repurchases and is NOT part of the primary A/B signal. If the same filing ALSO clearly announces a new or increased general repurchase authorisation that is separate from the tender, label A or B and write `TENDER` in notes; if the only news is the tender, or it is unclear whether a separate general authorisation exists, use J. Results, extensions, expirations or final counts of a tender already announced -> D or G with `TENDER` in notes. | "commenced a modified Dutch auction tender offer to purchase up to 5,000,000 shares of its common stock at a price not less than $20 and not more than $23"; "announced a fixed-price self-tender offer" |

## Decision aids
1. Look first for words like *authorized*, *approved*, *new*, *additional*, *increase*, *expand*, *replace*, *up to*. Then check whether the
   sentence refers to THIS filing's news or to something that happened earlier ("previously announced", "as announced on ...", "existing").
2. **A vs B:** B needs an existing programme that is being enlarged. "A new $1 billion program, replacing the prior program under which $50 million remained" -> B (capacity still existed). "A new program; the prior program was completed / expired" -> A.
3. **B vs C:** an extension in time only is C; more money or shares is B.
4. **D vs B:** an earnings release that says "the Board increased the authorization" is B; one that only reports what was bought is D.
5. **F:** an ASR is a way of executing an existing authorisation. If the SAME filing also announces a new/increased authorisation, label A or B and write `ASR` in notes.
6. **I:** if the "repurchase" is not the company's own common (or ordinary) stock, it is I, whatever the wording.
7. Amended filings (8-K/A) are not in the sample; if you see one, note it.
8. If the passages are not enough to decide, open the full text file named in `full_text_path` (same folder, `labeling_texts/`).
9. Non-US issuers filing 8-K (rare) are labelled like any other.
10. If you believe the filing does not mention repurchases at all, use I and note `NOMENTION`. This happens when the search
    matched an exhibit type that is not part of the package (for example a warrant or credit agreement filed as EX-10 that
    says "purchase up to"); the classifier sees exactly the same text you see (8-K body and EX-99 exhibits), so I is the right label.
11. Some rows have empty passage columns for the same reason; open the full text file to confirm before labelling I.

## What NOT to do
- Do not look up the stock, its price, the size of the company, what happened afterwards, or the company's later filings.
- Do not infer the label from the company name or from what "usually" happens.
- Do not skip rows; if truly undecidable, write your best non-A/B label and `AMBIG`.

## Optional notes tags
`AMBIG`, `TENDER` (only on A/B/D/G rows that also involve a tender; J rows need no tag), `ASR`, `SIZE=<dollars or shares or % as stated>`, `PRIOR=<what remained of the previous programme, if stated>`, `NOMENTION`, `PRESSREL_DATE=<date printed on the press release if it differs from the filing date>`.
The `SIZE` and `PRESSREL_DATE` notes are used only for descriptive characterisation, never for labels.

## Second file: `phase8b_retrieval_audit_candidates.csv`
Same labels (A-J), same rules. These filings were NOT captured by the main search expressions; they are used to estimate how many
real A/B announcements the retrieval misses (design: PHASE8B_RETRIEVAL_AUDIT_DESIGN.md). Label them with exactly the same standard.

## What the files deliberately do not show
No stock price, return, market capitalisation, index membership, current ticker symbol, or anything dated after the filing. The
company name, filing date, acceptance time, 8-K item codes and SIC description are as printed in the filing itself.
