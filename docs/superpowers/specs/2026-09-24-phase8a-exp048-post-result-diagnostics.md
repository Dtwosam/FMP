# Phase 8A — EXP-048 Post-Result Stability Diagnostic

**Date:** 2026-09-24
**Status:** POST-RESULT DIAGNOSTIC; NO NEW MODEL EXECUTION AUTHORIZED
**Decision:** DEC-131
**Source experiment:** EXP-20260924-048
**Source result:** DEC-130

## 1. Purpose

DEC-131 freezes the post-result diagnostic from the completed EXP-048 regime-consensus experiment before any successor protocol is written.

The diagnostic uses only already persisted EXP-048 evidence. It performs no new fit and authorizes no historical result execution.

## 2. Source binding

DEC-131 is bound to:

- source result decision: `DEC-130`
- source workflow run: `36006524422`
- source execution commit: `60b2796a64f0a4f7f95660d45ef7ab7fac519e9c`
- source evidence fingerprint: `acd3a9d7708c345b05082026de9eecc515abb9090a901126034e91173eb30647`
- DEC-130 merge commit: `39f7934896b83fdbd7f57dda75acded433419f92`
- DEC-130 reviewed-result source blob: `0556da8c036a55ba3b94d933f67f439eb306f9c2`

EXP-048 remains closed to rerun or replacement.

## 3. Variant accounting

EXP-048 evaluated exactly 54 regime-consensus density variants:

- aggregate selection passes: **17**
- aggregate selection rejects: **37**
- stability passes: **0**
- stability rejects: **17**
- unavailable budget variants: **0**
- accepted model candidates: **0**

## 4. Stability-failure partition

Among the 17 aggregate-passing variants:

- **17 / 17** fail at least one per-window financial-sign criterion;
- **13 / 17** also fail the frozen 10% candidate-share criterion;
- **13 / 17** therefore fail both share and financial-window criteria;
- **4 / 17** fail only financial-window criteria while satisfying the share floor in every window;
- **0 / 17** fail only the share rule.

The four financial-only rejects are:

- EURUSD 15m / 240m / budget 1000;
- EURUSD 1h / 240m / budget 250;
- EURUSD 1h / 240m / budget 500;
- EURUSD 1h / 240m / budget 1000.

## 5. 2021 activity

No aggregate-passing variant has zero candidates across both 2021 half-years.

Five variants do have zero candidates in one 2021 half-year:

- GBPUSD 5m / 60m / budget 250;
- GBPUSD 5m / 60m / budget 500;
- USDJPY 5m / 240m / budget 250;
- USDJPY 5m / 60m / budget 250;
- USDJPY 5m / 60m / budget 500.

This differs descriptively from EXP-047, where several aggregate passes had no activity across both 2021 half-years.

## 6. Diagnostic classification

DEC-131 records:

`WINDOW_FINANCIAL_INSTABILITY_DOMINANT`

This is a descriptive classification of the frozen EXP-048 evidence, not a causal market claim.

The regime-consensus mechanism reduces the most extreme 2021 inactivity pattern, but every aggregate pass still fails at least one frozen financial stability window.

## 7. Guardrails

DEC-131 keeps false:

- relaxation of the 10% stability share floor;
- relaxation of any financial stability requirement;
- removal of the 2021 stability windows;
- EXP-048 rerun authorization;
- EXP-048 replacement-run authorization;
- successor result execution;
- successor model fit;
- promotion;
- shadow/demo execution;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 8. Machine-checkable source

Source:

`src/fmp/market_learning/model_successor_regime_consensus_post_result_diagnostics.py`

Git blob:

`165ab1e0e10a9fb6453ad0880ea1df97d0a35fa8`

Focused tests:

`tests/test_phase8a_exp048_post_result_diagnostics.py`

Git blob:

`e162dc2194f8c17e02c0f92944d5b72e0a07447c`

DEC-131 opens only:

`SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = true`

## 9. Next gate

Any later successor protocol must explicitly target per-window financial generalization while preserving the reviewed EXP-048 result and without retroactively weakening the existing temporal-stability criteria.

No new historical model result, prospective shadow campaign, or trading action is authorized by DEC-131.
