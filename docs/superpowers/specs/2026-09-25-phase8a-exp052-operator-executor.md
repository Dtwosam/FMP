# Phase 8A — EXP-052 One-Shot Operator Executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; EXECUTES ONLY THROUGH DEC-169
**Decision:** DEC-171
**Experiment:** EXP-20260925-052

## Triggering evidence

DEC-170 merged at:

`07afb1194442320f730e53b5c5d5825b053ee1a5`

Its automatic read-only plan run:

`36114078121`

completed successfully on attempt 1 and proved:

- `operator_decision = DEC-169`;
- `read_only = true`;
- no manual-main EXP-052 run present;
- `run_state = MISSING`;
- stage `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- exact DEC-169 frozen dispatch command present as plan evidence;
- DEC-168 outer historical-run flags true;
- replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

Persisted plan artifact:

- artifact id: `10853944005`;
- name: `exp052-dec169-read-only-operator-plan-07afb1194442320f730e53b5c5d5825b053ee1a5`;
- digest: `sha256:1059a88f7e8cf00f965974edb3d3be203f5501a67ec8966068ac1ab9e348fcb9`;
- expired: false.

## Purpose

DEC-171 adds exactly one repository-hosted executor whose sole execution action is:

`python scripts/phase8a_exp052_operator.py advance --execute`

The executor contains no independent direct dispatch command or REST dispatch endpoint for the historical EXP-052 model workflow.

All live dispatch authority, clean-main validation, zero-run selection, double planning, and frozen command validation remain inside DEC-169.

## Executor identity

Workflow:

`.github/workflows/phase8a-exp052-operator-execute.yml`

Git blob:

`f31c5e5cfab8d00fe3e4ed6c86d92fcf87b36fff`

Workflow name:

`phase8a-exp052-operator-execute`

It triggers only when this executor workflow file itself is introduced or changed on `main`.

There is no manual dispatch, schedule, or pull-request trigger. The initial DEC-171 merge therefore causes the one intended executor attempt.

## Permissions and immutable runtime

The executor has `contents: read` and `actions: write`.

Actions write is required only because DEC-169 internally submits the already frozen EXP-052 historical model workflow.

The executor checks out exact `main`, uses Python 3.12.14, sets `PYTHONPATH=${{ github.workspace }}/src`, installs only `requirements/exp052-model-run.txt` without editable installation, and requires a clean worktree after dependency installation.

All temporary plan/receipt material is written under `RUNNER_TEMP`.

## Frozen read-only proof binding

Before execution, DEC-171 independently fetches and verifies exact run `36114078121`.

It requires exact workflow name/path, push event, branch `main`, head SHA `07afb1194442320f730e53b5c5d5825b053ee1a5`, completed success, and attempt 1.

It also requires the exact non-expired plan artifact id/name/digest:

`10853944005`

`exp052-dec169-read-only-operator-plan-07afb1194442320f730e53b5c5d5825b053ee1a5`

`sha256:1059a88f7e8cf00f965974edb3d3be203f5501a67ec8966068ac1ab9e348fcb9`

This historical proof does not replace DEC-169's live double-plan check.

## Exact execution path

The only action capable of causing model dispatch is:

`python scripts/phase8a_exp052_operator.py advance --execute`

DEC-169 then obtains a fresh `next` plan, validates zero-run state, derives the frozen command, obtains a second independent `next` plan, requires parsed-plan equality and command equality, and dispatches only if all checks still pass.

If any EXP-052 manual-main run appears before either plan, execution fails closed.

## No independent dispatch path

DEC-171 source contains no direct `gh workflow run phase8a-exp052-fit-temporal-support-utility-model-training.yml`, no model-workflow dispatch REST endpoint, no rerun command, no retry command, and no replacement-run path.

## Execution receipt

DEC-169 stdout is written outside the checkout to:

`$RUNNER_TEMP/operator-execution.json`

DEC-171 accepts the executor step only if the receipt proves:

- `operator_decision = DEC-169`;
- `advance_execute_requested = true`;
- `advance_dispatchable = true`;
- `dispatch_submitted = true`;
- `result_claimed = false`;
- original live state `MISSING`;
- original stage `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

The receipt is uploaded as:

`exp052-dec169-operator-execution-receipt-<executor-commit>`

A successful receipt proves only that dispatch was submitted. It does not claim a model result.

## First-attempt semantics

The EXP-052 workflow still contains the DEC-168 first-run rejection guard.

The first manual-main attempt consumes the slot regardless of success, failure, cancellation, or timeout.

DEC-171 authorizes no second executor attempt and no replacement run.

Any terminal model-run evidence must route through DEC-167.

## Focused tests

Focused tests:

`tests/test_phase8a_exp052_operator_executor.py`

Git blob:

`2c06ee1be92e2e6ba5d108bbcf11e07ed96fe2c8`

They verify one-time main-push/path scope, exact DEC-169 execution use, absence of direct dispatch/rerun paths, exact plan evidence bindings, immutable checkout/runtime, dispatch-only receipt semantics, downstream locks, and receipt persistence outside the checkout.

## Next gate

After DEC-171 merges, the executor workflow automatically runs once.

If DEC-169 submits the model workflow, that resulting manual-main EXP-052 run becomes the consumed DEC-168 attempt 1 and must be observed to terminal state without rerun.

The terminal run must then be reviewed through DEC-167 and, on success, its complete aggregate evidence must revalidate through DEC-165 before any result disposition is recorded.
