# Phase 8A — EXP-060 Workflow/CLI/Runtime Source Freeze

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED
**Decision:** DEC-256
**Experiment:** EXP-20260926-059

## Purpose

DEC-256 freezes the manual-main EXP-060 repaired regime-balance workflow source, public CLI, pinned numerical runtime, and exact-source execution gate after DEC-255.

The historical-result surface is defined but remains fail-closed. DEC-256 does not open a first-run slot, does not dispatch a workflow, and does not authorize model fitting or result production.

## Frozen source bindings

DEC-256 binds:

- DEC-253 merge: `7e5b399cb7960d385d956b33e5d96cea85bb2c28`
- DEC-253 protocol blob: `82d336250e2cdd9894afa5554c6b422e0de6b1fe`
- DEC-254 merge: `c8cac108bc098dbceda4b8903f5a56ac7f62bf47`
- DEC-254 training-core blob: `202dcaa8ba4ad25324fbe53d00e812c60fbb37dd`
- DEC-255 merge: `d3a52722c178c96eb865791be096661007d16dd5`
- DEC-255 artifact/evidence-contract blob: `2a6c550dcafac2e7013136fcbbef95b13c2e7d18`

## Workflow source

Workflow:

`.github/workflows/phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training.yml`

Git blob:

`20af1bf2f9057274a8c50d5b48becbf5f683ef86`

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

DEC-256 intentionally contains no first-run guard. That belongs to a later separately authorized gate.

## Public CLI

CLI:

`scripts/phase8a_exp060_model_run.py`

Git blob:

`90c6bc9e893c813d394e3a9c4adc5a155e938af0`

The CLI exposes:

- `status`;
- `require-execution`;
- `run-cell`;
- `aggregate`.

For every execution-capable command, the CLI requires the exact DEC-256 execution gate before readiness loading, authoritative artifact loading, regime-balance model-core execution, or aggregate compilation.

The CLI binds the DEC-254 repaired cell runner:

`run_fit_temporal_residual_regime_balance_utility_model_cell_core`

and the DEC-255 repaired aggregate compiler/writer.

The CLI contains no direct workflow-dispatch command.

## Runtime lock

Runtime requirements:

`requirements/exp060-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

Authorized Python version:

`3.12.14`

The numerical package set remains unchanged from the predecessor run surface.

## Execution gate

Execution gate:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_execution_gate.py`

Git blob:

`82f51bf85ccb1793b3a980b2884f3e122a03c8db`

The gate validates exact DEC-253/243/244 protocol/core/artifact identities, workflow/CLI/runtime blobs, and frozen legacy preprocessing/data-contract dependencies.

It also revalidates that all underlying protocol/core/artifact execution and fit authorization constants remain false.

DEC-256 sets false:

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

`tests/test_phase8a_exp060_model_workflow.py`

Git blob:

`e530e2122ac0ac59f1c02345d890f55c94bfec97`

They verify exact source binding, execution-closed state, manual-main/input-free workflow shape, absence of a first-run guard, exact matrix/runtime/artifact surface, partial and aggregate evidence preservation, execution-before-artifact-loading order, exact regime-balance cell-runner binding, and no direct dispatch path in the CLI.

## Next gate

After DEC-256 is green and merged, the next safe gate is a separate predeclared attempt-1 terminal-review contract.

That review contract must exist before any zero-prior-run proof, first-run guard, bounded historical slot, operator, executor, or actual EXP-060 model dispatch is considered.
