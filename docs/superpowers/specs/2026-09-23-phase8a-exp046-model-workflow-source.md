# Phase 8A — EXP-046 Locked Model Workflow Source

**Date:** 2026-09-23
**Status:** SOURCE-ONLY; EXP-046 EXECUTION AUTHORIZATION CLOSED
**Decision:** DEC-107
**Experiment:** EXP-20260923-046

## 1. Purpose

DEC-107 freezes the manual GitHub Actions workflow, fail-closed CLI, pinned runtime, and exact-source execution gate around the merged DEC-104/105/106 EXP-046 sources.

DEC-107 does not authorize a workflow run, model fit, historical result, rerun, promotion, prospective shadow/demo execution, broker mutation, live order, real-money action, or trading.

## 2. Frozen predecessor identities

DEC-107 binds:

- DEC-104 merge: `bb2ee82a7d081138e1c0847e8c406d6c3ac68589`
- DEC-104 protocol blob: `4c8da2259f1fd6d27862a50a47a0d8108b58bc2e`
- DEC-105 merge: `7aa3d86f6c1fce61dd7e35d9ba9830b1fa7355b5`
- DEC-105 training-core blob: `6733d3c530fba944b9ea0c62783ed2110552e532`
- DEC-106 merge: `f1316addb56741fcd9b6b12f57e66b677c515188`
- DEC-106 artifact/evidence runner blob: `2d8d6f82cd15f5bdb75bb384fe3efe1dc560857a`
- historical artifact-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

## 3. Workflow identity

Workflow file:

`.github/workflows/phase8a-exp046-stability-model-training.yml`

Workflow name:

`phase8a-exp046-stability-model-training`

Git blob:

`eb4690091a92021bb0c60f153800dc6cd9111cd5`

The workflow is:

- manual-only via `workflow_dispatch`;
- input-free;
- main-only;
- read-only for repository contents and Actions artifacts;
- pinned to Python 3.12.14;
- gated before every result-producing job;
- matrixed across exactly EURUSD/GBPUSD/USDJPY × 5m/15m/1h;
- fixed to exactly 60m and 240m horizons;
- fixed to the exact persisted feature/outcome/readiness artifact ids and ZIP hashes already used by the reviewed EXP-045 run;
- configured with `fail-fast: false` and `max-parallel: 3`;
- configured to preserve pair/timeframe partial evidence with `if: always()`, hidden files included, and missing partial files warned rather than masking an upstream failure;
- configured to aggregate only after all matrix jobs succeed.

The source-only workflow contains no prior-run guard yet. A later authorization decision must add the one-run rejection guard before opening execution.

## 4. CLI identity

CLI:

`scripts/phase8a_exp046_model_run.py`

Git blob:

`525be24ec365d50f6f7a390f7eb4f6ac370440b9`

Commands:

- `status`
- `require-execution`
- `run-cell`
- `aggregate`

Every command other than `status` passes through the DEC-107 execution gate before any authoritative model fitting or aggregation can occur.

The CLI also requires the supplied execution commit to equal checkout HEAD.

## 5. Runtime identity

Runtime lock:

`requirements/exp046-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

Pinned runtime:

- numpy 2.5.3
- scipy 1.18.1
- scikit-learn 1.9.1
- joblib 1.6.0
- threadpoolctl 3.7.0
- cloudpickle 3.1.2
- narwhals 2.26.0
- polars 1.44.2
- polars-runtime-32 1.44.2

The requirements bytes are intentionally identical to the frozen EXP-045 numerical runtime.

## 6. Execution gate identity

Gate source:

`src/fmp/market_learning/model_successor_stability_execution_gate.py`

Git blob:

`d20ab76ec7ce112f6a1ca5485e78a395bacdf49b`

The gate validates the exact Git blobs for:

- DEC-106 artifact/evidence runner;
- DEC-105 training core;
- DEC-104 protocol;
- historical artifact loader;
- DEC-107 workflow;
- DEC-107 CLI;
- DEC-107 runtime requirements;
- pyproject;
- preprocessing;
- feature schema;
- market-learning contracts;
- outcome construction.

The unchanged support blobs are:

- pyproject: `de850a1ba397fc69ba634ecf178d732b5012c378`
- preprocessing: `fcc42f45b9588d38311bc66bc454e6ea0a563e54`
- feature schema: `afbddc84676faadb8660b4da03c6abeb10cd2a13`
- market contracts: `4c5a75232e66715c0829e545d8659f59fb8b7724`
- outcomes: `c83fefd4252b2fe426af97686f86e43021760c77`

Any byte drift fails closed.

## 7. Source-only authorization state

DEC-107 sets:

`STABILITY_MODEL_WORKFLOW_SOURCE_FROZEN = true`

and keeps false:

- model-run dispatch authorization;
- authoritative historical model-result execution;
- model-protocol result authorization;
- model-fit authorization;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

The `require-execution` command therefore fails before model fitting under DEC-107.

## 8. Result artifact namespace

If a later separately merged decision authorizes execution without changing the frozen result format, the workflow source is predeclared to persist:

- pair/timeframe artifacts:
  `exp046-stability-model-cell-results-<SYMBOL>-<TIMEFRAME>-<HEAD_SHA>`
- aggregate artifact:
  `exp046-stability-model-result-evidence-<HEAD_SHA>-from-feature-35867307338-outcome-35876715434`

DEC-107 itself produces none of these artifacts.

## 9. No execution shortcut

DEC-107 introduces no:

- push trigger;
- schedule;
- repository-dispatch trigger;
- workflow inputs;
- automatic dispatch;
- rerun path;
- replacement-run authorization;
- broker or order path.

Manual presence of the workflow file is not execution authorization.

## 10. Next gate

Before any EXP-046 result-producing authorization, a later separate decision should freeze terminal-result review for both success and non-success outcomes.

Only after that review contract is frozen may another separate decision consider adding a one-run prior-run guard and authorizing at most one historical EXP-046 result-producing run.
