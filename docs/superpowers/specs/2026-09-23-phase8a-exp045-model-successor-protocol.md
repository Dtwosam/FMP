# Phase 8A — EXP-045 Successor Model Protocol

**Date:** 2026-09-23
**Status:** APPROVED BEFORE ANY EXP-045 MODEL RESULT
**Decision:** DEC-095
**Experiment:** EXP-20260923-045

## 1. Purpose

EXP-044 V1 is closed by DEC-094 after its single authorized model workflow failed.

EXP-045 is a separately identified successor experiment.

It exists because EXP-044 exposed two implementation/model-family failure modes:

1. hidden result directories were not persisted by the first workflow;
2. frozen logistic regression failed to converge in four pair/timeframe jobs at its predeclared 2,000-iteration ceiling.

Because those facts are now known, EXP-045 is explicitly post-result-informed retrospective research.

It must never be described as untouched out-of-sample evidence.

DEC-095 freezes the successor protocol only. It does not authorize model fitting or a result-producing workflow.

## 2. Predecessor identity

EXP-045 binds the reviewed predecessor:

- predecessor experiment: `EXP-20260923-044`;
- predecessor closure: DEC-094;
- failed model run: `35891605645`;
- failed run head SHA: `e97fa03d0e94fd505d0f926eb730e01a41947880`;
- base DEC-088 protocol fingerprint: `1caeec61c7b1a9a6863caafc4c3e85bc8cbcfd5f504f2f7473afe0d4b9c55605`.

The protocol records:

- `prior_result_informed=true`;
- `untouched_oos=false`.

Any future EXP-045 evidence inherits those facts.

## 3. Universe, features, target, and chronology

EXP-045 intentionally preserves the DEC-088 direct-market research object.

The universe remains 18 independent cells:

- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h;
- 60m and 240m horizons.

There is still no pooled cross-pair, cross-timeframe, or cross-horizon model.

Inputs remain exactly the 48 frozen `FEATURE_VALUE_COLUMNS`.

The target remains exactly:

`best_direction_0p5`

with classes:

- `LONG`;
- `SHORT`;
- `NO_TRADE`.

The target still reflects the frozen historical BID/ASK semantics plus 0.5-pip adverse slippage per fill.

Chronology remains:

- fit: 2015-01-01 through 2020-12-31 inclusive;
- selection: 2021-01-01 through 2022-12-31 inclusive;
- validation: 2023-01-01 through 2024-12-31 inclusive;
- retrospective holdout: 2025-01-01 through 2026-08-20 inclusive.

Exact-horizon boundary purge and no-refit-after-fit remain unchanged.

## 4. Model families and configurations

EXP-045 keeps the same two model families:

- L2 logistic regression;
- histogram gradient boosting.

The scikit-learn version remains `1.9.1`.

Logistic configuration is unchanged from DEC-088:

- penalty `l2`;
- `C=1.0`;
- solver `lbfgs`;
- tolerance `1e-8`;
- fit intercept true;
- class weight none;
- `max_iter=2000`;
- warm start false.

Histogram gradient boosting configuration is unchanged from DEC-088.

No hyperparameter search, solver substitution, iteration increase, class reweighting, calibration, resampling, AutoML, neural-network expansion, or post-result feature selection is authorized.

## 5. New predeclared family-failure policy

Each family is attempted exactly once on the fit split.

### Logistic non-convergence

If the unchanged logistic fit emits:

`sklearn.exceptions.ConvergenceWarning`

at its unchanged 2,000-iteration ceiling, EXP-045 records:

- family status: `FAILED_NON_CONVERGENCE`;
- failure reason: `LBFGS_MAX_ITER_REACHED`.

The family is not retried.

No alternate solver is attempted.

No iteration limit is changed.

No preprocessing change is permitted.

The three frozen logistic threshold slots remain present in evidence at 0.50, 0.60, and 0.70, but each is marked:

`FAMILY_UNAVAILABLE`

and:

`selection_gate_passed=false`.

The already-predeclared HGB family may continue under its unchanged configuration.

### Other family-fit failures

Any other model-family fit failure remains fail-closed for the cell.

It is not silently converted into an unavailable family.

### All families unavailable

If no frozen family produces a valid fitted model, the cell status is:

`NO_MODEL_FAMILY_AVAILABLE`

and later chronology remains locked.

This is distinct from:

`NO_MODEL_CHALLENGER`

which means at least one family fit successfully but no eligible variant passed the frozen financial selection gate.

## 6. Selection, validation, and retrospective holdout

Confidence cutoffs remain exactly:

- 0.50;
- 0.60;
- 0.70.

The selection gate remains unchanged:

- at least 250 directional candidates;
- total 0.5-pip net pips strictly positive;
- mean 0.5-pip net pips strictly positive;
- gross positive pips greater than absolute gross negative pips.

Tie-break remains unchanged:

1. higher total 0.5-pip net pips;
2. higher directional candidate count;
3. logistic before HGB;
4. higher confidence threshold.

Only successfully fitted-family variants can enter that tie-break.

Validation and retrospective holdout still require the frozen gates at both 0.5- and 1.0-pip adverse slippage.

The 0.2-pip scenario remains diagnostic.

No refit is permitted.

## 7. Evidence-persistence policy

EXP-045 predeclares the persistence behavior learned from EXP-044 before any EXP-045 result exists.

Future pair/timeframe result upload must:

- execute even when a later cell in the same job fails;
- include hidden result files;
- preserve any completed cell-result JSON;
- warn rather than convert an already-failed computation into a second upload failure when no file exists.

Future aggregate upload must include hidden evidence files.

Authoritative aggregate evidence still requires all 18 complete cell results.

Partial artifacts are review evidence only and cannot be promoted into an aggregate pass.

## 8. Evidence requirements

Each model cell must preserve:

- fit row count and class counts;
- one fit-status record for each frozen family;
- successful-family preprocessor/model fingerprints;
- failed-family failure status/reason;
- all six family/threshold variant slots;
- unavailable-family variant status;
- classification diagnostics where probabilities exist;
- probability digests where probabilities exist;
- candidate counts and candidate-identity digests;
- financial metrics and gate outcomes;
- selected variant identity or explicit no-model status;
- validation/holdout status;
- canonical result fingerprint.

Aggregate evidence must preserve all 18 exact cell identities and remain retrospective.

## 9. Authorization locks

DEC-095 is source-only.

It sets:

- `model_protocol_result_authorized=false`;
- `model_fit_authorized=false`;
- `promotion_authorized=false`;
- `shadow_authorized=false`;
- `demo_order_authorized=false`;
- `broker_mutation_authorized=false`;
- `live_order_authorized=false`;
- `real_money_authorized=false`;
- `trading_authorized=false`.

No EXP-045 workflow exists or is dispatched by DEC-095.

## 10. Next gate

A later separate decision may implement the deterministic EXP-045 training core.

That implementation must bind the exact DEC-095 protocol fingerprint and preserve every unchanged DEC-088 choice plus the new family-failure/evidence-persistence rules.

A still-later decision must separately authorize any result-producing EXP-045 historical fit.

Even a successful EXP-045 historical result cannot authorize promotion or prospective shadow activity without another explicit review.
