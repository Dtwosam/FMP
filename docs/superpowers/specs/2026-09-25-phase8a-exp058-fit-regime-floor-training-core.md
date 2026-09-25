# Phase 8A — EXP-058 Deterministic Fit-Regime-Floor Training Core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-232
**Experiment:** EXP-20260925-058

## Purpose

DEC-232 implements the deterministic in-memory training/evaluation core authorized by DEC-231.

The core preserves the complete repaired EXP-057 model/data/chronology/reference/gate pipeline and adds exactly one ranking score: fit-temporal residual regime-floor utility.

## Frozen source bindings

DEC-232 binds:

- DEC-231 merge: `a6926703d787a7fe0e2ba34261d14c4c4d362df2`
- DEC-231 protocol blob: `8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2`
- EXP-057 predecessor training-core blob: `ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd`

The predecessor core remains non-executable.

## Regime-floor calculation

For every unchanged EXP-057-eligible LONG/SHORT row:

- reuse the same three frozen jackknife view predictions;
- reuse the same four downside residual references attached to each view's excluded two-year fit regime;
- build exactly four lower bounds per view;
- take their arithmetic mean;
- repeat across all three views;
- define the row's regime-floor utility as the minimum of the three view/regime means.

Thus the new score uses exactly 12 existing residual lower bounds, grouped as 3 fit regimes × 4 half-years.

No new reference vector is created.

## Ranking and cutoff

The core ranks eligible rows by:

1. residual regime-floor utility;
2. residual lower-tail mean;
3. residual breadth;
4. robust residual-bound utility;
5. feature support;
6. utility support;
7. pooled calibrated utility;
8. raw utility;
9. row identity.

For each unchanged budget 250, 500, and 1000, the core freezes an eight-part numeric cutoff. Exact eight-part ties may exceed budget.

## Full deterministic pipeline

The core retains:

- exact frame validation and chronology splits;
- three jackknife views / six HGB regressors;
- six pooled calibration references;
- 24 fit-temporal utility-support references;
- 12 feature-support references;
- 24 residual references;
- existing residual-bound, breadth, and lower-tail scores;
- aggregate financial gates;
- four-window temporal stability;
- validation and retrospective holdout;
- no-refit / no-recalibration forward application.

Validation and holdout reuse the same fitted models, references, derived regime-floor score, and selection-derived eight-part cutoff.

## Fail-closed scope

DEC-232 is an in-memory core only.

It does not load authoritative artifacts, inspect readiness, dispatch workflows, produce an authoritative historical result, promote a candidate, mutate a broker, or trade.

All of the following remain false:

- result execution;
- model fit authorization outside the deterministic core;
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

`a930089290b1d3be71592dadebfbbd1c59095b77`

Focused tests:

`tests/test_phase8a_exp058_fit_regime_floor_training.py`

Git blob:

`03149abcf5683455d273a2ccd9df3a0b33e5b9e5`

The focused tests verify exact source binding, direct numeric regime-floor calculation, required 3×4 inventory, eight-part cutoff shape, full stability/forward cell-runner presence, and the non-executable authorization state.

## Next gate

After DEC-232 is green and merged, the next safe gate is a separate non-executable EXP-058 artifact/evidence contract bound to this exact training core.
