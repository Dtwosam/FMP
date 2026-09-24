# Phase 8A — EXP-045 / EXP-046 Cross-Run Reproducibility Audit

**Date:** 2026-09-24
**Status:** POST-RESULT DIAGNOSTIC; NO NEW MODEL EXECUTION AUTHORIZED
**Decision:** DEC-112

## 1. Purpose

DEC-112 freezes a cross-run reproducibility audit of the completed EXP-045 and EXP-046 historical model results before any successor protocol is designed.

The audit is post-result-informed. It compares already persisted artifacts only. It performs no new model fit and authorizes no result-producing execution.

## 2. Frozen source identities

Compared results:

- EXP-045 result decision: `DEC-102`
- EXP-045 run: `35911916239`
- EXP-045 head: `6d42a5053c5f2f696071715640dab24973a40517`
- EXP-045 evidence fingerprint: `3e0ebac02dbba690b4c03dd10c3fdd30c5eb0d6356b881e38f9a3527f0135c55`
- EXP-046 result decision: `DEC-111`
- EXP-046 run: `35978474425`
- EXP-046 head: `dabafcc290d2b383531532d873c7d6c697198d5a`
- EXP-046 evidence fingerprint: `499c91e4508f07bf8a637657969175fbba8e93d07236b94ded06ae884b386214`

Shared source/runtime identities:

- runtime requirements blob: `d25ab16056b9f5df283147d67b8f401f60ae7520`
- DEC-096 successor training blob reused by DEC-105: `3f0bc1bfa9640d08175e72cdf131bb97c94d562c`
- compared cell count: **18**

The two runtime requirement files are byte-identical and pin the same NumPy/SciPy/scikit-learn/Polars versions.

## 3. HGB reproducibility

For hist-gradient boosting:

- identical model fingerprints: **18 / 18 cells**
- identical 0.5/0.6/0.7 candidate identity sets: **54 / 54 variants**
- identical raw probability digests: **4 / 18 cells**

The model object identity and all thresholded candidate sets are reproducible across both runs. Raw probability byte digests are not generally identical.

DEC-112 therefore records:

`MATERIAL_DECISION_REPRODUCIBILITY_ESTABLISHED`

for the frozen HGB path.

This classification applies to the observed candidate decisions and frozen financial gate outputs, not to bitwise equality of every floating-point probability.

## 4. Logistic-regression reproducibility

Logistic family availability is not reproducible across the two runs.

Five cells changed family availability:

### Non-convergence in EXP-045, fitted in EXP-046

- EURUSD 15m / 240m
- EURUSD 5m / 60m
- EURUSD 5m / 240m

### Fitted in EXP-045, non-convergence in EXP-046

- GBPUSD 5m / 240m
- USDJPY 15m / 240m

### Non-convergence in both

- GBPUSD 5m / 60m
- USDJPY 5m / 60m
- USDJPY 5m / 240m

Among the ten cells where logistic regression fitted in both runs:

- identical model fingerprints: **4 / 10**
- identical raw probability digests: **4 / 10**
- identical thresholded candidate identities: **29 / 30 variants**

The single candidate-set difference among jointly fitted variants is USDJPY 15m / 60m logistic at confidence 0.5:

- EXP-045 directional candidates: **5579**
- EXP-046 directional candidates: **5578**

Its aggregate gate outcome remained unchanged.

DEC-112 therefore records:

`FAMILY_AVAILABILITY_REPRODUCIBILITY_FAILED`

for the frozen logistic path.

The audit establishes the observed reproducibility failure. It does not assign a root cause.

## 5. Effect on historical model conclusions

Exactly one aggregate-gate outcome changed because of the logistic availability difference:

- EURUSD 5m / 60m logistic at confidence 0.6
- EXP-045: family unavailable
- EXP-046: aggregate selection gate pass, then temporal-stability reject

EXP-046 still produced:

- stability-pass variants: **0**
- accepted model candidates: **0**

Therefore the cross-run logistic variation changes one intermediate aggregate-gate outcome but does not change DEC-111's final no-stable-challenger result.

The HGB GBPUSD 5m / 240m predecessor challenger remains materially reproducible across runs and was rejected by the predeclared EXP-046 temporal-stability screen.

## 6. Guardrails

DEC-112 keeps false:

- EXP-046 rerun authorization;
- EXP-046 replacement-run authorization;
- logistic-family reuse for a new result-producing successor;
- result-producing execution of any logistic numerical remedy;
- relaxation of the DEC-104 stability screen;
- successor result execution;
- successor model fit;
- promotion;
- shadow/demo execution;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

A later successor protocol may choose to exclude logistic regression, or may predeclare a numerical-reproducibility remedy. DEC-112 does not select or authorize either implementation.

## 7. Machine-checkable source

Source:

`src/fmp/market_learning/model_successor_cross_run_reproducibility.py`

Git blob:

`cf4f6ee1a7d387c3a48269a9f6aea8212dd56b1b`

DEC-112 opens only:

`SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = true`

## 8. Next gate

Any later successor protocol must explicitly account for the DEC-112 logistic reproducibility finding before logistic regression can participate in result-producing execution.

No new historical model result, prospective shadow campaign, or trading action is authorized by DEC-112.
