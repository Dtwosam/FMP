# Phase 8A — EXP-060 Clean-Main One-Way Operator

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED
**Decision:** DEC-259
**Experiment:** EXP-20260926-060

## Purpose

DEC-259 freezes a clean-main, one-way operator for the already bounded DEC-258 EXP-060 historical-result slot.

It does not dispatch the model workflow. It only derives the one next authoritative action from clean current `main` and the exact live EXP-060 workflow state.

## Frozen authorization binding

DEC-259 binds merged DEC-258 commit:

`c6aefd21b2deadd834248e69cf7117081ea58497`

The operator requires the EXP-060 execution gate to report:

- execution-gate decision `DEC-256`;
- execution-authorization decision `DEC-258`;
- exact DEC-253/254/255 repair protocol/repaired core/repaired artifact identities;
- exact DEC-256 workflow/CLI/gate identities;
- exact DEC-257 terminal-review identity.

## Clean-main preflight

Before deriving any action, the operator requires:

- local branch exactly `main`;
- local HEAD exactly equal to freshly fetched `origin/main`;
- clean working tree;
- origin remote exactly `Dtwosam/FMP`.

Any mismatch fails closed.

## One-way live state

The operator queries only manual-main runs of:

`phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml`

The live state is classified as exactly one of:

- `MISSING`;
- `IN_PROGRESS`;
- `TERMINAL`.

More than one manual-main run is rejected as a DEC-258 violation.

Only `MISSING` may expose a dispatch command.

`IN_PROGRESS` exposes no dispatch/replacement action.

`TERMINAL` exposes no dispatch/replacement action and routes through DEC-257.

## Frozen dispatch action

For `MISSING`, the only permitted command is:

`gh workflow run phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml --ref main -R Dtwosam/FMP`

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

`scripts/phase8a_exp060_operator.py`

Git blob:

`3d0647254e548d719d47981b11e1cd90028bd657`

The CLI exposes:

- `next` — read-only live-state planning;
- `advance` — non-executing preparation;
- `advance --execute` — at most one dispatch after two identical fresh `next` plans.

The execution path calls the public `next` planner twice immediately before submission and fails closed if the plans differ.

No rerun, retry, or replacement command exists.

## Operator source identity

Operator source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_operator.py`

Git blob:

`cab95c785127dae07edd7501df51e61f289982a5`

Focused tests:

`tests/test_phase8a_exp060_operator.py`

Git blob:

`72eb2f99ac234985da552468201d669ca684678d`

The tests pin clean-main checkout rules, exact workflow/run endpoints, one-run-only selection, one-way state classification, dispatch-only-on-`MISSING`, exact DEC-256/258 gate metadata, DEC-257 terminal review routing, aggregate artifact selection, tamper rejection, and the double-plan execution check.

## Authorization state

DEC-259 itself does not dispatch and does not consume the DEC-258 slot.

No replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading is authorized.

## Next gate

After DEC-259 is green and merged, the next safe gate is a repository-hosted read-only `next` plan runner.

Only after that merged-main proof succeeds and its exact artifact is independently bound may a separate one-shot executor source be considered.
