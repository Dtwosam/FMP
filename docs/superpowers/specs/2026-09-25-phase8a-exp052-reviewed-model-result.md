# Phase 8A — EXP-052 Reviewed Historical Fit-Temporal-Support Utility Result

**Date:** 2026-09-25
**Status:** REVIEWED AFTER THE SINGLE DEC-168-AUTHORIZED HISTORICAL RUN
**Decision:** DEC-172
**Experiment:** EXP-20260925-052

## 1. Purpose

DEC-172 records and closes review of the single historical EXP-052 fit-temporal-support utility model run authorized by DEC-168, dispatched only through the DEC-169 one-way operator, and predeclared for terminal review by DEC-167.

The workflow completed successfully and produced complete aggregate evidence.

The result does **not** produce a stable selected model challenger.

EXP-052 remains explicitly post-result-informed retrospective evidence and is not untouched out-of-sample evidence.

## 2. Exact workflow run identity

- workflow: `phase8a-exp052-fit-temporal-support-utility-model-training`
- workflow path: `.github/workflows/phase8a-exp052-fit-temporal-support-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run id: `36114617377`
- run attempt: `1`
- execution commit: `d477555cf116f07fa195de1b4a4c0d2f3b2838c5`
- conclusion: `success`

The first run consumes the one DEC-168 slot.

No rerun or replacement is authorized.

## 3. Job inventory

All 11 required jobs completed successfully:

| Job | Job id |
| --- | ---: |
| authorization-preflight | 108005664859 |
| EURUSD 5m model-cells | 108005808568 |
| EURUSD 15m model-cells | 108005808546 |
| EURUSD 1h model-cells | 108005808620 |
| GBPUSD 5m model-cells | 108005808521 |
| GBPUSD 15m model-cells | 108005808564 |
| GBPUSD 1h model-cells | 108005808596 |
| USDJPY 5m model-cells | 108005808748 |
| USDJPY 15m model-cells | 108005808614 |
| USDJPY 1h model-cells | 108005808594 |
| aggregate-model-evidence | 108011493112 |

## 4. Artifact inventory

The run produced exactly the expected ten non-expired artifacts.

Cell artifacts:

- EURUSD 5m: `10855256117`
- EURUSD 15m: `10854886924`
- EURUSD 1h: `10854054855`
- GBPUSD 5m: `10854917794`
- GBPUSD 15m: `10854811755`
- GBPUSD 1h: `10854713096`
- USDJPY 5m: `10855412103`
- USDJPY 15m: `10854778638`
- USDJPY 1h: `10855186784`

Aggregate artifact:

- artifact id: `10855585092`
- name: `exp052-fit-temporal-support-utility-model-result-evidence-d477555cf116f07fa195de1b4a4c0d2f3b2838c5-from-feature-35867307338-outcome-35876715434`
- GitHub artifact digest: `sha256:c7a593b2ded1f44aee447dd352d20101b54febb65be0c5f3e8a5791a1db4d263`

The downloaded ZIP independently hashes to the exact same SHA-256 value and contains exactly one `model-result-evidence.json`.

## 5. DEC-165 aggregate-evidence validation

The aggregate evidence is bound to execution commit:

`d477555cf116f07fa195de1b4a4c0d2f3b2838c5`

Its stored evidence fingerprint is:

`34e397e027a069db9344d56546b654f00bd34aff73240e5bca1d55e7b3dab7eb`

Recomputing the DEC-165 canonical JSON reproduces that fingerprint exactly.

All 18 individual cell-result fingerprints also recompute exactly.

The complete aggregate proves:

- 18 verified cells;
- 108 HGB regressors;
- 108 pooled excluded-regime calibration references;
- 432 fit-half-year temporal-support references;
- exact support/pooled/raw cutoff triples;
- frozen financial and temporal-stability gates;
- canonical cell/result chronology.

## 6. Aggregate result

DEC-165 summary evidence records:

| Metric | Result |
| --- | ---: |
| verified cells | 18 |
| verified regressors | 108 |
| pooled calibration references | 108 |
| fit-temporal-support references | 432 |
| selected cells | 0 |
| no stable challenger cells | 18 |
| aggregate-selection-pass variants | 1 |
| stable-selection-pass variants | 0 |
| unavailable budget variants | 26 |
| utility-eligible selection rows | 26,392 |
| validation-pass cells | 0 |
| retrospective-holdout-pass cells | 0 |

All 18 cells terminate without a stable selected challenger.

Validation and retrospective holdout remain locked for every cell.

## 7. Single aggregate pass

Exactly one variant passes the unchanged 0.5-pip aggregate selection gate:

- cell: `USDJPY 5m / 60m`
- budget anchor: `250`
- eligible selection rows: `1122`
- support cutoff: `0.9924051599114572`
- pooled calibrated cutoff: `0.9967413248462105`
- raw cutoff: `6.412340537481511`
- selected candidates: `250`
- LONG candidates: `248`
- SHORT candidates: `2`
- positive candidates: `130`
- negative candidates: `120`
- total net pips: `1247.500000000025`
- mean net pips: `4.9900000000001`
- gross positive pips: `5817.200000000012`
- absolute gross negative pips: `4569.699999999988`

All unchanged aggregate financial criteria pass.

## 8. Temporal stability rejection

The sole aggregate-pass variant fails the unchanged four-window temporal-stability gate.

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

- candidates: `0`
- candidate share: `0.0`
- total net pips: `0.0`
- mean net pips: null
- window gate: `REJECT`

### 2022 H2

- candidates: `250`
- candidate share: `1.0`
- total net pips: `1247.500000000025`
- mean net pips: `4.9900000000001`
- gross positive pips: `5817.200000000012`
- absolute gross negative pips: `4569.699999999988`
- window gate: `PASS`

The fit-half-year support-first ranking therefore does not broaden realized selection-period temporal coverage. It concentrates the complete 250-candidate aggregate-pass set in 2022 H2.

No variant is selected.

No validation or retrospective-holdout evaluation is unlocked.

## 9. Authorization closeout

DEC-172 records:

- accepted model candidate count: `0`
- model-run dispatch authorization: `false`
- replacement model-run authorization: `false`
- authoritative model-result execution authorization: `false`
- model-protocol result authorization: `false`
- model-fit authorization: `false`
- promotion authorization: `false`
- shadow authorization: `false`
- demo-order authorization: `false`
- broker mutation authorization: `false`
- live-order authorization: `false`
- real-money authorization: `false`
- trading authorization: `false`

The terminal reviewed stage is:

`FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`

No second EXP-052 run is authorized.

## 10. Frozen implementation

Reviewed-result source:

`src/fmp/market_learning/model_successor_fit_temporal_support_utility_result_decision.py`

Git blob:

`c9983c33792a8b143989b928a9c2af0c4ecda1e5`

Focused tests:

`tests/test_phase8a_exp052_model_result_decision.py`

Git blob:

`b33dd4d825509785dc879913c81696b1d6294f3d`

## 11. Next gate

A later separate decision may freeze post-result diagnostics over immutable EXP-050, EXP-051, and EXP-052 evidence.

That diagnostic may compare candidate identity, realized aggregate quality, cutoff movement, and temporal-support distribution descriptively.

It must not retroactively alter DEC-163 through DEC-172 or authorize rerun, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money trading, or trading.
