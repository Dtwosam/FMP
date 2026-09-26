# Phase 8A — EXP-058 Repository-Hosted Read-Only Operator Plan

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED
**Decision:** DEC-238
**Experiment:** EXP-20260925-058

## Purpose

DEC-238 adds a repository-hosted read-only proof for the exact DEC-237 EXP-058 operator `next` plan.

It exists only to prove the live one-shot state on merged `main` before any separate executor source is considered.

## Frozen predecessor binding

DEC-238 binds merged DEC-237 commit:

`516d000897ee870b6b8d32ccc790494635e2533c`

Frozen operator source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_operator.py`

Git blob:

`ffda686bf6c632f3c13bfaed8eafb23e8e565795`

Public operator CLI:

`scripts/phase8a_exp058_operator.py`

Git blob:

`aca3a47d79a0c32ae6590db3019557bea6bb6e89`

## Read-only workflow

Workflow:

`.github/workflows/phase8a-exp058-operator-plan.yml`

Git blob:

`436364fbc003be335a9801ab2569f7a7ed7cbe50`

The workflow:

- runs only on pushes to `main` affecting this proof workflow, the EXP-058 operator CLI, or the EXP-058 operator source;
- grants only `contents: read` and `actions: read`;
- has no `workflow_dispatch`, schedule, or pull-request trigger;
- checks out exact merged `main` with full history;
- requires local HEAD to equal `origin/main`;
- installs the pinned EXP-058 runtime without editable installation;
- proves the checkout remains clean after dependency installation;
- invokes only `python scripts/phase8a_exp058_operator.py next`;
- writes plan output only under `RUNNER_TEMP`;
- persists the read-only plan as an immutable artifact.

## Required proof

A successful DEC-238 plan must report:

- `operator_decision = DEC-237`;
- `read_only = true`;
- no existing EXP-058 manual-main model run;
- `run_state = MISSING`;
- no run id;
- stage `FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- the exact frozen EXP-058 dispatch command as plan evidence only.

The four bounded DEC-236 historical-run fields must remain true in the read-only plan:

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

DEC-238 must not:

- invoke `advance`;
- invoke `advance --execute`;
- call `gh workflow run` directly;
- call a workflow-dispatch REST endpoint;
- rerun or retry a model workflow;
- create a replacement run;
- claim a model result.

DEC-238 consumes no historical slot.

## Focused tests

Focused runner tests:

`tests/test_phase8a_exp058_operator_plan_runner.py`

Git blob:

`ab97b2c61170e9947f4942b6dccdfaa35263c0a1`

They pin main-push scope, read-only permissions, exact EXP-058 operator source path, `next`-only execution, clean-worktree behavior, exact plan identity fields, immutable plan persistence, and downstream locks.

## Next gate

Only after this workflow succeeds on merged `main` and its exact non-expired artifact is independently bound may a later separate one-shot executor source be considered.

DEC-238 itself does not dispatch the EXP-058 model workflow.
