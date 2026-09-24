# Phase 8A — EXP-050 Temporal-Jackknife Regime-Utility Successor Protocol

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY BEFORE ANY EXP-050 MODEL RESULT
**Decision:** DEC-141
**Experiment:** EXP-20260924-050

## 1. Purpose

DEC-141 freezes a separately identified successor protocol after DEC-140 found two simultaneous limitations in EXP-049:

1. 31 of 54 predeclared candidate-budget variants were unavailable because the frozen positive regime-utility consensus produced too few eligible rows; and
2. all eight aggregate-financial passes failed both candidate-share and financial temporal stability.

EXP-050 is explicitly post-result-informed and is not untouched out-of-sample evidence.

The successor does **not** lower the positive-utility requirement, change the candidate budgets, weaken any aggregate or temporal-stability gate, remove a 2021 window, retune HGB structure, or authorize a rerun.

The sole research change is the fit-view construction used by the same paired 0.5-pip utility regressors.

No model fit, historical result execution, workflow, dispatch, promotion, shadow/demo execution, broker mutation, order placement, or trading is authorized by DEC-141.

## 2. Predecessor binding

EXP-050 is bound to:

- predecessor experiment: `EXP-20260924-049`
- predecessor result decision: `DEC-139`
- predecessor diagnostic decision: `DEC-140`
- predecessor workflow run: `36029925264`
- predecessor execution commit: `eeb735bca7d38c3246f22a9606dfafe9c3df8279`
- predecessor evidence fingerprint: `29ecbb5bf3ce00f35c825e977d9b3fff1777e165ce9bef311fefcb7bfbdb091e`
- DEC-140 merge commit: `04f06deb4d68f9936438eec20dbb9610683bbc2e`
- DEC-140 diagnostic source blob: `e286be2574d4cee60322a4b65213af76ab34b381`
- DEC-139 reviewed-result source blob: `dce13838f32fbb8aa0e403c550b669f778dd0742`
- accepted predecessor model candidates: zero

EXP-049 remains closed to rerun or replacement.

## 3. Frozen unchanged research identity

EXP-050 preserves:

- EURUSD, GBPUSD, and USDJPY;
- 5m, 15m, and 1h feature timeframes;
- 60m and 240m horizons;
- all 18 pair/timeframe/horizon cells;
- the exact leakage-safe feature inputs;
- outer fit period 2015-01-01 through 2020-12-31;
- selection period 2021-01-01 through 2022-12-31;
- validation period 2023-01-01 through 2024-12-31;
- retrospective holdout 2025-01-01 through 2026-08-20;
- the exact three predecessor two-year fit-regime identities;
- the exact LONG/SHORT 0.5-pip financial targets;
- the exact HGB regression structural settings and runtime identity;
- candidate-budget anchors 250, 500, and 1000;
- aggregate minimum directional candidate count 250;
- the exact aggregate financial gate;
- the exact four half-year temporal-stability windows;
- the exact 10% per-window candidate-share floor;
- every existing per-window financial sign;
- exact validation and holdout cost scenarios;
- no refit after the fit stage.

Logistic regression and HGB classification remain excluded.

## 4. Sole research change: leave-one-regime-out fit views

EXP-049 fit each LONG/SHORT utility regressor on one isolated two-year regime:

- 2015-2016;
- 2017-2018;
- 2019-2020.

DEC-140 showed low positive-consensus coverage and no stable aggregate pass.

EXP-050 replaces those three narrow fit sets with three deterministic temporal-jackknife views. Each view trains on exactly two of the three frozen fit regimes and leaves the third completely out:

| View | Included regimes | Excluded regime | Fit years |
| --- | --- | --- | ---: |
| leave_out_fit_2015_2016 | 2017-2018 + 2019-2020 | 2015-2016 | 4 |
| leave_out_fit_2017_2018 | 2015-2016 + 2019-2020 | 2017-2018 | 4 |
| leave_out_fit_2019_2020 | 2015-2016 + 2017-2018 | 2019-2020 | 4 |

All three views use only rows inside the original 2015-2020 outer fit span.

The middle view is intentionally a union of two non-contiguous frozen regime blocks. Row identity and chronology remain unchanged; there is no interpolation, resampling, or forward leakage across the excluded block.

Each predecessor regime is excluded by exactly one view and included by exactly two views.

## 5. Why this targets DEC-140 without lowering gates

The temporal-jackknife construction increases each utility model's training support from two fit years to four while preserving an explicit temporal robustness stress:

- no view sees all six fit years;
- each historical two-year regime is withheld from one view;
- all three views must still independently agree on a positive direction;
- the score remains the least optimistic utility across the three views.

This is intended to reduce variance from very narrow regime-specific fits without replacing unanimity with majority voting, lowering the positive threshold, or averaging away disagreement.

It is a predeclared modeling change, not a post-result acceptance rescue.

## 6. Fit architecture

For each cell and each jackknife view, fit exactly two `HistGradientBoostingRegressor` models:

1. predicted LONG net pips at 0.5-pip adverse slippage;
2. predicted SHORT net pips at 0.5-pip adverse slippage.

That remains exactly six regressors per pair/timeframe/horizon cell.

For each view/target pair:

- construct the training row set as the union of the two explicitly included predecessor regimes;
- fit one median imputer only on that view's included rows;
- fit one HGB regressor on those same rows;
- do not borrow imputation state or rows from the excluded regime.

No view-weight search, subset-of-views fallback, full-fit fallback, classifier fallback, logistic model, probability calibration, or hyperparameter search is authorized.

## 7. Frozen regressor configuration

The regressor configuration is inherited exactly from EXP-049:

- loss: squared_error
- learning_rate: 0.05
- max_iter: 100
- max_leaf_nodes: 15
- max_depth: 3
- min_samples_leaf: 20
- l2_regularization: 1.0
- max_features: 1.0
- max_bins: 255
- early_stopping: false
- warm_start: false
- random_state: 20260923

DEC-141 changes fit-view row membership only.

## 8. Per-view direction rule

For every scored row and every jackknife view:

1. predict LONG 0.5-pip net utility;
2. predict SHORT 0.5-pip net utility;
3. choose LONG only if LONG is the unique larger prediction and LONG is greater than zero;
4. choose SHORT only if SHORT is the unique larger prediction and SHORT is greater than zero;
5. otherwise choose NO_TRADE.

A zero or negative best predicted utility cannot create a directional vote.

A LONG/SHORT predicted-utility tie cannot create a directional vote.

The positive-utility requirement is unchanged.

## 9. Temporal-jackknife consensus

A row is eligible only when all three jackknife views independently choose the same LONG or SHORT direction.

Any view disagreement or any view NO_TRADE result makes the row ineligible.

For an eligible row, robust utility is:

`minimum predicted net pips for the agreed direction across the three jackknife views`

No mean, maximum, weighted average, learned ensemble weight, selection-tuned weight, or majority vote is authorized.

## 10. Candidate-density anchors

The candidate-budget anchors remain:

- 250
- 500
- 1000

For each cell:

1. score the selection split with the same six frozen jackknife-view regressors;
2. keep only consensus-eligible rows;
3. sort robust utility descending and row identity ascending;
4. for each budget, use the budget-th ranked robust utility as the numeric cutoff;
5. include every eligible row at or above that cutoff.

Ties may exceed the nominal budget.

A budget is unavailable if fewer than the requested number of eligible selection rows exist.

No smaller budget rescue, per-window budget, quantile, cutoff, or utility recalibration is authorized.

## 11. Aggregate selection gate remains unchanged

Every available budget must still satisfy the exact 0.5-pip aggregate gate:

- directional candidate count at least 250;
- total net pips greater than zero;
- mean net pips greater than zero;
- gross positive pips greater than absolute gross negative pips.

Only aggregate passes may enter the stability screen.

## 12. Temporal stability remains unchanged

The exact four windows remain:

- selection_2021_h1;
- selection_2021_h2;
- selection_2022_h1;
- selection_2022_h2.

Every window must still satisfy all of:

- directional candidate share at least 10% of full-selection candidates;
- total net pips greater than zero;
- mean net pips greater than zero;
- gross positive pips greater than absolute gross negative pips.

No window may be removed.

No share or financial requirement may be weakened.

The same selection-derived cutoff must be used inside every stability window.

## 13. Selection and forward application

Only variants passing both aggregate and all four stability windows are selectable.

The predecessor material tie-break remains unchanged:

1. higher realized selection total net pips at 0.5-pip cost;
2. higher directional candidate count;
3. smaller candidate-budget anchor.

After selection:

- the exact six regressors remain frozen;
- the exact three jackknife view definitions remain frozen;
- the same positive-utility direction rule remains frozen;
- the same unanimous three-view consensus remains frozen;
- the same minimum predicted utility score remains frozen;
- the exact selection-derived numeric robust-utility cutoff is reused unchanged.

Validation does not refit, rebuild views, change included rows, recompute a budget, or recalibrate utility.

Retrospective holdout, if unlocked by validation, uses the same frozen model/rule/cutoff identity.

## 14. Multiple-comparison and evidence status

EXP-050 is explicitly informed by EXP-049 and DEC-140.

Historical evidence through 2026-08-20 remains retrospective/already seen.

No EXP-050 historical result can be described as untouched OOS.

No post-result threshold, view-weight, or fit-view rescue is authorized under this protocol.

## 15. Source identity

Protocol source:

`src/fmp/market_learning/model_successor_temporal_jackknife_utility_protocol.py`

Protocol source Git blob:

`b41b817b03aa0cc03a9d893227caa399b46d3cf8`

Focused tests:

`tests/test_phase8a_exp050_temporal_jackknife_utility_protocol.py`

Focused test Git blob:

`f458891e6160bb4e3af6c7a4b82b69b37771efe7`

Protocol version:

`fmp-exp050-temporal-jackknife-utility-protocol-v1`

Protocol decision:

`DEC-141`

## 16. Authorization state

DEC-141 keeps false:

- model-protocol result production;
- model fitting;
- historical result execution;
- feature change;
- financial-target change;
- outer chronology change;
- HGB structural retuning;
- positive-utility requirement change;
- jackknife-view weight search;
- jackknife-view fallback;
- density-anchor change;
- minimum-candidate-count change;
- stability-screen change;
- per-window financial-gate change;
- per-window cutoff tuning;
- per-window utility recalibration;
- logistic reintroduction;
- classifier fallback;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 17. Next gate

A later separate decision may implement the deterministic EXP-050 in-memory training/evaluation core.

That implementation must bind the exact DEC-141 protocol source, construct exactly the three frozen leave-one-regime-out views, fit exactly six regressors per cell, preserve all selection/stability/forward semantics, and remain non-executable until a later artifact/evidence and run-authorization chain is separately frozen.
