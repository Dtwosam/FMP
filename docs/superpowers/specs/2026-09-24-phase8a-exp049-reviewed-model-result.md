# Phase 8A — EXP-049 Reviewed Historical Regime-Utility Result

**Date:** 2026-09-24
**Status:** REVIEWED AFTER THE SINGLE DEC-137-AUTHORIZED HISTORICAL RUN
**Decision:** DEC-139
**Experiment:** EXP-20260924-049

## 1. Purpose

DEC-139 records and closes review of the single historical EXP-049 regime-utility model run authorized by DEC-137 and predeclared for terminal review by DEC-136.

The workflow completed successfully and produced complete aggregate evidence. The result does **not** produce a stable selected model challenger.

EXP-049 remains explicitly post-result-informed retrospective evidence and is not untouched out-of-sample evidence.

## 2. Exact workflow run identity

- workflow: `phase8a-exp049-regime-utility-model-training`
- workflow path: `.github/workflows/phase8a-exp049-regime-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run id: `36029925264`
- run attempt: `1`
- execution commit: `eeb735bca7d38c3246f22a9606dfafe9c3df8279`
- conclusion: `success`

The first run consumes the one DEC-137 slot. No rerun or replacement is authorized.

## 3. Job inventory

All 11 required jobs completed successfully:

| Job | Job id |
| --- | ---: |
| authorization-preflight | 107735801364 |
| USDJPY 5m model-cells | 107735993159 |
| GBPUSD 1h model-cells | 107735993169 |
| USDJPY 15m model-cells | 107735993188 |
| USDJPY 1h model-cells | 107735993231 |
| EURUSD 1h model-cells | 107735993233 |
| EURUSD 15m model-cells | 107735993253 |
| GBPUSD 5m model-cells | 107735993265 |
| EURUSD 5m model-cells | 107735993320 |
| GBPUSD 15m model-cells | 107735993383 |
| aggregate-model-evidence | 107740090995 |

The authorization preflight passed the exact merged-main requirement, prior-run rejection guard, pinned runtime installation, frozen workflow/source inspection, and separate DEC-137 result-execution authorization.

## 4. Artifact inventory

The run produced exactly the expected ten non-expired artifacts:

- nine pair/timeframe cell-result artifacts bound to execution commit `eeb735bca7d38c3246f22a9606dfafe9c3df8279`
- one aggregate artifact:
  - artifact id: `10822530555`
  - name: `exp049-regime-utility-model-result-evidence-eeb735bca7d38c3246f22a9606dfafe9c3df8279-from-feature-35867307338-outcome-35876715434`
  - GitHub artifact digest: `sha256:2cafb18dc1130f4fe0bf229b7df1deda24bfb7b1295f9a6ad688c1f5c1fd407c`

The downloaded ZIP independently hashes to the same SHA-256 value.

The archive contains exactly one `model-result-evidence.json`.

## 5. DEC-134 aggregate-evidence validation

The aggregate evidence is bound to:

- experiment: `EXP-20260924-049`
- code commit: `eeb735bca7d38c3246f22a9606dfafe9c3df8279`
- protocol decision: `DEC-132`
- training-core decision: `DEC-133`
- artifact-runner decision: `DEC-134`
- evidence label: `RETROSPECTIVE_ALREADY_SEEN`
- prior-result-informed: `true`
- untouched OOS: `false`

The stored evidence fingerprint is:

`29ecbb5bf3ce00f35c825e977d9b3fff1777e165ce9bef311fefcb7bfbdb091e`

Recomputing the canonical DEC-134 evidence fingerprint produces the exact same value.

DEC-134 validation records:

| Metric | Result |
| --- | ---: |
| verified cells | 18 |
| verified regressors | 108 |
| selected cells | 0 |
| no stable regime-utility challenger cells | 18 |
| aggregate-selection-pass variants | 8 |
| stable-selection-pass variants | 0 |
| unavailable budget variants | 31 |
| utility-eligible selection rows | 14,158 |
| validation-pass cells | 0 |
| retrospective-holdout-pass cells | 0 |

All 18 cell result chains terminate at `NO_REGIME_UTILITY_STABLE_MODEL_CHALLENGER`. Validation and retrospective holdout therefore remain `LOCKED_NO_SELECTION`.

## 6. Aggregate passes and stability result

Eight available variants pass the frozen 0.5-pip aggregate selection gate:

| Cell | Budget anchor | Selection candidates | Stability |
| --- | ---: | ---: | --- |
| EURUSD 1h / 240m | 250 | 250 | REJECT |
| GBPUSD 5m / 240m | 1000 | 1001 | REJECT |
| USDJPY 15m / 240m | 250 | 250 | REJECT |
| USDJPY 15m / 240m | 500 | 500 | REJECT |
| USDJPY 15m / 240m | 1000 | 1000 | REJECT |
| USDJPY 5m / 240m | 250 | 252 | REJECT |
| USDJPY 5m / 240m | 500 | 500 | REJECT |
| USDJPY 5m / 240m | 1000 | 1020 | REJECT |

None passes the unchanged four-window temporal-stability gate. Therefore no variant is selected and no validation or retrospective-holdout evaluation is unlocked.

This decision records the result only. Any detailed explanation of *why* the eight variants failed their specific stability windows must be frozen separately before it can guide a successor protocol.

## 7. Authorization closeout

DEC-139 closes the consumed one-run authorization and records:

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

`REGIME_UTILITY_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`

No second EXP-049 run is authorized.

## 8. Frozen implementation

The fail-closed result decision is:

`src/fmp/market_learning/model_successor_regime_utility_result_decision.py`

Focused result-decision tests are:

`tests/test_phase8a_exp049_model_result_decision.py`

A later separate decision may freeze post-result diagnostics over this immutable evidence. It must not retroactively alter DEC-132 through DEC-139 or authorize rerun, promotion, shadow/demo execution, broker mutation, live orders, real-money trading, or trading.
