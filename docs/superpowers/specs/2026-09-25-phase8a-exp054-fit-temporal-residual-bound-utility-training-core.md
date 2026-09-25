# Phase 8A — EXP-054 Fit-Temporal Residual-Bound Utility Training Core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / IN-MEMORY CORE / NON-EXECUTABLE
**Decision:** DEC-186
**Experiment:** EXP-20260925-054

## 1. Purpose

DEC-186 implements the deterministic in-memory training/evaluation core for the exact DEC-185 EXP-054 residual-bound utility protocol.

The implementation preserves the complete EXP-053 fitting, calibration, feature-support, financial-gate, temporal-stability, and forward chronology. It adds only:

- fit-half-year out-of-fit residual references;
- fixed lower-quartile downside residuals;
- robust residual-bound utility scoring;
- residual-bound-first ranking;
- a five-part selection cutoff.

DEC-186 does not load accepted historical artifacts and does not authorize authoritative model fitting, workflow dispatch, historical result execution, promotion, or trading.

## 2. Frozen source bindings

DEC-186 binds:

- DEC-185 merge: `3578491ab24b3fa6209ea674e02e1bce5dd99895`;
- DEC-185 protocol blob: `3ffac844f9ed5308512dc3313e850cc84fb6d144`;
- predecessor EXP-053 training-core blob: `4fd0e48302f97e188a8124e1543bde0ffdb43b6f`;
- predecessor training-core decision: `DEC-175`.

Any byte drift fails closed.

The predecessor source-level model-fit and result-execution locks must remain false.

## 3. Unchanged fit and support stack

Every cell still fits exactly:

- three leave-one-fit-regime-out HGB views;
- two utility regressors per view;
- six regressors per cell.

DEC-186 reuses the unchanged predecessor builders for:

- six pooled out-of-fit calibration references;
- 24 fit-half-year utility-support references;
- 12 fit-half-year feature-support references.

No classifier, logistic fallback, full-fit model, view weighting, or view fallback is introduced.

## 4. Residual-reference construction

For each jackknife view, its one excluded fit regime is partitioned into the same four frozen half-year windows.

For each view, target, and half-year:

1. score the half-year with the already-fitted out-of-fit view regressor;
2. read the realized fit-period target;
3. compute residual `realized - prediction`;
4. require all predictions, targets, and residuals finite;
5. sort residuals ascending;
6. freeze the lower-quartile residual at index `floor(0.25 * (n - 1))`.

Exactly:

- 3 views;
- 2 financial targets;
- 4 half-years;

produce **24 residual references per cell**.

## 5. Residual evidence

Every residual-reference record freezes:

- exact view identity;
- exact excluded fit regime;
- exact target column;
- exact half-year name/start/end-exclusive;
- row count;
- prediction digest;
- minimum residual;
- maximum residual;
- mean residual;
- sorted residual digest;
- fixed downside quantile `0.25`;
- exact quantile index;
- exact downside residual.

References are built only from excluded fit-regime rows.

Selection, validation, and retrospective-holdout rows never enter them.

## 6. Robust residual-bound score

DEC-186 first computes the exact EXP-053 consensus and all prior ranking components.

For each EXP-053-eligible row:

- the unanimous direction chooses the LONG or SHORT 0.5-pip target;
- each of the three view predictions is scored on the row;
- each view prediction is combined with each of that view's four frozen downside residuals;
- 12 finite lower-bound utilities are produced;
- the minimum is `robust_fit_temporal_residual_bound_utility`.

NO_TRADE rows remain outside ranking.

The residual-bound score may be negative. It is not a new eligibility criterion.

## 7. Selection ranking

Eligible rows are ranked exactly by:

1. robust residual-bound utility descending;
2. robust fit-temporal feature support descending;
3. robust fit-temporal utility support descending;
4. robust pooled calibrated utility descending;
5. robust raw utility descending;
6. row identity ascending.

The candidate budgets remain:

- 250;
- 500;
- 1000.

## 8. Five-part cutoff

For every available budget, DEC-186 freezes:

- residual-bound cutoff;
- feature-support cutoff;
- utility-support cutoff;
- pooled calibrated-utility cutoff;
- raw-utility cutoff.

Rows pass lexicographically in that exact order.

Exact five-part ties may exceed the nominal budget.

Unavailable budgets retain null values for all five cutoff components.

## 9. Financial and temporal gates

Candidate financial evaluation is unchanged.

Selection aggregate gating still uses the frozen 0.5-pip scenario and the same financial criteria.

Only aggregate passes unlock the unchanged four half-year temporal-stability windows.

The unchanged requirements remain:

- minimum 10% directional candidate share per window;
- positive total net pips;
- positive mean net pips;
- gross positive pips greater than absolute gross negative pips;
- all four windows must pass.

No window quota, window-specific cutoff, gate relaxation, or window removal is introduced.

## 10. Forward chronology

If no stable selection exists:

- validation remains `LOCKED_NO_SELECTION`;
- retrospective holdout remains `LOCKED_NO_SELECTION`.

If a stable selection exists, forward stages reuse:

- the exact six fitted regressors;
- the exact six pooled calibration references;
- the exact 24 utility-support references;
- the exact 12 feature-support references;
- the exact 24 residual references;
- the exact five-part selection-derived cutoff.

No fit, residual quantile, reference, budget, or cutoff is rebuilt.

## 11. Determinism

DEC-186 records deterministic digests for:

- prediction vectors used by residual references;
- sorted residual arrays;
- complete scored consensus rows.

Every completed cell receives a canonical result fingerprint before the fingerprint field is added.

## 12. Source-only boundary

The core accepts in-memory feature/outcome frames only.

It contains no:

- authoritative readiness validation;
- accepted historical artifact loading;
- workflow dispatch;
- GitHub run control;
- broker mutation;
- order submission.

Those remain later, separately authorized gates.

## 13. Source identity

Training core:

`src/fmp/market_learning/model_successor_fit_temporal_residual_bound_utility_training.py`

Git blob:

`1652024782c96780c186ef1cd21c7e85c491780c`

Focused tests:

`tests/test_phase8a_exp054_fit_temporal_residual_bound_utility_training.py`

Git blob:

`637bf03c82e38cdc29279b813ab63a527b5928aa`

Training-core version:

`fmp-exp054-fit-temporal-residual-bound-utility-training-core-v1`

Decision:

`DEC-186`

## 14. Authorization state

DEC-186 keeps false:

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

A later separate decision may freeze the EXP-054 artifact/evidence contract against the exact DEC-185/186 sources.

That contract must independently validate:

- 18 cells;
- 108 regressors;
- 108 pooled calibration references;
- 432 fit-temporal utility-support references;
- 216 fit-temporal feature-support references;
- 432 target-specific residual references;
- exact five-part cutoff evidence;
- unchanged financial/stability/forward chronology.

It must remain non-executable before readiness or accepted historical artifact loading.
