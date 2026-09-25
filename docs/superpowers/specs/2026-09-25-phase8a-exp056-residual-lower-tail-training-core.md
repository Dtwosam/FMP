# Phase 8A — EXP-056 Deterministic Residual Lower-Tail Training Core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-210
**Experiment:** EXP-20260925-056

## Purpose

DEC-210 implements the deterministic in-memory EXP-056 training/evaluation core against the exact DEC-209 protocol.

It does not create a historical workflow, artifact loader, readiness path, execution authorization, promotion path, shadow/demo path, broker mutation path, live-order path, real-money path, or trading path.

## Frozen source bindings

DEC-210 binds:

- DEC-209 merge: `d2e1aabba6c0f283da6802fe315a5a29b22b503c`
- DEC-209 protocol blob: `14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d`
- predecessor DEC-199 EXP-055 training-core blob: `c9517b7516940c78621448088c3933aa1c57e281`

The predecessor DEC-199 source must still report model-fit and result-execution authorization false.

## Reused predecessor mechanics

The core reuses unchanged EXP-055 and EXP-054 mechanics:

- frame validation and chronological split construction
- three jackknife views
- two HGB utility regressors per view
- six regressors per cell
- pooled out-of-fit utility calibration
- 24 fit-half-year utility-support references
- 12 fit-half-year feature-support references
- 24 target-specific residual references
- lower-quartile residual extraction at q = 0.25
- EXP-054 residual-bound utility
- EXP-055 residual-breadth score over twelve lower bounds
- financial metrics and aggregate gates
- four unchanged temporal-stability windows
- unchanged 10% candidate-share floor
- validation and retrospective-holdout financial gates
- row identities and deterministic result fingerprinting

## Residual lower-tail computation

For each already eligible row and agreed direction, DEC-210 reuses the same exact twelve downside-adjusted lower bounds.

The core:

1. sorts those twelve finite values ascending;
2. takes the three smallest values;
3. computes their arithmetic mean.

The score is:

`fit_temporal_residual_lower_tail_mean`

The lower-tail count is fixed at 3 and the source inventory at 12.

There is no interpolation, trimming, winsorization, or new reference family.

Ineligible rows remain outside candidate ranking.

## Selection cutoff

For each budget 250 / 500 / 1000, eligible rows are sorted by:

1. residual lower-tail mean descending
2. residual breadth descending
3. residual-bound utility descending
4. feature support descending
5. utility support descending
6. pooled calibrated utility descending
7. raw utility descending
8. row identity ascending

The budget-th row freezes a seven-part cutoff:

- lower-tail mean
- breadth
- residual bound
- feature support
- utility support
- pooled calibration
- raw utility

Forward candidate application uses the same lexicographic rule.

## Selection and forward evaluation

The full cell runner:

`run_fit_temporal_residual_lower_tail_utility_model_cell_core`

fits only the frozen jackknife regressors, builds only predecessor reference families, scores selection rows with the new lower-tail metric plus the retained breadth/residual/support signals, evaluates unchanged aggregate/stability gates, and only after a stable selection applies the exact frozen models/references/cutoff to validation and retrospective holdout.

If no stable selection exists, validation and holdout remain locked.

No downstream fit, recalibration, lower-tail retuning, quota, or selection-window adjustment is permitted.

## Evidence shape

The cell result retains predecessor fit evidence and adds:

- residual lower-tail rule
- lower-tail eligibility rule
- twelve-bound source inventory
- fixed worst-three count
- lower-tail consensus min/max diagnostics
- lower-tail-aware consensus digest
- selection-derived lower-tail cutoff
- lower-tail-first ranking/cutoff rules

## Authorization state

DEC-210 keeps false:

- authoritative result execution
- model fit authorization outside this deterministic in-memory core
- artifact loading
- readiness execution
- workflow dispatch
- rerun/replacement
- promotion
- shadow execution
- demo orders
- broker mutation
- live orders
- real-money action
- trading

## Source identity

Training core:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_training.py`

Git blob:

`484fb25375138ecd16e5d6954dbdbebebf8568f2`

Focused tests:

`tests/test_phase8a_exp056_fit_temporal_residual_lower_tail_utility_training.py`

Git blob:

`abe1866e0b014591cbfe9dc19afb97d48318b31c`

Training-core version:

`fmp-exp056-fit-temporal-residual-lower-tail-utility-training-core-v1`

## Next gate

After DEC-210 is green and merged, the next safe gate is a separate non-executable EXP-056 artifact/evidence contract that binds this exact core and validates complete evidence before any workflow source or execution authorization is considered.
