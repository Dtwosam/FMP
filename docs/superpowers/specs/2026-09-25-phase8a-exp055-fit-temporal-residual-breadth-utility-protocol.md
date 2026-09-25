# Phase 8A — EXP-055 Fit-Temporal Residual-Breadth Utility Protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-198
**Experiment:** EXP-20260925-055

## Purpose

DEC-198 opens a source-only successor to EXP-054 after DEC-197 shows that residual-bound ranking improved some downside windows and restored two aggregate passes but still did not create selection-period temporal breadth.

EXP-055 keeps EXP-054 eligibility, residual references, residual downside quantile, feature support, utility support, pooled calibration, budgets, chronology, financial gates, stability gates, validation/holdout chronology, and no-refit semantics unchanged.

It adds only a fit-period residual-breadth ranking score derived from the exact twelve EXP-054 downside-adjusted lower-bound utilities already available for each eligible row.

## Frozen predecessor bindings

DEC-198 binds:

- DEC-197 merge: `81271caa2ed3c2acc3257169c2f47572461cfc46`
- DEC-197 diagnostic blob: `3f53e79b52d3a2e4de1e7f61e142ecc55197aa87`
- DEC-196 reviewed-result blob: `17235435604bc5c0bd8950037bd8c49a0c6fb81a`
- EXP-054 protocol blob: `3ffac844f9ed5308512dc3313e850cc84fb6d144`
- EXP-054 reviewed evidence fingerprint: `307b576f06c6aa2fb01a267232a0de553bfa79c1bdbe6bf5d55b2bfc3b40787c`

The predecessor diagnostic classification must remain:

`RESIDUAL_BOUND_NARROWED_AGGREGATE_PASSES_AND_IMPROVED_SOME_DOWNSIDE_WINDOWS_BUT_DID_NOT_CREATE_TEMPORAL_BREADTH`

DEC-197 must still report zero accepted candidates and keep EXP-054 rerun/replacement, stability relaxation, selection-outcome ranking, selection-window recalibration, and selection-window quotas false.

## Unchanged predecessor pipeline

EXP-055 retains exactly:

- three leave-one-fit-regime-out HGB views
- two utility regressors per view
- six regressors per cell
- the same feature inputs
- the same LONG/SHORT 0.5-pip utility targets
- unchanged unanimous positive-utility direction eligibility
- six pooled out-of-fit utility calibration references per cell
- 24 fit-half-year utility-support references per cell
- 12 fit-half-year feature-support references per cell
- 24 target-specific out-of-fit residual references per cell
- the EXP-054 lower-quartile residual rule at q = 0.25
- candidate budgets 250 / 500 / 1000
- unchanged aggregate financial gates
- unchanged four selection-period half-year temporal-stability windows
- unchanged 10% per-window candidate-share floor
- unchanged per-window financial-sign requirements
- unchanged validation and retrospective-holdout chronology
- no-refit forward semantics

## Residual-breadth score

For an already EXP-054-eligible row and its frozen unanimous LONG or SHORT direction, EXP-054 already forms twelve downside-adjusted lower-bound utilities:

- three jackknife-view predictions
- four excluded-regime fit-half-year downside residuals per view
- one agreed-direction target per row

Those twelve comparisons cover the twelve frozen fit half-years across 2015–2020.

EXP-055 does not construct new reference vectors.

For each row:

1. reuse the exact twelve EXP-054 lower-bound utilities;
2. count how many are strictly greater than zero;
3. divide the count by 12.

This produces:

`fit_temporal_residual_breadth`

with possible values:

`0/12, 1/12, ..., 12/12`

A lower bound equal to zero does not count as positive.

The breadth score is ranking-only. It does not add a new row-eligibility requirement.

## Selection ranking

Eligible rows are ranked exactly by:

1. fit-temporal residual breadth descending;
2. robust fit-temporal residual-bound utility descending;
3. robust fit-temporal feature support descending;
4. robust fit-temporal utility support descending;
5. robust pooled calibrated utility descending;
6. robust raw utility descending;
7. row identity ascending.

This directly prefers rows whose conservative utility lower bounds remain positive across more frozen fit half-years while retaining EXP-054 worst-case residual-bound utility as the first tie-break.

No selection-window identity or outcome enters the ranking.

## Six-part cutoff

For every unchanged candidate budget, freeze the budget-th row's exact sextuple:

- residual breadth;
- residual-bound utility;
- feature support;
- fit-temporal utility support;
- pooled calibrated utility;
- raw utility.

Forward rows pass the sextuple lexicographically in the same order.

Exact sextuple ties may exceed the nominal budget.

Unavailable budgets keep all six cutoff components null.

## Forward chronology

If no stable selection exists:

- validation remains `LOCKED_NO_SELECTION`;
- retrospective holdout remains `LOCKED_NO_SELECTION`.

If a stable variant exists, validation and holdout reuse unchanged:

- the exact six fitted regressors;
- the exact six pooled references;
- the exact 24 utility-support references;
- the exact 12 feature-support references;
- the exact 24 residual references;
- the same twelve lower-bound comparisons used to derive breadth;
- the exact selection-derived six-part cutoff.

No model, reference, budget, breadth rule, residual quantile, or cutoff may be rebuilt downstream.

## Leakage and tuning prohibitions

EXP-055 forbids:

- realized selection outcomes in ranking;
- realized validation outcomes in ranking;
- realized holdout outcomes in ranking;
- selection-window residual references;
- validation-window residual references;
- holdout-window residual references;
- selection-window calibration;
- selection-window quotas;
- per-window cutoff tuning;
- stability-share relaxation;
- stability-financial relaxation;
- removal of early stability windows;
- pair/timeframe/horizon-specific breadth rules;
- budget-specific breadth rules.

## Authorization state

DEC-198 opens only the residual-breadth protocol source definition.

It keeps false:

- model protocol result production;
- model fitting;
- historical result execution;
- feature changes;
- financial target changes;
- chronology changes;
- HGB structural changes;
- jackknife changes;
- consensus changes;
- positive-utility eligibility changes;
- pooled calibration changes;
- utility-support changes;
- feature-support changes;
- EXP-054 residual-bound rule changes;
- selection-window calibration;
- selection-window quotas;
- validation/holdout recalibration;
- realized selection-outcome ranking;
- density-anchor changes;
- minimum candidate-count changes;
- stability-screen changes;
- per-window financial-gate changes;
- per-window cutoff tuning;
- logistic/classifier fallback;
- promotion;
- shadow/demo execution;
- broker mutation;
- live orders;
- real-money action;
- trading.

The sole protocol change authorized by DEC-198 is the residual-breadth ranking score and its corresponding six-part cutoff.

## Source identity

Protocol source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_protocol.py`

Git blob:

`0ef3f932cade1a62e1faf946e9a9b87cf9c98744`

Focused tests:

`tests/test_phase8a_exp055_fit_temporal_residual_breadth_utility_protocol.py`

Git blob:

`b5bb56110eb15f2280749bbe2355153baa17e906`

Protocol version:

`fmp-exp055-fit-temporal-residual-breadth-utility-protocol-v1`

## Evidence status

EXP-055 is explicitly prior-result-informed retrospective research.

It is not untouched out-of-sample evidence.

No EXP-055 model fit or historical result exists under DEC-198.

## Next gate

A later separate decision may implement the deterministic in-memory EXP-055 training/evaluation core against this exact protocol.

That implementation must remain source-only and non-executable before any artifact/evidence contract, readiness path, workflow, run authorization, or historical result production is considered.
