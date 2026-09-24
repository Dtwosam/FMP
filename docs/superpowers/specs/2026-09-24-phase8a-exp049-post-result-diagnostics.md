# Phase 8A — EXP-049 Post-Result Regime-Utility Diagnostic

**Date:** 2026-09-24
**Status:** POST-RESULT DIAGNOSTIC; NO NEW MODEL EXECUTION AUTHORIZED
**Decision:** DEC-140
**Source experiment:** EXP-20260924-049
**Source result:** DEC-139

## 1. Purpose

DEC-140 freezes the detailed post-result diagnostic from the completed EXP-049 regime-utility experiment before any successor protocol is written.

The diagnostic uses only the immutable DEC-139 / EXP-049 aggregate evidence. It performs no new fit, changes no gate, and authorizes no historical result execution.

The purpose is to separate two observed limitations:

1. positive-utility consensus coverage is insufficient for many predeclared budget variants; and
2. every aggregate-financial pass still fails both the candidate-share and financial dimensions of the frozen temporal-stability screen.

## 2. Source binding

DEC-140 is bound to:

- source result decision: `DEC-139`
- source workflow run: `36029925264`
- source execution commit: `eeb735bca7d38c3246f22a9606dfafe9c3df8279`
- source evidence fingerprint: `29ecbb5bf3ce00f35c825e977d9b3fff1777e165ce9bef311fefcb7bfbdb091e`
- DEC-139 merge commit: `3535e47d2224802eadf154330ef57519c8ea674c`
- DEC-139 reviewed-result source blob: `dce13838f32fbb8aa0e403c550b669f778dd0742`

EXP-049 remains closed to rerun or replacement.

## 3. Utility-coverage accounting

EXP-049 predeclared exactly 54 budget variants:

- 18 model cells;
- candidate-budget anchors 250, 500, and 1000 for each cell.

Observed availability:

- total variants: **54**
- available/evaluated variants: **23**
- unavailable because utility-eligible row count was below the requested budget: **31**
- cells with at least one unavailable budget: **13 / 18**
- cells with all three budgets unavailable: **7 / 18**

Among the 23 available variants:

- aggregate selection passes: **8**
- aggregate selection rejects: **15**

Therefore the regime-utility mechanism creates evaluable density variants in only part of the frozen matrix, while still producing multiple aggregate-financial passes.

No post-result relaxation of the positive-utility requirement or budget anchors is authorized by this diagnostic.

## 4. Aggregate-pass concentration

All eight aggregate-selection passes occur on the 240-minute horizon.

They occur in four cells:

| Cell | Passing budgets | Pass count |
| --- | --- | ---: |
| EURUSD 1h / 240m | 250 | 1 |
| GBPUSD 5m / 240m | 1000 | 1 |
| USDJPY 15m / 240m | 250, 500, 1000 | 3 |
| USDJPY 5m / 240m | 250, 500, 1000 | 3 |

There are:

- 8 aggregate passes at 240m;
- 0 aggregate passes at 60m.

This is a descriptive property of the frozen result, not a claim that the 240-minute horizon is intrinsically superior.

## 5. Candidate-share stability failure is universal

Every one of the eight aggregate-passing variants fails the frozen 10% directional-candidate-share requirement in both 2021 half-year windows.

Therefore:

- 2021 H1 share rejects: **8 / 8**
- 2021 H2 share rejects: **8 / 8**
- candidate-share rejects in at least one stability window: **8 / 8**

Two variants have zero candidates in at least one 2021 half:

- USDJPY 15m / 240m / budget 250;
- USDJPY 5m / 240m / budget 250.

One variant has zero candidates in both 2021 halves:

- USDJPY 5m / 240m / budget 250.

Thus the utility-ranking change does not remove early-window activity concentration among the variants that clear the aggregate financial gate.

## 6. Financial-window stability failure is also universal

Every aggregate-passing variant also fails at least one frozen per-window financial-sign requirement.

Therefore:

- financial-window rejects: **8 / 8**
- share-and-financial rejects: **8 / 8**
- financial-only rejects: **0 / 8**
- share-only rejects: **0 / 8**

Six of eight fail financial signs in 2022 H2:

- EURUSD 1h / 240m / budget 250;
- GBPUSD 5m / 240m / budget 1000;
- USDJPY 15m / 240m / budget 250;
- USDJPY 15m / 240m / budget 500;
- USDJPY 15m / 240m / budget 1000;
- USDJPY 5m / 240m / budget 250.

Across the eight variants, financial-sign failures occur in:

- 2021 H1: 5 variants;
- 2021 H2: 1 variant;
- 2022 H1: 1 variant;
- 2022 H2: 6 variants.

Only two aggregate-passing variants retain positive financial signs in 2022 H2, and neither survives the full four-window stability screen.

## 7. Diagnostic classification

DEC-140 records:

`UTILITY_COVERAGE_AND_DUAL_TEMPORAL_STABILITY_LIMITED`

This is a descriptive classification of the frozen EXP-049 evidence.

It means:

- a majority of predeclared budget variants are unavailable because too few rows satisfy the frozen regime-utility eligibility rule; and
- every aggregate-financial pass fails both candidate-share and financial temporal stability.

It does **not** assert a causal market mechanism and does not authorize any gate relaxation or successor execution.

## 8. Guardrails

DEC-140 explicitly keeps false:

- relaxation of the 10% stability share floor;
- relaxation of financial stability requirements;
- removal of the 2021 stability windows;
- lowering the frozen positive-utility eligibility requirement;
- adding smaller budget anchors as a result-producing change;
- EXP-049 rerun authorization;
- EXP-049 replacement-run authorization;
- successor result execution;
- successor model fit;
- promotion;
- shadow/demo execution;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

A later successor protocol may study a separately predeclared mechanism intended to improve utility coverage and temporal generalization, but DEC-140 does not choose that mechanism and does not authorize its execution.

## 9. Machine-checkable source

Source:

`src/fmp/market_learning/model_successor_regime_utility_post_result_diagnostics.py`

Focused tests:

`tests/test_phase8a_exp049_post_result_diagnostics.py`

DEC-140 opens only:

`SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = true`

## 10. Next gate

Any successor protocol must be frozen separately and must preserve:

- the immutable DEC-139 reviewed result;
- the existing chronology and no-lookahead rules;
- the current stability criteria unless a future source-only decision explicitly and prospectively replaces them before any result;
- the no-rerun status of EXP-049.

No new historical model result, prospective shadow campaign, or trading action is authorized by DEC-140.
