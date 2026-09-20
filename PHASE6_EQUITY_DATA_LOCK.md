# PHASE6_EQUITY_DATA_LOCK - chronological partitions for US equity/ETF research

Fixed on 2026-09-09 before any equity or factor performance figure was computed in this repository. This lock is independent of the crypto locks (crypto 2025 stays LOCKED and crypto 2026 UNTOUCHED regardless of anything here). Enforced programmatically by research/phase6_lock.py; tests/test_phase6_lock.py verifies the firewall.

## Partitions (apply to every Phase 6 data source: French library, Norgate or any later vendor)

| Segment | Start | End (exclusive) | Purpose | Regimes covered |
| --- | --- | --- | --- | --- |
| Development | 1963-07-01 (family-level, French library) / 1990-01-01 (stock-level, Norgate Platinum history start; Russell 3000 membership from 1990-07-01) | 2018-01-01 | hypothesis screening, architecture selection, all parameter neighbourhoods, all ensembles | 1970s stagflation, 1987 crash, 1990s bull, dot-com bubble and aftermath (2000-2003), 2003-2007 recovery, 2008 crisis, post-GFC bull (2009-2017), 2011 and 2015-16 corrections |
| Internal validation | 2018-01-01 | 2022-01-01 | one-shot confirmation of a frozen candidate set | Q4-2018 sell-off, 2019 rally, 2020 crash and recovery, 2021 retail/meme episode and rate-hike expectations |
| Final holdout | 2022-01-01 | 2026-09-01 | never inspected until the protocol's PRE_HOLDOUT freeze is satisfied and a human authorises access | 2022 inflation/rate shock bear market, 2023-2024 concentration rally, 2025-2026 |

Development eras used for replication-across-eras tests (mandate section 57), fixed now: E1 1963-07..1979-12; E2 1980-01..1999-12; E3 2000-01..2009-12; E4 2010-01..2017-12. Stock-level work uses E2b 1990-07..1999-12 in place of E1/E2.

Why these cuts: the mandate requires development to span the dot-com aftermath, 2008 and the post-GFC bull, and the holdout to remain untouched. Putting the 2020 crash in validation and the 2022 rate shock in the holdout leaves two genuinely distinct stress regimes outside development, so a candidate cannot be tuned to either. Weekday/rebalance-calendar choices, position counts and weighting rules are all part of development.

## Firewall rules

1. `phase6_lock.enforce(frame, segment)` is the only way loaders return rows; development access returns rows strictly before 2018-01-01 and never needs an unlock.
2. Validation rows are returned only if PHASE6_VALIDATION_UNLOCK.json exists at the repository root with keys frozen_candidate_hash, decision_document, decision_document_sha256, human_authorised (must be the JSON literal true) and authorised_on, and the named decision document exists with a matching SHA256. Editing the decision document after the unlock invalidates the unlock.
3. Holdout rows additionally require PHASE6_HOLDOUT_UNLOCK.json with the same structure and a valid validation unlock.
4. Neither unlock file exists today (tests/test_phase6_lock.py::test_repository_has_no_unlock_files). The agent may not create them; they are created by the human after reading the corresponding PHASE6_PREVALIDATION_DECISION.md / pre-holdout freeze document.
5. Raw vendor archives may physically contain post-2017 rows (the French zips run to 2026-07; a Norgate database is delivered whole). Raw files are hashed at acquisition and never edited; every loader truncates through the firewall; no script may read raw files except through research/phase6_french.py (or the future Norgate exporter/loader), and any new loader must call `enforce`. This mirrors the crypto practice where 2025 archives sit on disk unread.
6. No random train/test splits anywhere in Phase 6. Walk-forward inside development uses expanding or rolling windows with purging/embargo at least as long as the longest label horizon.
7. Summary statistics that could leak the locked segments (for example a full-sample factor mean printed for "context") are forbidden; the French annual blocks that extend to 2025 are never loaded by the screen scripts (the loader selects monthly/daily blocks only and truncates).

## Multiple-testing ledger

Every trial run on development is counted in PHASE6_EXPERIMENT_REGISTRY.csv with its economic family, architecture and parameter neighbourhood, continuing the cumulative hypothesis count from Phase 5 (388). Validation may be opened at most once per frozen candidate set; the number of candidates carried into validation is part of the deflation applied to the validation result.
