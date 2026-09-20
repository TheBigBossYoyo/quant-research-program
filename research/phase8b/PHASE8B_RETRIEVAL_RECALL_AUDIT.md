# PHASE8B_RETRIEVAL_RECALL_AUDIT - part (a): XBRL cross-check (built 2026-09-12T22:10:24.396547+00:00; blind to returns)

Issuers scanned: 4,473 (companyfacts on disk, facts filed >= 2018 removed at read time). Authorisation increases detected (amount or share count up > 1% versus the previous filing): 658.

**Share with a candidate 8-K of the same CIK in the 120 calendar days ending on the 10-Q/10-K filing date: 0.772**

By kind: {'shares': {'n': 283, 'recall': 0.6643109540636042}, 'usd': {'n': 375, 'recall': 0.8533333333333334}}

By year:

| year | n | recall |
| --- | --- | --- |
| 2011 | 8.000 | 0.750 |
| 2012 | 24.000 | 0.750 |
| 2013 | 52.000 | 0.692 |
| 2014 | 64.000 | 0.703 |
| 2015 | 162.000 | 0.815 |
| 2016 | 191.000 | 0.754 |
| 2017 | 157.000 | 0.809 |

Interpretation limits (preregistered): an issuer need not file an 8-K for an authorisation (many disclose in the 10-Q itself), and the XBRL tag changes for reasons other than a new programme; this number is a lower bound on 8-K retrieval recall for authorisation changes that were also announced by 8-K, and an upper bound on what an 8-K-only pipeline can see. Part (b), the human-labelled complement sample, is reported in PHASE8B_CLASSIFIER_HOLDOUT.md once labels exist; total system recall = retrieval recall x classifier recall.
