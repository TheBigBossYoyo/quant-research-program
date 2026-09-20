# PHASE8B_RETRIEVAL_AUDIT_DESIGN - sampling frame and estimator for the retrieval-recall audit, part (b) (written 2026-09-12 before any label exists)

## 1. Question
Does the Stage 1 target-expression retrieval (24 expressions, PHASE8B_PREREGISTRATION.md section 3) miss genuine A/B announcements (new or increased general repurchase authorisations) that an 8-K disclosed? Part (a) asks this with XBRL authorised-amount increases (PHASE8B_RETRIEVAL_RECALL_AUDIT.md: 77% of 658 increases have a candidate 8-K within 120 days). Part (b) asks it with human labels on filings the target set did not capture.

## 2. Population (sampling frame)
Every accession returned by the EDGAR full-text search (forms 8-K, filing dates 2004-01-01..2017-12-31, one query per expression per calendar month) for at least one audit expression - "repurchase", "repurchases", "repurchased", "buyback", "buy back", "buy-back" - and for no target expression (the complement), restricted to accessions whose search-index form is 8-K (8-K/A, listed separately by the index, are excluded) and whose CIK is known. No text was read to build the frame; no secondary keyword or heuristic search was used; the only extra attribute is the search index's 8-K item list.
Total frame: 124,261 accessions (complement before the form/CIK restriction: 129,569).

Frame limits, stated plainly: a filing that announces an authorisation without any of the six audit words (for example "acquire up to 2 million shares") is outside both the candidate pool and this frame and cannot be found by this audit; the XBRL cross-check (part a) is the only check that reaches such filings.

## 3. Strata
| Stratum | Definition (search-index items of the accession) | Frame count N_s | Sample n_s | Weight N_s/n_s | Sampling probability |
| --- | --- | ---: | ---: | ---: | ---: |
| B1 | items include 8.01 (Other Events) or 7.01 (Reg FD) and do not include 2.02 (earnings) - where stand-alone announcements are filed | 44,034 | 60 | 733.9 | 0.00136 |
| B2 | all other complement accessions (earnings releases with 2.02, and other items) | 80,227 | 30 | 2674.2 | 0.00037 |

The sample is stratified random, enriched by design (B1 is over-sampled relative to its frame share because stand-alone announcements are far more likely there). Within each stratum the rows are allocated across filing years in proportion to the stratum's counts with a floor per year (B1: 2, B2: 1); the order inside each year x stratum cell is a seeded permutation (seed 20260912 + 3) after keeping one accession per issuer per year; the first k rows that are eligible after fetching (header form 8-K, acceptance time present, text present) are kept (0 rows replaced). It is not a convenience sample: every row is eligible because it is in the frame, and nothing about its content selected it.

Per year:

| year | population_B1 | population_B2 | sample_B1 | sample_B2 |
| --- | --- | --- | --- | --- |
| 2004 | 4373 | 10725 | 5 | 3 |
| 2005 | 9741 | 5950 | 9 | 3 |
| 2006 | 4223 | 5939 | 5 | 2 |
| 2007 | 3015 | 5628 | 4 | 2 |
| 2008 | 1803 | 5103 | 3 | 2 |
| 2009 | 2225 | 5440 | 3 | 2 |
| 2010 | 2273 | 5334 | 4 | 2 |
| 2011 | 2239 | 5325 | 3 | 2 |
| 2012 | 2365 | 5239 | 4 | 2 |
| 2013 | 2317 | 5181 | 4 | 2 |
| 2014 | 2267 | 5114 | 4 | 2 |
| 2015 | 2343 | 5033 | 4 | 2 |
| 2016 | 2341 | 5105 | 4 | 2 |
| 2017 | 2509 | 5111 | 4 | 2 |

## 4. Estimator (frozen)
Let p_s be the share of stratum-s sample rows labelled A or B by the human. Missed A/B filings in the complement: M = N_B1 p_B1 + N_B2 p_B2 (stratum-weighted; a raw pooled rate over the 90 rows is never reported as a recall figure). Found A/B filings in the candidate pool: F = N_S1 q_S1 + N_S2 q_S2, where q_s is the A/B share in the main labelling sample's strata (N_S1 = 49,884, N_S2 = 57,250; n = 160 / 80). Retrieval recall = F / (F + M), with a 95% interval from a stratified bootstrap of the four binomial shares (1,000 draws, seed 20260912) and Wilson intervals per stratum reported alongside. Classifier recall is reported separately (HOLDOUT); total system recall = retrieval recall x classifier recall. Sampling weights are therefore required (N_s / n_s per stratum) and are stored in phase8b_retrieval_audit_meta.json and phase8b_labeling_meta.json.

## 5. What 90 rows can and cannot say
Expected A/B counts: if the true miss rate is 5% in B1 and 0.5% in B2, the sample yields about 3 and 0 positives. With 0 of 30 positives in B2 the Wilson 95% upper bound is 11.4%, i.e. up to about 9,100 missed filings in B2 alone, versus an F in the low thousands to low tens of thousands depending on q_S1 and q_S2. So the audit bounds the miss rate but cannot estimate retrieval recall to better than roughly plus or minus 15-25 points; it is a coarse check, not a precise measurement, and will be reported as such. A precise estimate (plus or minus 5 points) would need on the order of 300-500 complement labels, most of them in B2; the user may extend the sample with the same seeded order (data/derived/phase8b/complement_sample_ordered.parquet holds three times the quota per cell) before any label is read by the classifier process. This is written before labels exist so that the wide interval cannot be re-interpreted afterwards; part (a) remains the sharper instrument for authorisation changes that reached XBRL.
Rows whose 8-K body and EX-99 exhibits contain none of the keywords (the search matched another exhibit type; 37 of 90 rows have empty passages) are labelled I with NOMENTION by the guide; for the estimator they count as not-A/B, which is correct for an 8-K-body/EX-99 pipeline.

## 6. Provenance
Frame: data/derived/phase8b/complement.parquet (built from the per-expression hit caches). Sample and strata: research/phase8b/phase8b_retrieval_audit_strata.csv, phase8b_retrieval_audit_meta.json (hashed in PHASE8B_FREEZE_HASHES.jsonl). The earlier 60-row year-only design (2026-09-12, never labelled) is superseded and recorded in phase8b_config.json.
