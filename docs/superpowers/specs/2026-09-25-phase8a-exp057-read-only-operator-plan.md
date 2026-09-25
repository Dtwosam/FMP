# Phase 8A — EXP-057 Repository-Hosted Read-Only Operator Plan

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED
**Decision:** DEC-227
**Experiment:** EXP-20260925-057

## Purpose

DEC-227 adds a repository-hosted read-only proof for the exact DEC-226 EXP-057 operator `next` plan.

It exists only to prove the live one-shot state on merged `main` before any separate executor source is considered.

## Frozen predecessor binding

DEC-227 binds merged DEC-226 commit:

`158afdc948ca5bdbb985bcc313ba420aa9da48fa`

Frozen operator source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_operator.py`

Git blob:

`58d0002e4d74a75fec77d3074249e505857b8603`

Public operator CLI:

`scripts/phase8a_exp057_operator.py`

Git blob:

`2ba08d3f4411a84ff3708cc338d26f3d90bbaad4`

## Read-only workflow

Workflow:

`.github/workflows/phase8a-exp057-operator-plan.yml`

Git blob:

`c69af21d6d2c6c3b4ba0412a9668dd1f0d0a20ad`

The workflow:

- runs only on pushes to `main` affecting this proof workflow, the EXP-057 operator CLI, or the repaired EXP-057 operator source;
- grants only `contents: read` and `actions: read`;
- has no `workflow_dispatch`, schedule, or pull-request trigger;
- checks out exact merged `main` with full history;
- requires local HEAD to equal `origin/main`;
- installs the frozen EXP-057 runtime without editable installation;
- proves the checkout remains clean after dependency installation;
- invokes only `python scripts/phase8a_exp057_operator.py next`;
- writes plan output only under `RUNNER_TEMP`;
- persists the read-only plan as an immutable artifact.

## Required proof

A successful DEC-227 plan must report:

- `operator_decision = DEC-226`;
- `read_only = true`;
- no existing EXP-057 manual-main model run;
- `run_state = MISSING`;
- no run id;
- stage `FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RUN_DISPATCH_REQUIRED`;
- the exact frozen EXP-057 dispatch command as plan evidence only.

The four bounded DEC-225 historical-run fields must remain true in the read-only plan:

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

DEC-227 must not:

- invoke `advance`;
- invoke `advance --execute`;
- call `gh workflow run` directly;
- call a workflow-dispatch REST endpoint;
- rerun or retry a model workflow;
- create a replacement run;
- claim a model result.

DEC-227 consumes no historical slot.

## Focused tests

Focused runner tests:

`tests/test_phase8a_exp057_operator_plan_runner.py`

Git blob:

`0d88c76dd6023c9f147068b7bdd512e085441b3f`

They pin main-push scope, read-only permissions, exact repaired EXP-057 operator source path, `next`-only execution, clean-worktree behavior, exact plan identity fields, immutable plan persistence, and downstream locks.

## Next gate

Only after this workflow succeeds on merged `main` and its exact non-expired artifact is independently bound may a later separate one-shot executor source be considered.

DEC-227 itself does not dispatch the EXP-057 model workflow.
