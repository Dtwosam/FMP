# Phase 8A — EXP-047 Post-Result Temporal-Concentration Diagnostic

**Date:** 2026-09-24
**Status:** POST-RESULT DIAGNOSTIC; NO NEW MODEL EXECUTION AUTHORIZED
**Decision:** DEC-122
**Source experiment:** EXP-20260924-047
**Source result:** DEC-121

## 1. Purpose

DEC-122 freezes the detailed post-result diagnostic from the completed EXP-047 density experiment before any successor protocol is written.

The diagnostic uses only already persisted EXP-047 evidence. It performs no new model fit and authorizes no historical result execution.

The purpose is to distinguish density-generation failure from temporal-regime concentration without weakening the predeclared stability screen after seeing the result.

## 2. Source binding

DEC-122 is bound to:

- source result decision: `DEC-121`
- source workflow run: `35993400007`
- source execution commit: `5c4d81c0ebc9f930b2361d54cb0245a3d8c886d2`
- source evidence fingerprint: `f047310749a2742d75d2e448243080d368b6a5cdf66bc119ec33e59cc192352f`
- DEC-121 merge commit: `1c9dec9ea6025b45a35097c4d9c2eda11aaaad00`
- DEC-121 reviewed-result source blob: `1c1cffc360949609b2d4ae404a165154f3ce7b0f`

EXP-047 remains closed to rerun or replacement.

## 3. Density-variant accounting

EXP-047 evaluated exactly 54 HGB density variants:

- 18 model cells;
- 3 candidate-budget anchors per cell: 250, 500, 1000;
- unavailable budget variants: **0**.

Results:

- aggregate selection passes: **12**
- aggregate selection rejects: **42**
- stability passes: **0**
- stability rejects: **12**
- accepted model candidates: **0**

Thus density generation did create multiple aggregate-financial passes, but no variant survived temporal stability.

## 4. Cells containing aggregate passes

The 12 aggregate passes are concentrated in six cells:

| Cell | Passing budgets | Pass count |
| --- | --- | ---: |
| GBPUSD 1h / 60m | 250 | 1 |
| GBPUSD 5m / 240m | 250, 500 | 2 |
| USDJPY 15m / 60m | 250 | 1 |
| USDJPY 15m / 240m | 250, 500 | 2 |
| USDJPY 5m / 60m | 250, 500, 1000 | 3 |
| USDJPY 5m / 240m | 250, 500, 1000 | 3 |

No aggregate pass occurs in the other 12 cells.

## 5. Candidate-share failure is universal among aggregate passes

Every one of the 12 aggregate-passing variants fails the frozen 10% per-half-year candidate-share requirement in at least one stability window.

Therefore:

- candidate-share rejects: **12 / 12**
- stability passes: **0 / 12**

This establishes that aggregate candidate density is no longer the sole bottleneck. The selected activity remains temporally concentrated.

## 6. Financial-window failure is also common

Among the 12 aggregate passes:

- **10** also fail one or more per-window financial-sign requirements;
- **2** fail only candidate-share concentration while retaining positive financial signs in every window containing their candidates.

The two share-only rejects are:

- GBPUSD 1h / 60m / budget 250;
- GBPUSD 5m / 240m / budget 500.

Thus removing only the 10% share rule would still leave most aggregate passes unstable under the existing financial-window requirements.

## 7. 2021 concentration

Six aggregate-passing variants produce **zero candidates across both 2021 half-years**:

- USDJPY 15m / 240m / budget 250;
- USDJPY 15m / 240m / budget 500;
- USDJPY 5m / 60m / budget 250;
- USDJPY 5m / 240m / budget 250;
- USDJPY 5m / 240m / budget 500;
- USDJPY 5m / 240m / budget 1000.

Other passing variants often produce only a handful of 2021 candidates.

Examples:

- GBPUSD 5m / 240m / budget 250: 8 candidates across 2021;
- USDJPY 15m / 60m / budget 250: 1 candidate across 2021;
- USDJPY 5m / 60m / budget 500: 1 candidate across 2021;
- USDJPY 5m / 60m / budget 1000: 20 candidates across 2021.

This is direct evidence of regime/time concentration rather than simple global signal scarcity.

## 8. Diagnostic classification

DEC-122 records:

`TEMPORAL_REGIME_CONCENTRATION_DOMINANT`

This is a descriptive classification of the frozen EXP-047 evidence.

It does not assert a causal market mechanism and does not authorize a successor execution.

## 9. Guardrails

DEC-122 explicitly keeps false:

- relaxation of the 10% stability share floor;
- removal of the 2021 stability windows;
- adding still wider density anchors as a result-producing change;
- EXP-047 rerun authorization;
- EXP-047 replacement-run authorization;
- successor result execution;
- successor model fit;
- promotion;
- shadow/demo execution;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

A future successor may study a predeclared method intended to improve temporal/regime generalization, but DEC-122 does not choose or authorize that method.

## 10. Machine-checkable source

Source:

`src/fmp/market_learning/model_successor_density_post_result_diagnostics.py`

Git blob:

`ceb18c634af55051d2bbd5c749a7bc5862eba470`

Focused tests:

`tests/test_phase8a_exp047_post_result_diagnostics.py`

Git blob:

`4b109b5fe94a03cbea17fd444f0d7f3bc119baf6`

DEC-122 opens only:

`SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = true`

## 11. Next gate

Any later successor protocol must explicitly target temporal/regime generalization while preserving the reviewed EXP-047 result and without retroactively weakening the DEC-104/DEC-113 stability criteria.

No new historical model result, prospective shadow campaign, or trading action is authorized by DEC-122.
