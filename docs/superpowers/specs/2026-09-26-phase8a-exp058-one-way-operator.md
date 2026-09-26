# Phase 8A — EXP-058 Clean-Main One-Way Operator

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED
**Decision:** DEC-237
**Experiment:** EXP-20260925-058

## Purpose

DEC-237 freezes a clean-main, one-way operator for the single guarded historical EXP-058 slot opened by DEC-236.

The operator does not itself authorize a second attempt and does not dispatch anything merely by existing in source.

## Frozen authorization binding

DEC-237 binds DEC-236 merge:

`680359f2d4d03519952e84f257c9d16559b4e251`

The active source gate must report:

- execution-gate decision `DEC-234`;
- execution-authorization decision `DEC-236`;
- exact DEC-231/232/233/234/235 provenance;
- the guarded EXP-058 workflow identity;
- the four bounded historical-run fields true only while live state is `MISSING`;
- replacement/promotion/shadow/demo/broker/live/real-money/trading false.

## Checkout preflight

Before planning any action, the operator requires:

- local branch exactly `main`;
- a clean worktree;
- a fetched `origin/main`;
- local HEAD exactly equal to fetched `origin/main`;
- origin URL resolving exactly to `Dtwosam/FMP`.

Any mismatch fails closed.

## Live run state

The operator lists only the exact EXP-058 workflow on manual `main` dispatches.

It accepts at most one such run.

Live state is classified as:

- `MISSING` — no exact manual-main EXP-058 run exists;
- `IN_PROGRESS` — one exact run exists and is not completed;
- `TERMINAL` — one exact run exists and is completed.

Multiple exact manual-main runs fail closed.

## One-way action

Only `MISSING` may expose:

`gh workflow run phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training.yml --ref main -R Dtwosam/FMP`

In `MISSING`, the report may show the four already bounded DEC-236 historical-run fields true.

For `IN_PROGRESS` and `TERMINAL`:

- dispatch is false;
- authoritative result execution is false;
- model-protocol result production is false;
- model fit is false;
- replacement remains false;
- no dispatch command is present.

Terminal state routes through DEC-235.

## Public CLI

CLI:

`scripts/phase8a_exp058_operator.py`

Git blob:

`aca3a47d79a0c32ae6590db3019557bea6bb6e89`

Commands:

- `next` — read-only live plan;
- `advance` — non-executing preparation;
- `advance --execute` — execute only the exact currently frozen dispatch plan.

The executable path reads the public `next` plan twice. Any live-state or plan change between the first and second read fails closed.

There is no rerun, retry, or replacement command.

## Operator source

Source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_operator.py`

Git blob:

`ffda686bf6c632f3c13bfaed8eafb23e8e565795`

The source includes deterministic endpoint construction, exact workflow/run selection, state classification, frozen dispatch command construction, gate-provenance validation, aggregate-artifact selection, and downstream lock validation.

## Focused tests

Tests:

`tests/test_phase8a_exp058_operator.py`

Git blob:

`d1fbe9a7f5db6318be53870a149584c5bb02ecf6`

They pin clean-main checkout, exact workflow endpoints, one-run maximum, state classification, missing-only dispatchability, DEC-234/235/236 metadata, exact aggregate-artifact identity, double-plan execution, tamper rejection, and absence of rerun/replacement behavior.

## Downstream locks

DEC-237 keeps false:

- replacement model run;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

DEC-237 itself does not consume the DEC-236 historical slot.

## Next gate

The next safe gate is a repository-hosted read-only `next` proof with read-only Actions permissions and no execution path.
