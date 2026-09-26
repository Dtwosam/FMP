# Phase 8A — EXP-060 Artifact/Evidence Contract

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-255
**Experiment:** EXP-20260926-060

## Purpose

DEC-255 freezes the non-executable artifact/evidence contract for EXP-060 after the repaired deterministic DEC-254 training core.

It validates complete repaired cell evidence and deterministic aggregate evidence before any workflow source, readiness path, historical execution authorization, or model run is considered.

## Frozen source bindings

DEC-255 binds:

- DEC-254 merge: `c8cac108bc098dbceda4b8903f5a56ac7f62bf47`
- DEC-254 repaired training-core blob: `202dcaa8ba4ad25324fbe53d00e812c60fbb37dd`
- predecessor EXP-059 regime-balance artifact-contract blob: `a993d8a0a98b181c7810e4f0931be330352437b4`

The artifact layer independently revalidates the exact DEC-254 source dependency chain and the EXP-060 repair-protocol fingerprint.

## Repaired cell provenance

Each EXP-060 cell must bind:

- experiment `EXP-20260926-060`;
- protocol decision `DEC-253`;
- training-core decision `DEC-254`;
- DEC-253 merge `7e5b399cb7960d385d956b33e5d96cea85bb2c28`;
- DEC-253 protocol blob `82d336250e2cdd9894afa5554c6b422e0de6b1fe`;
- failed EXP-059 training-core blob `4f99c1d0cb18551b67cc89357ad4a3940c190cd2`;
- unchanged EXP-058 semantic-predecessor training-core blob `77f2010574b3d8ecc958930d5bfadf7ddb4f2231`;
- exact EXP-060 protocol version and protocol fingerprint;
- deterministic cell result fingerprint.

This distinguishes the implementation repair from the failed EXP-059 source while preserving identical regime-balance semantics.

## Cell evidence contract

Each cell must contain the complete inherited inventory:

- six regressors;
- six pooled calibration references;
- 24 fit-temporal utility-support references;
- 12 fit-temporal feature-support references;
- 24 exact target-specific residual references;
- 12 residual-breadth source bounds per eligible row;
- 12 lower-tail source bounds per eligible row;
- fixed lower-tail count of 3;
- three residual fit regimes;
- four residual windows per regime;
- 12 regime-floor source bounds per eligible row;
- three regime-balance source regimes;
- 12 regime-balance source bounds per eligible row;
- regime-balance penalty multiplier exactly 1.0;
- lower-tail/regime-floor/regime-balance-aware consensus diagnostics and digest;
- three frozen candidate budgets;
- nine-part cutoff for every available variant.

The nine-part cutoff is unchanged from EXP-059:

1. residual regime-balance utility;
2. residual regime-floor utility;
3. residual lower-tail mean;
4. residual breadth;
5. residual-bound utility;
6. feature support;
7. fit-temporal utility support;
8. pooled calibrated utility;
9. raw utility.

Unavailable budgets expose no cutoff and cannot pass selection.

## Aggregate evidence

Complete aggregate evidence requires exactly all 18 model cells and verifies:

- 108 regressors;
- 108 pooled calibration references;
- 432 utility-support references;
- 216 feature-support references;
- 432 residual references;
- residual-breadth inventory of 12 per eligible row;
- lower-tail source-bound inventory of 12 per eligible row;
- lower-tail count 3;
- residual regime count 3;
- four residual windows per regime;
- regime-floor source-bound inventory 12;
- regime-balance regime count 3;
- regime-balance source-bound inventory 12;
- regime-balance penalty multiplier 1.0.

Aggregate evidence receives a deterministic SHA-256 fingerprint under the frozen canonical serializer.

## Forward-lock validation

If a cell has no selected variant, validation and retrospective holdout must remain `LOCKED_NO_SELECTION`.

The contract does not authorize any downstream refit, recalibration, cutoff retuning, or window-specific adjustment.

## Authorization state

DEC-255 keeps false:

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

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_artifacts.py`

Git blob:

`2a6c550dcafac2e7013136fcbbef95b13c2e7d18`

Focused tests:

`tests/test_phase8a_exp060_regime_balance_repair_artifacts.py`

Git blob:

`d3ddef1ea784eedd04be73deb495b93df2559049`

Artifact-contract version:

`fmp-exp060-fit-temporal-residual-regime-balance-utility-implementation-repair-artifact-contract-v1`

## Next gate

After DEC-255 is green and merged, the next safe gate is a separate manual-main EXP-060 workflow/CLI/runtime source freeze with execution still closed.

No historical run is authorized by DEC-255.
