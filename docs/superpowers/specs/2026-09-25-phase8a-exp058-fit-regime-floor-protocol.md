# Phase 8A — EXP-058 Fit-Temporal Residual Regime-Floor Utility Protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-231
**Experiment:** EXP-20260925-058

## Purpose

DEC-231 opens a new source-only successor after DEC-230 shows that EXP-057 lower-tail ranking changes aggregate candidate identity and financial mix but still does not create selection-time temporal stability.

EXP-058 targets that remaining failure mode using only already-frozen fit-period evidence. It introduces one derived ranking score that rewards consistency across the three frozen fit eras without using selection-window outcomes, quotas, or relaxed temporal gates.

## Frozen predecessor bindings

DEC-231 binds:

- DEC-230 merge: `b3877047fabc779b7fcc88dde847c02b5a6f5b98`
- DEC-230 diagnostic blob: `09e88b85a51b858296a3af7d146251606f1d5533`
- DEC-229 result-decision blob: `185e2cdf089cb6f1a12619af58fd32860366498f`
- EXP-057 protocol blob: `2f355526476a4d41967bb46e1bfad6aa525cbfa9`
- EXP-057 evidence fingerprint: `4bf67108e0df38d4f213d08898fadd338285ac7a2ce56920b61e4dba0f3eec4c`

The predecessor result has zero stable selection passes and zero accepted model candidates.

## Existing residual-bound structure

EXP-058 reuses the exact twelve downside-adjusted lower-bound utilities already available for every EXP-057-eligible row and agreed LONG/SHORT direction.

They arise from:

- three frozen temporal jackknife views;
- each view excluding exactly one of the three frozen two-year fit regimes;
- four frozen half-year residual references within that excluded regime.

Thus each eligible row has exactly four bounds for each of the three frozen fit eras:

- 2015-2016;
- 2017-2018;
- 2019-2020.

No new residual reference vector is created.

## New fit-regime-floor score

For each eligible row:

1. Within each jackknife view, combine that view's row prediction with its four frozen downside residual references.
2. Take the arithmetic mean of the four resulting lower bounds. This is the row's lower-bound mean for the two-year fit regime excluded by that view.
3. Repeat for all three views, producing exactly three fit-regime means.
4. Define `fit_temporal_residual_regime_floor_utility` as the minimum of those three means.

This score therefore measures the weakest average downside-adjusted utility across the three frozen fit eras.

The grouping is by the actual excluded two-year fit regime. EXP-058 does not align half-year slots across regimes by season and does not create a new chronology.

## Ranking and cutoff

EXP-058 keeps EXP-057 eligibility unchanged.

Eligible rows rank lexicographically by:

1. fit-temporal residual regime-floor utility descending;
2. fit-temporal residual lower-tail mean descending;
3. fit-temporal residual breadth descending;
4. robust fit-temporal residual-bound utility descending;
5. robust fit-temporal feature support descending;
6. robust fit-temporal utility support descending;
7. robust pooled calibrated utility descending;
8. robust raw utility descending;
9. row identity ascending.

For each unchanged budget anchor 250, 500, and 1000, the budget-th ranked row freezes the first eight numeric components as the selection cutoff.

Exact eight-part ties may exceed the nominal budget.

## Forward application

Validation and retrospective holdout reuse unchanged:

- six frozen jackknife regressors;
- six pooled calibration references;
- 24 fit-temporal utility-support references;
- 12 feature-support references;
- 24 residual references;
- the same twelve row lower bounds;
- the derived three fit-regime means;
- the selection-derived eight-part cutoff.

There is no refit, recalibration, reference rebuild, budget recomputation, per-window tuning, or use of selection/validation/holdout outcomes to alter ranking.

## Unchanged protocol

DEC-231 does not change:

- features;
- financial targets;
- outer chronology;
- HGB structural configuration;
- jackknife views;
- unanimous positive-utility eligibility;
- pooled calibration;
- fit-temporal utility support;
- feature support;
- residual references;
- residual-bound utility;
- residual breadth;
- lower-tail mean;
- candidate budgets;
- aggregate financial gates;
- four temporal-stability windows;
- 10% minimum directional candidate share per window;
- per-window financial gates;
- validation chronology;
- retrospective holdout chronology;
- no-refit semantics.

## Prohibited information leakage

The new score uses only frozen fit-period residual references and frozen fit predictions.

DEC-231 forbids:

- selection-window outcomes in ranking;
- selection-window recalibration;
- selection-window quotas;
- validation or holdout outcomes in ranking;
- relaxing temporal-stability share or financial gates;
- removing early temporal windows;
- tuning cutoffs by selection window.

## Authorization state

DEC-231 authorizes only the new fit-temporal residual regime-floor protocol source.

It keeps false:

- model-protocol result production;
- model fit;
- historical result execution;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Source identity

Protocol source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_protocol.py`

Git blob:

`8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2`

Focused tests:

`tests/test_phase8a_exp058_fit_regime_floor_protocol.py`

Git blob:

`ddd14530237faa164202362bf24886c7c03cba0a`

## Next gate

After DEC-231 is green and merged, the next safe gate is a deterministic in-memory EXP-058 training/evaluation core implementing exactly this one derived score and eight-part cutoff.

Artifact loading, workflow dispatch, historical result execution, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain out of scope.
