# Phase 8A — EXP-047 HGB Candidate-Density Training Core

**Date:** 2026-09-24
**Status:** SOURCE-ONLY; NO EXP-047 HISTORICAL RESULT AUTHORIZED
**Decision:** DEC-114
**Experiment:** EXP-20260924-047

## 1. Purpose

DEC-114 implements the deterministic in-memory training/evaluation core for the DEC-113 EXP-047 HGB candidate-density protocol.

The core remains source-only. It may be exercised by synthetic/unit tests, but it does not authorize an authoritative EXP-047 fit or result-producing historical workflow.

## 2. Frozen source bindings

DEC-114 binds:

- DEC-113 merge commit: `060bde94835158d62d47640aaf1a77ec56b483ff`
- DEC-113 protocol blob: `871936729a1090d675f6f5181ef04c8f32494394`
- predecessor base training core blob: `34b50a3f907d26b1c5ec50a0a0b444a3417d04f7`

Any byte drift in these sources fails the DEC-114 source validator.

## 3. HGB-only fit

The core fits exactly one family:

`hist_gradient_boosting`

It uses the unchanged predecessor HGB fit path and exact frozen HGB configuration.

Logistic regression is not fitted. Its result record is explicitly marked:

`EXCLUDED_BY_DEC112_DEC113`

with zero fit attempts.

## 4. Selection scoring

For each model cell:

1. validate and chronologically split the frozen feature/outcome frames;
2. fit HGB once on the unchanged fit split;
3. score the full 2021-2022 selection split once;
4. preserve the exact selection probability digest and classification diagnostics;
5. reuse that one probability matrix for all density anchors and all four temporal-stability windows.

No selection refit occurs.

## 5. Directional confidence and ranking

A row is density-eligible only when its unique top predicted class is LONG or SHORT.

Directional confidence is the predicted probability of that unique top directional class.

For each frozen budget anchor 250/500/1000:

- eligible rows are sorted by directional confidence descending;
- row identity ascending is the deterministic tie-order;
- the confidence of the budget-th ranked row is the selection-derived cutoff;
- every eligible row at or above that numeric cutoff becomes a candidate.

Therefore score ties at the cutoff may increase the candidate count above the nominal budget.

If fewer than the budget number of eligible directional rows exist, the variant is marked unavailable and cannot pass selection.

## 6. Aggregate gate and stability

Each available density variant is evaluated under the unchanged selection financial scenarios.

The unchanged aggregate gate remains mandatory, including the 250-candidate floor.

Only aggregate-gate passes are evaluated under the unchanged DEC-104 four-window temporal-stability screen.

The same selection-derived cutoff is used inside every stability window.

All four windows must pass.

## 7. Selection tie-break

Only variants passing both aggregate and stability gates enter selection.

Selection maximizes the predecessor material tie-break metrics:

1. total net pips;
2. directional candidate count.

If these are equal, the smaller candidate-budget anchor wins as a deterministic final tie-break.

The model family is constant HGB and therefore does not participate in the tie-break.

## 8. Forward evaluation

If a density variant is selected:

- validation is scored without refit;
- the exact selection-derived cutoff is applied unchanged;
- no validation budget or quantile is recomputed;
- validation must pass the unchanged validation gate before holdout unlocks.

If validation passes:

- retrospective holdout is scored without refit;
- the same exact selection-derived cutoff is applied unchanged;
- no holdout budget or quantile is recomputed.

This preserves the DEC-113 forward-application rule.

## 9. Result state

A cell with no aggregate+stability passing density variant ends at:

`NO_DENSITY_STABLE_MODEL_CHALLENGER`

A selected cell may proceed only through the unchanged validation and retrospective-holdout gates.

All result fingerprints remain canonical SHA-256 values over the frozen in-memory result object.

## 10. Source identity

Implementation:

`src/fmp/market_learning/model_successor_density_training.py`

Git blob:

`8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945`

Core version:

`fmp-exp047-hgb-density-training-core-v1`

Core decision:

`DEC-114`

## 11. Authorization state

DEC-114 keeps false:

- authoritative density-training result execution;
- model-fit authorization;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

The module contains no workflow dispatch, GitHub dispatch command, broker-send path, or alternate execution trigger.

## 12. Next gate

A later separate decision may freeze an artifact-backed EXP-047 runner/evidence contract around merged DEC-113/DEC-114.

No authoritative historical data loading, workflow, fit, or result-producing execution is authorized by DEC-114.
