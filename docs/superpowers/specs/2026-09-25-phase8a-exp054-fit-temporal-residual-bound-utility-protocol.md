# Phase 8A — EXP-054 Fit-Temporal Residual-Bound Utility Protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-185
**Experiment:** EXP-20260925-054

## Purpose

DEC-185 opens a source-only successor to EXP-053 after DEC-184 proves that fit-temporal feature support broadens aggregate financial passes but still does not clear the unchanged temporal-stability gate.

The residual failure classes are:

1. insufficient candidate share in one or both 2021 half-years;
2. negative financial performance in 2022 H1 for nine of ten EXP-053 aggregate-pass variants.

EXP-054 keeps EXP-053 eligibility, feature support, utility support, budgets, chronology, financial gates, and stability gates unchanged.

It adds only an out-of-fit fit-half-year residual downside bound as the new primary ranking signal.

## Frozen predecessor bindings

DEC-185 binds:

- DEC-184 merge: `f40f4b8c7d88cc2eb6c571956021ecc10b7a38a3`;
- DEC-184 diagnostic blob: `a2fce33c15422abeb8323a6e3014ebf5a3a52794`;
- DEC-183 result-decision blob: `7001c2b7944bd7b75a0c70e6fb1a775ff50ba6b5`;
- EXP-053 protocol blob: `11ae3fc8e68687cc04957ed9243d8c5969227fb8`;
- EXP-053 reviewed evidence fingerprint: `cb32abc0e4ecd3df8b639d77b6770e255aa87701eb19180dfdfb25c37dfe48e1`.

The predecessor diagnostic classification must remain:

`FEATURE_SUPPORT_BROADENED_AGGREGATE_PASSES_BUT_DID_NOT_CLEAR_TEMPORAL_STABILITY`

DEC-184 must still report zero accepted candidates and keep rerun, replacement, gate relaxation, selection-window recalibration, selection-outcome ranking, and selection-window quotas false.

## Unchanged predecessor pipeline

EXP-054 retains exactly:

- three leave-one-fit-regime-out HGB views;
- two utility regressors per view;
- six regressors per cell;
- the same model-input feature set;
- the same LONG/SHORT 0.5-pip utility targets;
- unanimous positive-utility direction eligibility;
- six pooled out-of-fit calibration references per cell;
- 24 fit-half-year utility-support references per cell;
- 12 fit-half-year feature-support references per cell;
- candidate budgets 250 / 500 / 1000;
- unchanged aggregate financial gates;
- unchanged four half-year temporal-stability windows;
- unchanged 10% per-window candidate-share floor;
- unchanged per-window financial-sign requirements;
- unchanged validation and retrospective-holdout chronology;
- no-refit forward semantics.

## Residual reference construction

For each jackknife view, each of its four excluded-regime fit half-years, and each frozen LONG/SHORT target:

1. score that excluded fit half-year with the already-fitted view regressor;
2. compute residual `realized_target - predicted_target`;
3. require all residuals finite;
4. sort residuals ascending;
5. freeze one target-specific residual reference.

Because the parent fit regime is excluded from the view's model fit, every residual reference is out-of-fit relative to its scoring model.

There are:

- 3 views;
- 4 half-years per view;
- 2 targets;

for exactly **24 residual references per cell**.

Selection, validation, and holdout rows never enter a residual reference.

## Fixed downside residual

DEC-185 uses a single frozen lower-quartile residual:

`q = 0.25`

For a sorted residual reference of size `n > 0`, the frozen downside residual is the element at zero-based index:

`floor(0.25 * (n - 1))`

There is no interpolation.

The quantile is fixed before any EXP-054 result exists and is not tuned by selection, validation, holdout, pair, timeframe, horizon, or budget.

## Robust residual-bound utility

For an already EXP-053-eligible row and its frozen unanimous LONG or SHORT direction:

1. take the chosen direction's prediction from each of the three jackknife views;
2. for that view, add each of its four frozen target-specific downside residuals;
3. produce 12 downside-adjusted lower-bound utilities;
4. take the minimum across all 12.

That minimum is:

`robust_fit_temporal_residual_bound_utility`

It may be negative.

EXP-054 does **not** add a new eligibility requirement. The score is used only to rank rows that already pass the unchanged EXP-053 unanimous positive-utility eligibility.

## Selection ranking

Eligible rows are ranked exactly by:

1. robust fit-temporal residual-bound utility descending;
2. robust fit-temporal feature support descending;
3. robust fit-temporal utility support descending;
4. robust pooled calibrated utility descending;
5. robust raw utility descending;
6. row identity ascending.

This is intended to prefer rows whose predicted utility remains conservative after applying the worst out-of-fit fit-half-year downside residual bound.

It does not use selection outcomes.

## Five-part cutoff

For every unchanged candidate budget, freeze the budget-th row's exact quintuple:

- residual-bound utility;
- feature support;
- fit-temporal utility support;
- pooled calibrated utility;
- raw utility.

Forward rows pass this quintuple lexicographically in the same order.

Exact quintuple ties may exceed the nominal budget.

Unavailable budgets keep all five cutoff components null.

## Forward chronology

If no stable selection exists:

- validation remains `LOCKED_NO_SELECTION`;
- retrospective holdout remains `LOCKED_NO_SELECTION`.

If a stable variant exists, validation and holdout reuse unchanged:

- the exact six fitted regressors;
- the exact six pooled utility references;
- the exact 24 utility-support references;
- the exact 12 feature-support references;
- the exact 24 residual references;
- the exact selection-derived five-part cutoff.

No fit, reference, budget, quantile, or cutoff may be rebuilt downstream.

## Leakage and tuning prohibitions

EXP-054 forbids:

- realized selection outcomes in ranking;
- realized validation outcomes in ranking;
- realized holdout outcomes in ranking;
- selection-window residual references;
- validation-window residual references;
- holdout-window residual references;
- selection-window calibration;
- selection-window quotas;
- per-window cutoff tuning;
- pair/timeframe/horizon-specific residual quantiles;
- budget-specific residual quantiles;
- stability-share relaxation;
- stability-financial relaxation;
- removal of early stability windows.

## Authorization state

DEC-185 opens only the residual-bound protocol source definition.

It keeps false:

- model protocol result production;
- model fitting;
- historical result execution;
- feature changes;
- target changes;
- HGB configuration changes;
- jackknife changes;
- consensus changes;
- positive-utility eligibility changes;
- pooled calibration changes;
- utility-support changes;
- feature-support changes;
- selection-window calibration;
- selection-window quotas;
- validation/holdout recalibration;
- density-anchor changes;
- minimum candidate-count changes;
- stability-screen changes;
- per-window financial-gate changes;
- logistic/classifier fallback;
- promotion;
- shadow/demo execution;
- broker mutation;
- live orders;
- real-money action;
- trading authorization.

## Source identity

Protocol source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_bound_utility_protocol.py`

Git blob:

`3ffac844f9ed5308512dc3313e850cc84fb6d144`

Focused tests:

`tests/test_phase8a_exp054_fit_temporal_residual_bound_utility_protocol.py`

Git blob:

`9216230ca6e3c05ab352acd4ebd87f1354ab9f70`

Protocol version:

`fmp-exp054-fit-temporal-residual-bound-utility-protocol-v1`

## Evidence status

EXP-054 is explicitly prior-result-informed retrospective research.

It is not untouched out-of-sample evidence.

No historical EXP-054 result exists under DEC-185.

## Next gate

A later separate decision may implement the deterministic in-memory EXP-054 training/evaluation core against this exact protocol.

That implementation must remain source-only and non-executable before any artifact/evidence contract, readiness path, workflow, run authorization, or historical result production is considered.
