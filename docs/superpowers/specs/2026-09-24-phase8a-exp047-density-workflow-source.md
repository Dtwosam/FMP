# Phase 8A — EXP-047 Locked Model Workflow Source

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; EXP-047 EXECUTION AUTHORIZATION CLOSED
**Decision:** DEC-116
**Experiment:** EXP-20260924-047

## 1. Purpose

DEC-116 freezes the manual main-only, input-free EXP-047 workflow, CLI, pinned numerical runtime, and fail-closed exact-source execution gate around merged DEC-113/114/115.

DEC-116 does not authorize or dispatch an EXP-047 run.

## 2. Frozen predecessor bindings

DEC-116 binds:

- DEC-113 merge: `060bde94835158d62d47640aaf1a77ec56b483ff`
- DEC-113 protocol blob: `871936729a1090d675f6f5181ef04c8f32494394`
- DEC-114 merge: `3e236169ae71074630ece7d78516d5e6586abe1f`
- DEC-114 density-core blob: `8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945`
- DEC-115 merge: `93f1b25cb4260d6b25f484c33014e322cc1ea9af`
- DEC-115 artifact-runner blob: `2d3997ca97fb4568187be54914fe76e8dbf76ff5`
- historical artifact-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

The gate additionally binds the exact workflow, CLI, runtime, pyproject, preprocessing, feature schema, market contracts, and outcomes source bytes.

## 3. Workflow identity

Workflow:

`.github/workflows/phase8a-exp047-density-model-training.yml`

Git blob:

`7ae75dbca58266736be6a6cdf66bf58b61ec3b63`

Workflow name:

`phase8a-exp047-density-model-training`

The trigger is only:

`workflow_dispatch`

There are no user inputs, schedule trigger, pull-request trigger, or alternate automatic trigger.

The workflow explicitly requires:

- event `workflow_dispatch`;
- branch/ref `main`;
- read-only `contents` and `actions` permissions.

## 4. Pre-authorization semantics

DEC-116 intentionally does **not** add a prior-run rejection guard.

No EXP-047 dispatch/result/fit authorization exists yet, so the authorization preflight fails closed before model-cell execution.

If a later decision authorizes one guarded run, that later decision must separately harden the workflow with the appropriate first-run rejection guard before opening authorization.

## 5. Pinned runtime

Python is frozen at:

`3.12.14`

Runtime file:

`requirements/exp047-model-run.txt`

Git blob:

`d25ab16056b9f5df283147d67b8f401f60ae7520`

Pinned numerical runtime:

```text
numpy==2.5.3
scipy==1.18.1
scikit-learn==1.9.1
joblib==1.6.0
threadpoolctl==3.7.0
cloudpickle==3.1.2
narwhals==2.26.0
polars==1.44.2
polars-runtime-32==1.44.2
```

## 6. Historical artifact matrix

The workflow preserves the exact nine accepted pair/timeframe feature/outcome artifact identities and the exact readiness artifact.

It evaluates both frozen horizons:

- 60m
- 240m

for all:

- EURUSD 5m / 15m / 1h
- GBPUSD 5m / 15m / 1h
- USDJPY 5m / 15m / 1h

All downloaded ZIPs are checked against exact SHA-256 values before extraction.

Readiness artifact:

`10757578276`

## 7. Cell-result preservation

Each pair/timeframe job writes the 60m and 240m cell results under `.results`.

The pair/timeframe artifact is uploaded with `if: always()` and `if-no-files-found: warn` so valid partial historical evidence can survive a later terminal failure.

Artifact namespace:

`exp047-density-model-cell-results-<SYMBOL>-<TIMEFRAME>-<HEAD_SHA>`

## 8. Aggregate evidence

Only after all matrix jobs succeed does the aggregate job download the exact EXP-047 cell artifacts and require exactly 18 result files.

The aggregate artifact namespace is:

`exp047-density-model-result-evidence-<HEAD_SHA>-from-feature-35867307338-outcome-35876715434`

Aggregate evidence is compiled only through the DEC-115 contract.

## 9. CLI

CLI:

`scripts/phase8a_exp047_model_run.py`

Git blob:

`28941013c2cf9942a94667d58ec6b76de9d13cd2`

Commands:

- `status`
- `require-execution`
- `run-cell`
- `aggregate`

The CLI calls the exact DEC-116 execution gate before readiness loading, cell fitting, or aggregate compilation.

It contains no `gh workflow run` command and no dispatch bypass.

## 10. Execution gate

Gate source:

`src/fmp/market_learning/model_successor_density_execution_gate.py`

Git blob:

`8a581384a32c10246d123902c0cb30711456c268`

Decision:

`DEC-116`

The source gate verifies exact bytes for:

- DEC-113 protocol;
- DEC-114 density core;
- DEC-115 density artifact runner;
- historical artifact loader;
- workflow;
- CLI;
- pinned runtime;
- pyproject;
- preprocessing;
- feature schema;
- market-learning contracts;
- outcome source.

Any byte drift fails closed.

## 11. Authorization state

DEC-116 sets:

`DENSITY_MODEL_WORKFLOW_SOURCE_FROZEN = true`

and keeps false:

- model-run dispatch authorization;
- authoritative density-model result execution;
- model-protocol result production;
- model fitting;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

`require_authoritative_density_model_execution(...)` therefore fails before historical artifact loading or model work.

## 12. No terminal-result policy yet

DEC-116 freezes only workflow/CLI/gate source.

Before any future EXP-047 one-run authorization, a separate decision must predeclare the exact terminal-result review contract for success, failure, cancellation, and timeout.

This ordering prevents post-result review rules from being invented after seeing an EXP-047 result.

## 13. Next gate

The next safe source-only step is to predeclare the EXP-047 terminal-result review contract.

No EXP-047 workflow dispatch, fit, historical result production, prospective shadow, or trading action is authorized by DEC-116.
