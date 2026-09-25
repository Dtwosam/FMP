# Phase 8A — EXP-057 Predeclared Terminal Review

**Date:** 2026-09-25
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED
**Decision:** DEC-224
**Experiment:** EXP-20260925-057

## Purpose

DEC-224 predeclares the exact terminal review for any later separately authorized first EXP-057 historical model-result attempt.

It does not authorize workflow dispatch, model fitting, or result production.

## Frozen source bindings

DEC-224 binds:

- DEC-223 merge: `160c618352739a1ae12b86c80be9573e4c2f234a`
- DEC-223 workflow blob: `db9d8ccaa7da674124963acc6ab4e65e6c2ad83f`
- DEC-223 CLI blob: `889b2daa4e44175e0479377d6c8ea39846da596d`
- DEC-223 execution-gate blob: `07c7db8bc7fc29cf595aa617f1d66ec4f77e4879`

The reviewed workflow identity must be exactly:

- name: `phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training`
- path: `.github/workflows/phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run attempt: `1`

Any rerun attempt is rejected.

## Success review

A successful run must have exactly 11 completed jobs:

- one `authorization-preflight`;
- nine `model-cells (...)` matrix jobs;
- one `aggregate-model-evidence`.

All 11 jobs must conclude `success`.

The run must also expose exactly all expected non-expired artifacts:

- nine pair/timeframe cell-result artifacts;
- one aggregate model-result evidence artifact.

The aggregate artifact must contain complete evidence that recompiles exactly under DEC-222 for the reviewed head commit.

Successful aggregate revalidation verifies:

- 18 exact cells;
- 108 regressors;
- 108 pooled calibration references;
- 432 fit-temporal utility-support references;
- 216 fit-temporal feature-support references;
- 432 residual references;
- residual-breadth bound count 12 per eligible row;
- residual lower-tail source-bound count 12 per eligible row;
- fixed lower-tail count 3;
- deterministic aggregate evidence fingerprint.

A successful review still authorizes no promotion, shadow execution, or trading.

## Non-success review

Allowed terminal non-success conclusions are:

- `failure`;
- `cancelled`;
- `timed_out`.

For a non-success attempt:

- all 11 jobs must still be represented as completed;
- already-produced expected cell artifacts may be preserved;
- no aggregate artifact may be claimed;
- no aggregate result evidence may be claimed;
- no replacement model run is authorized.

The review reports exact preflight/matrix completion counts and routes the attempt to a failure-review state.

## No retry/replacement

The review rejects:

- attempt number greater than 1;
- unexpected artifacts;
- aggregate evidence on non-success;
- aggregate artifact on non-success;
- duplicate or malformed job identities;
- workflow identity drift.

No rerun, retry, or replacement path is opened by DEC-224.

## Authorization state

DEC-224 keeps false:

- workflow dispatch;
- authoritative model-result execution;
- model-protocol result production;
- model fit;
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

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_result_review.py`

Git blob:

`1a5f3e86b4d445ba4a77f3496f81de2b16b333cd`

Focused tests:

`tests/test_phase8a_exp057_model_result_review.py`

Git blob:

`7eeb1c27d81cacf7aa7aacbcf485aeaf97409b41`

## Next gate

After DEC-224 is green and merged, the next safe gate is a separate zero-prior-run proof plus first-run rejection guard and, at most, one bounded outer EXP-057 historical-result slot.

DEC-224 itself does not dispatch or authorize execution.
