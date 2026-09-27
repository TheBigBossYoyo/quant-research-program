# A falsification-first quant research program

I set out to find out whether a realistically executable trading strategy exists for a small retail account (Trading 212 for equities, Binance data for crypto), and to find out honestly rather than to talk myself into something. I worked under a written research protocol that forces every hypothesis to be registered before I see its result, so a losing idea cannot quietly get retuned into a winning one after the fact.

Most of the day-to-day research work (writing code, running experiments, drafting reports) was done by AI research agents, first OpenAI Codex / GPT and then Anthropic Claude, operating under that protocol. I was the human owner of the program, making the decisions that needed a human.

**Headline result so far: 490 registered hypotheses, no qualifying strategy.** Every serious trial, including every failure and every superseded run, stays in the repository. Nothing here is investment advice, and no live or paper trading code exists.

## What is in here

| Path | Content |
| --- | --- |
| `QUANT_RESEARCH_PROTOCOL_CODEX.md`, `AGENTS.md`, `CLAUDE.md` | the research protocol and the operating rules the AI agents worked under |
| `STATUS.md`, `PLAN.md`, `EXPERIMENTS.md`, `RESEARCH_JOURNAL.md`, `PHASE6_EXPERIMENT_REGISTRY.csv` | durable state: current status, the full experiment ledger, and a narrative journal |
| `PHASE*_*.md` | preregistrations, frozen specifications (with SHA-256 hashes), red-team reports and conclusions per phase |
| `research/` | all code: data acquisition, lock-enforced loaders, signal and portfolio engines, statistics, reports |
| `research/phase8b/` | the repurchase-announcement phase: preregistration, frozen config and hash log, retrieval report, and the human labelling package and UI |
| `tests/` | 498 unit and integration tests (causality, locks, accounting, costs, timing, labelling UI) |
| `reports/` | one timestamped folder per experiment run with its JSON, Markdown and small CSV results (large panels and binaries are not published) |

## Phases, briefly

1. **Crypto (E001-E049).** BTC/ETH and a 12-asset perpetual universe, 2022-2024 development: momentum, reversal, carry and funding, aggregate taker flow, microstructure proxies, technical-indicator stacks, a slow trend rule. One frozen trend specification replicated weakly across assets and then failed an independent cohort. 2025 validation was never opened.
2. **US equities and ETFs (E050-E057).** French-library factor evidence, then stock-level momentum, residual momentum, low-risk, 52-week-high, index-event and allocation-overlay tests on a survivorship-aware liquid universe. Modern-window (2010-2017) excess returns vanish after costs, and overlays reduce drawdown without beating the index.
3. **SEC EDGAR events (E058-E061).** Insider open-market purchases, XBRL quality conditioning, and an earnings-surprise falsification cell: no alpha survives once market, size and value are controlled for.
4. **Share-repurchase announcements, Phase 8B (E062).** 110,355 candidate 8-K filings retrieved and classified, with a human labelling gate before any return was computed. The classifier passed its validation (15 out of 15 on a blind sample). The economics did not: the strategy's 2013-2017 excess over an equal-weight universe (+6.03%/yr) turns out to be the same market, size, value and momentum exposure the announcing companies already had, not new alpha, and it loses outright to buy-and-hold on the S&P 500 while carrying twice the drawdown. Rejected.
5. **Five further mechanisms, screened before any backtest.** Analyst estimate revisions, short-interest positioning, CFTC commodity hedging pressure, on-chain blockchain fundamentals, and Treasury term-structure timing were each checked first for whether a causal, point-in-time test was even possible, before spending any of the hypothesis budget on an actual backtest. All five stopped at that screening stage: point-in-time analyst data is licensed to institutions only, the free short-interest history starts after my development window has to end, and the published evidence for the other three mechanisms was too weak or too indirect to justify running a real test. None of them added a strategy cell.

## Rules the program runs under

- Chronological locks: equity development data ends 2017-12-31; validation (2018-2021) and holdout (2022-01 through 2026-08) have never been opened, and this is enforced in code, not just by discipline (`research/phase6_lock.py`, `research/phase8b_lock.py`).
- Preregistration before results. Thresholds are never relaxed afterwards. A discovered defect forces a documented rerun with the first run kept, not deleted. Every trial counts toward multiplicity.
- Realistic costs (FX, spread, slippage), next-open execution, delisting haircuts, no look-ahead in universe construction.
- A null result is an acceptable outcome. A suspiciously good one gets more scrutiny, not less.

## Why nothing has passed, and why that is the point

The honest result of this program is that 490 registered hypotheses have produced no strategy I would trust with money, and I think that is a fair outcome rather than a failed one. Several candidates looked genuinely promising on a first pass and were only rejected once I checked them against the right benchmark. The repurchase-announcement result is the clean example: it beat an equal-weighted universe by six points a year, which would look like a discovery if I had stopped measuring there. It lost to the value-weighted market instead, and had no alpha left once size and momentum were controlled for. The same pattern of a real-looking excess return over a weak benchmark that disappears against a proper one is what killed the insider-purchase and analyst-revision candidates too. A research program that never says no to anything is not measuring skill, it is measuring how many chances it gave itself to get lucky. I would rather end up with 490 honest nulls than one backtest I cannot defend.

## Data policy

No data files are published. Vendor price histories (EODHD) are licensed for personal use; Binance and SEC archives are public but large. The acquisition scripts and the hash manifests inside the reports, together with the lock-enforced loaders, reproduce the datasets. SEC requests need a declared contact: set the environment variable `SEC_USER_AGENT` (for example `"Your Name your@email"`). EODHD access needs `EODHD_API_TOKEN` in the environment; no credential is stored in this repository.

## Running it

```text
cd research
set PYTHONUTF8=1
python -m unittest discover -s ../tests
```

Python 3.12+ with numpy, pandas, pyarrow, scipy, statsmodels, requests, beautifulsoup4, lxml and exchange_calendars. The Phase 8B labelling UI (`START_PHASE8B_LABELER.bat`, standard library only) is documented in `research/phase8b/README_LABELER.md`.

## Disclaimer

Research only. Backtests are not evidence of future performance. Nothing in this repository is a recommendation to buy or sell anything.
