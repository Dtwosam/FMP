# Phase 8A — EXP-060 Reviewed Historical Model Result

**Date:** 2026-09-26
**Status:** REVIEWED RESULT / NO STABLE CHALLENGER
**Decision:** DEC-262
**Experiment:** EXP-20260926-060

## Historical attempt identity

The sole DEC-258-authorized EXP-060 historical workflow is:

- run id: `36260155597`
- workflow: `phase8a-exp060-fit-temporal-residual-regime-balance-utility-model-training`
- event: `workflow_dispatch`
- branch: `main`
- head SHA: `0062546fda38bfc768122cf03b9a4d69d1b8e0b7`
- run attempt: `1`
- conclusion: `success`

DEC-261 executor run `36260093042` completed successfully and submitted exactly this attempt. Its immutable execution-evidence artifact is `10911873209` with digest `sha256:742e01aca58ab397ef5d48dd50a5392e8cd89548d0a6fb6b28ef5207a3dc6307`. The one permitted EXP-060 historical slot is consumed.

## DEC-257 terminal review

The successful attempt satisfies the predeclared DEC-257 success contract:

- authorization-preflight: success;
- nine pair/timeframe matrix jobs: success;
- aggregate-model-evidence: success;
- nine expected cell artifacts: present and non-expired;
- aggregate artifact: present and non-expired.

Aggregate artifact:

- artifact id: `10912798284`
- artifact name: `exp060-fit-temporal-residual-regime-balance-utility-model-result-evidence-0062546fda38bfc768122cf03b9a4d69d1b8e0b7-from-feature-35867307338-outcome-35876715434`
- artifact digest: `sha256:9090a1a1c7849c703eaa38e5571a36a65f5a47f250c6c0e3a7e21777367b8bc9`

The downloaded ZIP SHA-256 independently matches the GitHub artifact digest exactly.

## Deterministic aggregate evidence

The reviewed aggregate evidence binds code commit:

`0062546fda38bfc768122cf03b9a4d69d1b8e0b7`

Evidence fingerprint:

`52a840d0919992e1fe9ef3342ddefe46cfb1ad8ccd23c8dfe55963d4c1669b37`

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
- 12 regime-floor source bounds per eligible row;
- 3 regime-balance source regimes;
- 12 regime-balance source bounds per eligible row;
- regime-balance penalty multiplier 1.0.

## Variant accounting

Across 54 budget variants:

- 28 are available;
- 26 are budget-unavailable;
- utility-eligible selection rows total `26,392`;
- 2 variants pass the aggregate selection gate;
- 0 variants pass temporal stability;
- 0 cells select a model;
- validation and retrospective holdout remain locked;
- accepted model candidate count is 0.

All 18 cells report:

`NO_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_STABLE_MODEL_CHALLENGER`

## Aggregate-pass variants

Exactly two variants pass the aggregate gate:

- USDJPY / 5m / 60m / budget 500;
- USDJPY / 5m / 60m / budget 1000.

Their four frozen selection-window directional candidate counts are:

- budget 500: `0 / 0 / 27 / 473`;
- budget 1000: `0 / 3 / 105 / 892`.

Both fail the unchanged temporal-stability gate. The regime-balance repair changes candidate concentration relative to earlier experiments but does not create selection-time temporal breadth.

## Result interpretation

DEC-262 records a technically successful, fully evidenced historical model-result run with no stable challenger.

This is a valid negative research result, not a technical failure. The repaired EXP-060 implementation completed its intended protocol, and the frozen selection rules rejected every cell before validation or retrospective holdout.

DEC-262 does not authorize:

- rerun;
- retry;
- replacement model run;
- additional EXP-060 model fitting;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Source identity

Reviewed-result source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_result_decision.py`

Git blob:

`2684419f983a04d1771443126104a8e7059cc03b`

Focused tests:

`tests/test_phase8a_exp060_model_result_decision.py`

Git blob:

`dd6eb6424a97d9f743df0ff0bf8790d4505372b6`

Predeclared terminal-review source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_balance_utility_repair_result_review.py`

Git blob:

`989ebc7b0cc33e5076f83ea94337fe6581c321e3`

## Next safe gate

After DEC-262 is green and merged, the next safe gate is a source-only Phase 8A post-result assessment. It may classify what the EXP-060 negative result means for the direct market-learning track and the Phase 8A acceptance gate. It may not reopen EXP-060, invent a replacement attempt, or authorize Phase 8B, demo, broker, live-order, real-money, or trading behavior.
