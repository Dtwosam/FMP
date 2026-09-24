# Phase 8A — EXP-051 Predeclared Terminal-Result Review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-051 HISTORICAL MODEL RESULT OR RUN AUTHORIZATION
**Decision:** DEC-154
**Experiment:** EXP-20260924-051

## 1. Purpose

DEC-154 freezes the exact terminal-review contract for the future first EXP-051 historical model run before any result-producing authorization exists.

It does not authorize dispatch, model fitting, historical result execution, a replacement run, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.

## 2. Frozen workflow identity

Only a run with all of the following is reviewable:

- workflow name: `phase8a-exp051-temporal-calibrated-utility-model-training`
- workflow path: `.github/workflows/phase8a-exp051-temporal-calibrated-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run attempt: exactly `1`
- terminal status: `completed`
- conclusion: `success`, `failure`, `cancelled`, or `timed_out`

Any rerun attempt is rejected.

The review binds the merged DEC-153 source identity:

- DEC-153 merge: `b0fb55aca2d818e7306a15b200b1e10fcc151ad2`
- workflow blob: `4ab7480e31e91cbfe39eb5e289eccadde428d1a4`
- CLI blob: `c88b05a14bc961391ff59e29f742c1dac27272b6`
- execution-gate blob: `37a0b7af464c464beff0976addc1464f68e916cc`

## 3. Required job inventory

The terminal job payload must contain exactly 11 unique completed jobs:

- one `authorization-preflight`;
- nine `model-cells (...)` matrix jobs;
- one `aggregate-model-evidence`.

Unknown job names, duplicate job IDs, non-completed jobs, or a different count fail closed.

## 4. Expected cell artifacts

The only accepted pair/timeframe cell artifact identities are:

- EURUSD 5m
- EURUSD 15m
- EURUSD 1h
- GBPUSD 5m
- GBPUSD 15m
- GBPUSD 1h
- USDJPY 5m
- USDJPY 15m
- USDJPY 1h

For run head `<sha>`, the exact cell artifact namespace is:

`exp051-temporal-calibrated-utility-model-cell-results-<symbol>-<timeframe>-<sha>`

Artifacts must be non-expired and uniquely named.

## 5. Expected aggregate artifact

For run head `<sha>`, the only accepted aggregate artifact is:

`exp051-temporal-calibrated-utility-model-result-evidence-<sha>-from-feature-35867307338-outcome-35876715434`

No unrelated artifact may be present in the reviewed workflow artifact listing.

## 6. Successful-run review

A successful run is reviewable only when:

- authorization preflight succeeded;
- all nine matrix jobs succeeded;
- aggregate job succeeded;
- all nine cell artifacts exist;
- the aggregate artifact exists;
- aggregate evidence is supplied to the review function;
- DEC-152 aggregate-evidence validation succeeds using the run head SHA as the expected code commit.

A GitHub `success` conclusion by itself is insufficient.

DEC-152 independently requires the complete 18-cell result, 108 regressors, 108 calibration references, calibrated/raw cutoff evidence, chronology/status chains, and canonical fingerprints.

The successful terminal stage is:

`TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_REVIEW_REQUIRED`

That stage authorizes no replacement run, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading.

## 7. Non-success review

A first run ending in failure, cancellation, or timeout may preserve a subset of valid pair/timeframe cell artifacts.

It may not claim:

- an aggregate artifact;
- aggregate result evidence;
- a successful result.

The review records:

- preflight conclusion;
- successful matrix-job count;
- failed matrix-job count;
- cancelled matrix-job count;
- skipped matrix-job count;
- number of persisted cell artifacts.

The non-success terminal stage is:

`TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`

A non-success first attempt does not authorize a rerun or replacement.

## 8. Replacement and rerun policy

DEC-154 freezes:

- rerun attempt greater than 1: rejected;
- replacement model run authorized: false;
- promotion authorized: false;
- shadow authorized: false;
- demo order authorized: false;
- broker mutation authorized: false;
- live order authorized: false;
- real-money authorized: false;
- trading authorized: false.

Any future replacement decision would require a separate source-of-truth change after reviewing terminal evidence.

## 9. Source identity

Review source:

`src/fmp/market_learning/model_successor_temporal_calibrated_utility_result_review.py`

Git blob:

`bd46dfd1cb8674ab8088d858b378ca37c5d75687`

Focused tests:

`tests/test_phase8a_exp051_model_result_review.py`

Git blob:

`132ec628d41f6ef84797c683e8114f3b3d935a22`

## 10. Next gate

After DEC-154 is merged, a later separate authorization decision may:

1. independently verify that zero prior manual-main EXP-051 workflow runs exist;
2. bind the merged DEC-153 workflow/gate and DEC-154 review source;
3. add a first-run rejection guard;
4. authorize at most one outer historical result-producing attempt.

That authorization decision must not dispatch the workflow itself.

The first eventual attempt, regardless of success, failure, cancellation, or timeout, consumes the one-run slot unless an even later replacement decision explicitly changes the source of truth.
