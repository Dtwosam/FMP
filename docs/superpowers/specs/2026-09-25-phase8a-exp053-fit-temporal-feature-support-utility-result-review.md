# Phase 8A — EXP-053 Predeclared Terminal-Result Review

**Date:** 2026-09-25
**Status:** APPROVED BEFORE ANY EXP-053 HISTORICAL MODEL RESULT OR RUN AUTHORIZATION
**Decision:** DEC-178
**Experiment:** EXP-20260925-053

## 1. Purpose

DEC-178 freezes the exact terminal-review contract for the future first EXP-053 historical model run before any result-producing authorization exists.

It authorizes no dispatch, fitting, result execution, replacement run, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading.

## 2. Frozen workflow identity

Only a run with all of the following is reviewable:

- workflow name `phase8a-exp053-fit-temporal-feature-support-utility-model-training`;
- workflow path `.github/workflows/phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml`;
- event `workflow_dispatch`;
- branch `main`;
- run attempt exactly `1`;
- status `completed`;
- conclusion `success`, `failure`, `cancelled`, or `timed_out`.

Any rerun attempt is rejected.

The review binds the merged DEC-177 source:

- DEC-177 merge: `7faa5e765f08a47062444ebce3756bf9435ef1d4`;
- workflow blob: `0a6704f75e83b06b7555dbb9dc912cda31443bbc`;
- CLI blob: `dbd146100d81be6ffc492de448d8dc4e0a2f4e73`;
- execution-gate blob: `600ea84946fe908d143f3fbe2082b3505733cdf5`.

## 3. Required jobs

The terminal job payload must contain exactly 11 unique completed jobs:

- one `authorization-preflight`;
- nine `model-cells (...)` matrix jobs;
- one `aggregate-model-evidence`.

Unknown jobs, duplicate IDs, non-completed jobs, or a different count fail closed.

## 4. Expected artifacts

For run head `<sha>`, the exact cell artifact namespace is:

`exp053-fit-temporal-feature-support-utility-model-cell-results-<symbol>-<timeframe>-<sha>`

Exactly the nine frozen EURUSD/GBPUSD/USDJPY × 5m/15m/1h identities are recognized.

The only accepted aggregate artifact is:

`exp053-fit-temporal-feature-support-utility-model-result-evidence-<sha>-from-feature-35867307338-outcome-35876715434`

Artifacts must be uniquely named and non-expired. Unrelated artifacts fail closed.

## 5. Successful-run review

A successful run requires:

- successful authorization preflight;
- all nine matrix jobs successful;
- aggregate job successful;
- all nine cell artifacts present;
- aggregate artifact present;
- aggregate evidence supplied to the review function;
- DEC-176 aggregate-evidence revalidation using the run head SHA.

A GitHub `success` conclusion alone is insufficient.

DEC-176 independently requires:

- 18 cells;
- 108 regressors;
- 108 pooled calibration references;
- 432 fit-temporal utility-support references;
- 216 fit-temporal feature-support references;
- exact four-part cutoff evidence;
- unchanged financial/stability gates;
- chronology/status chains;
- canonical cell and aggregate fingerprints.

Successful terminal stage:

`FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_REVIEW_REQUIRED`

That stage authorizes nothing downstream.

## 6. Non-success review

A first attempt ending in failure, cancellation, or timeout may preserve a subset of valid cell artifacts.

It may not claim:

- aggregate artifact;
- aggregate result evidence;
- successful result.

The review records preflight result, matrix success/failure/cancel/skipped counts, and persisted cell-artifact count.

Non-success stage:

`FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`

The first attempt still consumes the slot once a later authorization exists; DEC-178 itself creates no slot.

## 7. Rerun/replacement policy

DEC-178 freezes:

- rerun attempt > 1: rejected;
- replacement run authorized: false;
- promotion: false;
- shadow: false;
- demo order: false;
- broker mutation: false;
- live order: false;
- real-money action: false;
- trading: false.

## 8. Source identity

Review source:

`src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_result_review.py`

Git blob:

`c1586f8ddf48ad1125adaed7d8d8f0a476862beb`

Focused tests:

`tests/test_phase8a_exp053_model_result_review.py`

Git blob:

`8a13c038afe0c73ba353f7fc645aa4279bd42b6a`

## 9. Next gate

After DEC-178 merges, a separate authorization decision may:

1. independently verify zero prior manual-main EXP-053 runs;
2. bind DEC-177 workflow/gate and DEC-178 review;
3. add a first-run rejection guard;
4. authorize at most one outer historical result-producing attempt.

That later decision must not dispatch the workflow itself.
