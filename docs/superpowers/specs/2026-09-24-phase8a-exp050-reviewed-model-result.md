# Phase 8A — EXP-050 Reviewed Historical Temporal-Jackknife Utility Result

**Date:** 2026-09-24
**Status:** REVIEWED AFTER THE SINGLE DEC-146-AUTHORIZED HISTORICAL RUN
**Decision:** DEC-148
**Experiment:** EXP-20260924-050

## 1. Purpose

DEC-148 records and closes review of the single historical EXP-050 temporal-jackknife utility model run authorized by DEC-146 and predeclared for terminal review by DEC-145.

The workflow completed successfully and produced complete aggregate evidence. The result does **not** produce a stable selected model challenger.

EXP-050 remains explicitly post-result-informed retrospective evidence and is not untouched out-of-sample evidence.

## 2. Exact workflow run identity

- workflow: `phase8a-exp050-temporal-jackknife-utility-model-training`
- workflow path: `.github/workflows/phase8a-exp050-temporal-jackknife-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run id: `36049824739`
- run attempt: `1`
- execution commit: `25d48828b981c4309f4a859d2a33a56094638f21`
- conclusion: `success`

The first run consumes the one DEC-146 slot. No rerun or replacement is authorized.

## 3. Job inventory

All 11 required jobs completed successfully:

| Job | Job id |
| --- | ---: |
| authorization-preflight | 107802306696 |
| EURUSD 5m model-cells | 107802469142 |
| USDJPY 5m model-cells | 107802469161 |
| USDJPY 15m model-cells | 107802469174 |
| GBPUSD 1h model-cells | 107802469212 |
| EURUSD 15m model-cells | 107802469234 |
| GBPUSD 15m model-cells | 107802469292 |
| USDJPY 1h model-cells | 107802469341 |
| EURUSD 1h model-cells | 107802469372 |
| GBPUSD 5m model-cells | 107802469402 |
| aggregate-model-evidence | 107807743681 |

The authorization preflight passed the exact merged-main requirement, first-run rejection guard, pinned runtime installation, frozen workflow/source inspection, and separate DEC-146 result-execution authorization.

## 4. Artifact inventory

The run produced exactly the expected ten non-expired artifacts:

- nine pair/timeframe cell-result artifacts bound to execution commit `25d48828b981c4309f4a859d2a33a56094638f21`
- one aggregate artifact:
  - artifact id: `10829959147`
  - name: `exp050-temporal-jackknife-utility-model-result-evidence-25d48828b981c4309f4a859d2a33a56094638f21-from-feature-35867307338-outcome-35876715434`
  - GitHub artifact digest: `sha256:4a2b223425c2e8df60e13ec0ad22c46da618957999a7a7d23908ff9fd3b20275`

The downloaded ZIP independently hashes to the same SHA-256 value.

The archive contains exactly one `model-result-evidence.json`.

## 5. DEC-143 aggregate-evidence validation

The aggregate evidence is bound to:

- experiment: `EXP-20260924-050`
- code commit: `25d48828b981c4309f4a859d2a33a56094638f21`
- protocol decision: `DEC-141`
- training-core decision: `DEC-142`
- artifact-runner decision: `DEC-143`
- evidence label: `RETROSPECTIVE_ALREADY_SEEN`
- prior-result-informed: `true`
- untouched OOS: `false`

The stored evidence fingerprint is:

`866b4a8f26553bad8c80a7b2e0e68aedb50bfa42b3c767ce91478c9dfd720023`

Recomputing the canonical DEC-143 evidence fingerprint produces the exact same value.

All 18 individual cell-result fingerprints also recompute exactly.

DEC-143 validation records:

| Metric | Result |
| --- | ---: |
| verified cells | 18 |
| verified regressors | 108 |
| selected cells | 0 |
| no stable temporal-jackknife utility challenger cells | 18 |
| aggregate-selection-pass variants | 3 |
| stable-selection-pass variants | 0 |
| unavailable budget variants | 26 |
| utility-eligible selection rows | 26,392 |
| validation-pass cells | 0 |
| retrospective-holdout-pass cells | 0 |

All 18 cell result chains terminate at `NO_TEMPORAL_JACKKNIFE_UTILITY_STABLE_MODEL_CHALLENGER`. Validation and retrospective holdout therefore remain `LOCKED_NO_SELECTION`.

## 6. Aggregate passes and stability result

Exactly three available variants pass the frozen 0.5-pip aggregate selection gate. All are the USDJPY 5m / 60m cell:

| Cell | Budget anchor | Selection candidates | Selection total net pips | Stability |
| --- | ---: | ---: | ---: | --- |
| USDJPY 5m / 60m | 250 | 250 | 612.9 | REJECT |
| USDJPY 5m / 60m | 500 | 501 | 247.4 | REJECT |
| USDJPY 5m / 60m | 1000 | 1000 | 504.3 | REJECT |

None passes the unchanged four-window temporal-stability gate.

For all three variants, 2021 H1 contains zero directional candidates. The 250 and 500 variants also contain zero candidates in 2021 H2; the 1000 variant contains one 2021 H2 candidate and fails both share and financial signs there. The 500 and 1000 variants produce positive 2022 H1 financial signs but still miss the frozen 10% share requirement. All three pass the 2022 H2 window.

Therefore no variant is selected and no validation or retrospective-holdout evaluation is unlocked.

This decision records the result only. Any detailed successor interpretation must be frozen separately before it can guide a new protocol.

## 7. Authorization closeout

DEC-148 closes the consumed one-run authorization and records:

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

`TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`

No second EXP-050 run is authorized.

## 8. Frozen implementation

The fail-closed result decision is:

`src/fmp/market_learning/model_successor_temporal_jackknife_utility_result_decision.py`

Focused result-decision tests are:

`tests/test_phase8a_exp050_model_result_decision.py`

A later separate decision may freeze post-result diagnostics over this immutable evidence. It must not retroactively alter DEC-141 through DEC-148 or authorize rerun, promotion, shadow/demo execution, broker mutation, live orders, real-money trading, or trading.
