# Phase 4 Previous-Day High/Low Rejection Evidence — EXP-20260914-004

**Experiment:** `EXP-20260914-004`  
**Experiment result:** FAIL — baseline survivor did not pass robustness review  
**Conclusion:** REJECT  
**Phase:** Phase 4 remains ACTIVE  
**Final-test touched: NO**

## Evidence identity

- implementation / benchmark commit: `7db3a747236942fa393521e5866e3245d1a22a99`
- merged-main tests: run `34883815429` — SUCCESS; 423 tests PASS, workflow YAML PASS, compile PASS
- unchanged Phase 3 acceptance: run `34883815462` — SUCCESS
- previous-day rejection benchmark: run `34883815436` — SUCCESS
- completed matrix: 3 pairs × 3 signal timeframes × development/validation = **18/18** successful cells
- frozen grid per cell: 3 penetration buffers × 3 adverse-slippage levels = 9 rows
- independently inspected benchmark rows: **162/162**
- independent validation errors: **zero**
- protocol: `fmp-phase4-previous-day-rejection-grid-v1`
- strategy version: `fmp-previous-day-rejection-v1`

Accepted Phase 2 processed-manifest identities:

- EURUSD: `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`
- GBPUSD: `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`
- USDJPY: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`

## Frozen research protocol

DEC-018 remains authoritative for the chronological split, timing bridge, source-free boundary, final-test lock, cost model, and unchanged Phase 3 risk rules. DEC-022 freezes this family:

- pairs: EURUSD, GBPUSD, USDJPY
- signal timeframes: 5m, 15m, 1h
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive
- previous completed trading-day reference: `[17:00 America/New_York, 17:00 America/New_York)`, with Monday-Friday session ends
- previous-day high/low: midpoint-quote extrema at the tested signal timeframe; target midpoint is `(high + low) / 2`
- eligible signal labels: 08:00 through 14:00 Europe/London; exact mandatory flat at 16:00 Europe/London
- penetration buffers: exactly 0, 2, 5 pips
- first directional rejection only; dual-level rejection fails closed as `AMBIGUOUS_DUAL_REJECTION`
- LONG stop at signal midpoint low; SHORT stop at signal midpoint high; target at previous-day midpoint
- adverse slippage per fill: 0.2, 0.5, 1.0 pips; historical BID/ASK spread; zero commission; zero financing
- accepted Phase 3 risk/execution semantics unchanged
- no post-result parameter expansion under this experiment ID

## Artifact registry

| Pair | Timeframe | Split | Artifact ID | GitHub ZIP SHA-256 |
| --- | --- | --- | ---: | --- |
| EURUSD | 5m | development | `10363981924` | `f7cc796f4a501b317547a1eb47bd2b4a1acf53f82dd028e9d5b0a68f976a1543` |
| EURUSD | 5m | validation | `10364650936` | `c985d9b57d0afa3cfac8d5a851b522a0861fb61a530de69acf103408711e3efe` |
| EURUSD | 15m | development | `10363489661` | `a16bb6a987cd0ddfa938b814dd3f29ad0380c74d2e406d9601f0aed0713dfcee` |
| EURUSD | 15m | validation | `10363816798` | `ac92add9e0c772137802149511c104e52a4b4fc78c67458df792f72448b3debc` |
| EURUSD | 1h | development | `10364231852` | `114ca938f739f928d152b20408a027068480683c86c084286975b9a678a5397a` |
| EURUSD | 1h | validation | `10364610838` | `4728b87c56022e3a785cff94044f899de9b5dc95beb5808c75ae19946cdf6b8a` |
| GBPUSD | 5m | development | `10363868667` | `282f4ec3065ff9f4ecec96057e4103504cda9e21264c49f809850eddee6d2ab6` |
| GBPUSD | 5m | validation | `10364456535` | `5c07f4294a4d45b73bf8b0ec831573af470609ddf29c90428237ec7243baa4cb` |
| GBPUSD | 15m | development | `10364076644` | `09c22ec3bc383f9e2a393071e96e9d03b4e3ca4ced99dffa18e62af1a3c77194` |
| GBPUSD | 15m | validation | `10363309149` | `3876da4356b2178af4113b4d3e0d99ef6fd6ed7ea316d0e1be680e1e67d24aa1` |
| GBPUSD | 1h | development | `10363593543` | `1279eae597223be77df748f4fb050a4ec9d289b8cf1c78625214c0d0cd89bdad` |
| GBPUSD | 1h | validation | `10363691923` | `ff3bae0d2f79880f56712c8998e53152d071ea7f995bea14fc0a6a0eeca2df8f` |
| USDJPY | 5m | development | `10363652325` | `6a07948640003276c9b29fb27222af57ce0f90731f6b84728a88b04c3ef3c51d` |
| USDJPY | 5m | validation | `10364451587` | `4c37ccb9a19d36a0925c4c7e16d4e8460209d885526ec738cb860aeeb5b4e192` |
| USDJPY | 15m | development | `10364391510` | `0e4c32a7b03e8e82f6e86018c93c4d29cb8e0e6af616f22d33f539366ab21963` |
| USDJPY | 15m | validation | `10364436419` | `af65135acfdcc98f37bb7527002366ca51091656222b9834b5b249b16ea27678` |
| USDJPY | 1h | development | `10363593479` | `1bb963c469732b56b5c1b90190631dc8d0a723719a3069a9922d5583676e3050` |
| USDJPY | 1h | validation | `10364386327` | `fa445a0829d3101a8f258e2bbf10e7b4763670d71b9f6ac7dd00fe21029d83f9` |

Each downloaded ZIP contained exactly `benchmark.json` and `manifest.json`.

## Independent verification

A fresh whole-set verifier checked all 18 downloaded artifacts and all 162 rows. It required:

- exact GitHub ZIP SHA-256 for every artifact
- exactly two ZIP members: `benchmark.json` and `manifest.json`
- manifest protocol `fmp-phase4-benchmark-artifacts-v1`
- internal benchmark SHA-256 and byte size matching the manifest
- exact code commit `7db3a747236942fa393521e5866e3245d1a22a99`
- exact symbol/timeframe/development-or-validation identity from the artifact name
- exact accepted Phase 2 processed-manifest identity
- exact 3-buffer × 3-cost row set in every cell
- exact slippage set 0.2 / 0.5 / 1.0 for each frozen buffer
- identical candidate SHA/count/reason counts across all three cost scenarios for every strategy configuration
- candidate accounting: trade count plus rejection count equals candidate count
- requested risk 0.25%, zero commission, and zero financing in run identity
- no `final` split anywhere in the evidence set

Result: **18 artifacts / 162 configuration rows / zero independent errors**.

## Frozen 0.2-pip promotion screen

At the 0.2-pip baseline, a frozen pair/timeframe/buffer point could survive only if the same buffer had all three of the following on both development and validation:

- net return > 0
- expectancy/trade > 0
- profit factor > 1

Result: **1 of 27** pair/timeframe/buffer points survives the first gate:

**USDJPY 5m / 5-pip penetration buffer**

| Split | Net return | Expectancy/trade | Profit factor | Trades | Max drawdown |
| --- | ---: | ---: | ---: | ---: | ---: |
| Development | +4.0039% | +$138.0644 | 1.9002 | 29 | 2.0245% |
| Validation | +0.0657% | +$2.3461 | 1.0133 | 28 | 1.7179% |

The validation edge is therefore barely above the frozen gate rather than a broad margin.

Several superficially attractive split-only results reverse across chronology and do not survive. Examples include EURUSD 1h / 5 pips, GBPUSD 1h / 5 pips, GBPUSD 15m / 5 pips, and USDJPY 15m / 5 pips. No result from one split is permitted to rescue failure on the other.

## Predeclared robustness review of the sole survivor

Because USDJPY 5m / 5 pips passes the first gate, the predeclared downstream review applies without any parameter expansion.

### 0.5-pip robustness

| Split | 0.2-pip return | 0.5-pip return | 0.5-pip expectancy | 0.5-pip PF |
| --- | ---: | ---: | ---: | ---: |
| Development | +4.0039% | +3.6067% | +$124.3681 | 1.7663 |
| Validation | +0.0657% | **-0.2343%** | **-$8.3685** | **0.9547** |

The same point fails the 0.5-pip robustness check on validation. At diagnostic 1.0-pip slippage, development remains +2.9479% / PF 1.5737 while validation deteriorates to -0.7324% / PF 0.8683.

### Neighboring-buffer stability

At baseline 0.2-pip slippage, USDJPY 5m neighboring buffers are not stable:

| Buffer | Development return | Development PF | Validation return | Validation PF |
| ---: | ---: | ---: | ---: | ---: |
| 0 pips | -44.3238% | 0.5926 | -37.1117% | 0.3778 |
| 2 pips | -3.6059% | 0.8874 | -20.6860% | 0.1730 |
| 5 pips | +4.0039% | 1.9002 | +0.0657% | 1.0133 |

The surviving point is isolated rather than supported by adjacent buffer behavior.

### Subperiod concentration and sample size

Development has only 29 trades across six years. Calendar PnL is negative in 2015 and 2018; the largest contribution is concentrated in 2020, which contributes about +3.8084% of starting equity while the full development result is +4.0039%.

Validation has only 28 trades across three years. Calendar PnL is negative in 2021 (-0.2590%) and 2022 (-0.4438%) and positive only in 2023 (+0.7686%). The thin +0.0657% aggregate validation result therefore depends on the final validation year overcoming losses in the first two years.

### Top-winner dependence

Using the stored reward/risk outcomes at 0.2-pip slippage:

- development: the largest winner contributes about **36.97%** of total positive R; the top three contribute about **63.16%**
- validation: the largest winner contributes about **35.81%** of total positive R; the top three contribute about **85.38%**

The validation edge is highly dependent on a small number of winners.

### Robustness conclusion

The sole baseline survivor fails the predeclared robustness review on multiple independent dimensions:

- validation turns negative at 0.5-pip adverse slippage
- both neighboring buffers fail on development and validation
- trade counts are only 29 development / 28 validation
- validation is negative in 2021 and 2022 and positive only in 2023
- the top three winners contribute about 85% of validation positive R

No post-result widening or alternate buffer search is permitted under EXP-004.

## Safety boundary

The benchmark consumed only accepted Phase 2 processed artifacts through the source-free Phase 4 workflow. It did not:

- request Dukascopy or another upstream source
- write or mutate Phase 1 raw storage
- alter `docs/phase1-exact-gap-queue.json`
- use Phase 1 acquisition credentials
- use the final-test split
- change the frozen grid after results were observed

The final-test period remains structurally locked.

A legacy session-breakout benchmark workflow also matched the implementation merge because that older workflow watches broad strategy/research paths. That rerun is not part of EXP-004 evidence and does not alter or reselect the frozen USDJPY 15m session-breakout candidate.

## Conclusion

`EXP-20260914-004` is **FAIL / REJECT**. One point, USDJPY 5m / 5-pip penetration buffer, narrowly passes the first 0.2-pip development-and-validation gate, but it fails the predeclared robustness review and is not promoted. No previous-day high/low rejection candidate advances and no post-result parameter expansion is authorized under this experiment ID.

The previously promoted **USDJPY 15m session-breakout, 5-pip buffer, 1.5x target-range multiple** candidate remains frozen unchanged. Phase 4 remains ACTIVE. The next family in the baseline queue is the distinct **session high/low sweep/rejection** family. The final test, Phase 5, broker/live integration, and real-money trading remain locked.
