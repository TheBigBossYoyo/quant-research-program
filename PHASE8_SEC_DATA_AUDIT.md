# PHASE8_SEC_DATA_AUDIT - results of the frozen audit rules (PHASE8_DATA_AUDIT.md), 2026-09-12; no event return was computed before this document

## D1 acquisition
48 quarterly ZIPs 2006Q1..2017Q4 plus the readme acquired from sec.gov (533 MB), SHA256 per file in data/metadata/phase8_sec_acquisition_*.jsonl; every ZIP opens with the nine expected tables. Nothing from 2018 onward was downloaded.

## D2 schema
SUBMISSION, REPORTINGOWNER and NONDERIV_TRANS carry the fields used by the rules in all 48 quarters. Submissions: 2,722,773 (document types {'4': 2385951, '3': 197085, '4/A': 70772, '5': 55883, '3/A': 11072, '5/A': 2010}). Code-P non-derivative rows: 596,340.

## D3 codes and dates
Rows with FILING_DATE before TRANS_DATE (negative delay): 209 of 512,797 candidate rows (0.041 percent), excluded. TRANS_TIMELINESS values observed: blank, E, L.

## Row filter funnel (PHASE8_EVENT_RULES.md section 2)
| Step | Rows |
| --- | ---: |
| 0_code_p_joined | 596,340 |
| 1_original_form4 | 562,927 |
| 2_acquired_form4_trans | 552,541 |
| 3_common_equity_title | 520,429 |
| 4_positive_shares_price | 512,943 |
| 5_no_swap | 512,797 |
| 6_nonnegative_delay | 512,586 |
| 7_value_ge_10k | 250,355 |
| 8_after_duplicates | 246,106 |
| 9_mapped | 180,998 |
| 10_price_plausible | 164,027 |

Within-accession duplicates removed: 2,495; cross-accession duplicates removed: 1,754.

## D4 ticker mapping
| Year | Code-P rows (after filters) | Mapped to a priced EODHD code | Share |
| --- | ---: | ---: | ---: |
| 2006 | 25,436 | 16,884 | 0.66 |
| 2007 | 35,166 | 23,103 | 0.66 |
| 2008 | 46,508 | 31,959 | 0.69 |
| 2009 | 16,532 | 11,242 | 0.68 |
| 2010 | 14,386 | 9,869 | 0.69 |
| 2011 | 17,971 | 13,847 | 0.77 |
| 2012 | 14,574 | 11,600 | 0.80 |
| 2013 | 12,365 | 9,667 | 0.78 |
| 2014 | 15,919 | 13,301 | 0.84 |
| 2015 | 17,971 | 14,629 | 0.81 |
| 2016 | 16,280 | 13,805 | 0.85 |
| 2017 | 12,998 | 11,092 | 0.85 |

Years below the 0.70 threshold (2006-2010) are flagged MAPPING_GAP; unmapped rows are dominated by OTC/pink-sheet issuers with no EODHD history, which could not be eligible in the liquid universe. The 2009-2012 window therefore carries the flag; the gate window 2013-2017 maps at 0.78-0.85.

## D5 amendments
Original Form 4 rows whose (issuer, owner, filing date) was later amended by a 4/A: 8,481 of 246,106 (3.4 percent). Amendments are excluded from the signal; a rerun excluding later-amended originals is a red-team item.

## D6 price plausibility
Share of mapped rows whose reported price lies within [0.80, 1.20] of the EODHD close on or before the transaction date: 0.906 (threshold 0.80 passed). Rows outside the band (private placements at a discount, data errors) are excluded.

## D7 hand reconciliation (seed 20260912, ten included rows, EDGAR documents fetched on 2026-09-12)
| Accession | Issuer | Dataset filing date | EDGAR filed | EDGAR acceptance (ET) | Transaction date / shares / price match | Owner CIK and role match |
| --- | --- | --- | --- | --- | --- | --- |
| 0001221432-14-000057 | Calamos Asset Management, Inc. /DE/ (CLMS) | 2014-06-13 | 2014-06-13 (refetched) | 20140613171144 (refetched) | yes | yes |
| 0000109380-11-000314 | ZIONS BANCORPORATION /UT/ (ZION) | 2011-09-01 | 20110901 | 20110901191613 | yes | yes |
| 0000919574-16-017050 | TransDigm Group INC (TDG) | 2016-12-06 | 20161206 | 20161206190245 | yes | yes |
| 0001179110-15-008280 | StarTek, Inc. (SRT) | 2015-05-21 | 20150521 | 20150521160202 | yes | yes |
| 0001225208-16-033767 | UDR, Inc. (UDR) | 2016-05-23 | 20160523 | 20160523114130 | yes | yes |
| 0001104659-10-062046 | Howard Hughes Corp (HHC) | 2010-12-10 | 20101210 | 20101210083048 | yes | yes |
| 0001418214-11-000004 | Orient Paper Inc. (ONP) | 2011-09-21 | 20110921 | 20110921154243 | yes | yes |
| 0001209191-09-043354 | KONA GRILL INC (KONA) | 2009-09-03 | 20090903 | 20090903190043 | yes | yes |
| 0001140361-17-023988 | REGENERON PHARMACEUTICALS INC (REGN) | 2017-06-06 | 20170606 | 20170606170040 | yes | yes |
| 0001465740-15-000105 | TWO HARBORS INVESTMENT CORP. (TWO) | 2015-11-18 | 20151118 | 20151118163601 | yes | yes |

All ten filings reconcile: dataset filing dates equal EDGAR filing dates; acceptance timestamps fall on the filing date (three before 16:00 ET, seven after), so entry at the open of the next trading day is always after acceptance; transaction dates, share counts, prices, owner CIKs and relationships match the filed XML. Multi-line filings (TDG, HHC, REGN, CLMS) confirm that the dataset carries one row per transaction line, which the duplicate and aggregation rules handle. D7 PASS.

## D8 events
| Year | Events (issuer-filing-day) | Cluster | Opportunistic | Officer | Director-only | Timely share | Median purchase value USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2006 | 4,970 | 1,536 | 7 | 1,604 | 2,320 | 0.90 | 78,978 |
| 2007 | 6,665 | 2,623 | 97 | 2,340 | 3,027 | 0.89 | 75,900 |
| 2008 | 9,045 | 3,677 | 733 | 3,294 | 3,773 | 0.89 | 76,011 |
| 2009 | 5,275 | 1,914 | 733 | 1,923 | 2,523 | 0.89 | 50,000 |
| 2010 | 4,719 | 1,359 | 1,054 | 1,589 | 2,346 | 0.91 | 64,789 |
| 2011 | 6,404 | 2,399 | 1,330 | 2,556 | 2,967 | 0.91 | 70,221 |
| 2012 | 5,305 | 1,768 | 1,209 | 2,060 | 2,393 | 0.91 | 70,608 |
| 2013 | 4,358 | 1,398 | 867 | 1,522 | 2,201 | 0.92 | 80,590 |
| 2014 | 5,628 | 2,075 | 1,188 | 2,232 | 2,686 | 0.92 | 87,421 |
| 2015 | 7,170 | 2,748 | 1,565 | 2,882 | 3,070 | 0.92 | 85,040 |
| 2016 | 6,336 | 2,300 | 1,327 | 2,417 | 2,818 | 0.91 | 84,582 |
| 2017 | 5,649 | 1,980 | 1,391 | 2,137 | 2,524 | 0.91 | 99,635 |

Total events 2006-2017: 71,524. Opportunistic classification needs three prior purchase years, hence the ramp from 2009. D9 (share on Tier 2 eligible names and on the PIT S&P 1500) is reported in PHASE8_INSIDER_EVENT_STUDY.md from the backtest's event preparation.
