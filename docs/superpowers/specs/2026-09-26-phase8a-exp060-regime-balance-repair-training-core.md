# Phase 8A — EXP-060 Deterministic Regime-Balance Repair Training Core

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-254
**Experiment:** EXP-20260926-060

## Purpose

DEC-254 implements the deterministic in-memory EXP-060 training/evaluation core against the exact DEC-253 implementation-repair protocol.

It preserves the complete EXP-059 regime-balance model/evaluation semantics and changes only the four predecessor-depth accesses authorized by DEC-253.

DEC-254 creates no artifact loader, workflow dispatch, readiness execution, historical-result authorization, rerun/replacement path, promotion path, shadow/demo path, broker mutation path, live-order path, real-money path, or trading path.

## Frozen source bindings

DEC-254 binds:

- DEC-253 merge: `7e5b399cb7960d385d956b33e5d96cea85bb2c28`
- DEC-253 repair-protocol blob: `82d336250e2cdd9894afa5554c6b422e0de6b1fe`
- failed EXP-059 regime-balance training-core blob: `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`
- semantic predecessor EXP-058 regime-floor training-core blob: `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`

The semantic predecessor remains model-fit and result-execution closed.

## Exact implementation repair

The repaired core retains the same predecessor module chain and changes only four metadata accesses:

- `FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW`
- `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE`
- `RESIDUAL_BREADTH_ELIGIBILITY_RULE`
- `RESIDUAL_BREADTH_POSITIVITY_RULE`

Each access changes from:

`_predecessor._predecessor.<name>`

to:

`_predecessor._predecessor._predecessor.<name>`

No other dependency-depth change is authorized.

## Unchanged mechanics

DEC-254 retains the frozen EXP-059 mechanics exactly:

- chronology and outer splits;
- three jackknife fit regimes;
- six HGB utility regressors per cell;
- pooled out-of-fit calibration;
- 24 utility-support references;
- 12 feature-support references;
- 24 residual references;
- residual-bound utility;
- residual breadth;
- lower-tail mean;
- three fit-regime means;
- regime-floor utility;
- regime-balance utility = arithmetic mean of three regime means minus exactly 1.0 times their range;
- candidate budgets 250 / 500 / 1000;
- nine-part lexicographic ranking/cutoff;
- four temporal-stability windows;
- minimum directional candidate share 0.10;
- unchanged financial gates;
- validation and retrospective-holdout chronology;
- exact no-refit/no-recalibration forward application.

The full cell runner remains:

`run_fit_temporal_residual_regime_balance_utility_model_cell_core`

## Provenance

Cell results bind:

- EXP-060 experiment identity;
- DEC-254 training-core identity;
- DEC-253 protocol identity/fingerprint;
- failed EXP-059 training-core blob;
- unchanged EXP-058 semantic predecessor training-core blob.

This distinguishes the implementation repair from the failed EXP-059 source without changing the model semantics.

## Authorization state

DEC-254 keeps false:

- authoritative result execution;
- model fit authorization outside this deterministic in-memory core;
- artifact loading;
- readiness execution;
- workflow dispatch;
- rerun/replacement;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

The training gate reports:

- implementation dependency repair authorized: true;
- protocol semantics change authorized: false;
- regime-balance score retained: true.

## Source identity

Training core:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_training.py`

Git blob:

`202dcaa8ba4ad25324fbe53d00e812c60fbb37dd`

Focused tests:

`tests/test_phase8a_exp060_implementation_repair_training.py`

Git blob:

`b651a35a3e54a9dd909ee6061662550b2b84dc43`

Training-core version:

`fmp-exp060-fit-temporal-residual-regime-balance-utility-implementation-repair-training-core-v1`

## Next gate

After DEC-254 is green and merged, the next safe gate is a separate non-executable EXP-060 artifact/evidence contract bound to this exact repaired core.

No historical result execution is authorized by DEC-254.
