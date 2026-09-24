# Phase 8A — EXP-047 HGB Candidate-Density Successor Protocol

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY BEFORE ANY EXP-047 MODEL RESULT
**Decision:** DEC-113
**Experiment:** EXP-20260924-047

## 1. Purpose

DEC-113 freezes a separately identified successor protocol after DEC-112 established that HGB material candidate decisions reproduce across EXP-045/046 while logistic family availability does not.

EXP-047 is explicitly post-result-informed and is not untouched OOS.

The protocol changes only the mapping from HGB selection probabilities to candidate density. It does not lower the 250-candidate aggregate floor and does not weaken the four-window temporal-stability screen.

DEC-113 authorizes no model fit, historical result execution, workflow, dispatch, promotion, shadow/demo execution, broker mutation, order placement, or trading.

## 2. Predecessor binding

EXP-047 is bound to:

- predecessor experiment: `EXP-20260923-046`
- predecessor result decision: `DEC-111`
- predecessor result evidence fingerprint: `499c91e4508f07bf8a637657969175fbba8e93d07236b94ded06ae884b386214`
- predecessor reproducibility decision: `DEC-112`
- DEC-111 merge: `0fca0ec79f75c07a9cbabaae57ddaee6cafac651`
- DEC-112 merge: `42c6a20388a406a0c350d9ea9e0cfdb64b6d7fbc`
- DEC-112 source blob: `cf4f6ee1a7d387c3a48269a9f6aea8212dd56b1b`

Logistic regression is excluded from EXP-047 result-producing participation because DEC-112 records family-availability reproducibility failure.

## 3. Frozen HGB density diagnostic

The persisted EXP-046 HGB variants show:

- evaluated HGB variants: **54**
- variants meeting the existing 250-candidate count criterion: **23**
- variants with positive gross/mean/total financial signs: **13**
- variants passing the full aggregate selection gate: **1**
- positive-financial-sign variants below the 250-candidate floor: **12**

The sole HGB aggregate-gate pass, GBPUSD 5m / 240m at confidence 0.6, failed the existing temporal-stability screen.

Therefore DEC-113 does not relax the candidate floor or stability screen. Instead it replaces the three absolute HGB confidence thresholds with selection-derived density anchors.

## 4. Frozen unchanged research identity

EXP-047 preserves the exact predecessor:

- symbols: EURUSD, GBPUSD, USDJPY;
- timeframes: 5m, 15m, 1h;
- horizons: 60m and 240m;
- 18 model cells;
- exact 48 feature columns;
- target: `best_direction_0p5`;
- target slippage: 0.5 pips per fill;
- target classes: LONG, SHORT, NO_TRADE;
- fit split: 2015-01-01 through 2020-12-31;
- selection split: 2021-01-01 through 2022-12-31;
- validation split: 2023-01-01 through 2024-12-31;
- retrospective holdout: 2025-01-01 through 2026-08-20;
- no refit after the fit split;
- exact frozen HGB configuration;
- exact selection/validation/holdout cost scenarios;
- exact aggregate financial gate;
- minimum directional candidates: 250;
- exact DEC-104 four-half-year temporal-stability windows;
- minimum 10% selection-candidate share in every stability window;
- positive financial signs required in every stability window.

No feature, target, chronology, HGB model-config, candidate-count floor, or stability-screen change is authorized.

## 5. Model-family boundary

The only authorized model family in EXP-047 is:

`hist_gradient_boosting`

Logistic regression is excluded.

DEC-113 does not attempt to repair logistic regression and does not authorize a solver, preprocessing, tolerance, iteration-limit, threading, or numerical-runtime remedy.

A later independent experiment may study logistic numerical reproducibility, but it cannot silently re-enter EXP-047.

## 6. Candidate-density anchors

The frozen selection candidate-budget anchors are:

- **250**
- **500**
- **1000**

For each HGB cell/horizon:

1. score the full frozen selection split once;
2. identify rows whose unique top predicted class is LONG or SHORT;
3. define directional confidence as the predicted probability of that unique directional top class;
4. sort eligible selection rows by directional confidence descending, then row identity ascending;
5. for each budget anchor, use the directional confidence of the budget-th ranked eligible row as the frozen numeric cutoff;
6. select every eligible row whose directional confidence is greater than or equal to that cutoff.

Ties at the cutoff may therefore produce more candidates than the nominal budget anchor.

A budget variant is unavailable if fewer than the budget number of eligible directional rows exist.

## 7. Aggregate and temporal gates

Every budget variant must still pass the unchanged aggregate selection gate, including:

- directional candidate count >= 250;
- positive total net pips;
- positive mean net pips;
- gross positive pips greater than absolute gross negative pips.

Only aggregate-gate passes are evaluated under the unchanged four-window temporal-stability screen.

All four stability windows must pass.

The budget anchor is therefore a density-generation mechanism, not an acceptance criterion and not a relaxation of any existing gate.

## 8. Forward application

The exact numeric confidence cutoff derived from the 2021-2022 selection split is frozen for that variant.

Validation and retrospective holdout:

- do not recompute a quantile;
- do not choose a new budget;
- do not retune the cutoff;
- apply the exact selection-derived cutoff unchanged.

Validation remains required before retrospective holdout is unlocked.

## 9. Selection tie-break

Variants passing both the aggregate gate and all temporal-stability windows use the predecessor selection tie-break.

If predecessor tie-break metrics are exactly equal, the smaller candidate-budget anchor wins as a final deterministic tie-break.

## 10. Source identity

Protocol source:

`src/fmp/market_learning/model_successor_density_protocol.py`

Git blob:

`871936729a1090d675f6f5181ef04c8f32494394`

Protocol version:

`fmp-exp047-hgb-density-protocol-v1`

Protocol decision:

`DEC-113`

## 11. Authorization state

DEC-113 keeps false:

- model-protocol result production;
- model fitting;
- historical result execution;
- logistic reintroduction;
- feature change;
- target change;
- chronology change;
- HGB model-config change;
- minimum-candidate-count change;
- temporal-stability-screen change;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 12. Next gate

A later separate decision may implement a deterministic EXP-047 training/evaluation core that adds only the frozen candidate-density mapping around the unchanged HGB fit and unchanged acceptance gates.

That implementation must bind the exact DEC-113 protocol source before any result-producing workflow or fit is authorized.
