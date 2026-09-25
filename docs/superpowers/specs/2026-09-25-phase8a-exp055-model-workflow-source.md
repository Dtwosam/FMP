# Phase 8A — EXP-055 Model Workflow Source Freeze

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED
**Decision:** DEC-201
**Experiment:** EXP-20260925-055

## Purpose

DEC-201 freezes the manual-main EXP-055 historical model workflow source, public CLI, pinned numerical runtime, and exact-source execution gate after DEC-200 establishes the non-executable evidence contract.

This decision does not authorize a historical model run.

## Frozen source bindings

DEC-201 binds:

- DEC-198 merge: `670f5d615b837b9268f8fb807aa198e7d14d0f1a`
- DEC-199 merge: `aaa80ce43a4dbd38e52e418dd16b61642d22b2b5`
- DEC-200 merge: `879d4a6c038277e6f69a2db971710b5ce1eaf103`
- DEC-198 protocol blob: `0ef3f932cade1a62e1faf946e9a9b87cf9c98744`
- DEC-199 core blob: `c9517b7516940c78621448088c3933aa1c57e281`
- DEC-200 artifact-contract blob: `65ca27a20d4e4fadd73c22b0b5693dc9d7ebeafb`

## Workflow

Workflow:

`.github/workflows/phase8a-exp055-fit-temporal-residual-breadth-utility-model-training.yml`

Git blob:

`da5b498deb7c8d15993eaeb686127f138ce9f161`

The workflow is:

- manual `workflow_dispatch` only;
- main-branch only;
- input-free;
- read-only for repository contents and Actions;
- Python 3.12.14;
- pinned to `requirements/exp055-model-run.txt`;
- fixed to the same accepted feature/outcome/readiness artifact identities used by the frozen predecessor path;
- fixed to all nine pair/timeframe datasets and both 60m/240m horizons;
- configured to preserve partial per-pair/timeframe cell evidence on failure;
- configured to aggregate exactly 18 cell results when execution is separately authorized.

DEC-201 intentionally contains no first-run guard. A later authorization decision must first predeclare terminal review and then explicitly open at most one guarded outer run slot.

## Public CLI

CLI:

`scripts/phase8a_exp055_model_run.py`

Git blob:

`41eeb09fe0730f5184e71a9f7413a3bc5f568e63`

It exposes:

- `status`
- `require-execution`
- `run-cell`
- `aggregate`

All execution-capable commands pass through the exact execution gate before readiness or authoritative artifact loading.

The CLI invokes the DEC-199 full residual-breadth cell core and DEC-200 aggregate evidence compiler.

## Runtime

Pinned runtime:

`requirements/exp055-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

It freezes:

- numpy 2.5.3
- scipy 1.18.1
- scikit-learn 1.9.1
- joblib 1.6.0
- threadpoolctl 3.7.0
- cloudpickle 3.1.2
- narwhals 2.26.0
- polars 1.44.2
- polars-runtime-32 1.44.2

## Exact-source gate

Execution gate:

`src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_execution_gate.py`

Git blob:

`e252f0550ca1c0bdc2ea16d32bc0b6a854b1c39c`

Decision:

`DEC-201`

The gate validates exact Git blobs for:

- DEC-200 artifact contract
- DEC-199 training core
- DEC-198 protocol
- legacy authoritative data loader
- EXP-055 workflow
- EXP-055 CLI
- EXP-055 pinned runtime
- pyproject
- preprocessing
- feature schema
- market-learning contracts
- outcome source

## Execution remains closed

DEC-201 freezes all four outer historical-result controls as false:

- model-run dispatch
- authoritative model-result execution
- model-protocol result production
- model fitting

Therefore `require-execution` must fail closed even when the workflow is manually dispatched.

No historical EXP-055 model result can be produced under DEC-201 alone.

## Downstream locks

DEC-201 also keeps false:

- promotion
- shadow execution
- demo orders
- broker mutation
- live orders
- real-money action
- trading

## Focused tests

Focused tests:

`tests/test_phase8a_exp055_model_workflow.py`

Git blob:

`05dc61310e480e16e0376bfba4c196c2297ac660`

They verify exact source bindings, closed execution flags, manual-main/input-free workflow scope, absence of a first-run guard, exact nine-dataset matrix, pinned runtime, partial/aggregate evidence paths, CLI preflight ordering, and numeric runtime identity.

## Next gate

After DEC-201 is green and merged, the next safe gate is a separate predeclared attempt-1 terminal-review contract.

Only after that review contract is frozen may another separate decision prove zero prior EXP-055 manual-main model runs, add a first-run guard, and consider one bounded historical-result slot.
