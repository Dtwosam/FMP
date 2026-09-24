# Phase 8A — EXP-049 Artifact-Backed Evidence Contract

**Date:** 2026-09-24
**Status:** APPROVED SOURCE-ONLY / NON-EXECUTABLE
**Decision:** DEC-134
**Experiment:** EXP-20260924-049

## Purpose

DEC-134 freezes the artifact-backed result-evidence boundary for the DEC-132 / DEC-133 EXP-049 regime-utility successor.

It does not authorize an historical model fit or result-producing workflow.

The source exists so a later separately authorized run can load only the accepted feature/outcome/readiness artifacts, execute the exact DEC-133 core, and emit evidence that can be independently revalidated.

## Exact source binding

DEC-134 binds:

- DEC-132 merge: d17326eebf6b456211225d7bad3a182a0307b707
- DEC-132 protocol blob: ad2fcb22656fc7a1490f4cdf87fb25c62895a1ac
- DEC-133 merge: a6420e35a9219c81e65c5179843488f94b6668d3
- DEC-133 training-core blob: e1018b20210b7bb8d666071d8eb878aba5899111
- accepted historical data-loader blob: 27c0848d16722a22b4762f5842396c2aebc92bec
- frozen base training helper blob: 34b50a3f907d26b1c5ec50a0a0b444a3417d04f7
- frozen density/stability helper blob: 8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945

Source validation fails closed on any blob drift.

## Accepted historical inputs

A future authorized runner may consume only the already accepted feature, outcome, and readiness artifacts identified by the existing authoritative model-artifact contract.

No alternate file, regenerated dataset, manually substituted data, or new historical source is admitted by DEC-134.

## Exact 18-cell completeness

Result evidence must contain exactly the frozen 18 pair/timeframe/horizon cells.

Duplicate, missing, unsupported, or extra cell identities fail closed.

Every cell must preserve the exact processed-manifest SHA-256 and the four frozen outer split identities.

## Six-regressor fit inventory

Every cell must contain exactly:

- three fit regimes;
- two target regressors in each regime;
- six total regressors.

The target inventory is exactly:

- long_net_pips_0p5
- short_net_pips_0p5

Each regressor record must carry:

- FITTED status;
- one fit attempt;
- finite target summary;
- matching target row count;
- preprocessor fingerprint;
- model fingerprint.

Full-fit fallback, HGB-classifier fallback, and logistic fallback remain forbidden.

## Utility consensus validation

For every scored selection/forward block, DEC-134 validates:

- LONG / SHORT / NO_TRADE counts sum to row count;
- eligible count equals LONG + SHORT;
- eligible rate is exact;
- robust-utility bounds are absent when no row is eligible;
- otherwise robust-utility bounds are finite, strictly positive, and ordered;
- every regime exposes both target prediction digests;
- every digest is a valid SHA-256.

## Candidate-budget validation

The exact 250 / 500 / 1000 budgets remain required.

For an unavailable budget:

- status must be UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS;
- eligible count must be below the requested budget;
- no cutoff may exist;
- aggregate and final selection flags must be false;
- temporal stability must remain locked as BUDGET_UNAVAILABLE.

For an evaluated budget:

- eligible count must be at least the budget;
- selected-at-cutoff count must be at least the budget and no larger than eligible count;
- robust-utility cutoff must be finite and strictly positive;
- the realized 0.5-pip financial scenario must validate exactly.

All three variants must report the same utility-eligible selection-row count because the budget changes only the rank cutoff, not consensus eligibility.

## Aggregate financial gate

DEC-134 recomputes the exact aggregate gate from supplied metrics:

- directional candidate count at least 250;
- total net pips greater than zero;
- mean net pips greater than zero;
- gross positive pips greater than absolute gross negative pips.

The stored gate criteria and pass flag must exactly match the recomputed result.

## Temporal stability

Only aggregate passes may carry evaluated temporal-stability windows.

Exactly the four frozen half-year windows are required.

For every window, DEC-134 recomputes:

- candidate share using the full-selection candidate count denominator;
- the 10% share criterion;
- positive total net pips;
- positive mean net pips;
- gross-positive dominance.

Window criteria, pass flags, overall PASS/REJECT status, and the frozen share floor must all agree.

Aggregate rejects must keep stability locked with zero windows.

## Selection consistency

NO_REGIME_UTILITY_STABLE_MODEL_CHALLENGER is accepted only when no variant passes the complete aggregate + stability chain and selected_variant is null.

SELECTED is accepted only when at least one stable variant exists and the selected budget/cutoff uniquely matches a stable variant.

A no-challenger status cannot hide a stable variant.

## Forward-stage consistency

If no selection exists, validation and holdout must remain LOCKED_NO_SELECTION.

If validation rejects, holdout must remain LOCKED_VALIDATION_REJECT.

If validation passes, holdout must contain a realized PASS or REJECT result.

Any unlocked forward result must preserve:

- exact row count;
- regime-utility consensus accounting;
- consensus digest;
- frozen candidate budget;
- strictly positive selection-derived cutoff;
- exact diagnostic/gate scenario inventory;
- internally recomputable financial gates.

## Fingerprints

Each cell result fingerprint is independently recomputed from canonical JSON excluding only its supplied result_fingerprint field.

The aggregate evidence fingerprint is independently recomputed from canonical JSON excluding only its supplied evidence_fingerprint field.

Fingerprint mismatch fails closed.

## Aggregate summary

The evidence compiler records and revalidates:

- verified cell count;
- selected cell count;
- no-stable-challenger count;
- aggregate selection-pass variant count;
- stable selection-pass variant count;
- unavailable-budget variant count;
- total utility-eligible selection rows;
- verified regressor count;
- validation-pass cell count;
- holdout-pass cell count.

A complete 18-cell result contains exactly 108 verified regressors.

## Locked authoritative bundle

The artifact runner includes the future bundle path but checks AUTHORITATIVE_REGIME_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED before loading readiness or extracted historical artifacts.

Under DEC-134 this flag is false.

Therefore no authoritative historical EXP-049 fit can begin through this source.

## Source identity

Artifact/evidence source:

src/fmp/market_learning/model_successor_regime_utility_artifacts.py

Git blob:

6b3ec2fc8c6a8e6089d71e21d3243cea50a6fa13

Focused tests:

tests/test_phase8a_exp049_regime_utility_artifacts.py

Git blob:

0c7c746ee0e7365e5e4dd0fef96cc4c3eac7418a

Artifact runner version:

fmp-exp049-regime-utility-artifact-runner-v1

Decision:

DEC-134

## Authorization state

DEC-134 keeps false:

- authoritative EXP-049 model fit;
- authoritative EXP-049 result execution;
- workflow dispatch;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## Next gate

A later separate decision may freeze a manual-main EXP-049 workflow/CLI that binds the exact DEC-134 artifact source, pinned runtime, accepted artifact identities, and exact DEC-132 through DEC-134 source chain.

That workflow must remain non-dispatchable until terminal review and one-run authorization are separately predeclared.
