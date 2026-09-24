# Phase 8A — EXP-050 Temporal-Jackknife Utility Workflow Source

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY; EXP-050 EXECUTION AUTHORIZATION CLOSED
**Decision:** DEC-144
**Experiment:** EXP-20260924-050

## 1. Purpose

DEC-144 freezes the manual-main workflow, CLI, pinned numerical runtime, and exact-source execution gate around the merged DEC-141 protocol, DEC-142 deterministic training core, and DEC-143 artifact/evidence contract.

This decision creates the source shape required for a later historical result run.

It does **not** authorize workflow dispatch, model fitting, model-protocol result production, or authoritative historical result execution.

## 2. Frozen source chain

DEC-144 binds:

- DEC-141 merge: `4729da0e769f76f44b97ff6349ee25c5b7c0f5c7`
- DEC-141 protocol blob: `b41b817b03aa0cc03a9d893227caa399b46d3cf8`
- DEC-142 merge: `fa6fd14a880a84a44795efe4099679ed0f642497`
- DEC-142 training-core blob: `ec97a9941af052d6e223e4bafab9a9989ec57ff0`
- DEC-143 merge: `f0f584f2bfa1d6f0858af46312e41ffde5fe7d71`
- DEC-143 artifact/evidence blob: `60076ccb45b3468bce68f88f667225e0b5662d92`
- accepted historical data-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

The gate also binds the exact workflow, CLI, runtime requirements, pyproject, preprocessing, feature schema, market-learning contracts, and outcome-schema bytes.

Any bound-byte drift fails closed.

## 3. Workflow identity

Workflow:

`.github/workflows/phase8a-exp050-temporal-jackknife-utility-model-training.yml`

Git blob:

`ec8ed4ab3f0b8a18ffc735af92172e059ed29955`

Workflow name:

`phase8a-exp050-temporal-jackknife-utility-model-training`

The workflow is:

- manual `workflow_dispatch` only;
- input-free;
- `main` branch only;
- read-only GitHub contents/actions permissions;
- Python 3.12.14;
- no schedule;
- no pull-request trigger;
- no alternate dispatch trigger.

DEC-144 intentionally does **not** add a first-run guard. That guard belongs only to a later one-run authorization decision after terminal review is frozen and zero prior manual-main EXP-050 runs are independently verified.

## 4. Frozen historical matrix

The workflow preserves the exact accepted nine pair/timeframe historical source cells:

- EURUSD 5m / 15m / 1h
- GBPUSD 5m / 15m / 1h
- USDJPY 5m / 15m / 1h

Each matrix job evaluates the exact two horizons:

- 60 minutes
- 240 minutes

The workflow uses the already accepted EXP-044 feature, outcome, and readiness artifacts with their exact artifact IDs and ZIP SHA-256 values.

No new historical acquisition is performed.

## 5. Partial-result preservation

Each pair/timeframe job may upload any cell results that exist if a later separately authorized execution terminates after partial work.

Artifact namespace:

`exp050-temporal-jackknife-utility-model-cell-results-<symbol>-<timeframe>-<commit>`

Partial persistence is evidence preservation only. It does not create a complete aggregate result.

## 6. Aggregate evidence

The aggregate job requires the full matrix and compiles exactly 18 cell results through the DEC-143 evidence contract.

Aggregate artifact namespace:

`exp050-temporal-jackknife-utility-model-result-evidence-<commit>-from-feature-35867307338-outcome-35876715434`

The compiler cannot invent missing cells or bypass DEC-143 validation.

## 7. CLI

CLI:

`scripts/phase8a_exp050_model_run.py`

Git blob:

`70c5e9b8d22888b9727e234fd80ea3e3ba4e5e09`

Supported commands are limited to:

- `status`
- `require-execution`
- `run-cell`
- `aggregate`

The CLI contains no workflow-dispatch command.

Every result-producing command calls the execution requirement before readiness loading, historical artifact loading, fitting, or aggregation.

The supplied code commit must equal checkout HEAD.

## 8. Runtime lock

Requirements:

`requirements/exp050-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

Pinned packages:

- numpy 2.5.3
- scipy 1.18.1
- scikit-learn 1.9.1
- joblib 1.6.0
- threadpoolctl 3.7.0
- cloudpickle 3.1.2
- narwhals 2.26.0
- polars 1.44.2
- polars-runtime-32 1.44.2

Authorized Python version:

`3.12.14`

The numerical runtime is unchanged from EXP-049 so the jackknife fit-view change does not silently introduce a library/runtime change.

## 9. Execution gate

Gate source:

`src/fmp/market_learning/model_successor_temporal_jackknife_utility_execution_gate.py`

Git blob:

`4814f0db86bec943d7282ab13586559b1eb8caa7`

Decision:

`DEC-144`

The gate first verifies that every upstream DEC-141/142/143 protocol/core/runner execution and fit flag remains false.

DEC-144 state:

- workflow source frozen: true
- run dispatch authorized: false
- authoritative historical result execution authorized: false
- model-protocol result authorized: false
- model fit authorized: false
- promotion authorized: false
- shadow authorized: false
- demo order authorized: false
- broker mutation authorized: false
- live order authorized: false
- real-money authorized: false
- trading authorized: false

Therefore `require-execution` fails closed at the dispatch-authorization check before result production.

## 10. Focused tests

Tests:

`tests/test_phase8a_exp050_model_workflow.py`

Git blob:

`cce991971cef68fdeeb14cb2c26ecf54ba35985f`

They verify:

- exact DEC-141/142/143 identities;
- exact workflow/CLI/runtime source bindings;
- all result/fit/trading authorizations remain false;
- `require-execution` fails closed;
- workflow is manual-main and input-free;
- no first-run authorization guard exists yet;
- exact nine-cell matrix and 60m/240m horizons;
- exact pinned Python/runtime requirements;
- partial and aggregate evidence namespaces;
- CLI gate ordering before readiness/model/aggregate actions;
- absence of a CLI dispatch bypass.

## 11. Next gate

Before any EXP-050 historical result authorization, a separate decision must predeclare the exact terminal-result review contract.

That review must define before any run exists:

- accepted workflow identity and attempt number;
- required job inventory;
- required cell/aggregate artifact inventory;
- DEC-143 aggregate-evidence revalidation rules;
- failed/cancelled/timed-out first-attempt handling;
- rerun/replacement policy;
- terminal review states.

Only after that review is frozen may another separate decision consider a one-run historical authorization.

DEC-144 itself dispatches nothing and creates no historical result.
