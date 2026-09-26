# Phase 8A — EXP-060 Predeclared Terminal Review

**Date:** 2026-09-26
**Status:** APPROVED REVIEW SOURCE / EXECUTION CLOSED
**Decision:** DEC-257
**Experiment:** EXP-20260926-059

## Purpose

DEC-257 predeclares exact terminal review for any later separately authorized first EXP-060 historical model-result attempt.

It does not authorize workflow dispatch, model fitting, result production, retry, rerun, replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.

## Frozen source bindings

DEC-257 binds merged DEC-256:

- DEC-256 merge: `cef9f6d201bf2b025f08c924a11c84e9684b9ba0`
- workflow blob: `20af1bf2f9057274a8c50d5b48becbf5f683ef86`
- CLI blob: `90c6bc9e893c813d394e3a9c4adc5a155e938af0`
- execution-gate blob: `82f51bf85ccb1793b3a980b2884f3e122a03c8db`

The exact workflow identity is:

- name: `phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training`
- path: `.github/workflows/phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml`
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

`exp060-fit-temporal-residual-regime-balance-utility-model-cell-results-<symbol>-<timeframe>-<head_sha>`

The aggregate artifact is:

`exp060-fit-temporal-residual-regime-balance-utility-model-result-evidence-<head_sha>-from-feature-35867307338-outcome-35876715434`

All reviewed artifacts must be non-expired and uniquely named.

## Successful terminal review

A successful run requires:

- preflight success;
- all nine matrix jobs success;
- aggregate job success;
- all nine expected cell artifacts;
- the exact aggregate artifact;
- aggregate evidence supplied to the reviewer.

The aggregate evidence is deterministically recompiled through the frozen DEC-255 repaired compiler for the reviewed head commit. The supplied and recompiled payloads must match exactly.

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

DEC-257 keeps false:

- replacement model run;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

DEC-257 itself also does not authorize workflow dispatch, authoritative result execution, model-protocol result production, or model fit.

## Source identity

Terminal-review source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_result_review.py`

Git blob:

`989ebc7b0cc33e5076f83ea94337fe6581c321e3`

Focused tests:

`tests/test_phase8a_exp060_model_result_review.py`

Git blob:

`a9679622fd5a7ca9328dbcb44be073ffabd21240`

## Next gate

After DEC-257 is green and merged, the next safe gate is a separate zero-prior-run proof plus first-run rejection guard and at most one bounded outer historical-result slot.

DEC-257 itself does not open or consume that slot.
