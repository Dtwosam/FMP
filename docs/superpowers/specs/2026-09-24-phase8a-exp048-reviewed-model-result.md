# Phase 8A — EXP-048 Reviewed Historical Regime-Consensus Result

**Date:** 2026-09-24
**Status:** REVIEWED AFTER THE SINGLE DEC-128-AUTHORIZED HISTORICAL RUN
**Decision:** DEC-130
**Experiment:** EXP-20260924-048

## 1. Purpose

DEC-130 records and closes review of the single historical EXP-048 regime-consensus model run authorized by DEC-128 and predeclared for terminal review by DEC-127.

The workflow completed successfully and produced complete aggregate evidence. The result does **not** produce a stable selected model challenger.

EXP-048 remains explicitly post-result-informed retrospective evidence and is not untouched out-of-sample evidence.

## 2. Exact workflow run identity

- workflow: `phase8a-exp048-regime-consensus-model-training`
- workflow path: `.github/workflows/phase8a-exp048-regime-consensus-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run id: `36006524422`
- run attempt: `1`
- execution commit: `60b2796a64f0a4f7f95660d45ef7ab7fac519e9c`
- conclusion: `success`

The first run consumes the one DEC-128 slot. No rerun or replacement is authorized.

## 3. Job inventory

All 11 jobs completed successfully:

| Job | Job id |
| --- | ---: |
| authorization-preflight | 107655980381 |
| EURUSD 15m model-cells | 107656160749 |
| USDJPY 1h model-cells | 107656160763 |
| EURUSD 5m model-cells | 107656160814 |
| USDJPY 15m model-cells | 107656160817 |
| GBPUSD 1h model-cells | 107656160877 |
| EURUSD 1h model-cells | 107656160881 |
| GBPUSD 15m model-cells | 107656160974 |
| GBPUSD 5m model-cells | 107656161010 |
| USDJPY 5m model-cells | 107656161242 |
| aggregate-model-evidence | 107659528925 |

The authorization preflight passed the exact merged-main requirement, first-run rejection guard, pinned runtime installation, frozen workflow source inspection, and separately authorized execution gate.

## 4. Artifact inventory

All nine pair/timeframe artifacts plus the aggregate artifact are present and non-expired.

| Artifact | Artifact id | ZIP SHA-256 |
| --- | ---: | --- |
| EURUSD 5m | 10810123833 | c5b96e7cf19b4d1e2f8f17060018eb5befef1d504d412f62b9b6fe71ab7f3c19 |
| EURUSD 15m | 10811160585 | 156e34c3cc8008e5de77efc3369af4648af02451a0fba253f388150eca38cdad |
| EURUSD 1h | 10811225451 | f284d4eeec6459dd768a47027e2538fc50799106f401e0071e831637c18e431e |
| GBPUSD 5m | 10810776915 | 95cb2d5ece8082a897aba7b6e9c9b1cf708366c5a7671ffbc09c48519fe62901 |
| GBPUSD 15m | 10811225897 | 7d8ac9473d8a846b99e2077b953ccfebdcdaf5b8872a6360fc32fba5cd77a324 |
| GBPUSD 1h | 10811610031 | 80d2011850c619afdd5ed5ee4d25c315cafcce413cb7e02fb249ae9c034e52ec |
| USDJPY 5m | 10810703436 | 3a618aca41eb94df9a3b8d44a0e70d3fa0bbfa7e63841465ede341d71b188d24 |
| USDJPY 15m | 10811136503 | 8c41d5c4ad227952239e7d738a4c4c627fa64ee898167efadf72e28a008520de |
| USDJPY 1h | 10811615343 | 2f9d81b7cd72bff4a468962e148fc66a8b64ece0d2852e237ab807b2e88a54a0 |
| aggregate result evidence | 10811660325 | ea6f228baac35b7a858942452b8fb4fa44d312387a1c5812d164b5a954170d9f |

Aggregate artifact name:

`exp048-regime-consensus-model-result-evidence-60b2796a64f0a4f7f95660d45ef7ab7fac519e9c-from-feature-35867307338-outcome-35876715434`

## 5. Aggregate evidence identity

The aggregate JSON records:

- experiment id: `EXP-20260924-048`
- evidence version: `1`
- evidence label: `RETROSPECTIVE_ALREADY_SEEN`
- code commit: `60b2796a64f0a4f7f95660d45ef7ab7fac519e9c`
- verified cells: `18`
- aggregate evidence fingerprint: `acd3a9d7708c345b05082026de9eecc515abb9090a901126034e91173eb30647`
- prior-result-informed: `true`
- untouched OOS: `false`

The evidence fingerprint was independently recomputed from canonical JSON after removing the supplied fingerprint field and exactly matched the supplied value.

## 6. Aggregate result summary

Across all 18 model cells:

- selected cells: **0**
- no-regime-consensus-stable-model-challenger cells: **18**
- validation passes: **0**
- retrospective holdout passes: **0**
- aggregate-selection-gate-pass variants: **17**
- stability-pass variants: **0**
- stability-rejected variants: **17**
- unavailable budget variants: **0**
- accepted model candidates: **0**
- total consensus-eligible selection rows across all 18 cells: **431,086**

Each cell contains exactly three regime-model fits.

Logistic regression remained excluded in all 18 cells under DEC-112/DEC-123.

No cell reached validation, so retrospective holdout remained locked everywhere.

## 7. Cells with aggregate-gate passes

Seven cells produced one or more aggregate-gate passes:

| Cell | Consensus-eligible selection rows | Aggregate passes | Stability passes |
| --- | ---: | ---: | ---: |
| EURUSD 15m / 240m | 14,008 | 3 | 0 |
| EURUSD 1h / 240m | 3,980 | 3 | 0 |
| EURUSD 5m / 240m | 38,204 | 2 | 0 |
| GBPUSD 1h / 60m | 4,904 | 1 | 0 |
| GBPUSD 5m / 60m | 57,687 | 2 | 0 |
| USDJPY 5m / 60m | 57,584 | 3 | 0 |
| USDJPY 5m / 240m | 41,256 | 3 | 0 |

Every aggregate pass was rejected by the unchanged temporal-stability screen.

## 8. Interpretation boundary

The unanimous three-regime HGB filter materially changes the candidate-generation mechanism and produces 17 aggregate-financial passes, but it still produces zero temporally stable selected challengers under the predeclared criteria.

DEC-130 records that result only. It does not infer a causal market mechanism and does not relax any gate after seeing the outcome.

## 9. Review outcome

DEC-127's successful terminal-review path is satisfied:

- exact attempt-1 workflow identity;
- all 11 jobs successful;
- all nine cell artifacts present;
- aggregate artifact present;
- aggregate evidence bound to the execution commit;
- exact 18-cell inventory;
- canonical evidence fingerprint valid;
- downstream authorization locks false.

DEC-130 classifies the result as:

`REGIME_CONSENSUS_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`

This is a successful historical experiment execution with no stable selected model challenger.

## 10. Closure and authorization state

DEC-130 closes the consumed EXP-048 run authorization.

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

No EXP-048 result may be promoted into prospective or trading use.

## 11. Machine-checkable review source

Reviewed-result module:

`src/fmp/market_learning/model_successor_regime_consensus_result_decision.py`

Git blob:

`0556da8c036a55ba3b94d933f67f439eb306f9c2`

Focused regression tests:

`tests/test_phase8a_exp048_model_result_decision.py`

Git blob:

`59efeba44200b8b168b1c218c005009f2838e352`

The reviewed-result module wraps the predeclared DEC-127 terminal-review validator and additionally requires the exact run id, execution commit, attempt, conclusion, aggregate artifact identity/digest, evidence fingerprint, consensus-eligible total, and frozen result counts recorded above.

## 12. Next research boundary

Any further model research must be a separately identified, explicitly post-result-informed successor diagnostic/protocol frozen before any new result-producing execution.

DEC-130 itself authorizes no successor run and no prospective/shadow/trading action.
