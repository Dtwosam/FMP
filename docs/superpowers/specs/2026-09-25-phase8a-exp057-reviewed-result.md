# Phase 8A — EXP-057 Reviewed Historical Result

**Date:** 2026-09-25
**Status:** REVIEWED SUCCESSFUL RUN / NO STABLE MODEL CHALLENGER
**Decision:** DEC-229
**Experiment:** EXP-20260925-057

## Historical attempt identity

The sole DEC-225-authorized EXP-057 historical model workflow is:

- run id: `36192572271`
- workflow: `phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training`
- event: `workflow_dispatch`
- branch: `main`
- head SHA: `491a2e2715b4da7013737ecaebc65a58ac3417f9`
- run attempt: `1`
- conclusion: `success`

DEC-228 merged at the same head SHA and its one-shot executor completed successfully before submitting this run. The DEC-225 historical slot is consumed.

## DEC-224 terminal review

The run satisfies the successful branch of the predeclared DEC-224 terminal review:

- exactly 11 completed successful workflow jobs;
- exactly nine non-expired pair/timeframe cell artifacts;
- exactly one non-expired aggregate result artifact;
- complete deterministic recompilation under the DEC-222 artifact contract;
- no replacement run authorized.

Reviewed aggregate artifact:

- artifact id: `10890155292`
- artifact name: `exp057-fit-temporal-residual-lower-tail-utility-model-result-evidence-491a2e2715b4da7013737ecaebc65a58ac3417f9-from-feature-35867307338-outcome-35876715434`
- artifact digest: `sha256:6aeeb1efa22bc515907f05c2c48bc234da2bc3d40a44117f1c0fb1d3824de3fe`
- evidence fingerprint: `4bf67108e0df38d4f213d08898fadd338285ac7a2ce56920b61e4dba0f3eec4c`

## Verified evidence

DEC-229 revalidates:

- 18 cells;
- 108 regressors;
- 108 pooled calibration references;
- 432 utility-support references;
- 216 feature-support references;
- 432 residual references;
- 12 residual-breadth bounds per eligible row;
- 12 residual lower-tail source bounds per eligible row;
- fixed lower-tail count 3;
- 54 total budget variants;
- 28 available variants;
- 26 unavailable variants;
- 26,392 utility-eligible selection rows.

## Selection outcome

Exactly three variants pass the aggregate selection gate:

- USDJPY / 5m / 60m / budget 250;
- USDJPY / 5m / 60m / budget 500;
- USDJPY / 5m / 60m / budget 1000.

Their four frozen temporal-window candidate counts are:

- budget 250: `0 / 0 / 0 / 250`
- budget 500: `0 / 0 / 3 / 497`
- budget 1000: `0 / 1 / 73 / 926`

All three fail the unchanged temporal-stability gate.

Therefore:

- stable selection-pass variants: `0`;
- selected cells: `0`;
- cells reporting no stable challenger: `18`;
- validation-pass cells: `0`;
- retrospective-holdout-pass cells: `0`;
- accepted model candidates: `0`.

No validation or holdout stage opens because no cell reaches stable selection.

## Result interpretation

The EXP-057 implementation repair succeeded operationally: the repaired source completed all 18 cells and the aggregate evidence contract without the dependency-export failures that stopped EXP-056.

The model-selection outcome remains negative. The repaired lower-tail ranking broadens the aggregate-pass inventory to include budget 500, but no aggregate-pass variant clears temporal stability.

DEC-229 therefore records:

`FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`

This is a reviewed historical result, not a promotion decision.

## Closed authorizations

DEC-229 closes:

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

No second EXP-057 attempt is authorized.

## Source identity

Reviewed result-decision source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_result_decision.py`

Git blob:

`185e2cdf089cb6f1a12619af58fd32860366498f`

Focused tests:

`tests/test_phase8a_exp057_model_result_decision.py`

Git blob:

`a1fd0bdd1a8ce87538460351630053efabda6ce3`

Predeclared terminal-review source remains:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_result_review.py`

Git blob:

`1a5f3e86b4d445ba4a77f3496f81de2b16b333cd`

## Next safe gate

After DEC-229 is green and merged, the next safe gate is post-result diagnostic analysis only.

That diagnostic may compare EXP-057 against immutable predecessor evidence to determine what changed in aggregate-pass breadth and temporal concentration. It may not authorize a rerun/retry/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.
