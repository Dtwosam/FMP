# Phase 8A — EXP-054 One-Shot Operator Executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; EXECUTES ONLY THROUGH DEC-192
**Decision:** DEC-195
**Experiment:** EXP-20260925-054

## Triggering evidence

DEC-194 merged at:

`c4746803f116af2727bbbd73d5d58ed031b9adf8`

Corrected read-only plan run:

`36151472585`

completed successfully on attempt 1 and proved:

- `operator_decision = DEC-192`;
- `read_only = true`;
- no manual-main EXP-054 run present;
- `run_state = MISSING`;
- stage `FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- exact DEC-192 frozen dispatch command present only as plan evidence;
- the DEC-191 historical-run authorization fields true;
- replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

Persisted plan artifact:

- artifact id: `10871223861`;
- name: `exp054-dec192-read-only-operator-plan-c4746803f116af2727bbbd73d5d58ed031b9adf8`;
- digest: `sha256:83508d99b1fbf9be621ea309fa7012451977a0146a02cbba520b0edf9dab9c72`;
- expired: false.

## Purpose

DEC-195 adds exactly one repository-hosted executor whose sole execution-capable action is:

`python scripts/phase8a_exp054_operator.py advance --execute`

The executor contains no independent direct dispatch command or REST dispatch endpoint for the historical EXP-054 model workflow.

All live dispatch authority, clean-main validation, zero-run selection, double planning, and frozen command validation remain inside DEC-192.

## Executor identity

Workflow:

`.github/workflows/phase8a-exp054-operator-execute.yml`

Git blob:

`b051668d47c249fb42c3d27ecf5bdf9159f88279`

Workflow name:

`phase8a-exp054-operator-execute`

It triggers only when this executor workflow file itself is introduced or changed on `main`. There is no manual dispatch, schedule, or pull-request trigger. The initial DEC-195 merge therefore causes at most one intended executor attempt.

## Frozen read-only proof binding

Before execution, DEC-195 independently fetches and verifies exact run `36151472585`: exact workflow name/path, push event, branch `main`, head SHA `c4746803f116af2727bbbd73d5d58ed031b9adf8`, completed success, and attempt 1.

It also requires the exact non-expired plan artifact id/name/digest above. This historical proof does not replace DEC-192's live double-plan check.

## Exact execution path

The only action capable of causing model dispatch is:

`python scripts/phase8a_exp054_operator.py advance --execute`

DEC-192 obtains a fresh `next` plan, validates clean current main and zero-run state, derives the frozen command, obtains a second independent `next` plan, requires parsed-plan equality and command equality, and dispatches only if all checks still pass. If any EXP-054 manual-main run appears before either plan, execution fails closed.

## No independent dispatch path

DEC-195 source contains no direct model-workflow `gh workflow run` command, no model-workflow dispatch REST endpoint, no rerun command, no retry command, and no replacement-run path.

## Execution receipt

DEC-192 stdout is written outside the checkout to `$RUNNER_TEMP/operator-execution.json`. DEC-195 accepts the step only if the receipt proves `operator_decision = DEC-192`, explicit execution requested, dispatchable true, dispatch submitted true, result claimed false, original state `MISSING`, original stage `FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`, and all downstream replacement/trading locks false.

The receipt is uploaded as `exp054-dec192-operator-execution-receipt-<executor-commit>`. A successful receipt proves only that dispatch was submitted. It does not claim a model result.

## First-attempt semantics

The EXP-054 workflow retains the DEC-191 first-run rejection guard. The first manual-main attempt consumes the slot regardless of success, failure, cancellation, or timeout. DEC-195 authorizes no second executor attempt and no replacement run.

Any terminal model-run evidence must route through DEC-190.

## Focused tests

Focused tests:

`tests/test_phase8a_exp054_operator_executor.py`

Git blob:

`b0a2cfbe22e0162ea41b65a60d50bc882730efa3`

They verify one-time main-push/path scope, exact DEC-192 execution use, absence of direct dispatch/rerun/retry paths, exact plan evidence bindings, immutable checkout/runtime, dispatch-only receipt semantics, downstream locks, and receipt persistence outside the checkout.

## Next gate

After DEC-195 merges, the executor workflow automatically runs once. If DEC-192 submits the model workflow, that manual-main EXP-054 run becomes the consumed DEC-191 attempt 1 and must be observed to terminal state without rerun. The terminal run must then be reviewed through DEC-190 before any result disposition is recorded.
