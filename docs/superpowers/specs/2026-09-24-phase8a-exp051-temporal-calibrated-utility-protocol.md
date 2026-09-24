# Phase 8A — EXP-051 Out-of-Fit Calibrated Utility Successor Protocol

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY BEFORE ANY EXP-051 MODEL RESULT
**Decision:** DEC-150
**Experiment:** EXP-20260924-051

## 1. Purpose

DEC-150 freezes a separately identified successor protocol after DEC-149 recorded that EXP-050 increased utility-eligible coverage but still concentrated every aggregate pass in USDJPY 5m / 60m and produced zero candidates in 2021 H1 for all three passing variants.

EXP-051 is explicitly post-result-informed retrospective research. It is not untouched out-of-sample evidence.

The protocol preserves the complete EXP-050 model, chronology, eligibility, budget, aggregate-financial, temporal-stability, validation, and holdout structure. Its sole research change is the ranking scale:

- raw predicted utility still determines direction eligibility exactly as in EXP-050;
- each jackknife view's utility prediction is calibrated against predictions made on that view's own excluded fit regime;
- candidate ranking uses the minimum calibrated percentile across the three views rather than the minimum raw predicted utility alone.

The objective is to test whether score-scale drift across historical fit eras contributed to the later-period concentration observed in DEC-149 without forcing candidate counts into any selection window and without relaxing the stability gate.

DEC-150 authorizes no model fit, historical result execution, workflow, dispatch, promotion, shadow/demo execution, broker mutation, order placement, real-money action, or trading.

## 2. Predecessor binding

EXP-051 is bound to:

- predecessor experiment: `EXP-20260924-050`
- predecessor result decision: `DEC-148`
- predecessor diagnostic decision: `DEC-149`
- predecessor workflow run: `36049824739`
- predecessor execution commit: `25d48828b981c4309f4a859d2a33a56094638f21`
- predecessor result evidence fingerprint: `866b4a8f26553bad8c80a7b2e0e68aedb50bfa42b3c767ce91478c9dfd720023`
- DEC-149 merge commit: `d8874bf213c420fb506cc9ee8c4dfb2caffbb9e1`
- DEC-149 diagnostic source blob: `f23465ca30249ce8abab3c9fdf07ce39a8679a9a`
- DEC-148 reviewed-result source blob: `70402f6c21f4ed22b4991025c98e6c1664215215`
- EXP-050 protocol source blob: `b41b817b03aa0cc03a9d893227caa399b46d3cf8`

EXP-050 remains closed to rerun or replacement.

## 3. Frozen predecessor result facts

DEC-149 records:

- 54 predeclared budget variants;
- 28 available variants;
- 26 unavailable budget variants;
- three aggregate-selection passes;
- zero temporal-stability passes;
- all three aggregate passes in USDJPY 5m / 60m;
- all three aggregate passes with zero candidates in 2021 H1;
- 26,392 utility-eligible selection rows;
- zero accepted model challengers.

DEC-150 does not reinterpret any of those outcomes.

## 4. Frozen unchanged research identity

EXP-051 preserves the EXP-050 identity:

- symbols: EURUSD, GBPUSD, USDJPY;
- timeframes: 5m, 15m, 1h;
- horizons: 60m and 240m;
- 18 model cells;
- exact 48 model-input feature columns;
- LONG and SHORT 0.5-pip net-pip regression targets;
- outer fit period: 2015-01-01 through 2020-12-31;
- selection split: 2021-01-01 through 2022-12-31;
- validation split: 2023-01-01 through 2024-12-31;
- retrospective holdout: 2025-01-01 through 2026-08-20;
- exact three EXP-050 leave-one-regime-out fit views;
- exact frozen HGB regression configuration and preprocessing;
- six regressors per cell;
- unanimous positive-utility directional eligibility;
- candidate-budget anchors: 250, 500, 1000;
- aggregate minimum directional candidates: 250;
- exact aggregate financial gate;
- exact four half-year temporal-stability windows;
- exact 10% per-window candidate-share floor;
- positive financial signs in every stability window;
- exact validation and holdout scenarios;
- no refit after the fit stage.

Logistic regression and HGB classification remain excluded.

## 5. Unchanged EXP-050 direction eligibility

For every scored row, each of the three frozen jackknife views still:

1. predicts LONG 0.5-pip net utility;
2. predicts SHORT 0.5-pip net utility;
3. chooses a direction only when one prediction is uniquely higher than the other and that higher prediction is greater than zero.

A row remains eligible only when all three views choose the same LONG or SHORT direction.

Any disagreement, tie, or non-positive winning utility remains NO_TRADE.

No majority vote, view fallback, full-fit fallback, threshold relaxation, or alternate model family is authorized.

The predecessor raw robust utility remains:

`minimum agreed-direction raw predicted net pips across the three views`

EXP-051 retains that value as a secondary score and evidence field. It no longer uses it as the sole candidate-ranking scale.

## 6. Sole protocol change: excluded-regime out-of-fit calibration

Each jackknife view was fitted on two of the three frozen fit regimes and excluded exactly one two-year regime.

For each view and each target separately:

1. keep the already-fitted EXP-050 view regressor unchanged;
2. score exactly the rows in that view's excluded fit regime;
3. collect the finite predicted utilities;
4. sort those predictions ascending;
5. freeze the sorted prediction vector as that view/target calibration reference.

There are exactly six calibration references per cell:

- three jackknife views;
- two utility targets per view.

The calibration reference uses model predictions only.

Realized LONG/SHORT outcomes do not enter the percentile calibration.

Selection, validation, and retrospective-holdout rows do not enter calibration.

An empty calibration reference or a non-finite prediction fails closed.

## 7. Per-view calibrated utility percentile

For a scored row that has an agreed direction, each view's raw prediction for that direction is converted using the frozen reference for that same view and target.

The percentile is:

`count(reference_prediction <= raw_predicted_utility) / reference_count`

This is a deterministic right empirical CDF value in the closed interval from 0 to 1.

The reference remains fixed after the fit stage.

No selection-period quantile fit, year-specific normalization, window-specific scaling, validation calibration, holdout calibration, learned calibration model, or outcome-informed calibration is authorized.

## 8. Robust calibrated ranking score

For an EXP-050-eligible row:

`robust calibrated utility = minimum of the three agreed-direction calibrated percentiles`

The minimum is frozen to preserve the existing worst-view discipline.

The protocol therefore keeps two scores:

- robust calibrated utility: primary ranking score;
- robust raw utility: unchanged EXP-050 minimum raw predicted utility, used as the secondary ranking score.

No mean percentile, maximum percentile, weighted view score, learned view weight, or temporal-window weight is authorized.

## 9. Candidate budgets and cutoff

The candidate-budget anchors remain:

- 250
- 500
- 1000

For each cell/horizon/budget:

1. retain only rows satisfying the unchanged unanimous positive-utility eligibility rule;
2. rank by robust calibrated utility descending;
3. break calibrated-score ties by robust raw utility descending;
4. break remaining ties by row identity ascending;
5. freeze the budget-th row's `(robust calibrated utility, robust raw utility)` pair as the selection cutoff.

A row passes the frozen cutoff when:

- its robust calibrated utility is greater than the cutoff percentile; or
- its robust calibrated utility equals the cutoff percentile and its robust raw utility is greater than or equal to the cutoff raw utility.

Exact score-pair ties may exceed the nominal budget.

If fewer than the requested budget number of eligible rows exist, that budget variant remains unavailable exactly as before.

No smaller budget anchor is introduced.

## 10. Aggregate and temporal gates

Every available variant must pass the unchanged aggregate financial gate.

Only aggregate passes enter the unchanged temporal-stability screen.

All four frozen windows must still pass:

- directional candidate share at least 10%;
- positive total net pips;
- positive mean net pips;
- gross positive pips greater than absolute gross negative pips.

DEC-150 does not force candidate quotas into 2021, remove a failed window, lower the share floor, or weaken financial signs.

The stability screen remains an independent test of the new ranking rule.

## 11. Forward application

The fit-stage state frozen for forward evaluation consists of:

- the same six EXP-050 jackknife utility regressors;
- the same six excluded-regime calibration-reference vectors;
- the same unanimous positive-utility direction rule;
- the selection-derived calibrated/raw cutoff pair.

Validation must reuse all of them unchanged.

No validation refit, calibration rebuild, budget recomputation, percentile recalibration, or threshold tuning is authorized.

If validation passes, retrospective holdout uses the identical frozen regressors, calibration references, direction rule, and cutoff pair.

## 12. Why this change does not force the desired result

DEC-149 observed no candidates in 2021 H1 for all three aggregate-pass variants.

DEC-150 does not insert a year or half-year into the ranking formula, reserve a quota for 2021, rebalance the selection set by date, or tune a cutoff separately inside any stability window.

The calibration references come only from 2015-2020 excluded fit-regime predictions and are frozen before the 2021-2022 selection split is ranked.

Therefore the unchanged 2021/2022 stability windows can still reject EXP-051 completely.

A complete rejection remains an acceptable and preserved result.

## 13. Authorization state

DEC-150 keeps false:

- model-protocol result production;
- model fitting;
- historical result execution;
- feature change;
- financial-target change;
- outer chronology change;
- HGB structural configuration change;
- jackknife-view change;
- unanimous utility-consensus change;
- positive-utility requirement change;
- selection-window calibration;
- validation calibration;
- holdout calibration;
- candidate-budget change;
- minimum-candidate-count change;
- stability-screen change;
- per-window financial-gate change;
- per-window cutoff tuning;
- logistic reintroduction;
- classifier fallback;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

The only protocol-level change set true is deterministic out-of-fit utility calibration for ranking.

## 14. Frozen implementation

Protocol source:

`src/fmp/market_learning/model_successor_temporal_calibrated_utility_protocol.py`

Focused tests:

`tests/test_phase8a_exp051_temporal_calibrated_utility_protocol.py`

Protocol version:

`fmp-exp051-temporal-calibrated-utility-protocol-v1`

Protocol decision:

`DEC-150`

## 15. Next gate

A later separate decision may implement only the deterministic in-memory EXP-051 training/evaluation core against this exact protocol source.

That core may add the six excluded-regime calibration references and calibrated ranking mechanics around the frozen EXP-050 training/scoring pipeline.

It may not authorize authoritative artifact loading, historical result execution, workflow dispatch, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.
