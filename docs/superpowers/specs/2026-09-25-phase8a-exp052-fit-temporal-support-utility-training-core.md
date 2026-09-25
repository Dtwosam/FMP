# Phase 8A — EXP-052 Fit-Temporal-Support Utility Training Core

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NO AUTHORITATIVE EXP-052 FIT
**Decision:** DEC-164
**Experiment:** EXP-20260925-052

## 1. Purpose

DEC-164 implements the deterministic in-memory training and evaluation core for the DEC-163 fit-temporal-support protocol.

It reuses the frozen EXP-051 fitting and pooled-calibration machinery and adds only:

- 24 out-of-fit fit-half-year support references per cell;
- support-first scoring;
- a support / pooled-calibrated / raw cutoff triple;
- forward reuse of the frozen triple and references.

No accepted historical artifact loader, result-producing workflow, authoritative historical fit, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading path is added.

## 2. Exact source binding

The training core binds:

- DEC-163 merged commit: `9108cd170b2eccf73bddb6cbf8d6d7118dbd9cd1`;
- DEC-163 protocol blob: `01d5080560ec5d41653694b4df086ff2f10e770d`;
- predecessor DEC-151 training-core blob: `959fbfd52f41c08de3c1a26769e0e7fd2545b92a`.

DEC-151 independently binds its DEC-150 protocol and frozen predecessor training core.

DEC-164 source validation fails closed on direct source drift and requires all predecessor source-level fit/result authorization flags to remain false.

## 3. Unchanged fitting topology

The core preserves the exact six-regressor EXP-051 fitting topology.

For each cell:

- the same three two-regime jackknife fit views are built;
- each view fits LONG and SHORT 0.5-pip HGB utility regressors;
- exactly six regressors are fitted;
- target summaries, preprocessor fingerprints, and model fingerprints are retained.

No full-fit fallback, classifier fallback, view weighting, or view rescue is added.

## 4. Pooled EXP-051 calibration retained

After fitting, DEC-164 calls the exact frozen DEC-151 pooled calibration builder.

Per cell it retains:

- three view records;
- two utility targets per view;
- six pooled excluded-regime prediction references total.

The EXP-051 pooled percentile remains the secondary ranking score.

No pooled calibration rule changes.

## 5. Fit-half-year support references

DEC-164 then builds the DEC-163 support references.

For each view:

1. identify the two-year regime excluded from that view;
2. split it into the four frozen half-years;
3. score each half-year with the already-fitted view model;
4. do this separately for LONG and SHORT;
5. require non-empty finite predictions;
6. sort each prediction vector ascending;
7. freeze its digest and summary.

Per view:

- 2 targets;
- 4 windows per target;
- 8 support references.

Per cell:

- 3 views;
- 24 support references.

Every support reference remains out-of-fit relative to the model that produces it.

## 6. Support evidence

Each support-reference evidence record contains:

- view identity;
- included regimes;
- excluded regime;
- target identity;
- support-window name;
- parent regime;
- start;
- end-exclusive;
- row count;
- minimum prediction;
- maximum prediction;
- mean prediction;
- row-bound prediction digest;
- sorted-reference digest.

A count other than 24 fails closed.

## 7. Selection scoring

For any scored frame, the core computes the exact predecessor three-view raw predictions once.

It then preserves EXP-051 direction eligibility:

- every view must select the same LONG or SHORT direction;
- the unique winning utility must be positive;
- disagreement or non-positive utility remains NO_TRADE.

For eligible rows, the core computes:

- robust raw utility: unchanged predecessor minimum raw utility;
- robust pooled calibrated utility: unchanged EXP-051 minimum pooled percentile across three views;
- robust fit-temporal support: minimum percentile across the 12 view-by-half-year support comparisons for the agreed direction.

All pooled and support percentiles must be finite and inside [0, 1].

## 8. Consensus evidence

Selection and any unlocked forward stage record:

- row count;
- LONG / SHORT / NO_TRADE counts;
- eligible row count and rate;
- minimum/maximum robust raw utility;
- minimum/maximum robust pooled calibrated utility;
- minimum/maximum robust fit-temporal support;
- three-view target prediction digests;
- a row-bound consensus digest covering row identity, direction, raw utility, pooled utility, and support.

## 9. Cutoff triple

For each unchanged budget anchor 250/500/1000, eligible selection rows rank by:

1. fit-temporal support descending;
2. pooled calibrated utility descending;
3. raw utility descending;
4. row identity ascending.

If fewer eligible rows exist than the budget, the budget remains unavailable.

Otherwise the budget-th row freezes:

- `selection_derived_support_cutoff`;
- `selection_derived_pooled_calibrated_cutoff`;
- `selection_derived_raw_cutoff`.

Candidate application is lexicographic.

Exact triple ties may exceed the nominal budget.

## 10. Financial evaluation

The cutoff triple only changes which already-eligible rows are candidates.

Realized evaluation still uses the frozen financial machinery.

For every requested scenario the core records:

- directional candidate count;
- total net pips;
- mean net pips;
- gross positive pips;
- gross negative pips;
- independently computed financial gate.

No outcome value enters fitting, pooled calibration, or support calibration.

## 11. Temporal stability

Only aggregate financial passes enter the unchanged four-window stability screen.

For each 2021 H1 / 2021 H2 / 2022 H1 / 2022 H2 window the core applies the exact same frozen cutoff triple and computes:

- candidate count;
- share of full-selection candidate count;
- financial metrics;
- unchanged window gate.

All windows must pass.

No per-window quota, cutoff, support recalibration, pooled recalibration, or gate relaxation exists.

## 12. Variant selection

Among variants passing aggregate financial and temporal stability, DEC-164 reuses the predecessor material tie-break unchanged:

1. higher 0.5-pip total net pips;
2. higher directional candidate count;
3. smaller budget anchor.

The support score is not introduced as a post-gate performance tie-break.

## 13. Validation and retrospective holdout

If no selection variant survives, validation remains locked.

If selected, validation reuses:

- the exact six fitted models;
- the exact six pooled references;
- the exact 24 support references;
- the same raw direction rule;
- the exact support/pooled/raw cutoff triple.

No refit or reference rebuild occurs.

Retrospective holdout remains locked unless validation passes and then uses the identical frozen state.

## 14. Cell result evidence

The deterministic in-memory result includes:

- EXP-052 protocol/training identity;
- DEC-163 source binding;
- processed-manifest identity;
- split row counts;
- six model fit records;
- six pooled calibration references;
- 24 fit-temporal support references;
- selection consensus diagnostics and digest;
- all three budget variants;
- aggregate and stability evidence;
- selected variant, if any;
- validation evidence, if unlocked;
- holdout evidence, if unlocked;
- canonical result fingerprint;
- explicit false execution/promotion/trading locks.

If no variant survives, the selection status is:

`NO_FIT_TEMPORAL_SUPPORT_UTILITY_STABLE_MODEL_CHALLENGER`

## 15. Source-only boundary

The in-memory core can fit caller-supplied frames for deterministic research testing, as predecessor source-only cores do.

That does not authorize:

- loading accepted historical artifacts;
- running all 18 accepted historical cells;
- producing authoritative EXP-052 evidence;
- workflow dispatch;
- promotion;
- trading.

The outer source-level flags remain false.

## 16. Source identity

Training core:

`src/fmp/market_learning/model_successor_fit_temporal_support_utility_training.py`

Git blob:

`fe5664438752a161134bbed6f55d9985f1c1470a`

Focused tests:

`tests/test_phase8a_exp052_fit_temporal_support_utility_training.py`

Git blob:

`fbf19a91e8225421e30f0d8ec2e5280d21ef35fd`

Training-core version:

`fmp-exp052-fit-temporal-support-utility-training-core-v1`

Decision:

`DEC-164`

## 17. Authorization state

DEC-164 keeps false:

- authoritative EXP-052 result execution;
- authoritative model fit;
- workflow execution;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 18. Next gate

A later separate decision may freeze an EXP-052 artifact-backed runner/evidence contract.

That contract must bind the exact DEC-163 protocol and DEC-164 training-core blobs, validate complete 18-cell / 108-regressor / 108 pooled-reference / 432 support-reference aggregate evidence, and remain non-executable before accepted historical artifact loading.
