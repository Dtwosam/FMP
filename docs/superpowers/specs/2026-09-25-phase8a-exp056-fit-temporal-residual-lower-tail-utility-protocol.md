# Phase 8A — EXP-056 Fit-Temporal Residual Lower-Tail Utility Protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-209
**Experiment:** EXP-20260925-056

## Purpose

DEC-209 opens a source-only successor to EXP-055 after DEC-208 shows that binary fit-period residual breadth did not transfer into selection-period chronological breadth and weakened the surviving aggregate-pass variants' financial quality.

EXP-056 keeps EXP-055 eligibility, lower-bound construction, residual breadth, residual-bound utility, feature support, utility support, pooled calibration, budgets, chronology, aggregate financial gates, temporal-stability gates, validation/holdout chronology, and no-refit semantics unchanged.

It adds only a continuous fit-period residual lower-tail ranking score derived from the same twelve frozen EXP-055 lower-bound utilities.

## Frozen predecessor bindings

DEC-209 binds:

- DEC-208 merge: `9efc720149fea77ab60e50ac0222f6ed1c458195`
- DEC-208 diagnostic blob: `5ff61be317b225d9d7ec656b4789c4561d52b522`
- DEC-207 reviewed-result blob: `e2226117ebf10b762557d43549390c46c243bbae`
- EXP-055 protocol blob: `0ef3f932cade1a62e1faf946e9a9b87cf9c98744`
- EXP-055 reviewed evidence fingerprint: `f3a386dad7f23ac9d6867d030ac90e0884f3ab658c9ffecce8647048037d2510`

The predecessor diagnostic classification must remain:

`FIT_RESIDUAL_BREADTH_DID_NOT_TRANSFER_TO_SELECTION_TEMPORAL_BREADTH_AND_WEAKENED_PASS_VARIANT_FINANCIALS`

DEC-208 must still report zero accepted candidates and keep EXP-055 rerun/replacement, stability relaxation, selection-outcome ranking, selection-window recalibration/quotas, and breadth retuning on selection outcomes false.

## Unchanged predecessor pipeline

EXP-056 retains exactly:

- three frozen jackknife views
- two utility regressors per view
- six regressors per cell
- unchanged LONG/SHORT 0.5-pip utility targets
- unchanged unanimous positive-utility direction eligibility
- six pooled out-of-fit calibration references per cell
- 24 fit-half-year utility-support references per cell
- 12 fit-half-year feature-support references per cell
- 24 target-specific residual references per cell
- the EXP-054/055 q = 0.25 downside-residual rule
- the exact twelve downside-adjusted lower-bound utilities per eligible row
- the EXP-055 residual-breadth score
- candidate budgets 250 / 500 / 1000
- unchanged aggregate financial gates
- unchanged four selection-period half-year temporal-stability windows
- unchanged 10% per-window candidate-share floor
- unchanged per-window financial-sign requirements
- unchanged validation and retrospective-holdout chronology
- no-refit forward semantics

## Residual lower-tail score

For an already EXP-055-eligible row and its frozen unanimous LONG or SHORT direction:

1. reuse the exact twelve EXP-055 downside-adjusted lower-bound utilities;
2. sort the twelve finite bounds ascending;
3. take the arithmetic mean of the three smallest bounds.

Three is the exact lower-quartile count because `0.25 × 12 = 3`.

There is:

- no interpolation;
- no trimming;
- no winsorization;
- no new reference vector;
- no selection-window information;
- no validation/holdout information.

The resulting score is:

`fit_temporal_residual_lower_tail_mean`

The score preserves continuous lower-tail margin that the binary EXP-055 breadth count discarded.

## Selection ranking

Eligible rows are ranked exactly by:

1. fit-temporal residual lower-tail mean descending;
2. fit-temporal residual breadth descending;
3. robust fit-temporal residual-bound utility descending;
4. robust fit-temporal feature support descending;
5. robust fit-temporal utility support descending;
6. robust pooled calibrated utility descending;
7. robust raw utility descending;
8. row identity ascending.

No selection-window identity or realized selection outcome enters ranking.

## Seven-part cutoff

For every unchanged candidate budget, freeze the budget-th row's exact septuple:

- residual lower-tail mean;
- residual breadth;
- residual-bound utility;
- feature support;
- fit-temporal utility support;
- pooled calibrated utility;
- raw utility.

Forward rows pass the septuple lexicographically in the same order.

Exact septuple ties may exceed the nominal budget.

Unavailable budgets keep all cutoff components null.

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
- the same twelve lower-bound utilities;
- the fixed worst-three arithmetic-mean lower-tail rule;
- the exact selection-derived seven-part cutoff.

No model, reference, budget, lower-tail rule, residual quantile, breadth rule, or cutoff may be rebuilt downstream.

## Leakage and tuning prohibitions

EXP-056 forbids:

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
- pair/timeframe/horizon-specific tail rules;
- budget-specific tail rules.

## Authorization state

DEC-209 opens only the residual lower-tail protocol source definition.

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
- residual-bound changes;
- residual-breadth changes;
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

The sole protocol change authorized by DEC-209 is the continuous worst-three lower-tail mean ranking score and its corresponding seven-part cutoff.

## Source identity

Protocol source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_protocol.py`

Git blob:

`14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d`

Focused tests:

`tests/test_phase8a_exp056_fit_temporal_residual_lower_tail_utility_protocol.py`

Git blob:

`683bc8f424f01d6e8cbb1f9478ea0140cfcdeb81`

Protocol version:

`fmp-exp056-fit-temporal-residual-lower-tail-utility-protocol-v1`

## Evidence status

EXP-056 is explicitly prior-result-informed retrospective research.

It is not untouched out-of-sample evidence.

No EXP-056 model fit or historical result exists under DEC-209.

## Next gate

A later separate decision may implement the deterministic in-memory EXP-056 training/evaluation core against this exact protocol.

That implementation must remain source-only and non-executable before any artifact/evidence contract, readiness path, workflow, run authorization, or historical result production is considered.
