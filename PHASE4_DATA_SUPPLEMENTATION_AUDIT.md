# Phase 4 data supplementation audit

Purpose: data integrity only. Twenty official Binance daily 1h kline archives fill the 120 hours missing from each of four monthly archives. Merging adds rows only where the monthly archive has none; any overlapping hour must be byte-identical or the loader fails. No forward fill, no synthetic rows, no signal, sizing, cost, funding or universe change. The first pass (E044_20260909T092223) is retained unchanged and labelled superseded.

| Asset | Missing period | Original source status | Supplemental source | Hash/checksum | Treatment |
| --- | --- | --- | --- | --- | --- |
| SOLUSDT | 2022-02-26 00:00-23:00 UTC (24 hours) | monthly archive SOLUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/SOLUSDT/1h/SOLUSDT-1h-2022-02-26.zip | 24fbcb67b854564ee8f0d14028b277c272083c59ad2fd8bcbc8d496712fb57dc | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| SOLUSDT | 2022-02-27 00:00-23:00 UTC (24 hours) | monthly archive SOLUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/SOLUSDT/1h/SOLUSDT-1h-2022-02-27.zip | 4a3f57259893da63acf2978799f3fb28bc8130ca95f23fe08ed11eaaff1840b1 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| SOLUSDT | 2022-02-28 00:00-23:00 UTC (24 hours) | monthly archive SOLUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/SOLUSDT/1h/SOLUSDT-1h-2022-02-28.zip | ea4f7d6d0dbca651066ef3e361e5457b1eba91ac077a942f48344a174abee40e | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| SOLUSDT | 2022-04-01 00:00-23:00 UTC (24 hours) | monthly archive SOLUSDT-1h-2022-04.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/SOLUSDT/1h/SOLUSDT-1h-2022-04-01.zip | 186d8581e36ce03557fc0e517c2923a0c7cb6f8e5ecb47b9e7086f6bcefd7971 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| SOLUSDT | 2022-04-02 00:00-23:00 UTC (24 hours) | monthly archive SOLUSDT-1h-2022-04.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/SOLUSDT/1h/SOLUSDT-1h-2022-04-02.zip | 9fe6fc49767488828f44db95d52412dcefd2b2b28924a92ab5461590fa80844c | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| XRPUSDT | 2022-02-26 00:00-23:00 UTC (24 hours) | monthly archive XRPUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/XRPUSDT/1h/XRPUSDT-1h-2022-02-26.zip | d419516ba374ab4200f4d4817748545c4ce7e49aac657086bebd1220abbf12c8 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| XRPUSDT | 2022-02-27 00:00-23:00 UTC (24 hours) | monthly archive XRPUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/XRPUSDT/1h/XRPUSDT-1h-2022-02-27.zip | b09dbb334e5951ed1fed51ceb65cdbb6a061b2d6212b9f67e4a957f9e683a433 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| XRPUSDT | 2022-02-28 00:00-23:00 UTC (24 hours) | monthly archive XRPUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/XRPUSDT/1h/XRPUSDT-1h-2022-02-28.zip | 0e6587a0fd2c66e5716d7d6457cbb10ab8ce4e2b9bd52497e33c9cd49f6de351 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| XRPUSDT | 2022-04-01 00:00-23:00 UTC (24 hours) | monthly archive XRPUSDT-1h-2022-04.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/XRPUSDT/1h/XRPUSDT-1h-2022-04-01.zip | df4d9cca7b11d850ce0fa8d6dcd43dbf29a354c2a15446d80e1fa4dd4a4a59dd | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| XRPUSDT | 2022-04-02 00:00-23:00 UTC (24 hours) | monthly archive XRPUSDT-1h-2022-04.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/XRPUSDT/1h/XRPUSDT-1h-2022-04-02.zip | 98e3150b8510696a1d26fc948e9ad4d80b427ebcd791bf11263ac302cd66aa36 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| FTMUSDT | 2022-02-26 00:00-23:00 UTC (24 hours) | monthly archive FTMUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/FTMUSDT/1h/FTMUSDT-1h-2022-02-26.zip | abbbed954de32ff246f3268cbd4cf3361840ff853123cb4046de8fd4419129c8 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| FTMUSDT | 2022-02-27 00:00-23:00 UTC (24 hours) | monthly archive FTMUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/FTMUSDT/1h/FTMUSDT-1h-2022-02-27.zip | 9489972291a66f6c18eb3f6ddbc8b12109f35bbd3677ea2e4c0c643c899f2969 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| FTMUSDT | 2022-02-28 00:00-23:00 UTC (24 hours) | monthly archive FTMUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/FTMUSDT/1h/FTMUSDT-1h-2022-02-28.zip | da5f066c2da04f74911de33c8b4e76db2a8f8cd75f6b16c9e4f11fd8cef8df45 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| FTMUSDT | 2022-04-01 00:00-23:00 UTC (24 hours) | monthly archive FTMUSDT-1h-2022-04.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/FTMUSDT/1h/FTMUSDT-1h-2022-04-01.zip | 87bb785f6432555c46800241eef57fed9634d4da91e3c7ce2a48f3a7605eb5f4 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| FTMUSDT | 2022-04-02 00:00-23:00 UTC (24 hours) | monthly archive FTMUSDT-1h-2022-04.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/FTMUSDT/1h/FTMUSDT-1h-2022-04-02.zip | 573c852b1c2e42671f4228c4909a19ab1fcc2990488197ee6669face6867862b | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| LTCUSDT | 2022-02-26 00:00-23:00 UTC (24 hours) | monthly archive LTCUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/LTCUSDT/1h/LTCUSDT-1h-2022-02-26.zip | 426ccd90cb2b9c17da9fc1ad4e7eb07067764a332066a8e7ec75c88e6ffcce18 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| LTCUSDT | 2022-02-27 00:00-23:00 UTC (24 hours) | monthly archive LTCUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/LTCUSDT/1h/LTCUSDT-1h-2022-02-27.zip | 5234c4c09c5347651c50813a2070111e920b261807ad6d3554946b9ae4a7f367 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| LTCUSDT | 2022-02-28 00:00-23:00 UTC (24 hours) | monthly archive LTCUSDT-1h-2022-02.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/LTCUSDT/1h/LTCUSDT-1h-2022-02-28.zip | 2516ad0fd306c2754ca3b341508b9a5df3beb607d8d25114359ba80a4d3beca1 | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| LTCUSDT | 2022-04-01 00:00-23:00 UTC (24 hours) | monthly archive LTCUSDT-1h-2022-04.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/LTCUSDT/1h/LTCUSDT-1h-2022-04-01.zip | b1dd41d59f59a6ebe3d625de71db3bb2f88717f526ba5d2e0fb04ba7aa8da9fa | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |
| LTCUSDT | 2022-04-02 00:00-23:00 UTC (24 hours) | monthly archive LTCUSDT-1h-2022-04.zip verified but lacks the day | https://data.binance.vision/data/futures/um/daily/klines/LTCUSDT/1h/LTCUSDT-1h-2022-04-02.zip | 3c9631ea621728f3ae38885dec7ac8276956fd8a4f45e8b71de0c6016e84559b | official daily archive merged for absent hours only; identical-overlap check; no forward fill; no strategy change |

## Integrity before and after (all fourteen histories)

| Asset | Missing hours before | Incomplete 4h bars before | Missing hours after | Incomplete 4h bars after | Supplemented hours | Non-4h funding events | Funding mark fallbacks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SOLUSDT | 120 | 30 | 0 | 0 | 120 | 49 | 6 |
| XRPUSDT | 120 | 30 | 0 | 0 | 120 | 0 | 6 |
| BNBUSDT | 0 | 0 | 0 | 0 | 0 | 0 | 9 |
| DOTUSDT | 0 | 0 | 0 | 0 | 0 | 0 | 9 |
| DOGEUSDT | 0 | 0 | 0 | 0 | 0 | 0 | 6 |
| ADAUSDT | 0 | 0 | 0 | 0 | 0 | 0 | 6 |
| AVAXUSDT | 0 | 0 | 0 | 0 | 0 | 0 | 9 |
| AXSUSDT | 0 | 0 | 0 | 0 | 0 | 0 | 9 |
| MATICUSDT | 0 | 1 | 0 | 1 | 0 | 0 | 9 |
| FTMUSDT | 120 | 30 | 0 | 0 | 120 | 0 | 6 |
| LTCUSDT | 120 | 30 | 0 | 0 | 120 | 0 | 6 |
| LINKUSDT | 0 | 0 | 0 | 0 | 0 | 0 | 9 |
| BTCUSDT | 0 | 0 | 0 | 0 | 0 | 0 | 9 |
| ETHUSDT | 0 | 0 | 0 | 0 | 0 | 0 | 6 |

Mark-price monthly archives were complete on the supplemented days, so no mark supplement was needed. Remaining incomplete 4h bars (MATICUSDT: the mandated 08:00 UTC exit bar) are contract administration, not gaps. Non-4h funding events exist only for SOLUSDT and are settled at their hourly boundary by the frozen event accounting. Funding mark fallbacks are hourly settlements whose mark open is absent from the mark archive and use the labelled trade-open proxy; adverse funding stress covers them.

## Why five missing days matter: frozen-signal diagnostic (gapped versus supplemented inputs)

The frozen trend ensemble uses full-window simple moving averages (100/150/200/250 bars). With the gap bars absent, every window that contained a missing 4h bar evaluated to NaN, so after each gap all seven votes were unavailable for roughly 130 bars and individual votes for up to 250 bars. The engine's fillna(0) on an all-NaN ensemble is a forced flat position, which is not the frozen rule's intended behaviour. The breakout component (20-bar channel, ATR14, 250-bar rank with 120 minimum) was unaffected. Measured on 2022-2024 signals (scratch diagnostic, same frozen `signals()`):

| Asset | Trend bars with NaN ensemble (gapped) | Trend bars whose target differs | Differing span | Breakout bars differing |
| --- | ---: | ---: | --- | ---: |
| SOLUSDT | 238 | 348 | 2022-02-26 to 2022-05-02 | 0 |
| XRPUSDT | 238 | 283 | 2022-02-26 to 2024-08-29 (last is an isolated rounding-level vote flip) | 0 |
| FTMUSDT | 238 | 276 | 2022-02-26 to 2022-04-20 | 0 |
| LTCUSDT | 238 | 331 | 2022-02-26 to 2022-07-27 | 0 |

So the first pass under-represented the trend sleeve on these four assets for two to five months of 2022 and then followed a different path-dependent sizing history. Supplementation restores the rule as frozen; it does not change the rule.

## First pass versus supplemented rerun (stress case, equal E040)

First pass E044_20260909T092223; rerun E044_20260909T135755. All metrics for the ten assets whose inputs did not change are identical to the last digit (regression check). Rows changed: 112 across ['FTMUSDT', 'LTCUSDT', 'SOLUSDT', 'XRPUSDT']. Sign changes in total net return: none.

| Asset | Supplemented | Sharpe first | Sharpe rerun | Net return first | Net return rerun | Max DD first | Max DD rerun | Trades first | Trades rerun |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SOLUSDT | True | 1.1625 | 1.0098 | 2.6174 | 1.9852 | -0.3175 | -0.3175 | 198 | 213 |
| XRPUSDT | True | 0.1254 | -0.0175 | -0.0456 | -0.1809 | -0.6169 | -0.6363 | 249 | 264 |
| BNBUSDT | False | 0.0258 | 0.0258 | -0.0840 | -0.0840 | -0.3852 | -0.3852 | 274 | 274 |
| DOTUSDT | False | 0.5900 | 0.5900 | 0.5782 | 0.5782 | -0.3043 | -0.3043 | 199 | 199 |
| DOGEUSDT | False | 1.0082 | 1.0082 | 1.8593 | 1.8593 | -0.3521 | -0.3521 | 174 | 174 |
| ADAUSDT | False | 1.0106 | 1.0106 | 1.4926 | 1.4926 | -0.3637 | -0.3637 | 215 | 215 |
| AVAXUSDT | False | 1.1517 | 1.1517 | 2.2667 | 2.2667 | -0.3495 | -0.3495 | 221 | 221 |
| AXSUSDT | False | 0.8145 | 0.8145 | 1.2108 | 1.2108 | -0.3343 | -0.3343 | 204 | 204 |
| MATICUSDT | False | 0.4821 | 0.4821 | 0.4042 | 0.4042 | -0.4366 | -0.4366 | 196 | 196 |
| FTMUSDT | True | 0.9631 | 1.0597 | 1.9870 | 2.5131 | -0.4440 | -0.4440 | 165 | 172 |
| LTCUSDT | True | -0.3066 | -0.4411 | -0.3653 | -0.4496 | -0.6550 | -0.6558 | 240 | 245 |
| LINKUSDT | False | -0.3216 | -0.3216 | -0.4768 | -0.4768 | -0.6711 | -0.6711 | 256 | 256 |
| BTCUSDT | False | 1.0600 | 1.0600 | 1.1430 | 1.1430 | -0.2067 | -0.2067 | 192 | 192 |
| ETHUSDT | False | 0.6916 | 0.6916 | 0.6420 | 0.6420 | -0.3628 | -0.3628 | 200 | 200 |
