# Phase 8A — EXP-058 Deterministic Residual Regime-Floor Training Core

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-232
**Experiment:** EXP-20260925-058

## Purpose

DEC-232 implements the deterministic in-memory EXP-058 training/evaluation core against the exact DEC-231 protocol.

It does not create a workflow, artifact loader, readiness path, execution authorization, promotion path, shadow/demo path, broker mutation path, live-order path, real-money path, or trading path.

## Frozen source bindings

DEC-232 binds:

- DEC-231 merge: `a6926703d787a7fe0e2ba34261d14c4c4d362df2`
- DEC-231 protocol blob: `8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2`
- predecessor DEC-221 repaired lower-tail training-core blob: `ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd`

The predecessor core must still report model-fit and result-execution authorization false.

## Reused predecessor mechanics

The EXP-058 core delegates unchanged mechanics to the frozen repaired EXP-057 implementation:

- frame validation and chronological split construction;
- three jackknife views;
- two HGB utility regressors per view;
- six regressors per cell;
- pooled out-of-fit utility calibration;
- 24 fit-half-year utility-support references;
- 12 fit-half-year feature-support references;
- 24 target-specific residual references;
- lower-quartile residual extraction at q = 0.25;
- residual-bound utility;
- residual breadth;
- worst-three residual lower-tail mean;
- aggregate financial metrics and gates;
- four unchanged temporal-stability windows;
- unchanged 10% candidate-share floor;
- validation and retrospective-holdout financial gates;
- row identities and deterministic result fingerprinting.

## Residual regime-floor computation

For each already eligible LONG or SHORT row, the core reuses the exact twelve EXP-057 downside-adjusted lower bounds.

The twelve bounds are grouped by their three frozen jackknife views. Each view contributes exactly four bounds from the half-years of the two-year fit regime excluded by that view.

For each row:

1. compute the arithmetic mean of the four bounds within each view;
2. require exactly three finite regime means;
3. define the residual regime-floor utility as the minimum of the three means.

This creates no new reference vector and uses no selection, validation, or holdout outcome.

## Selection cutoff

Eligible rows rank by:

1. residual regime-floor utility descending;
2. residual lower-tail mean descending;
3. residual breadth descending;
4. residual-bound utility descending;
5. feature support descending;
6. fit-temporal utility support descending;
7. pooled calibrated utility descending;
8. raw utility descending;
9. row identity ascending.

For each unchanged budget 250 / 500 / 1000, the budget-th row freezes an eight-part numeric cutoff.

Forward candidate application uses the same lexicographic order, with the final raw-utility comparison inclusive.

## Selection and forward evaluation

The full cell runner is:

`run_fit_temporal_residual_regime_floor_utility_model_cell_core`

It fits only the frozen jackknife regressors, builds only predecessor reference families, scores rows with the new regime-floor utility plus the inherited EXP-057 ranking stack, evaluates unchanged aggregate/stability gates, and only after a stable selection applies the exact frozen models/references/eight-part cutoff to validation and retrospective holdout.

If no stable selection exists, validation and holdout remain locked.

No downstream fit, recalibration, regime regrouping, quota, budget change, or window-specific tuning is permitted.

## Evidence shape

The cell result retains predecessor fit evidence and adds:

- regime-floor rule;
- regime-floor eligibility rule;
- three-regime inventory;
- four residual windows per regime;
- twelve-bound regime-floor inventory;
- regime-floor consensus min/max diagnostics;
- regime-floor-aware consensus digest;
- selection-derived regime-floor cutoff.

## Authorization state

DEC-232 keeps false:

- authoritative result execution;
- model-fit authorization outside this deterministic in-memory core;
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

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_training.py`

Git blob:

`e7343f2dcff747fbedc128074258226f23a405fa`

Focused tests:

`tests/test_phase8a_exp058_fit_regime_floor_training.py`

Git blob:

`87c55efb7ab02a7538a916fc87aa932b5484381b`

Training-core version:

`fmp-exp058-fit-temporal-residual-regime-floor-utility-training-core-v1`

## Next gate

After DEC-232 is green and merged, the next safe gate is a separate non-executable EXP-058 artifact/evidence contract bound to this exact core.

No workflow source or historical execution authorization is opened by DEC-232.
