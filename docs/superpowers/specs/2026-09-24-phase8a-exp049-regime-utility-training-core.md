# Phase 8A — EXP-049 Regime-Utility Training Core

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NO AUTHORITATIVE EXP-049 FIT
**Decision:** DEC-133
**Experiment:** EXP-20260924-049

## 1. Purpose

DEC-133 implements the deterministic in-memory training and evaluation core for the DEC-132 regime-utility protocol.

This source makes the frozen protocol machine-checkable without creating an authoritative historical model result.

No workflow, dispatch path, artifact-backed historical run, broker mutation, order path, promotion, or trading authorization is added.

## 2. Exact source binding

The training core binds:

- DEC-132 merged commit: d17326eebf6b456211225d7bad3a182a0307b707
- DEC-132 protocol blob: ad2fcb22656fc7a1490f4cdf87fb25c62895a1ac
- frozen base EXP-044 training helper blob: 34b50a3f907d26b1c5ec50a0a0b444a3417d04f7
- frozen density/stability helper blob: 8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945

Source validation fails closed on any mismatch.

## 3. Fit-regime construction

The core reconstructs exactly the three DEC-132 fit regimes:

- fit_2015_2016
- fit_2017_2018
- fit_2019_2020

The outer chronological split implementation remains the existing leakage-safe EXP-044 split helper.

Entry and exit timestamps must both remain inside their assigned split.

## 4. Regression fit

For every pair/timeframe/horizon cell and every fit regime, the core fits exactly two HistGradientBoostingRegressor models:

- long_net_pips_0p5
- short_net_pips_0p5

Each target is checked for finite values.

Each regressor receives its own fit-regime-only median preprocessor state.

The exact DEC-132 HGB regression configuration is used.

No classifier, logistic model, full-fit fallback, model weighting, or parameter search is present.

## 5. Deterministic fit evidence

For every regressor the core records:

- target row count;
- minimum target net pips;
- maximum target net pips;
- mean target net pips;
- positive, negative, and zero target counts;
- preprocessor fingerprint;
- model fingerprint.

The source therefore exposes enough deterministic evidence for a later artifact layer to verify six exact fit objects per cell without changing the model-selection rule.

## 6. Scoring

Every scored split is transformed only by the preprocessor fitted with its matching regime/target model.

Predictions must:

- have exactly one value per row;
- be finite;
- preserve exact row identity.

Each target prediction vector receives a deterministic row-bound digest.

## 7. Per-regime utility vote

For each regime and scored row:

- LONG votes only when predicted LONG utility is uniquely greater than predicted SHORT utility and greater than zero;
- SHORT votes only when predicted SHORT utility is uniquely greater than predicted LONG utility and greater than zero;
- ties and non-positive best predictions vote NO_TRADE.

The core does not use realized selection outcomes to determine this vote.

## 8. Three-regime consensus

A row is eligible only when all three regimes produce the same LONG or SHORT vote.

Robust utility is the minimum predicted utility for that agreed direction across the three regimes.

Any disagreement or NO_TRADE vote makes the row ineligible.

The consensus direction and robust utility are bound to row identity in a deterministic digest.

## 9. Selection cutoff

For each frozen budget 250, 500, and 1000:

- rank eligible selection rows by robust utility descending;
- use row identity ascending as the deterministic tie order;
- freeze the budget-th robust utility as the numeric selection cutoff;
- include all eligible rows at or above the cutoff.

Ties may expand candidate count.

A budget is unavailable when fewer than the budget number of eligible rows exist.

Any directional robust utility that is non-finite or non-positive fails closed.

## 10. Aggregate gate

The selected candidates are evaluated with the existing realized financial metric helper.

The unchanged 0.5-pip aggregate gate remains:

- at least 250 directional candidates;
- positive total net pips;
- positive mean net pips;
- gross positive pips greater than absolute gross negative pips.

Only aggregate passes enter temporal stability.

## 11. Temporal stability

The existing four half-year windows and existing stability helper are reused.

The core preserves:

- 10% minimum candidate share in every window;
- positive total net pips in every window;
- positive mean net pips in every window;
- gross positive pips greater than absolute gross negative pips in every window;
- all four windows must pass.

No window-specific cutoff or utility recalibration is added.

## 12. Selection tie-break

Among variants that pass aggregate and temporal stability:

1. higher realized selection total net pips;
2. higher directional candidate count;
3. smaller candidate-budget anchor.

This exactly implements the DEC-132 material ordering.

## 13. Validation

If no selection variant passes, validation is locked.

If a variant is selected:

- the six fitted regressors remain unchanged;
- the regime vote rule remains unchanged;
- the three-regime consensus remains unchanged;
- the robust utility score remains unchanged;
- the exact numeric selection-derived cutoff is applied unchanged.

Validation evaluates the frozen 0.5 and 1.0-pip gate scenarios plus the 0.2-pip diagnostic scenario.

No refit or threshold recomputation occurs.

## 14. Retrospective holdout

Retrospective holdout remains locked unless validation passes.

If validation passes, the same six fitted regressors and the same exact selection-derived cutoff are applied to holdout.

The evidence remains retrospective/already seen and prior-result-informed.

## 15. Result identity

The in-memory cell result records:

- experiment/protocol/training-core identity;
- bound source blobs and DEC-132 merge;
- data manifest identity;
- split row counts;
- all six fit fingerprints;
- selection consensus diagnostics/digest;
- all budget variants;
- aggregate and temporal-stability evidence;
- selected variant, if any;
- validation evidence, if unlocked;
- holdout evidence, if unlocked;
- deterministic result fingerprint;
- every promotion/execution lock false.

## 16. Source identity

Training core:

src/fmp/market_learning/model_successor_regime_utility_training.py

Training core Git blob:

e1018b20210b7bb8d666071d8eb878aba5899111

Focused tests:

tests/test_phase8a_exp049_regime_utility_training.py

Focused test Git blob:

0606d8208b8c7edac40f1073e5b5e8248dfc107b

Training-core version:

fmp-exp049-regime-utility-training-core-v1

Training-core decision:

DEC-133

## 17. Authorization state

DEC-133 keeps false:

- authoritative EXP-049 result execution;
- authoritative model fitting;
- historical workflow execution;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

The presence of estimator.fit inside a deterministic in-memory research core is not an authorization to run the accepted historical artifact set.

## 18. Next gate

A later separate decision may freeze an artifact-backed EXP-049 runner/evidence contract that loads only the already accepted feature/outcome/readiness artifacts and calls this exact training core across all 18 cells.

That later layer must bind this training-core Git blob before any workflow or historical result authorization is considered.
