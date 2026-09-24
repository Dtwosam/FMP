# Phase 8A — EXP-051 One-Shot Operator Executor

**Date:** 2026-09-24
**Status:** APPROVED SOURCE; EXECUTES ONLY THROUGH DEC-156
**Decision:** DEC-160
**Experiment:** EXP-20260924-051

## 1. Triggering evidence

DEC-159 merged at:

`a997808602ab3a9f4ca53982895c05cb0a358e67`

Its automatic read-only plan run was:

`36065565456`

That run completed successfully on attempt 1 and proved the exact merged DEC-156 operator state:

- `read_only = true`;
- no manual-main EXP-051 run present;
- `run_state = MISSING`;
- stage `TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- exact DEC-156 frozen dispatch command present as plan evidence;
- DEC-155 outer run/result/fit flags true;
- replacement/promotion/shadow/demo/broker/live/real-money/trading locks false.

The persisted plan artifact is:

- artifact id: `10835714803`;
- name: `exp051-dec156-read-only-operator-plan-a997808602ab3a9f4ca53982895c05cb0a358e67`;
- expired: false.

No EXP-051 historical model run existed at the time that plan was verified.

## 2. Purpose

DEC-160 adds exactly one repository-hosted executor whose sole execution action is:

`python scripts/phase8a_exp051_operator.py advance --execute`

The executor contains no independent direct dispatch command for the historical EXP-051 model workflow.

Therefore all live dispatch authority, clean-main validation, zero-run selection, double planning, and frozen command validation remain inside DEC-156.

## 3. Executor identity

Workflow:

`.github/workflows/phase8a-exp051-operator-execute.yml`

Git blob:

`0c93bdf44bfbe63b997d62f116f20de776873d06`

Workflow name:

`phase8a-exp051-operator-execute`

It triggers only when this executor workflow file itself is introduced or changed on `main`.

There is no:

- `workflow_dispatch`;
- schedule;
- pull-request trigger.

This means the initial DEC-160 merge causes the one intended executor attempt.

## 4. Permissions

The executor has:

- `contents: read`;
- `actions: write`.

Actions write permission is required only because the existing DEC-156 operator internally submits the already frozen EXP-051 historical model workflow.

The executor source itself does not embed the model-workflow dispatch command or dispatch REST endpoint.

## 5. Clean-main and immutable runtime

The executor:

1. checks out exact `main` with full history;
2. requires push event and `refs/heads/main`;
3. requires local branch `main`;
4. requires local HEAD equals `origin/main`;
5. uses Python 3.12.14;
6. installs only `requirements/exp051-model-run.txt`;
7. exports `PYTHONPATH=${{ github.workspace }}/src`;
8. requires a clean worktree after dependency installation.

All temporary evidence is written under `RUNNER_TEMP`, outside the Git checkout.

DEC-156 independently repeats its own clean-main and clean-worktree validation.

## 6. Frozen read-only proof binding

Before execution, DEC-160 independently fetches and verifies the exact successful DEC-159 plan run:

`36065565456`

It requires:

- workflow name `phase8a-exp051-operator-plan`;
- workflow path `.github/workflows/phase8a-exp051-operator-plan.yml`;
- event `push`;
- branch `main`;
- head SHA `a997808602ab3a9f4ca53982895c05cb0a358e67`;
- completed success;
- attempt 1.

It also requires exactly the frozen non-expired plan artifact id/name pair:

`10835714803`

`exp051-dec156-read-only-operator-plan-a997808602ab3a9f4ca53982895c05cb0a358e67`

This historical proof does not replace the live DEC-156 double-plan check.

## 7. Exact execution path

The only action capable of causing the model dispatch is:

`python scripts/phase8a_exp051_operator.py advance --execute`

DEC-156 then:

- obtains a fresh `next` plan;
- validates the live zero-run state;
- derives the frozen dispatch command;
- obtains a second independent `next` plan immediately before execution;
- requires the two parsed plans to be identical;
- requires the two derived commands to be identical;
- submits the frozen workflow command only if all checks pass.

If any EXP-051 manual-main run appears before either plan, execution fails closed.

## 8. No independent dispatch path

DEC-160 source contains no:

- `gh workflow run phase8a-exp051-temporal-calibrated-utility-model-training.yml`;
- model-workflow dispatch REST endpoint;
- rerun command;
- retry command;
- replacement-run path.

The executor cannot construct a second path around DEC-156.

## 9. Execution receipt

DEC-156 stdout is written outside the checkout to:

`$RUNNER_TEMP/operator-execution.json`

DEC-160 accepts the executor step only if the receipt proves:

- `operator_decision = DEC-156`;
- `advance_execute_requested = true`;
- `advance_dispatchable = true`;
- `dispatch_submitted = true`;
- `result_claimed = false`;
- original live state was `MISSING`;
- original stage was `TEMPORAL_CALIBRATED_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`;
- replacement/promotion/shadow/demo/broker/live/real-money/trading locks remain false.

The receipt is uploaded as:

`exp051-dec156-operator-execution-receipt-<executor-commit>`

A successful executor receipt proves only that a dispatch was submitted. It does not claim a model result.

## 10. First-attempt semantics remain DEC-155

The EXP-051 workflow itself still contains the DEC-155 first-run rejection guard.

The first manual-main attempt consumes the slot regardless of:

- success;
- failure;
- cancellation;
- timeout.

DEC-160 authorizes no second executor attempt and no replacement run.

Any terminal model-run evidence must route through DEC-154.

## 11. Focused tests

Focused tests:

`tests/test_phase8a_exp051_operator_executor.py`

Git blob:

`6b734dc9f06488e584a10ff99407c78a3c04548f`

They verify:

- one-time main-push/path scope;
- no manual/scheduled/PR trigger;
- exact DEC-156 `advance --execute` use;
- absence of direct model dispatch;
- exact read-only plan run/artifact bindings;
- immutable checkout/runtime;
- receipt claims dispatch only;
- all downstream locks false;
- receipt persistence outside the checkout.

## 12. Authorization state

DEC-160 does not change the DEC-150 research protocol or any downstream promotion/trading lock.

It does not authorize:

- a second historical run;
- retry;
- replacement;
- promotion;
- shadow/demo execution;
- broker mutation;
- live order;
- real-money action;
- trading.

Its only purpose is to provide an available environment for the already authorized DEC-155 first attempt while forcing all dispatch logic through DEC-156.

## 13. Next gate

After DEC-160 merges, the executor workflow automatically runs once.

If the DEC-156 executor succeeds, the resulting EXP-051 model workflow becomes the consumed attempt 1 and must be observed to a terminal state.

No rerun is permitted.

The terminal run must then be reviewed through DEC-154 and, on success, its complete aggregate evidence must revalidate through DEC-152 before any result disposition is recorded.
