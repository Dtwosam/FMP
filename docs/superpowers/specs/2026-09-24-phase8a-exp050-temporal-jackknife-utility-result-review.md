# Phase 8A — EXP-050 Predeclared Terminal-Result Review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-050 HISTORICAL MODEL RESULT OR RUN AUTHORIZATION
**Decision:** DEC-145
**Experiment:** EXP-20260924-050

## 1. Purpose

DEC-145 freezes the exact terminal-review contract for the future first EXP-050 historical model run before any result-producing authorization exists.

It does not authorize dispatch, model fitting, historical result execution, a replacement run, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.

## 2. Frozen workflow identity

Only a run with all of the following is reviewable:

- workflow name: `phase8a-exp050-temporal-jackknife-utility-model-training`
- workflow path: `.github/workflows/phase8a-exp050-temporal-jackknife-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run attempt: exactly `1`
- terminal status: `completed`
- conclusion: `success`, `failure`, `cancelled`, or `timed_out`

Any rerun attempt is rejected.

The review binds the merged DEC-144 source identity:

- DEC-144 merge: `9f2986c783823cf7d9647ed4b0a50c66470bea21`
- workflow blob: `ec8ed4ab3f0b8a18ffc735af92172e059ed29955`
- CLI blob: `70c5e9b8d22888b9727e234fd80ea3e3ba4e5e09`
- execution-gate blob: `4814f0db86bec943d7282ab13586559b1eb8caa7`

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

`exp050-temporal-jackknife-utility-model-cell-results-<symbol>-<timeframe>-<sha>`

Artifacts must be non-expired and uniquely named.

## 5. Expected aggregate artifact

For run head `<sha>`, the only accepted aggregate artifact is:

`exp050-temporal-jackknife-utility-model-result-evidence-<sha>-from-feature-35867307338-outcome-35876715434`

No unrelated artifact may be present in the reviewed workflow artifact listing.

## 6. Successful-run review

A successful run is reviewable only when:

- authorization preflight succeeded;
- all nine matrix jobs succeeded;
- aggregate job succeeded;
- all nine cell artifacts exist;
- the aggregate artifact exists;
- aggregate evidence is supplied to the review function;
- DEC-143 aggregate-evidence validation succeeds using the run head SHA as the expected code commit.

A GitHub `success` conclusion by itself is insufficient; the persisted evidence must independently pass the frozen DEC-143 contract.

The successful terminal stage is:

`TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_REVIEW_REQUIRED`

That stage still authorizes no promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading.

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

`TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`

A non-success first attempt does not authorize a rerun or replacement.

## 8. Replacement and rerun policy

DEC-145 freezes:

- rerun attempt greater than 1: rejected;
- replacement model run authorized: false;
- promotion authorized: false;
- shadow authorized: false;
- demo order authorized: false;
- broker mutation authorized: false;
- live order authorized: false;
- real-money authorized: false;
- trading authorized: false.

Any future replacement decision would require a separate source-of-truth change after reviewing the terminal failure evidence.

## 9. Source identity

Review source:

`src/fmp/market_learning/model_successor_temporal_jackknife_utility_result_review.py`

Git blob:

`e93f7f26e6f0cf8541c9dffd0d359acf0a7ec64e`

Focused tests:

`tests/test_phase8a_exp050_model_result_review.py`

Git blob:

`54dd7a4c973a685efcc7a4b732c2be46e64e7aff`

## 10. Next gate

After DEC-145 is merged, a later separate authorization decision may:

1. independently verify that zero prior manual-main EXP-050 workflow runs exist;
2. bind the merged DEC-144 workflow/gate and DEC-145 review source;
3. add a first-run rejection guard;
4. authorize at most one outer historical result-producing attempt.

That authorization decision must not dispatch the workflow itself.

The first eventual attempt, regardless of success, failure, cancellation, or timeout, consumes the one-run slot unless an even later replacement decision explicitly changes the source of truth.
