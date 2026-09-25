# Phase 8A — EXP-053 Fit-Temporal Feature-Support Model Workflow Source

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-177
**Experiment:** EXP-20260925-053

## 1. Purpose

DEC-177 freezes the manual-main workflow source, public CLI, pinned numerical runtime, and exact-source execution gate for EXP-053.

This makes the future historical execution path inspectable without opening it.

DEC-177 does **not** authorize workflow dispatch, historical result execution, model fit, protocol-result production, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.

## 2. Frozen source chain

DEC-177 binds:

- DEC-174 protocol merge: `9687eb8ea3920e87d6681adf7366a3ce0bba7154`;
- DEC-174 protocol blob: `11ae3fc8e68687cc04957ed9243d8c5969227fb8`;
- DEC-175 training-core merge: `60abce7c2674f9c25e4132037c9eb24cab1baf22`;
- DEC-175 training-core blob: `4fd0e48302f97e188a8124e1543bde0ffdb43b6f`;
- DEC-176 artifact-contract merge: `a37462015ada9499fccf7ebb0a9f515e74bff1b6`;
- DEC-176 artifact/evidence blob: `431c879bf26d88e33bdf0f0965ec62566b1a3e22`;
- accepted historical artifact-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`.

The gate independently requires the DEC-174/175/176 source-level execution and fit locks to remain false.

## 3. Workflow identity

Workflow:

`.github/workflows/phase8a-exp053-fit-temporal-feature-support-utility-model-training.yml`

Git blob:

`0a6704f75e83b06b7555dbb9dc912cda31443bbc`

Workflow name:

`phase8a-exp053-fit-temporal-feature-support-utility-model-training`

The only trigger is `workflow_dispatch`.

There are no inputs, schedules, or pull-request triggers.

Permissions remain read-only for repository contents and Actions.

Every execution job explicitly requires manual dispatch on `refs/heads/main`.

## 4. Deliberate absence of a first-run guard

DEC-177 intentionally contains no prior-run query or first-run rejection guard.

That guard belongs only after terminal review is frozen and a separate decision independently verifies run history.

Therefore the mere presence of `workflow_dispatch` is not dispatch authorization.

## 5. Authorization preflight

Before any matrix work can run, authorization-preflight requires:

1. exact manual dispatch on merged main;
2. Python 3.12.14;
3. the pinned EXP-053 numerical runtime;
4. successful DEC-177 source inspection;
5. successful separate historical-execution authorization.

The fifth step currently fails closed because all outer execution flags remain false.

## 6. Frozen historical matrix

The workflow preserves exactly nine pair/timeframe sources:

- EURUSD 5m / 15m / 1h;
- GBPUSD 5m / 15m / 1h;
- USDJPY 5m / 15m / 1h.

Each row carries the same accepted immutable feature/outcome artifact IDs and ZIP SHA-256 values used by the reviewed predecessor chain.

Readiness remains artifact `10757578276` with the exact frozen ZIP SHA-256.

No alternate dataset or regenerated history is accepted.

## 7. Cell execution shape

The workflow preserves:

- `fail-fast: false`;
- `max-parallel: 3`;
- nine matrix entries;
- horizons exactly 60 and 240 minutes.

Each matrix job rechecks the execution gate before downloading accepted artifacts, verifies ZIP hashes, resolves exact extracted roots, and invokes the public EXP-053 CLI for both horizons.

Partial cell evidence is uploaded with `if: always()`.

## 8. Aggregate evidence

The aggregate job depends on all matrix jobs, downloads the exact 18 cell-result files, and invokes the EXP-053 aggregate CLI.

Cell artifact prefix:

`exp053-fit-temporal-feature-support-utility-model-cell-results-`

Aggregate prefix:

`exp053-fit-temporal-feature-support-utility-model-result-evidence-`

The aggregate name also binds the accepted feature/outcome workflow identities.

Any future complete result must pass DEC-176 validation, including:

- 18 cells;
- 108 regressors;
- 108 pooled references;
- 432 fit-temporal utility-support references;
- 216 fit-temporal feature-support references;
- exact feature/utility-support/pooled/raw cutoff quadruples;
- canonical fingerprints.

DEC-177 cannot produce this evidence while execution remains unauthorized.

## 9. Public CLI

CLI:

`scripts/phase8a_exp053_model_run.py`

Git blob:

`dbd146100d81be6ffc492de448d8dc4e0a2f4e73`

Commands:

- `status`;
- `require-execution`;
- `run-cell`;
- `aggregate`.

The CLI checks the separate execution gate before loading readiness, accepted feature/outcome artifacts, running a model cell, or compiling aggregate evidence.

`--code-commit` must equal checkout HEAD.

The CLI contains no direct workflow-dispatch command.

## 10. Numerical runtime

Requirements:

`requirements/exp053-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

Python:

`3.12.14`

Pinned packages are unchanged from EXP-052:

- numpy 2.5.3;
- scipy 1.18.1;
- scikit-learn 1.9.1;
- joblib 1.6.0;
- threadpoolctl 3.7.0;
- cloudpickle 3.1.2;
- narwhals 2.26.0;
- polars 1.44.2;
- polars-runtime-32 1.44.2.

## 11. Exact-source gate

Gate:

`src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_execution_gate.py`

Git blob:

`600ea84946fe908d143f3fbe2082b3505733cdf5`

Gate decision:

`DEC-177`

It exact-binds DEC-174 protocol, DEC-175 core, DEC-176 artifact contract, accepted historical loader, workflow, CLI, runtime requirements, project metadata, preprocessing, feature schema, market-learning contracts, and outcomes.

Any bound-byte drift fails closed.

## 12. Execution state

DEC-177 freezes:

- workflow source frozen: true;
- workflow dispatch authorized: false;
- authoritative model-result execution authorized: false;
- protocol-result authorized: false;
- model fit authorized: false.

Promotion, shadow, demo order, broker mutation, live order, real-money action, and trading remain false.

Calling `require-execution` while these flags remain false raises before historical artifact loading or fitting.

## 13. Focused tests

Focused tests:

`tests/test_phase8a_exp053_model_workflow.py`

Git blob:

`8a9e93f1a8dede52ec4689550327f5b0e8292928`

They verify exact DEC-174/175/176 bindings, all execution flags false, fail-closed execution requirement, manual-main/input-free workflow shape, deliberate absence of a first-run guard, exact matrix/horizons/runtime, partial/aggregate evidence naming, execution check ordering, and absence of direct dispatch logic in the CLI.

## 14. Next gate

The next safe gate is a separately frozen attempt-1 terminal-review contract.

Only after terminal review is frozen may a later decision independently verify zero prior manual-main EXP-053 runs, add the first-run rejection guard, and consider opening one outer historical result-producing slot.

DEC-177 itself dispatches nothing.
