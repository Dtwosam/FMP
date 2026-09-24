# Phase 8A — EXP-049 Regime-Utility Workflow Source

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY; EXP-049 EXECUTION AUTHORIZATION CLOSED
**Decision:** DEC-135
**Experiment:** EXP-20260924-049

## Purpose

DEC-135 freezes the manual-main workflow, CLI, pinned numerical runtime, and exact-source execution gate around the merged DEC-132 protocol, DEC-133 deterministic training core, and DEC-134 artifact/evidence contract.

This decision creates the source shape required for a later historical result run. It does not authorize dispatch, model fitting, protocol-result production, or historical result execution.

## Frozen source chain

The execution gate binds:

- DEC-132 merge: `d17326eebf6b456211225d7bad3a182a0307b707`
- DEC-132 protocol blob: `ad2fcb22656fc7a1490f4cdf87fb25c62895a1ac`
- DEC-133 merge: `a6420e35a9219c81e65c5179843488f94b6668d3`
- DEC-133 core blob: `e1018b20210b7bb8d666071d8eb878aba5899111`
- DEC-134 merge: `1576336d8faaf146aaa11d4213b21e69134ceaa7`
- DEC-134 artifact/evidence runner blob: `6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13`
- accepted historical data loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

The gate also binds the exact workflow, CLI, runtime requirements, pyproject, preprocessing, feature schema, market-learning contracts, and outcome-schema bytes.

Any bound byte drift fails closed.

## Workflow identity

Workflow:

`.github/workflows/phase8a-exp049-regime-utility-model-training.yml`

Git blob:

`955152835ec1cedf39d6d31e54d6028a7953fab5`

Workflow name:

`phase8a-exp049-regime-utility-model-training`

The workflow is:

- manual `workflow_dispatch` only;
- input-free;
- `main` branch only;
- read-only GitHub contents/actions permissions;
- Python 3.12.14;
- no schedule;
- no pull-request trigger;
- no alternate dispatch trigger.

DEC-135 intentionally does not add a first-run guard. That guard belongs to a later authorization decision only after terminal review is frozen and zero prior runs are independently verified.

## Frozen historical matrix

The workflow retains the exact nine accepted pair/timeframe source cells:

- EURUSD 5m / 15m / 1h
- GBPUSD 5m / 15m / 1h
- USDJPY 5m / 15m / 1h

Each matrix job evaluates the exact two horizons:

- 60 minutes
- 240 minutes

The workflow uses the already accepted EXP-044 feature, outcome, and readiness artifacts with their exact artifact IDs and ZIP SHA-256 values.

No new historical acquisition is performed.

## Partial-result preservation

Each pair/timeframe job may upload any cell results that exist if a later authorized execution terminates after partial work.

The artifact namespace is bound to:

`exp049-regime-utility-model-cell-results-<symbol>-<timeframe>-<commit>`

Partial persistence is evidence preservation only. It does not convert an incomplete run into an aggregate result.

## Aggregate evidence

The aggregate job requires all matrix jobs and compiles exactly 18 cell results through the DEC-134 aggregate-evidence contract.

Aggregate artifact namespace:

`exp049-regime-utility-model-result-evidence-<commit>-from-feature-35867307338-outcome-35876715434`

The aggregate compiler cannot invent missing cells and cannot bypass DEC-134 cell validation.

## CLI

CLI:

`scripts/phase8a_exp049_model_run.py`

Git blob:

`cba5ece4eda8e02a7ca07a780d8caa69a239e094`

Supported commands are limited to:

- `status`
- `require-execution`
- `run-cell`
- `aggregate`

The CLI contains no workflow dispatch command.

For every result-producing command, the execution requirement is evaluated before readiness loading, historical artifact loading, model fitting, or aggregation.

The CLI also requires the supplied code commit to equal the current checkout HEAD.

## Runtime lock

Requirements:

`requirements/exp049-model-run.txt`

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

The numerical runtime matches the predecessor model-run environment rather than silently changing library behavior during the objective change.

## Execution gate

Gate source:

`src/fmp/market_learning/model_successor_regime_utility_execution_gate.py`

Git blob:

`9d2ffc670a1572febb0e4a29bfda426f8252e5ee`

Decision:

`DEC-135`

The gate verifies that all upstream protocol, training-core, and artifact-runner execution/fit flags remain false before accepting the frozen source identity.

DEC-135 state:

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

Therefore `require-execution` fails closed at the dispatch-authorization check.

## Focused tests

Tests:

`tests/test_phase8a_exp049_model_workflow.py`

Git blob:

`906474f199d595579b29c96b683299fa269c7e8d`

They verify:

- exact DEC-132/133/134 identities;
- exact workflow/CLI/runtime source bindings;
- all execution and trading authorizations remain false;
- `require-execution` fails closed;
- workflow is manual-main, input-free, and trigger-restricted;
- no first-run authorization guard exists yet;
- exact nine-cell matrix and 60m/240m horizons;
- exact pinned Python/runtime requirements;
- partial and aggregate evidence namespaces;
- CLI gate ordering before readiness/model/aggregate actions;
- absence of a CLI dispatch bypass.

## Next gate

Before any historical result authorization, a separate decision must predeclare the exact terminal-result review contract.

That review must define, before a result exists:

- accepted workflow identity and attempt number;
- required job inventory;
- required cell and aggregate artifact inventory;
- aggregate-evidence revalidation rules;
- failed/cancelled/timed-out first-run handling;
- rerun/replacement policy;
- terminal review states.

Only after that review is frozen may another separate decision consider a one-run historical authorization.

DEC-135 itself dispatches nothing and creates no historical model result.
