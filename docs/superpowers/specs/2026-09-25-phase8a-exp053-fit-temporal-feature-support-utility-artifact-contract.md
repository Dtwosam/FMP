# Phase 8A — EXP-053 Fit-Temporal Feature-Support Artifact Contract

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-176
**Experiment:** EXP-20260925-053

## 1. Purpose

DEC-176 freezes the artifact-backed runner and aggregate evidence contract for EXP-053.

It binds the exact DEC-174 protocol, merged DEC-175 in-memory training core, accepted immutable historical feature/outcome/readiness identities, accepted historical artifact loader, and the frozen EXP-052 artifact validator for every unchanged financial, stability, and utility-support invariant.

DEC-176 does **not** authorize accepted historical fitting or result execution.

The authoritative bundle must reject before readiness validation or historical artifact loading while the DEC-176 outer execution lock is false.

## 2. Exact source binding

DEC-176 binds:

- DEC-174 merge: `9687eb8ea3920e87d6681adf7366a3ce0bba7154`
- DEC-174 protocol blob: `11ae3fc8e68687cc04957ed9243d8c5969227fb8`
- DEC-175 merge: `60abce7c2674f9c25e4132037c9eb24cab1baf22`
- DEC-175 training-core blob: `4fd0e48302f97e188a8124e1543bde0ffdb43b6f`
- predecessor EXP-052 training-core blob: `fe5664438752a161134bbed6f55d9985f1c1470a`
- predecessor EXP-052 artifact-validator blob: `ae06184b9a84405119b6ed434a8973139d8ae006`
- accepted historical artifact-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

Any bound-byte drift fails closed.

## 3. Unchanged predecessor validation

For unchanged EXP-052 evidence, DEC-176 reuses the frozen DEC-165 validators rather than reimplementing them.

Before predecessor validation, DEC-176 normalizes only the explicit DEC-174 suffix in forbidden/excluded status labels.

The predecessor validators still independently enforce:

- exact three-view jackknife topology;
- six HGB regressors per cell;
- six pooled excluded-regime calibration references per cell;
- 24 fit-half-year utility-support references per cell;
- EXP-052 direction eligibility;
- utility-support/pooled/raw score constraints;
- 250/500/1000 budget identity;
- aggregate financial gates;
- four-window temporal-stability gates;
- validation/holdout scenario inventory;
- exact forward chronology.

## 4. Feature-support evidence

Every cell must additionally prove exactly 12 fit-temporal feature-support references:

- four excluded-regime half-year references per jackknife view;
- three jackknife views;
- 12 references per cell;
- 216 references across the complete 18-cell aggregate.

Each view-level feature-support record must prove:

- status `FROZEN`;
- exact included-regime pair;
- exact excluded regime;
- exactly four references;
- exact frozen half-year window inventory.

Each half-year record must prove:

- status `FROZEN`;
- exact name, parent regime, start, and end-exclusive;
- positive row count;
- positive transformed dimension count;
- positive active dimension count no greater than transformed dimensions;
- valid reused preprocessor SHA-256;
- valid center SHA-256;
- valid scale SHA-256;
- valid active-dimension-mask SHA-256;
- finite non-negative minimum, maximum, and mean reference distances;
- minimum <= mean <= maximum;
- valid sorted-reference-distance SHA-256.

The declared count is not trusted without validating all 12 records.

## 5. Consensus evidence

Every selection or unlocked forward consensus block must preserve the complete EXP-052 consensus evidence and additionally carry:

- `minimum_robust_fit_temporal_feature_support`;
- `maximum_robust_fit_temporal_feature_support`;
- `fit_temporal_feature_support_reference_count = 12`.

If no eligible rows exist, both feature-support bounds must be null.

Otherwise both bounds must be finite, ordered, and within `[0, 1]`.

## 6. Four-part cutoff

Every evaluated budget and unlocked forward block must carry:

- selection-derived feature-support cutoff;
- selection-derived utility-support cutoff;
- selection-derived pooled calibrated cutoff;
- selection-derived raw cutoff.

The first three must be finite within `[0, 1]`.

The raw cutoff must be finite and strictly positive.

Unavailable budgets must keep the feature-support cutoff null, while the frozen predecessor validator independently requires all predecessor cutoff fields null.

## 7. Variant and stability validation

DEC-176 validates the feature-support cutoff first, then delegates the unchanged EXP-052 variant evidence to DEC-165 after removing only the feature-specific cutoff field.

That predecessor validation independently recomputes:

- budget availability;
- aggregate 0.5-pip financial gate;
- persisted aggregate-pass flag;
- four-window stability evidence;
- persisted stability result;
- final selection-pass flag.

No selection-window feature calibration, quota, rescue logic, or gate change is accepted.

## 8. Selected variant identity

The terminal no-challenger state is:

`NO_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_STABLE_MODEL_CHALLENGER`

It is valid only when no persisted variant passes both aggregate and stability gates and `selected_variant` is null.

A selected result must match exactly one stable persisted variant by:

- HGB-regression model family;
- budget anchor;
- feature-support cutoff;
- utility-support cutoff;
- pooled calibrated cutoff;
- raw cutoff.

Ambiguous or unmatched selection evidence fails closed.

## 9. Forward status chain

The exact chronology remains:

- no selection => validation and holdout locked;
- selected + validation reject => holdout locked;
- selected + validation pass => holdout must contain PASS or REJECT evidence.

Every unlocked forward block must prove:

- feature-support consensus and digest;
- the exact four-part cutoff;
- complete unchanged predecessor financial/scenario evidence.

DEC-176 renames the feature-support consensus into the predecessor consensus key only inside a defensive copy for DEC-165 validation; persisted EXP-053 evidence remains unchanged.

## 10. Cell fingerprints

Every cell result must carry a canonical result fingerprint.

DEC-176 recomputes SHA-256 over canonical JSON excluding only `result_fingerprint`.

Any mismatch rejects the cell.

## 11. Aggregate summary

The aggregate summary is recomputed from independently validated cells.

It records:

- verified cell count;
- selected cell count;
- no-stable-challenger cell count;
- aggregate-selection-pass variant count;
- stable-selection-pass variant count;
- unavailable-budget variant count;
- utility-eligible selection-row count;
- verified regressor count;
- verified pooled-calibration-reference count;
- verified fit-temporal utility-support-reference count;
- verified fit-temporal feature-support-reference count;
- validation-pass cell count;
- holdout-pass cell count.

A complete EXP-053 aggregate must contain exactly:

- 18 verified cells;
- 108 verified regressors;
- 108 verified pooled calibration references;
- 432 verified fit-temporal utility-support references;
- 216 verified fit-temporal feature-support references.

No supplied summary value is trusted without recomputation.

## 12. Aggregate fingerprint

The aggregate evidence binds:

- DEC-176 artifact-runner version and decision;
- EXP-053 experiment identity;
- exact code commit;
- DEC-174/175 merge and source identities;
- predecessor core/helper and loader identities;
- protocol and training-core identities;
- accepted historical feature/outcome/readiness identities;
- all 18 ordered cell results;
- recomputed summary;
- explicit false fit/promotion/trading locks.

The evidence fingerprint is canonical SHA-256 over the complete aggregate record excluding only the fingerprint field itself.

## 13. Authoritative bundle lock

The authoritative entry point first checks:

`AUTHORITATIVE_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED`

DEC-176 freezes that flag to `false`.

Calling the bundle while false raises before:

- source validation;
- readiness validation;
- historical feature/outcome loading;
- model fitting;
- result compilation.

## 14. Source identity

Artifact/evidence source:

`src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_artifacts.py`

Git blob:

`431c879bf26d88e33bdf0f0965ec62566b1a3e22`

Focused tests:

`tests/test_phase8a_exp053_fit_temporal_feature_support_utility_artifacts.py`

Git blob:

`6e442423d8d85467ff4f07b23584b0f04767b61f`

Artifact-runner version:

`fmp-exp053-fit-temporal-feature-support-utility-artifact-runner-v1`

Decision:

`DEC-176`

## 15. Authorization state

DEC-176 keeps false:

- authoritative EXP-053 historical result execution;
- authoritative EXP-053 model fit;
- workflow execution;
- replacement run;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 16. Next gate

A later separate decision may freeze a manual-main, input-free EXP-053 workflow, public CLI, pinned numerical runtime, and exact-source execution gate.

That workflow source must remain non-executable until terminal review and a separate one-run authorization are frozen in later decisions.
