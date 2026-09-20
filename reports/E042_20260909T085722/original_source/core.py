"""Auditable long/cash screening, not an order simulator or live broker."""
from pathlib import Path
import hashlib
import json
import zipfile
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COLS = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
        'quote_volume', 'trades', 'taker_base', 'taker_quote', 'ignore']

def config():
    c = json.loads((ROOT / 'config/research.json').read_text())
    if c['mode'] != 'research_only' or c['live_trading'] or not c['final_test_locked']:
        raise ValueError('Only research with locked final test is implemented')
    return c

def code_hash():
    h = hashlib.sha256()
    for p in sorted((ROOT / 'research').glob('*.py')) + [ROOT / 'config/research.json']:
        h.update(p.name.encode()); h.update(p.read_bytes())
    return h.hexdigest()

def load_data(symbol, validation=False):
    c = config()
    years = range(2022, 2026 if validation else 2025)
    frames, sources = [], []
    for year in years:
        for month in range(1, 13):
            p = ROOT / 'data/raw' / f'{symbol}-5m-{year}-{month:02}.zip'
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            assert digest == p.with_name(p.name+'.CHECKSUM').read_text().split()[0]
            sources.append(dict(file=p.name, sha256=digest))
            with zipfile.ZipFile(p) as z:
                assert len(z.namelist()) == 1
                with z.open(z.namelist()[0]) as f:
                    d = pd.read_csv(f, names=COLS)
            # Binance spot switched archive timestamps from ms to us in Jan 2025.
            unit = 'us' if d.time.iloc[0] > 10**14 else 'ms'
            d.index = pd.to_datetime(d.time, unit=unit, utc=True)
            ct = pd.to_datetime(d.close_time, unit=unit, utc=True)
            assert ((ct.to_numpy() >= d.index.to_numpy()) &
                    (ct.to_numpy() < (d.index + pd.Timedelta(minutes=5)).to_numpy())).all()
            frames.append(d)
    d = pd.concat(frames)
    assert d.index.is_unique and d.index.is_monotonic_increasing
    assert (d.index.minute % 5 == 0).all() and (d.index.second == 0).all()
    assert np.isfinite(d[COLS]).all().all()
    assert (d[['open','high','low','close']] > 0).all().all()
    assert (d.high >= d[['open','close','low']].max(axis=1)).all()
    assert (d.low <= d[['open','close','high']].min(axis=1)).all()
    assert (d[['volume','quote_volume','trades','taker_base','taker_quote']] >= 0).all().all()
    assert (d.taker_base <= d.volume + 1e-7).all()
    end = c['validation_end_exclusive'] if validation else c['train_end_exclusive']
    expected = pd.date_range(c['start'], end, freq='5min', inclusive='left', tz='UTC')
    assert d.index.min() >= expected.min() and d.index.max() <= expected.max()
    missing = expected.difference(d.index)
    integrity = dict(symbol=symbol, rows=len(d), missing_count=len(missing),
                     missing_timestamps=[x.isoformat() for x in missing],
                     zero_volume_bars=int((d.volume == 0).sum()),
                     unchanged_close_bars=int((d.close.diff() == 0).sum()),
                     start=str(d.index.min()), end=str(d.index.max()), sources=sources)
    return d.reindex(expected), integrity

def aggregate(d, minutes):
    g = d.resample(f'{minutes}min', label='left', closed='left', origin='epoch')
    a = g.agg(dict(open='first', high='max', low='min', close='last', volume='sum',
                   quote_volume='sum', taker_base='sum', trades='sum'))
    a.loc[g.open.count() != minutes // 5, :] = np.nan
    # Signal completeness must not erase a valid earlier execution price.
    # This avoids using a later-in-bucket outage to decide a fill at bucket open.
    a['execution_open'] = d.open.reindex(a.index)
    a['execution_volume'] = d.volume.reindex(a.index)
    return a

def signal(d, family, lookback):
    if family in ('momentum','reversal'):
        s = d.close / d.close.shift(lookback) - 1
        s = s.where(d.close.rolling(lookback+1).count() == lookback+1)
        return s if family == 'momentum' else -s
    if family == 'flow':
        return (2*d.taker_base/d.volume-1).where(d.volume > 0)
    if family == 'sma':
        return d.close / d.close.rolling(lookback).mean() - 1
    if family == 'buyhold':
        return pd.Series(1., index=d.index)
    raise ValueError(family)

def simulate(d, s, cost_bps, delay=2):
    """Signal at close t, transact at open t+2; full bar latency.

    Long/cash all-in binary transitions only. Entry units reserve exact proportional
    cost; exit costs charged on appreciated notional. Missing marks explicitly carry
    last observed open with no fills; the next observed price books the entire gap.
    Terminal liquidation at last observed open (no fabricated last close fill).
    """
    if delay < 2:
        raise ValueError('Require at least one full bar after close')
    if cost_bps < 0:
        raise ValueError('Negative cost')
    target = (s > 0).astype(float).shift(delay).fillna(0.)
    price = d['execution_open'] if 'execution_open' in d else d.open
    volume = d['execution_volume'] if 'execution_volume' in d else d.volume
    tradable = price.notna() & (volume > 0)
    target = target.where(tradable).ffill().fillna(0.)
    valid = np.flatnonzero(tradable.to_numpy())
    if len(valid) < 2:
        raise ValueError('Insufficient prices')
    target.iloc[valid[-1]:] = 0.
    mark = price.ffill()
    r = (mark.shift(-1)/mark-1).fillna(0.)
    change = target.diff().fillna(target.iloc[0])
    c = cost_bps/10000
    factor = pd.Series(1., index=d.index)
    factor.loc[change > 0] = 1/(1+c)
    factor.loc[change < 0] = 1-c
    net = factor*(1+target*r)-1
    return pd.DataFrame(dict(net=net, gross=target*r, position=target,
                             turnover=change.abs(), asset_return=r))

def metrics(b, minutes):
    r = b.net
    equity = (1+r).cumprod()
    peak = equity.cummax().clip(lower=1.)
    dd = equity/peak-1
    daily = (1+r).resample('1D').prod()-1
    years = len(daily)/365.25
    vol = daily.std(ddof=1)*np.sqrt(365.25)
    sharpe = daily.mean()/daily.std(ddof=1)*np.sqrt(365.25) if vol > 0 else 0.
    downside = np.sqrt(np.mean(np.minimum(daily, 0.)**2))*np.sqrt(365.25)
    cagr = float(equity.iloc[-1]**(1/years)-1)
    pos = b.position.to_numpy()
    changes = np.diff(np.r_[0., pos])
    entries = np.flatnonzero(changes > 0)
    exits = np.flatnonzero(changes < 0)
    assert len(entries) == len(exits)
    # Include entry cost and exit cost in each closed round-trip.
    prefix = np.r_[1., equity.to_numpy()]
    trades = prefix[exits+1]/prefix[entries]-1
    wins = trades[trades > 0]; losses = trades[trades < 0]
    durations = (exits-entries)*minutes/60
    underwater = (dd < -1e-12).to_numpy()
    runs = np.diff(np.r_[0, np.flatnonzero(~underwater)+1, len(dd)+1])-1
    benchmark = b.asset_return
    var = benchmark.var()
    beta = r.cov(benchmark)/var if var > 0 else 0.
    alpha = (r.mean()-beta*benchmark.mean())*(365.25*1440/minutes)
    q = float(daily.quantile(.05))
    return dict(cumulative_return=float(equity.iloc[-1]-1), cagr=cagr,
        annualized_volatility=float(vol), sharpe=float(sharpe),
        sortino=float(daily.mean()*365.25/downside) if downside else None,
        calmar=cagr/abs(float(dd.min())) if dd.min() < 0 else None,
        max_drawdown=float(dd.min()), average_drawdown=float(dd.mean()),
        max_drawdown_duration_days=float(max(runs, default=0)*minutes/1440),
        trades=len(trades), win_rate=float(np.mean(trades > 0)) if len(trades) else None,
        profit_factor=float(wins.sum()/-losses.sum()) if len(losses) else None,
        payoff_ratio=float(wins.mean()/-losses.mean()) if len(wins) and len(losses) else None,
        expectancy=float(trades.mean()) if len(trades) else None,
        turnover=float(b.turnover.sum()), avg_holding_hours=float(durations.mean()) if len(durations) else None,
        exposure=float(b.position.mean()), beta=float(beta), arithmetic_alpha_annual=float(alpha),
        skew=float(daily.skew()), excess_kurtosis=float(daily.kurt()),
        daily_var95_loss=-q, daily_cvar95_loss=-float(daily[daily <= q].mean()),
        calendar_returns={str(y):float((1+x).prod()-1) for y,x in daily.groupby(daily.index.year)})
