# Phase 8A — EXP-053 Fit-Temporal Feature-Support Utility Protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY PROTOCOL / NO EXP-053 FIT
**Decision:** DEC-174
**Experiment:** EXP-20260925-053

## Purpose

DEC-174 opens EXP-053 as a narrow source-only successor to DEC-173.

DEC-173 showed that fit-period utility-support percentiles changed candidate identity but did not transfer into selection-period temporal support. EXP-053 therefore keeps the entire EXP-052 utility pipeline and adds one new fit-only signal: **feature-distribution temporal support**.

The goal is to test whether a candidate market state is recurrent across all frozen fit half-years, rather than only whether its predicted utility is high relative to fit-half-year prediction distributions.

No historical EXP-053 model fit or result execution is authorized.

## Frozen predecessor identity

DEC-174 binds:

- DEC-173 merge: `da3eb522f4178b635a261fe9ec6022d3cf94cbc8`;
- DEC-173 diagnostic blob: `af57f0eb6c00e18bb587203dc81530702e657e87`;
- DEC-172 result-decision blob: `c9983c33792a8b143989b928a9c2af0c4ecda1e5`;
- predecessor EXP-052 protocol blob: `01d5080560ec5d41653694b4df086ff2f10e770d`;
- predecessor EXP-052 evidence fingerprint: `34e397e027a069db9344d56546b654f00bd34aff73240e5bca1d55e7b3dab7eb`.

The predecessor diagnostic classification must remain:

`FIT_TEMPORAL_SUPPORT_DID_NOT_TRANSFER_TO_SELECTION_TIME_AND_TOP250_FINANCIAL_QUALITY_SLIGHTLY_DECLINED`

## What remains unchanged

EXP-053 preserves EXP-052:

- three leave-one-regime-out jackknife views;
- six HGB utility regressors per cell;
- unchanged LONG/SHORT 0.5-pip utility targets;
- positive-utility unanimous direction eligibility;
- six pooled excluded-regime calibration references;
- 24 fit-half-year utility-support references;
- robust fit-temporal utility support;
- robust pooled calibrated utility;
- robust raw utility;
- 250 / 500 / 1000 candidate budgets;
- unchanged 0.5-pip aggregate financial gate;
- four half-year selection stability windows;
- 10% minimum candidate-share floor;
- unchanged per-window financial requirements;
- unchanged variant selection chronology;
- validation then retrospective holdout;
- no-refit forward application.

No model input feature is added or removed.

## New fit-temporal feature-support references

Each jackknife view already has a fitted feature preprocessor and one excluded two-year fit regime.

That excluded regime is split into the same four frozen half-years already used by EXP-052.

For each view and excluded half-year:

1. transform the half-year's model-input feature rows through the already-fitted view preprocessor;
2. compute a finite per-dimension mean;
3. compute a population standard deviation per transformed dimension;
4. omit only dimensions whose frozen half-year standard deviation is zero from distance calculation;
5. fail closed if no active dimensions remain;
6. for each reference row, compute mean squared standardized distance from the half-year center across active dimensions;
7. require all distances finite;
8. sort the reference distances ascending;
9. freeze the center, scale, active-dimension identity, row-bound distance digest, and sorted-distance digest.

There is exactly one feature-support reference per view and half-year.

Therefore EXP-053 requires:

- 4 references per view;
- 3 views;
- **12 fit-temporal feature-support references per cell**.

These references use fit-period features only.

They use no realized outcome and no selection, validation, or holdout row.

## Scored-row feature support

For any scored row:

1. transform its model-input features through each frozen jackknife view preprocessor;
2. compute its standardized distance to each of that view's four frozen excluded-half-year feature references;
3. map distance to support by:

`count(reference_distance >= scored_row_distance) / reference_count`

Ties are included.

Smaller feature distance therefore produces higher support.

For an EXP-052-eligible row, **robust fit-temporal feature support** is the minimum support percentile across all 12 view-by-half-year comparisons.

## Ranking

Direction eligibility remains exactly EXP-052.

Selection ranks eligible rows by:

1. robust fit-temporal feature support descending;
2. EXP-052 robust fit-temporal utility support descending;
3. robust pooled calibrated utility descending;
4. robust raw utility descending;
5. row identity ascending.

This preserves all previous utility information as secondary scores while making fit-period feature recurrence the primary rank.

## Selection cutoff

For each unchanged budget anchor, the budget-th ranked row freezes a four-component cutoff:

1. robust fit-temporal feature support;
2. robust fit-temporal utility support;
3. robust pooled calibrated utility;
4. robust raw utility.

Cutoff application is lexicographic in that order.

Exact quadruple ties may exceed the nominal budget.

## Forward application

Validation and retrospective holdout reuse exactly:

- the six frozen jackknife regressors;
- six pooled utility references;
- 24 fit-half-year utility-support references;
- 12 fit-half-year feature-support references;
- unchanged direction eligibility;
- the selection-derived four-component cutoff.

Forward stages may not:

- refit models;
- rebuild any reference;
- recompute the budget;
- tune by selection/stability window;
- use selection outcomes;
- use validation outcomes;
- use holdout outcomes;
- change the cutoff.

## Fail-closed policies

EXP-053 fails closed for:

- empty feature-support reference;
- no positive-scale transformed feature dimension;
- nonfinite transformed feature values;
- nonfinite center/scale;
- nonfinite distance;
- malformed reference identities.

## Explicitly forbidden changes

DEC-174 does not authorize:

- model-feature changes;
- financial-target changes;
- chronology changes;
- HGB structural configuration changes;
- jackknife topology changes;
- unanimous-consensus changes;
- positive-utility threshold changes;
- pooled calibration changes;
- EXP-052 utility-support changes;
- selection-window calibration;
- selection-window quotas;
- validation calibration;
- holdout calibration;
- realized selection-outcome ranking;
- budget-anchor changes;
- aggregate candidate-floor changes;
- stability-screen changes;
- per-window financial-gate changes;
- per-window cutoff tuning;
- logistic-regression reintroduction;
- classifier fallback.

## Authorization state

DEC-174 keeps false:

- model-protocol result production;
- model fit;
- historical result execution;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

It authorizes only the source definition of fit-temporal feature support.

## Source identity

Protocol source:

`src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_protocol.py`

Git blob:

`11ae3fc8e68687cc04957ed9243d8c5969227fb8`

Focused tests:

`tests/test_phase8a_exp053_fit_temporal_feature_support_utility_protocol.py`

Git blob:

`42dd04bdabe791deaf0d58c42b2f5a6d5181ac30`

Protocol version:

`fmp-exp053-fit-temporal-feature-support-utility-protocol-v1`

## Next gate

The next safe gate is a deterministic in-memory EXP-053 training/evaluation core against this exact protocol source.

That core may implement the 12 feature-support references and four-part cutoff in memory only.

It must not load accepted historical artifacts or authorize authoritative fitting/result execution.
