# Phase 8A — EXP-052 Predeclared Terminal-Result Review

**Date:** 2026-09-25
**Status:** APPROVED BEFORE ANY EXP-052 HISTORICAL MODEL RESULT OR RUN AUTHORIZATION
**Decision:** DEC-167
**Experiment:** EXP-20260925-052

## 1. Purpose

DEC-167 freezes the exact terminal-review contract for the future first EXP-052 historical model run before any result-producing authorization exists.

It does not authorize dispatch, model fitting, historical result execution, a replacement run, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.

## 2. Frozen workflow identity

Only a run with all of the following is reviewable:

- workflow name: `phase8a-exp052-fit-temporal-support-utility-model-training`;
- workflow path: `.github/workflows/phase8a-exp052-fit-temporal-support-utility-model-training.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- run attempt: exactly `1`;
- terminal status: `completed`;
- conclusion: `success`, `failure`, `cancelled`, or `timed_out`.

Any rerun attempt is rejected.

The review binds the merged DEC-166 source identity:

- DEC-166 merge: `2883cc46c65ff7c672c9f8d7192fc7fb240a9835`;
- workflow blob: `a49af5daeb14177a44154ef96b135f64a98a85bf`;
- CLI blob: `728691476a2285ec4cdec594a020aa5c84b04c5e`;
- execution-gate blob: `139028be1c354a99599a3ed6505a1a4725889c02`.

## 3. Required job inventory

The terminal job payload must contain exactly 11 unique completed jobs:

- one `authorization-preflight`;
- nine `model-cells (...)` matrix jobs;
- one `aggregate-model-evidence`.

Unknown job names, duplicate job IDs, non-completed jobs, or a different count fail closed.

## 4. Expected cell artifacts

The only accepted pair/timeframe cell artifact identities are:

- EURUSD 5m;
- EURUSD 15m;
- EURUSD 1h;
- GBPUSD 5m;
- GBPUSD 15m;
- GBPUSD 1h;
- USDJPY 5m;
- USDJPY 15m;
- USDJPY 1h.

For run head `<sha>`, the exact cell artifact namespace is:

`exp052-fit-temporal-support-utility-model-cell-results-<symbol>-<timeframe>-<sha>`

Artifacts must be non-expired and uniquely named.

## 5. Expected aggregate artifact

For run head `<sha>`, the only accepted aggregate artifact is:

`exp052-fit-temporal-support-utility-model-result-evidence-<sha>-from-feature-35867307338-outcome-35876715434`

No unrelated artifact may be present in the reviewed workflow artifact listing.

## 6. Successful-run review

A successful run is reviewable only when:

- authorization preflight succeeded;
- all nine matrix jobs succeeded;
- aggregate job succeeded;
- all nine cell artifacts exist;
- the aggregate artifact exists;
- aggregate evidence is supplied to the review function;
- DEC-165 aggregate-evidence validation succeeds using the run head SHA as the expected code commit.

A GitHub `success` conclusion by itself is insufficient.

DEC-165 independently requires:

- 18 cells;
- 108 regressors;
- 108 pooled calibration references;
- 432 fit-temporal-support references;
- support/pooled/raw cutoff evidence;
- frozen financial/stability gates;
- chronology/status chains;
- canonical cell and aggregate fingerprints.

The successful terminal stage is:

`FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_REVIEW_REQUIRED`

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

`FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`

A non-success first attempt does not authorize a rerun or replacement.

## 8. Replacement and rerun policy

DEC-167 freezes:

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

`src/fmp/market_learning/model_successor_fit_temporal_support_utility_result_review.py`

Git blob:

`dbccea23117adbc50fa54345ec418fde54f254a3`

Focused tests:

`tests/test_phase8a_exp052_model_result_review.py`

Git blob:

`a03655452521c0bad378c045f323fa63f52e2cb6`

## 10. Next gate

After DEC-167 is merged, a later separate authorization decision may:

1. independently verify that zero prior manual-main EXP-052 workflow runs exist;
2. bind the merged DEC-166 workflow/gate and DEC-167 review source;
3. add a first-run rejection guard;
4. authorize at most one outer historical result-producing attempt.

That authorization decision must not dispatch the workflow itself.

The first eventual attempt, regardless of success, failure, cancellation, or timeout, consumes the one-run slot unless an even later replacement decision explicitly changes the source of truth.
