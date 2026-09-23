# Phase 8A — EXP-046 Predeclared Terminal-Result Review

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-046 HISTORICAL MODEL RESULT
**Decision:** DEC-108
**Experiment:** EXP-20260923-046

## 1. Purpose

DEC-108 freezes the terminal review contract for any later separately authorized EXP-046 historical model run.

DEC-108 is approved before any EXP-046 model result exists and before any EXP-046 run authorization is opened.

It changes no protocol, training core, artifact runner, workflow, CLI, runtime, historical data, or result-producing authorization.

## 2. Frozen workflow identity

The review accepts only:

- workflow name: `phase8a-exp046-stability-model-training`
- workflow path: `.github/workflows/phase8a-exp046-stability-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run attempt: exactly `1`
- terminal status: `completed`

Allowed terminal conclusions:

- `success`
- `failure`
- `cancelled`
- `timed_out`

Any rerun attempt is rejected.

## 3. Exact job inventory

Terminal review requires exactly 11 completed jobs:

1. one `authorization-preflight`;
2. nine `model-cells (...)` matrix jobs;
3. one `aggregate-model-evidence`.

No unexpected job name is accepted.

## 4. Exact artifact namespace

The only allowed pair/timeframe artifacts are:

`exp046-stability-model-cell-results-<SYMBOL>-<TIMEFRAME>-<HEAD_SHA>`

for exactly:

- EURUSD 5m
- EURUSD 15m
- EURUSD 1h
- GBPUSD 5m
- GBPUSD 15m
- GBPUSD 1h
- USDJPY 5m
- USDJPY 15m
- USDJPY 1h

The only allowed aggregate artifact is:

`exp046-stability-model-result-evidence-<HEAD_SHA>-from-feature-35867307338-outcome-35876715434`

Artifacts must be unique and non-expired.

## 5. Successful terminal review

A successful workflow conclusion requires:

- successful authorization preflight;
- all nine matrix jobs successful;
- aggregate job successful;
- all nine pair/timeframe artifacts present;
- aggregate artifact present;
- aggregate evidence supplied;
- successful DEC-106 aggregate-evidence revalidation against the exact workflow head SHA.

The terminal stage is:

`STABILITY_MODEL_RESULT_REVIEW_REQUIRED`

This stage is evidence review only. It does not authorize promotion, prospective shadow, demo execution, broker mutation, live orders, real-money action, or trading.

## 6. Non-success terminal review

For a terminal `failure`, `cancelled`, or `timed_out` run:

- aggregate evidence must be absent;
- aggregate artifact must be absent;
- the aggregate job may be skipped, failed, or cancelled;
- any valid persisted pair/timeframe artifacts remain reviewable;
- matrix success/failure/cancelled/skipped counts are recorded;
- no replacement run is authorized.

The terminal stage is:

`STABILITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`

## 7. Rerun and replacement boundary

DEC-108 sets:

`REPLACEMENT_MODEL_RUN_AUTHORIZED = false`

and rejects any `run_attempt != 1`.

A failed/cancelled/timed-out first run cannot be retried merely because partial evidence exists.

Any later authorization decision must explicitly state whether the first attempt consumes the run slot. DEC-108 itself authorizes no run.

## 8. Evidence labels

Any successful EXP-046 result remains:

- `prior_result_informed = true`
- `untouched_oos = false`

The experiment is retrospective and cannot be relabeled as untouched prospective evidence.

## 9. Source identity

Review source:

`src/fmp/market_learning/model_successor_stability_result_review.py`

Git blob:

`e5ff3c6a0cb65ba14bb3bd43d5dd1d4a5a491cf6`

Focused tests:

`tests/test_phase8a_exp046_model_result_review.py`

Git blob:

`ea610254e5f54bfa162866ff1fef829a7e9402f2`

## 10. Authorization state

DEC-108 keeps false:

- replacement model-run authorization;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

DEC-108 does not modify DEC-107's closed dispatch/result/fit gate.

## 11. Next gate

Only after DEC-108 merges may a later separate decision consider:

1. verifying zero prior manual-main EXP-046 runs;
2. hardening the workflow with a prior-run rejection guard;
3. binding the exact merged DEC-107 workflow/CLI/gate source plus DEC-108 review source;
4. authorizing at most one guarded historical EXP-046 result-producing run.

That later decision must not itself claim a model result before execution occurs.
