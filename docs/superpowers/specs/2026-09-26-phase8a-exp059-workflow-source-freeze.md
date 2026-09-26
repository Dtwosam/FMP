# Phase 8A — EXP-059 Workflow/CLI/Runtime Source Freeze

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED
**Decision:** DEC-245
**Experiment:** EXP-20260926-059

## Purpose

DEC-245 freezes the manual-main EXP-059 workflow source, public CLI, pinned numerical runtime, and exact-source execution gate after DEC-244.

The historical-result surface is defined but remains fail-closed. DEC-245 does not open a first-run slot, does not dispatch a workflow, and does not authorize model fitting or result production.

## Frozen source bindings

DEC-245 binds:

- DEC-242 merge: `a14afb226722d168c3d899d7079776388161a52d`
- DEC-242 protocol blob: `cd4e790098a5c8d99ea2aa5264465b5d4b6b6acc`
- DEC-243 merge: `9f427f06f315288bd9b132de19901beb5a5ddfc8`
- DEC-243 training-core blob: `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`
- DEC-244 merge: `b539c48cd62fb8e510ecaa15ce507c114f9401bb`
- DEC-244 artifact/evidence-contract blob: `a993d8a0a98b181c7810e4f0931be330352437b4`

## Workflow source

Workflow:

`.github/workflows/phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training.yml`

Git blob:

`d416c43c9e582f49cd60314c6ee736925e8185e8`

The workflow is:

- manual `workflow_dispatch` only;
- main-branch only;
- input-free;
- read-only GitHub permissions;
- Python 3.12.14;
- exact nine pair/timeframe datasets;
- exact 60m and 240m horizons;
- exact frozen feature/outcome/readiness artifact identities;
- partial cell-evidence preserving;
- aggregate-evidence producing.

DEC-245 intentionally contains no first-run guard. That belongs to a later separately authorized gate.

## Public CLI

CLI:

`scripts/phase8a_exp059_model_run.py`

Git blob:

`44c084c226c62c30ddf16741027593a4a835605f`

The CLI exposes:

- `status`;
- `require-execution`;
- `run-cell`;
- `aggregate`.

For every execution-capable command, the CLI requires the exact DEC-245 execution gate before readiness loading, authoritative artifact loading, regime-balance model-core execution, or aggregate compilation.

The CLI binds the DEC-243 cell runner:

`run_fit_temporal_residual_regime_balance_utility_model_cell_core`

and the DEC-244 aggregate compiler/writer.

The CLI contains no direct workflow-dispatch command.

## Runtime lock

Runtime requirements:

`requirements/exp059-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

Authorized Python version:

`3.12.14`

The numerical package set remains unchanged from the predecessor run surface.

## Execution gate

Execution gate:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_execution_gate.py`

Git blob:

`d6556cf3bc3a1189c2ee6648c1870ec307a2178f`

The gate validates exact DEC-242/243/244 protocol/core/artifact identities, workflow/CLI/runtime blobs, and frozen legacy preprocessing/data-contract dependencies.

It also revalidates that all underlying protocol/core/artifact execution and fit authorization constants remain false.

DEC-245 sets false:

- model-run dispatch authorization;
- authoritative historical result execution;
- model-protocol result production;
- model fit;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

Any `require-execution` call must fail closed.

## Focused tests

Focused workflow tests:

`tests/test_phase8a_exp059_model_workflow.py`

Git blob:

`e75663b17d334fc73b3fc905779988f5807e7e6d`

They verify exact source binding, execution-closed state, manual-main/input-free workflow shape, absence of a first-run guard, exact matrix/runtime/artifact surface, partial and aggregate evidence preservation, execution-before-artifact-loading order, exact regime-balance cell-runner binding, and no direct dispatch path in the CLI.

## Next gate

After DEC-245 is green and merged, the next safe gate is a separate predeclared attempt-1 terminal-review contract.

That review contract must exist before any zero-prior-run proof, first-run guard, bounded historical slot, operator, executor, or actual EXP-059 model dispatch is considered.
