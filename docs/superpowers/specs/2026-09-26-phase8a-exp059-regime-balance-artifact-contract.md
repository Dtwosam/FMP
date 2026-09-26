# Phase 8A — EXP-059 Artifact/Evidence Contract

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-244
**Experiment:** EXP-20260926-059

## Purpose

DEC-244 freezes the non-executable artifact/evidence contract for EXP-059 after DEC-243 completes the deterministic in-memory regime-balance core.

It validates exact cell-result structure and deterministic aggregate evidence before any workflow source, readiness path, historical execution authorization, or model run is considered.

## Frozen source bindings

DEC-244 binds:

- DEC-243 merge: `9f427f06f315288bd9b132de19901beb5a5ddfc8`
- DEC-243 training-core blob: `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`
- predecessor DEC-233 artifact-contract blob: `5a34f354b68e14bb7116c79f15f9cfebe149a811`

The contract revalidates the exact DEC-243 training-source chain and EXP-059 protocol fingerprint.

## Cell evidence contract

Each EXP-059 cell must bind the exact experiment/protocol/training decisions and contain:

- six regressors;
- six pooled calibration references;
- 24 fit-temporal utility-support references;
- 12 fit-temporal feature-support references;
- 24 exact target-specific residual references;
- 12 residual-breadth lower bounds per eligible row;
- 12 residual lower-tail source bounds per eligible row;
- fixed lower-tail count of 3;
- three residual fit regimes;
- four residual windows per regime;
- 12 regime-floor source bounds per eligible row;
- three regime-balance source regimes per eligible row;
- 12 regime-balance source bounds per eligible row;
- fixed regime-balance penalty multiplier 1.0;
- regime-balance-aware consensus diagnostics and digest;
- the three frozen candidate budgets;
- a nine-part cutoff for every available variant;
- deterministic cell result fingerprint.

The nine-part cutoff is:

1. residual regime-balance utility;
2. residual regime-floor utility;
3. residual lower-tail mean;
4. residual breadth;
5. residual-bound utility;
6. feature support;
7. fit-temporal utility support;
8. pooled calibrated utility;
9. raw utility.

Unavailable budgets must expose all nine cutoff fields as null and cannot pass selection.

## Aggregate evidence

Complete aggregate evidence requires exactly all 18 model cells and verifies:

- 108 regressors;
- 108 pooled calibration references;
- 432 utility-support references;
- 216 feature-support references;
- 432 residual references;
- residual-breadth bound inventory of 12 per eligible row;
- residual lower-tail source-bound inventory of 12 per eligible row;
- residual lower-tail count of 3;
- residual regime count of 3;
- residual windows per regime of 4;
- regime-floor source-bound inventory of 12 per eligible row;
- regime-balance regime count of 3;
- regime-balance source-bound inventory of 12 per eligible row;
- regime-balance penalty multiplier of 1.0.

The aggregate payload receives a deterministic SHA-256 evidence fingerprint under the frozen canonical serializer.

## Forward-lock validation

If a cell has no selected variant, validation and retrospective holdout must remain `LOCKED_NO_SELECTION`.

The contract does not authorize any downstream refit, recalibration, cutoff retuning, regime-balance retuning, or window-specific adjustment.

## Authorization state

DEC-244 keeps false:

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

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_artifacts.py`

Git blob:

`a993d8a0a98b181c7810e4f0931be330352437b4`

Focused tests:

`tests/test_phase8a_exp059_regime_balance_artifacts.py`

Git blob:

`12ee1e63d2bfc0cae1ee272290f866e1de021520`

Artifact-contract version:

`fmp-exp059-fit-temporal-residual-regime-balance-utility-artifact-contract-v1`

## Next gate

After DEC-244 is green and merged, the next safe gate is a separate manual-main EXP-059 workflow/CLI/runtime source freeze with execution still closed.

No historical run is authorized by DEC-244.
