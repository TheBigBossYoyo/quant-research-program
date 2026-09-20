# PHASE8_QUALITY_CONDITIONING - E060 (reports/E060_20260912T191133; development only; frozen rule of PHASE8_PREREGISTRATION.md section 5)

Conditioning variables from SEC companyfacts (4,717 issuer files acquired, 4,443 with facts), used causally by the `filed` date of the latest 10-K/10-Q before each entry: operating profitability = trailing-year OperatingIncomeLoss / Assets, compared with the monthly cross-sectional median across Tier 2 eligible issuers with facts (96 monthly medians available); net issuance = change in dei EntityCommonStockSharesOutstanding over about one year of filings. Applied to the C1 ANY events of E058 (6,603): profitability available for 4,431, issuance for 3,976.

| Cell | Events | 2009-2012 excess vs EW (t) | 2013-2017 excess vs EW (t) | Years positive | 2013-17 net CAGR / EW / SPY | Alpha vs SPY t | Gates failed |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| Q1 PROFITABLE (above median) | 1,641 | +3.08% (0.64) | +3.72% (1.70) | 4/5 | 12.2 / 8.2 / 15.2 | -1.96 | G2, G4, G8 |
| Q2 NO_ISSUANCE (<= 5% share growth) | 2,975 | -0.87% (-0.25) | -1.50% (-0.55) | 2/5 | 6.3 / 8.2 / 15.2 | -2.36 | G1, G2, G3, G4, G7, G8, G9 |
| diagnostic: Q1 and Q2 | 1,020 | -5.57% (-0.70) | +4.11% (2.11) | 4/5 | 12.5 / 8.2 / 15.2 | -2.03 | G4, G8 |
| diagnostic: UNPROFITABLE (below median) | 2,790 | -2.61% (-0.87) | +5.57% (1.75) | 4/5 | 13.6 / 8.2 / 15.2 | -1.16 | G2, G4, G8, G9 |

## Does quality conditioning help?
No. Purchases at profitable issuers earn +3.7 percent a year over the equal-weight universe in 2013-2017, purchases at unprofitable issuers earn +5.6 percent, and the no-issuance filter removes the excess altogether; every conditioned cell has a negative alpha against SPY (t -1.2 to -2.4). There is no coherent quality interaction, and the conditioning does not create an architecture that beats the deployable alternative. Both preregistered E060 cells: REJECTED.
