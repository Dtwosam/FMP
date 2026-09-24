# Phase 8A — EXP-049 Predeclared Terminal-Result Review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-049 HISTORICAL MODEL RESULT OR RUN AUTHORIZATION
**Decision:** DEC-136
**Experiment:** EXP-20260924-049

## Purpose

DEC-136 freezes the exact terminal-review contract for the future first EXP-049 historical model run before any result-producing authorization exists.

It does not authorize dispatch, fitting, historical result execution, a replacement run, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.

## Frozen workflow identity

Only a run with all of the following is reviewable:

- workflow name: `phase8a-exp049-regime-utility-model-training`
- workflow path: `.github/workflows/phase8a-exp049-regime-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run attempt: exactly 1
- terminal status: completed
- conclusion: success, failure, cancelled, or timed_out

Any rerun attempt is rejected.

The review source records the merged DEC-135 identity:

- DEC-135 merge: `0fe11d26fd74355e39f7379f3eeba869d848271c`
- workflow blob: `955152835ec1cedf39d6d31e54d6028a7953fab5`
- CLI blob: `cba5ece4eda8e02a7ca07a780d8caa69a239e094`
- execution-gate blob: `9d2ffc670a1572febb0e4a29bfda426f8252e5ee`

## Required job inventory

The terminal job payload must contain exactly 11 unique completed jobs:

- one `authorization-preflight`;
- nine `model-cells (...)` matrix jobs;
- one `aggregate-model-evidence`.

Unknown job names, duplicate job IDs, non-completed jobs, or a different count fail closed.

## Expected cell artifacts

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

`exp049-regime-utility-model-cell-results-<symbol>-<timeframe>-<sha>`

Artifacts must be non-expired and uniquely named.

## Expected aggregate artifact

For run head `<sha>`, the only accepted aggregate artifact is:

`exp049-regime-utility-model-result-evidence-<sha>-from-feature-35867307338-outcome-35876715434`

No unrelated artifact may be present in the reviewed workflow artifact listing.

## Successful-run review

A successful run is reviewable only when:

- authorization preflight succeeded;
- all nine matrix jobs succeeded;
- aggregate job succeeded;
- all nine cell artifacts exist;
- the aggregate artifact exists;
- aggregate evidence is supplied to the review function;
- DEC-134 aggregate-evidence validation succeeds using the run head SHA as the expected code commit.

A successful workflow therefore cannot be treated as a valid EXP-049 result merely because GitHub reports `success`; the persisted evidence must independently pass the frozen result-evidence contract.

The resulting stage is:

`REGIME_UTILITY_MODEL_RESULT_REVIEW_REQUIRED`

That stage still authorizes no promotion, shadow, demo, broker mutation, live order, real-money action, or trading.

## Non-success review

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

The resulting stage is:

`REGIME_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`

A non-success first attempt does not automatically authorize a rerun or replacement.

## Replacement and rerun policy

DEC-136 freezes:

- rerun attempt > 1: rejected;
- replacement model run authorized: false;
- promotion authorized: false;
- shadow authorized: false;
- demo order authorized: false;
- broker mutation authorized: false;
- live order authorized: false;
- real-money authorized: false;
- trading authorized: false.

Any future replacement-run decision would require a separate source-of-truth change after reviewing the terminal failure evidence.

## Source identity

Review source:

`src/fmp/market_learning/model_successor_regime_utility_result_review.py`

Git blob:

`1c48405fa8b754ee8d6756dac701332ac72816bd`

Focused tests:

`tests/test_phase8a_exp049_model_result_review.py`

Git blob:

`7d072b0ced240afe33135e6fde689bae511fbc54`

## Next gate

After DEC-136 is merged, a later separate authorization decision may:

1. independently verify that zero prior manual-main EXP-049 workflow runs exist;
2. bind the merged DEC-135 workflow/gate and DEC-136 review source;
3. add a first-run rejection guard;
4. authorize at most one outer historical result-producing attempt.

That authorization decision must not dispatch the workflow itself.

The first eventual attempt, regardless of success, failure, cancellation, or timeout, must consume the one-run slot unless an even later replacement decision explicitly changes the source of truth.
