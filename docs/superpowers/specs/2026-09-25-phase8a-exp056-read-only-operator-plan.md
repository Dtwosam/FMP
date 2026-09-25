# Phase 8A — EXP-056 Repository-Hosted Read-Only Operator Plan

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED
**Decision:** DEC-216
**Experiment:** EXP-20260925-056

## Purpose

DEC-216 adds a repository-hosted read-only proof for the exact DEC-215 EXP-056 operator `next` plan.

It exists only to prove the live one-shot state on merged `main` before any separate executor source is considered.

## Frozen predecessor binding

DEC-216 binds merged DEC-215 commit:

`328a42ebe2248ca8200bf5d8f50d37fd28186d87`

The frozen operator source remains:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_operator.py`

Git blob:

`de7e4134ba29c619d9d12c9f372bfee96fc1c902`

The public operator CLI remains:

`scripts/phase8a_exp056_operator.py`

Git blob:

`db626a1703cb2238948d4f832ce6e8db093880f4`

## Read-only workflow

Workflow:

`.github/workflows/phase8a-exp056-operator-plan.yml`

Git blob:

`921c4a93aa271b4db3816f8e4e2adb178a0a0318`

The workflow:

- runs only on pushes to `main` affecting the proof workflow, EXP-056 operator CLI, or EXP-056 operator source;
- has only `contents: read` and `actions: read` permissions;
- has no `workflow_dispatch`, schedule, or pull-request trigger;
- checks out exact merged `main` with full history;
- requires local HEAD to equal `origin/main`;
- installs the frozen EXP-056 runtime without editable installation;
- proves the checkout remains clean after dependency installation;
- invokes only `python scripts/phase8a_exp056_operator.py next`;
- writes plan output only under `RUNNER_TEMP`;
- persists the read-only plan as an immutable artifact.

## Required proof

A successful DEC-216 plan must report:

- `operator_decision = DEC-215`;
- `read_only = true`;
- no existing EXP-056 manual-main model run;
- `run_state = MISSING`;
- no run id;
- stage `FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- the exact frozen EXP-056 dispatch command as plan evidence only.

The four bounded DEC-214 historical-run fields must remain true in the read-only plan:

- model-run dispatch authorization;
- authoritative model-result execution authorization;
- model-protocol result authorization;
- model-fit authorization.

The following must remain false:

- replacement model run;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Prohibited actions

DEC-216 must not:

- invoke `advance`;
- invoke `advance --execute`;
- call `gh workflow run` directly;
- call a workflow-dispatch REST endpoint;
- rerun or retry a model workflow;
- create a replacement run;
- claim a model result.

DEC-216 consumes no historical slot.

## Focused tests

Focused runner tests:

`tests/test_phase8a_exp056_operator_plan_runner.py`

Git blob:

`1c864a53dcbadd7d87f28f96f060a5963e3c4e78`

They pin main-push scope, read-only permissions, exact EXP-056 operator source path, `next`-only execution, clean-worktree behavior, exact plan identity fields, immutable plan persistence, and downstream locks.

## Next gate

Only after this workflow succeeds on merged `main` and its exact non-expired artifact is independently bound may a later separate one-shot executor source be considered.

DEC-216 itself does not dispatch the EXP-056 model workflow.
