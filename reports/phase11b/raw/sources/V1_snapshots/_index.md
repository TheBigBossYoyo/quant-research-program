# V1 snapshot index
Retrieved (batch): 2026-09-26 21:53 UTC

- binance_fee_schedule: https://www.binance.com/en/fee/schedule -> HTTP 202 (0 bytes)
- binance_mica_blog: https://www.binance.com/en/blog/regulation/5369321191341949883 -> HTTP 202 (0 bytes)
- kraken_fee_schedule: https://www.kraken.com/features/fee-schedule -> HTTP 200 (1390521 bytes)
- kraken_deposit_options: https://support.kraken.com/articles/360000381846-cash-deposit-options-fees-minimums-and-processing-times- -> HTTP 200 (1288316 bytes)
- kraken_withdrawal_options: https://support.kraken.com/articles/360000423043-cash-withdrawal-options-fees-minimums-and-processing-times- -> HTTP 200 (1213855 bytes)
- coinbase_advanced_trade: https://www.coinbase.com/advanced-trade -> HTTP 200 (416215 bytes)
- coinbase_sepa_deposit: https://help.coinbase.com/en/exchange/funding/depositing-with-sepa-transfers -> HTTP 200 (82315 bytes)
- bitstamp_fee_schedule: https://www.bitstamp.net/fee-schedule/ -> HTTP 200 (212 bytes)
- bitvavo_fees: https://bitvavo.com/en/fees -> HTTP 403 (5743 bytes)
- bitvavo_min_transaction: https://support.bitvavo.com/hc/en-us/articles/4405175127825-What-is-the-minimum-transaction-amount -> HTTP 200 (103515 bytes)
- trading212_crypto_fees: https://helpcentre.trading212.com/hc/en-us/articles/30752021087005-What-fees-does-Trading-212-charge-for-crypto-trading -> HTTP 200 (27993 bytes)
- trading212_crypto_account: https://helpcentre.trading212.com/hc/en-us/articles/30717768082461-What-is-the-Trading-212-Crypto-account -> HTTP 200 (27600 bytes)
- trading212_instruments: https://helpcentre.trading212.com/hc/en-us/articles/11717160183197-What-trading-instruments-does-Trading-212-offer -> HTTP 200 (28277 bytes)
- trading212_fx_fee: https://helpcentre.trading212.com/hc/en-us/articles/360018909758-What-is-the-FX-fee-Invest-Stocks-ISA -> HTTP 200 (28864 bytes)
- trading212_crypto_etn_isa: https://helpcentre.trading212.com/hc/en-us/articles/31007919710365-Crypto-ETNs-in-ISA-accounts -> HTTP 200 (26597 bytes)
- trading212_crypto_etn_approval: https://helpcentre.trading212.com/hc/en-us/articles/30591328588573-How-to-obtain-approval-to-invest-in-Crypto-ETNs -> HTTP 200 (28686 bytes)
- trading212_markets_ltd_crypto_regs: https://helpcentre.trading212.com/hc/en-us/articles/30718913607709-Trading-212-Markets-Ltd-Crypto-Account-Regulations -> HTTP 200 (26930 bytes)
- trading212_interest_on_cash: https://helpcentre.trading212.com/hc/en-us/articles/15475153380637-What-is-interest-on-cash -> HTTP 200 (37037 bytes)
- ishares_ib1t_uk: https://www.ishares.com/uk/professionals/en/products/337088 -> HTTP 200 (1181517 bytes)
- wisdomtree_btcw: https://www.wisdomtree.com/investments/etfs/crypto/btcw -> HTTP 403 (5834 bytes)
- justetf_btcw: https://www.justetf.com/en/etf-profile.html?isin=GB00BJYDH287 -> HTTP 200 (474279 bytes)
- justetf_ethw: https://www.justetf.com/en/etf-profile.html?isin=GB00BJYDH394 -> HTTP 200 (474334 bytes)
- justetf_coinshares_btc: https://www.justetf.com/en/etf-profile.html?isin=GB00BLD4ZL17 -> HTTP 200 (474240 bytes)
- justetf_21shares_btc_core: https://www.justetf.com/en/etf-profile.html?isin=CH1199067674 -> HTTP 200 (473832 bytes)
- fca_press_release_cetn: https://www.fca.org.uk/news/press-releases/fca-opens-retail-access-crypto-etns -> HTTP 200 (176605 bytes)
- coindesk_binance_eu_halt: https://www.coindesk.com/policy/2026/06/26/binance-tells-eu-users-it-will-no-longer-provide-services-after-failing-to-secure-mica-license -> HTTP 200 (1706429 bytes)

## Quarantine note (added by the main audit, 2026-09-26)

The captures of the justETF, iShares IB1T, WisdomTree BTCW (live and archive) and Trading 212 instrument-list pages were
moved to `QUARANTINE_UNREAD_MAY_CONTAIN_PRICE_DATA/` because such pages can embed price, NAV or performance tables.
They were not read for that content and must not be. All snapshot files are git-ignored; hashes are in
`reports/phase11b/raw/RAW_MANIFEST_SHA256.txt`.
