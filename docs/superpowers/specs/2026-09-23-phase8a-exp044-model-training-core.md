# Phase 8A — EXP-044 Deterministic Model-Training Core

**Date:** 2026-09-23
**Status:** APPROVED — SOURCE IMPLEMENTATION ONLY; HISTORICAL RESULT RUN STILL LOCKED
**Decision:** DEC-090
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-088 froze the model-training protocol and DEC-089 machine-bound that protocol to the verified DEC-074 preparation chain.

DEC-090 implements the deterministic in-memory training/evaluation core for that frozen protocol without adding a GitHub Actions training workflow, a CLI entry point, or any historical EXP-044 model result.

Synthetic unit-test fits are permitted only to verify source behavior. They are not EXP-044 historical evidence and do not change any execution, promotion, or trading authorization.

## 2. Frozen protocol identity

The core consumes the unchanged DEC-088 contract:

- decision: `DEC-088`;
- version: `fmp-exp044-model-protocol-v1`;
- protocol fingerprint: `1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605`;
- exactly 18 pair/timeframe/horizon cells;
- exactly 48 model-input feature values;
- target: `best_direction_0p5`;
- model families: fixed L2 logistic regression and fixed histogram gradient boosting;
- thresholds: 0.50, 0.60, 0.70;
- no refit after the fit split.

## 3. Input and join contract

The core accepts one feature frame and one outcome frame for a single `ModelCell`.

It validates:

- exact symbol/timeframe/horizon identity;
- required feature and outcome columns;
- `fmp-market-feature-v1` and `fmp-market-outcome-grid-v1` identities;
- `RETROSPECTIVE_ALREADY_SEEN` evidence labeling;
- one exact processed Phase 2 manifest SHA-256;
- unique feature and outcome identities;
- exact horizon timing;
- finite scenario PnL values;
- consistency between each frozen best-direction label and its corresponding long/short net-pip values.

Features and outcomes are joined only on the frozen market-learning feature identity. Missing exact-horizon rows remain excluded rather than shifted or repaired.

## 4. Chronology

The DEC-088 chronological splits are applied from `available_at_utc` and `exit_timestamp_utc`.

A row is admitted only when both its observation availability and its exact target exit remain inside the split. This preserves the 60m/240m boundary purge.

Every required split must be non-empty. The fit split must contain all three frozen target classes.

## 5. Fit behavior

Each model family is fit exactly once on the fit split.

Preprocessing reuses the already-tested deterministic Phase 6 preprocessing implementation because its mechanics match DEC-088:

- fit-period median imputation;
- fail closed on an all-null fit column;
- fit-period standardization for logistic regression only;
- no scaling for histogram gradient boosting.

The estimator configurations are imported directly from DEC-088. No hyperparameter search, calibration, resampling, class weighting, or refit is introduced.

## 6. Selection

Each fitted family scores the selection split once.

For each family, the fixed 0.50, 0.60, and 0.70 confidence thresholds create the six frozen variants.

The core computes the frozen 0.5-pip financial selection gate:

- at least 250 directional candidates;
- strictly positive total net pips;
- strictly positive mean net pips;
- gross positive pips greater than absolute gross negative pips.

If more than one variant passes, the exact DEC-088 deterministic tie-break is applied.

If none passes, the result is `NO_MODEL_CHALLENGER`; validation and holdout remain locked.

## 7. Validation and retrospective holdout

The selected fitted model is reused unchanged. There is no refit.

Validation evaluates the selected threshold under:

- 0.2 pip diagnostic;
- 0.5 pip mandatory gate;
- 1.0 pip mandatory gate.

Only if both mandatory validation scenarios pass may the retrospective 2025-2026 holdout open.

The holdout reuses the exact same fitted preprocessor, estimator, and selected confidence threshold and applies the same 0.5/1.0 mandatory gate with 0.2 as diagnostic.

The holdout remains retrospective already-seen evidence and is not prospective/OOS proof.

## 8. Deterministic evidence

The in-memory result records:

- protocol identity and fingerprint;
- processed-manifest identity;
- split row counts;
- fit target counts;
- per-family preprocessor and fitted-model fingerprints;
- multiclass log loss and confusion matrices;
- probability digests;
- all six selection variants;
- selected variant identity or `NO_MODEL_CHALLENGER`;
- per-scenario candidate counts and PnL metrics;
- candidate-identity digests;
- validation/holdout lock or gate status;
- one canonical result fingerprint.

Negative results are first-class evidence.

## 9. Source-only execution boundary

DEC-090 deliberately adds no:

- `.github/workflows/phase8a-exp044-model-training.yml`;
- model-training CLI command;
- authoritative artifact loader;
- GitHub workflow dispatch mapping;
- historical EXP-044 run.

`MODEL_TRAINING_RESULT_EXECUTION_AUTHORIZED` remains false.

Synthetic unit tests may call the core on generated frames solely to prove deterministic implementation behavior.

## 10. Authorization locks

DEC-090 does not authorize:

- authoritative historical model fitting;
- model-protocol result publication;
- promotion;
- shadow campaign admission;
- demo orders;
- broker mutation;
- live orders;
- real-money trading.

## 11. Next gate

A later separate decision must bind the exact merged DEC-090 source identity before adding an authoritative artifact-backed runner/workflow or enabling any result-producing historical fit.

That later gate must still revalidate the DEC-088 protocol fingerprint and the verified DEC-074 evidence chain before execution.
