# Phase 8A — EXP-055 Residual-Breadth Artifact/Evidence Contract

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-200
**Experiment:** EXP-20260925-055

## Purpose

DEC-200 freezes the non-executable artifact/evidence contract for EXP-055 after DEC-199 completes the deterministic in-memory core.

It does not load authoritative historical artifacts, run model fitting, dispatch workflows, authorize a historical result, promote a model, start shadow/demo execution, mutate a broker, place orders, risk real money, or trade.

## Frozen source bindings

DEC-200 binds:

- DEC-199 merge: `aaa80ce43a4dbd38e52e418dd16b61642d22b2b5`
- DEC-199 training-core blob: `c9517b7516940c78621448088c3933aa1c57e281`
- predecessor EXP-054 artifact-contract blob: `37a5cd982e0a5b6634d5dc036c44cef706d487f3`

The DEC-199 training source must still validate its DEC-198 protocol and frozen DEC-188 predecessor dependencies.

## Complete cell evidence

Every EXP-055 cell must bind the exact experiment, protocol decision, and training-core decision.

The contract requires each cell to contain:

- 6 fitted regressors
- 6 pooled calibration references
- 24 fit-temporal utility-support references
- 12 fit-temporal feature-support references
- 24 exact fit-temporal residual references
- 12 residual-breadth lower-bound comparisons per scored eligible row
- breadth-aware consensus diagnostics and digest
- exactly the three frozen candidate budgets
- deterministic cell result fingerprint
- downstream execution/trading flags false

Residual references reuse the strict EXP-054 identity validation, including exact view, target, parent-regime, half-year dates, row counts, prediction digests, residual digests, and finite downside residuals.

## Six-part cutoff evidence

Available variants must freeze a finite sextuple:

1. residual breadth in [0, 1]
2. residual-bound utility, finite
3. feature support in [0, 1]
4. utility support in [0, 1]
5. pooled calibrated utility in [0, 1]
6. raw utility > 0

Unavailable budgets must expose no cutoff values and cannot pass selection.

## Aggregate evidence

A complete aggregate requires all 18 exact model cells with no duplicates.

The compiler verifies totals of:

- 108 regressors
- 108 pooled calibration references
- 432 utility-support references
- 216 feature-support references
- 432 residual references
- 12 residual-breadth lower-bound comparisons per eligible scored row

The aggregate fingerprint is deterministic under the frozen canonical serializer.

## Fail-closed execution boundary

The authoritative bundle entry point rejects before any execution because authoritative result execution remains false.

DEC-200 source contains no workflow dispatch or broker path.

## Source identity

Artifact/evidence contract:

`src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_artifacts.py`

Git blob:

`65ca27a20d4e4fadd73c22b0b5693dc9d7ebeafb`

Focused tests:

`tests/test_phase8a_exp055_fit_temporal_residual_breadth_utility_artifacts.py`

Git blob:

`ff57999b49a916efe6f6e10a2f8b8d3f8bb244fd`

Contract version:

`fmp-exp055-fit-temporal-residual-breadth-utility-artifact-contract-v1`

## Next gate

After DEC-200 is green and merged, a later separate decision may freeze a manual-main workflow, public CLI, pinned runtime, and exact-source execution gate while keeping dispatch, historical result execution, and model-fit authorization false.
