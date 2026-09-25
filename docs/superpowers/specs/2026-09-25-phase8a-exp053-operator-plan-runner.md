# Phase 8A — EXP-053 Read-Only Operator Plan Runner

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY READ-ONLY RUNNER; NO EXP-053 DISPATCH
**Decision:** DEC-181
**Experiment:** EXP-20260925-053

## Purpose

DEC-181 adds a read-only GitHub Actions runner that executes the exact merged DEC-180 operator `next` path on current `main`.

It exists only to produce and persist the clean-main zero-run operator plan in a repository-hosted environment. It does not dispatch EXP-053, call `advance`, call `advance --execute`, or introduce an alternate execution path.

## Frozen predecessor chain

DEC-181 binds:

- DEC-179 one-run authorization merge: `7711a726cde6fc3e827259bf9f8a0878e28eb5b4`;
- DEC-180 operator merge: `459cca3f046c7bc143941bb0d42e4810ad3625dd`;
- DEC-180 operator core blob: `47455c4be8cae5e65c2157000c05f514d551ad32`;
- DEC-180 public CLI blob: `04bad97e1c9b215b7ac8b699ddc2cb6c329331b3`;
- DEC-180 focused test blob: `685feea42865fc198ce70fb27dcce0903673b79b`.

The underlying DEC-174 through DEC-179 source and authorization chain remains unchanged.

## Runner identity

Workflow:

`.github/workflows/phase8a-exp053-operator-plan.yml`

Git blob:

`ae9fac8c80758a81773f865077ad6c3e15640645`

Workflow name:

`phase8a-exp053-operator-plan`

The runner triggers only on a push to `main` that changes this workflow file. It has no `workflow_dispatch`, schedule, or pull-request trigger and only read-only contents/Actions permissions.

## Clean-worktree environment

The runner checks out exact current `main` with full history, requires push/main identity, sets `PYTHONPATH=${{ github.workspace }}/src`, and installs only:

`python -m pip install -r requirements/exp053-model-run.txt`

It does not use editable installation.

It then requires an empty porcelain status.

Plan output is written outside the checkout at:

`$RUNNER_TEMP/operator-plan.json`

so DEC-180's independent clean-worktree check remains valid.

## Exact operator invocation

The only operator command is:

`python scripts/phase8a_exp053_operator.py next`

The runner contains no call to `advance`, `advance --execute`, or direct model-workflow dispatch.

## Required zero-run plan

The runner succeeds only when the persisted DEC-180 plan proves:

- `operator_decision = DEC-180`;
- `read_only = true`;
- `run_present = false`;
- `run_state = MISSING`;
- `run_id = null`;
- stage `FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- the exact frozen EXP-053 dispatch command is present only as plan evidence.

It requires the four DEC-179 outer historical-run flags true while replacement/promotion/shadow/demo/broker/live/real-money/trading locks remain false.

## Plan artifact

A successful run persists:

`exp053-dec180-read-only-operator-plan-<commit>`

containing `operator-plan.json`.

The artifact proves only the observed plan at that exact merged-main commit. It does not dispatch or add authorization.

## Focused tests

Focused tests:

`tests/test_phase8a_exp053_operator_plan_runner.py`

Git blob:

`433744641b5767242404e85b09000bee15665aab`

They verify main-push/path-only scope, absence of manual/scheduled/PR triggers, exact `next` invocation, absence of execution paths, non-editable dependency installation, external output, clean-main checks, and downstream locks.

## Authorization state

DEC-181 changes no model-run authorization. It does not dispatch EXP-053, consume the DEC-179 slot, authorize retry/replacement, or authorize promotion/trading.

## Next gate

After DEC-181 merges, its automatic read-only run must succeed and its persisted plan must be inspected.

Only if that exact plan proves DEC-180 `MISSING / RUN_DISPATCH_REQUIRED` may a separate later decision define a one-shot executor whose only execution action invokes the existing DEC-180 `advance --execute` path.

That executor must not contain an independent direct model-workflow dispatch path.
