# Phase 8A — EXP-050 Predeclared Terminal-Result Review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-050 HISTORICAL RESULT OR RUN AUTHORIZATION
**Decision:** DEC-145
**Experiment:** EXP-20260924-050

## 1. Purpose

DEC-145 freezes the exact terminal review contract for a possible future EXP-050 historical run before any run authorization or result exists.

It changes no DEC-144 execution flag and authorizes no dispatch, fitting, historical result production, replacement run, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading.

## 2. Reviewable run identity

Only a run matching all of the following is reviewable:

- workflow name: `phase8a-exp050-temporal-jackknife-utility-model-training`
- workflow path: `.github/workflows/phase8a-exp050-temporal-jackknife-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run attempt: exactly `1`
- terminal status: `completed`
- conclusion: `success`, `failure`, `cancelled`, or `timed_out`

Any rerun attempt is rejected.

## 3. DEC-144 source binding

The review binds the exact DEC-144 workflow source:

- DEC-144 merge: `9f2986c783823cf7d9647ed4b0a50c66470bea21`
- workflow blob: `ec8ed4ab3f0b8a18ffc735af92172e059ed29955`
- CLI blob: `70c5e9b8d22888b9727e234fd80ea3e3ba4e5e09`
- execution-gate blob: `4814f0db86bec943d7282ab13586559b1eb8caa7`

DEC-144 remains pre-authorization: dispatch/result/fit flags remain false.

## 4. Exact job inventory

Terminal review requires exactly 11 completed jobs:

- one `authorization-preflight`;
- nine matrix jobs whose names begin `model-cells (`;
- one `aggregate-model-evidence`.

Duplicate job IDs, malformed names, unexpected jobs, missing jobs, or non-completed jobs fail closed.

## 5. Exact artifact inventory

The only accepted cell artifact names are:

`exp050-temporal-jackknife-utility-model-cell-results-<symbol>-<timeframe>-<head-sha>`

for exactly the nine frozen pair/timeframe cells.

The only accepted aggregate artifact name is:

`exp050-temporal-jackknife-utility-model-result-evidence-<head-sha>-from-feature-35867307338-outcome-35876715434`

Every reviewed artifact must be non-expired.

Unexpected or duplicate artifact names fail closed.

## 6. Successful first-attempt review

A successful run requires all of:

- preflight conclusion `success`;
- all nine matrix conclusions `success`;
- aggregate conclusion `success`;
- all nine expected cell artifacts present;
- the one expected aggregate artifact present;
- aggregate evidence supplied to the review;
- aggregate evidence successfully revalidated through the DEC-143 EXP-050 contract against the exact workflow head SHA.

A successful terminal review stops at:

`TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_REVIEW_REQUIRED`

Success alone does not authorize promotion or any trading path.

## 7. Non-success first-attempt review

For a first attempt ending `failure`, `cancelled`, or `timed_out`:

- any valid subset of the exact nine cell artifacts may be preserved;
- no aggregate artifact may be claimed;
- no aggregate evidence may be supplied;
- matrix success/failure/cancelled/skipped counts are recorded;
- preflight conclusion is recorded.

A non-success terminal review stops at:

`TEMPORAL_JACKKNIFE_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`

Partial evidence remains evidence only. It cannot be promoted to a complete result.

## 8. Rerun and replacement policy

DEC-145 authorizes:

- no rerun;
- no replacement run;
- no retry after failure, cancellation, timeout, or success.

Any later replacement authorization would require a separate explicit decision; DEC-145 contains none.

## 9. Review implementation

Review source:

`src/fmp/market_learning/model_successor_temporal_jackknife_utility_result_review.py`

Git blob:

`e93f7f26e6f0cf8541c9dffd0d359acf0a7ec64e`

Focused tests:

`tests/test_phase8a_exp050_model_result_review.py`

Git blob:

`54dd7a4c973a685efcc7a4b732c2be46e64e7aff`

The tests cover complete success, partial failure, preflight failure, rerun rejection, aggregate-evidence requirements, non-success aggregate prohibition, unexpected artifacts, and workflow identity rejection.

## 10. Authorization state

DEC-145 keeps false:

- replacement model-run authorization;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

It does not alter the false DEC-144 dispatch/result/protocol-result/model-fit flags.

## 11. Next gate

Only after DEC-145 is merged may a later separate decision:

1. independently verify zero prior manual-main EXP-050 runs;
2. harden the workflow with a first-run rejection guard;
3. open at most one outer historical result-producing authorization.

That later decision must itself dispatch nothing.

DEC-145 creates no model result.
