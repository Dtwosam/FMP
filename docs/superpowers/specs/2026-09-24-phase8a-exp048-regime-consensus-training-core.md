# Phase 8A — EXP-048 HGB Fit-Regime Consensus Training Core

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; NO EXP-048 HISTORICAL RESULT AUTHORIZED
**Decision:** DEC-124
**Experiment:** EXP-20260924-048

## 1. Purpose

DEC-124 implements the deterministic in-memory training/evaluation core for the DEC-123 EXP-048 fit-regime consensus protocol.

The core remains source-only. It may be exercised by synthetic/unit tests, but it does not authorize an authoritative EXP-048 model fit or result-producing historical workflow.

## 2. Frozen source bindings

DEC-124 binds:

- DEC-123 merge commit: `39674f482e57922ac61fb0a6dff15a5ef621efd3`
- DEC-123 protocol blob: `39b6b3f5adc7f34ffd8cebcf881138d6ca3eab84`
- base training core blob: `34b50a3f907d26b1c5ec50a0a0b444a3417d04f7`
- unchanged EXP-047 density-helper core blob: `8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945`

Any byte drift in these dependencies fails the DEC-124 source validator.

## 3. Exact fit architecture

For each model cell, the unchanged outer fit interval is partitioned into the exact DEC-123 regime windows:

- `fit_2015_2016`
- `fit_2017_2018`
- `fit_2019_2020`

Each regime window:

- uses the unchanged chronological split semantics;
- must be non-empty;
- must contain all three target classes;
- fits exactly one `hist_gradient_boosting` model;
- fits its own preprocessing state using only that regime window;
- records exactly one fit attempt, preprocessor fingerprint, and model fingerprint.

No full-fit fallback model is fitted.

Logistic regression is not fitted.

## 4. Unanimous consensus scoring

Every scored split is evaluated by all three frozen regime models.

For each row:

1. each regime model produces the exact canonical LONG/SHORT/NO_TRADE probability vector;
2. each model must have a unique top class;
3. all three unique top classes must agree;
4. that common class must be LONG or SHORT.

Otherwise the row is `NO_TRADE`.

Consensus confidence is the minimum probability assigned to the agreed directional class across the three models.

The core records:

- each regime model's probability digest;
- consensus direction counts;
- consensus-eligible row count/rate;
- minimum and maximum eligible consensus confidence;
- a deterministic consensus digest over row identity, agreed direction, and consensus confidence.

No weighting, averaging, calibration, or majority vote is introduced.

## 5. Candidate-density anchors

The unchanged candidate-budget anchors remain:

- 250
- 500
- 1000

For each budget:

- only consensus-eligible selection rows participate;
- ranking is consensus confidence descending, row identity ascending;
- the budget-th confidence becomes the numeric cutoff;
- all eligible rows at or above that cutoff are candidates;
- ties may exceed the nominal budget;
- fewer than the budget number of eligible rows makes the variant unavailable.

## 6. Aggregate and temporal gates

Each available variant is evaluated through the unchanged financial metrics and aggregate gate.

The unchanged 250-candidate minimum remains mandatory.

Only aggregate passes enter the unchanged four-window temporal-stability screen.

The same selection-derived cutoff is reused inside every stability window.

All four windows must pass the unchanged:

- 10% minimum candidate share;
- positive total net pips;
- positive mean net pips;
- gross positive pips greater than absolute gross negative pips.

## 7. Selection tie-break

Only variants passing both aggregate and temporal-stability gates enter selection.

The deterministic tie-break is:

1. higher 0.5-pip total net pips;
2. higher directional candidate count;
3. smaller candidate-budget anchor.

No regime-specific performance term is introduced.

## 8. Forward evaluation

If a selection variant exists:

- validation is scored by the same three frozen regime models;
- the same unanimous direction rule is used;
- the exact selection-derived numeric cutoff is reused unchanged;
- no validation quantile or budget is recomputed;
- no refit occurs.

Only a validation pass unlocks retrospective holdout.

Retrospective holdout uses the identical three models, consensus rule, and frozen cutoff without refit or recomputation.

## 9. Result state

A cell without an aggregate+stability passing variant ends at:

`NO_REGIME_CONSENSUS_STABLE_MODEL_CHALLENGER`

The result preserves:

- exact protocol/source identities;
- exact processed-manifest identity;
- split row counts;
- three regime-model fit identities;
- consensus digests;
- density variants;
- unchanged aggregate/stability/validation/holdout gates;
- canonical result fingerprint.

## 10. Source identity

Implementation:

`src/fmp/market_learning/model_successor_regime_consensus_training.py`

Git blob:

`d902f9601ef3b04e0deaead18951d43350cb09be`

Core version:

`fmp-exp048-regime-consensus-training-core-v1`

Core decision:

`DEC-124`

Focused tests:

`tests/test_phase8a_exp048_regime_consensus_training.py`

Git blob:

`d2ce56fd55f3a2210642d568f8e3bc7a31a61271`

## 11. Authorization state

DEC-124 keeps false:

- authoritative EXP-048 result execution;
- model-fit authorization;
- workflow/dispatch authorization;
- logistic reintroduction;
- full-fit single-model fallback;
- density-anchor change;
- stability-screen change;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

The module contains no workflow dispatch, GitHub dispatch command, broker-send path, or alternate execution trigger.

## 12. Next gate

A later separate decision may freeze an artifact-backed EXP-048 runner/evidence contract around the merged DEC-123/DEC-124 sources.

No authoritative historical artifact loading, workflow, fit, or result-producing execution is authorized by DEC-124.
