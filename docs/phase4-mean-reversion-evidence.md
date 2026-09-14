# Phase 4 Mean-Reversion Evidence — EXP-20260914-003

**Experiment:** `EXP-20260914-003`  
**Experiment result:** FAIL — no serious candidate evidence found  
**Conclusion:** REJECT  
**Phase:** Phase 4 remains ACTIVE  
**Final-test touched: NO**

## Evidence identity

- implementation / benchmark commit: `87003a3982ca61eb6fd030c5291616d98dbb0c1a`
- merged-main tests: run `34875463710` — SUCCESS; workflow YAML and compile PASS
- unchanged Phase 3 acceptance: run `34875463714` — SUCCESS
- mean-reversion benchmark: run `34875463677` — SUCCESS
- completed matrix: 3 pairs × 3 signal timeframes × development/validation = **18/18** successful cells
- frozen grid per cell: 3 lookbacks × 2 thresholds × 3 adverse-slippage levels = 18 rows
- independently inspected benchmark rows: **324/324**
- independent validation errors: **zero**
- protocol: `fmp-phase4-mean-reversion-grid-v1`
- strategy version: `fmp-mean-reversion-v1`

Accepted Phase 2 processed-manifest identities:

- EURUSD: `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`
- GBPUSD: `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`
- USDJPY: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`

## Frozen research protocol

DEC-018 remains authoritative for the chronological split, timing bridge, source-free boundary, final-test lock, cost model, and unchanged Phase 3 risk rules. DEC-020 freezes this family:

- pairs: EURUSD, GBPUSD, USDJPY
- signal timeframes: 5m, 15m, 1h
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive
- rolling midpoint-close lookbacks: exactly 4h, 8h, 16h
- fresh-excursion thresholds: exactly 1.5σ and 2.0σ
- preceding-N population mean/std excludes the current observation; previous z uses its own preceding-N reference
- eligible signal labels: 08:00 through 14:00 Europe/London; exact mandatory flat at 16:00 Europe/London
- adverse slippage per fill: 0.2, 0.5, 1.0 pips; historical BID/ASK spread; zero commission; zero financing
- accepted Phase 3 risk/execution semantics unchanged
- no post-result parameter expansion under this experiment ID

## Artifact registry

| Pair | Timeframe | Split | Artifact ID | GitHub ZIP SHA-256 |
| --- | --- | --- | ---: | --- |
| EURUSD | 5m | development | `10362161915` | `da11fae0713e3589bb1d95ee734295159a6b64087bfe39fd899d2cebc77ceb83` |
| EURUSD | 5m | validation | `10360494358` | `1291578cb0207110dc59e43920a20fa42068a09cc8b1e26d77f6cbd77757a7a0` |
| EURUSD | 15m | development | `10361178774` | `7637c833fc78701e6b4e9ad77503ab9df84e8d08c63649fa7d9fd5116d9a62d7` |
| EURUSD | 15m | validation | `10360502757` | `364b8cae2b5de5a46e4a7e57285b838fac9448c475a28f82ee9360f1655e10f8` |
| EURUSD | 1h | development | `10360179383` | `871085d9b3b720a9398313e58996fe5cbd42f5eac8d0ed27413415088466c05e` |
| EURUSD | 1h | validation | `10361300622` | `8f5d06c0416fceac0828fa17f1e18598afcb387be2298f047a5a91797b9b037c` |
| GBPUSD | 5m | development | `10362905316` | `0db2fe65cadfd6e0ecd4eb9d2c31b98b0d3a23678ff554fbd882a60029355f1d` |
| GBPUSD | 5m | validation | `10360677584` | `51ed65e11869f03c266985348a777cb9b8f3174c366b432d9df5e3239cc588e1` |
| GBPUSD | 15m | development | `10360563940` | `546d00f9d9da51442d39afea1f8ead2738fc05bb3aad8a4e4cac31f58d57276c` |
| GBPUSD | 15m | validation | `10361351709` | `0850ac188ee7380a836e78baa7b64edb3fc77390295ba5a5a8df669fb26751a7` |
| GBPUSD | 1h | development | `10360763278` | `3a49fc1130fa49d896ff3f5f48053ab4c9cc276e8c1233a263822d4c792e979e` |
| GBPUSD | 1h | validation | `10360383165` | `b6a004c12ea1388559515894fafd2d89603033c2981624bdd39b6268497dbce3` |
| USDJPY | 5m | development | `10361878034` | `d3194484bc81be892972864a59b0fc56cfd51844f9321e1deb609f5b6c12fb48` |
| USDJPY | 5m | validation | `10361735252` | `6f87fc54e44f658a9bf8143b74c873b892fd04ac51743f877535e7e347e35292` |
| USDJPY | 15m | development | `10361715922` | `2631e7858a263dcd90ac6333652300c925f519679bad310b80ba9d040fb3ac3f` |
| USDJPY | 15m | validation | `10360978535` | `0fae7c12b72c89d50457d23928a06a10f1689632284bdfd9093f727046e80c84` |
| USDJPY | 1h | development | `10360843017` | `3e8a7c7310e72e8ad790b63a8bd5c2daba1c8aa67b1e0fcba284d879b4a8059b` |
| USDJPY | 1h | validation | `10361295269` | `93698a55f074f67c27ac961000a855f668bec953cd7f1d70f58b19eecfadda44` |

Each downloaded ZIP contained exactly `benchmark.json` and `manifest.json`.

## Independent verification

A fresh whole-set verifier checked all 18 downloaded artifacts and all 324 rows. It required:

- exact GitHub ZIP SHA-256 for every artifact
- exactly two ZIP members: `benchmark.json` and `manifest.json`
- manifest protocol `fmp-phase4-benchmark-artifacts-v1`
- internal benchmark SHA-256 and byte size matching the manifest
- exact code commit `87003a3982ca61eb6fd030c5291616d98dbb0c1a`
- exact symbol/timeframe/development-or-validation identity from the artifact name
- exact accepted Phase 2 processed-manifest identity
- exact 6-strategy × 3-cost row set in every cell
- exact slippage set 0.2 / 0.5 / 1.0 for each frozen lookback/threshold point
- identical candidate SHA/count/reason counts across all three cost scenarios for every strategy configuration
- requested risk 0.25%, zero commission, and zero financing in run identity
- no `final` split anywhere in the evidence set

Result: **18 artifacts / 324 configuration rows / zero independent errors**.

## Frozen promotion screen

At the 0.2-pip baseline, a frozen lookback/threshold point could survive only if the same configuration had all three of the following on both development and validation:

- net return > 0
- expectancy/trade > 0
- profit factor > 1

Result: **zero** of 54 pair/timeframe/configuration points survive.

The failure is stronger than merely lacking matched development↔validation winners:

- development: 0/54 rows have positive net return; 0/54 have positive expectancy; 0/54 have profit factor above 1
- validation: 0/54 rows have positive net return; 0/54 have positive expectancy; 0/54 have profit factor above 1
- development net-return range: -75.6688% to -7.3404%
- validation net-return range: -53.7975% to -3.8866%
- development expectancy range: -$49.4891 to -$6.3444 per trade
- validation expectancy range: -$70.6003 to -$6.7948 per trade
- development profit-factor range: 0.6150 to 0.9596
- validation profit-factor range: 0.5396 to 0.9582

Because no configuration passes the first predeclared 0.2-pip gate, there is no survivor eligible for the downstream 0.5-pip robustness assessment. The stored 0.5- and 1.0-pip rows remain evidence, but they are not used to rescue or retune a failed baseline after observing results.

## Safety boundary

The benchmark consumed only accepted Phase 2 processed artifacts through the source-free Phase 4 workflow. It did not:

- request Dukascopy or another upstream source
- write or mutate Phase 1 raw storage
- alter `docs/phase1-exact-gap-queue.json`
- use Phase 1 acquisition credentials
- use the final-test split
- change the frozen grid after results were observed

The final-test period remains structurally locked.

## Conclusion

`EXP-20260914-003` is **FAIL / REJECT**. The deterministic intraday mean-reversion family fails the first frozen promotion gate across every pair, timeframe, lookback, and threshold at baseline 0.2-pip adverse slippage. No mean-reversion candidate is promoted, and no post-result parameter expansion is authorized under this experiment ID.

The previously promoted **USDJPY 15m session-breakout, 5-pip buffer, 1.5x target-range multiple** candidate remains frozen unchanged. Phase 4 remains ACTIVE. The next approved family in the baseline queue is **previous-day high/low rejection**. The final test, Phase 5, broker/live integration, and real-money trading remain locked.
