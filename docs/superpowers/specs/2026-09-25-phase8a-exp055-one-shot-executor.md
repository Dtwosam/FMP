# Phase 8A — EXP-055 One-Shot Operator Executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; EXECUTES ONLY THROUGH DEC-204
**Decision:** DEC-206
**Experiment:** EXP-20260925-055

## Triggering read-only proof

DEC-205 merged at:

`e91594cec316412336e04361b6032a09229af0ab`

Read-only plan run:

`36162871611`

completed successfully on attempt 1 and proved:

- `operator_decision = DEC-204`;
- `read_only = true`;
- no manual-main EXP-055 run present;
- `run_state = MISSING`;
- stage `FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- exact DEC-204 frozen dispatch command present only as plan evidence;
- the bounded DEC-203 historical-run fields true;
- replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

Persisted plan artifact:

- artifact id: `10875772980`
- name: `exp055-dec204-read-only-operator-plan-e91594cec316412336e04361b6032a09229af0ab`
- digest: `sha256:16b6f8e573b30873d4b4599da6d5bda1b12eacbb06fc322e9659e474662d0f75`
- expired: false

## Purpose

DEC-206 adds exactly one repository-hosted executor whose sole execution-capable action is:

`python scripts/phase8a_exp055_operator.py advance --execute`

The executor contains no independent direct dispatch command or model-workflow dispatch REST endpoint.

All live dispatch authority, clean-main validation, zero-run selection, double planning, and frozen command validation remain inside DEC-204.

## Executor identity

Workflow:

`.github/workflows/phase8a-exp055-operator-execute.yml`

Git blob:

`ca9e6e06a945fc6e2866ea1ea85532767fecd155`

Workflow name:

`phase8a-exp055-operator-execute`

It triggers only when this executor workflow file itself is introduced or changed on `main`. There is no manual dispatch, schedule, or pull-request trigger. The initial DEC-206 merge therefore causes at most one intended executor attempt.

Focused tests:

`tests/test_phase8a_exp055_operator_executor.py`

Git blob:

`9f43afacf5a10be00c4220a4b439e34cf0929e52`

## Frozen read-only proof binding

Before execution, DEC-206 independently fetches and verifies exact run `36162871611`:

- exact workflow name/path;
- push event;
- branch `main`;
- head SHA `e91594cec316412336e04361b6032a09229af0ab`;
- completed success;
- attempt 1.

It also requires exact non-expired plan artifact id/name/digest above.

This historical proof does not replace DEC-204's live double-plan check.

## Exact execution path

The only action capable of causing model dispatch is:

`python scripts/phase8a_exp055_operator.py advance --execute`

DEC-204 obtains a fresh `next` plan, validates clean current main and zero-run state, derives the frozen command, obtains a second independent `next` plan, requires structured equality and command equality, and dispatches only if every check still passes.

If any EXP-055 manual-main run appears before either plan, execution fails closed.

## No independent dispatch path

DEC-206 source contains no direct model-workflow `gh workflow run` command, no model-workflow dispatch REST endpoint, no rerun command, no retry command, and no replacement path.

## Execution receipt

DEC-204 stdout is written outside the checkout to `$RUNNER_TEMP/operator-execution.json`.

DEC-206 accepts the step only if the receipt proves:

- `operator_decision = DEC-204`;
- explicit execution requested;
- dispatchable true;
- dispatch submitted true;
- result claimed false;
- original run state `MISSING`;
- original stage `FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- all downstream replacement/trading locks false.

The receipt is uploaded as:

`exp055-dec204-operator-execution-receipt-<executor-commit>`

A successful receipt proves only that dispatch was submitted. It does not claim a model result.

## First-attempt semantics

The EXP-055 model workflow retains the DEC-203 first-run rejection guard.

The first manual-main attempt consumes the slot regardless of success, failure, cancellation, or timeout.

DEC-206 authorizes no second executor attempt and no replacement model run.

Any terminal model-run evidence must route through DEC-202.

## Authorization boundary

Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain false.

## Next gate

After DEC-206 merges, its executor workflow runs automatically once.

If DEC-204 submits the model workflow, that manual-main EXP-055 run becomes the consumed DEC-203 attempt 1 and must be observed to terminal state without rerun.

The terminal run must then be reviewed through DEC-202 before any result disposition is recorded.
