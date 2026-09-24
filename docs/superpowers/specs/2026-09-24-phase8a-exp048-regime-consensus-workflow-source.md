# Phase 8A — EXP-048 Locked Regime-Consensus Model Workflow Source

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; EXP-048 EXECUTION AUTHORIZATION CLOSED
**Decision:** DEC-126
**Experiment:** EXP-20260924-048

## 1. Purpose

DEC-126 freezes the manual main-only, input-free EXP-048 workflow, model CLI, pinned numerical runtime, and fail-closed exact-source execution gate around merged DEC-123/124/125.

DEC-126 does not authorize or dispatch an EXP-048 run.

## 2. Frozen predecessor bindings

DEC-126 binds:

- DEC-123 merge: `39674f482e57922ac61fb0a6dff15a5ef621efd3`
- DEC-123 protocol blob: `39b6b3f5adc7f34ffd8cebcf881138d6ca3eab84`
- DEC-124 merge: `83c5b40eebae884cda9b2b65a8494dcd63bcbb7a`
- DEC-124 regime-consensus core blob: `d902f9601ef3b04e0deaead18951d43350cb09be`
- DEC-125 merge: `c695ea8add9227896d26b5641f4f8b51f4bb310e`
- DEC-125 artifact-runner blob: `b62f3ff775f30c96fa2f6f1a15256fd696ea5c2e`
- historical artifact-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

The gate additionally binds the exact workflow, CLI, runtime, pyproject, preprocessing, feature schema, market contracts, and outcomes source bytes.

## 3. Workflow identity

Workflow:

`.github/workflows/phase8a-exp048-regime-consensus-model-training.yml`

Git blob:

`09d6d9fa710d18637648de23ae45968628032765`

Workflow name:

`phase8a-exp048-regime-consensus-model-training`

The trigger is only:

`workflow_dispatch`

There are no user inputs, schedule trigger, pull-request trigger, push trigger, or alternate automatic trigger.

The workflow requires:

- event `workflow_dispatch`;
- branch/ref `main`;
- read-only `contents` and `actions` permissions.

## 4. Pre-authorization semantics

DEC-126 intentionally has **no first-run rejection guard**.

No EXP-048 dispatch/result/fit authorization exists, so the authorization preflight must fail closed at:

`require-authoritative-regime-consensus-model-execution`

before any matrix historical artifact download or model fit can occur.

A later authorization decision may add a first-run rejection guard only after a terminal-result review contract has been frozen and zero prior manual-main runs are independently verified.

## 5. Pinned runtime

Python is frozen at:

`3.12.14`

Runtime file:

`requirements/exp048-model-run.txt`

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

This is byte-identical to the predecessor numerical runtime.

## 6. Historical artifact matrix

The workflow preserves the exact nine accepted pair/timeframe feature/outcome artifact identities and exact readiness artifact.

It evaluates both frozen horizons:

- 60m
- 240m

for:

- EURUSD 5m / 15m / 1h
- GBPUSD 5m / 15m / 1h
- USDJPY 5m / 15m / 1h

All downloaded ZIPs are verified against exact SHA-256 values before extraction.

Readiness artifact:

`10757578276`

## 7. Cell-result preservation

Each pair/timeframe job writes the 60m and 240m EXP-048 regime-consensus results under `.results`.

The pair/timeframe artifact is uploaded with `if: always()` and `if-no-files-found: warn` so valid partial historical evidence can survive a later terminal failure.

Artifact namespace:

`exp048-regime-consensus-model-cell-results-<SYMBOL>-<TIMEFRAME>-<HEAD_SHA>`

## 8. Aggregate evidence

Only after all matrix jobs succeed does the aggregate job download the exact EXP-048 cell artifacts and require exactly 18 result files.

Aggregate artifact namespace:

`exp048-regime-consensus-model-result-evidence-<HEAD_SHA>-from-feature-35867307338-outcome-35876715434`

Aggregate evidence is compiled only through DEC-125.

## 9. Model CLI

CLI:

`scripts/phase8a_exp048_model_run.py`

Git blob:

`f4a6941512824c1d60bff98175dd2fce9353aa68`

Commands:

- `status`
- `require-execution`
- `run-cell`
- `aggregate`

The CLI calls the exact DEC-126 execution gate before readiness loading, historical artifact loading, model fitting, or aggregate compilation.

It contains no `gh workflow run` command and no dispatch bypass.

## 10. Execution gate

Gate source:

`src/fmp/market_learning/model_successor_regime_consensus_execution_gate.py`

Git blob:

`b70e2a8854439f20b25a9549820fad9c95612390`

Decision:

`DEC-126`

The source gate verifies exact bytes for:

- DEC-123 protocol;
- DEC-124 regime-consensus core;
- DEC-125 artifact runner;
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

## 11. Focused tests

Focused tests:

`tests/test_phase8a_exp048_model_workflow.py`

Git blob:

`41670501a441396ea1a17ad93ff009243a6102d8`

They require:

- exact source identities;
- source-only non-executable gate state;
- manual-main, input-free workflow;
- no first-run guard yet;
- exact nine-dataset matrix;
- exact 60m/240m loop;
- Python 3.12.14 and pinned numerical runtime;
- partial-cell evidence upload on failure;
- exact aggregate namespace;
- execution gate before readiness/model/aggregate operations;
- no CLI dispatch path.

## 12. Authorization state

DEC-126 sets:

`REGIME_CONSENSUS_MODEL_WORKFLOW_SOURCE_FROZEN = true`

and keeps false:

- model-run dispatch authorization;
- authoritative regime-consensus result execution;
- model-protocol result production;
- model fitting;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

`require_authoritative_regime_consensus_model_execution(...)` therefore fails closed before historical data or model work.

## 13. No terminal-result policy yet

DEC-126 freezes only workflow/CLI/runtime/gate source.

Before any future EXP-048 one-run authorization, a separate decision must predeclare the exact terminal-result review contract for success, failure, cancellation, and timeout.

This ordering prevents post-result review rules from being invented after seeing an EXP-048 result.

## 14. Next gate

The next safe source-only step is to predeclare the EXP-048 terminal-result review contract.

No EXP-048 workflow dispatch, model fit, historical result production, prospective shadow, or trading action is authorized by DEC-126.
