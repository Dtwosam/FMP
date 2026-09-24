# Phase 8A — EXP-049 HGB Regime-Utility Successor Protocol

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY BEFORE ANY EXP-049 MODEL RESULT
**Decision:** DEC-132
**Experiment:** EXP-20260924-049

## 1. Purpose

DEC-132 freezes a separately identified successor protocol after DEC-131 recorded window-level financial instability as the dominant observed EXP-048 failure mode.

EXP-049 is explicitly post-result-informed and is not untouched out-of-sample evidence.

The protocol does not relax the reviewed stability screen. Instead, it changes the learning objective so the model estimates the same cost-aware financial quantity that the stability gate later tests.

No model fit, historical result execution, workflow, dispatch, promotion, shadow/demo execution, broker mutation, order placement, or trading is authorized by this decision.

## 2. Predecessor binding

EXP-049 is bound to:

- predecessor experiment: EXP-20260924-048
- predecessor result decision: DEC-130
- predecessor diagnostic decision: DEC-131
- predecessor run: 36006524422
- predecessor result evidence fingerprint: acd3a9d7708c345b05082026de9eecc515abb9090a901126034e91173eb30647
- DEC-131 merge commit: c07127c9651818b3dea817976a0e87ea76765f38
- DEC-131 diagnostic source blob: 165ab1e0e10a9fb6453ad0880ea1df97d0a35fa8
- accepted predecessor model challengers: zero

DEC-131 observed 17 aggregate selection passes, 17 window-financial rejections, 13 candidate-share rejections, and four variants that satisfied the share requirement in every window but still failed a financial window.

EXP-048 remains closed to rerun or replacement.

## 3. Frozen unchanged research identity

EXP-049 preserves:

- EURUSD, GBPUSD, and USDJPY;
- 5m, 15m, and 1h feature timeframes;
- 60m and 240m horizons;
- all 18 pair/timeframe/horizon cells;
- the exact 48 leakage-safe feature inputs;
- outer fit period 2015-01-01 through 2020-12-31;
- selection period 2021-01-01 through 2022-12-31;
- validation period 2023-01-01 through 2024-12-31;
- retrospective holdout 2025-01-01 through 2026-08-20;
- the exact three disjoint fit-regime windows from EXP-048;
- the structural HGB settings and scikit-learn runtime identity;
- candidate-budget anchors 250, 500, and 1000;
- aggregate minimum directional candidate count 250;
- the exact aggregate financial gate;
- the exact four DEC-104 half-year stability windows;
- the exact 10% per-window candidate-share floor;
- every existing per-window financial sign;
- exact validation and holdout cost scenarios;
- no refit after the fit stage.

Logistic regression remains excluded.

No classifier fallback is authorized.

## 4. Sole research change: direct financial utility objective

EXP-048 learned a three-class direction label and ranked candidates by class probability consensus.

DEC-131 showed that every aggregate-passing variant still failed at least one realized financial stability window.

EXP-049 therefore replaces the predecessor class target for model fitting with the two already materialized, cost-aware 0.5-pip outcome columns:

- long_net_pips_0p5
- short_net_pips_0p5

The 0.5-pip values already include the frozen adverse slippage assumption used by the selection financial gate.

No new market-data source, feature, label horizon, or cost scenario is introduced.

The old best_direction_0p5 class remains part of the immutable historical outcome artifact, but it is not the EXP-049 fit target.

## 5. Fit architecture

The outer 2015-2020 fit span remains partitioned into exactly three contiguous non-overlapping windows:

| Regime | Start | End exclusive |
| --- | --- | --- |
| fit_2015_2016 | 2015-01-01 | 2017-01-01 |
| fit_2017_2018 | 2017-01-01 | 2019-01-01 |
| fit_2019_2020 | 2019-01-01 | 2021-01-01 |

For each cell and each regime, fit exactly two HistGradientBoostingRegressor models:

1. predicted LONG net pips at 0.5-pip adverse slippage;
2. predicted SHORT net pips at 0.5-pip adverse slippage.

That is exactly six regressors per pair/timeframe/horizon cell.

Each regressor fits its own median-imputation state using only rows from its fit regime.

No regime may borrow preprocessing state from another regime.

No full-fit fallback, subset-of-regimes fallback, classifier fallback, logistic model, ensemble weight search, or probability calibration is authorized.

## 6. Frozen regressor configuration

The regressor uses squared-error loss.

The structural settings are inherited unchanged from the frozen HGB classifier configuration:

- learning_rate 0.05
- max_iter 100
- max_leaf_nodes 15
- max_depth 3
- min_samples_leaf 20
- l2_regularization 1.0
- max_features 1.0
- max_bins 255
- early_stopping false
- warm_start false
- random_state 20260923

The objective change from classification to direct financial regression is the research change. Structural retuning is not part of DEC-132.

## 7. Per-regime direction rule

For each scored row and each fit regime:

1. predict LONG 0.5-pip net utility;
2. predict SHORT 0.5-pip net utility;
3. choose LONG only if LONG is the unique larger prediction and LONG is greater than zero;
4. choose SHORT only if SHORT is the unique larger prediction and SHORT is greater than zero;
5. otherwise choose NO_TRADE.

A zero or negative best predicted utility cannot create a directional vote.

A LONG/SHORT predicted-utility tie cannot create a directional vote.

## 8. Regime-utility consensus

A row is eligible only when all three fit regimes independently choose the same LONG or SHORT direction.

Any regime disagreement or any regime NO_TRADE result makes the row ineligible.

For an eligible row, robust utility is:

minimum predicted net pips for the agreed direction across the three fit regimes.

This deliberately uses the least optimistic regime estimate. Mean, maximum, weighted average, learned ensemble weight, or selection-tuned aggregation is not authorized.

The robust utility must be positive by construction because every regime must independently vote for the same positive-utility direction.

## 9. Candidate-density anchors

The frozen candidate budgets remain:

- 250
- 500
- 1000

For each cell:

1. score the selection split with the same six frozen regressors;
2. keep only regime-utility-consensus-eligible rows;
3. sort robust utility descending and row identity ascending;
4. for each budget, take the budget-th ranked robust-utility value as the numeric cutoff;
5. include every eligible row at or above that cutoff.

Ties may produce more candidates than the nominal budget.

A budget is unavailable if fewer than the requested number of eligible selection rows exist.

No per-window budget, quantile, cutoff, or utility recalibration is authorized.

## 10. Aggregate selection gate

Every available budget must still satisfy the predecessor aggregate gate at the exact 0.5-pip scenario:

- directional candidate count at least 250;
- total net pips greater than zero;
- mean net pips greater than zero;
- gross positive pips greater than absolute gross negative pips.

The direct financial objective does not substitute for this realized financial gate.

Only aggregate passes may enter the stability screen.

## 11. Temporal stability gate remains unchanged

The exact four windows remain:

- selection_2021_h1
- selection_2021_h2
- selection_2022_h1
- selection_2022_h2

Every window must still satisfy all of:

- directional candidate share at least 10% of the full-selection candidate count;
- total net pips greater than zero;
- mean net pips greater than zero;
- gross positive pips greater than absolute gross negative pips.

No 2021 window may be removed.

No financial requirement may be weakened.

No candidate-share floor may be weakened.

EXP-049 is designed to target financial generalization before this gate, not to change the gate after seeing results.

## 12. Selection and tie-break

Only variants passing both aggregate and four-window stability gates are selectable.

Among selectable variants, retain the existing material ordering:

1. higher realized selection total net pips at 0.5-pip cost;
2. higher directional candidate count;
3. smaller candidate-budget anchor.

No fit-regime-specific realized performance weight is added.

## 13. Forward application

After selection:

- the exact six regressors remain frozen;
- the same per-regime positive-utility direction rule remains frozen;
- the same unanimous three-regime consensus rule remains frozen;
- the same minimum predicted utility score remains frozen;
- the exact selection-derived numeric robust-utility cutoff is reused unchanged.

Validation does not recompute a budget or cutoff.

Validation does not refit or recalibrate the utility models.

Retrospective holdout, if unlocked by validation, uses the same frozen model/rule/cutoff identity.

## 14. Why this is not a gate relaxation

DEC-131 found that four EXP-048 variants already satisfied the candidate-share requirement in all windows but still failed a financial window.

EXP-049 does not respond by reducing the 10% floor, dropping a half-year, accepting zero/negative financial signs, or widening candidate density after the result.

It moves the fit objective closer to the realized net-pip quantity while leaving the acceptance conditions untouched.

That makes a future failure informative: direct cost-aware utility modeling still failed the already-reviewed financial generalization standard.

## 15. Multiple-comparison and evidence status

EXP-049 is explicitly informed by EXP-048 results.

Historical evidence through 2026-08-20 remains retrospective/already seen.

No EXP-049 historical result can be described as untouched OOS.

A future result must be labeled prior-result-informed.

No post-result threshold rescue is authorized under this protocol.

## 16. Source identity

Protocol source:

src/fmp/market_learning/model_successor_regime_utility_protocol.py

Protocol source Git blob:

ad2fcb22656fc7a1490f4cdf87fb25c62895a1ac

Focused tests:

tests/test_phase8a_exp049_regime_utility_protocol.py

Focused test Git blob:

647523e86bcf7d54755ea745866ab7c66c89dc6d

Protocol version:

fmp-exp049-regime-utility-protocol-v1

Protocol decision:

DEC-132

## 17. Authorization state

DEC-132 keeps false:

- model-protocol result production;
- model fitting;
- historical result execution;
- feature change;
- further target change after the frozen two financial targets;
- outer chronology change;
- HGB structural retuning;
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

## 18. Next gate

A later separate decision may implement the deterministic EXP-049 training/evaluation core.

That implementation must bind the exact DEC-132 protocol source, fit exactly six regressors per cell, preserve the exact selection/stability/forward semantics above, and remain non-executable until a later artifact/evidence and run-authorization chain is separately frozen.
