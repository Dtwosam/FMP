# Phase 8A — EXP-056 Reviewed Failed Historical Result

**Date:** 2026-09-25
**Status:** REVIEWED FAILED ATTEMPT / NO MODEL RESULT
**Decision:** DEC-218
**Experiment:** EXP-20260925-056

## Historical attempt identity

The sole DEC-214-authorized EXP-056 historical model workflow is:

- run id: `36175841645`
- workflow: `phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training`
- event: `workflow_dispatch`
- branch: `main`
- head SHA: `3ce20d7445f6837cae067c0c561002215b05b2f9`
- run attempt: `1`
- conclusion: `failure`

The DEC-217 executor run `36175790573` completed successfully and submitted exactly this attempt. The first-run slot is therefore consumed.

## DEC-213 terminal review

The attempt satisfies the non-success branch of the predeclared DEC-213 terminal review:

- authorization-preflight: `success`
- nine matrix jobs: all `failure`
- aggregate-model-evidence: `skipped`
- persisted cell artifacts: `0`
- aggregate artifact present: `false`
- aggregate result evidence: not claimed
- replacement model run authorized: `false`

No model cell result survived to artifact persistence.

## Failure classification

DEC-218 classifies the attempt as:

`IMPLEMENTATION_DEPENDENCY_EXPORT_DRIFT_PREVENTED_ALL_EXP056_CELL_RESULTS`

The lower-tail training core delegates predecessor mechanics through:

`fmp.market_learning.model_successor_fit_temporal_residual_breadth_utility_training`

but dereferences constants that that predecessor module does not export.

Across the nine matrix jobs, the exact terminal AttributeError inventory is:

- eight jobs: missing `MIN_STABILITY_WINDOW_CANDIDATE_SHARE`
- one job: missing `FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL`

The exact affected matrix job ids are frozen in the DEC-218 result-decision source.

This is an implementation dependency/export defect. It is not a model-selection result, not an aggregate financial result, and not evidence that the EXP-056 lower-tail ranking passed or failed its intended gates.

## No result claim

EXP-056 produced:

- no persisted cell artifact;
- no aggregate artifact;
- no aggregate evidence fingerprint;
- no selected variant;
- no validation result;
- no retrospective-holdout result;
- no accepted model candidate.

Therefore DEC-218 records `model_result_produced = false`.

It does not synthesize, infer, or backfill any missing model evidence from EXP-054 or EXP-055.

## Closed authorizations

DEC-218 closes:

- model-run dispatch;
- replacement model run;
- authoritative model-result execution;
- model-protocol result production;
- model fit.

It keeps false:

- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

No second EXP-056 attempt is authorized.

## Source identity

Reviewed failed-result source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_result_decision.py`

Git blob:

`75fc25ae97c03730ab75a3036059f761d8234630`

Focused tests:

`tests/test_phase8a_exp056_failed_result_decision.py`

Git blob:

`9062d2aa990786e87cc6162e4c1f99b54bcc2d4a`

Predeclared terminal-review source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_result_review.py`

Git blob:

`0bfc50d39d04d82e95c731b7284c7be143191efd`

## Next safe gate

The next safe gate is a separate source-only implementation-defect diagnostic.

That diagnostic may identify the exact dependency-export repair required for a future successor experiment. It may not authorize an EXP-056 rerun, retry, replacement run, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.
