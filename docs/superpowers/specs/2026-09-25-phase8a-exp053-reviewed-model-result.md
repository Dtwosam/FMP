# Phase 8A — EXP-053 Reviewed Historical Fit-Temporal Feature-Support Utility Result

**Date:** 2026-09-25
**Status:** REVIEWED AFTER THE SINGLE DEC-179-AUTHORIZED HISTORICAL RUN
**Decision:** DEC-183
**Experiment:** EXP-20260925-053

## 1. Purpose

DEC-183 records and closes review of the single historical EXP-053 fit-temporal feature-support utility model run authorized by DEC-179, dispatched through the DEC-180 one-way operator after DEC-181 read-only proof and DEC-182 executor source freeze, and predeclared for terminal review by DEC-178.

The workflow completed successfully and produced complete aggregate evidence.

The result does **not** produce a stable selected model challenger.

EXP-053 remains explicitly post-result-informed retrospective evidence and is not untouched out-of-sample evidence.

## 2. Executor handoff note

DEC-182 executor run `36127676468` successfully completed its exact DEC-180 `advance --execute` step and submitted the historical EXP-053 workflow.

Its later receipt-verification step failed because `operator-execution.json` was empty/non-JSON at verification time.

That post-dispatch bookkeeping failure did not invalidate or retract the already-submitted workflow. It does not authorize a second executor attempt, rerun, or replacement.

The authoritative run created by that dispatch is:

`36127730584`

and consumes the DEC-179 slot.

## 3. Exact workflow run identity

- workflow: `phase8a-exp053-fit-temporal-feature-support-utility-model-training`
- workflow path: `.github/workflows/phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run id: `36127730584`
- run attempt: `1`
- execution commit: `1a6e3670215665f2aed04d28c66c674408080953`
- conclusion: `success`

The first run consumes the one DEC-179 slot.

No rerun or replacement is authorized.

## 4. Job inventory

All 11 required jobs completed successfully:

| Job | Job id |
| --- | ---: |
| authorization-preflight | 108047617144 |
| EURUSD 5m model-cells | 108047757846 |
| EURUSD 15m model-cells | 108047757849 |
| EURUSD 1h model-cells | 108047758108 |
| GBPUSD 5m model-cells | 108047757843 |
| GBPUSD 15m model-cells | 108047757836 |
| GBPUSD 1h model-cells | 108047757973 |
| USDJPY 5m model-cells | 108047757814 |
| USDJPY 15m model-cells | 108047757840 |
| USDJPY 1h model-cells | 108047757838 |
| aggregate-model-evidence | 108053617166 |

## 5. Artifact inventory

The run produced exactly the expected ten non-expired artifacts.

Cell artifacts:

- EURUSD 5m: `10860771314`
- EURUSD 15m: `10860845882`
- EURUSD 1h: `10860527925`
- GBPUSD 5m: `10860539704`
- GBPUSD 15m: `10860179251`
- GBPUSD 1h: `10860644015`
- USDJPY 5m: `10861770918`
- USDJPY 15m: `10861126725`
- USDJPY 1h: `10860931916`

Aggregate artifact:

- artifact id: `10860962726`
- name: `exp053-fit-temporal-feature-support-utility-model-result-evidence-1a6e3670215665f2aed04d28c66c674408080953-from-feature-35867307338-outcome-35876715434`
- GitHub artifact digest: `sha256:2f52fdcf2b7e3634d7f58a33f55d31d6e20ca787e0f7dfb056233a846fb47330`

The downloaded ZIP independently hashes to the exact same SHA-256 value and contains exactly one `model-result-evidence.json`.

## 6. DEC-176 aggregate-evidence validation

The aggregate evidence is bound to execution commit:

`1a6e3670215665f2aed04d28c66c674408080953`

Its stored evidence fingerprint is:

`cb32abc0e4ecd3df8b639d77b6770e255aa87701eb19180dfdfb25c37dfe48e1`

Recomputing DEC-176 canonical JSON with the exact repository serializer reproduces that fingerprint exactly.

All 18 individual cell-result fingerprints also recompute exactly.

The complete aggregate proves:

- 18 verified cells;
- 108 HGB regressors;
- 108 pooled excluded-regime calibration references;
- 432 fit-half-year utility-support references;
- 216 fit-half-year feature-support references;
- exact feature-support / utility-support / pooled-calibrated / raw cutoff quadruples;
- frozen financial and temporal-stability gates;
- canonical cell/result chronology.

## 7. Aggregate result

DEC-176 summary evidence records:

| Metric | Result |
| --- | ---: |
| verified cells | 18 |
| verified regressors | 108 |
| pooled calibration references | 108 |
| fit-temporal utility-support references | 432 |
| fit-temporal feature-support references | 216 |
| selected cells | 0 |
| no stable challenger cells | 18 |
| aggregate-selection-pass variants | 10 |
| stable-selection-pass variants | 0 |
| unavailable budget variants | 26 |
| utility-eligible selection rows | 26,392 |
| validation-pass cells | 0 |
| retrospective-holdout-pass cells | 0 |

All 18 cells terminate without a stable selected challenger.

Validation and retrospective holdout remain locked for every cell.

## 8. Aggregate-pass inventory

Feature-support-first ranking expands aggregate financial passes from one EXP-052 variant to ten EXP-053 variants.

| Cell | Budget | Net pips | Mean pips | Half-year candidate counts (21H1/21H2/22H1/22H2) | Half-year net pips (21H1/21H2/22H1/22H2) |
| --- | ---: | ---: | ---: | --- | --- |
| GBPUSD 15m / 240m | 250 | 306.5 | 1.226 | 19 / 41 / 77 / 113 | 284.1 / 170.7 / -812.0 / 663.7 |
| GBPUSD 5m / 240m | 250 | 291.5 | 1.166 | 22 / 20 / 73 / 135 | 236.0 / 277.6 / -59.6 / -162.5 |
| GBPUSD 5m / 240m | 500 | 1,138.6 | 2.2772 | 57 / 33 / 131 / 279 | 1,043.7 / 323.8 / -875.1 / 646.2 |
| GBPUSD 5m / 240m | 1000 | 1,889.5 | 1.8895 | 83 / 62 / 274 / 581 | 1,220.7 / 180.3 / -1,263.6 / 1,752.1 |
| USDJPY 15m / 60m | 250 | 400.5 | 1.602 | 0 / 3 / 51 / 196 | 0.0 / 4.4 / 202.2 / 193.9 |
| USDJPY 15m / 240m | 250 | 916.2 | 3.6648 | 0 / 27 / 88 / 135 | 0.0 / 395.7 / -558.2 / 1,078.7 |
| USDJPY 15m / 240m | 500 | 1,991.7 | 3.9834 | 0 / 35 / 214 / 251 | 0.0 / 476.0 / -1,981.6 / 3,497.3 |
| USDJPY 15m / 240m | 1000 | 2,495.5 | 2.4955 | 0 / 45 / 382 / 573 | 0.0 / 824.3 / -2,607.7 / 4,278.9 |
| USDJPY 1h / 240m | 250 | 131.6 | 0.5264 | 4 / 17 / 59 / 170 | 15.5 / 258.1 / -421.2 / 279.2 |
| USDJPY 5m / 60m | 1000 | 485.2 | 0.4852 | 0 / 3 / 130 / 867 | 0.0 / 21.2 / -67.2 / 531.2 |

All ten pass the unchanged aggregate 0.5-pip financial gate.

## 9. Temporal-stability rejection

None of the ten aggregate passes clears all four unchanged half-year windows.

The failure pattern is no longer simply one late-period concentration:

- several GBPUSD variants now produce meaningful 2021 candidates and positive early-period net pips;
- USDJPY variants still show extremely thin or zero 2021 H1 coverage;
- many variants suffer negative 2022 H1 net performance;
- several GBPUSD variants also fail the 10% candidate-share floor in one or both 2021 half-years;
- no variant satisfies candidate-share and financial-sign requirements in every window simultaneously.

The feature-support layer therefore broadens aggregate financial viability and changes temporal candidate distribution, but it still does not produce a stable challenger under the frozen gate.

No variant is selected.

No validation or retrospective-holdout evaluation is unlocked.

## 10. Authorization closeout

DEC-183 records:

- accepted model candidate count: `0`;
- model-run dispatch authorization: `false`;
- replacement model-run authorization: `false`;
- authoritative model-result execution authorization: `false`;
- model-protocol result authorization: `false`;
- model-fit authorization: `false`;
- promotion authorization: `false`;
- shadow authorization: `false`;
- demo-order authorization: `false`;
- broker mutation authorization: `false`;
- live-order authorization: `false`;
- real-money authorization: `false`;
- trading authorization: `false`.

The terminal reviewed stage is:

`FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`

No second EXP-053 run is authorized.

## 11. Frozen implementation

Reviewed-result source:

`src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_result_decision.py`

Git blob:

`7001c2b7944bd7b75a0c70e6fb1a775ff50ba6b5`

Focused tests:

`tests/test_phase8a_exp053_model_result_decision.py`

Git blob:

`d90d51497ce6adf4ebef2fafe511588f716639eb`

## 12. Next gate

A later separate decision may freeze post-result diagnostics over immutable EXP-050, EXP-051, EXP-052, and EXP-053 evidence.

That diagnostic may compare candidate identity, aggregate financial quality, cutoff movement, feature-support distribution, utility-support distribution, and temporal coverage descriptively.

It must not retroactively alter DEC-174 through DEC-183 or authorize rerun, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money trading, or trading.
