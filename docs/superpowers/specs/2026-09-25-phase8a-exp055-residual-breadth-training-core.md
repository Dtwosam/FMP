# Phase 8A — EXP-055 Deterministic Residual-Breadth Training Core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-199
**Experiment:** EXP-20260925-055

## Purpose

DEC-199 implements the deterministic in-memory EXP-055 training/evaluation core against the exact DEC-198 protocol.

It does not create a historical workflow, artifact loader, readiness path, execution authorization, promotion path, shadow/demo path, broker mutation path, live-order path, real-money path, or trading path.

## Frozen source bindings

DEC-199 binds:

- DEC-198 merge: `670f5d615b837b9268f8fb807aa198e7d14d0f1a`
- DEC-198 protocol blob: `0ef3f932cade1a62e1faf946e9a9b87cf9c98744`
- predecessor DEC-188 training core blob: `4f3f189c104d41352433397421f021896c03a5e9`

The predecessor DEC-188 source must still report model-fit and result-execution authorization false.

## Reused predecessor mechanics

The core delegates unchanged mechanics to the frozen EXP-054 implementation:

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
- financial metrics and aggregate gates
- four unchanged temporal-stability windows
- unchanged 10% candidate-share floor
- validation and retrospective-holdout financial gates
- row identities and deterministic result fingerprinting

## Residual-breadth computation

For each already eligible row and agreed direction, DEC-199 reuses the exact twelve EXP-054 prediction-plus-downside-residual lower bounds.

The core computes:

`fit_temporal_residual_breadth = count(lower_bound > 0) / 12`

The breadth score is finite and constrained to [0, 1] for eligible rows.

Ineligible rows remain outside candidate ranking.

No new reference vectors are built.

## Selection cutoff

For each budget 250 / 500 / 1000, eligible rows are sorted by:

1. residual breadth descending
2. residual-bound utility descending
3. feature support descending
4. utility support descending
5. pooled calibrated utility descending
6. raw utility descending
7. row identity ascending

The budget-th row freezes a six-part cutoff:

- breadth
- residual bound
- feature support
- utility support
- pooled calibration
- raw utility

Forward candidate application uses the same lexicographic rule.

## Selection and forward evaluation

The full cell runner:

`run_fit_temporal_residual_breadth_utility_model_cell_core`

fits only the frozen jackknife regressors, builds only predecessor reference families, scores selection rows with the new breadth metric, evaluates unchanged aggregate/stability gates, and only after a stable selection applies the exact frozen models/references/cutoff to validation and retrospective holdout.

If no stable selection exists, validation and holdout remain locked.

No downstream fit, recalibration, breadth retuning, quota, or selection-window adjustment is permitted.

## Evidence shape

The cell result retains predecessor fit evidence and adds:

- fit-temporal residual-breadth rule
- strict-positivity rule
- breadth eligibility rule
- twelve-bound inventory
- breadth consensus min/max diagnostics
- breadth-aware consensus digest
- selection-derived breadth cutoff
- breadth-first ranking/cutoff rules

## Authorization state

DEC-199 keeps false:

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

`src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_training.py`

Git blob:

`c9517b7516940c78621448088c3933aa1c57e281`

Focused tests:

`tests/test_phase8a_exp055_fit_temporal_residual_breadth_utility_training.py`

Git blob:

`cb2f4173fcefcb1a282300eb04374c0b8f468dbf`

Training-core version:

`fmp-exp055-fit-temporal-residual-breadth-utility-training-core-v1`

## Next gate

After DEC-199 is green and merged, the next safe gate is a separate non-executable EXP-055 artifact/evidence contract that binds this exact core and validates complete evidence before any workflow source or execution authorization is considered.
