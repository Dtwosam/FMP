# Phase 8A — EXP-055 Reviewed Historical Model Result

**Date:** 2026-09-25
**Status:** REVIEWED RESULT SOURCE / NO STABLE CHALLENGER
**Decision:** DEC-207
**Experiment:** EXP-20260925-055

## Historical run identity

The sole DEC-203-authorized EXP-055 model workflow is:

- run id: `36163466744`
- workflow: `phase8a-exp055-fit-temporal-residual-breadth-utility-model-training`
- event: `workflow_dispatch`
- branch: `main`
- head SHA: `fa3f90709fa71f3b49f43985c505707da3c524af`
- run attempt: `1`
- conclusion: `success`

All 11 DEC-202-required jobs completed successfully: authorization preflight, all nine pair/timeframe model-cell jobs, and aggregate-model-evidence.

## Executor bookkeeping

DEC-206 executor run `36163408366` submitted the model workflow successfully, then failed only in its post-dispatch receipt parser because the captured receipt file was empty/non-JSON. That failure does not invalidate the submitted EXP-055 model run and does not authorize a second executor, rerun, retry, or replacement.

## Artifact identity

All nine exact cell artifacts are present and non-expired.

The aggregate artifact is:

- artifact id: `10878066267`
- name: `exp055-fit-temporal-residual-breadth-utility-model-result-evidence-fa3f90709fa71f3b49f43985c505707da3c524af-from-feature-35867307338-outcome-35876715434`
- digest: `sha256:146e07d58b7dbd1086bd2aec63abdfc50dcd4427f382ae576a27c4ac732c27ba`
- non-expired: true

The downloaded ZIP reproduces that SHA-256 digest exactly and contains exactly one `model-result-evidence.json`.

## Evidence validation

The aggregate evidence fingerprint is:

`f3a386dad7f23ac9d6867d030ac90e0884f3ab658c9ffecce8647048037d2510`

It recomputes exactly under the frozen canonical serializer.

All 18 cell fingerprints also recompute exactly.

The complete evidence contains:

- 18 model cells
- 108 regressors
- 108 pooled calibration references
- 432 fit-temporal utility-support references
- 216 fit-temporal feature-support references
- 432 fit-temporal residual references
- fixed residual-breadth lower-bound inventory: 12 bounds per eligible row
- 54 candidate-budget variants
- 28 available variants
- 26 unavailable variants
- 26,392 utility-eligible selection rows

## Selection result

EXP-055 produces exactly two aggregate-selection-pass variants:

- USDJPY / 5m / 60m / budget 250
- USDJPY / 5m / 60m / budget 1000

Neither clears the unchanged four-window temporal-stability gate.

Their directional-candidate counts across the frozen windows
`2021 H1 / 2021 H2 / 2022 H1 / 2022 H2` are:

- budget 250: `0 / 0 / 0 / 251`
- budget 1000: `0 / 1 / 83 / 916`

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

DEC-207 closes:

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

No second EXP-055 attempt is authorized.

## Source and tests

Reviewed-result source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_breadth_utility_result_decision.py`

Git blob:

`e2226117ebf10b762557d43549390c46c243bbae`

Focused tests:

`tests/test_phase8a_exp055_model_result_decision.py`

Git blob:

`f9910692694e651810e6feede8945488232d2933`

## Next safe gate

The next safe gate is a separate post-result diagnostic over immutable EXP-054 and EXP-055 reviewed evidence. That diagnostic may explain whether residual breadth changed concentration, candidate density, or financial-window shape, but it may not authorize a rerun, gate relaxation, selection-window tuning, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.
