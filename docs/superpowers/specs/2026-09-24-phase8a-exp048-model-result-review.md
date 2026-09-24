# Phase 8A — EXP-048 Predeclared Terminal-Result Review

**Date:** 2026-09-24
**Status:** APPROVED BEFORE ANY EXP-048 HISTORICAL MODEL RESULT OR RUN AUTHORIZATION
**Decision:** DEC-127
**Experiment:** EXP-20260924-048

## Purpose

DEC-127 freezes the exact terminal-review contract for any future guarded EXP-048 historical model run before any such run is authorized. It does not authorize dispatch, model fitting, historical result execution, retry/replacement, promotion, shadow/demo execution, broker mutation, orders, or trading.

## Exact run identity

A reviewable run must have:

- workflow name `phase8a-exp048-regime-consensus-model-training`;
- workflow path `.github/workflows/phase8a-exp048-regime-consensus-model-training.yml`;
- event `workflow_dispatch`;
- branch `main`;
- run attempt exactly `1`;
- status `completed`;
- valid 40-character hexadecimal head SHA.

Allowed terminal conclusions are only:

- `success`
- `failure`
- `cancelled`
- `timed_out`

Any rerun attempt is rejected.

## Exact job inventory

DEC-127 requires exactly 11 completed jobs:

1. one `authorization-preflight`;
2. nine `model-cells (...)` matrix jobs;
3. one `aggregate-model-evidence`.

All job IDs must be unique integers. Unexpected job names fail closed.

## Exact artifact namespace

Nine cell artifacts are allowed:

`exp048-regime-consensus-model-cell-results-<SYMBOL>-<TIMEFRAME>-<HEAD_SHA>`

for the exact EURUSD/GBPUSD/USDJPY × 5m/15m/1h matrix.

The only aggregate artifact allowed is:

`exp048-regime-consensus-model-result-evidence-<HEAD_SHA>-from-feature-35867307338-outcome-35876715434`

Artifact names must be unique and non-expired. Unexpected artifacts fail closed.

## Successful-run review

A terminal `success` requires:

- successful authorization preflight;
- all nine matrix jobs successful;
- aggregate job successful;
- all nine cell artifacts present;
- aggregate artifact present;
- aggregate evidence supplied;
- aggregate evidence revalidated through the frozen DEC-125 validator against the exact workflow head SHA.

The stage returned is:

`REGIME_CONSENSUS_MODEL_RESULT_REVIEW_REQUIRED`

This is a review requirement, not promotion authorization.

## Non-success review

For `failure`, `cancelled`, or `timed_out`:

- no aggregate evidence may be claimed;
- no aggregate artifact may be present;
- a valid subset of persisted cell artifacts may remain;
- aggregate job conclusion must be `skipped`, `failure`, or `cancelled`.

The reviewer records matrix outcome counts and returns:

`REGIME_CONSENSUS_MODEL_RUN_FAILURE_REVIEW_REQUIRED`

No retry/replacement is authorized by a non-success result.

## Source identity

Implementation:

`src/fmp/market_learning/model_successor_regime_consensus_result_review.py`

Git blob:

`0cd943cb4bb8780a6adfab02b0743c8415dcd5fe`

Decision constant:

`REGIME_CONSENSUS_MODEL_RESULT_REVIEW_DECISION = "DEC-127"`

Focused tests:

`tests/test_phase8a_exp048_model_result_review.py`

Git blob:

`da7c39aec0ee7a21b6213cff5f18d3a5bed7cd26`

## Authorization state

DEC-127 keeps false:

- replacement model-run authorization;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

DEC-127 does not modify DEC-126's closed dispatch/result/fit authorization.

## Next gate

Only after DEC-127 merges may a later decision consider at most one guarded historical EXP-048 run. Such a decision must independently verify zero prior manual-main EXP-048 runs and add a first-run rejection guard before opening the slot.

DEC-127 itself performs no dispatch and authorizes no result-producing execution.
