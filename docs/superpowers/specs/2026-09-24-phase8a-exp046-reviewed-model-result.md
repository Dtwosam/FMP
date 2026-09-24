# Phase 8A — EXP-046 Reviewed Historical Stability-Model Result

**Date:** 2026-09-24
**Status:** REVIEWED AFTER THE SINGLE DEC-109-AUTHORIZED HISTORICAL RUN
**Decision:** DEC-111
**Experiment:** EXP-20260923-046

## 1. Purpose

DEC-111 records and closes review of the single historical EXP-046 stability-model run authorized by DEC-109 and predeclared for terminal review by DEC-108.

The workflow completed successfully and produced complete aggregate evidence. The result does **not** produce a stable selected model challenger.

EXP-046 remains explicitly post-result-informed retrospective evidence and is not untouched out-of-sample evidence.

## 2. Exact workflow run identity

- workflow: `phase8a-exp046-stability-model-training`
- workflow path: `.github/workflows/phase8a-exp046-stability-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run id: `35978474425`
- run attempt: `1`
- execution commit: `dabafcc290d2b383531532d873c7d6c697198d5a`
- conclusion: `success`

The first run consumes the one DEC-109 slot. No rerun or replacement is authorized.

## 3. Job inventory

All 11 jobs completed successfully:

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

The authorization preflight passed the exact merged-main requirement, prior-run rejection guard, pinned runtime installation, frozen workflow source inspection, and separately authorized execution gate.

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
- verified cells: `18`
- aggregate evidence fingerprint: `499c91e4508f07bf8a637657969175fbba8e93d07236b94ded06ae884b386214`
- prior-result-informed: `true`
- untouched OOS: `false`

The evidence fingerprint was independently recomputed from canonical JSON after removing the supplied fingerprint field and exactly matched the supplied value.

## 6. Aggregate result summary

Across all 18 model cells:

- selected cells: **0**
- no-stable-model-challenger cells: **18**
- no-model-family-available cells: **0**
- validation passes: **0**
- retrospective holdout passes: **0**
- logistic non-convergence cells: **5**
- aggregate-selection-gate-pass variants: **2**
- stability-pass variants: **0**
- stability-rejected variants: **2**
- accepted model candidates: **0**

The five predeclared logistic non-convergences occurred in:

- GBPUSD 5m / 60m
- GBPUSD 5m / 240m
- USDJPY 15m / 240m
- USDJPY 5m / 60m
- USDJPY 5m / 240m

HGB fitted in every cell.

## 7. Stability-screen findings

Exactly two variants passed the unchanged predecessor aggregate selection gate. Both failed the DEC-104 four-window temporal-stability screen.

### EURUSD 5m / 60m logistic at confidence 0.6

Aggregate selection:

- directional candidates: **288**
- mean net pips: **+3.709722222222171**
- total net pips: **+1068.3999999999853**

Temporal windows:

- 2021H1: 1 candidate, share 0.3472%, mean −46.30 pips, FAIL
- 2021H2: 1 candidate, share 0.3472%, mean −9.70 pips, FAIL
- 2022H1: 62 candidates, share 21.5278%, mean +5.1516 pips, PASS
- 2022H2: 224 candidates, share 77.7778%, mean +3.59375 pips, PASS

The variant was both temporally concentrated and financially negative in the two 2021 windows.

### GBPUSD 5m / 240m HGB at confidence 0.6

Aggregate selection:

- directional candidates: **460**
- mean net pips: **+5.116739130434755**
- total net pips: **+2353.6999999999875**

Temporal windows:

- 2021H1: 6 candidates, share 1.3043%, mean +36.45 pips, FAIL on candidate-share concentration
- 2021H2: 35 candidates, share 7.6087%, mean +28.5257 pips, FAIL on candidate-share concentration
- 2022H1: 87 candidates, share 18.9130%, mean +9.1552 pips, PASS
- 2022H2: 332 candidates, share 72.1739%, mean +1.0244 pips, PASS

This is the same predecessor aggregate challenger that EXP-045 later rejected in validation. Under the predeclared EXP-046 stability screen it is rejected before validation because its selection-period activity is heavily concentrated in 2022.

## 8. Review outcome

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

This is a successful historical experiment execution with no stable selected model challenger.

## 9. Closure and authorization state

DEC-111 closes the consumed EXP-046 run authorization.

The following remain false:

- model-run dispatch authorization;
- replacement-run authorization;
- authoritative model-result execution authorization;
- model-protocol-result authorization;
- model-fit authorization;
- promotion authorization;
- shadow authorization;
- demo-order authorization;
- broker mutation authorization;
- live-order authorization;
- real-money authorization;
- trading authorization.

No EXP-046 result may be promoted into prospective or trading use.

## 10. Machine-checkable review source

The DEC-111 reviewed-result module is:

`src/fmp/market_learning/model_successor_stability_result_decision.py`

Git blob:

`eb8970b21a48bb52c1ba75af64680f945abcbaa5`

It wraps the predeclared DEC-108 terminal-review validator and additionally requires the exact run id, execution commit, attempt, conclusion, aggregate artifact identity/digest, evidence fingerprint, and frozen result counts recorded above.

## 11. Next research boundary

Any further model research must be a separately identified, explicitly post-result-informed successor experiment with its own diagnostic/protocol frozen before any new result-producing execution.

DEC-111 itself authorizes no successor run and no prospective/shadow/trading action.
