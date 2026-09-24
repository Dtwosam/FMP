# Phase 8A — EXP-047 Predeclared Terminal-Result Review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-047 HISTORICAL MODEL RESULT OR RUN AUTHORIZATION
**Decision:** DEC-117
**Experiment:** EXP-20260924-047

## 1. Purpose

DEC-117 freezes the exact terminal-review contract for any future guarded EXP-047 historical model run before any such run is authorized.

This prevents success/failure review semantics from being changed after seeing an EXP-047 result.

DEC-117 does not authorize a workflow dispatch, model fit, historical result execution, replacement run, promotion, shadow/demo execution, broker mutation, order placement, or trading.

## 2. Exact workflow identity

A reviewable run must have:

- workflow name: `phase8a-exp047-density-model-training`
- workflow path: `.github/workflows/phase8a-exp047-density-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run attempt: exactly `1`
- status: `completed`
- valid 40-character hexadecimal head SHA

Allowed terminal conclusions:

- `success`
- `failure`
- `cancelled`
- `timed_out`

Any rerun attempt is rejected.

## 3. Exact job inventory

DEC-117 requires exactly 11 completed jobs:

1. one `authorization-preflight`
2. nine `model-cells (...)` matrix jobs
3. one `aggregate-model-evidence`

All job IDs must be valid integers and unique.

Unexpected job names fail review closed.

## 4. Exact artifact namespace

Artifacts may only use the exact EXP-047 names tied to the run head SHA.

Nine pair/timeframe cell artifacts:

`exp047-density-model-cell-results-<SYMBOL>-<TIMEFRAME>-<HEAD_SHA>`

for:

- EURUSD 5m
- EURUSD 15m
- EURUSD 1h
- GBPUSD 5m
- GBPUSD 15m
- GBPUSD 1h
- USDJPY 5m
- USDJPY 15m
- USDJPY 1h

Aggregate artifact:

`exp047-density-model-result-evidence-<HEAD_SHA>-from-feature-35867307338-outcome-35876715434`

Artifact names must be unique and non-expired.

Unexpected artifacts fail review closed.

## 5. Successful-run review

For a terminal `success`:

- authorization preflight must succeed;
- all nine matrix jobs must succeed;
- aggregate job must succeed;
- all nine cell artifacts must be present;
- aggregate artifact must be present;
- aggregate evidence must be supplied to the reviewer;
- aggregate evidence must revalidate through the frozen DEC-115 validator against the exact workflow head SHA.

The reviewer then returns:

`DENSITY_MODEL_RESULT_REVIEW_REQUIRED`

This stage is a review requirement, not promotion authorization.

## 6. Non-success review

For `failure`, `cancelled`, or `timed_out`:

- no aggregate evidence may be claimed;
- no aggregate artifact may be present;
- a valid subset of already-persisted cell artifacts may be preserved;
- the aggregate job conclusion must be one of `skipped`, `failure`, or `cancelled`.

The reviewer records counts of successful, failed, cancelled, and skipped matrix jobs and returns:

`DENSITY_MODEL_RUN_FAILURE_REVIEW_REQUIRED`

A failed/cancelled/timed-out run does not authorize a retry or replacement.

## 7. Partial evidence

DEC-117 deliberately preserves valid partial pair/timeframe artifacts on a non-success terminal outcome.

Partial evidence does not become aggregate EXP-047 result evidence and does not authorize a replacement run.

## 8. Aggregate validator

Successful aggregate evidence is validated only through:

`validate_density_model_result_evidence(...)`

from DEC-115.

The review does not recreate or weaken the density/cutoff/stability/evidence contract.

## 9. Review source identity

Implementation:

`src/fmp/market_learning/model_successor_density_result_review.py`

Git blob:

`466e163edc42145b7cf2d698c48c713e0e804a95`

Decision constant:

`DENSITY_MODEL_RESULT_REVIEW_DECISION = "DEC-117"`

## 10. Authorization state

DEC-117 keeps false:

- replacement model-run authorization;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

DEC-117 does not modify DEC-116's closed dispatch/result/fit authorization.

## 11. Next gate

Only after DEC-117 is merged may a later separate decision consider authorizing at most one guarded historical EXP-047 result-producing run.

Such an authorization must independently verify that zero prior manual-main EXP-047 runs exist and must harden the workflow with a first-run rejection guard before opening the one-run slot.

DEC-117 itself performs no dispatch and authorizes no result-producing execution.
