# Phase 8A — EXP-056 Workflow/CLI/Runtime Source Freeze

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / EXECUTION CLOSED
**Decision:** DEC-212
**Experiment:** EXP-20260925-056

## Purpose

DEC-212 freezes the manual-main EXP-056 workflow source, public CLI, pinned numerical runtime, and exact-source execution gate after DEC-211.

This decision creates the future historical-result execution surface but keeps it fail-closed. It does not open a first-run slot, does not dispatch the workflow, and does not authorize model fitting or result production.

## Frozen predecessor bindings

DEC-212 binds:

- DEC-209 merge: `d2e1aabba6c0f283da6802fe315a5a29b22b503c`
- DEC-209 protocol blob: `14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d`
- DEC-210 merge: `029159999fae7eaa67811f8b3d8bf2bf8834e491`
- DEC-210 training-core blob: `c472ed48e7b79d22056d43deb0fe09166ccf34c9`
- DEC-211 merge: `193312de6d03dc8286956f7594602f67688b1d23`
- DEC-211 artifact/evidence-contract blob: `f554011c092f5c4ec5d3f9b8e2330bfc974376f8`

## Workflow source

Workflow:

`.github/workflows/phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml`

Git blob:

`83e5434c065167294b854b58308fec6d39d800db`

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

DEC-212 intentionally contains no first-run guard. That belongs to a later separately authorized gate.

## Public CLI

CLI:

`scripts/phase8a_exp056_model_run.py`

Git blob:

`30e79ef7ef20d12d75fc97103b9411b7b467ecef`

The CLI exposes:

- `status`;
- `require-execution`;
- `run-cell`;
- `aggregate`.

For every execution-capable command, the CLI requires the exact execution gate before readiness loading, authoritative artifact loading, model-core execution, or aggregate compilation.

The CLI contains no direct `gh workflow run` dispatch path.

## Runtime lock

Runtime requirements:

`requirements/exp056-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

The numerical environment is inherited unchanged from the predecessor run surface.

Authorized Python version:

`3.12.14`

## Execution gate

Execution gate:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_execution_gate.py`

Git blob:

`a81f746c8b19abc63f1bb83da0c32f1023644b94`

The gate validates exact protocol/core/artifact/workflow/CLI/runtime and legacy dependency blobs and rechecks that all underlying protocol/core/artifact execution and fit authorization constants remain false.

DEC-212 sets false:

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

`tests/test_phase8a_exp056_model_workflow.py`

Git blob:

`938f2abd2f1488affcb3ce0e7a3d64c2ec0f0165`

They verify exact source binding, execution-closed state, manual-main/input-free workflow shape, absence of a first-run guard, exact matrix/runtime/artifact surface, evidence preservation, execution-before-artifact-loading order, and no direct dispatch path in the CLI.

## Next gate

After DEC-212 is green and merged, the next safe gate is a separate predeclared attempt-1 terminal-review contract.

That review contract must exist before any zero-prior-run proof, first-run guard, bounded historical slot, operator, executor, or actual model dispatch is considered.
