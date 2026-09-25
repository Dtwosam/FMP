# Phase 8A — EXP-056 Artifact/Evidence Contract

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-211
**Experiment:** EXP-20260925-056

## Purpose

DEC-211 freezes the non-executable artifact/evidence contract for EXP-056 after DEC-210 completes the deterministic in-memory residual lower-tail core.

It validates exact cell-result structure and deterministic aggregate evidence before any workflow source, readiness path, historical execution authorization, or model run is considered.

## Frozen source bindings

DEC-211 binds:

- DEC-210 merge: `029159999fae7eaa67811f8b3d8bf2bf8834e491`
- DEC-210 training-core blob: `c472ed48e7b79d22056d43deb0fe09166ccf34c9`
- predecessor EXP-055 artifact-contract blob: `65ca27a20d4e4fadd73c22b0b5693dc9d7ebeafb`

The artifact contract also revalidates the exact DEC-210 training-source dependency chain and EXP-056 protocol fingerprint.

## Cell evidence contract

Each EXP-056 cell must bind the exact experiment/protocol/training decisions and contain:

- six regressors;
- six pooled calibration references;
- 24 fit-temporal utility-support references;
- 12 fit-temporal feature-support references;
- 24 exact target-specific residual references;
- 12 residual-breadth lower bounds per eligible row;
- 12 residual lower-tail source bounds per eligible row;
- fixed lower-tail count of 3;
- lower-tail-aware consensus diagnostics and digest;
- the three frozen candidate budgets;
- a seven-part cutoff for every available variant;
- deterministic cell result fingerprint.

The seven-part cutoff is:

1. residual lower-tail mean;
2. residual breadth;
3. residual-bound utility;
4. feature support;
5. fit-temporal utility support;
6. pooled calibrated utility;
7. raw utility.

Unavailable budgets must expose all seven cutoff fields as null and cannot pass selection.

## Aggregate evidence

Complete aggregate evidence requires exactly all 18 model cells and verifies:

- 108 regressors;
- 108 pooled calibration references;
- 432 utility-support references;
- 216 feature-support references;
- 432 residual references;
- residual-breadth bound inventory of 12 per eligible row;
- residual lower-tail source-bound inventory of 12 per eligible row;
- residual lower-tail count of 3.

The aggregate payload receives a deterministic SHA-256 evidence fingerprint under the frozen canonical serializer.

## Forward-lock validation

If a cell has no selected variant, validation and retrospective holdout must remain `LOCKED_NO_SELECTION`.

The contract does not authorize any downstream refit, recalibration, cutoff retuning, or window-specific adjustment.

## Authorization state

DEC-211 keeps false:

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

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_artifacts.py`

Git blob:

`f554011c092f5c4ec5d3f9b8e2330bfc974376f8`

Focused tests:

`tests/test_phase8a_exp056_fit_temporal_residual_lower_tail_utility_artifacts.py`

Git blob:

`6ece494a68757f67b664bfcf0967ab2dbda41fb8`

Artifact-contract version:

`fmp-exp056-fit-temporal-residual-lower-tail-utility-artifact-contract-v1`

## Next gate

After DEC-211 is green and merged, the next safe gate is a separate manual-main EXP-056 workflow/CLI/runtime source freeze with execution still closed.

No historical run is authorized by DEC-211.
