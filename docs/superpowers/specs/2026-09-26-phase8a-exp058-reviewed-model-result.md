# Phase 8A — EXP-058 Reviewed Historical Model Result

**Date:** 2026-09-26
**Status:** REVIEWED RESULT / NO STABLE CHALLENGER
**Decision:** DEC-240
**Experiment:** EXP-20260925-058

## Historical attempt identity

The sole DEC-236-authorized EXP-058 historical workflow is:

- run id: `36207673978`
- workflow: `phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training`
- event: `workflow_dispatch`
- branch: `main`
- head SHA: `2339762cda013322c8704cee12218ec4f4fb8c36`
- run attempt: `1`
- conclusion: `success`

The DEC-239 executor completed successfully and submitted exactly this attempt. The first-run slot is consumed.

## DEC-235 terminal review

The successful attempt satisfies the predeclared DEC-235 success contract:

- authorization-preflight: success;
- nine matrix jobs: success;
- aggregate-model-evidence: success;
- nine expected cell artifacts: present and non-expired;
- aggregate artifact: present and non-expired.

Aggregate artifact:

- artifact id: `10895236824`
- artifact digest: `sha256:0e4efa5602410a58fa754dfcd44745d69f4e2905d6ce0dd2062030e791808c3a`

## Deterministic aggregate evidence

The reviewed aggregate evidence binds code commit:

`2339762cda013322c8704cee12218ec4f4fb8c36`

Evidence fingerprint:

`7e5019f0e00ada90a8f9c111d2b6fdb4ba41908f86a47203258b333439c8c8ee`

Independent canonical SHA-256 recomputation matches exactly.

Verified inventory:

- 18 model cells;
- 108 regressors;
- 108 pooled calibration references;
- 432 fit-temporal utility-support references;
- 216 fit-temporal feature-support references;
- 432 residual references;
- 12 residual-breadth bounds per eligible row;
- 12 residual lower-tail source bounds per eligible row;
- lower-tail count 3;
- 3 residual fit regimes;
- 4 residual windows per regime;
- 12 regime-floor source bounds per eligible row.

## Variant accounting

Across 54 budget variants:

- 28 are available;
- 26 are budget-unavailable;
- utility-eligible selection rows total `26,392`;
- 3 variants pass the aggregate selection gate;
- 0 variants pass temporal stability;
- 0 cells select a model;
- validation and retrospective holdout remain locked;
- accepted model candidate count is 0.

All 18 cells report:

`NO_FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_STABLE_MODEL_CHALLENGER`

## Aggregate-pass variants

Exactly three variants pass the aggregate gate:

- USDJPY / 5m / 60m / budget 250;
- USDJPY / 5m / 60m / budget 500;
- USDJPY / 5m / 60m / budget 1000.

Their four frozen selection-window directional candidate counts are:

- budget 250: `0 / 0 / 0 / 250`
- budget 500: `0 / 0 / 7 / 493`
- budget 1000: `0 / 3 / 72 / 925`

Each fails the unchanged temporal-stability gate. The regime-floor ranking therefore changes candidate concentration but still does not create selection-time temporal breadth.

## Result interpretation

DEC-240 records a successful historical model-result run with no stable challenger.

It does not authorize:

- rerun;
- retry;
- replacement model run;
- model fit beyond the consumed attempt;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Source identity

Reviewed-result source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_result_decision.py`

Git blob:

`f5a5f7e49b7088f4af9b35a9143e486c3fba3d1a`

Focused tests:

`tests/test_phase8a_exp058_model_result_decision.py`

Git blob:

`b07289e842649910eb2c098e23d3ce120365f511`

## Next safe gate

After DEC-240 is green and merged, the next safe gate is source-only post-result diagnostic analysis.

That diagnostic may compare EXP-058 with the nearest successful predecessor result and classify the remaining chronology failure. It may not reopen EXP-058 or authorize any execution or trading path.
