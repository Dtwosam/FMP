# Phase 8A — EXP-054 Reviewed Historical Model Result

**Date:** 2026-09-25
**Status:** REVIEWED RESULT SOURCE / NO STABLE CHALLENGER
**Decision:** DEC-196
**Experiment:** EXP-20260925-054

## Historical run identity

The sole DEC-191-authorized EXP-054 model workflow is:

- run id: `36152351767`
- workflow: `phase8a-exp054-fit-temporal-residual-bound-utility-model-training`
- event: `workflow_dispatch`
- branch: `main`
- head SHA: `5ca369a87f8a761c3232b75f95a701043721fd36`
- run attempt: `1`
- conclusion: `success`

All 11 DEC-190-required jobs completed successfully: one authorization preflight, nine pair/timeframe model-cell jobs, and one aggregate-model-evidence job.

## Artifact identity

All nine exact cell artifacts are present and non-expired.

The aggregate artifact is:

- artifact id: `10873466808`
- name: `exp054-fit-temporal-residual-bound-utility-model-result-evidence-5ca369a87f8a761c3232b75f95a701043721fd36-from-feature-35867307338-outcome-35876715434`
- digest: `sha256:d9adb29cb1bc4d9c6b2bbc65e80c168d90a7d0df909d0c1fb1377347b2ee223b`
- non-expired: true

The downloaded ZIP reproduces that SHA-256 digest exactly and contains exactly one `model-result-evidence.json`.

## Evidence validation

The aggregate evidence fingerprint is:

`307b576f06c6aa2fb01a267232a0de553bfa79c1bdbe6bf5d55b2bfc3b40787c`

It recomputes exactly under the frozen canonical serializer.

DEC-190 deterministic recompilation requirements are satisfied. Independent result-decision checks also verify all 18 cell fingerprints.

The complete evidence contains:

- 18 model cells
- 108 regressors
- 108 pooled calibration references
- 432 fit-temporal utility-support references
- 216 fit-temporal feature-support references
- 432 fit-temporal residual references
- 54 candidate-budget variants
- 28 available variants
- 26 unavailable variants
- 26,392 utility-eligible selection rows

## Selection result

EXP-054 produces exactly two aggregate-selection-pass variants:

- USDJPY / 5m / 60m / budget 250
- USDJPY / 5m / 60m / budget 1000

Neither clears the unchanged temporal-stability gate.

Therefore:

- aggregate-selection-pass variants: 2
- stable-selection-pass variants: 0
- selected cells: 0
- cells with no stable challenger: 18
- validation-pass cells: 0
- retrospective-holdout-pass cells: 0
- accepted model candidates: 0

Validation and retrospective holdout remain locked for all cells because no selection-period stable challenger exists.

## Closed authorizations

DEC-196 closes:

- model-run dispatch
- replacement model run
- authoritative model-result execution
- model-protocol result production
- model fit

It keeps false:

- promotion
- shadow execution
- demo orders
- broker mutation
- live orders
- real-money action
- trading

No second EXP-054 attempt is authorized.

## Source and tests

Reviewed-result source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_bound_utility_result_decision.py`

Git blob:

`17235435604bc5c0bd8950037bd8c49a0c6fb81a`

Focused tests:

`tests/test_phase8a_exp054_model_result_decision.py`

Git blob:

`4f773a996455f12652b653a29cf554dbb9a3401e`

## Next safe gate

The next safe gate is a separate post-result diagnostic over immutable EXP-053 and EXP-054 reviewed evidence. That diagnostic may explain why the residual-bound ranking reduced aggregate passes from EXP-053 while still failing temporal stability. It may not authorize a rerun, gate relaxation, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.
