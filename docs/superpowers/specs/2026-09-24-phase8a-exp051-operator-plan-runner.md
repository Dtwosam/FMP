# Phase 8A — EXP-051 Read-Only Operator Plan Runner

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY READ-ONLY RUNNER; NO EXP-051 DISPATCH
**Decision:** DEC-157
**Experiment:** EXP-20260924-051

## 1. Purpose

DEC-157 adds a read-only GitHub Actions runner that executes the exact merged DEC-156 operator `next` path on current `main`.

Its purpose is only to produce and persist the clean-main zero-run operator plan in an environment available to the repository when the user's local Desktop Commander device is offline.

DEC-157 does **not** dispatch EXP-051, call the operator `advance` path, or introduce any alternate model-run execution path.

## 2. Frozen predecessor chain

DEC-157 binds:

- DEC-155 one-run authorization merge: `a8b6204faccf411fd489ca5a1d004d90ed75be33`;
- DEC-156 operator merge: `609f440cb7d1689c9f2d42ae342db390d7d43bbc`;
- DEC-156 operator core blob: `de021a9cde4bd7c995ccb95e340df883c692d9dd`;
- DEC-156 public CLI blob: `bdf798e7db33917c3432f2e153c0eba563ab7ce3`;
- DEC-156 focused test blob: `47dc36184e3088322c1f983112781c3ec330d865`.

The underlying DEC-150 through DEC-155 source and authorization chain remains unchanged.

## 3. Runner identity

Workflow:

`.github/workflows/phase8a-exp051-operator-plan.yml`

Git blob:

`ede8d1a7e7e4f4bd2dcad643e354b606b8ecb925`

Workflow name:

`phase8a-exp051-operator-plan`

The runner is triggered only by a push to `main` that changes this workflow file.

It has:

- no `workflow_dispatch` trigger;
- no schedule;
- no pull-request trigger;
- read-only contents permission;
- read-only Actions permission.

The initial merge that introduces the workflow therefore causes exactly the intended read-only plan execution.

## 4. Exact clean-main checkout

The runner checks out:

- `ref: main`;
- full history with `fetch-depth: 0`.

Before running the operator it requires:

- event `push`;
- ref `refs/heads/main`;
- local branch exactly `main`;
- local HEAD exactly equal to `origin/main`.

The DEC-156 operator independently repeats its own clean-main validation, including origin identity and clean worktree.

## 5. Exact operator invocation

The runner executes only:

`python scripts/phase8a_exp051_operator.py next`

and persists stdout to:

`operator-plan.json`

It contains no call to:

- `advance`;
- `advance --execute`;
- `gh workflow run phase8a-exp051-temporal-calibrated-utility-model-training.yml`.

Therefore DEC-157 cannot submit the historical model workflow.

## 6. Required zero-run plan

The runner succeeds only when the persisted DEC-156 plan proves:

- `operator_decision = DEC-156`;
- `read_only = true`;
- `run_present = false`;
- `run_state = MISSING`;
- `run_id = null`;
- stage `TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- the exact frozen dispatch command is present as plan evidence.

It also requires the four outer DEC-155 historical-run flags to be true in the plan:

- run dispatch authorized;
- authoritative result execution authorized;
- protocol result authorized;
- model fit authorized.

## 7. Downstream locks

The runner requires all of the following to remain false:

- replacement model-run authorization;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

Any drift fails the read-only runner.

## 8. Plan artifact

A successful run persists the exact operator plan as:

`exp051-dec156-read-only-operator-plan-<commit>`

containing:

`operator-plan.json`

The artifact is evidence of the plan observed at that exact merged-main commit only.

It is not itself dispatch authorization beyond the already merged DEC-155 source authorization.

## 9. Numerical runtime

The runner uses:

- Python 3.12.14;
- `requirements/exp051-model-run.txt`;
- editable installation of the repository.

This is the same pinned runtime already frozen for EXP-051.

## 10. Focused tests

Focused tests:

`tests/test_phase8a_exp051_operator_plan_runner.py`

Git blob:

`0ba4ee0d163d2e5611baa7fa91974f82e9dcf384`

They verify:

- main-push/path-only scope;
- absence of manual, scheduled, or PR triggers;
- exact `next` invocation;
- absence of `advance`, `advance --execute`, and direct model-workflow dispatch;
- clean-main checkout checks;
- pinned Python/runtime;
- persisted plan artifact;
- downstream lock inventory.

## 11. Authorization state

DEC-157 changes no model-run authorization flags.

It does not:

- dispatch EXP-051;
- consume the DEC-155 slot;
- authorize a retry or replacement;
- authorize promotion or any trading path.

## 12. Next gate

After DEC-157 merges, its automatic read-only run must complete successfully and the persisted/operator-log plan must be inspected.

Only if that exact plan proves the DEC-156 `MISSING` / `RUN_DISPATCH_REQUIRED` state may a separate later decision define an environment-specific executor that invokes the existing DEC-156 `advance --execute` path without bypassing it.

That later executor must not contain an independent direct model-workflow dispatch path.
