# Phase 8A — EXP-052 Read-Only Operator Plan Runner

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY READ-ONLY RUNNER; NO EXP-052 DISPATCH
**Decision:** DEC-170
**Experiment:** EXP-20260925-052

## Purpose

DEC-170 adds a read-only GitHub Actions runner that executes the exact merged DEC-169 operator `next` path on current `main`.

Its only purpose is to produce and persist the clean-main zero-run operator plan in a repository-hosted environment.

DEC-170 does **not** dispatch EXP-052, call the operator `advance` path, or introduce any alternate model-run execution path.

## Frozen predecessor chain

DEC-170 binds:

- DEC-168 one-run authorization merge: `673b96906002b898dd09ff913a0efe6b9be369e3`;
- DEC-169 operator merge: `6288eea1308186db20202e5662ca1665b17f65f6`;
- DEC-169 operator core blob: `9e57fa87215d8e7ca373d226f8e2fec873a0fd10`;
- DEC-169 public CLI blob: `1c4c212e3bcc16c1e241efeb9ef5986d0bc5b24d`;
- DEC-169 focused test blob: `9550f0126c4fe959d0ad979a096c03bcbc9f0199`.

The underlying DEC-163 through DEC-168 source and authorization chain remains unchanged.

## Runner identity

Workflow:

`.github/workflows/phase8a-exp052-operator-plan.yml`

Git blob:

`12f1d64b0cd97897864d90ef5f914d296e2788c2`

Workflow name:

`phase8a-exp052-operator-plan`

The runner is triggered only by a push to `main` that changes this workflow file.

It has no `workflow_dispatch` trigger, no schedule, no pull-request trigger, and only read-only contents/Actions permissions.

The initial merge therefore causes exactly one intended read-only plan execution.

## Clean-worktree environment

The runner checks out current `main` with full history and requires exact push/main identity.

It sets:

`PYTHONPATH=${{ github.workspace }}/src`

It installs only:

`python -m pip install -r requirements/exp052-model-run.txt`

It does not use editable installation.

It then requires:

`test -z "$(git status --porcelain)"`

before invoking the operator.

Plan output is written outside the repository:

`$RUNNER_TEMP/operator-plan.json`

so the operator's independent clean-worktree preflight remains valid.

## Exact operator invocation

The runner executes only:

`python scripts/phase8a_exp052_operator.py next`

It contains no call to `advance`, `advance --execute`, or direct `gh workflow run phase8a-exp052-fit-temporal-support-utility-model-training.yml`.

Therefore DEC-170 cannot submit the historical model workflow.

## Required zero-run plan

The runner succeeds only when the persisted DEC-169 plan proves:

- `operator_decision = DEC-169`;
- `read_only = true`;
- `run_present = false`;
- `run_state = MISSING`;
- `run_id = null`;
- stage `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- the exact frozen dispatch command is present as plan evidence.

It also requires the four outer DEC-168 historical-run flags to be true in the plan and all replacement/promotion/shadow/demo/broker/live/real-money/trading locks to remain false.

## Plan artifact

A successful run persists:

`exp052-dec169-read-only-operator-plan-<commit>`

containing `operator-plan.json`.

The artifact is evidence of the plan observed at that exact merged-main commit only.

It does not itself dispatch or add authorization beyond DEC-168.

## Focused tests

Focused tests:

`tests/test_phase8a_exp052_operator_plan_runner.py`

Git blob:

`ec653df6782c5f442c94eb973b13759712a1cc5d`

They verify main-push/path-only scope, absence of manual/scheduled/PR triggers, exact `next` invocation, absence of execution paths, non-editable dependency installation, external `RUNNER_TEMP` output, clean-main checks, and downstream locks.

## Authorization state

DEC-170 changes no model-run authorization flags.

It does not dispatch EXP-052, consume the DEC-168 slot, authorize a retry/replacement, or authorize promotion/trading.

## Next gate

After DEC-170 merges, its automatic read-only run must complete successfully and the persisted plan must be inspected.

Only if that exact plan proves the DEC-169 `MISSING` / `RUN_DISPATCH_REQUIRED` state may a separate later decision define an environment-specific executor that invokes the existing DEC-169 `advance --execute` path without bypassing it.

That later executor must not contain an independent direct model-workflow dispatch path.
