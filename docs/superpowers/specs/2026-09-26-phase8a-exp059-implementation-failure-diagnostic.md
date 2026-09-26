# Phase 8A — EXP-059 Implementation-Failure Diagnostic

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY DIAGNOSTIC
**Decision:** DEC-252
**Experiment:** EXP-20260926-059

## Purpose

DEC-252 explains why the sole EXP-059 historical attempt failed before producing any model evidence.

It does not reopen the consumed EXP-059 slot and does not reinterpret the failed attempt as a regime-balance model result.

## Frozen bindings

DEC-252 binds:

- DEC-251 merge: `639fa26f841d0d3bb4c8577372a8539a0c0fd38f`
- DEC-251 result-decision blob: `c8ca7143e687494b81205556af7e317ec69937fd`
- EXP-059 regime-balance training-core blob: `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`
- EXP-058 regime-floor training-core blob: `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`
- EXP-057 lower-tail-repair training-core blob: `ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd`
- EXP-055 breadth training-core blob: `c9517b7516940c78621448088c3933aa1c57e281`

The reviewed failed run remains `36239443323`.

## Diagnostic method

The diagnostic parses the frozen Python sources with the Python AST and validates the exact predecessor import chain:

1. EXP-059 regime-balance -> EXP-058 regime-floor
2. EXP-058 regime-floor -> EXP-057 lower-tail repair
3. EXP-057 lower-tail repair -> EXP-055 residual breadth

It then inventories the EXP-059 nested breadth-metadata attribute chains and compares the exported top-level names at the lower-tail-repair and breadth layers.

## Exact implementation defect

EXP-059 uses four breadth metadata accesses at two predecessor levels:

- `FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW`
- `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE`
- `RESIDUAL_BREADTH_ELIGIBILITY_RULE`
- `RESIDUAL_BREADTH_POSITIVITY_RULE`

At EXP-059, `_predecessor._predecessor` resolves to the EXP-057 lower-tail-repair training module. That module does not export those breadth metadata names.

The EXP-055 breadth training module one level deeper does export all four.

The historical attempt directly observed the missing `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE` export in all nine matrix jobs.

## Classification

DEC-252 classifies the failure as:

`EXP059_IMPLEMENTATION_FAILED_BEFORE_EVIDENCE_DUE_PREDECESSOR_DEPTH_DRIFT`

This is an implementation dependency-depth defect, not a regime-balance model result.

## Exact repair boundary

A future successor implementation may repair only these four accesses:

`_predecessor._predecessor.<name> -> _predecessor._predecessor._predecessor.<name>`

for the four breadth metadata names listed above.

No protocol semantics, regime-balance math, model family, data identity, chronology, ranking, cutoff, candidate budget, financial gate, temporal-stability gate, validation, or holdout rule may change under this repair.

## Authorization state

DEC-252 keeps false:

- EXP-059 rerun;
- EXP-059 replacement run;
- successor model fit;
- successor historical result execution;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

It opens only successor protocol source design under a new experiment identity.

## Source identity

Diagnostic source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_failure_diagnostics.py`

Git blob:

`d73008c7faf236f915685110d6cf59988d6fc27f`

Focused tests:

`tests/test_phase8a_exp059_implementation_failure_diagnostics.py`

Git blob:

`3432d5ffb6799eb3adf4d25780cfc00141ba038e`

## Next gate

After DEC-252 is green and merged, the next safe gate is a source-only successor protocol with a new experiment identity that preserves EXP-059 protocol semantics exactly and authorizes only the four-name predecessor-depth repair.

No model fitting or historical execution is authorized by DEC-252.
