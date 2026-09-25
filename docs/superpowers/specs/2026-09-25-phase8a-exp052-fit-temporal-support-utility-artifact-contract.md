# Phase 8A — EXP-052 Fit-Temporal-Support Artifact Contract

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-165
**Experiment:** EXP-20260925-052

## 1. Purpose

DEC-165 freezes the artifact-backed runner and aggregate evidence contract for EXP-052.

It binds the exact DEC-163 protocol, merged DEC-164 training core, accepted historical feature/outcome/readiness identities, the accepted historical artifact loader, and the frozen generic financial/stability validation helpers.

This source remains non-executable for authoritative historical fitting.

## 2. Exact source binding

DEC-165 binds:

- DEC-163 merged commit: `9108cd170b2eccf73bddb6cbf8d6d7118dbd9cd1`;
- DEC-163 protocol blob: `01d5080560ec5d41653694b4df086ff2f10e770d`;
- DEC-164 merged commit: `d9f893504b2d790eb73bc49edf4c0919ef2ff914`;
- DEC-164 training-core blob: `fe5664438752a161134bbed6f55d9985f1c1470a`;
- predecessor DEC-151 training-core blob: `959fbfd52f41c08de3c1a26769e0e7fd2545b92a`;
- accepted historical artifact-loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`;
- generic financial/stability artifact-helper blob: `6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13`.

Any direct source drift fails closed.

## 3. Complete cell inventory

A complete aggregate result requires exactly the frozen 18-cell universe:

- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h;
- 60m and 240m horizons.

Duplicate, missing, or unexpected cells fail closed.

Every cell must retain a valid processed-manifest SHA-256 and positive row counts for fit, selection, validation, and retrospective holdout.

## 4. Six-regressor fit evidence

Each cell must contain exactly the three frozen jackknife views and exactly two HGB utility regressors per view.

The contract validates:

- exact included/excluded fit regimes;
- fit status;
- positive fit row count;
- LONG and SHORT 0.5-pip target identity;
- one fit attempt per regressor;
- target-summary row accounting;
- preprocessor fingerprint;
- model fingerprint.

A complete 18-cell aggregate must verify exactly 108 regressors.

## 5. Six pooled EXP-051 references per cell

DEC-165 preserves and validates the existing pooled calibration layer.

For each of the three views:

- exact included/excluded regime identity;
- one pooled reference for LONG;
- one pooled reference for SHORT;
- finite minimum/maximum/mean prediction;
- ordered bounds;
- row-bound prediction digest;
- sorted-reference digest.

The complete aggregate must verify:

- 6 pooled references per cell;
- 108 pooled references across 18 cells.

## 6. Twenty-four fit-temporal support references per cell

DEC-165 independently validates the new DEC-164 support layer.

Each view's excluded two-year fit regime must expose exactly its four frozen half-year windows.

For every view, target, and support window, the evidence must preserve:

- exact support-window name;
- exact parent regime;
- exact start;
- exact end-exclusive;
- positive row count;
- `FROZEN` status;
- finite minimum/maximum/mean prediction;
- ordered prediction bounds;
- row-bound prediction digest;
- sorted-reference digest.

Per cell:

- 3 views;
- 2 targets;
- 4 half-year windows;
- 24 support references.

Across the complete 18-cell aggregate:

- exactly 432 support references.

The validator checks each reference shape and identity rather than trusting the declared total.

## 7. Forbidden fallback inventory

Each fit block must explicitly preserve:

- full-fit single model: `FORBIDDEN_BY_DEC150_DEC163`;
- view-weight search: `FORBIDDEN_BY_DEC150_DEC163`;
- view fallback: `FORBIDDEN_BY_DEC150_DEC163`;
- selection-window calibration: `FORBIDDEN_BY_DEC150_DEC163`;
- HGB classifier: `EXCLUDED_BY_DEC150_DEC163`;
- logistic regression: `EXCLUDED_BY_DEC112_DEC150_DEC163`.

Any altered status or non-zero attempt count fails closed.

## 8. Support consensus evidence

Selection and every unlocked forward stage must include the EXP-052 consensus block.

The contract validates:

- exact row count;
- LONG / SHORT / NO_TRADE counts;
- eligible row count and rate;
- positive finite raw utility bounds;
- pooled calibrated utility bounds inside [0, 1];
- fit-temporal-support bounds inside [0, 1];
- all three view prediction digest sets;
- LONG and SHORT prediction digests per view;
- row-bound consensus digest.

If no eligible row exists, all raw/pooled/support bounds must be null.

## 9. Candidate budgets and cutoff triple

The budget inventory remains exactly:

- 250;
- 500;
- 1000.

Unavailable budgets must prove:

- fewer eligible rows than the budget;
- null support cutoff;
- null pooled cutoff;
- null raw cutoff;
- aggregate pass false;
- final selection pass false;
- stability state `BUDGET_UNAVAILABLE`.

Available budgets must prove:

- eligible count at least the budget;
- selected-at-cutoff count from budget through eligible count;
- support cutoff inside [0, 1];
- pooled cutoff inside [0, 1];
- positive finite raw cutoff;
- exact 0.5-pip selection scenario;
- independently revalidated financial gate.

Exact support/pooled/raw ties may exceed the nominal budget.

## 10. Unchanged temporal stability

Only aggregate financial passes may expose stability-window evidence.

The contract independently revalidates the same four frozen selection windows using the same helper and requires:

- exact window identities;
- 10% directional-candidate-share floor;
- positive total net pips;
- positive mean net pips;
- gross positive pips greater than absolute gross negative pips;
- exact persisted gate result.

Aggregate rejects must keep temporal stability locked with no windows.

## 11. Selection and forward chronology

The no-challenger state is:

`NO_FIT_TEMPORAL_SUPPORT_UTILITY_STABLE_MODEL_CHALLENGER`

It is valid only when no variant passes both aggregate and temporal stability and selected variant is null.

A selected variant must uniquely match one stable persisted variant by:

- HGB-regression family;
- budget;
- support cutoff;
- pooled cutoff;
- raw cutoff.

Forward chronology remains:

- no selection => validation and holdout locked;
- validation reject => holdout locked;
- validation pass => holdout contains PASS or REJECT evidence.

Every unlocked forward stage must reuse the exact cutoff triple and full diagnostic/gate scenario inventory.

## 12. Canonical fingerprints

Each cell retains its canonical result fingerprint.

DEC-165 independently recomputes SHA-256 over canonical JSON excluding only `result_fingerprint`.

The aggregate evidence similarly recomputes its canonical evidence fingerprint excluding only `evidence_fingerprint`.

Any mismatch fails closed.

## 13. Aggregate summary

The aggregate summary is recomputed from validated cells and records:

- verified cell count;
- selected cell count;
- no-stable-challenger cell count;
- aggregate-selection-pass variant count;
- stable-selection-pass variant count;
- unavailable-budget variant count;
- utility-eligible selection-row count;
- verified regressor count;
- verified pooled-reference count;
- verified support-reference count;
- validation-pass cell count;
- holdout-pass cell count.

A complete EXP-052 aggregate must contain exactly:

- 18 verified cells;
- 108 verified regressors;
- 108 verified pooled references;
- 432 verified fit-temporal-support references.

## 14. Authoritative historical source identity

The aggregate evidence must bind the already accepted immutable:

- feature workflow run / artifact / fingerprint;
- outcome workflow run / artifact / fingerprint;
- readiness artifact / fingerprint.

No alternate local dataset or replacement history is accepted.

## 15. Authoritative bundle lock

The artifact-backed entry point first checks:

`AUTHORITATIVE_FIT_TEMPORAL_SUPPORT_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED`

DEC-165 freezes it to `false`.

Calling the authoritative bundle while false raises before:

- source validation;
- readiness validation;
- feature/outcome artifact loading;
- model fitting;
- aggregate compilation.

## 16. Frozen implementation

Artifact/evidence source:

`src/fmp/market_learning/model_successor_fit_temporal_support_utility_artifacts.py`

Git blob:

`ae06184b9a84405119b6ed434a8973139d8ae006`

Focused tests:

`tests/test_phase8a_exp052_fit_temporal_support_utility_artifacts.py`

Git blob:

`90de05fd9f74930d9c04c0432d4f6ca0fd4241ef`

Artifact-runner version:

`fmp-exp052-fit-temporal-support-utility-artifact-runner-v1`

Decision:

`DEC-165`

## 17. Authorization state

DEC-165 keeps false:

- authoritative EXP-052 result execution;
- authoritative EXP-052 model fit;
- workflow dispatch;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 18. Next gate

A later separate decision may freeze a manual-main, input-free EXP-052 workflow, public CLI, pinned numerical runtime, and exact-source execution gate against the exact DEC-163/164/165 sources.

That workflow source must remain non-executable until terminal review and a later single-run authorization chain are separately frozen.
