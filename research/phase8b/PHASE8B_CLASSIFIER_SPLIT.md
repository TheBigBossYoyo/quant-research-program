# PHASE8B_CLASSIFIER_SPLIT - frozen classifier partition of the 240 main labelling candidates (2026-09-12, before any label)

File: research/phase8b/phase8b_classifier_split.csv (columns event_id, accession, cik, year, stratum, classifier_partition). SHA-256: a41851f9edd62878d76ffcbb2656d924bea3aab30182c2bdc04b914974452e27. Mirror used by the evaluation harness: phase8b_label_split.csv (DEV/HOLDOUT). Both depend only on the seeded sample order, filing year, stratum and CIK; no human label, text content or price enters.

| Partition | Rows |
| --- | ---: |
| DEVELOPMENT | 167 |
| HOLDOUT | 73 |

Year distribution:

| year | DEVELOPMENT | HOLDOUT |
| --- | --- | --- |
| 2004 | 11 | 4 |
| 2005 | 12 | 5 |
| 2006 | 12 | 6 |
| 2007 | 13 | 6 |
| 2008 | 11 | 7 |
| 2009 | 12 | 4 |
| 2010 | 12 | 4 |
| 2011 | 12 | 5 |
| 2012 | 12 | 5 |
| 2013 | 12 | 5 |
| 2014 | 12 | 6 |
| 2015 | 12 | 6 |
| 2016 | 12 | 5 |
| 2017 | 12 | 5 |

By stratum: {('S1', 'DEVELOPMENT'): 111, ('S1', 'HOLDOUT'): 49, ('S2', 'DEVELOPMENT'): 56, ('S2', 'HOLDOUT'): 24}.
Duplicate CIKs: 238 distinct issuers among 240 rows; 2 issuers appear twice (different years or strata); issuers straddling the partitions: 0 (rule: every row of a CIK inherits the partition of that CIK's first assigned row, cells visited in year/stratum order).
Rule: HOLDOUT = positions 2, 5, 8, ... of a seeded permutation (seed 20260912 + 1) inside every year x stratum cell, then the CIK rule. Development code reads labels through phase8b_classifier_eval.load_labels, which blanks HOLDOUT labels; HOLDOUT is scored once by evaluate_holdout after the classifier files match their frozen hashes. The split is not changed after labels are entered.
