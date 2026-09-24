# Phase 8A — EXP-050 Temporal-Jackknife Utility Artifact Contract

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-143
**Experiment:** EXP-20260924-050

## 1. Purpose

DEC-143 freezes the artifact-backed runner and aggregate evidence contract for EXP-050.

It binds the exact DEC-141 protocol, merged DEC-142 training core, accepted historical feature/outcome/readiness identities, the accepted historical artifact loader, and the generic financial/stability validation helpers inherited from DEC-134 under an exact helper-blob binding.

This decision does **not** authorize historical fitting or result execution.

The authoritative bundle must reject execution before readiness or historical artifact loading unless a later decision explicitly opens the outer execution lock.

## 2. Exact source binding

DEC-143 binds:

- DEC-141 merge: `4729da0e769f76f44b97ff6349ee25c5b7c0f5c7`
- DEC-141 protocol blob: `b41b817b03aa0cc03a9d893227caa399b46d3cf8`
- DEC-142 merge: `fa6fd14a880a84a44795efe4099679ed0f642497`
- DEC-142 training-core blob: `ec97a9941af052d6e223e4bafab9a9989ec57ff0`
- predecessor EXP-049 training-core blob: `e1018b20210b7bb8d666071d8eb878aba5899111`
- predecessor DEC-134 artifact-helper blob: `6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13`
- accepted historical artifact loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

Any bound-byte drift fails closed.

## 3. Authoritative historical source identity

The contract reuses the already accepted immutable historical feature, outcome, and readiness artifacts.

Aggregate evidence must carry the exact authoritative identities for:

- feature workflow run and feature evidence artifact/fingerprint;
- outcome workflow run and outcome evidence artifact/fingerprint;
- readiness artifact and readiness fingerprint.

No alternate historical source, ad hoc file, regenerated label set, or hidden local dataset is accepted.

## 4. Cell completeness

A complete aggregate result must contain exactly all 18 frozen model cells:

- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h;
- 60m and 240m horizons.

Duplicate, missing, or unexpected cell identities fail closed.

## 5. Jackknife fit evidence

Every cell must prove exactly three jackknife view fits:

- `leave_out_fit_2015_2016`
- `leave_out_fit_2017_2018`
- `leave_out_fit_2019_2020`

For each view, evidence must include the exact included-regime pair and exact excluded regime declared by DEC-141.

Every view must report:

- status `FITTED`;
- positive row count;
- exactly two regressors;
- exact LONG and SHORT 0.5-pip targets.

Each regressor must report:

- one fit attempt;
- finite target summary;
- row-count-consistent positive/negative/zero accounting;
- deterministic preprocessor fingerprint;
- deterministic model fingerprint.

The total verified regressor count is exactly six per cell and 108 across the complete 18-cell result.

Full-fit fallback, view-weight search, view fallback, HGB classifier fallback, and logistic fallback must all remain explicitly forbidden/excluded.

## 6. View prediction evidence

Selection and any unlocked forward stage must contain a complete temporal-jackknife utility consensus block.

The contract independently validates:

- row count;
- LONG/SHORT/NO_TRADE counts;
- eligible row count and exact eligible rate;
- positive robust-utility bounds when eligible rows exist;
- all three view names;
- both target prediction digests per view;
- the row-bound consensus digest.

A missing view digest or target digest fails closed.

## 7. Budget and realized financial evidence

The candidate budgets remain exactly:

- 250
- 500
- 1000

For every variant the contract validates:

- utility-eligible row accounting;
- budget-unavailable semantics when eligible rows are insufficient;
- positive finite robust-utility cutoff when available;
- deterministic tie-expanded candidate count;
- exact 0.5-pip aggregate realized financial metrics and gate recomputation.

The unchanged generic DEC-134 variant/financial validator is reused under an exact artifact-helper blob binding.

## 8. Temporal stability

Only aggregate passes may expose temporal-stability windows.

The exact four half-year windows and exact 10% candidate-share plus financial-sign criteria remain unchanged.

The contract independently recomputes window pass/fail semantics from persisted metrics through the frozen helper implementation.

No aggregate reject may claim unlocked stability evidence.

## 9. Selection and forward stages

The no-challenger terminal selection status is:

`NO_TEMPORAL_JACKKNIFE_UTILITY_STABLE_MODEL_CHALLENGER`

That status is valid only when no stable variant exists and no selected variant is present.

If a variant is selected, it must uniquely correspond to one stable persisted variant by model family, budget anchor, and exact cutoff.

Validation and retrospective holdout must obey the same frozen status chain:

- no selection => both locked;
- validation reject => holdout locked;
- validation pass => holdout must produce PASS or REJECT evidence.

Any unlocked forward block must use the temporal-jackknife consensus evidence, exact selection-derived cutoff, and complete frozen gate/diagnostic scenario inventory.

## 10. Cell and aggregate fingerprints

Every cell result fingerprint is independently recomputed from canonical JSON excluding only the fingerprint field itself.

Aggregate evidence includes:

- experiment/protocol/training/artifact-runner identities;
- exact source blobs and merge identities;
- authoritative historical source identity;
- all 18 ordered cell results;
- compiled summary;
- explicit execution/promotion/trading locks.

The aggregate evidence fingerprint is independently recomputed from canonical JSON.

## 11. Aggregate summary

The aggregate contract records:

- verified cell count;
- selected cell count;
- no-stable-challenger cell count;
- aggregate-selection-pass variant count;
- stable-selection-pass variant count;
- unavailable-budget variant count;
- utility-eligible selection-row count;
- verified regressor count;
- validation-pass cell count;
- holdout-pass cell count.

No summary value is trusted without recomputing it from validated cell evidence.

## 12. Authoritative bundle lock

The authoritative bundle entry point first checks:

`AUTHORITATIVE_TEMPORAL_JACKKNIFE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED`

DEC-143 freezes that flag to `false`.

A call while false raises before:

- readiness validation;
- historical feature/outcome loading;
- model fitting;
- aggregate result production.

Thus the artifact contract is source-complete but non-executable.

## 13. Source identity

Artifact/evidence source:

`src/fmp/market_learning/model_successor_temporal_jackknife_utility_artifacts.py`

Git blob:

`60076ccb45b3468bce68f88f667225e0b5662d92`

Focused tests:

`tests/test_phase8a_exp050_temporal_jackknife_utility_artifacts.py`

Git blob:

`2247d07528cf20ed1d57f41305da83cbac648e7a`

Artifact-runner version:

`fmp-exp050-temporal-jackknife-utility-artifact-runner-v1`

Decision:

`DEC-143`

## 14. Authorization state

DEC-143 keeps false:

- authoritative EXP-050 result execution;
- authoritative EXP-050 model fit;
- workflow execution;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 15. Next gate

A later separate decision may freeze a manual-main, input-free EXP-050 workflow, CLI, pinned runtime, and exact-source execution gate while keeping dispatch/result/fit authorization closed.

Terminal review must still be predeclared separately before any one-run authorization.
