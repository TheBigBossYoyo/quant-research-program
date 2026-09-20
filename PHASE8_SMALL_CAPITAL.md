# PHASE8_SMALL_CAPITAL - EUR 500 and EUR 1,000 simulations of the E058 primary architecture (MANUAL_USD, 20 slots, 126-session hold, EUR 1 minimum order, fractional shares assumed available)

| Cell | Capital | Final multiple 2009-17 | Average simultaneous holdings | Median trade USD | Trades | Skipped: below EUR 1 / slots full | Estimated annual cost EUR |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| C1_ANY | 500 | 3.15 | 18.94 | 56.3 | 342 | 0 / 5417 | 2.9 |
| C1_ANY | 1000 | 3.15 | 18.94 | 112.5 | 342 | 0 / 5417 | 5.9 |
| C2_CLUSTER | 500 | 2.76 | 18.94 | 55.1 | 340 | 0 / 1234 | 2.7 |
| C2_CLUSTER | 1000 | 2.76 | 18.94 | 110.2 | 340 | 0 / 1234 | 5.4 |
| C3_OPPORTUNISTIC | 500 | 2.05 | 17.57 | 53.6 | 316 | 0 / 295 | 2.4 |
| C3_OPPORTUNISTIC | 1000 | 2.05 | 17.57 | 107.1 | 316 | 0 / 295 | 4.8 |
| C4_OFFICER | 500 | 3.12 | 18.86 | 56.9 | 341 | 0 / 1368 | 2.8 |
| C4_OFFICER | 1000 | 3.12 | 18.86 | 113.9 | 341 | 0 / 1368 | 5.7 |
| C5_DIRECTOR_ONLY | 500 | 4.07 | 18.92 | 58.9 | 341 | 0 / 3003 | 3.0 |
| C5_DIRECTOR_ONLY | 1000 | 4.07 | 18.92 | 117.7 | 341 | 0 / 3003 | 6.1 |

Mechanically the architecture is feasible at EUR 500: positions of about USD 29 and trades of USD 25-35 clear the EUR 1 minimum, fractional shares are required for every position, and annual costs are a few euros. Feasibility is not the reason for rejection; the label RESEARCH_WORTHY_BUT_CAPITAL_LIMITED does not apply because the statistical architecture itself fails the development gates.
