# Phase 8A — EXP-052 Fit-Temporal-Support Utility Protocol

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY PROTOCOL / NO EXP-052 FIT
**Decision:** DEC-163
**Experiment:** EXP-20260925-052

## 1. Purpose

DEC-163 opens EXP-052 as a narrow source-only successor to EXP-051.

DEC-162 shows that EXP-051's out-of-fit pooled percentile calibration improves the shared USDJPY 5m / 60m top-250 financial result, but it does not create candidate support in 2021 and it degrades the broader 500/1000 rankings.

EXP-052 therefore changes only the ranking evidence used after unchanged EXP-051 direction eligibility.

The new evidence is fit-only temporal support.

No model fit, historical result execution, workflow dispatch, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading authorization is opened.

## 2. Exact predecessor binding

DEC-163 binds:

- DEC-162 merge: `3d8453c544fc4b06c691d1068828ec6da9fc7110`;
- DEC-162 diagnostic blob: `00b9cbb5b0c95bd161d429d1f973d1e807f02a48`;
- DEC-161 result-decision blob: `14bc6f2e9172aa325aeb556b7abeacf2c756c475`;
- EXP-051 protocol blob: `c39309c4115cae1ea058e56f30cae4af6407e36e`;
- EXP-051 result-evidence fingerprint: `7dd836ed1c76c8eefd09b2b75e1eef9e875f5c6261c6fbb2cac8e3209781aaea`.

The predecessor diagnostic classification must remain:

`TOP_250_FINANCIAL_QUALITY_IMPROVED_BUT_EARLY_TEMPORAL_COVERAGE_UNCHANGED_AND_BROAD_BUDGETS_DEGRADED`

The predecessor must continue to record:

- zero accepted model candidates;
- 28 available budget variants;
- 26 unavailable budget variants;
- zero stable-selection passes;
- 26,392 utility-eligible selection rows;
- successor protocol source design open;
- successor fit and result execution closed.

## 3. Unchanged model and eligibility layer

EXP-052 preserves EXP-051 exactly through direction eligibility.

Per cell, it keeps:

- the same three leave-one-regime-out jackknife views;
- the same two HGB regressors per view;
- the same six regressors total;
- the same LONG and SHORT 0.5-pip net-utility targets;
- the same positive-utility requirement;
- the same unanimous direction rule;
- the same disagreement-to-NO_TRADE policy;
- the same robust raw utility;
- the same six pooled excluded-regime calibration references;
- the same EXP-051 robust pooled calibrated utility.

No feature, target, model-family, HGB structure, fit-period, view, or direction-eligibility change is authorized.

## 4. Frozen fit-only support windows

Each two-year excluded fit regime is split into four fixed half-year windows.

### Excluded regime 2015-2016

- `fit_2015_h1`: 2015-01-01 to 2015-07-01
- `fit_2015_h2`: 2015-07-01 to 2016-01-01
- `fit_2016_h1`: 2016-01-01 to 2016-07-01
- `fit_2016_h2`: 2016-07-01 to 2017-01-01

### Excluded regime 2017-2018

- `fit_2017_h1`: 2017-01-01 to 2017-07-01
- `fit_2017_h2`: 2017-07-01 to 2018-01-01
- `fit_2018_h1`: 2018-01-01 to 2018-07-01
- `fit_2018_h2`: 2018-07-01 to 2019-01-01

### Excluded regime 2019-2020

- `fit_2019_h1`: 2019-01-01 to 2019-07-01
- `fit_2019_h2`: 2019-07-01 to 2020-01-01
- `fit_2020_h1`: 2020-01-01 to 2020-07-01
- `fit_2020_h2`: 2020-07-01 to 2021-01-01

No selection, validation, or retrospective-holdout row appears in these windows.

## 5. Out-of-fit support-reference construction

For each cell, jackknife view, and LONG/SHORT target:

1. identify the exact two-year regime excluded from that view;
2. split that excluded regime into its four frozen half-years;
3. score every row in each half-year using the already-fitted view regressor;
4. require every prediction to be finite;
5. sort the half-year prediction vector ascending;
6. freeze it as one support reference.

This creates:

- 4 support references per view/target;
- 8 per view;
- 24 per cell.

Every support-reference row is out-of-fit for the regressor scoring it.

Realized outcomes do not enter support-reference construction.

## 6. Support percentile

For a scored row that already satisfies EXP-051 direction eligibility, each view's agreed-direction raw utility is compared independently with the four support references attached to that view and direction.

Each percentile is:

`count(reference_prediction <= raw_predicted_utility) / reference_count`

Across three views and four half-years per view, each eligible row receives exactly 12 support-percentile comparisons.

Empty or non-finite references fail closed.

## 7. Robust fit-temporal support

The primary EXP-052 ranking score is:

`minimum support percentile across all 12 view-by-half-year comparisons`

This is intentionally conservative.

A high score requires the row's predicted agreed-direction utility to rank strongly against every out-of-fit fit-half-year reference, not merely against the pooled two-year excluded regime.

EXP-051's pooled calibrated utility remains the secondary score.

EXP-051's robust raw utility remains the tertiary score.

## 8. Selection ranking

Eligible selection rows are sorted by:

1. robust fit-temporal support descending;
2. EXP-051 robust pooled calibrated utility descending;
3. robust raw utility descending;
4. row identity ascending.

The raw EXP-051 direction-eligibility set remains unchanged.

The protocol does not impose a selection-window quota, selection-window calibration, or realized-outcome ranking feature.

## 9. Cutoff triple

For each unchanged budget anchor:

- 250;
- 500;
- 1000;

the budget-th ranked row freezes:

- robust fit-temporal support cutoff;
- robust pooled calibrated-utility cutoff;
- robust raw-utility cutoff.

A scored row passes when:

- support is above the support cutoff; or
- support equals the cutoff and pooled calibrated utility is above its cutoff; or
- both are equal and robust raw utility is at least the raw cutoff.

Exact triple ties may exceed the nominal budget.

Budgets remain unavailable when the unchanged eligible-row count is below the anchor.

## 10. Aggregate and stability gates remain unchanged

EXP-052 does not alter the frozen selection financial gate.

It also preserves the exact four selection stability windows:

- 2021 H1;
- 2021 H2;
- 2022 H1;
- 2022 H2.

Every window still requires:

- candidate share at least 10% of full-selection candidate count;
- positive total net pips;
- positive mean net pips;
- gross positive pips greater than absolute gross negative pips.

All four windows must pass.

No share-floor relaxation, financial-gate relaxation, window removal, or per-window cutoff tuning is authorized.

## 11. Validation and retrospective holdout

If selection produces no stable variant, validation remains locked.

If a variant is selected, validation reuses unchanged:

- the six fitted regressors;
- the six pooled EXP-051 calibration references;
- the 24 fit-half-year support references;
- the raw unanimous direction rule;
- the selection-derived support/pooled/raw cutoff triple.

Validation performs no refit, recalibration, reference rebuild, budget recomputation, or window tuning.

Retrospective holdout remains locked unless validation passes and then reuses the identical frozen state.

## 12. Explicitly forbidden leakage paths

EXP-052 forbids:

- selection rows in support references;
- validation rows in support references;
- holdout rows in support references;
- realized selection outcomes in ranking;
- realized fit outcomes in support calibration;
- support-reference rebuilding after selection;
- selection-window calibration;
- validation calibration;
- holdout calibration;
- per-window cutoff tuning.

The only new information is the time partition of already-authorized out-of-fit fit predictions.

## 13. Authorization state

DEC-163 keeps false:

- authoritative protocol-result production;
- model fit;
- historical result execution;
- feature change;
- financial-target change;
- outer chronology change;
- HGB structural change;
- jackknife-view change;
- unanimous direction-consensus change;
- positive-utility requirement change;
- pooled EXP-051 calibration change;
- selection-window calibration;
- validation calibration;
- holdout calibration;
- realized-selection-outcome ranking;
- budget-anchor change;
- minimum candidate-floor change;
- stability-screen change;
- per-window financial-gate change;
- per-window cutoff tuning;
- logistic reintroduction;
- classifier fallback;
- promotion;
- shadow/demo execution;
- broker mutation;
- live orders;
- real-money action;
- trading authorization.

Only fit-temporal-support calibration is authorized as the protocol change.

## 14. Source identity

Protocol source:

`src/fmp/market_learning/model_successor_fit_temporal_support_utility_protocol.py`

Git blob:

`01d5080560ec5d41653694b4df086ff2f10e770d`

Focused tests:

`tests/test_phase8a_exp052_fit_temporal_support_utility_protocol.py`

Git blob:

`fac0c626fc72ce9e4f88beb15e59c01e39a3af4c`

Protocol version:

`fmp-exp052-fit-temporal-support-utility-protocol-v1`

Decision:

`DEC-163`

## 15. Next gate

After DEC-163 merges and repository regressions pass, the next safe step is a deterministic in-memory EXP-052 training/evaluation core.

That core may implement the 24 fit-half-year support references and frozen support-first ranking against caller-supplied frames.

It must not add accepted historical artifact loading, workflow dispatch, authoritative fitting, result execution, promotion, or trading authority.
