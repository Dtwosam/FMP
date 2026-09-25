# Phase 8A — EXP-058 Artifact/Evidence Contract

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-233
**Experiment:** EXP-20260925-058

## Purpose

DEC-233 freezes the non-executable artifact/evidence contract for EXP-058 after DEC-232 completes the deterministic in-memory residual regime-floor core.

It validates exact cell-result structure and deterministic aggregate evidence before any workflow source, readiness path, historical execution authorization, or model run is considered.

## Frozen source bindings

DEC-233 binds:

- DEC-232 merge: `24cb20bb0b1e3aa25f1ea87e1cfbba22587a0ae6`
- DEC-232 training-core blob: `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`
- predecessor EXP-057 artifact-contract blob: `d69eb668ade480b66faf992190b3a4929f414960`

The contract also revalidates the exact DEC-232 training-source dependency chain and EXP-058 protocol fingerprint.

## Cell evidence contract

Each EXP-058 cell must bind the exact experiment/protocol/training decisions and contain:

- six regressors;
- six pooled calibration references;
- 24 fit-temporal utility-support references;
- 12 fit-temporal feature-support references;
- 24 exact target-specific residual references;
- 12 residual-breadth lower bounds per eligible row;
- 12 residual lower-tail source bounds per eligible row;
- fixed lower-tail count of 3;
- exactly 3 residual fit regimes;
- exactly 4 residual windows per regime;
- exactly 12 regime-floor source bounds per eligible row;
- regime-floor-aware consensus diagnostics and digest;
- the three frozen candidate budgets;
- an eight-part cutoff for every available variant;
- deterministic cell result fingerprint.

The eight-part cutoff is:

1. residual regime-floor utility;
2. residual lower-tail mean;
3. residual breadth;
4. residual-bound utility;
5. feature support;
6. fit-temporal utility support;
7. pooled calibrated utility;
8. raw utility.

Unavailable budgets must expose all eight cutoff fields as null and cannot pass selection.

## Aggregate evidence

Complete aggregate evidence requires exactly all 18 model cells and verifies:

- 108 regressors;
- 108 pooled calibration references;
- 432 utility-support references;
- 216 feature-support references;
- 432 residual references;
- residual-breadth bound inventory of 12 per eligible row;
- residual lower-tail source-bound inventory of 12 per eligible row;
- lower-tail count of 3;
- residual regime count of 3;
- residual windows per regime of 4;
- regime-floor source-bound inventory of 12 per eligible row.

The aggregate payload receives a deterministic SHA-256 evidence fingerprint under the frozen canonical serializer.

## Forward-lock validation

If a cell has no selected variant, validation and retrospective holdout must remain `LOCKED_NO_SELECTION`.

The contract does not authorize any downstream refit, recalibration, regime regrouping, cutoff retuning, or window-specific adjustment.

## Authorization state

DEC-233 keeps false:

- authoritative historical result execution;
- model fit authorization;
- workflow dispatch;
- rerun/replacement;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

The authoritative bundle entry point fails closed before execution.

## Source identity

Artifact/evidence contract:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_artifacts.py`

Git blob:

`5a34f354b68e14bb7116c79f15f9cfebe149a811`

Focused tests:

`tests/test_phase8a_exp058_regime_floor_artifacts.py`

Git blob:

`7338dd5cba39e98c9e56a1b352444a543a1e227c`

Artifact-contract version:

`fmp-exp058-fit-temporal-residual-regime-floor-utility-artifact-contract-v1`

## Next gate

After DEC-233 is green and merged, the next safe gate is a separate manual-main EXP-058 workflow/CLI/runtime source freeze with execution still closed.

No historical run is authorized by DEC-233.
