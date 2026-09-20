# PHASE8_DATA_AUDIT - rules for the SEC insider data audit (frozen 2026-09-12 before any event return); results in PHASE8_SEC_DATA_AUDIT.md

| Test | Rule | Consequence |
| --- | --- | --- |
| D1 acquisition integrity | every quarterly ZIP 2006Q1..2017Q4 present, SHA256 logged, opens with the expected nine tables | missing quarter blocks the phase |
| D2 schema stability | the NONDERIV_TRANS, SUBMISSION, REPORTINGOWNER columns used by the rules exist in every quarter | schema change is handled explicitly or the quarter is dropped and reported |
| D3 code and date sanity | TRANS_CODE distribution per year; FILING_DATE >= TRANS_DATE for >= 99 percent of code-P rows (negative delays are data errors, excluded and counted); TRANS_TIMELINESS values in {E, L, blank} | descriptive; violations excluded |
| D4 ticker mapping | share of code-P rows mapped to a priced EODHD code per year; unmapped share reported; mapping by symbol, `_old` variants, then CIK | if mapping < 70 percent in any development year, the year is flagged MAPPING_GAP in results |
| D5 duplicates and amendments | counts of within-accession duplicates, cross-accession duplicates, and originals later amended (4/A with DATE_OF_ORIG_SUB equal to the original FILING_DATE and the same owner/issuer) | descriptive; the amended-original rerun is a red-team item |
| D6 price plausibility | share of code-P rows whose price is within [0.8, 1.2] of the EODHD close; the rest excluded | if < 80 percent of mapped rows pass, the mapping is re-examined before proceeding |
| D7 hand reconciliation | ten randomly selected included events (seed 20260912) are checked against the actual Form 4 documents on EDGAR (transaction date, shares, price, owner name, relationship, filing date) | any field mismatch in more than one of ten blocks the phase until explained |
| D8 event counts | included events per year, per role, cluster share, opportunistic share, timely share, median purchase value | descriptive; G10 needs >= 150 entered events in 2013-2017 per cell |
| D9 universe coverage | share of events on Tier 2 eligible names at entry; share on PIT S&P 1500 names from 2012-04 | descriptive |
