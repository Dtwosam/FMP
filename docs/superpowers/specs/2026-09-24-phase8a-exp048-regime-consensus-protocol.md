# Phase 8A — EXP-048 HGB Fit-Regime Consensus Successor Protocol

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY BEFORE ANY EXP-048 MODEL RESULT
**Decision:** DEC-123
**Experiment:** EXP-20260924-048

## 1. Purpose

DEC-123 freezes a separately identified successor protocol after DEC-122 recorded temporal/regime concentration as the dominant observed EXP-047 failure mode.

EXP-048 is explicitly post-result-informed and is not untouched OOS.

The protocol preserves the frozen HGB model configuration, candidate-density anchors, aggregate financial gates, validation/holdout chronology, and four-window stability screen. Its sole research change is the fit architecture: replace one full-fit HGB model with three disjoint fit-era HGB models and require unanimous directional consensus before a row is eligible.

DEC-123 authorizes no model fit, historical result execution, workflow, dispatch, promotion, shadow/demo execution, broker mutation, order placement, or trading.

## 2. Predecessor binding

EXP-048 is bound to:

- predecessor experiment: `EXP-20260924-047`
- predecessor result decision: `DEC-121`
- predecessor diagnostic decision: `DEC-122`
- predecessor run: `35993400007`
- predecessor result evidence fingerprint: `f047310749a2742d75d2e448243080d368b6a5cdf66bc119ec33e59cc192352f`
- DEC-122 merge commit: `c893bd8b69743b28c8488854b3b026e69e62362e`
- DEC-122 diagnostic source blob: `ceb18c634af55051d2bbd5c749a7bc5862eba470`

EXP-047 remains closed to rerun or replacement.

## 3. Frozen unchanged research identity

EXP-048 preserves:

- symbols: EURUSD, GBPUSD, USDJPY;
- timeframes: 5m, 15m, 1h;
- horizons: 60m and 240m;
- 18 model cells;
- exact 48 feature columns;
- target: `best_direction_0p5`;
- target slippage: 0.5 pips per fill;
- target classes: LONG, SHORT, NO_TRADE;
- outer fit period: 2015-01-01 through 2020-12-31;
- selection split: 2021-01-01 through 2022-12-31;
- validation split: 2023-01-01 through 2024-12-31;
- retrospective holdout: 2025-01-01 through 2026-08-20;
- exact frozen HGB hyperparameters/runtime;
- HGB-only family scope;
- candidate-budget anchors: 250, 500, 1000;
- aggregate minimum directional candidates: 250;
- exact aggregate financial gate;
- exact DEC-104 four half-year stability windows;
- exact 10% per-window candidate-share floor;
- positive financial signs in every stability window;
- exact validation/holdout scenarios;
- no refit after the fit stage.

Logistic regression remains excluded.

## 4. Sole protocol change: three disjoint fit-regime models

The original 2015-2020 fit period is partitioned into exactly three contiguous non-overlapping windows:

| Regime model | Start | End exclusive |
| --- | --- | --- |
| fit_2015_2016 | 2015-01-01 | 2017-01-01 |
| fit_2017_2018 | 2017-01-01 | 2019-01-01 |
| fit_2019_2020 | 2019-01-01 | 2021-01-01 |

Each window trains its own HGB model using the exact frozen HGB configuration and preprocessing fitted only on that regime window.

All three regime models are mandatory.

No fallback to a single full-fit model, subset of regime models, alternate model family, or retuned HGB configuration is authorized.

## 5. Directional consensus

For any scored row:

1. score the row with all three frozen regime models;
2. determine each model's unique top predicted class;
3. the row is consensus-eligible only when all three unique top classes are identical;
4. that common class must be LONG or SHORT;
5. disagreement, any NO_TRADE top class, or any top-class tie makes the row ineligible and therefore NO_TRADE.

The frozen rule is:

`all three regime models must agree on the same unique directional top class`

This is intended to require a candidate direction to be supported across distinct fit-era regimes before selection-period density/gating is considered.

## 6. Consensus confidence

For a consensus-eligible row, consensus confidence is:

`minimum(probability assigned to the agreed directional class across the three regime models)`

The minimum, rather than the mean or maximum, is frozen to prevent one strongly confident regime model from masking weak support in another fit regime.

No learned model weights, selection-tuned weights, calibration, or voting threshold are authorized.

## 7. Candidate-density anchors

The frozen candidate-budget anchors remain:

- 250
- 500
- 1000

For each cell/horizon:

1. score the selection split with all three regime models;
2. retain only consensus-eligible rows;
3. rank them by consensus confidence descending and row identity ascending;
4. for each budget, use the budget-th ranked row's consensus confidence as the numeric cutoff;
5. include every eligible row at or above the cutoff.

Score ties may exceed the nominal budget.

A budget variant is unavailable if fewer than the budget number of consensus-eligible selection rows exist.

## 8. Aggregate and temporal gates

Every available budget variant must still pass the unchanged aggregate financial gate.

The 250-candidate aggregate floor remains mandatory.

Only aggregate passes enter the unchanged four-window temporal-stability screen.

All four windows must pass the unchanged:

- minimum 10% candidate share;
- positive total net pips;
- positive mean net pips;
- gross positive pips greater than absolute gross negative pips.

DEC-123 does not relax any reviewed EXP-047 stability criterion.

## 9. Forward application

The three regime models are frozen after the fit stage.

For a selected variant:

- validation uses the same three models;
- the same unanimous direction rule;
- the same minimum consensus-confidence definition;
- the exact numeric cutoff derived from selection;
- no validation quantile or budget recomputation;
- no refit.

If validation passes, retrospective holdout uses the identical frozen models/rule/cutoff.

## 10. Selection tie-break

Variants passing aggregate and stability gates use the predecessor material tie-break:

1. total net pips;
2. directional candidate count;
3. smaller candidate-budget anchor.

No regime-specific performance weight is added to the tie-break.

## 11. Source identity

Protocol source:

`src/fmp/market_learning/model_successor_regime_consensus_protocol.py`

Git blob:

`e104383600f13ccc9d1bdc2176a778f9cd5bf539`

Focused tests:

`tests/test_phase8a_exp048_regime_consensus_protocol.py`

Git blob:

`2d9f479d8e01b9c71d51db82ed23e622d8f4a22b`

Protocol version:

`fmp-exp048-regime-consensus-protocol-v1`

Protocol decision:

`DEC-123`

## 12. Authorization state

DEC-123 keeps false:

- model-protocol result production;
- model fitting;
- historical result execution;
- feature change;
- target change;
- outer chronology change;
- HGB hyperparameter change;
- density-anchor change;
- minimum-candidate-count change;
- stability-screen change;
- logistic reintroduction;
- single full-fit fallback;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 13. Next gate

A later separate decision may implement a deterministic EXP-048 training/evaluation core that adds only the frozen three-regime fit and consensus mechanics around the unchanged HGB/density/stability pipeline.

That implementation must bind the exact DEC-123 protocol source before any result-producing workflow or fit is authorized.
