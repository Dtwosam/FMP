# Phase 8A — EXP-053 One-Shot Operator Executor

**Date:** 2026-09-25
**Status:** APPROVED SOURCE; EXECUTES ONLY THROUGH DEC-180
**Decision:** DEC-182
**Experiment:** EXP-20260925-053

## Triggering evidence

DEC-181 merged at:

`7e5d042ab7cc46c18de0f72bd4302ec9dd676e84`

Its automatic read-only plan run:

`36126977702`

completed successfully on attempt 1 and proved:

- `operator_decision = DEC-180`;
- `read_only = true`;
- no manual-main EXP-053 run present;
- `run_state = MISSING`;
- stage `FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- exact DEC-180 frozen dispatch command present as plan evidence;
- DEC-179 outer historical-run flags true;
- replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

Persisted plan artifact:

- artifact id: `10860591486`;
- name: `exp053-dec180-read-only-operator-plan-7e5d042ab7cc46c18de0f72bd4302ec9dd676e84`;
- digest: `sha256:9ca87fe6ec7c0ff8193ee4eef943e82053721c3fd762e5e69d7fa711471f6066`;
- expired: false.

The downloaded artifact contains exactly one `operator-plan.json` and reproduces the exact zero-run state above.

## Purpose

DEC-182 adds exactly one repository-hosted executor whose sole execution action is:

`python scripts/phase8a_exp053_operator.py advance --execute`

The executor contains no independent direct dispatch command or REST dispatch endpoint for the historical EXP-053 model workflow.

All live dispatch authority, clean-main validation, zero-run selection, double planning, and frozen command validation remain inside DEC-180.

## Executor identity

Workflow:

`.github/workflows/phase8a-exp053-operator-execute.yml`

Git blob:

`d02a17528436427a8906247480615c880f9724d9`

Workflow name:

`phase8a-exp053-operator-execute`

It triggers only when this executor workflow file itself is introduced or changed on `main`.

There is no manual dispatch, schedule, or pull-request trigger. The initial DEC-182 merge therefore causes the one intended executor attempt.

## Permissions and immutable runtime

The executor has `contents: read` and `actions: write`.

Actions write is required only because DEC-180 internally submits the already frozen EXP-053 historical model workflow.

The executor checks out exact `main`, uses Python 3.12.14, sets `PYTHONPATH=${{ github.workspace }}/src`, installs only `requirements/exp053-model-run.txt` without editable installation, and requires a clean worktree after dependency installation.

All temporary plan/receipt material is written under `RUNNER_TEMP`.

## Frozen read-only proof binding

Before execution, DEC-182 independently fetches and verifies exact run `36126977702`.

It requires exact workflow name/path, push event, branch `main`, head SHA `7e5d042ab7cc46c18de0f72bd4302ec9dd676e84`, completed success, and attempt 1.

It also requires the exact non-expired plan artifact id/name/digest:

`10860591486`

`exp053-dec180-read-only-operator-plan-7e5d042ab7cc46c18de0f72bd4302ec9dd676e84`

`sha256:9ca87fe6ec7c0ff8193ee4eef943e82053721c3fd762e5e69d7fa711471f6066`

This historical proof does not replace DEC-180's live double-plan check.

## Exact execution path

The only action capable of causing model dispatch is:

`python scripts/phase8a_exp053_operator.py advance --execute`

DEC-180 then obtains a fresh `next` plan, validates zero-run state, derives the frozen command, obtains a second independent `next` plan, requires parsed-plan equality and command equality, and dispatches only if all checks still pass.

If any EXP-053 manual-main run appears before either plan, execution fails closed.

## No independent dispatch path

DEC-182 source contains no direct `gh workflow run phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml`, no model-workflow dispatch REST endpoint, no rerun command, no retry command, and no replacement-run path.

## Execution receipt

DEC-180 stdout is written outside the checkout to:

`$RUNNER_TEMP/operator-execution.json`

DEC-182 accepts the executor step only if the receipt proves:

- `operator_decision = DEC-180`;
- `advance_execute_requested = true`;
- `advance_dispatchable = true`;
- `dispatch_submitted = true`;
- `result_claimed = false`;
- original live state `MISSING`;
- original stage `FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

The receipt is uploaded as:

`exp053-dec180-operator-execution-receipt-<executor-commit>`

A successful receipt proves only that dispatch was submitted. It does not claim a model result.

## First-attempt semantics

The EXP-053 workflow still contains the DEC-179 first-run rejection guard.

The first manual-main attempt consumes the slot regardless of success, failure, cancellation, or timeout.

DEC-182 authorizes no second executor attempt and no replacement run.

Any terminal model-run evidence must route through DEC-178.

## Focused tests

Focused tests:

`tests/test_phase8a_exp053_operator_executor.py`

Git blob:

`7cb0ffefcffb50eade46e86780cc7a98c1db636b`

They verify one-time main-push/path scope, exact DEC-180 execution use, absence of direct dispatch/rerun/retry paths, exact plan evidence bindings, immutable checkout/runtime, dispatch-only receipt semantics, downstream locks, and receipt persistence outside the checkout.

## Next gate

After DEC-182 merges, the executor workflow automatically runs once.

If DEC-180 submits the model workflow, that resulting manual-main EXP-053 run becomes the consumed DEC-179 attempt 1 and must be observed to terminal state without rerun.

The terminal run must then be reviewed through DEC-178 and, on success, its complete aggregate evidence must revalidate through DEC-176 before any result disposition is recorded.
