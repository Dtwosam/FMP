# Phase 8A — EXP-057 Artifact/Evidence Contract

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-222
**Experiment:** EXP-20260925-057

## Purpose

DEC-222 freezes the non-executable artifact/evidence contract for EXP-057 after DEC-221 completes the deterministic implementation-repair training core.

It validates the exact repaired-core provenance and the complete inherited lower-tail evidence structure before any workflow source, readiness path, historical execution authorization, or model run is considered.

## Frozen source bindings

DEC-222 binds:

- DEC-221 merge: `6ea34dd3c62f72c55376e891eeb44d96ad5de54b`
- DEC-221 repaired training-core blob: `ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd`
- predecessor EXP-056 artifact-contract blob: `f554011c092f5c4ec5d3f9b8e2330bfc974376f8`

The contract revalidates the complete DEC-221 training-source dependency chain and EXP-057 repair-protocol fingerprint.

## Cell evidence contract

Every EXP-057 cell must bind:

- experiment `EXP-20260925-057`;
- protocol decision `DEC-220`;
- training decision `DEC-221`;
- DEC-220 merge `865ab1569a0765078ed099008a5722f8a6d310b4`;
- DEC-220 protocol blob `2f355526476a4d41967bb46e1bfad6aa525cbfa9`;
- failed EXP-056 core blob `c472ed48e7b79d22056d43deb0fe09166ccf34c9`;
- EXP-055 predecessor core blob `c9517b7516940c78621448088c3933aa1c57e281`.

Each cell must also contain:

- six regressors;
- six pooled calibration references;
- 24 fit-temporal utility-support references;
- 12 fit-temporal feature-support references;
- 24 target-specific residual references;
- 12 residual-breadth lower bounds per eligible row;
- 12 residual lower-tail source bounds per eligible row;
- fixed lower-tail count of 3;
- lower-tail-aware consensus diagnostics and digest;
- exactly the three frozen candidate budgets;
- a seven-part cutoff for every available variant;
- deterministic cell result fingerprint.

## Seven-part cutoff

Available variants require the exact finite cutoff septuple:

1. residual lower-tail mean;
2. residual breadth;
3. residual-bound utility;
4. feature support;
5. fit-temporal utility support;
6. pooled calibrated utility;
7. raw utility.

Unavailable budgets expose all seven cutoff fields as null and cannot pass selection.

## Aggregate evidence

Complete aggregate evidence requires exactly all 18 model cells and verifies:

- 108 regressors;
- 108 pooled calibration references;
- 432 utility-support references;
- 216 feature-support references;
- 432 residual references;
- 12 residual-breadth bounds per eligible row;
- 12 lower-tail source bounds per eligible row;
- fixed lower-tail count of 3.

The aggregate payload receives a deterministic SHA-256 evidence fingerprint under the frozen canonical serializer.

## Forward locks

If a cell has no selected variant, validation and retrospective holdout must remain `LOCKED_NO_SELECTION`.

DEC-222 authorizes no downstream refit, recalibration, cutoff retuning, window-specific adjustment, or evidence substitution.

## Authorization state

DEC-222 keeps false:

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

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_artifacts.py`

Git blob:

`d69eb668ade480b66faf992190b3a4929f414960`

Focused tests:

`tests/test_phase8a_exp057_implementation_repair_artifacts.py`

Git blob:

`616bb6d8e1ab68336fdff4f04fb4018f36b51ffb`

Artifact-contract version:

`fmp-exp057-fit-temporal-residual-lower-tail-utility-implementation-repair-artifact-contract-v1`

## Next gate

After DEC-222 is green and merged, the next safe gate is a separate manual-main EXP-057 workflow/CLI/runtime source freeze with execution still closed.

No historical run is authorized by DEC-222.
