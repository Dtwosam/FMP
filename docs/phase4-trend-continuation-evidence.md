# Phase 4 Trend-Continuation Evidence — EXP-20260914-002

**Experiment:** `EXP-20260914-002`  
**Experiment result:** FAIL — no serious candidate evidence found  
**Conclusion:** REJECT  
**Phase:** Phase 4 remains ACTIVE  
**Final-test touched: NO**

## Evidence identity

- implementation / benchmark commit: `d1c821cb8b4bfaaddbc334fee0f2f3b1dfe054a2`
- merged-main tests: run `34863705694` — SUCCESS, 378 tests PASS, workflow YAML PASS, compile PASS
- unchanged Phase 3 acceptance: run `34863705935` — SUCCESS
- trend-continuation benchmark: run `34863705913` — SUCCESS
- completed matrix: 3 pairs × 3 signal timeframes × development/validation = **18/18** successful cells
- frozen grid per cell: 3 trend windows × 2 targets × 3 adverse-slippage levels = 18 rows
- independently inspected benchmark rows: **324/324**
- independent validation errors: **zero**
- protocol: `fmp-phase4-trend-continuation-grid-v1`
- strategy version: `fmp-trend-continuation-v1`

Accepted Phase 2 processed-manifest identities:

- EURUSD: `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`
- GBPUSD: `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`
- USDJPY: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`

## Frozen research protocol

DEC-018 remains authoritative for the shared chronological split, timing bridge, cost model, final-test lock, and unchanged Phase 3 risk rules. DEC-019 freezes this family:

- pairs: EURUSD, GBPUSD, USDJPY
- signal timeframes: 5m, 15m, 1h
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive
- trend windows: `2h/8h`, `4h/16h`, `8h/32h`
- targets: `1.0R`, `1.5R`
- adverse slippage per fill: 0.2, 0.5, 1.0 pips
- historical BID/ASK spread; zero commission; zero financing
- unchanged accepted Phase 3 risk/execution rules
- no post-result parameter expansion under this experiment ID

## Artifact registry

| Pair | Timeframe | Split | Artifact ID | GitHub ZIP SHA-256 |
| --- | --- | --- | ---: | --- |
| EURUSD | 5m | development | `10357553183` | `d5717ba490a7527c2d1cd8df0df5ffa6b50ae1686bb442ffd6a3c6a1f08017b8` |
| EURUSD | 5m | validation | `10356751472` | `78ecbc5ff9693fcc64146f76514cdb7d730af37bc5163ffa60ed5926630c56a8` |
| EURUSD | 15m | development | `10356626048` | `4c6f6dd8bda812e4b281f2500b1d517482cf9f1b61827ef57963367463243784` |
| EURUSD | 15m | validation | `10355533498` | `7ab7a3e6694cb29d5bcfb7b34ab46781eda61873f47e5026f4d2d82e5d9500b8` |
| EURUSD | 1h | development | `10357065032` | `acc528d3bbee063f8083cc73f2df62f2ebe103def75362aadc4dfb68c174f40b` |
| EURUSD | 1h | validation | `10355354168` | `67c1494bae33fd1f26ace7cd461b0c4191bea3d09af1d533ab79c86d644c2622` |
| GBPUSD | 5m | development | `10356488292` | `fa9cb3f41485018efda2d1cda304e1ee8b7922bb3143fc350f34e3bc92178cdd` |
| GBPUSD | 5m | validation | `10355669918` | `41e4c8a0d576da686641f2b15f953c5298b6026b0703be6952677aeb5134c5c0` |
| GBPUSD | 15m | development | `10356324879` | `4806cf0a12beccdc2d71698fa9438fc6a050b9ddead9a39f72f4e3d8848581c7` |
| GBPUSD | 15m | validation | `10355468910` | `bf845fb56a57c8be52f0577349a05f6d593afcd982b9fbbd836c89f38de64520` |
| GBPUSD | 1h | development | `10356133866` | `9dbb50ebdaa85c97ab68c2c3df7015f6d5f8f1df6fbdab171205e77292fb99e1` |
| GBPUSD | 1h | validation | `10356227028` | `f4fd528441b5651f375fbd394d75ab258b4eb587cf8f528679cb218472e680e9` |
| USDJPY | 5m | development | `10357665333` | `20178f5cf190317a8580069a9e227551a77462dff4eed93902904f5892838300` |
| USDJPY | 5m | validation | `10356209826` | `d1fa15ba39eeeca1a9b717c2423158e51b332ff494c65d69c58a5fca90c5bbff` |
| USDJPY | 15m | development | `10357116417` | `bc6a955b0f8fe533c173a2e8e5c37a541aa05909480e4040bac5ca4f5b6cd4f9` |
| USDJPY | 15m | validation | `10355613731` | `7b95060fc46d1cb8f38eaba2fc4138ceb84ab2484996270956575491384802d5` |
| USDJPY | 1h | development | `10356540432` | `14f77282cfb7d9186c8dbf8d335bdbdaee7a9ae86afba0031b52b502dea96b33` |
| USDJPY | 1h | validation | `10356475348` | `035835ae2db441adf5f8a2c03418d8c5d57654bdfd37eed0096929d659539813` |

Each downloaded ZIP contained exactly `benchmark.json` and `manifest.json`. The GitHub ZIP SHA-256, internal manifest SHA-256/byte size, code commit, processed-data identity, split bounds, strategy identity, and full frozen grid all matched.

## Independent verification

A fresh whole-set verifier checked all 18 artifacts and all 324 rows. It required:

- exact GitHub ZIP SHA-256 for every artifact
- exactly two ZIP members: `benchmark.json` and `manifest.json`
- manifest protocol `fmp-phase4-benchmark-artifacts-v1`
- internal benchmark SHA-256 and byte size matching the manifest
- exact code commit `d1c821cb8b4bfaaddbc334fee0f2f3b1dfe054a2`
- exact accepted Phase 2 processed-manifest identity for the symbol
- exact development/validation boundaries and no final-test split
- exact 6-strategy × 3-cost row set in every cell
- identical candidate SHA/count/reason counts across the three cost scenarios for each frozen strategy configuration
- requested risk 0.25% and starting equity $100,000
- Phase 3 accounting identities for return, expectancy, profit factor, and daily realized PnL

Result: **18 artifacts / 324 configuration rows / zero independent errors**.

## Promotion screen

For a frozen strategy configuration to remain a serious candidate at a given cost level, both development and validation had to have:

- net return > 0
- expectancy/trade > 0
- profit factor > 1

Matched development↔validation survivors:

| Pair / timeframe | 0.2-pip | 0.5-pip | 1.0-pip |
| --- | ---: | ---: | ---: |
| EURUSD 5m | 0 | 0 | 0 |
| EURUSD 15m | 0 | 0 | 0 |
| EURUSD 1h | 0 | 0 | 0 |
| GBPUSD 5m | 0 | 0 | 0 |
| GBPUSD 15m | 0 | 0 | 0 |
| GBPUSD 1h | 0 | 0 | 0 |
| USDJPY 5m | 0 | 0 | 0 |
| USDJPY 15m | 0 | 0 | 0 |
| USDJPY 1h | 0 | 0 | 0 |

Therefore the full family has **zero** configuration overlap even at the 0.2-pip baseline. Cost stress cannot rescue a configuration that already fails temporal agreement.

## Failure characteristics

The family shows split-specific winners rather than development-to-validation persistence.

At 0.2-pip adverse slippage:

- EURUSD 5m development has one positive configuration; validation has zero. The best development point, `C / 1.5R`, returns +2.3354%, while the best validation point is still -15.1547%.
- EURUSD 15m development `C / 1.5R` reaches +5.7678% with PF 1.0514; validation has zero qualifying configurations.
- EURUSD 1h has four qualifying development configurations; validation has zero.
- GBPUSD 5m has zero qualifying configurations on either split.
- GBPUSD 15m development `C / 1.5R` reaches +4.2965%; validation has zero qualifying configurations.
- GBPUSD 1h development `C / 1.5R` is the strongest split-only result at +14.8309%, +$24.7595 expectancy/trade, PF 1.2294, 3.3801% max drawdown; its validation result is -2.7022%, -$8.5784 expectancy/trade, PF 0.9251.
- USDJPY 5m has zero qualifying configurations on either split.
- USDJPY 15m development has zero qualifying configurations, while validation has two; validation `A / 1.5R` reaches +9.2320%, demonstrating a chronological reversal rather than a stable edge.
- USDJPY 1h development has one marginal qualifier (`C / 1.5R`, +0.4104%, PF 1.0058), while validation qualifiers occur at different configurations, including `A / 1.5R` at +7.8361%.

These split reversals fail the frozen research standard's temporal robustness requirement. No trend-continuation configuration is promoted.

## Safety boundary

The benchmark consumed only accepted Phase 2 processed artifacts through the source-free Phase 4 workflow. It did not:

- request Dukascopy or any upstream market-data source
- write or mutate Phase 1 raw storage
- alter `docs/phase1-exact-gap-queue.json`
- use Phase 1 acquisition credentials
- use the final-test split
- change the frozen grid after results were observed

The final-test period remains structurally locked.

## Conclusion

`EXP-20260914-002` is **FAIL / REJECT**. The predeclared trend-continuation family produced no configuration with positive net return, positive expectancy, and profit factor above one on both development and validation at baseline 0.2-pip adverse slippage; there are also zero survivors at 0.5 or 1.0 pip.

The previously promoted **USDJPY 15m session-breakout, 5-pip buffer, 1.5x target** candidate remains frozen unchanged. Phase 4 remains ACTIVE. The next predeclared family is **mean reversion**. The final test, Phase 5, broker/live integration, and real-money trading remain locked.
