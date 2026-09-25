# Phase 8A — EXP-056 Predeclared Terminal Review

**Date:** 2026-09-25
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED
**Decision:** DEC-213
**Experiment:** EXP-20260925-056

## Purpose

DEC-213 predeclares the exact attempt-1 terminal-review contract for any later separately authorized EXP-056 historical model-result run.

It does not authorize workflow dispatch, model fitting, result execution, reruns, replacements, promotion, or trading.

## Frozen DEC-212 source bindings

DEC-213 binds merged DEC-212 commit:

`3da30377a5d358471e79a32466f93fd80cf3a02f`

and exact source blobs:

- workflow: `83e5434c065167294b854b58308fec6d39d800db`
- CLI: `30e79ef7ef20d12d75fc97103b9411b7b467ecef`
- execution gate: `a81f746c8b19abc63f1bb83da0c32f1023644b94`

The review accepts only:

- workflow name `phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training`
- workflow path `.github/workflows/phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml`
- event `workflow_dispatch`
- branch `main`
- run attempt `1`
- terminal status `completed`

Rerun attempts are rejected.

## Successful terminal review

A successful run must contain exactly 11 completed jobs:

- one `authorization-preflight`;
- nine pair/timeframe `model-cells (...)` jobs;
- one `aggregate-model-evidence` job.

All 11 must conclude successfully.

The artifact inventory must contain exactly the nine expected non-expired pair/timeframe cell artifacts and the one expected non-expired aggregate artifact for the reviewed head SHA.

The aggregate evidence must deterministically recompile through DEC-211 for the exact reviewed head commit and match byte-for-byte as a Python mapping.

Verified successful evidence includes:

- 18 cells;
- 108 regressors;
- 108 pooled calibration references;
- 432 utility-support references;
- 216 feature-support references;
- 432 residual references;
- residual-breadth bound inventory: 12 per eligible row;
- residual lower-tail source-bound inventory: 12 per eligible row;
- fixed residual lower-tail count: 3;
- exact aggregate evidence fingerprint.

## Non-success terminal review

A terminal failure, cancellation, or timeout may preserve only produced cell artifacts.

It cannot claim:

- aggregate result evidence;
- aggregate artifact;
- rerun authorization;
- retry authorization;
- replacement-run authorization.

The review records preflight and matrix job outcomes for diagnostic purposes only.

## Closed downstream state

DEC-213 keeps false:

- replacement model run;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Source identity

Terminal-review source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_result_review.py`

Git blob:

`0bfc50d39d04d82e95c731b7284c7be143191efd`

Focused tests:

`tests/test_phase8a_exp056_model_result_review.py`

Git blob:

`bf1494a3995eb40a5af9ea2210a8cbc0c20add0b`

## Next gate

Only after DEC-213 is green and merged may a later separate decision:

1. prove zero prior exact EXP-056 manual-main runs;
2. add a first-run rejection guard;
3. consider opening at most one bounded outer historical-result slot.

DEC-213 itself does not authorize or dispatch execution.
