# Phase 8A — EXP-051 Read-Only Operator Plan Output-Path Repair

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY REPAIR; NO EXP-051 DISPATCH
**Decision:** DEC-159
**Experiment:** EXP-20260924-051

## 1. Triggering evidence

DEC-158 merged at:

`a72bb89b9e4edcc3d7a3617a1b917d64b6ec4d97`

Its automatic repaired read-only plan run was:

`36065119686`

That run proved:

- exact merged-main checkout;
- Python 3.12.14 setup;
- non-editable dependency installation;
- explicit post-install clean-worktree success.

The subsequent exact DEC-156 `next` invocation still failed closed with:

`ValueError: EXP-051 dispatch requires a clean working tree`

No EXP-051 historical model workflow was dispatched and the DEC-155 single-run slot remained unconsumed.

## 2. Root cause

DEC-158 removed package-install mutation correctly.

However the runner invoked:

`python scripts/phase8a_exp051_operator.py next | tee operator-plan.json`

The shell opened `operator-plan.json` inside the repository before the Python process executed DEC-156's independent checkout preflight.

That untracked plan file made the worktree dirty at the exact point DEC-156 inspected it.

The operator again behaved correctly by failing closed.

## 3. Repair

DEC-159 changes only where read-only plan output is persisted.

The runner now executes:

`python scripts/phase8a_exp051_operator.py next > "$RUNNER_TEMP/operator-plan.json"`

The output file is outside the Git checkout.

Plan verification reads:

`$RUNNER_TEMP/operator-plan.json`

and the artifact upload uses:

`${{ runner.temp }}/operator-plan.json`

No file is created in the repository before DEC-156 completes its checkout validation.

## 4. Repaired workflow identity

Workflow:

`.github/workflows/phase8a-exp051-operator-plan.yml`

Git blob:

`187011b6b4f1179c2b83c90062d58d15a29f9639`

All DEC-158 environment protections remain:

- `PYTHONPATH=${{ github.workspace }}/src`;
- non-editable dependency installation;
- explicit clean-worktree assertion after installation;
- exact DEC-156 `next` invocation.

The runner still contains no:

- manual model-workflow dispatch;
- operator `advance`;
- operator `advance --execute`;
- retry or replacement path.

## 5. Focused tests

Focused tests:

`tests/test_phase8a_exp051_operator_plan_runner.py`

Git blob:

`0490a32292b67559701d765dacff7997a4d57ce0`

They now additionally require:

- artifact output under `runner.temp`;
- verification through `RUNNER_TEMP`;
- absence of the checkout-local `tee operator-plan.json` pattern.

## 6. Authorization state

DEC-159 changes no DEC-155 model-run authorization.

It does not:

- dispatch EXP-051;
- consume the one-run slot;
- authorize a retry;
- authorize a replacement run;
- authorize promotion;
- authorize shadow/demo execution;
- authorize broker mutation;
- authorize live orders;
- authorize real-money action;
- authorize trading.

## 7. Next gate

After DEC-159 merges, the workflow-file change automatically triggers the read-only plan runner again.

The run must succeed through:

- clean merged-main checkout;
- immutable runtime setup;
- DEC-156 `next`;
- exact zero-run plan validation;
- immutable plan artifact upload.

Only after that exact plan is inspected may a separate executor decision be frozen.
