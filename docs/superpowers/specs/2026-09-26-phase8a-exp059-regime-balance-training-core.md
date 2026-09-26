# Phase 8A — EXP-059 Deterministic Regime-Balance Training Core

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-243
**Experiment:** EXP-20260926-059

## Purpose

DEC-243 implements the deterministic in-memory EXP-059 training/evaluation core against merged DEC-242.

It reuses the exact EXP-058 model, data, chronology, reference, financial-gate, temporal-stability, validation, and holdout machinery and adds only the fit-regime balance score plus its nine-part ranking/cutoff.

## Frozen source bindings

DEC-243 binds:

- DEC-242 merge: `a14afb226722d168c3d899d7079776388161a52d`
- DEC-242 protocol blob: `cd4e790098a5c8d99ea2aa5264465b5d4b6b6acc`
- predecessor DEC-232 training-core blob: `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`

The predecessor core must still report model-fit and result-execution authorization false.

## Regime-balance computation

For each already eligible row and agreed direction, DEC-243 reuses the same frozen jackknife predictions and 24 residual references used by EXP-058.

For each of the three views, it recomputes the exact four-bound arithmetic mean. The resulting three regime means are used to compute:

- retained regime floor = minimum regime mean;
- regime center = arithmetic mean of the three regime means;
- regime spread = maximum minus minimum regime mean;
- regime-balance utility = center minus exactly `1.0 * spread`.

The recomputed floor must match the predecessor EXP-058 regime-floor array exactly for every eligible row or the scorer fails closed.

No new reference family is created.

## Ranking and cutoff

Eligible rows rank by:

1. regime-balance utility descending;
2. regime-floor utility descending;
3. residual lower-tail mean descending;
4. residual breadth descending;
5. residual-bound utility descending;
6. feature support descending;
7. utility support descending;
8. pooled calibrated utility descending;
9. raw utility descending;
10. row identity ascending.

Each unchanged budget 250 / 500 / 1000 freezes the nine numeric components from the budget-th row.

Forward candidate application uses the identical lexicographic rule, with the final raw-utility comparison inclusive.

## Selection and forward evaluation

The full cell runner:

`run_fit_temporal_residual_regime_balance_utility_model_cell_core`

fits only the unchanged frozen jackknife regressors, builds only predecessor reference families, scores selection rows with regime balance, applies the unchanged aggregate and four-window stability gates, and only after a stable selection applies the exact frozen models/references/nine-part cutoff to validation and retrospective holdout.

If no stable selection exists, validation and holdout remain locked.

No downstream refit, recalibration, quota, stability-window change, or selection-window tuning is permitted.

## Authorization state

DEC-243 keeps false:

- authoritative historical result execution;
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

## Source identity

Training core:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_training.py`

Git blob:

`4f99c1d0cb18551b67cc89357ad4a3940c190cd2`

Focused tests:

`tests/test_phase8a_exp059_regime_balance_training.py`

Git blob:

`4f5a2222da5aab5e60558b3594f64e02f511838b`

Training-core version:

`fmp-exp059-fit-temporal-residual-regime-balance-utility-training-core-v1`

## Next gate

After DEC-243 is green and merged, the next safe gate is a separate non-executable EXP-059 artifact/evidence contract bound to this exact core.
