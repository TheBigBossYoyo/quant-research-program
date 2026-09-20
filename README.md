# A falsification-first quantitative research program

This repository is the complete working record of a preregistered search for a realistically executable trading
strategy for a very small retail account (EUR 500-1,000, Trading 212 for equities, Binance data for crypto).
It was run by AI research agents (OpenAI Codex / GPT, then Anthropic Claude) under a written protocol, with a human
owner making the decisions that needed a human.

**Headline result so far: 489 registered hypotheses, no qualifying strategy.** Every serious trial, including every
failure and every superseded run, is kept. Nothing here is investment advice, and no live or paper trading code exists.

## What is in here

| Path | Content |
| --- | --- |
| `QUANT_RESEARCH_PROTOCOL_CODEX.md`, `AGENTS.md`, `CLAUDE.md` | the research protocol and the operating rules the agents worked under |
| `STATUS.md`, `PLAN.md`, `EXPERIMENTS.md`, `RESEARCH_JOURNAL.md`, `PHASE6_EXPERIMENT_REGISTRY.csv` | durable state: current status, the experiment ledger (E001-E062), and a narrative journal |
| `PHASE*_*.md` | preregistrations, frozen specifications (with SHA-256 files), red-team reports and conclusions per phase |
| `research/` | all code: data acquisition, lock-enforced loaders, signal/portfolio engines, statistics, reports |
| `research/phase8b/` | Phase 8B (repurchase announcements): preregistration, frozen config and hash log, retrieval report, human-labelling package and the local labelling UI |
| `tests/` | 265 unit and integration tests (causality, locks, accounting, costs, timing, labelling UI) |
| `reports/` | one timestamped folder per experiment run with its JSON/Markdown/small CSV results (large panels and binaries are not published) |

## Phases in one paragraph each

1. **Crypto, Phases 1-5 (E001-E049).** BTC/ETH and a 12-asset perpetual universe, 2022-2024 development: momentum,
   reversal, carry/funding, aggregate taker flow, microstructure proxies, technical-indicator stacks, a slow trend
   rule. One frozen trend specification replicated weakly across assets and then failed an independent cohort.
   2025 validation was never opened.
2. **US equities and ETFs, Phases 6-7A (E050-E057).** French-library factor evidence, then stock-level momentum,
   residual momentum, low-risk, 52-week-high, index-event and allocation-overlay tests on a survivorship-aware liquid
   universe. Modern-window (2010-2017) excess returns vanish after costs; overlays reduce drawdown but do not beat the
   index.
3. **SEC EDGAR events, Phase 8 (E058-E061).** Insider open-market purchases, XBRL quality conditioning and an
   earnings-surprise falsification cell: no alpha after market, size and value controls.
4. **Phase 8B (E062), in progress.** New or increased share-repurchase authorisations disclosed by 8-K. The design is
   frozen and hashed; 110,355 candidate filings were retrieved; the branch is **stopped at a human-label gate**: a
   person must label 240 + 90 filings before any classifier is built or any return is computed.

## Rules the program runs under

- Chronological locks: equity development data end 2017-12-31; validation 2018-2021 and holdout 2022-01..2026-08
  have **never been opened** and are blocked in software (`research/phase6_lock.py`, `research/phase8b_lock.py`).
- Preregistration before results; thresholds never relaxed afterwards; defects force a documented rerun with the
  first run retained; every trial counted for multiplicity.
- Realistic costs (FX, spread, slippage), next-open execution, delisting haircuts, no look-ahead in universes.
- A null result is an acceptable outcome. A suspiciously good result gets more scrutiny, not less.

## Data policy

No data files are published. Vendor price histories (EODHD) are licensed for personal use; Binance and SEC archives
are public but large. The acquisition scripts, manifests of hashes inside the reports, and the lock-enforced loaders
reproduce the datasets. SEC requests need a declared contact: set the environment variable `SEC_USER_AGENT`
(for example `"Your Name your@email"`). EODHD access needs `EODHD_API_TOKEN` in the environment; no credential is
stored in this repository.

## Running

```text
cd research
set PYTHONUTF8=1
python -m unittest discover -s ../tests
```

Python 3.12+ with numpy, pandas, pyarrow, scipy, statsmodels, requests, beautifulsoup4, lxml and exchange_calendars.
The Phase 8B labelling UI (`START_PHASE8B_LABELER.bat`, standard library only) is documented in
`research/phase8b/README_LABELER.md`.

## Disclaimer

Research only. Backtests are not evidence of future performance. Nothing in this repository is a recommendation to
buy or sell anything.
