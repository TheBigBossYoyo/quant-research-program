"""Render an evidence summary from immutable experiment results."""
import json
from pathlib import Path
from core import ROOT

def main():
    screen_path=ROOT/'reports/E001_20260908T094021'
    audit_path=ROOT/'reports/E002_20260908T094107'
    stress_path=ROOT/'reports/E003_20260908T094233'
    s=json.loads((screen_path/'results.json').read_text())
    a=json.loads((audit_path/'results.json').read_text())
    t=json.loads((stress_path/'results.json').read_text())
    base=[r for r in s['rows'] if r['case']=='base']
    signals=[r for r in base if r['family'] not in ['buyhold','sma']]
    pct=lambda v:f'{100*v:.1f}%'
    lines=['# Initial research findings — 2026-09-08', '',
        '**Verdict: no strategy currently passes. No paper/live eligibility.**','',
        'These are development-only results for 2022–2024, in USDT, using current standard spot commission plus assumed execution friction. No OOS performance is claimed. 2025 archives were acquired but were not loaded into analysis; 2026 final test was not acquired. No credentials or orders were used.','',
        '## Evidence and decision','',
        f"- {len(signals)} registered signal-asset configurations; 20 simple benchmark configurations. Three cost scenarios each; all 270 results retained.",
        '- Zero of 42 configurations at 5/15/60 minutes produced positive base-cost cumulative returns. This rejects these specific rules under these assumptions, not all short-horizon alpha.',
        '- Two daily 48-bar momentum candidates passed the cheap stress screen. Both failed even unadjusted 95% uncertainty checks; multiple-testing correction strengthens rejection.',
        '- Both also suffered approximately 45–47% development drawdowns at 1x exposure when invested. Leverage is not justified.',
        '- Eight additional neighboring signal-asset configurations were examined only for falsification (78 total). No parameter replacement or retuning adopted.',
        '- All 96 raw monthly archives (43,010,937 compressed bytes) match official SHA256. Development: 315,632 observed bars per asset; sixteen missing and fourteen zero-volume bars each. Signal completeness and executable bucket-open observations are separated.','',
        '## Serious candidate comparison','',
        '| Strategy | Market | Timeframe | Net CAGR | Sharpe | Sortino | Max DD | Trades | Costs | OOS | Robustness / verdict |',
        '|---|---|---|---:|---:|---:|---:|---:|---|---|---|']
    for r in base:
        if r['minutes']==1440 and (r['family'] in ['buyhold','sma','flow'] or r['family']=='momentum' and r['lookback']==48):
            lines.append(f"| {r['family']} {r['lookback']} | {r['symbol']} | daily | {pct(r['cagr'])} | {r['sharpe']:.2f} | {r['sortino']:.2f} | {pct(r['max_drawdown'])} | {r['trades']} | 12 bps/side | Not opened | {'Benchmark only' if r['family'] in ['buyhold','sma'] else 'REJECTED for promotion'} |")
    lines+=['','## Uncertainty and adversarial risk','']
    for x in a['results']:
        u=x['development_uncertainty'];ci=u['sharpe_ci95'];ai=u['arithmetic_alpha_annual_ci95']
        lines.append(f"- {x['candidate']['symbol']}: 14-day block-bootstrap Sharpe 95% interval [{ci[0]:.2f}, {ci[1]:.2f}], annualized arithmetic alpha versus buyhold [{pct(ai[0])}, {pct(ai[1])}]. Both include zero. These are descriptive development intervals, not held-out estimates.")
    for x in t['audits']:
        risk=x['unlevered_drawdown_risk']['probability_max_drawdown_exceeds']
        lines.append(f"- {x['symbol']}: in 4,000 resampled 365-day paths at 1x, maximum drawdown exceeded 30% in {pct(risk['0.3'])} and 50% in {pct(risk['0.5'])}. Conditional resampling is not a calibrated future probability. Alpha intervals also include zero with 7/30/60-day blocks.")
    lines+=['','BTC neighboring lookbacks all remain positive at stressed costs but retain roughly 46–54% maximum drawdowns. ETH is more parameter-sensitive. A broad positive region does not remove uncertainty, beta exposure or unacceptable tail risk. No need to consume validation to rescue these failed evidence gates.','',
        '## Capital and implementation limits','',
        'The symbol snapshots give a 5-USDT minimum notional for both assets, quantity steps 0.00001 BTC and 0.0001 ETH, and a 0.01-USDT price tick. These are current snapshots, not historical filter histories. EUR500 is not assumed equal to 500 USDT. No EUR conversion return series or account entitlements were available. Minimum efficient capital is **not established**.','']
    for x in t['liquidity']:
        lines.append(f"- {x['symbol']}: 0.1% of the historical first-percentile five-minute quote volume is {x['conservative_0_1pct_of_p1_quote_volume_usdt']:.2f} USDT. This is a conservative volume-based order bound, not an executable depth estimate.")
    lines+=['','A 500-USDT hypothetical order passes that volume bound for BTC but not ETH; split/smaller orders or narrower liquidity conditions would be needed under the proposed rule. Actual order size is not modeled in the first screen. Zero-volume intervals cannot execute. Fees: 10 bps optimistic (fee-only floor), 12 bps base (10+2 assumed friction), 24 bps stress (20+4). No maker fill, BNB discount, borrow, funding or leverage assumption.','',
        'Rounding, minimum notionals, fee-asset dust, historical spreads/depth, partial fills, disconnect handling, EUR conversion and independent circuit breakers are not implemented in this Phase-I screen. Costs/slippage are scenarios, not venue-calibrated fills; no execution or capital-readiness claim is permitted. Actual risk allocation remains zero.','',
        '## Research integrity and next decision','',
        'The earlier E001_20260908T093818 and E002_20260908T093848 runs are superseded because an incomplete aggregate bar could erase a valid earlier fill. The original artifacts remain on disk; a targeted regression test and corrected rerun replace their evidentiary role. Fourteen tests pass.','',
        'Do not expand random indicators or unlock holdout after this failure. Highest-value next branch is to establish actual account jurisdiction, Binance product entitlements and Trading 212 account/currency, then preregister a feasible alternative (long-only same-currency equities/ETFs with corporate-action-safe data, or properly funded carry if derivatives are permitted). Current records do not establish those user-specific facts. Longer-history crypto trend research is possible, but is not a reason to promote this weak three-year result.','',
        'See VENUE_CONSTRAINTS_2026-09-08.md for official source URLs, retrieval date, account-specific unknowns and measured-versus-assumed distinctions. No paid subscriptions or live trading.','',
        '## Complete base-cost screen (including failures)','',
        '| Market | Minutes | Rule | Lookback | Net CAGR | Sharpe | Max DD | Trades | Decision |',
        '|---|---:|---|---:|---:|---:|---:|---:|---|']
    for r in base:
        lines.append(f"| {r['symbol']} | {r['minutes']} | {r['family']} | {r['lookback']} | {pct(r['cagr'])} | {r['sharpe']:.2f} | {pct(r['max_drawdown'])} | {r['trades']} | {'Benchmark' if r['family'] in ['buyhold','sma'] else 'REJECTED for promotion'} |")
    lines+=['','Full metrics, cost scenarios, calendar returns, integrity/provenance, parameters, seeds and code fingerprints:','',
        '- E001_20260908T094021/results.json and metrics.csv',
        '- E002_20260908T094107/results.json',
        '- E003_20260908T094233/results.json and parameter_surface.csv','']
    with (ROOT/'reports/INITIAL_RESEARCH_REPORT_2026-09-08.md').open('x',encoding='utf8') as f:
        f.write('\n'.join(lines))

if __name__=='__main__':main()
