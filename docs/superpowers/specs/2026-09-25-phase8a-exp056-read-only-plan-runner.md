# Phase 8A — EXP-056 Repository-Hosted Read-Only Plan Runner

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / READ-ONLY / NOT DISPATCHED
**Decision:** DEC-216
**Experiment:** EXP-20260925-056

## Purpose

DEC-216 adds a repository-hosted read-only proof for the exact DEC-215 `next` plan.

It exists to prove the live merged-main EXP-056 state is still `MISSING` before any one-shot executor is considered.

The runner cannot dispatch the EXP-056 model workflow.

## Frozen predecessor binding

DEC-216 binds DEC-215 merged commit:

`328a42ebe2248ca8200bf5d8f50d37fd28186d87`

The exact operator source/CLI remain those frozen by DEC-215.

## Trigger and permissions

Workflow:

`.github/workflows/phase8a-exp056-operator-plan.yml`

Git blob:

`921c4a93aa271b4db3816f8e4e2adb178a0a0318`

The workflow triggers only on `push` to `main` when the plan workflow, operator CLI, or operator source is introduced or changed.

It has:

- `contents: read`
- `actions: read`

It has no:

- manual dispatch trigger;
- schedule;
- pull-request trigger;
- write permission.

## Exact checkout proof

The runner:

1. checks out exact `main`;
2. fetches full history;
3. requires event `push`;
4. requires ref `refs/heads/main`;
5. requires local branch `main`;
6. requires local HEAD exactly equal `origin/main`.

## Runtime and worktree

Python is pinned to 3.12.14.

The runner installs only:

`requirements/exp056-model-run.txt`

without editable package installation.

It then requires:

`git status --porcelain`

to remain empty.

Plan output is written only under `RUNNER_TEMP`.

## Exact read-only action

The sole operator invocation is:

`python scripts/phase8a_exp056_operator.py next`

The runner contains no:

- `advance`;
- `advance --execute`;
- direct EXP-056 model-workflow dispatch command;
- rerun/retry/replacement action.

## Required zero-run plan

A successful plan must prove:

- `operator_decision = DEC-215`
- `read_only = true`
- `run_present = false`
- `run_state = MISSING`
- `run_id = null`
- stage `FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`
- exact frozen dispatch command present only as plan evidence
- four bounded DEC-214 historical-run fields true
- replacement/promotion/shadow/demo/broker/live/real-money/trading fields false

## Immutable proof artifact

The runner uploads:

`exp056-dec215-read-only-operator-plan-<merged-main-sha>`

containing only the plan JSON.

## Focused tests

Focused tests:

`tests/test_phase8a_exp056_operator_plan_runner.py`

Git blob:

`874549bd519c9412050230376effb8b954e3be0b`

## Authorization state

DEC-216 changes no authorization and consumes no historical slot.

It keeps false:

- replacement run;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

Only after the merged-main DEC-216 proof succeeds may a separate one-shot executor be considered.

That executor must independently bind the exact successful plan run/artifact and contain no direct model-workflow dispatch path outside DEC-215.
