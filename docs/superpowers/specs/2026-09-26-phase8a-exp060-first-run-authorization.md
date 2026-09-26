# Phase 8A — EXP-060 First-Run Authorization Gate

**Date:** 2026-09-26
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED
**Decision:** DEC-258
**Experiment:** EXP-20260926-060

## Zero-prior-run proof

Immediately after DEC-257 merged and before DEC-258 source was opened, the exact EXP-060 GitHub Actions workflow page was read directly.

GitHub reported:

- exact EXP-060 workflow runs: `0`
- page state: `This workflow has no runs yet.`

The exact workflow identity checked was:

- name: `phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training`
- path: `.github/workflows/phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`

No EXP-060 historical model-result attempt had consumed the first-run slot.

## Frozen predecessor bindings

DEC-258 binds:

- DEC-256 merge: `cef9f6d201bf2b025f08c924a11c84e9684b9ba0`
- DEC-256 workflow blob: `20af1bf2f9057274a8c50d5b48becbf5f683ef86`
- DEC-256 CLI blob: `90c6bc9e893c813d394e3a9c4adc5a155e938af0`
- DEC-256 execution-gate blob: `82f51bf85ccb1793b3a980b2884f3e122a03c8db`
- DEC-257 merge: `5998292b80c0986bdcc0b9f2a91cb024ef92158a`
- DEC-257 terminal-review blob: `989ebc7b0cc33e5076f83ea94337fe6581c321e3`

The DEC-253/254/255 repair protocol, repaired training-core, and repaired artifact-contract identities remain unchanged and remain internally non-executable.

## First-run guard

DEC-258 hardens the manual-main EXP-060 workflow with a rejection guard before the execution authorization step.

At runtime the guard:

1. fetches the current workflow run by `GITHUB_RUN_ID`;
2. verifies the current run's exact name/path/event/main-branch identity;
3. fetches manual-main runs for the exact EXP-060 workflow;
4. excludes the current run id;
5. requires the current GitHub run to have `run_attempt == 1`;
6. fails closed if any prior manual-main EXP-060 run exists.

The guarded workflow blob is:

`91a5bb720ca10b261533409e36f6143994afcca3`

No retry, rerun, or replacement semantics are introduced.

## Outer historical-result slot

DEC-258 opens only the outer historical-result slot in the exact execution gate.

After merge, the gate may report true for:

- model-run dispatch authorization;
- authoritative historical result execution;
- model-protocol result production;
- model fitting for that bounded historical attempt.

The underlying DEC-253/254/255 repair protocol, repaired training-core, and repaired artifact-contract execution/fit authorization constants remain false. DEC-258 is the only outer source authorization.

Execution-gate source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_execution_gate.py`

Git blob:

`3a6bb23d237ab8d74896e06821d0189ed689e169`

## One-attempt semantics

DEC-258 does not itself dispatch the workflow.

The first manual-main EXP-060 workflow attempt, once separately submitted, consumes the slot regardless of terminal outcome:

- success;
- failure;
- cancellation;
- timeout.

Any terminal outcome must route through DEC-257.

A second EXP-060 dispatch is blocked by prior-run detection. A GitHub rerun of the same run ID is blocked by the explicit `run_attempt == 1` assertion. Retry or replacement is not authorized.

## Downstream locks

DEC-258 keeps false:

- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

No portfolio/shadow candidate is created by this authorization source.

## Focused tests

Focused workflow/authorization tests:

`tests/test_phase8a_exp060_model_workflow.py`

Git blob:

`ad305ccf0d2dde2e2074ae069735743d5033cbdf`

They verify exact source binding, the one-slot outer authorization, the first-run rejection guard, manual-main/input-free workflow shape, pinned numerical runtime, evidence preservation, execution-before-artifact-loading order, and continued downstream locks.

## Next gate

After DEC-258 is green and merged, the next safe gate is a separate clean-main, double-plan, one-way operator.

That operator may derive at most one dispatch action only while the exact EXP-060 workflow state is still `MISSING`.

DEC-258 itself does not dispatch a model run.
