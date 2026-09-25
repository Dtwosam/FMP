# Phase 8A — EXP-057 Workflow/CLI/Runtime Source Freeze

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED
**Decision:** DEC-223
**Experiment:** EXP-20260925-057

## Purpose

DEC-223 freezes the manual-main EXP-057 workflow source, public CLI, pinned numerical runtime, and exact-source execution gate after DEC-222.

This decision creates the future historical-result execution surface for the repaired EXP-057 implementation but keeps it fail-closed. It does not add a first-run guard, does not dispatch the workflow, and does not authorize model fitting or result production.

## Frozen predecessor bindings

DEC-223 binds:

- DEC-220 merge: `865ab1569a0765078ed099008a5722f8a6d310b4`
- DEC-220 repair-protocol blob: `2f355526476a4d41967bb46e1bfad6aa525cbfa9`
- DEC-221 merge: `6ea34dd3c62f72c55376e891eeb44d96ad5de54b`
- DEC-221 repaired training-core blob: `ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd`
- DEC-222 merge: `51e9ccde9feaada7932384fc4547b721c1341588`
- DEC-222 artifact/evidence-contract blob: `d69eb668ade480b66faf992190b3a4929f414960`

## Workflow source

Workflow:

`.github/workflows/phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml`

Git blob:

`db9d8ccaa7da674124963acc6ab4e65e6c2ad83f`

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

DEC-223 intentionally contains no first-run guard. That belongs to a later separately authorized gate.

## Public CLI

CLI:

`scripts/phase8a_exp057_model_run.py`

Git blob:

`889b2daa4e44175e0479377d6c8ea39846da596d`

The CLI exposes:

- `status`;
- `require-execution`;
- `run-cell`;
- `aggregate`.

For every execution-capable command, the CLI requires the exact DEC-223 execution gate before readiness loading, authoritative artifact loading, repaired model-core execution, or aggregate compilation.

The CLI calls:

- repaired DEC-222 aggregate compiler/writer;
- repaired DEC-221 training module;
- the actual exported deterministic cell runner `run_fit_temporal_residual_lower_tail_utility_model_cell_core`.

The CLI contains no direct `gh workflow run` dispatch path.

## Runtime lock

Runtime requirements:

`requirements/exp057-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

Authorized Python version:

`3.12.14`

The numerical environment is identical to the frozen predecessor runtime.

## Execution gate

Execution gate:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_execution_gate.py`

Git blob:

`07c7db8bc7fc29cf595aa617f1d66ec4f77e4879`

The gate validates exact DEC-220/221/222 protocol/core/artifact identities, exact workflow/CLI/runtime blobs, and stable legacy preprocessing/data-contract sources. It also rechecks that all underlying protocol/core/artifact execution and fit authorization constants remain false.

DEC-223 sets false:

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

`tests/test_phase8a_exp057_model_workflow.py`

Git blob:

`63d12da6af913bd981081002b11e6ce3393cdb7e`

They verify exact repaired source binding, execution-closed state, manual-main/input-free workflow shape, absence of a first-run guard, exact matrix/runtime/artifact surface, partial/aggregate evidence preservation, authorization-before-artifact-loading order, repaired aggregate compiler identity, actual cell-runner symbol, and absence of a direct dispatch path in the CLI.

## Next gate

After DEC-223 is green and merged, the next safe gate is a separate predeclared attempt-1 terminal-review contract.

That review contract must exist before any zero-prior-run proof, first-run guard, bounded historical slot, operator, executor, or actual EXP-057 dispatch is considered.
