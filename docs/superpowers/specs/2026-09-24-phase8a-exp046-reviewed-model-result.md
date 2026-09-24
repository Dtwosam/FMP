# Phase 8A — EXP-046 Reviewed Historical Stability-Model Result

**Date:** 2026-09-24
**Status:** REVIEWED AFTER THE SINGLE DEC-109-AUTHORIZED HISTORICAL RUN
**Decision:** DEC-111
**Experiment:** EXP-20260923-046

## 1. Purpose

DEC-111 records and closes review of the single historical EXP-046 stability-model run authorized by DEC-109 and predeclared for terminal review by DEC-108.

The workflow completed successfully and produced complete aggregate evidence. The result produces no stable selected challenger and no accepted model candidate.

EXP-046 remains post-result-informed retrospective evidence and is not untouched out-of-sample evidence.

DEC-111 also records a cross-run reproducibility defect isolated to the logistic-regression fit path. That defect does not rewrite the predeclared DEC-108 terminal contract, but it blocks opening another successor protocol until separately diagnosed.

## 2. Exact workflow run identity

- workflow: `phase8a-exp046-stability-model-training`
- workflow path: `.github/workflows/phase8a-exp046-stability-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run id: `35978474425`
- run attempt: `1`
- execution commit: `dabafcc290d2b383531532d873c7d6c697198d5a`
- conclusion: `success`

The first EXP-046 run consumes the one DEC-109 run slot. No rerun or replacement is authorized.

## 3. Job inventory

All 11 DEC-108 jobs completed successfully:

| Job | Job id |
| --- | ---: |
| authorization-preflight | 107564457334 |
| GBPUSD 1h model-cells | 107564797795 |
| USDJPY 15m model-cells | 107564797821 |
| EURUSD 1h model-cells | 107564797826 |
| USDJPY 1h model-cells | 107564797858 |
| GBPUSD 5m model-cells | 107564797865 |
| EURUSD 15m model-cells | 107564797948 |
| USDJPY 5m model-cells | 107564797963 |
| EURUSD 5m model-cells | 107564798138 |
| GBPUSD 15m model-cells | 107564798211 |
| aggregate-model-evidence | 107574313561 |

No job or step failed.

## 4. Artifact inventory

All nine pair/timeframe artifacts plus the aggregate artifact are present and non-expired.

| Artifact | Artifact id | ZIP SHA-256 |
| --- | ---: | --- |
| EURUSD 5m | 10800005480 | 5ee30f3a61a6f7966aa30bb2e9d290b6b81611812aa531567a14512294c40349 |
| EURUSD 15m | 10799383135 | 83bf2d086fedc9d79a1a26a05297045096fcbc7fd6c3a3c5b5a98813d8f8d56c |
| EURUSD 1h | 10799536352 | c380b0f7e85317857b6d7ffee988192ade3171246605f4d637c375cd646b41fa |
| GBPUSD 5m | 10799966027 | c295be33d63ae576c9583f1547a664537d937c5e9de7bb5bf51030469202f354 |
| GBPUSD 15m | 10798874566 | 1f2a5b79011a3ab28fdb1e997ae99ae5b3b94f7253af189b6e14cc08b2adf46e |
| GBPUSD 1h | 10799029521 | f99436c4246f8db9290872e8a304e1c342de616499209cd8cd6e2ea8fea6b52f |
| USDJPY 5m | 10799807808 | fc9b0b259a0582273816818c9b8af891352d351c8bb1d6a9d3721e4ce6f1c299 |
| USDJPY 15m | 10799937027 | ed9302c8530058fd1d5982b271645434c38e3d4458b5480ad18a5cf1647ae666 |
| USDJPY 1h | 10800376001 | d70e275adcedec41e15ca23a97ffa11a5ef01a0b274199da3847f7cff95a3e63 |
| aggregate result evidence | 10800835426 | f52ffa5d98eb196a33b97c6c09172a97c2c4ad712a41603ec7aef535825cb5d2 |

The aggregate artifact name is:

`exp046-stability-model-result-evidence-dabafcc290d2b383531532d873c7d6c697198d5a-from-feature-35867307338-outcome-35876715434`

## 5. Aggregate evidence identity

The aggregate JSON records:

- experiment id: `EXP-20260923-046`
- evidence version: `1`
- evidence label: `RETROSPECTIVE_ALREADY_SEEN`
- code commit: `dabafcc290d2b383531532d873c7d6c697198d5a`
- protocol decision: `DEC-104`
- training-core decision: `DEC-105`
- runner decision: `DEC-106`
- verified cells: `18`
- aggregate evidence fingerprint: `499c91e4508f07bf8a637657969175fbba8e93d07236b94ded06ae884b386214`
- prior-result-informed: `true`
- untouched OOS: `false`

The evidence fingerprint was independently recomputed from canonical JSON with the fingerprint field removed and exactly matches the supplied fingerprint.

## 6. Result summary

Across all 18 cells:

- selected cells: **0**
- no-stable-model-challenger cells: **18**
- no-model-family-available cells: **0**
- validation passes: **0**
- retrospective holdout passes: **0**
- logistic non-convergence cells: **5**
- aggregate selection-gate passing variants: **2**
- temporal-stability passing variants: **0**
- temporal-stability rejected variants: **2**
- accepted model-candidate count: **0**

Every cell therefore stopped before validation selection.

## 7. Stability-screen findings

Exactly two variants passed the unchanged predecessor aggregate selection gate.

### 7.1 EURUSD 5m / 60m logistic regression at 0.6

Aggregate 2021-2022 selection evidence at 0.5-pip slippage:

- directional candidates: **288**
- mean net pips: **+3.7097222222**
- total net pips: **+1068.4**

Temporal windows:

| Window | Candidates | Candidate share | Mean net pips | Total net pips | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| 2021H1 | 1 | 0.3472% | -46.30 | -46.30 | REJECT |
| 2021H2 | 1 | 0.3472% | -9.70 | -9.70 | REJECT |
| 2022H1 | 62 | 21.5278% | +5.1516 | +319.40 | PASS |
| 2022H2 | 224 | 77.7778% | +3.59375 | +805.00 | PASS |

This variant is both temporally concentrated and financially negative in the two 2021 half-year windows.

### 7.2 GBPUSD 5m / 240m HGB at 0.6

This is the HGB identity that was selected and later rejected at validation in EXP-045.

Aggregate 2021-2022 selection evidence is unchanged:

- directional candidates: **460**
- mean net pips: **+5.1167391304**
- total net pips: **+2353.7**

Temporal windows:

| Window | Candidates | Candidate share | Mean net pips | Total net pips | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| 2021H1 | 6 | 1.3043% | +36.45 | +218.70 | REJECT |
| 2021H2 | 35 | 7.6087% | +28.5257 | +998.40 | REJECT |
| 2022H1 | 87 | 18.9130% | +9.1552 | +796.50 | PASS |
| 2022H2 | 332 | 72.1739% | +1.0244 | +340.10 | PASS |

The positive aggregate result is highly concentrated in 2022. DEC-104 therefore blocks it before validation, exactly as predeclared.

## 8. Cross-run reproducibility audit

After terminal review, the EXP-046 fitted-model evidence was compared with the frozen EXP-045 artifacts for the same cells, data, model configurations, pinned Python numerical packages, and predecessor fitting implementation.

### 8.1 HGB path

Across all 18 cells:

- common fitted HGB cells: **18**
- exact HGB preprocessor fingerprints: **18/18**
- exact HGB model fingerprints: **18/18**

The HGB path is byte-reproducible across the two historical runs.

### 8.2 Logistic path

Across the 10 cells where logistic regression fitted in both runs:

- exact logistic preprocessor fingerprints: **10/10**
- exact logistic model fingerprints: **4/10**
- logistic model fingerprint mismatches: **6/10**

Five cell fit-status outcomes also changed:

| Cell | EXP-045 | EXP-046 |
| --- | --- | --- |
| EURUSD 5m / 60m | FAILED_NON_CONVERGENCE | FITTED |
| EURUSD 5m / 240m | FAILED_NON_CONVERGENCE | FITTED |
| EURUSD 15m / 240m | FAILED_NON_CONVERGENCE | FITTED |
| GBPUSD 5m / 240m | FITTED | FAILED_NON_CONVERGENCE |
| USDJPY 15m / 240m | FITTED | FAILED_NON_CONVERGENCE |

The pinned `requirements/exp045-model-run.txt` and `requirements/exp046-model-run.txt` numerical package sets are identical. DEC-105 imports the exact DEC-096 logistic fitting implementation. The fit input preprocessing fingerprints are identical.

DEC-111 therefore records an unresolved **cross-run logistic numerical-reproducibility defect**. The evidence supports localization to the logistic fit path; it does not establish a specific BLAS, CPU, solver, or runner root cause.

This defect does not retroactively alter the valid DEC-108 terminal review. It does prevent treating the source as fully cross-run deterministic and prevents opening a new successor protocol until the issue is separately diagnosed.

## 9. Review outcome

DEC-108's successful terminal-review path is satisfied:

- exact attempt-1 workflow identity;
- all 11 jobs successful;
- all nine cell artifacts present;
- aggregate artifact present;
- aggregate evidence bound to the execution commit;
- exact 18-cell inventory;
- canonical evidence fingerprint valid;
- downstream authorization locks false.

DEC-111 classifies the result as:

`STABILITY_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`

The accepted-model-candidate count is zero.

## 10. Closure and authorization state

DEC-111 closes the consumed EXP-046 run authorization.

The following remain false:

- model-run dispatch authorization;
- replacement-run authorization;
- authoritative model-result execution authorization;
- model-protocol-result authorization;
- model-fit authorization;
- successor-protocol source-open authorization;
- promotion authorization;
- shadow authorization;
- demo-order authorization;
- broker mutation authorization;
- live-order authorization;
- real-money authorization;
- trading authorization.

The following diagnostic requirement is true:

`LOGISTIC_REPRODUCIBILITY_DIAGNOSTIC_REQUIRED = true`

No EXP-046 result may be promoted into prospective or trading use.

## 11. Machine-checkable review source

The DEC-111 reviewed-result module is:

`src/fmp/market_learning/model_successor_stability_result_decision.py`

Git blob:

`de344ef314df7c7707b24cd9b5f59568b2582fa6`

It wraps the predeclared DEC-108 terminal-review validator and additionally requires the exact run id, execution commit, attempt, conclusion, aggregate artifact identity/digest, evidence fingerprint, result counts, and cross-run reproducibility facts recorded above.

## 12. Next research boundary

Before any EXP-047 or other successor protocol source is opened, a separate source-only decision must diagnose or harden the logistic-regression cross-run reproducibility path.

That diagnostic must not rerun EXP-046, must not reinterpret low-count or rejected variants as accepted, and must not authorize a historical model result.

DEC-111 itself authorizes no successor protocol, fit, workflow, result execution, promotion, shadow, broker mutation, order, or trading action.
