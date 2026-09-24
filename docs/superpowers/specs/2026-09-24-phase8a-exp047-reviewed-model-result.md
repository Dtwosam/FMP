# Phase 8A — EXP-047 Reviewed Historical Density-Model Result

**Date:** 2026-09-24
**Status:** REVIEWED AFTER THE SINGLE DEC-118-AUTHORIZED HISTORICAL RUN
**Decision:** DEC-121
**Experiment:** EXP-20260924-047

## 1. Purpose

DEC-121 records and closes review of the single historical EXP-047 density-model run authorized by DEC-118 and predeclared for terminal review by DEC-117.

The workflow completed successfully and produced complete aggregate evidence. The result does **not** produce a stable selected model challenger.

EXP-047 remains explicitly post-result-informed retrospective evidence and is not untouched out-of-sample evidence.

## 2. Exact workflow run identity

- workflow: `phase8a-exp047-density-model-training`
- workflow path: `.github/workflows/phase8a-exp047-density-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run id: `35993400007`
- run attempt: `1`
- execution commit: `5c4d81c0ebc9f930b2361d54cb0245a3d8c886d2`
- conclusion: `success`

The first run consumes the one DEC-118 slot. No rerun or replacement is authorized.

## 3. Job inventory

All 11 jobs completed successfully:

| Job | Job id |
| --- | ---: |
| authorization-preflight | 107612572955 |
| EURUSD 1h model-cells | 107612786212 |
| EURUSD 5m model-cells | 107612786232 |
| EURUSD 15m model-cells | 107612786235 |
| GBPUSD 5m model-cells | 107612786242 |
| USDJPY 5m model-cells | 107612786281 |
| GBPUSD 15m model-cells | 107612786293 |
| USDJPY 15m model-cells | 107612786298 |
| USDJPY 1h model-cells | 107612786342 |
| GBPUSD 1h model-cells | 107612786381 |
| aggregate-model-evidence | 107615098473 |

The authorization preflight passed the exact merged-main requirement, first-run rejection guard, pinned runtime installation, frozen workflow source inspection, and separately authorized execution gate.

## 4. Artifact inventory

All nine pair/timeframe artifacts plus the aggregate artifact are present and non-expired.

| Artifact | Artifact id | ZIP SHA-256 |
| --- | ---: | --- |
| EURUSD 5m | 10805068835 | cb359a51ca334a13f1498a862f8fb245a1f7e4163c57558c0b4afe8ba8215914 |
| EURUSD 15m | 10805610518 | 04cfc5706b9b284f7b4a15c38bd216206d80a41fd84182df08c56bb0f812ef6b |
| EURUSD 1h | 10805371466 | 5a0e3934e36bf78c957bd5625505f89b162ebe3403a06935d9e458e3e0bcc284 |
| GBPUSD 5m | 10805471545 | 378b17645f3869d0d832abdefa2ded0694a7ebbb52c0c3b842661497d4491302 |
| GBPUSD 15m | 10805317588 | d736073ebac08c9a82c71897b1dd638a7dee89d6a25fd791bc6eb1aec544f04c |
| GBPUSD 1h | 10805386966 | 79a196835b435ac66e84124e8f7ae4b8dade22b5a98ca12840d7c6058d1e0f0f |
| USDJPY 5m | 10804479637 | 12a1746267bc789415e528ac8f75c609de0a2f61f3c078f1fa89a67ed7a9a45e |
| USDJPY 15m | 10805765253 | eeeedf6e6b761c868b759fbacb325b035559e09325c2e818c6821fde2c312a31 |
| USDJPY 1h | 10804914838 | 92b47040559f70c6555759d934d3fdd4b7cbd2fbf9ae5fe8b5431b93cb7c29c5 |
| aggregate result evidence | 10805174168 | 7e685380301ac82b5a64724d340cc4a3aa366e2e25098f31da0b97218135188a |

The aggregate artifact name is:

`exp047-density-model-result-evidence-5c4d81c0ebc9f930b2361d54cb0245a3d8c886d2-from-feature-35867307338-outcome-35876715434`

## 5. Aggregate evidence identity

The aggregate JSON records:

- experiment id: `EXP-20260924-047`
- evidence version: `1`
- evidence label: `RETROSPECTIVE_ALREADY_SEEN`
- code commit: `5c4d81c0ebc9f930b2361d54cb0245a3d8c886d2`
- verified cells: `18`
- aggregate evidence fingerprint: `f047310749a2742d75d2e448243080d368b6a5cdf66bc119ec33e59cc192352f`
- prior-result-informed: `true`
- untouched OOS: `false`

The evidence fingerprint was independently recomputed from canonical JSON after removing the supplied fingerprint field and exactly matched the supplied value.

The evidence binds the exact DEC-113 protocol, DEC-114 training core, DEC-115 runner, frozen feature/outcome artifacts, and readiness artifact.

## 6. Aggregate result summary

Across all 18 model cells:

- selected cells: **0**
- no-density-stable-model-challenger cells: **18**
- validation passes: **0**
- retrospective holdout passes: **0**
- aggregate-selection-gate-pass variants: **12**
- stability-pass variants: **0**
- stability-rejected variants: **12**
- unavailable budget variants: **0**
- accepted model candidates: **0**

HGB fitted in all 18 cells.

Logistic regression remained excluded in all 18 cells under DEC-112/DEC-113.

No cell reached validation, so retrospective holdout remained locked everywhere.

## 7. Cells with aggregate-gate passes

Only six of the 18 cells produced one or more aggregate-gate passes:

| Cell | Aggregate passes | Stability passes |
| --- | ---: | ---: |
| GBPUSD 1h / 60m | 1 | 0 |
| GBPUSD 5m / 240m | 2 | 0 |
| USDJPY 15m / 60m | 1 | 0 |
| USDJPY 15m / 240m | 2 | 0 |
| USDJPY 5m / 60m | 3 | 0 |
| USDJPY 5m / 240m | 3 | 0 |

Every aggregate pass was rejected by the frozen DEC-104/DEC-113 temporal-stability screen.

## 8. Stability-screen findings

The density anchors materially increased the number of aggregate-gate-passing HGB variants relative to EXP-046, but did not create temporal stability.

### GBPUSD 1h / 60m

Budget 250 passed the aggregate gate:

- 250 selection candidates
- mean net pips: **+2.6856**
- total net pips: **+671.4**

It failed because 2021H2 contributed only 13 candidates, or **5.2%**, below the frozen 10% share floor.

### GBPUSD 5m / 240m

Budgets 250 and 500 passed the aggregate gate.

Budget 250:

- mean net pips: **+18.8804**
- total net pips: **+4720.1**
- 2021H1: 0 candidates
- 2021H2: 8 candidates / 3.2%

Budget 500:

- mean net pips: **+4.8956**
- total net pips: **+2447.8**
- 2021H1: 6 candidates / 1.2%
- 2021H2: 40 candidates / 8.0%

Both fail on temporal concentration.

### USDJPY 15m

The 60m budget-250 variant passed the aggregate gate but had 0 candidates in 2021H1, 1 in 2021H2, and negative 2022H1 financial performance.

For 240m, budgets 250 and 500 passed the aggregate gate. Both had zero candidates in both 2021 half-years; budget 500 also turned negative in 2022H2.

### USDJPY 5m

All three budgets passed the aggregate gate for both 60m and 240m.

The dominant pattern is extreme temporal concentration:

- several variants have zero candidates in both 2021 half-years;
- higher budgets introduce only tiny 2021 shares;
- some 1000-budget variants also turn negative in 2022H2.

Thus widening density produced more financially positive aggregate variants, but not persistent selection-period activity across the frozen windows.

## 9. Review outcome

DEC-117's successful terminal-review path is satisfied:

- exact attempt-1 workflow identity;
- all 11 jobs successful;
- all nine cell artifacts present;
- aggregate artifact present;
- aggregate evidence bound to the execution commit;
- exact 18-cell inventory;
- canonical evidence fingerprint valid;
- downstream authorization locks false.

DEC-121 classifies the result as:

`DENSITY_MODEL_RESULT_REVIEWED_NO_STABLE_CHALLENGER`

This is a successful historical experiment execution with no stable selected model challenger.

## 10. Closure and authorization state

DEC-121 closes the consumed EXP-047 run authorization.

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

No EXP-047 result may be promoted into prospective or trading use.

## 11. Machine-checkable review source

The DEC-121 reviewed-result module is:

`src/fmp/market_learning/model_successor_density_result_decision.py`

Git blob:

`1c1cffc360949609b2d4ae404a165154f3ce7b0f`

Focused regression tests are:

`tests/test_phase8a_exp047_model_result_decision.py`

Git blob:

`ff3695b0543342982ceea347c81cb5e021354a8c`

The reviewed-result module wraps the predeclared DEC-117 terminal-review validator and additionally requires the exact run id, execution commit, attempt, conclusion, aggregate artifact identity/digest, evidence fingerprint, and frozen result counts recorded above.

## 12. Next research boundary

Any further model research must be a separately identified, explicitly post-result-informed successor diagnostic/protocol frozen before any new result-producing execution.

DEC-121 itself authorizes no successor run and no prospective/shadow/trading action.
