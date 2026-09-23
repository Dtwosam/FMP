# Phase 8A — EXP-045 Deterministic Successor Training Core

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 HISTORICAL MODEL RESULT
**Decision:** DEC-096
**Experiment:** EXP-20260923-045

## 1. Purpose

DEC-095 froze the post-result-informed EXP-045 successor model protocol after DEC-094 closed EXP-044 V1.

DEC-096 implements the deterministic in-memory training/evaluation core for that exact successor protocol.

It is source-only.

DEC-096 does not create:

- a historical artifact-backed runner;
- a result-producing CLI;
- a GitHub Actions model-training workflow;
- an operator dispatch state;
- a model-fit authorization;
- promotion or trading authorization.

Synthetic unit-test fits are allowed only to validate source behavior.

## 2. Frozen source dependencies

DEC-096 binds the unchanged closed EXP-044 base training-core Git blob:

`34b50a3f907d26b1c5ec50a0a0b444a3417d04f7`

and the exact DEC-095 successor protocol Git blob:

`44129fc5337fb55b9c7d81f5ba0561ea788bd264`

The implementation fails closed if either checked-out source identity drifts.

The DEC-095 successor protocol fingerprint is recomputed at runtime and embedded in every synthetic/result object produced by the core.

## 3. Reused deterministic mechanics

DEC-096 reuses the already-tested DEC-090 mechanics for:

- feature/outcome identity validation;
- exact horizon timing;
- processed-manifest identity checks;
- chronological split construction;
- all-three-class fit support;
- fit-period median imputation;
- logistic fit-period standardization;
- fixed estimator construction;
- probability validation;
- candidate conversion;
- financial gate calculation;
- deterministic tie-break;
- validation and retrospective-holdout evaluation;
- candidate/probability/model/preprocessor fingerprints.

The reused helper code remains byte-bound to the closed DEC-090 training core.

No estimator parameters are redefined or changed in DEC-096.

## 4. Successor family fit control flow

Each DEC-095 family is attempted exactly once on the fit split.

### Successful family

A successfully fitted family records:

- status `FITTED`;
- fit-attempt count 1;
- preprocessor fingerprint;
- model fingerprint.

Its three frozen confidence variants are evaluated normally.

### Logistic non-convergence

If unchanged logistic regression raises the exact DEC-090 convergence failure:

`EXP-044 logistic regression failed to converge`

the successor records:

- status `FAILED_NON_CONVERGENCE`;
- failure reason `LBFGS_MAX_ITER_REACHED`;
- fit-attempt count 1;
- retry authorization false.

No second call to the family fitter occurs.

Its three threshold slots remain present at 0.50, 0.60, and 0.70 with:

- `family_fit_status=FAILED_NON_CONVERGENCE`;
- `evaluation_status=FAMILY_UNAVAILABLE`;
- `selection_gate_passed=false`.

No probabilities or probability digest are fabricated for that family.

The unchanged HGB family may continue.

### Other family failures

Any other family-fit exception propagates and fails the cell closed.

DEC-096 does not generalize the EXP-044 logistic failure into a generic ignore-errors policy.

## 5. Selection behavior

Successfully fitted families are scored using the unchanged DEC-095/DEC-088 selection rules.

The result still contains six family/threshold slots when logistic is unavailable:

- three unavailable logistic slots;
- three evaluated HGB slots.

Only variants with `selection_gate_passed=true` may enter the unchanged deterministic tie-break.

If at least one family fit but no eligible variant passes, status is:

`NO_MODEL_CHALLENGER`

If no family is available, the explicit successor status is:

`NO_MODEL_FAMILY_AVAILABLE`

and validation/holdout remain locked.

## 6. Validation and retrospective holdout

A selected variant is never refit.

The selected frozen fitted family is evaluated on validation using the exact DEC-095 gates.

Only a validation pass opens the retrospective holdout.

The holdout remains retrospective and post-result-informed.

DEC-096 never labels EXP-045 history as untouched OOS.

## 7. Result identity

Every core result includes:

- experiment ID `EXP-20260923-045`;
- DEC-096 training-core version/decision;
- bound base training-core blob;
- DEC-095 protocol version/decision/fingerprint;
- DEC-088 base protocol fingerprint;
- predecessor failed run `35891605645`;
- `prior_result_informed=true`;
- `untouched_oos=false`;
- cell identity;
- split counts;
- family fit statuses;
- all selection variants;
- validation/holdout state;
- canonical result fingerprint.

All promotion/trading flags remain false inside the result.

## 8. Authorization locks

DEC-096 keeps:

- `SUCCESSOR_TRAINING_RESULT_EXECUTION_AUTHORIZED=false`;
- `MODEL_FIT_AUTHORIZED=false`;
- promotion false;
- shadow false;
- demo-order false;
- broker-mutation false;
- live-order false;
- real-money false;
- trading false.

There is no EXP-045 training workflow.

## 9. Next gate

A later separate decision may freeze an artifact-backed EXP-045 runner and aggregate-result evidence contract.

That later source must consume only already-persisted historical feature/outcome evidence, bind the exact merged DEC-095/096 identities, and preserve the DEC-095 evidence-persistence policy.

No historical result-producing EXP-045 fit may run until another separately merged execution authorization opens it.
