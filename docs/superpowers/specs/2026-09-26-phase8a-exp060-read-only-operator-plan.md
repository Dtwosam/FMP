# Phase 8A — EXP-060 Repository-Hosted Read-Only Operator Plan

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED
**Decision:** DEC-260
**Experiment:** EXP-20260926-060

## Purpose

DEC-260 adds a repository-hosted read-only proof for the exact DEC-259 EXP-060 operator `next` plan.

It exists only to prove the live one-shot state on merged `main` before any separate executor source is considered.

## Frozen predecessor binding

DEC-260 binds merged DEC-259 commit:

`cf2efadd1bbf457eb20357dfa74d6c2ea7278823`

Frozen operator source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_operator.py`

Git blob:

`54f1c5c7d856eb4bf0eb5366cf43ae38a3f25d2c`

Public operator CLI:

`scripts/phase8a_exp060_operator.py`

Git blob:

`16c553d2dc959fe1e24796a95019163d1967e836`

## Read-only workflow

Workflow:

`.github/workflows/phase8a-exp060-operator-plan.yml`

Git blob:

`88ee067dfcf77dd7d6c2456d3b202c12aaa76dda`

The workflow:

- runs only on pushes to `main` affecting this proof workflow, the EXP-060 operator CLI, or the EXP-060 operator source;
- grants only `contents: read` and `actions: read`;
- has no `workflow_dispatch`, schedule, or pull-request trigger;
- checks out exact merged `main` with full history;
- requires local HEAD to equal `origin/main`;
- installs the frozen EXP-060 runtime without editable installation;
- proves the checkout remains clean after dependency installation;
- invokes only `python scripts/phase8a_exp060_operator.py next`;
- writes plan output only under `RUNNER_TEMP`;
- persists the read-only plan as an immutable artifact.

## Required proof

A successful DEC-260 plan must report:

- `operator_decision = DEC-259`;
- `read_only = true`;
- no existing EXP-060 manual-main model run;
- `run_state = MISSING`;
- no run id;
- stage `FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_MODEL_RUN_DISPATCH_REQUIRED`;
- the exact frozen EXP-060 dispatch command as plan evidence only.

The four bounded DEC-258 historical-run fields must remain true in the read-only plan:

- model-run dispatch authorization;
- authoritative repaired model-result execution authorization;
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

DEC-260 must not:

- invoke `advance`;
- invoke `advance --execute`;
- call `gh workflow run` directly;
- call a workflow-dispatch REST endpoint;
- rerun or retry a model workflow;
- create a replacement run;
- claim a model result.

DEC-260 consumes no historical slot.

## Focused tests

Focused runner tests:

`tests/test_phase8a_exp060_operator_plan_runner.py`

Git blob:

`b1df3c05ba69e2e2afdde8d8fd43d4588d75bb30`

They pin main-push scope, read-only permissions, exact EXP-060 operator source path, `next`-only execution, clean-worktree behavior, exact plan identity fields, immutable plan persistence, and downstream locks.

## Next gate

Only after this workflow succeeds on merged `main` and its exact non-expired artifact is independently bound may a later separate one-shot executor source be considered.

DEC-260 itself does not dispatch the EXP-060 model workflow.
