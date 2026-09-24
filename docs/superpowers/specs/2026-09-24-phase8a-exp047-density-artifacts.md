# Phase 8A — EXP-047 Artifact-Backed Runner and Evidence Contract

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; AUTHORITATIVE EXP-047 RESULT EXECUTION CLOSED
**Decision:** DEC-115
**Experiment:** EXP-20260924-047

## 1. Purpose

DEC-115 freezes the artifact-backed historical-data runner and deterministic aggregate evidence contract around merged DEC-113/DEC-114.

It reuses only the exact verified historical feature/outcome/readiness artifacts already accepted for EXP-044/045/046.

DEC-115 remains non-executable for authoritative EXP-047 fitting/result production.

## 2. Frozen source bindings

DEC-115 binds:

- DEC-113 merge: `060bde94835158d62d47640aaf1a77ec56b483ff`
- DEC-113 protocol blob: `871936729a1090d675f6f5181ef04c8f32494394`
- DEC-114 merge: `3e236169ae71074630ece7d78516d5e6586abe1f`
- DEC-114 training-core blob: `8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945`
- verified historical artifact-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

Any byte drift fails closed.

## 3. Historical data identity

The runner reuses the exact authoritative historical evidence:

- feature run: `35867307338`
- outcome run: `35876715434`
- readiness artifact: `10757578276`

No alternate dataset, regeneration, or refreshed feature/outcome source is introduced by DEC-115.

## 4. Cell-result contract

Every EXP-047 cell result must match the exact DEC-113/114 protocol/core identity and one of the 18 frozen symbol/timeframe/horizon cells.

Fit records must contain exactly:

- HGB: `FITTED`, one fit attempt, valid preprocessor/model fingerprints;
- logistic regression: `EXCLUDED_BY_DEC112_DEC113`, zero fit attempts.

No logistic fitted/non-converged variant is permitted in EXP-047 evidence.

## 5. Density-variant inventory

Each cell must contain exactly three HGB density variants with budget anchors:

- 250
- 500
- 1000

A variant is either:

- `BUDGET_UNAVAILABLE` because fewer than the budget number of unique directional rows exist; or
- `EVALUATED` with a finite selection-derived cutoff and a selected-at-cutoff count greater than or equal to the budget anchor.

For evaluated variants, the 0.5-pip selection candidate count must equal the recorded selected-at-cutoff count.

## 6. Aggregate/stability consistency

For every evaluated variant:

- aggregate gate status must match the 0.5-pip financial gate;
- aggregate rejects must lock temporal stability;
- aggregate passes must contain the exact four DEC-104 stability windows;
- candidate-share values are recomputed from window candidate counts and the full selection candidate count;
- every stability financial criterion is recomputed;
- final selection-gate status must equal aggregate-pass AND all-window stability-pass.

The three budget slots must be unique and complete.

## 7. Chronology/result-status consistency

A cell ending at `NO_DENSITY_STABLE_MODEL_CHALLENGER` must keep validation and holdout locked.

A selected cell must identify an actually stable-passing budget/cutoff pair.

Validation rejection must lock holdout.

Validation pass must produce a retrospective holdout PASS or REJECT result.

## 8. Cell fingerprint

Each cell result carries a canonical SHA-256 fingerprint over the entire unsigned cell-result object.

DEC-115 recomputes and requires that fingerprint exactly.

## 9. Aggregate evidence

Aggregate evidence requires all 18 exact cells.

The aggregate records:

- exact DEC-113/114 source identities;
- exact historical feature/outcome/readiness identities;
- all 18 cell result fingerprints/status summaries;
- aggregate-pass variant count;
- stable-pass variant count;
- stability-reject variant count;
- unavailable-budget variant count;
- all downstream authorization locks.

The aggregate evidence itself carries a canonical SHA-256 fingerprint.

## 10. Authoritative execution gate

`run_authoritative_density_model_bundle(...)` checks:

`AUTHORITATIVE_DENSITY_MODEL_RESULT_EXECUTION_AUTHORIZED`

before source validation, readiness validation, artifact loading, or model fitting.

Under DEC-115 this value is false.

Therefore DEC-115 cannot perform authoritative EXP-047 fitting or result production.

## 11. Source identity

Implementation:

`src/fmp/market_learning/model_successor_density_artifacts.py`

Git blob:

`2d3997ca97fb4568187be54914fe76e8dbf76ff5`

Runner version:

`fmp-exp047-density-artifact-runner-v1`

Decision:

`DEC-115`

## 12. Authorization state

DEC-115 keeps false:

- authoritative EXP-047 result execution;
- EXP-047 model-fit authorization;
- model-protocol result production;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 13. Next gate

A later separate decision may freeze a manual main-only workflow/CLI/execution gate around merged DEC-113/114/115.

No workflow, dispatch, result execution, or model-fit authorization is opened by DEC-115.
