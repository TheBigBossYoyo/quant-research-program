# Phase 4 E040 frozen specification

Status: frozen before new-asset strategy evaluation. No Git repository exists; provenance uses SHA256 file manifests. The original sources were preserved in reports/E042_20260909T085722/original_source. Original E040 results reproduce exactly, including bootstrap and alpha output. User explicitly authorized accounting correction while preserving all signal rules.

## Exact rules and provenance

The accompanying JSON-form YAML is the canonical machine-readable specification. Configuration SHA256: a5c5e208bd2c635cb9918047e5cfdab13823fb05020fc6cd146759679a004826. Source hashes are embedded there. Trend has SEVEN equally averaged available votes, not eight: sign(close minus SMA150/200/250), and sign(SMA100/150/200/250 minus that SMA five bars earlier). SMA has full-period warmup; pandas mean skips unavailable votes. There is no EMA or trend stop. Exposure changes only when the target changes. The breakout is the exact E040-selected E038 implementation: prior 20-bar high/low channel, Wilder ATR14, preceding-bar ATR rank below .20 over 250 bars with minimum120, no volume gate, 3ATR stop with prior completed-bar ATR at entry and trailing high/low updates after each completed bar. A stopped direction remains blocked until the raw target leaves it.

Equal E040 is 50/50 daily component returns. Inverse volatility uses 60 trailing daily standard deviations shifted one day, reciprocal normalized weights, and cash when weights are undefined. Preserve these conventions including trend terminal marking and breakout liquidation. No asset-specific parameters or leverage optimization.

## Approved accounting corrections

Separate the raw hourly observation at a 4h bucket start from complete-bucket signal OHLC. A later missing hour must not cancel an earlier opening order. Preserve latest observed mark across gaps. Debit or credit funding to incoming holdings at scheduled settlement, before orders or later stops. Convert funding timestamp jitter to the nearest scheduled hour only within 60 seconds, log every displacement, and reject unresolvable non-4h-boundary events. Funding mark open is an explicit approximation, with trade-open fallback labelled and stressed. Return insolvency is absorbing. Trade metrics include actual dollar fees and funding. Original sizing and all signal arrays are unchanged; E042 verifies equality on BTC and ETH. Equity drift can exceed1x: measured maximum trend exposure1.29 BTC and1.51 ETH. This is the original sizing interpretation permitted by the mandate, not a hard unlevered guarantee.

## Universe and study design

Select historically as of2021-12-31, not by today's capitalization. Require >=365-day listing age, >=360 observed2021 daily bars, median daily quote turnover>=20m USDT over2021-07-01..2021-12-31; top12 by that liquidity, excluding BTC/ETH. The minimum-history rule is one full year known at selection plus a planned three-year replication horizon2022-2024. Do not retrospectively require survival for all three years: later delisted names stay included. This avoids selecting winners through minimum-history survival. Exhaustive historical membership depends on the existing archived-contract inventory and is not guaranteed to include every historical symbol. Legacy research already used other signals on this panel: this is frozen-architecture replication, not a pristine unseen cross-section.

Warmup uses pre2022 prices only; initialize flat with signals from prior completed bars at2022 start. No replication performance is inspected for2020/2021. All outcomes across2022-2024 count, including delistings and losses. Data eligibility and universe hashes must be published before any strategy run.

## Allocation, inference and gate

See canonical configuration for exact predefined methods and thresholds. The primary estimand is cross-asset median annual daily-regression intercept, tested with common-time block resampling14/30/60days so crypto dependence remains. Intercept is an arithmetic return premium relative to factors, not proof of causal alpha. Secondary component and allocation comparisons cannot substitute for a failed primary portfolio. Median Sharpe .3 is a modest practical effect floor; majority2/3 requires breadth;95% common-block lower alpha bounds require uncertainty evidence;40% primary DD and concentration limits are risk vetoes, not significance thresholds. Report sensitivity honestly without changing gates.

2025 remains locked until every gate passes and a second final freeze exists.2026 is always protected. No current prices, volume or2026 data may support selection. No live trading, subscriptions or capital exposure.
