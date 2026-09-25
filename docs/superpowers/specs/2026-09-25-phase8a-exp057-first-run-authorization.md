# Phase 8A — EXP-057 First-Run Authorization Gate

**Date:** 2026-09-25
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED
**Decision:** DEC-225
**Experiment:** EXP-20260925-057

## Zero-prior-run proof

Immediately before DEC-225 was frozen, the latest 100 repository GitHub Actions runs were queried.

That set contained:

- manual-main workflow-dispatch runs: `1`
- exact EXP-057 workflow matches: `0`

The exact workflow identity checked was:

- name: `phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training`
- path: `.github/workflows/phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`

No EXP-057 historical model-result attempt had consumed the first-run slot.

## Frozen predecessor bindings

DEC-225 binds:

- DEC-223 merge: `160c618352739a1ae12b86c80be9573e4c2f234a`
- DEC-223 workflow blob: `db9d8ccaa7da674124963acc6ab4e65e6c2ad83f`
- DEC-223 CLI blob: `889b2daa4e44175e0479377d6c8ea39846da596d`
- DEC-223 execution-gate blob: `07c7db8bc7fc29cf595aa617f1d66ec4f77e4879`
- DEC-224 merge: `e0f2328334d6da6b52cad53f23c9a3b05eeb72cd`
- DEC-224 terminal-review blob: `1a5f3e86b4d445ba4a77f3496f81de2b16b333cd`

All DEC-220/221/222 repaired protocol/core/artifact identities remain unchanged.

## First-run guard

DEC-225 hardens the exact manual-main EXP-057 workflow with a rejection guard before execution authorization.

At runtime the guard:

1. fetches the current workflow run by `GITHUB_RUN_ID`;
2. verifies exact workflow name/path/event/main-branch identity;
3. fetches manual-main runs for the exact EXP-057 workflow;
4. excludes the current run id;
5. fails closed if any prior manual-main EXP-057 run exists.

The guarded workflow blob is:

`2f28eea9f1e9cb941a91553bd6a7dc93245da7f8`

No retry, rerun, or replacement semantics are introduced.

## Outer historical-result slot

DEC-225 opens only the outer historical-result slot in the exact execution gate.

After merge, the gate may report true for:

- model-run dispatch authorization;
- authoritative historical result execution;
- model-protocol result production;
- model fitting for that bounded historical attempt.

The underlying DEC-220/221/222 protocol/core/artifact authorization constants remain false. DEC-225 is the only outer source authorization.

Execution-gate source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_execution_gate.py`

Git blob:

`2eaedc5fdde2e622f0e3394ea78ae5435b8d5347`

## One-attempt semantics

DEC-225 does not itself dispatch the workflow.

The first manual-main EXP-057 workflow attempt, once separately submitted, consumes the slot regardless of terminal outcome:

- success;
- failure;
- cancellation;
- timeout.

Any terminal outcome must route through DEC-224.

A second EXP-057 attempt, rerun, retry, or replacement is not authorized.

## Downstream locks

DEC-225 keeps false:

- replacement model run;
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

`tests/test_phase8a_exp057_model_workflow.py`

Git blob:

`0ff23cf161b3681f87023105cfa6f20ef3871127`

They verify exact DEC-223/224 source binding, the DEC-225 outer authorization, the first-run rejection guard, manual-main/input-free workflow shape, pinned numerical runtime, evidence preservation, repaired CLI/compiler/runner identity, and the continued absence of a direct dispatch path from the CLI.

## Next gate

After DEC-225 is green and merged, the next safe gate is a separate clean-main, double-plan, one-way operator.

That operator may derive at most one dispatch action only while the exact EXP-057 workflow state is still `MISSING`.

DEC-225 itself does not dispatch a model run.
