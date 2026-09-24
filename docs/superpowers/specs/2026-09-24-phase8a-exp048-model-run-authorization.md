# Phase 8A — EXP-048 Single Historical Model-Run Authorization

**Date:** 2026-09-24
**Status:** AUTHORIZED SOURCE; NO EXP-048 RUN DISPATCHED BY THIS DECISION
**Decision:** DEC-128
**Experiment:** EXP-20260924-048

## 1. Preconditions

Before DEC-128 source work, GitHub reported zero manual-main runs for:

`phase8a-exp048-regime-consensus-model-training`

DEC-127 terminal review was already merged.

DEC-128 therefore considers only the first guarded historical EXP-048 result-producing attempt.

## 2. Frozen predecessor bindings

DEC-128 binds:

- DEC-123 protocol/core lineage;
- DEC-124 regime-consensus training core;
- DEC-125 artifact/evidence contract;
- DEC-126 locked workflow source merge: `e2713ab33648901d42f9a9e1c4b8e7f0ff7920a6`;
- DEC-126 pre-authorization workflow blob: `09d6d9fa710d18637648de23ae45968628032765`;
- DEC-126 CLI blob: `f4a6941512824c1d60bff98175dd2fce9353aa68`;
- DEC-126 pre-authorization gate blob: `b70e2a8854439f20b25a9549820fad9c95612390`;
- DEC-127 review merge: `589782a92f9f1db2008bff99065cb070017311ca`;
- DEC-127 review blob: `0cd943cb4bb8780a6adfab02b0743c8415dcd5fe`.

## 3. First-run rejection guard

DEC-128 hardens the workflow before runtime installation or model fitting.

The authorization-preflight now:

1. fetches the exact current workflow run by `GITHUB_RUN_ID`;
2. verifies exact workflow name/path, event `workflow_dispatch`, and branch `main`;
3. lists manual-main runs for the exact EXP-048 workflow;
4. excludes only the current `GITHUB_RUN_ID`;
5. fails if any other prior manual-main EXP-048 run exists.

The hardened workflow Git blob is:

`89a2c78af2c3d0925d7c8a2773af9291caacd95d`

## 4. Single-attempt semantics

The first manual-main EXP-048 workflow attempt consumes the DEC-128 run slot regardless of whether it:

- succeeds;
- fails;
- is cancelled;
- times out.

No automatic rerun or replacement is authorized.

GitHub rerun actions are not authorized by DEC-128.

## 5. Outer authorization layer

The authorized execution-gate source is:

`src/fmp/market_learning/model_successor_regime_consensus_execution_gate.py`

Git blob:

`3312667537eedfc2cd41d1ec91c877e1b05770f9`

It records:

`REGIME_CONSENSUS_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-128"`

and opens only the outer historical result-producing flags:

- `REGIME_CONSENSUS_MODEL_RUN_DISPATCH_AUTHORIZED = true`
- `AUTHORITATIVE_REGIME_CONSENSUS_MODEL_RESULT_EXECUTION_AUTHORIZED = true`
- `REGIME_CONSENSUS_MODEL_PROTOCOL_RESULT_AUTHORIZED = true`
- `REGIME_CONSENSUS_MODEL_FIT_AUTHORIZED = true`

The underlying DEC-123 protocol, DEC-124 core, and DEC-125 artifact-runner source-level execution/fit authorization constants remain false and are explicitly checked as frozen dependencies.

## 6. What remains unchanged

DEC-128 does not change:

- three exact fit-regime windows;
- HGB-only model-family boundary;
- logistic exclusion;
- unanimous directional-consensus rule;
- minimum agreed-direction consensus confidence;
- 250/500/1000 candidate-density anchors;
- HGB model configuration;
- feature columns;
- target;
- chronology;
- 250-candidate aggregate floor;
- aggregate financial gate;
- four-window stability screen;
- validation/holdout scenarios;
- historical feature/outcome/readiness artifacts;
- pinned Python 3.12.14 numerical runtime;
- DEC-125 artifact/evidence validation;
- DEC-127 terminal-review semantics.

## 7. Mandatory terminal review

Any terminal EXP-048 run must be reviewed through DEC-127.

Success requires the exact complete 11-job/10-artifact shape and DEC-125 aggregate-evidence revalidation.

Failure/cancellation/timeout may preserve valid partial cell evidence but cannot claim aggregate result evidence.

DEC-128 does not authorize a replacement after any terminal outcome.

## 8. No dispatch by this decision

DEC-128 changes source authorization only.

It does **not** invoke:

`gh workflow run phase8a-exp048-regime-consensus-model-training.yml --ref main -R Dtwosam/FMP`

A separate one-way operator/execution step is required after DEC-128 merges.

## 9. Downstream authorization state

DEC-128 keeps false:

- replacement model-run authorization;
- promotion;
- prospective shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

No accepted candidate exists merely because one historical result run is authorized.

## 10. Next gate

The next safe source step is a clean-main, one-way operator that can expose exactly one dispatch only while no EXP-048 run exists and routes any terminal evidence through DEC-127.

DEC-128 itself dispatches nothing.
