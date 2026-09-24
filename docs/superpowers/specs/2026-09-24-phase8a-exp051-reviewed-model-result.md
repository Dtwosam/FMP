# Phase 8A — EXP-051 Reviewed Historical Temporal-Calibrated Utility Result

**Date:** 2026-09-24
**Status:** REVIEWED AFTER THE SINGLE DEC-155-AUTHORIZED HISTORICAL RUN
**Decision:** DEC-161
**Experiment:** EXP-20260924-051

## 1. Purpose

DEC-161 records and closes review of the single historical EXP-051 temporal-calibrated utility model run authorized by DEC-155, dispatched only through the DEC-156 one-way operator path, and predeclared for terminal review by DEC-154.

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

The first manual-main run consumes the one DEC-155 slot.

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

The authorization preflight passed the exact merged-main requirement, the DEC-155 first-run rejection guard, pinned EXP-051 runtime installation, frozen source inspection, and separate historical result-execution authorization.

## 4. Artifact inventory

The run produced exactly the expected ten non-expired artifacts:

- nine pair/timeframe cell-result artifacts bound to execution commit `3443b95ae3c524c74df4b2daebe9c526eb01ec9c`;
- one aggregate artifact:
  - artifact id: `10837836415`
  - name: `exp051-temporal-calibrated-utility-model-result-evidence-3443b95ae3c524c74df4b2daebe9c526eb01ec9c-from-feature-35867307338-outcome-35876715434`
  - GitHub artifact digest: `sha256:ffbd18124dfe94c6eb25ae92fa4fda9650a26bd152173b000549b9a6e9fcace0`

The downloaded ZIP independently hashes to the same SHA-256 value.

The archive contains exactly one `model-result-evidence.json`.

## 5. DEC-152 aggregate-evidence validation

The aggregate evidence is bound to:

- experiment: `EXP-20260924-051`;
- code commit: `3443b95ae3c524c74df4b2daebe9c526eb01ec9c`;
- protocol decision: `DEC-150`;
- training-core decision: `DEC-151`;
- artifact-runner decision: `DEC-152`;
- evidence label: `RETROSPECTIVE_ALREADY_SEEN`;
- prior-result-informed: `true`;
- untouched OOS: `false`.

The stored evidence fingerprint is:

`7dd836ed1c76c8eefd09b2b75e1eef9e875f5c6261c6fbb2cac8e3209781aaea`

Independent canonical SHA-256 recomputation produces the exact same fingerprint.

All 18 individual cell-result fingerprints also recompute exactly.

DEC-152 summary evidence records:

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

Validation and retrospective holdout therefore remain:

`LOCKED_NO_SELECTION`

## 6. Aggregate pass and stability result

Exactly one available variant passes the frozen 0.5-pip aggregate selection gate:

| Cell | Budget anchor | Selection candidates | Selection total net pips | Stability |
| --- | ---: | ---: | ---: | --- |
| USDJPY 5m / 60m | 250 | 250 | 1,288.1 | REJECT |

The frozen calibrated/raw cutoff pair is:

- robust calibrated utility: `0.9971023442510035`;
- robust raw utility: `1.852905399735933`.

The four unchanged stability windows record:

| Window | Candidates | Candidate share | Total net pips | Result |
| --- | ---: | ---: | ---: | --- |
| 2021 H1 | 0 | 0.000 | 0.0 | REJECT |
| 2021 H2 | 0 | 0.000 | 0.0 | REJECT |
| 2022 H1 | 3 | 0.012 | -28.1 | REJECT |
| 2022 H2 | 247 | 0.988 | 1,316.2 | PASS |

The full selection variant produces:

- 250 candidates;
- 239 LONG;
- 11 SHORT;
- total net pips: `1,288.1`;
- mean net pips: `5.1524`;
- gross positive pips: `5,608.7`;
- absolute gross negative pips: `4,320.6`.

The unchanged temporal-stability gate still rejects the variant because all four windows must pass.

No validation or retrospective-holdout evaluation is unlocked.

## 7. Relationship to EXP-050

This decision records results only.

Descriptively:

- utility-eligible selection rows remain `26,392`;
- unavailable budget variants remain `26`;
- aggregate-selection passes change from three under EXP-050 to one under EXP-051;
- stable-selection passes remain zero.

DEC-161 does not claim why those differences occurred and does not authorize a rescue interpretation.

Any detailed post-result diagnostic must be frozen separately before guiding another successor protocol.

## 8. Authorization closeout

DEC-161 closes the consumed one-run authorization and records:

- accepted model candidate count: `0`;
- model-run dispatch authorization: `false`;
- replacement model-run authorization: `false`;
- authoritative model-result execution authorization: `false`;
- model-protocol result authorization: `false`;
- model-fit authorization: `false`;
- promotion authorization: `false`;
- shadow authorization: `false`;
- demo-order authorization: `false`;
- broker-mutation authorization: `false`;
- live-order authorization: `false`;
- real-money authorization: `false`;
- trading authorization: `false`.

The reviewed terminal stage is:

`TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`

No second EXP-051 run is authorized.

## 9. Frozen implementation

Fail-closed result decision:

`src/fmp/market_learning/model_successor_temporal_calibrated_utility_result_decision.py`

Git blob:

`14bc6f2e9172aa325aeb556b7abeacf2c756c475`

Focused result-decision tests:

`tests/test_phase8a_exp051_model_result_decision.py`

Git blob:

`691ec9d8a0bda18812374467d5f31ad44a02619a`

## 10. Next gate

A later separate decision may freeze a post-result diagnostic over the immutable DEC-161 evidence.

That diagnostic must not retroactively alter DEC-150 through DEC-161, authorize an EXP-051 rerun or replacement, weaken the frozen stability gate, or open promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.
