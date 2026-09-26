# Phase 8A — EXP-059 Predeclared Terminal Review

**Date:** 2026-09-26
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED
**Decision:** DEC-246
**Experiment:** EXP-20260926-059

## Purpose

DEC-246 predeclares exact terminal review for any later separately authorized first EXP-059 historical model-result attempt.

It does not authorize workflow dispatch, model fitting, result production, retry, rerun, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.

## Frozen source bindings

DEC-246 binds merged DEC-245:

- DEC-245 merge: `d33e2f1e6e7f39c12811dbc07c5cd960f8e2442f`
- workflow blob: `d416c43c9e582f49cd60314c6ee736925e8185e8`
- CLI blob: `44c084c226c62c30ddf16741027593a4a835605f`
- execution-gate blob: `d6556cf3bc3a1189c2ee6648c1870ec307a2178f`

The exact workflow identity is:

- name: `phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training`
- path: `.github/workflows/phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`

Only run attempt 1 is reviewable.

## Exact job inventory

Terminal review requires exactly 11 completed jobs:

- one `authorization-preflight`;
- nine matrix `model-cells (...)` jobs;
- one `aggregate-model-evidence` job.

Unexpected, missing, duplicated, or incomplete jobs fail closed.

## Exact artifact inventory

Expected cell artifacts are the nine pair/timeframe artifacts named:

`exp059-fit-temporal-residual-regime-balance-utility-model-cell-results-<symbol>-<timeframe>-<head_sha>`

The aggregate artifact is:

`exp059-fit-temporal-residual-regime-balance-utility-model-result-evidence-<head_sha>-from-feature-35867307338-outcome-35876715434`

All reviewed artifacts must be non-expired and uniquely named.

## Successful terminal review

A successful run requires:

- preflight success;
- all nine matrix jobs success;
- aggregate job success;
- all nine expected cell artifacts;
- the exact aggregate artifact;
- aggregate evidence supplied to the reviewer.

The aggregate evidence is deterministically recompiled through the frozen DEC-244 compiler for the reviewed head commit. The supplied and recompiled payloads must match exactly.

Successful revalidation verifies:

- 18 cells;
- 108 regressors;
- 108 pooled calibration references;
- 432 utility-support references;
- 216 feature-support references;
- 432 residual references;
- 12 residual-breadth bounds per eligible row;
- 12 residual lower-tail source bounds per eligible row;
- lower-tail count 3;
- three residual fit regimes;
- four residual windows per regime;
- 12 regime-floor source bounds per eligible row;
- three regime-balance source regimes;
- 12 regime-balance source bounds per eligible row;
- regime-balance penalty multiplier 1.0;
- the exact aggregate evidence fingerprint.

A successful review only routes the frozen historical evidence to a later result-decision gate. It does not authorize replacement or downstream execution.

## Non-success terminal review

Accepted non-success terminal conclusions are:

- `failure`;
- `cancelled`;
- `timed_out`.

A non-success review may preserve only produced expected cell artifacts. It may not claim an aggregate artifact or aggregate result evidence.

Any run attempt greater than 1 is rejected. No rerun, retry, or replacement path is opened.

## Authorization state

DEC-246 keeps false:

- replacement model run;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

DEC-246 itself also does not authorize workflow dispatch, authoritative result execution, model-protocol result production, or model fit.

## Source identity

Terminal-review source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_result_review.py`

Git blob:

`5adc6ad72b2dfab1de1cca09a9bb2bc09663bfc5`

Focused tests:

`tests/test_phase8a_exp059_model_result_review.py`

Git blob:

`e3d2abfe369a4a92510adce9c7b1d110bc363a28`

## Next gate

After DEC-246 is green and merged, the next safe gate is a separate zero-prior-run proof plus first-run rejection guard and at most one bounded outer historical-result slot.

DEC-246 itself does not open or consume that slot.
