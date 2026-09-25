# Phase 8A — EXP-055 Repository-Hosted Read-Only Plan Runner

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED
**Decision:** DEC-205
**Experiment:** EXP-20260925-055

## Purpose

DEC-205 binds merged DEC-204 and adds a repository-hosted GitHub Actions proof for the exact read-only EXP-055 operator plan.

The runner exists only to prove that merged current main still sees the EXP-055 workflow as `MISSING` and derives the one DEC-203-authorized dispatch command without executing it.

## Frozen predecessor binding

DEC-205 binds DEC-204 merge:

`a4a7ff734846f6444f34dcde762f41578b0cf38b`

The runner invokes only:

`python scripts/phase8a_exp055_operator.py next`

It never invokes `advance` or `advance --execute`.

## Trigger and permissions

Workflow:

`.github/workflows/phase8a-exp055-operator-plan.yml`

Git blob:

`43f7c06aee4d551abc9e098186c8d1d75b740828`

Workflow name:

`phase8a-exp055-operator-plan`

It triggers only on a push to `main` that changes:

- the plan workflow itself;
- the public EXP-055 operator CLI;
- the EXP-055 operator library.

There is no manual dispatch, schedule, or pull-request trigger.

Permissions are limited to:

- `contents: read`
- `actions: read`

There is no Actions write permission.

## Clean-main proof

The runner checks out exact `main` with full history and requires:

- event `push`;
- ref `refs/heads/main`;
- local branch `main`;
- local HEAD exactly equals `origin/main`.

It installs the pinned EXP-055 numerical runtime without editable installation and then proves the checkout remains clean.

Plan output is written only to `RUNNER_TEMP`, not into the repository checkout.

## Required plan state

The runner accepts only a plan proving:

- `operator_decision = DEC-204`;
- `read_only = true`;
- `run_present = false`;
- `run_state = MISSING`;
- `run_id = null`;
- stage `FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- the exact frozen dispatch command appears only as plan evidence;
- model-run dispatch, historical-result execution, model-protocol result production, and model fit are true within the bounded DEC-203 slot;
- replacement, promotion, shadow/demo, broker mutation, live orders, real-money action, and trading remain false.

## No dispatch path

The runner source contains no call to:

- `phase8a_exp055_operator.py advance`;
- `advance --execute`;
- a direct model-workflow dispatch command;
- a rerun or retry endpoint.

The frozen dispatch command may appear only inside the plan assertion as expected read-only data.

## Persisted evidence

A successful proof uploads:

`exp055-dec204-read-only-operator-plan-<merged-main-sha>`

containing the immutable `operator-plan.json`.

Focused tests:

`tests/test_phase8a_exp055_operator_plan_runner.py`

Git blob:

`3b934e99e0b499946fb4372b27eaf3cdc06851c3`

## Authorization boundary

DEC-205 changes no authorization.

It does not dispatch the historical model workflow and does not consume the DEC-203 slot.

Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.

## Next gate

Only after the merged-main DEC-205 proof succeeds may a separate one-shot executor source be considered.

That executor must independently bind the successful read-only run and artifact and must still rely on DEC-204's fresh double-plan zero-run check immediately before any dispatch.
