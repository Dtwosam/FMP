# Phase 8A — EXP-059 Reviewed Failed Historical Result

**Date:** 2026-09-26
**Status:** REVIEWED FAILED ATTEMPT / NO MODEL RESULT
**Decision:** DEC-251
**Experiment:** EXP-20260926-059

## Historical attempt identity

The sole DEC-247-authorized EXP-059 historical model workflow is:

- run id: `36239443323`
- workflow: `phase8a-exp059-fit-temporal-residual-regime-balance-utility-model-training`
- event: `workflow_dispatch`
- branch: `main`
- head SHA: `8b47a025598feea1b9a382c4f0c35ac644512acc`
- run attempt: `1`
- conclusion: `failure`

The DEC-250 executor completed successfully and submitted exactly this attempt. The first-run slot is therefore consumed.

## DEC-246 terminal review

The attempt satisfies the non-success branch of the predeclared DEC-246 terminal review:

- authorization-preflight: `success`
- nine matrix jobs: all `failure`
- aggregate-model-evidence: `skipped`
- persisted cell artifacts: `0`
- aggregate artifact present: `false`
- aggregate result evidence: not claimed
- replacement model run authorized: `false`

No model-cell result survived to artifact persistence.

## Failure classification

DEC-251 classifies the attempt as:

`IMPLEMENTATION_DEPENDENCY_EXPORT_DEPTH_DRIFT_PREVENTED_ALL_EXP059_CELL_RESULTS`

All nine matrix jobs terminate with the same AttributeError:

`model_successor_fit_temporal_residual_lower_tail_utility_repair_training` has no exported `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE`.

The runtime suggestion names `FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_RULE`, but DEC-251 does not substitute that symbol. The historical source explicitly intended the breadth rule and addressed it through an intermediate predecessor depth that does not export it.

This is an implementation dependency/export-depth defect. It is not a model-selection result, aggregate financial result, or evidence that the EXP-059 regime-balance ranking passed or failed its intended gates.

## No result claim

EXP-059 produced:

- no persisted cell artifact;
- no aggregate artifact;
- no aggregate evidence fingerprint;
- no selected variant;
- no validation result;
- no retrospective-holdout result;
- no accepted model candidate.

DEC-251 records `model_result_produced = false` and does not infer or backfill evidence from predecessor experiments.

## Closed authorizations

DEC-251 closes:

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

No second EXP-059 attempt is authorized.

## Source identity

Reviewed failed-result source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_result_decision.py`

Git blob:

`c8ca7143e687494b81205556af7e317ec69937fd`

Focused tests:

`tests/test_phase8a_exp059_failed_result_decision.py`

Git blob:

`4b10d137160c7fcbc6b570940db7b2cccfd6b6e7`

Predeclared terminal-review source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_result_review.py`

Git blob:

`5adc6ad72b2dfab1de1cca09a9bb2bc09663bfc5`

## Next safe gate

The next safe gate is a separate source-only implementation-defect diagnostic.

That diagnostic may identify the exact predecessor-depth repair required for a future successor experiment. It may not authorize an EXP-059 rerun, retry, replacement run, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.
