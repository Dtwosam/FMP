# Phase 8A — EXP-053 Fit-Temporal Feature-Support Utility Training Core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / IN-MEMORY CORE / NON-EXECUTABLE
**Decision:** DEC-175
**Experiment:** EXP-20260925-053

## 1. Purpose

DEC-175 implements the deterministic in-memory training/evaluation core for EXP-053 against the exact DEC-174 protocol.

The core reuses the complete EXP-052 utility pipeline and adds only the frozen fit-temporal feature-support layer plus the four-part selection cutoff.

This decision does not authorize accepted historical artifact loading, authoritative fitting, authoritative result execution, promotion, or trading.

## 2. Frozen source bindings

DEC-175 binds:

- DEC-174 merge: `9687eb8ea3920e87d6681adf7366a3ce0bba7154`
- DEC-174 protocol blob: `11ae3fc8e68687cc04957ed9243d8c5969227fb8`
- predecessor EXP-052 training-core blob: `fe5664438752a161134bbed6f55d9985f1c1470a`
- predecessor training-core decision: `DEC-164`

The predecessor source-level fit and result-execution locks must remain false.

Any bound-byte drift fails closed.

## 3. Unchanged model fit

Every cell retains exactly:

- three leave-one-fit-regime-out views;
- two HGB utility regressors per view;
- six regressors per cell;
- the same model-input feature set;
- the same HGB structural configuration;
- the same LONG/SHORT 0.5-pip utility targets;
- the same six pooled excluded-regime calibration references;
- the same 24 fit-half-year utility-support references.

No classifier, logistic fallback, full-fit model, view weighting, or view fallback is introduced.

## 4. Feature-support references

For each jackknife view, DEC-175 identifies the one excluded fit regime and its four frozen half-year windows.

For each view-by-half-year reference:

1. reuse the already-fitted view preprocessor;
2. transform only that half-year's fit rows using the frozen model-input columns;
3. require all transformed values finite;
4. compute a per-dimension population mean and population standard deviation;
5. mark active dimensions where frozen scale is strictly positive;
6. fail closed if no active dimensions remain;
7. compute each reference row's mean squared standardized distance over active dimensions;
8. sort all finite reference distances ascending.

Exactly four feature-support references are created per view and 12 per cell.

No realized outcome and no selection, validation, or holdout row enters a feature-support reference.

## 5. Feature-reference evidence

Each frozen feature reference records:

- exact half-year name, parent regime, start, and end-exclusive;
- positive row count;
- transformed dimension count;
- active dimension count;
- reused preprocessor fingerprint;
- center digest;
- scale digest;
- active-dimension-mask digest;
- minimum, maximum, and mean reference distance;
- sorted reference-distance digest.

The fit block records exactly 12 feature-support references per cell.

## 6. Scored-row feature support

Each scored row is transformed through each frozen view preprocessor.

For every one of the 12 view-by-half-year references, the row receives a distance using the reference's frozen center, scale, and active dimensions.

Feature support is the right-tail empirical percentile:

`count(reference_distance >= row_distance) / reference_count`

Ties are included.

Robust fit-temporal feature support is the minimum across all 12 references.

Values must remain finite and within `[0, 1]`.

## 7. Unchanged EXP-052 eligibility and utility scores

DEC-175 first computes the exact EXP-052 consensus:

- unanimous positive-utility direction;
- robust raw utility;
- robust pooled calibrated utility;
- robust fit-temporal utility support.

The EXP-053 feature-support score does not change direction eligibility.

Feature support is an additional ranking signal only after the row is already EXP-052 eligible.

## 8. Selection ranking

Eligible rows are ranked exactly by:

1. robust fit-temporal feature support descending;
2. robust fit-temporal utility support descending;
3. robust pooled calibrated utility descending;
4. robust raw utility descending;
5. row identity ascending.

Candidate-budget anchors remain exactly:

- 250;
- 500;
- 1000.

## 9. Four-part cutoff

For every available budget, DEC-175 freezes the budget-th row's exact quadruple:

- feature-support cutoff;
- fit-temporal utility-support cutoff;
- pooled calibrated-utility cutoff;
- raw-utility cutoff.

A scored row passes lexicographically:

- feature support above cutoff passes;
- if equal, utility support above cutoff passes;
- if equal again, pooled calibrated utility above cutoff passes;
- if all three are equal, raw utility greater than or equal to the raw cutoff passes.

Exact quadruple ties may exceed the nominal budget.

Unavailable budgets keep all four cutoff values null.

## 10. Financial and stability evaluation

The financial scenario engine is unchanged.

Selection uses the same 0.5-pip aggregate financial gate.

Only aggregate financial passes unlock the same four half-year temporal-stability windows.

The same requirements remain:

- minimum 10% candidate share per window;
- positive total net pips;
- positive mean net pips;
- gross positive pips greater than absolute gross negative pips;
- all four windows must pass.

No window quota, per-window cutoff tuning, gate relaxation, or window removal is introduced.

## 11. Forward chronology

If no stable selection exists:

- validation remains `LOCKED_NO_SELECTION`;
- retrospective holdout remains `LOCKED_NO_SELECTION`.

If a stable variant exists, validation and then holdout reuse unchanged:

- the exact six fitted regressors;
- the exact six pooled utility references;
- the exact 24 utility-support references;
- the exact 12 feature-support references;
- the exact selection-derived four-part cutoff;
- no refit or rebuilt reference.

Validation/holdout diagnostics may score rows, but cannot change ranking or cutoffs.

## 12. Determinism and fingerprints

The core records deterministic digests for feature-reference arrays and feature-support consensus rows.

Every cell result receives a canonical result fingerprint over the complete result record before the fingerprint field is added.

The core performs no filesystem artifact discovery and no authoritative historical source loading.

## 13. Source identity

Training core:

`src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_training.py`

Git blob:

`4fd0e48302f97e188a8124e1543bde0ffdb43b6f`

Focused tests:

`tests/test_phase8a_exp053_fit_temporal_feature_support_utility_training.py`

Git blob:

`a9b888311a8bbbb239243cf24418d3056df28524`

Training-core version:

`fmp-exp053-fit-temporal-feature-support-utility-training-core-v1`

Decision:

`DEC-175`

## 14. Authorization state

DEC-175 keeps false:

- authoritative historical result execution;
- authoritative model fit;
- workflow dispatch;
- replacement run;
- promotion;
- prospective shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 15. Next gate

A later separate decision may freeze the EXP-053 artifact/evidence contract against this exact DEC-175 core.

That contract must independently validate all 18 cells, 108 regressors, 108 pooled references, 432 utility-support references, **216 feature-support references** (12 per cell across 18 cells), plus the four-part cutoff and unchanged forward-status chain.

It must remain non-executable before readiness or accepted historical artifact loading.
