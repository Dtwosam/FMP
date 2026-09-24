# Phase 8A — EXP-051 Read-Only Operator Plan Runner Environment Repair

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY REPAIR; NO EXP-051 DISPATCH
**Decision:** DEC-158
**Experiment:** EXP-20260924-051

## 1. Triggering evidence

DEC-157 merged at:

`c80e1224cd092539cb904c1f58bdeb8b072aed63`

Its automatic read-only plan run was:

`36064683930`

The runner passed:

- exact merged-main checkout;
- push/main identity checks;
- Python setup;
- pinned runtime installation.

The exact DEC-156 `next` invocation then failed closed with:

`ValueError: EXP-051 dispatch requires a clean working tree`

No EXP-051 model workflow was dispatched and the DEC-155 single-run slot remained unconsumed.

## 2. Root cause

The DEC-157 runner installed the repository with:

`python -m pip install -r requirements/exp051-model-run.txt -e .`

Editable installation mutated the checkout with local package-install metadata before DEC-156 performed its independent clean-worktree validation.

The operator behaved correctly by rejecting that environment.

## 3. Repair

DEC-158 changes only the read-only runner environment.

The runner now exports:

`PYTHONPATH=${{ github.workspace }}/src`

and installs only the frozen external runtime:

`python -m pip install -r requirements/exp051-model-run.txt`

It does not install the repository in editable mode.

Before invoking DEC-156, it explicitly requires:

`test -z "$(git status --porcelain)"`

The DEC-156 operator then independently performs the same clean-worktree requirement through its own checkout gate.

## 4. Repaired runner identity

Workflow:

`.github/workflows/phase8a-exp051-operator-plan.yml`

Git blob:

`e1bf3a4db4804ec237638c5b87bf9fb99b2c5ed3`

The workflow trigger, permissions, clean-main checkout, exact `next` invocation, plan validation, and artifact persistence remain otherwise unchanged from DEC-157.

It still contains no:

- `workflow_dispatch`;
- schedule;
- pull-request trigger;
- `advance`;
- `advance --execute`;
- direct EXP-051 model-workflow dispatch command.

## 5. Focused test identity

Focused tests:

`tests/test_phase8a_exp051_operator_plan_runner.py`

Git blob:

`1534a732930036b4bf3a1ed120cf7338f85b873f`

The tests now additionally require:

- no editable repository installation;
- `PYTHONPATH` points to the frozen checkout's `src`;
- an explicit clean-worktree assertion after dependency installation.

## 6. Authorization state

DEC-158 changes no DEC-155 authorization flag.

It does not:

- dispatch EXP-051;
- consume the one-run slot;
- add a retry or replacement path;
- authorize promotion;
- authorize shadow/demo execution;
- authorize broker mutation;
- authorize live orders;
- authorize real-money action;
- authorize trading.

## 7. Next gate

After DEC-158 merges, its workflow-file change automatically triggers the repaired read-only plan runner.

That run must successfully produce a DEC-156 plan proving:

- `read_only = true`;
- no manual-main EXP-051 run exists;
- `run_state = MISSING`;
- stage `TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- exact frozen dispatch-command evidence;
- all downstream locks false.

Only after that exact plan is inspected may a separate executor decision be considered.
