# PHASE8_VALIDATION_DECISION

# **DEVELOPMENT GATE: FAIL - EDGAR_EVENT_FAMILY_REJECTED**

Date 2026-09-12. Frozen rules: PHASE8_PREREGISTRATION.md (hashes in PHASE8_PREREGISTRATION.sha256). No threshold was changed after results; two runs superseded for defects found before interpretation are retained (reports/E058_superseded_*).

## Basis
- E058 insider open-market purchases (five preregistered cells, reports/E058_20260912T185148): no cell passes G1-G10 with multiplicity. The only cell with a positive 2013-2017 excess over the equal-weight universe (C5 DIRECTOR_ONLY, +7.55 percent a year, t 2.78, five positive years, BH pass) has no alpha against SPY (CAPM t -0.52; FF3 alpha -2 percent a year with market beta 1.2, SMB 0.17, HML 0.20) and a deflated-Sharpe probability of 0.89; it fails G4. C1 ANY +2.82 percent (t 0.75) with alpha t -1.45; C2 CLUSTER, C3 OPPORTUNISTIC and C4 OFFICER do not beat the universe. Event-study abnormal returns after the conservative next-day-open entry are negative or zero at every horizon (PHASE8_INSIDER_EVENT_STUDY.md).
- E060 quality conditioning: both cells rejected; no coherent interaction (PHASE8_QUALITY_CONDITIONING.md).
- E059 repurchase announcements: stopped at the classifier stage per the frozen rule (no hand-labelled validation set; PHASE8_REPURCHASE_CLASSIFIER.md); contributes no evidence.
- E061 earnings falsification: see the appended result below.
- Red team (PHASE8_RED_TEAM.md): the equal-weight excess is market, size and value exposure of insiders buying beaten-down smaller stocks; no single year, stock, insider or event drives it; costs do not change any gate.

## Consequence
Nothing is frozen for validation. The validation segment 2018-2021 is NOT opened. The holdout 2022-01..2026-08 is NOT opened. No purchase is requested. Cumulative ledger 488 cells (E058 5, E060 2, E059 1 not run, E061 1).

## What would reopen this family
A demonstrated positive alpha against the deployable benchmark under the frozen rules on an independent construction (for example weekly entries capturing the first five sessions after acceptance with a documented USD-balance execution path), preregistered as a new experiment; or a validated repurchase-announcement classifier (E059) meeting the precision requirement.

## E061 result (appended 2026-09-12)
SUE top decile 63-session abnormal return +0.2 percent (CI -2.9 to +2.2), bottom decile -1.0 percent (CI -4.7 to +1.5); 2013-2017 top and bottom both +0.3 percent; top-decile portfolio excess over the EW universe +4.0 percent a year (t 1.43) with zero alpha against SPY. No post-announcement drift in the free XBRL data; the falsification holds. Final outcome unchanged: EDGAR_EVENT_FAMILY_REJECTED.
