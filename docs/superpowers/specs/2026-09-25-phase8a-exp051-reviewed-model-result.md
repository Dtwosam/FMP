# Phase 8A — EXP-051 Reviewed Historical Temporal-Calibrated Utility Result

**Date:** 2026-09-25
**Status:** REVIEWED AFTER THE SINGLE DEC-155-AUTHORIZED HISTORICAL RUN
**Decision:** DEC-161
**Experiment:** EXP-20260924-051

## 1. Purpose

DEC-161 records and closes review of the single historical EXP-051 temporal-calibrated utility model run authorized by DEC-155, dispatched only through the DEC-156 one-way operator, and predeclared for terminal review by DEC-154.

The workflow completed successfully and produced complete aggregate evidence.

The result does **not** produce a stable selected model challenger.

EXP-051 remains explicitly post-result-informed retrospective evidence and is not untouched out-of-sample evidence.

## 2. Exact workflow run identity

- workflow: `phase8a-exp051-temporal-calibrated-utility-model-training`
- workflow path: `.github/workflows/phase8a-exp051-temporal-calibrated-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run id: `36066217609`
- run attempt: `1`
- execution commit: `3443b95ae3c524c74df4b2daebe9c526eb01ec9c`
- conclusion: `success`

The first run consumes the one DEC-155 slot.

No rerun or replacement is authorized.

## 3. Job inventory

All 11 required jobs completed successfully:

| Job | Job id |
| --- | ---: |
| authorization-preflight | 107856484610 |
| EURUSD 5m model-cells | 107856870897 |
| EURUSD 15m model-cells | 107856870933 |
| EURUSD 1h model-cells | 107856870796 |
| GBPUSD 5m model-cells | 107856870953 |
| GBPUSD 15m model-cells | 107856870845 |
| GBPUSD 1h model-cells | 107856870850 |
| USDJPY 5m model-cells | 107856870854 |
| USDJPY 15m model-cells | 107856870959 |
| USDJPY 1h model-cells | 107856870807 |
| aggregate-model-evidence | 107864877962 |

The authorization preflight passed the exact merged-main requirement, first-run rejection guard, pinned runtime installation, frozen workflow/source inspection, and separate DEC-155 result-execution authorization.

## 4. Artifact inventory

The run produced exactly the expected ten non-expired artifacts:

| Dataset | Artifact id |
| --- | ---: |
| EURUSD 5m | 10836309300 |
| EURUSD 15m | 10836746257 |
| EURUSD 1h | 10836123340 |
| GBPUSD 5m | 10836377595 |
| GBPUSD 15m | 10836169635 |
| GBPUSD 1h | 10836857558 |
| USDJPY 5m | 10836624044 |
| USDJPY 15m | 10836513542 |
| USDJPY 1h | 10837259018 |

Aggregate artifact:

- artifact id: `10837836415`
- name: `exp051-temporal-calibrated-utility-model-result-evidence-3443b95ae3c524c74df4b2daebe9c526eb01ec9c-from-feature-35867307338-outcome-35876715434`
- GitHub artifact digest: `sha256:ffbd18124dfe94c6eb25ae92fa4fda9650a26bd152173b000549b9a6e9fcace0`

The downloaded ZIP independently hashes to the exact same SHA-256 value.

The archive contains exactly one `model-result-evidence.json`.

## 5. DEC-152 aggregate-evidence validation

The aggregate evidence is bound to:

- experiment: `EXP-20260924-051`
- code commit: `3443b95ae3c524c74df4b2daebe9c526eb01ec9c`
- protocol decision: `DEC-150`
- training-core decision: `DEC-151`
- artifact-runner decision: `DEC-152`
- evidence label: `RETROSPECTIVE_ALREADY_SEEN`
- prior-result-informed: `true`
- untouched OOS: `false`

It binds the exact frozen source identities:

- DEC-150 merge: `b80a1f688afe8f5056aa31c1a2ff5b4ebbc11833`
- DEC-150 protocol blob: `c39309c4115cae1ea058e56f30cae4af6407e36e`
- DEC-151 merge: `68028ef37b72e3f0695b475928434ede40ad7690`
- DEC-151 training-core blob: `959fbfd52f41c08de3c1a26769e0e7fd2545b92a`
- predecessor training-core blob: `ec97a9941af052d6e223e4bafab9a9989ec57ff0`
- predecessor artifact-helper blob: `6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13`
- accepted historical artifact-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

It also binds the already accepted immutable historical source identities:

- feature run: `35867307338`
- feature evidence artifact: `10753455784`
- feature evidence fingerprint: `1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815`
- outcome run: `35876715434`
- outcome evidence artifact: `10758027876`
- outcome evidence fingerprint: `b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117`
- readiness artifact: `10757578276`
- readiness fingerprint: `412573f505ec7912ff934cc6338cf4591b604e0beddb2cb6abb79447c777b105`

The stored evidence fingerprint is:

`7dd836ed1c76c8eefd09b2b75e1eef9e875f5c6261c6fbb2cac8e3209781aaea`

Recomputing canonical DEC-152 JSON with the exact repository serializer reproduces the exact fingerprint.

All 18 individual cell-result fingerprints also recompute exactly.

## 6. Aggregate result

DEC-152 validation records:

| Metric | Result |
| --- | ---: |
| verified cells | 18 |
| verified regressors | 108 |
| verified calibration references | 108 |
| selected cells | 0 |
| no stable temporal-calibrated utility challenger cells | 18 |
| aggregate-selection-pass variants | 1 |
| stable-selection-pass variants | 0 |
| unavailable budget variants | 26 |
| utility-eligible selection rows | 26,392 |
| validation-pass cells | 0 |
| retrospective-holdout-pass cells | 0 |

All 18 cell result chains terminate at:

`NO_TEMPORAL_CALIBRATED_UTILITY_STABLE_MODEL_CHALLENGER`

Validation and retrospective holdout therefore remain locked for every cell.

## 7. Single aggregate pass

Exactly one variant passes the frozen 0.5-pip aggregate selection gate:

- cell: `USDJPY 5m / 60m`
- budget anchor: `250`
- EXP-050-eligible selection rows: `1122`
- calibrated cutoff: `0.9971023442510035`
- raw cutoff: `1.852905399735933`
- selected candidates: `250`
- LONG candidates: `239`
- SHORT candidates: `11`
- total net pips: `1288.1000000000117`
- mean net pips: `5.152400000000047`
- gross positive pips: `5608.700000000004`
- absolute gross negative pips: `4320.599999999992`

All four unchanged aggregate financial criteria pass.

## 8. Temporal stability rejection

The aggregate-pass USDJPY 5m / 60m budget-250 variant fails the unchanged four-window temporal-stability gate:

### 2021 H1

- candidates: `0`
- candidate share: `0.0`
- total net pips: `0.0`
- mean net pips: null
- window gate: `REJECT`

### 2021 H2

- candidates: `0`
- candidate share: `0.0`
- total net pips: `0.0`
- mean net pips: null
- window gate: `REJECT`

### 2022 H1

- candidates: `3`
- candidate share: `0.012`
- total net pips: `-28.100000000000477`
- mean net pips: `-9.366666666666825`
- gross positive pips: `0.0`
- absolute gross negative pips: `28.100000000000477`
- window gate: `REJECT`

### 2022 H2

- candidates: `247`
- candidate share: `0.988`
- total net pips: `1316.2000000000123`
- mean net pips: `5.328744939271305`
- gross positive pips: `5608.700000000004`
- absolute gross negative pips: `4292.499999999993`
- window gate: `PASS`

The calibrated ranking therefore concentrates essentially the full selected candidate set in 2022 H2 and does not solve the frozen temporal-coverage problem.

No variant is selected.

No validation or retrospective-holdout evaluation is unlocked.

## 9. Authorization closeout

DEC-161 closes the consumed one-run authorization and records:

- accepted model candidate count: `0`
- model-run dispatch authorization: `false`
- replacement model-run authorization: `false`
- authoritative model-result execution authorization: `false`
- model-protocol result authorization: `false`
- model-fit authorization: `false`
- promotion authorization: `false`
- shadow authorization: `false`
- demo-order authorization: `false`
- broker-mutation authorization: `false`
- live-order authorization: `false`
- real-money authorization: `false`
- trading authorization: `false`

The reviewed terminal stage is:

`TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`

No second EXP-051 run is authorized.

## 10. Frozen implementation

Fail-closed result decision:

`src/fmp/market_learning/model_successor_temporal_calibrated_utility_result_decision.py`

Git blob:

`015ab8a20c5d8b19f9fc1ee736e08b0bddeae669`

Focused tests:

`tests/test_phase8a_exp051_model_result_decision.py`

Git blob:

`65f1e01298adc07b64e1d733bae0e2f3066fcf7f`

## 11. Next gate

A later separate decision may freeze post-result diagnostics over this immutable EXP-051 evidence.

That diagnostic may compare EXP-050 and EXP-051 only descriptively. It must not retroactively alter DEC-150 through DEC-161 or authorize rerun, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money trading, or trading.
