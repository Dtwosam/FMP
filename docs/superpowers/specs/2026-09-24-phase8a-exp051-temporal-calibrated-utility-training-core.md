# Phase 8A — EXP-051 Temporal-Calibrated Utility Training Core

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NO AUTHORITATIVE EXP-051 FIT
**Decision:** DEC-151
**Experiment:** EXP-20260924-051

## 1. Purpose

DEC-151 implements the deterministic in-memory training and evaluation core for the DEC-150 out-of-fit calibrated-utility protocol.

The source makes the frozen EXP-051 mechanics machine-checkable while keeping the accepted historical artifact set outside this layer.

No artifact-backed runner, workflow, dispatch path, historical result execution, promotion, shadow/demo execution, broker mutation, order path, real-money action, or trading authorization is added.

## 2. Exact source binding

The training core binds:

- DEC-150 merged commit: `b80a1f688afe8f5056aa31c1a2ff5b4ebbc11833`
- DEC-150 protocol blob: `c39309c4115cae1ea058e56f30cae4af6407e36e`
- predecessor EXP-050 training-core blob: `ec97a9941af052d6e223e4bafab9a9989ec57ff0`

The predecessor core independently validates its own DEC-141 protocol and frozen EXP-049 helper dependencies.

DEC-151 source validation fails closed if either direct dependency changes.

## 3. Unchanged jackknife fitting

The core preserves the exact EXP-050 fitting topology.

The fit period remains split into:

- `fit_2015_2016`
- `fit_2017_2018`
- `fit_2019_2020`

The exact three leave-one-regime-out views remain:

- `leave_out_fit_2015_2016` = 2017-2018 + 2019-2020
- `leave_out_fit_2017_2018` = 2015-2016 + 2019-2020
- `leave_out_fit_2019_2020` = 2015-2016 + 2017-2018

For every cell and view, the same two HGB regressors are fitted:

- `long_net_pips_0p5`
- `short_net_pips_0p5`

There remain exactly six regressors per cell.

The implementation reuses the exact EXP-050/predecessor fit and scoring helpers through the frozen training-core binding.

## 4. Excluded-regime calibration references

After fitting each view, the core identifies the exact two-year fit regime excluded from that view.

For each view and target:

1. score every row of the excluded regime using the already-fitted view regressor;
2. require a finite prediction for every row;
3. sort the prediction vector ascending;
4. freeze the sorted vector as the calibration reference.

The result is exactly six calibration references per cell.

The reference evidence records:

- view name;
- included regimes;
- excluded regime;
- row count;
- target identity;
- minimum prediction;
- maximum prediction;
- mean prediction;
- row-bound prediction digest;
- sorted-reference digest.

No realized target values enter the calibration calculation.

No selection, validation, or holdout row enters the calibration reference.

## 5. Deterministic empirical percentile

For any raw predicted utility, the core computes:

`count(reference_prediction <= raw_predicted_utility) / reference_count`

The implementation uses the right empirical CDF.

Calibration fails closed if:

- the reference is empty;
- a reference prediction is non-finite;
- the reference is not sorted;
- a scored prediction is non-finite.

The output percentile must remain in the closed interval from 0 to 1.

## 6. Unchanged direction eligibility

The exact EXP-050 direction rule is reused.

For each row:

- every view predicts LONG and SHORT raw 0.5-pip utility;
- a view chooses LONG only when LONG is uniquely higher than SHORT and greater than zero;
- a view chooses SHORT only when SHORT is uniquely higher than LONG and greater than zero;
- otherwise that view is NO_TRADE;
- all three views must choose the same directional class.

Any disagreement or non-positive winner makes the row ineligible.

The raw robust utility remains the minimum agreed-direction raw prediction across the three views.

## 7. Robust calibrated utility

For an eligible row, each view's agreed-direction raw prediction is converted to the empirical percentile of that view/target's frozen excluded-regime reference.

The robust calibrated utility is:

`minimum calibrated percentile across the three views`

The core retains both:

- robust calibrated utility;
- robust raw utility.

The calibrated score is primary for ranking.

The raw score is secondary.

No view mean, maximum, majority vote, learned weighting, window weighting, or selection-period normalization exists.

## 8. Calibrated/raw cutoff pair

For each unchanged budget anchor 250/500/1000, eligible selection rows are ranked by:

1. robust calibrated utility descending;
2. robust raw utility descending;
3. row identity ascending.

The budget-th row freezes:

- `selection_derived_calibrated_cutoff`
- `selection_derived_raw_cutoff`

A row passes the pair when:

- calibrated utility is above the calibrated cutoff; or
- calibrated utility equals the calibrated cutoff and raw utility is at least the raw cutoff.

Exact calibrated/raw score-pair ties may exceed the nominal budget.

A budget remains unavailable when fewer than the requested number of EXP-050-eligible rows exist.

## 9. Financial evaluation

The calibrated cutoff only changes which already-eligible rows become candidates.

Realized financial evaluation continues to use the frozen base financial machinery.

For each requested cost scenario, the core records:

- candidate count;
- total net pips;
- mean net pips;
- gross positive pips;
- gross negative pips;
- unchanged financial-gate result.

No outcome value enters model fitting or calibration.

## 10. Temporal stability

Only aggregate financial passes enter the stability screen.

The core reuses the exact four frozen half-year windows and the exact window gate.

For each window it applies the same calibrated/raw cutoff pair and computes realized candidate metrics.

Every window must still satisfy:

- candidate share at least 10% of full-selection candidate count;
- positive total net pips;
- positive mean net pips;
- gross positive pips greater than absolute gross negative pips.

No per-window cutoff, quota, calibration rebuild, or gate relaxation is implemented.

## 11. Selection tie-break

Among variants passing aggregate financial and temporal stability, the unchanged material selection ordering is reused:

1. higher 0.5-pip selection total net pips;
2. higher directional candidate count;
3. smaller candidate-budget anchor.

Calibration score is not added as a post-gate performance tie-break.

## 12. Validation and retrospective holdout

If no variant survives selection, validation remains locked.

If a variant is selected, validation reuses:

- the same six fitted regressors;
- the same six calibration-reference vectors;
- the same unanimous positive-utility rule;
- the same calibrated-score rule;
- the exact calibrated/raw cutoff pair frozen on selection.

Validation performs no refit and no recalibration.

Retrospective holdout remains locked unless validation passes.

If reached, holdout uses the identical frozen models, references, and cutoff pair.

## 13. In-memory result evidence

The cell result records:

- experiment/protocol/training-core identity;
- DEC-150 merge and protocol blob;
- predecessor training-core blob;
- processed data manifest identity;
- split row counts;
- six model fit fingerprints;
- six out-of-fit calibration-reference records;
- selection prediction and calibrated-consensus diagnostics;
- calibrated-consensus digest;
- every budget variant;
- aggregate and temporal-stability evidence;
- selected variant, if any;
- validation evidence, if unlocked;
- holdout evidence, if unlocked;
- deterministic result fingerprint;
- all execution/promotion/trading locks false.

If no variant survives, the selection status is:

`NO_TEMPORAL_CALIBRATED_UTILITY_STABLE_MODEL_CHALLENGER`

## 14. Source identity

Training core:

`src/fmp/market_learning/model_successor_temporal_calibrated_utility_training.py`

Focused tests:

`tests/test_phase8a_exp051_temporal_calibrated_utility_training.py`

Training-core version:

`fmp-exp051-temporal-calibrated-utility-training-core-v1`

Training-core decision:

`DEC-151`

## 15. Authorization state

DEC-151 keeps false:

- authoritative EXP-051 result execution;
- authoritative model fitting;
- historical workflow execution;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

The in-memory core can fit caller-supplied frames for deterministic research testing, exactly like predecessor source-only cores. That does not authorize loading or fitting the accepted historical artifact set.

## 16. Next gate

A later separate decision may freeze an EXP-051 artifact-backed runner/evidence contract that loads only the already accepted historical feature/outcome/readiness artifacts and calls this exact training core across all 18 cells.

That later layer must bind the DEC-151 training-core Git blob and remain non-executable until a separate workflow/source gate and later authorization chain are frozen.
