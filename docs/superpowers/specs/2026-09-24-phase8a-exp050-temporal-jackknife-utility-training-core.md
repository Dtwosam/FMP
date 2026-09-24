# Phase 8A — EXP-050 Temporal-Jackknife Utility Training Core

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NO AUTHORITATIVE EXP-050 FIT
**Decision:** DEC-142
**Experiment:** EXP-20260924-050

## 1. Purpose

DEC-142 implements the deterministic in-memory training and evaluation core for the DEC-141 temporal-jackknife utility protocol.

This source makes the frozen EXP-050 protocol machine-checkable without creating an authoritative historical result.

No artifact-backed runner, workflow, dispatch path, historical execution, promotion, broker mutation, order path, or trading authorization is added.

## 2. Exact source binding

The training core binds:

- DEC-141 merged commit: `4729da0e769f76f44b97ff6349ee25c5b7c0f5c7`
- DEC-141 protocol blob: `b41b817b03aa0cc03a9d893227caa399b46d3cf8`
- predecessor EXP-049 training-core blob: `e1018b20210b7bb8d666071d8eb878aba5899111`

The predecessor training core itself fail-closed validates its frozen protocol/base/density dependencies. DEC-142 therefore reuses only already-frozen utility scoring, cutoff, financial, and temporal-stability helpers through an exact predecessor-core Git-blob binding.

Source validation fails closed on any mismatch.

## 3. Jackknife fit-view construction

The existing three predecessor fit-regime frames remain:

- `fit_2015_2016`
- `fit_2017_2018`
- `fit_2019_2020`

The core builds exactly three DEC-141 views:

- `leave_out_fit_2015_2016` = 2017-2018 + 2019-2020
- `leave_out_fit_2017_2018` = 2015-2016 + 2019-2020
- `leave_out_fit_2019_2020` = 2015-2016 + 2017-2018

Each view requires exactly two included regimes and exactly one excluded regime.

The concatenated view row count must equal the sum of its two source-regime row counts.

No missing regime, duplicate view, inclusion of the excluded regime, or altered view inventory is accepted.

## 4. Regression fit

For every pair/timeframe/horizon cell and every jackknife view, the core fits exactly two regressors:

- `long_net_pips_0p5`
- `short_net_pips_0p5`

That remains six HGB regressors per cell.

Each regressor uses the exact predecessor fitting helper, which preserves:

- finite-target validation;
- median imputation fitted only on the supplied fit rows;
- no standardization;
- the exact frozen HistGradientBoostingRegressor configuration;
- deterministic preprocessor and estimator fingerprints.

Because the supplied fit frame is the exact jackknife view union, the excluded two-year regime cannot contribute rows or preprocessing state.

## 5. Reused predecessor machinery

DEC-142 deliberately reuses the exact predecessor helpers for:

- positive unanimous utility direction;
- least-optimistic robust utility;
- row-bound prediction and consensus digests;
- 250/500/1000 robust-utility cutoffs;
- cutoff tie expansion;
- candidate-direction application;
- realized financial metrics;
- aggregate financial gate;
- four-window temporal-stability evaluation;
- selection tie-break.

This is source reuse under exact blob binding, not inheritance by convention.

The research change remains limited to the fit-view topology.

## 6. View-aware scoring

Every scored split is transformed separately by each frozen view/target model.

For each view and target:

- exactly one prediction is required per row;
- every prediction must be finite;
- row identity must match across all six scored regressors;
- a deterministic prediction digest is recorded.

View prediction digests are recorded by jackknife-view name.

## 7. Positive unanimous utility consensus

The same rule remains:

- a view votes LONG only when predicted LONG utility is uniquely greater than SHORT and greater than zero;
- a view votes SHORT only when predicted SHORT utility is uniquely greater than LONG and greater than zero;
- otherwise it votes NO_TRADE;
- all three views must vote the same directional class.

Robust utility remains the minimum agreed-direction prediction across the three views.

Any disagreement or NO_TRADE vote makes the row ineligible.

No majority voting, view weighting, or threshold relaxation exists in the core.

## 8. Selection cutoffs

For each budget 250, 500, and 1000:

- rank eligible selection rows by robust utility descending;
- row identity ascending provides deterministic tie order;
- use the budget-th robust utility as the frozen cutoff;
- include all eligible rows at or above the cutoff.

A budget remains unavailable when fewer than the requested number of eligible rows exist.

Non-finite or non-positive directional robust utility fails closed.

## 9. Aggregate and temporal-stability gates

The exact predecessor 0.5-pip aggregate financial gate is reused.

Only aggregate passes enter temporal stability.

The exact predecessor four half-year stability windows and requirements are reused:

- candidate share at least 10% of the full-selection directional count;
- positive total net pips;
- positive mean net pips;
- gross positive pips greater than absolute gross negative pips.

No window-specific cutoff or utility recalibration is introduced.

## 10. Selection tie-break

Among variants passing aggregate and temporal stability, the existing material ordering is reused:

1. higher realized selection total net pips;
2. higher directional candidate count;
3. smaller candidate-budget anchor.

## 11. Validation and retrospective holdout

If no variant passes selection, validation remains locked.

If a variant is selected:

- all six view regressors remain frozen;
- all three view definitions remain frozen;
- direction, unanimity, and robust-utility rules remain frozen;
- the exact numeric selection-derived cutoff is reused.

Validation applies the existing gate and diagnostic scenarios with no refit.

Retrospective holdout remains locked unless validation passes and, if reached, uses the exact same frozen view/model/cutoff identity.

## 12. Result evidence shape

The in-memory cell result records:

- experiment/protocol/training-core identity;
- DEC-141 merge and protocol blob;
- predecessor training-core blob/decision;
- data manifest identity;
- split row counts;
- three jackknife-view definitions;
- six fit records and fingerprints;
- view-specific prediction digests;
- selection consensus diagnostics/digest;
- all budget variants;
- aggregate and temporal-stability evidence;
- selected variant, if any;
- validation evidence, if unlocked;
- holdout evidence, if unlocked;
- deterministic result fingerprint;
- every execution/promotion/trading lock false.

If no variant survives the frozen selection gates, the selection status is:

`NO_TEMPORAL_JACKKNIFE_UTILITY_STABLE_MODEL_CHALLENGER`

## 13. Source identity

Training core:

`src/fmp/market_learning/model_successor_temporal_jackknife_utility_training.py`

Training core Git blob:

`ec97a9941af052d6e223e4bafab9a9989ec57ff0`

Focused tests:

`tests/test_phase8a_exp050_temporal_jackknife_utility_training.py`

Focused test Git blob:

`f7066a775659b1b391b0e29af13601cff015ebb5`

Training-core version:

`fmp-exp050-temporal-jackknife-utility-training-core-v1`

Training-core decision:

`DEC-142`

## 14. Authorization state

DEC-142 keeps false:

- authoritative EXP-050 result execution;
- authoritative model fitting;
- historical workflow execution;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

The presence of `estimator.fit` through the frozen predecessor helper inside this deterministic research core is not authorization to run the accepted historical artifact set.

## 15. Next gate

A later separate decision may freeze an EXP-050 artifact-backed runner/evidence contract that loads only already accepted historical feature/outcome/readiness artifacts and calls this exact training core across all 18 cells.

That later layer must bind this training-core Git blob before any workflow or historical result authorization is considered.
