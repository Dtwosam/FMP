# Phase 8A — EXP-059 Clean-Main One-Way Operator

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED
**Decision:** DEC-248
**Experiment:** EXP-20260926-059

## Purpose

DEC-248 freezes a clean-main, one-way operator for the already bounded DEC-247 EXP-059 historical-result slot.

It does not dispatch the model workflow. It only derives the one next authoritative action from clean current `main` and the exact live EXP-059 workflow state.

## Frozen authorization binding

DEC-248 binds merged DEC-247 commit:

`41975d1ddbabcc31f490b8b36def2a491010c277`

The operator requires the EXP-059 execution gate to report:

- execution-gate decision `DEC-245`;
- execution-authorization decision `DEC-247`;
- exact DEC-242/243/244 protocol/core/artifact identities;
- exact DEC-245 workflow/CLI/gate identities;
- exact DEC-246 terminal-review identity.

## Clean-main preflight

Before deriving any action, the operator requires:

- local branch exactly `main`;
- local HEAD exactly equal to freshly fetched `origin/main`;
- clean working tree;
- origin remote exactly `Dtwosam/FMP`.

Any mismatch fails closed.

## One-way live state

The operator queries only manual-main runs of:

`phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training.yml`

The live state is classified as exactly one of:

- `MISSING`;
- `IN_PROGRESS`;
- `TERMINAL`.

More than one manual-main run is rejected as a DEC-247 violation.

Only `MISSING` may expose a dispatch command.

`IN_PROGRESS` exposes no dispatch/replacement action.

`TERMINAL` exposes no dispatch/replacement action and routes through DEC-246.

## Frozen dispatch action

For `MISSING`, the only permitted command is:

`gh workflow run phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training.yml --ref main -R Dtwosam/FMP`

The operator report must keep false:

- replacement model run;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Public CLI

CLI:

`scripts/phase8a_exp059_operator.py`

Git blob:

`720bab7054ecd55fd90a1ef6dbae8b00ceb5dabd`

The CLI exposes:

- `next` — read-only live-state planning;
- `advance` — non-executing preparation;
- `advance --execute` — at most one dispatch after two identical fresh `next` plans.

The execution path calls the public `next` planner twice immediately before submission and fails closed if the plans differ.

No rerun, retry, or replacement command exists.

## Operator source identity

Operator source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_operator.py`

Git blob:

`12a4fcce685e2136aea6a9d0e3e27ba39b320f1e`

Focused tests:

`tests/test_phase8a_exp059_operator.py`

Git blob:

`b80a3233dda65573fe2d51f31fc14b3e97f13ba3`

The tests pin clean-main checkout rules, exact workflow/run endpoints, one-run-only selection, one-way state classification, dispatch-only-on-`MISSING`, exact DEC-245/247 gate metadata, DEC-246 terminal review routing, aggregate artifact selection, tamper rejection, and the double-plan execution check.

## Authorization state

DEC-248 itself does not dispatch and does not consume the DEC-247 slot.

No replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading is authorized.

## Next gate

After DEC-248 is green and merged, the next safe gate is a repository-hosted read-only `next` plan runner.

Only after that merged-main proof succeeds and its exact artifact is independently bound may a separate one-shot executor source be considered.
