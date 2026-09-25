# Phase 8A — EXP-055 Clean-Main One-Way Operator

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED
**Decision:** DEC-204
**Experiment:** EXP-20260925-055

## Purpose

DEC-204 binds merged DEC-203 first-run authorization and adds a fail-closed operator that can derive exactly one next action from live GitHub state without itself dispatching anything unless the explicit `advance --execute` path is later invoked from a separately controlled runner.

The operator exists to prevent duplicate historical runs and stale-main dispatches.

## Frozen authorization binding

DEC-204 binds DEC-203 merge:

`420861c171e327d0363ed684ce57d8e8f3126d60`

It validates the exact DEC-201 execution-gate decision and DEC-203 execution-authorization decision, together with the frozen DEC-198 through DEC-202 source chain.

## Checkout preflight

Before planning any action, the operator requires:

- local branch exactly `main`
- local HEAD is a valid Git SHA
- fetched `origin/main` is a valid Git SHA
- local HEAD exactly equals fetched `origin/main`
- working tree is clean
- `origin` resolves exactly to `Dtwosam/FMP`

Any mismatch fails closed.

## Workflow-state classification

The operator reads the exact EXP-055 manual-main workflow history and accepts at most one relevant run.

State is classified as:

- `MISSING`: no manual-main EXP-055 run exists
- `IN_PROGRESS`: the one existing run is not completed
- `TERMINAL`: the one existing run is completed

More than one relevant run is a hard error because DEC-203 authorizes only one historical attempt.

## One-way action rule

Only `MISSING` may expose the exact frozen command:

`gh workflow run phase8a-exp055-fit-temporal-residual-breadth-utility-model-training.yml --ref main -R Dtwosam/FMP`

For `MISSING`, the report may expose the four bounded historical-run authorization fields as true:

- model-run dispatch
- authoritative historical-result execution
- model-protocol result production
- model fit

Replacement-run authorization remains false.

For `IN_PROGRESS`, all four historical-run fields are false and no dispatch command may appear.

For `TERMINAL`, all four historical-run fields are false, no dispatch command may appear, and the next action is DEC-202 terminal review.

## Double-plan execution safety

The public CLI supports:

- `next`: read-only plan
- `advance`: prepare one action without dispatch
- `advance --execute`: execute only after a second independent `next` plan exactly matches the first

If live state changes between the two plans, execution fails closed.

The CLI contains no rerun command and no replacement-run path.

## Terminal evidence path

When a terminal successful model run exists, the operator identifies exactly one non-expired aggregate artifact named:

`exp055-fit-temporal-residual-breadth-utility-model-result-evidence-<head>-from-feature-35867307338-outcome-35876715434`

It downloads the artifact, requires exactly one `model-result-evidence.json`, requires the evidence `code_commit` to match the reviewed run head, and delegates acceptance to the frozen DEC-202 terminal-review contract.

## Downstream locks

DEC-204 keeps false:

- replacement model run
- promotion
- shadow execution
- demo orders
- broker mutation
- live orders
- real-money action
- trading

## Source identity

Operator library:

`src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_operator.py`

Git blob:

`5d7ee9fea71626fc370bfec81f9747d8af79b5b0`

Public operator CLI:

`scripts/phase8a_exp055_operator.py`

Git blob:

`c8ca1f558b1f89b6db15d294145d116ac7441ac0`

Focused tests:

`tests/test_phase8a_exp055_operator.py`

Git blob:

`394cde7441ecb0a14f4044898280c4cdecbbfd82`

## Next gate

After DEC-204 is green and merged, the next safe gate is a repository-hosted **read-only** plan runner that invokes only `next`, uses read-only permissions, and proves the live zero-run state on merged main.

DEC-204 itself does not dispatch the EXP-055 model workflow.
