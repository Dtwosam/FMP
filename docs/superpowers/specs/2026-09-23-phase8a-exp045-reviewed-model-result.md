# Phase 8A — EXP-045 Reviewed Historical Model Result

**Date:** 2026-09-23
**Status:** REVIEWED AFTER THE SINGLE DEC-099-AUTHORIZED HISTORICAL RUN
**Decision:** DEC-102
**Experiment:** EXP-20260923-045

## 1. Purpose

DEC-102 records and closes review of the single historical EXP-045 model-result run authorized by DEC-099 and predeclared for terminal review by DEC-100.

The run completed successfully as a GitHub Actions workflow and produced complete aggregate evidence. The result does **not** produce an accepted model challenger.

EXP-045 remains post-result-informed retrospective evidence and is not untouched out-of-sample evidence.

## 2. Exact workflow run identity

- workflow: `phase8a-exp045-model-training`
- workflow path: `.github/workflows/phase8a-exp045-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`
- run id: `35911916239`
- run attempt: `1`
- execution commit: `6d42a5053c5f2f696071715640dab24973a40517`
- conclusion: `success`

This first run consumes the one DEC-099 run slot. No rerun or replacement is authorized.

## 3. Job inventory

All 11 jobs completed successfully:

| Job | Job id |
| --- | ---: |
| authorization-preflight | 107353620434 |
| GBPUSD 15m model-cells | 107353779152 |
| GBPUSD 1h model-cells | 107353779161 |
| GBPUSD 5m model-cells | 107353779183 |
| EURUSD 5m model-cells | 107353779188 |
| USDJPY 1h model-cells | 107353779202 |
| EURUSD 15m model-cells | 107353779209 |
| EURUSD 1h model-cells | 107353779245 |
| USDJPY 5m model-cells | 107353779255 |
| USDJPY 15m model-cells | 107353779328 |
| aggregate-model-evidence | 107365635911 |

The authorization preflight passed the exact merged-main requirement, prior-run rejection guard, pinned runtime installation, frozen workflow source inspection, and separately authorized execution gate.

## 4. Artifact inventory

All nine pair/timeframe artifacts plus the aggregate artifact are present and non-expired.

| Artifact | Artifact id | ZIP SHA-256 |
| --- | ---: | --- |
| EURUSD 5m | 10773444973 | 236cdb91af7ebdcd3e5fd98bfd8dfabcbcbfb25221fd16aa903f764d24ce6c37 |
| EURUSD 15m | 10773198666 | 3e9b351dec386ed7a9a415a8cd5f070f2baa5adf6c2c6819f9e7cda3b2192774 |
| EURUSD 1h | 10773811698 | b3567613ec8f8d94dd8d989de99663591679c12dd1a1f2a382b1dbdd44aed33f |
| GBPUSD 5m | 10773709400 | f680a3f0acdef2c4f1e58c8b1c4d850bbe30753d916b9893c967860358517c28 |
| GBPUSD 15m | 10773553841 | 108915955a4a300667151614bd95e8020bc24bd73f5f201135d5fd54d4feffea |
| GBPUSD 1h | 10774685531 | 95f862158e7421a7e57edb0a71d98c7c9434a6331d532db083f1be366bd199fe |
| USDJPY 5m | 10775341008 | b41c922ea830bb71638455f00058b422d45fa3c30d82c3e6074d349f6627ddd0 |
| USDJPY 15m | 10774751957 | b829a00d2a67281c8d3234882a925cb737e5ab5dc9f3cf027fc06a4615b2ac78 |
| USDJPY 1h | 10774845741 | a6b1d87f77d4993588bdb9c5ed0696dd1c576dd070751f78462ca96d5622d52b |
| aggregate result evidence | 10774927034 | 8602d0b5e9bb6ad746f5cd5c96e878e631d6ed090dcd7a236c0ee00c6fadd5a5 |

The aggregate artifact name is:

`exp045-model-result-evidence-6d42a5053c5f2f696071715640dab24973a40517-from-feature-35867307338-outcome-35876715434`

## 5. Aggregate evidence identity

The aggregate JSON:

- experiment id: `EXP-20260923-045`
- evidence version: `1`
- evidence label: `RETROSPECTIVE_ALREADY_SEEN`
- code commit: `6d42a5053c5f2f696071715640dab24973a40517`
- verified cells: `18`
- aggregate evidence fingerprint: `3e0ebac02dbba690b4c03dd10c3fdd30c5eb0d6356b881e38f9a3527f0135c55`
- prior-result-informed: `true`
- untouched OOS: `false`

The evidence fingerprint was independently recomputed from canonical JSON and exactly matches the supplied fingerprint.

## 6. Result summary

Across all 18 model cells:

- selected cells: **1**
- no-model-challenger cells: **17**
- no-model-family-available cells: **0**
- validation passes: **0**
- retrospective holdout passes: **0**
- logistic non-convergence cells: **6**
- HGB fit failures: **0**

The single selected cell was:

- GBPUSD
- 5m timeframe
- 240m horizon
- selection status: `SELECTED`
- validation status: `REJECT`
- retrospective holdout status: `LOCKED_VALIDATION_REJECT`

Therefore the accepted model-candidate count is **0**.

The six predeclared logistic non-convergences occurred in:

- EURUSD 15m / 240m
- EURUSD 5m / 60m
- EURUSD 5m / 240m
- GBPUSD 5m / 60m
- USDJPY 5m / 60m
- USDJPY 5m / 240m

These are valid DEC-095 family-level outcomes rather than workflow failures.

## 7. Review outcome

DEC-100's successful terminal-review path is satisfied:

- exact attempt-1 workflow identity;
- all 11 jobs successful;
- all nine cell artifacts present;
- aggregate artifact present;
- aggregate evidence bound to the execution commit;
- exact 18-cell inventory;
- canonical evidence fingerprint valid;
- downstream authorization locks false.

DEC-102 classifies the result as:

`SUCCESSOR_MODEL_RESULT_REVIEWED_NO_ACCEPTED_CHALLENGER`

This is a successful historical experiment execution with no accepted model challenger.

## 8. Closure and authorization state

DEC-102 closes the consumed EXP-045 run authorization.

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

No EXP-045 result may be promoted into prospective or trading use.

## 9. Machine-checkable review source

The DEC-102 reviewed-result module is:

`src/fmp/market_learning/model_successor_result_decision.py`

Git blob:

`d672fc334702fcea2edc4a50cd331598fb192586`

It wraps the predeclared DEC-100 terminal-review validator and additionally requires the exact run id, execution commit, attempt, conclusion, aggregate artifact identity/digest, evidence fingerprint, and result counts recorded above.

## 10. Next research boundary

Any further model research must be a separately identified, explicitly post-result-informed successor experiment with its own protocol frozen before any result-producing execution.

DEC-102 itself authorizes no successor run and no prospective/shadow/trading action.
