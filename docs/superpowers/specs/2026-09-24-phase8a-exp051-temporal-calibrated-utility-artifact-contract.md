# Phase 8A — EXP-051 Temporal-Calibrated Utility Artifact Contract

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-152
**Experiment:** EXP-20260924-051

## 1. Purpose

DEC-152 freezes the artifact-backed runner and aggregate evidence contract for EXP-051.

It binds the exact DEC-150 protocol, merged DEC-151 training core, accepted historical feature/outcome/readiness identities, the accepted historical artifact loader, and frozen generic financial/stability validation helpers.

This decision does **not** authorize historical fitting or result execution.

The authoritative bundle must reject before readiness validation or historical artifact loading while the DEC-152 outer execution lock is false.

## 2. Exact source binding

DEC-152 binds:

- DEC-150 merge: `b80a1f688afe8f5056aa31c1a2ff5b4ebbc11833`
- DEC-150 protocol blob: `c39309c4115cae1ea058e56f30cae4af6407e36e`
- DEC-151 merge: `68028ef37b72e3f0695b475928434ede40ad7690`
- DEC-151 training-core blob: `959fbfd52f41c08de3c1a26769e0e7fd2545b92a`
- predecessor EXP-050 training-core blob: `ec97a9941af052d6e223e4bafab9a9989ec57ff0`
- generic regime-utility artifact-helper blob: `6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13`
- accepted historical artifact-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

Any bound-byte drift fails closed.

## 3. Authoritative historical source identity

The contract reuses only the already accepted immutable historical market-learning artifacts.

Aggregate result evidence must carry the exact identities for:

- authoritative feature workflow run;
- feature evidence artifact and fingerprint;
- authoritative outcome workflow run;
- outcome evidence artifact and fingerprint;
- readiness artifact and readiness fingerprint.

No alternate local dataset, regenerated label set, ad hoc partition, or replacement history is accepted.

## 4. Cell completeness

A complete aggregate result requires exactly the frozen 18-cell universe:

- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h;
- 60m and 240m horizons.

Duplicate, missing, or unexpected identities fail closed.

Each cell must bind the accepted processed-manifest SHA-256 and retain positive row counts for fit, selection, validation, and retrospective holdout.

## 5. Jackknife fit evidence

Every cell must prove exactly three jackknife views with the exact included/excluded regime topology frozen by DEC-150.

Every view must contain:

- status `FITTED`;
- positive fit row count;
- exactly two regressors;
- exact LONG and SHORT 0.5-pip targets.

Every regressor must contain:

- one fit attempt;
- valid target summary and row accounting;
- deterministic preprocessor fingerprint;
- deterministic model fingerprint.

The complete aggregate must validate exactly:

- six regressors per cell;
- 108 regressors across 18 cells.

## 6. Out-of-fit calibration-reference evidence

Every cell must also contain exactly three view-level calibration records and exactly two target references per view.

That is:

- six calibration references per cell;
- 108 calibration references across the complete 18-cell aggregate.

Each view-level record must prove:

- status `FROZEN`;
- exact included-regime pair;
- exact excluded regime;
- positive excluded-regime row count;
- exactly two target references.

Each target reference must prove:

- status `FROZEN`;
- exact excluded-regime identity;
- row count equal to the containing view calibration row count;
- finite minimum, maximum, and mean predictions;
- minimum <= mean <= maximum;
- row-bound prediction SHA-256;
- sorted-reference SHA-256.

The contract validates the evidence shape and identities, not merely the declared total count.

## 7. Forbidden fallback evidence

The fit block must explicitly preserve:

- full-fit single model: `FORBIDDEN_BY_DEC150`;
- view-weight search: `FORBIDDEN_BY_DEC150`;
- view fallback: `FORBIDDEN_BY_DEC150`;
- selection-window calibration: `FORBIDDEN_BY_DEC150`;
- HGB classifier: `EXCLUDED_BY_DEC150`;
- logistic regression: `EXCLUDED_BY_DEC112_DEC150`.

Any altered fallback inventory fails closed.

## 8. Calibrated consensus evidence

Selection and every unlocked forward stage must carry a temporal-calibrated utility consensus block.

The contract validates:

- exact row count;
- LONG/SHORT/NO_TRADE counts;
- exact eligible count;
- exact eligible rate;
- positive finite raw robust-utility bounds when eligible rows exist;
- calibrated robust-utility bounds within [0, 1];
- ordered raw and calibrated bounds;
- all three view prediction digest sets;
- both LONG and SHORT prediction digests per view;
- row-bound calibrated-consensus fingerprint.

If no eligible rows exist, all raw and calibrated utility bounds must be null.

## 9. Budget availability and cutoff-pair evidence

The candidate-budget inventory remains exactly:

- 250;
- 500;
- 1000.

For an unavailable variant, the contract requires:

- status `UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS`;
- eligible count below the requested budget;
- null calibrated cutoff;
- null raw cutoff;
- aggregate-pass false;
- final-pass false;
- stability status `BUDGET_UNAVAILABLE`;
- no stability windows.

For an available variant, the contract requires:

- status `AVAILABLE`;
- eligible count at least the budget;
- selected-at-cutoff count between budget and eligible count;
- calibrated cutoff finite and within [0, 1];
- raw cutoff finite and greater than zero;
- exactly the unchanged 0.5-pip selection scenario;
- independently revalidated financial gate.

Exact calibrated/raw score-pair ties may make the selected-at-cutoff count larger than the nominal budget.

## 10. Temporal stability

Only aggregate financial passes may expose temporal-stability evidence.

The contract revalidates the exact four half-year windows using the frozen helper:

- window identity;
- candidate count;
- candidate share relative to the full-selection candidate count;
- 10% share floor;
- positive total net pips;
- positive mean net pips;
- positive-vs-negative gross-pip sign requirement;
- exact persisted pass/fail flag.

Aggregate rejects must keep stability locked with no window evidence.

No per-window threshold, quota, calibration rebuild, or rescue interpretation is accepted.

## 11. Selection identity

The terminal no-challenger state is:

`NO_TEMPORAL_CALIBRATED_UTILITY_STABLE_MODEL_CHALLENGER`

That state is valid only when:

- no variant passes both aggregate and temporal stability;
- selected variant is null.

A selected result must correspond to exactly one stable persisted variant by:

- HGB-regression family;
- budget anchor;
- calibrated cutoff;
- raw cutoff.

A selected record that cannot be matched uniquely fails closed.

## 12. Forward status chain

The contract preserves the exact chronology:

- no selection => validation and holdout locked;
- selected + validation reject => holdout locked;
- selected + validation pass => holdout must contain PASS or REJECT evidence.

Every unlocked forward block must reuse:

- temporal-calibrated consensus evidence;
- exact candidate budget;
- exact calibrated cutoff;
- exact raw cutoff;
- complete diagnostic/gate scenario inventory;
- independently recomputed financial gates.

No forward recalibration field is accepted as a substitute for the frozen cutoff pair.

## 13. Cell fingerprints

Every cell result must carry a canonical result fingerprint.

The contract independently recomputes SHA-256 over canonical JSON excluding only `result_fingerprint`.

Any mismatch rejects the cell before aggregate acceptance.

## 14. Aggregate summary

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
- verified calibration-reference count;
- validation-pass cell count;
- holdout-pass cell count.

A complete EXP-051 aggregate must contain exactly:

- 18 verified cells;
- 108 verified regressors;
- 108 verified calibration references.

No supplied summary value is trusted without recomputation.

## 15. Aggregate fingerprint

The aggregate evidence binds:

- artifact-runner version and DEC-152;
- EXP-051 experiment identity;
- exact code commit;
- DEC-150/DEC-151 merge and source identities;
- frozen helper/loader identities;
- protocol and training-core identities;
- authoritative historical source identities;
- all 18 ordered cell results;
- recomputed summary;
- explicit false fit/promotion/trading locks.

The evidence fingerprint is canonical SHA-256 over the complete aggregate record excluding only the fingerprint field itself.

## 16. Authoritative bundle lock

The authoritative entry point first checks:

`AUTHORITATIVE_TEMPORAL_CALIBRATED_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED`

DEC-152 freezes that flag to `false`.

Calling the bundle while false raises before:

- source validation;
- readiness validation;
- historical feature/outcome loading;
- model fitting;
- result compilation.

This keeps the artifact contract source-complete but non-executable.

## 17. Source identity

Artifact/evidence source:

`src/fmp/market_learning/model_successor_temporal_calibrated_utility_artifacts.py`

Git blob:

`3b25ad8dee80ad2d68a421b01b3e7789b1de9f1a`

Focused tests:

`tests/test_phase8a_exp051_temporal_calibrated_utility_artifacts.py`

Git blob:

`1c0bec0b6f337266d97fc3b79efa1afdab60e8b1`

Artifact-runner version:

`fmp-exp051-temporal-calibrated-utility-artifact-runner-v1`

Decision:

`DEC-152`

## 18. Authorization state

DEC-152 keeps false:

- authoritative EXP-051 historical result execution;
- authoritative EXP-051 model fit;
- workflow execution;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 19. Next gate

A later separate decision may freeze a manual-main, input-free EXP-051 workflow, public CLI, pinned numerical runtime, and exact-source execution gate.

That workflow source must remain non-executable until terminal review and a separate one-run authorization are frozen in later decisions.
