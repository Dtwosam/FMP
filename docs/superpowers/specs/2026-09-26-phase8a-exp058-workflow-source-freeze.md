# Phase 8A — EXP-058 Workflow/CLI/Runtime Source Freeze

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED
**Decision:** DEC-234
**Experiment:** EXP-20260925-058

## Purpose

DEC-234 freezes the manual-main EXP-058 workflow source, public CLI, pinned numerical runtime, and exact-source execution gate after DEC-233.

This decision defines the future historical-result execution surface but keeps it fail-closed. It does not open a first-run slot, does not dispatch the workflow, and does not authorize model fitting or result production.

## Frozen predecessor bindings

DEC-234 binds:

- DEC-231 merge: `a6926703d787a7fe0e2ba34261d14c4c4d362df2`
- DEC-231 protocol blob: `8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2`
- DEC-232 merge: `24cb20bb0b1e3aa25f1ea87e1cfbba22587a0ae6`
- DEC-232 training-core blob: `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`
- DEC-233 merge: `5425184a53b2bd5241291f9d561f47b69ca4d134`
- DEC-233 artifact/evidence-contract blob: `5a34f354b68e14bb7116c79f15f9cfebe149a811`

## Workflow source

Workflow:

`.github/workflows/phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training.yml`

Git blob:

`78e9bf66ade5f6fb42ebe27e28b7ba24f36741b8`

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

DEC-234 intentionally contains no first-run guard. That belongs to a later separately authorized gate.

## Public CLI

CLI:

`scripts/phase8a_exp058_model_run.py`

Git blob:

`e35a6ee0ff11bd3928b3bf05bf19f3572f64952c`

The CLI exposes:

- `status`;
- `require-execution`;
- `run-cell`;
- `aggregate`.

For every execution-capable command, the CLI requires the exact execution gate before readiness loading, authoritative artifact loading, regime-floor model-core execution, or aggregate compilation.

The CLI calls:

`run_fit_temporal_residual_regime_floor_utility_model_cell_core`

and the DEC-233 deterministic aggregate compiler/writer.

The CLI contains no direct workflow-dispatch path.

## Runtime lock

Runtime requirements:

`requirements/exp058-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

Authorized Python version:

`3.12.14`

## Execution gate

Execution gate:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_execution_gate.py`

Git blob:

`74881c0fee21392872ffd3df1378639bb04fea4a`

The gate validates exact DEC-231/232/233 protocol/core/artifact identities, exact workflow/CLI/runtime blobs, and frozen legacy preprocessing/data-contract dependencies.

It also rechecks that all underlying protocol/core/artifact execution and fit authorization constants remain false.

DEC-234 sets false:

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

`tests/test_phase8a_exp058_model_workflow.py`

Git blob:

`ba3e43ffc121fa6eae4b46148622a3f01c1e4e84`

They verify exact source binding, execution-closed state, manual-main/input-free workflow shape, absence of a first-run guard, exact matrix/runtime/artifact surface, evidence preservation, execution-before-artifact-loading order, exact regime-floor cell-runner binding, and no direct dispatch path in the CLI.

## Next gate

After DEC-234 is green and merged, the next safe gate is a separate predeclared attempt-1 terminal-review contract.

That review contract must exist before any zero-prior-run proof, first-run guard, bounded historical slot, operator, executor, or actual model dispatch is considered.
