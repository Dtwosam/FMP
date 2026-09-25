# Phase 8A — EXP-052 Fit-Temporal-Support Model Workflow Source

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-166
**Experiment:** EXP-20260925-052

## 1. Purpose

DEC-166 freezes the manual-main workflow source, public CLI, pinned numerical runtime, and exact-source execution gate for EXP-052.

This decision makes the future historical execution path inspectable without opening it.

DEC-166 does **not** authorize:

- workflow dispatch;
- historical model-result execution;
- authoritative model fit;
- protocol-result production;
- rerun or replacement;
- promotion;
- shadow/demo execution;
- broker mutation;
- live order placement;
- real-money action;
- trading.

## 2. Frozen predecessor chain

DEC-166 binds the exact merged source chain:

- DEC-163 protocol merge: `9108cd170b2eccf73bddb6cbf8d6d7118dbd9cd1`;
- DEC-163 protocol blob: `01d5080560ec5d41653694b4df086ff2f10e770d`;
- DEC-164 training-core merge: `d9f893504b2d790eb73bc49edf4c0919ef2ff914`;
- DEC-164 training-core blob: `fe5664438752a161134bbed6f55d9985f1c1470a`;
- DEC-165 artifact-contract merge: `0753e85546bcef430863eceb99bdc38f43572477`;
- DEC-165 artifact/evidence blob: `ae06184b9a84405119b6ed434a8973139d8ae006`;
- accepted historical artifact-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`.

The gate independently validates the predecessor protocol/core/runner source-level execution and fit flags remain false.

## 3. Workflow identity

Workflow:

`.github/workflows/phase8a-exp052-fit-temporal-support-utility-model-training.yml`

Git blob:

`a49af5daeb14177a44154ef96b135f64a98a85bf`

Workflow name:

`phase8a-exp052-fit-temporal-support-utility-model-training`

The workflow has exactly one trigger:

`workflow_dispatch`

It has:

- no user inputs;
- no schedule;
- no pull-request trigger;
- read-only repository contents permission;
- read-only Actions permission.

Every execution job explicitly requires:

- event `workflow_dispatch`;
- ref `refs/heads/main`.

## 4. No first-run guard in DEC-166

DEC-166 intentionally does **not** add the one-run rejection guard.

The workflow contains no:

- prior-run query;
- second-run rejection rule;
- run-slot accounting;
- retry authorization;
- replacement authorization.

This is deliberate.

A later decision must first freeze terminal review and then independently verify run history before any one-run authorization is considered.

DEC-166 therefore cannot be treated as dispatch permission merely because a `workflow_dispatch` trigger exists.

## 5. Authorization preflight

Before any matrix job can run, `authorization-preflight` requires:

1. exact manual dispatch on merged `main`;
2. Python `3.12.14`;
3. pinned EXP-052 numerical requirements;
4. successful inspection of the frozen DEC-166 workflow source gate;
5. successful separate historical-execution authorization.

The fifth step currently fails closed because all outer execution flags remain false.

## 6. Frozen dataset matrix

The workflow preserves the accepted nine pair/timeframe historical source identities:

- EURUSD 5m;
- EURUSD 15m;
- EURUSD 1h;
- GBPUSD 5m;
- GBPUSD 15m;
- GBPUSD 1h;
- USDJPY 5m;
- USDJPY 15m;
- USDJPY 1h.

Each matrix row carries the exact accepted feature/outcome artifact id and ZIP SHA-256 already used by the reviewed predecessor workflow.

The readiness source remains:

- artifact id: `10757578276`;
- accepted readiness ZIP SHA-256 already frozen in the workflow source.

No alternate data source or local replacement history is accepted.

## 7. Cell execution shape

The workflow preserves:

- `fail-fast: false`;
- `max-parallel: 3`;
- exactly nine dataset matrix entries;
- horizons exactly `60` and `240` minutes.

Each pair/timeframe matrix job:

1. rechecks the exact DEC-166 execution gate;
2. downloads the exact frozen feature/outcome/readiness artifacts;
3. verifies ZIP SHA-256 identities;
4. extracts only those frozen artifacts;
5. runs the public EXP-052 CLI for both horizons;
6. persists partial cell-result evidence even when later aggregate work cannot complete.

This source shape does not authorize the execution gate it calls.

## 8. Aggregate evidence shape

The aggregate job depends on all matrix jobs and preserves the predecessor fail-closed evidence pattern.

It collects the exact 18 result files and invokes the EXP-052 aggregate CLI.

The output artifact naming prefix is:

`exp052-fit-temporal-support-utility-model-result-evidence-`

The cell artifact naming prefix is:

`exp052-fit-temporal-support-utility-model-cell-results-`

The aggregate evidence must ultimately pass DEC-165 validation, including:

- 18 cells;
- 108 regressors;
- 108 pooled references;
- 432 fit-temporal-support references;
- exact support/pooled/raw cutoff triples;
- canonical fingerprints.

DEC-166 does not produce such evidence because execution remains unauthorized.

## 9. Public CLI

CLI:

`scripts/phase8a_exp052_model_run.py`

Git blob:

`728691476a2285ec4cdec594a020aa5c84b04c5e`

Commands:

- `status`;
- `require-execution`;
- `run-cell`;
- `aggregate`.

The CLI checks the separate execution gate before:

- loading readiness;
- loading authoritative feature/outcome artifacts;
- fitting a model cell;
- compiling aggregate evidence.

It also requires `--code-commit` to equal checkout HEAD.

There is no direct GitHub workflow-dispatch command in the CLI.

## 10. Pinned numerical runtime

Runtime requirements:

`requirements/exp052-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

Python:

`3.12.14`

Pinned packages:

- `numpy==2.5.3`
- `scipy==1.18.1`
- `scikit-learn==1.9.1`
- `joblib==1.6.0`
- `threadpoolctl==3.7.0`
- `cloudpickle==3.1.2`
- `narwhals==2.26.0`
- `polars==1.44.2`
- `polars-runtime-32==1.44.2`

This matches the reviewed predecessor numerical runtime.

## 11. Exact-source execution gate

Execution gate:

`src/fmp/market_learning/model_successor_fit_temporal_support_utility_execution_gate.py`

Git blob:

`139028be1c354a99599a3ed6505a1a4725889c02`

Gate decision:

`DEC-166`

The validator exact-binds:

- DEC-163 protocol;
- DEC-164 training core;
- DEC-165 artifact contract;
- accepted historical artifact loader;
- workflow;
- CLI;
- runtime requirements;
- `pyproject.toml`;
- preprocessing;
- feature schema;
- market-learning contracts;
- market outcomes.

Any bound-byte drift fails closed.

## 12. Execution flags

DEC-166 freezes:

- `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_WORKFLOW_SOURCE_FROZEN = true`;
- `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RUN_DISPATCH_AUTHORIZED = false`;
- `AUTHORITATIVE_FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = false`;
- `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = false`;
- `FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_FIT_AUTHORIZED = false`.

And keeps false:

- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

Calling `require-execution` while these remain false raises before any historical artifact loading or fitting.

## 13. Focused tests

Focused tests:

`tests/test_phase8a_exp052_model_workflow.py`

Git blob:

`3c40d8c8fbcbde98005e394cf15b25fb7629505f`

They verify:

- exact DEC-163/164/165 source bindings;
- all execution flags false;
- fail-closed execution requirement;
- manual-main, input-free workflow shape;
- deliberate absence of a first-run guard;
- exact 9-dataset matrix;
- exact 60/240 horizons;
- Python 3.12.14;
- pinned runtime;
- partial and aggregate evidence naming;
- execution check before readiness/model/aggregate work;
- absence of direct dispatch logic in the CLI.

## 14. Next gate

The next safe gate is a separately frozen attempt-1 terminal-review contract.

That review must predeclare:

- exact expected workflow identity;
- exact job inventory;
- partial artifact handling;
- complete aggregate artifact requirements on success;
- DEC-165 aggregate revalidation;
- no rerun/replacement authorization.

Only after terminal review is frozen may a separate decision independently verify zero prior manual-main EXP-052 runs, add the first-run rejection guard, and consider opening one outer historical result-producing slot.

DEC-166 itself dispatches nothing.
