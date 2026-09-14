# Phase 4 Session-Breakout Evidence

**Review date:** 2026-09-14  
**Experiment:** `EXP-20260914-001 — Session breakout baseline`  
**Phase:** Phase 4 — Baseline Strategy Research  
**Experiment result:** PASS — serious-candidate evidence found  
**Phase 4 status:** ACTIVE  
**Final-test touched: NO**

## Scope and immutable identity

This record covers only the predeclared source-free development/validation session-breakout experiment. It does not evaluate the final-test period, close Phase 4, start Phase 5, grant broker/live access, or change the DEC-008 real-money lock.

- implementation / benchmark code commit: `cc01929b80cbd1d5619de8476caa8f3d3410262e`
- merged-main tests run: `34848136901` — SUCCESS, 348 tests PASS, workflow YAML PASS, compile PASS
- unchanged Phase 3 acceptance run: `34848137105` — SUCCESS
- Phase 4 benchmark workflow: `phase4-session-breakout`
- merged-main benchmark run: `34848137086`
- benchmark event / branch: `push` / `main`
- benchmark conclusion: SUCCESS
- matrix: 3 pairs × 3 signal timeframes × 2 chronological splits = 18 cells
- artifact coverage independently inspected: **18/18**
- benchmark configuration rows independently inspected: **486/486**
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive

Accepted Phase 2 processed-manifest SHA-256 identities embedded in every corresponding benchmark artifact:

- EURUSD: `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`
- GBPUSD: `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`
- USDJPY: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`

Every artifact reports schema `fmp-canonical-1m-v1` and exact code commit `cc01929b80cbd1d5619de8476caa8f3d3410262e`.

## Artifact registry

| Pair | Timeframe | Split | Artifact ID | GitHub / independently recomputed ZIP SHA-256 |
| --- | --- | --- | ---: | --- |
| EURUSD | 5m | development | `10351950549` | `16b90001dd234ffc80af1ae885ec92cf47e3e975161cae5687ed76ec105b0199` |
| EURUSD | 5m | validation | `10349770177` | `bd7bb4468682d8b6d4ca8af8ca79dd02d330ed7e148c0fa7e292625edb61a064` |
| EURUSD | 15m | development | `10349253757` | `0f4c21fcb04d896ff79c2eedf4f878fc8d6a36b905d07969c94e4ead692d731d` |
| EURUSD | 15m | validation | `10348554022` | `219ab1b606f7598ac8b59dd9f4dc2f8a30c8e25ccf5a0b5f97d607839a871705` |
| EURUSD | 1h | development | `10348971684` | `55c40c45e72dcbf25e078781c8c5280c112256986e4bde7e601bbab0408dadbd` |
| EURUSD | 1h | validation | `10348733033` | `f99aaa265c900e1ae3e0d9c3cbdae418c2403273acf61dbd663002d033b1bd98` |
| GBPUSD | 5m | development | `10351831154` | `0613efad82aacaeab4aedc177475c566480879c716fa80712fdd03e8b462c929` |
| GBPUSD | 5m | validation | `10349731065` | `d0b41f5d3bf78f302e1a4adcde758c24ea099d53b82d50d8c33871d8e9336745` |
| GBPUSD | 15m | development | `10350080240` | `70f15fd9f0d9696888bee387af6ce4ae660ef5254c440646447c66547e11d122` |
| GBPUSD | 15m | validation | `10348534117` | `48841ff757af7152095832f3ccf5b83e9d8afdbcd570620d3e6e53319c9572f1` |
| GBPUSD | 1h | development | `10349465532` | `ba141b5b3239b162d4f647d78caf152f7df1bd9ec9ecca3e088d096dd7be3fc3` |
| GBPUSD | 1h | validation | `10349265935` | `9a0b18144eb823ef61d59ef1d1108971cedfc976f4d897f66182a50e0a809457` |
| USDJPY | 5m | development | `10350268408` | `1d4705bd5208dd69fc6999a374675bb55d0da964e969a79c6753bef75ef8ea21` |
| USDJPY | 5m | validation | `10348972681` | `760dc7b7da584a1cb0b74dbe04554e757ed4c2a1a815b4ef6df1853f69b44e39` |
| USDJPY | 15m | development | `10349341980` | `2b8121406e8374d5c65a1a225b5e040a14d72c441f83a1b7e5e295a0906715cf` |
| USDJPY | 15m | validation | `10348339399` | `5f2c0eb432f7edc15b33ec4f7a90a4642e32a43525157b8fac0957a79a9b2c8f` |
| USDJPY | 1h | development | `10348453932` | `a75ff99ed11b854ec67b64d5c5f1b1b66da947c0b3180cd8614ede80f7e07080` |
| USDJPY | 1h | validation | `10349236719` | `0475d0924270b7aef7a740b058e2ec810d061bc45932cf6eca5c9b5210293991` |

Each ZIP contains exactly `benchmark.json` and `manifest.json`. Independent inspection recomputed every ZIP SHA-256, every manifest-listed benchmark byte size/SHA-256, and the benchmark identities with zero discrepancies.

## Independent protocol and accounting verification

Across all 486 configuration rows, independent inspection verified:

- exact ordered 9-point grid per pair/timeframe and exact 0.2/0.5/1.0-pip slippage scenarios;
- candidate bytes, candidate count, and candidate reason counts are identical across the three cost scenarios for each strategy configuration;
- candidate reason counts sum exactly to candidate count;
- `trade_count + rejection_count == candidate_count` for every row (`NO_TRADE` is represented within rejection evidence rather than added again);
- every row binds to the exact merged-main code commit, processed schema, requested risk 0.25%, $100,000 starting research equity, and matching slippage identity;
- development/validation split bounds are exact and no final-test split is present;
- required core metrics are finite where mathematically defined;
- no artifact, manifest, grid, accounting, or identity discrepancy was found.

## Full-grid outcome

At baseline 0.2-pip adverse slippage, 19 configurations have positive net return, positive expectancy, and profit factor above 1 on both development and validation. Seventeen are USDJPY configurations; the other two are GBPUSD 5m target-1.5 configurations. EURUSD has no configuration satisfying that development-and-validation condition.

At 0.5-pip adverse slippage, exactly 9 configurations remain positive on both development and validation, and **all 9 are USDJPY**. They are target-1.5 configurations across all three 5m buffers, all three 15m buffers, plus USDJPY 1h `(2 pips, 1.5x)`, `(5 pips, 1.0x)`, and `(5 pips, 1.5x)`.

At severe **1.0-pip** adverse slippage, no configuration remains positive on both development and validation. This is a material limitation and is part of the candidate decision.

GBPUSD's strongest overlapping 5m point is `2-pip / 1.5x`: +4.35% development and +1.97% validation at 0.2-pip slippage, but both splits become negative at 0.5-pip slippage. EURUSD 5m development is negative for all nine parameter points even though a few validation points are mildly positive. Neither pair supplies robustness comparable with the USDJPY region.

## Frozen serious candidate

The strongest evidence-supported candidate from this experiment is **USDJPY 15m, 5 pips buffer, 1.5x target-range multiple**. It is retained because of development/validation agreement, neighboring-parameter stability, cost-stress survival at 0.5 pips, and same-parameter support on adjacent signal timeframes—not because it is merely the single best in-sample return.

| Split / slippage | Trades | Net return | Expectancy/trade | Profit factor | Max drawdown | Win rate | Sharpe | Sortino |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Development / 0.2 pip | 620 | +5.8023% | +$9.3585 | 1.1477 | 2.9370% | 50.16% | 0.5188 | 0.5499 |
| Validation / 0.2 pip | 362 | +3.7076% | +$10.2421 | 1.1449 | 2.9860% | 52.21% | 0.5617 | 0.6417 |
| Development / 0.5 pip | 620 | +3.4625% | +$5.5847 | 1.0865 | 3.3522% | 49.68% | 0.3162 | 0.3313 |
| Validation / 0.5 pip | 362 | +2.5224% | +$6.9680 | 1.0971 | 3.0752% | 51.93% | 0.3873 | 0.4392 |
| Development / 1.0 pip | 620 | -0.3228% | -$0.5207 | 0.9922 | 4.5292% | 48.06% | -0.0219 | -0.0224 |
| Validation / 1.0 pip | 362 | +0.5769% | +$1.5938 | 1.0217 | 3.3899% | 50.83% | 0.0962 | 0.1069 |

### Neighboring-parameter and cross-timeframe stability

For USDJPY 15m with target 1.5x, all three buffers remain positive on both splits at 0.5-pip slippage: buffer 0 (+2.82% development / +0.29% validation), buffer 2 (+1.31% / +1.34%), and buffer 5 (+3.46% / +2.52%).

The same USDJPY `5-pip / 1.5x` configuration also remains positive on development and validation at 0.5-pip slippage on 5m (+2.08% / +2.93%) and 1h (+0.33% / +2.19%). All three signal timeframes lose development profitability at 1.0-pip slippage, so this is evidence of moderate—not extreme—cost robustness.

### Calendar-year concentration

For the frozen USDJPY 15m candidate at 0.2-pip slippage, development years are positive in 2016, 2018, 2019, and 2020 and negative in 2015 and 2017. Validation is negative in 2021, strongly positive in 2022, and positive in 2023. About 91.6% of validation gross positive PnL occurs in 2022. That concentration is a material weakness even though the candidate remains positive outside 2022 in 2023 and survives neighboring-parameter/cost checks.

The evidence therefore supports retaining the candidate for the Phase 4 baseline program, but it does not support treating the strategy as cost-insensitive or uniformly stable through time.

## Experiment conclusion

`EXP-20260914-001` is **PASS** with conclusion **PROMOTE** in the repository's research-registry sense: promote the frozen USDJPY 15m `5-pip / 1.5x` configuration as a serious Phase 4 candidate to retain while subsequent predeclared baseline families are researched.

This is explicitly **not** promotion to final-test evaluation, Phase 4 PASS, Phase 5, broker integration, live trading, or real-money execution. Candidate selection across the admitted baseline program is not materially complete, so the final-test period remains locked.

The next research family is **trend continuation**, following the approved family order. The session-breakout candidate must remain frozen while that family is designed and evaluated; no post-result expansion of `EXP-20260914-001` is authorized.

## Safety boundary

The merged-main benchmark read only the accepted Phase 2 processed artifacts via GitHub Actions artifact download using exact artifact IDs and ZIP digests. It did not request GitHub OIDC, call Supabase, acquire Dukascopy/source data, mutate `fmp-raw`, alter `docs/phase1-exact-gap-queue.json`, or load the final-test split.

Phase 4 remains ACTIVE. Phase 5 remains UNSTARTED. Real-money trading remains locked under DEC-008.
