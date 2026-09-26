# Phase 8A — EXP-059 First-Run Authorization Gate

**Date:** 2026-09-26
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED
**Decision:** DEC-247
**Experiment:** EXP-20260926-059

## Zero-prior-run proof

Immediately after DEC-246 merged and before DEC-247 source was opened, the latest 100 repository GitHub Actions runs were queried.

That set contained:

- manual-main workflow-dispatch runs: `1`
- exact EXP-059 workflow matches: `0`

The exact workflow identity checked was:

- name: `phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training`
- path: `.github/workflows/phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`

No EXP-059 historical model-result attempt had consumed the first-run slot.

## Frozen predecessor bindings

DEC-247 binds:

- DEC-245 merge: `d33e2f1e6e7f39c12811dbc07c5cd960f8e2442f`
- DEC-245 workflow blob: `d416c43c9e582f49cd60314c6ee736925e8185e8`
- DEC-245 CLI blob: `44c084c226c62c30ddf16741027593a4a835605f`
- DEC-245 execution-gate blob: `d6556cf3bc3a1189c2ee6648c1870ec307a2178f`
- DEC-246 merge: `018c8cb223c3553ad4db4ba5b33b339a9a8fa918`
- DEC-246 terminal-review blob: `5adc6ad72b2dfab1de1cca09a9bb2bc09663bfc5`

The DEC-242/243/244 protocol, training-core, and artifact-contract identities remain unchanged and remain internally non-executable.

## First-run guard

DEC-247 hardens the manual-main EXP-059 workflow with a rejection guard before the execution authorization step.

At runtime the guard:

1. fetches the current workflow run by `GITHUB_RUN_ID`;
2. verifies the current run's exact name/path/event/main-branch identity;
3. fetches manual-main runs for the exact EXP-059 workflow;
4. excludes the current run id;
5. fails closed if any prior manual-main EXP-059 run exists.

The guarded workflow blob is:

`6c3e516be8d6eaed834fb1955efccf43f414318f`

No retry, rerun, or replacement semantics are introduced.

## Outer historical-result slot

DEC-247 opens only the outer historical-result slot in the exact execution gate.

After merge, the gate may report true for:

- model-run dispatch authorization;
- authoritative historical result execution;
- model-protocol result production;
- model fitting for that bounded historical attempt.

The underlying DEC-242/243/244 protocol, training-core, and artifact-contract execution/fit authorization constants remain false. DEC-247 is the only outer source authorization.

Execution-gate source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_execution_gate.py`

Git blob:

`7e6d07c1d7f24bb69912227906990e59abc7be0d`

## One-attempt semantics

DEC-247 does not itself dispatch the workflow.

The first manual-main EXP-059 workflow attempt, once separately submitted, consumes the slot regardless of terminal outcome:

- success;
- failure;
- cancellation;
- timeout.

Any terminal outcome must route through DEC-246.

A second EXP-059 attempt, rerun, retry, or replacement is not authorized.

## Downstream locks

DEC-247 keeps false:

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

`tests/test_phase8a_exp059_model_workflow.py`

Git blob:

`d1fa6a2c1cd2169b1dc40f1904010a9293cfb9fb`

They verify exact source binding, the one-slot outer authorization, the first-run rejection guard, manual-main/input-free workflow shape, pinned numerical runtime, evidence preservation, execution-before-artifact-loading order, and continued downstream locks.

## Next gate

After DEC-247 is green and merged, the next safe gate is a separate clean-main, double-plan, one-way operator.

That operator may derive at most one dispatch action only while the exact EXP-059 workflow state is still `MISSING`.

DEC-247 itself does not dispatch a model run.
