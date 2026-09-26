# Phase 8A — EXP-058 Predeclared Terminal Review

**Date:** 2026-09-26
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED
**Decision:** DEC-235
**Experiment:** EXP-20260925-058

## Purpose

DEC-235 predeclares exact attempt-1 terminal review for any later separately authorized EXP-058 historical run.

It does not authorize workflow dispatch, authoritative result execution, model-protocol result production, model fitting, rerun, retry, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.

## Frozen source binding

DEC-235 binds merged DEC-234 commit:

`365093ea81fdaf871680b42b02d67ebce3768d34`

and the exact DEC-234 execution-closed surface:

- workflow blob: `78e9bf66ade5f6fb42ebe27e28b7ba24f36741b8`
- public CLI blob: `e35a6ee0ff11bd3928b3bf05bf19f3572f64952c`
- execution-gate blob: `74881c0fee21392872ffd3df1378639bb04fea4a`

The only reviewable workflow is:

`phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training`

at:

`.github/workflows/phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training.yml`

The review accepts only `workflow_dispatch` on `main`, completed status, and run attempt 1.

## Exact workflow job inventory

Every reviewed terminal run must contain exactly 11 completed jobs:

- one `authorization-preflight`;
- nine `model-cells (...)` matrix jobs;
- one `aggregate-model-evidence`.

Any unknown, duplicate, incomplete, or missing job fails closed.

## Successful terminal review

A run with conclusion `success` must have:

- successful authorization preflight;
- all nine matrix jobs successful;
- aggregate job successful;
- all nine expected pair/timeframe cell artifacts;
- the exact aggregate evidence artifact;
- all ten artifacts non-expired;
- aggregate evidence available for deterministic recompilation under DEC-233.

The aggregate evidence is accepted only if recompilation reproduces the evidence object exactly for the reviewed head commit.

Successful revalidation verifies:

- 18 cells;
- 108 regressors;
- 108 pooled calibration references;
- 432 fit-temporal utility-support references;
- 216 fit-temporal feature-support references;
- 432 residual references;
- 12 residual-breadth bounds per eligible row;
- 12 lower-tail source bounds per eligible row;
- lower-tail count 3;
- residual fit-regime count 3;
- residual windows per regime 4;
- 12 regime-floor source bounds per eligible row;
- the exact deterministic aggregate evidence fingerprint.

The successful review stage is:

`FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RESULT_REVIEW_REQUIRED`

## Non-success terminal review

Accepted non-success conclusions are:

- `failure`;
- `cancelled`;
- `timed_out`.

A non-success review may preserve only expected produced cell artifacts.

It must not claim:

- an aggregate artifact;
- aggregate evidence;
- a replacement run;
- a retry;
- a rerun.

The non-success review stage is:

`FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`

The review records preflight and matrix-job conclusion counts for later result classification.

## One-attempt semantics

Any run attempt greater than 1 is rejected.

DEC-235 contains no path that can authorize a second historical attempt.

## Source identity

Terminal-review source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_result_review.py`

Git blob:

`76ba5de3ef92c02a8139213040dc3cf4d8efd75c`

Focused tests:

`tests/test_phase8a_exp058_model_result_review.py`

Git blob:

`3a71fde170622be55f43261625b5fabf20a178eb`

## Next gate

Only after DEC-235 is green and merged may a separate zero-prior-run proof, first-run rejection guard, and at most one bounded outer historical-result slot be considered.

DEC-235 itself does not dispatch or fit the model.
