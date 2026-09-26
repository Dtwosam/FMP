# Phase 8A — EXP-059 Repository-Hosted Read-Only Operator Plan

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED
**Decision:** DEC-249
**Experiment:** EXP-20260926-059

## Purpose

DEC-249 adds a repository-hosted read-only proof for the exact DEC-248 EXP-059 operator `next` plan.

It exists only to prove the live one-shot state on merged `main` before any separate executor source is considered.

## Frozen predecessor binding

DEC-249 binds merged DEC-248 commit:

`67942688e417debf413e63b99555743eea2122ff`

Frozen operator source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_operator.py`

Git blob:

`12a4fcce685e2136aea6a9d0e3e27ba39b320f1e`

Public operator CLI:

`scripts/phase8a_exp059_operator.py`

Git blob:

`720bab7054ecd55fd90a1ef6dbae8b00ceb5dabd`

## Read-only workflow

Workflow:

`.github/workflows/phase8a-exp059-operator-plan.yml`

Git blob:

`160b5aee27d63443862e32137e3b4fe75997d3d9`

The workflow:

- runs only on pushes to `main` affecting this proof workflow, the EXP-059 operator CLI, or the EXP-059 operator source;
- grants only `contents: read` and `actions: read`;
- has no `workflow_dispatch`, schedule, or pull-request trigger;
- checks out exact merged `main` with full history;
- requires local HEAD to equal `origin/main`;
- installs the frozen EXP-059 runtime without editable installation;
- proves the checkout remains clean after dependency installation;
- invokes only `python scripts/phase8a_exp059_operator.py next`;
- writes plan output only under `RUNNER_TEMP`;
- persists the read-only plan as an immutable artifact.

## Required proof

A successful DEC-249 plan must report:

- `operator_decision = DEC-248`;
- `read_only = true`;
- no existing EXP-059 manual-main model run;
- `run_state = MISSING`;
- no run id;
- stage `FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- the exact frozen EXP-059 dispatch command as plan evidence only.

The four bounded DEC-247 historical-run fields must remain true in the read-only plan:

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

DEC-249 must not:

- invoke `advance`;
- invoke `advance --execute`;
- call `gh workflow run` directly;
- call a workflow-dispatch REST endpoint;
- rerun or retry a model workflow;
- create a replacement run;
- claim a model result.

DEC-249 consumes no historical slot.

## Focused tests

Focused runner tests:

`tests/test_phase8a_exp059_operator_plan_runner.py`

Git blob:

`05766f40bbe9fbda01f96fa1eb5d4acef3c5f443`

They pin main-push scope, read-only permissions, exact EXP-059 operator source path, `next`-only execution, clean-worktree behavior, exact plan identity fields, immutable plan persistence, and downstream locks.

## Next gate

Only after this workflow succeeds on merged `main` and its exact non-expired artifact is independently bound may a later separate one-shot executor source be considered.

DEC-249 itself does not dispatch the EXP-059 model workflow.
