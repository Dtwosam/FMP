# Phase 8A — EXP-058 Post-Result Diagnostic

**Date:** 2026-09-26
**Status:** APPROVED SOURCE-ONLY DIAGNOSTIC
**Decision:** DEC-241
**Experiment:** EXP-20260925-058

## Purpose

DEC-241 compares the closed EXP-058 historical result against the nearest successful predecessor, EXP-057, to isolate what the fit-derived regime-floor ranking changed and what remained structurally unresolved.

## Frozen bindings

DEC-241 binds:

- DEC-240 merge: `d691c8e12f40cf4baf3fc93f598b24d23b8435f4`
- DEC-240 result-decision blob: `f5a5f7e49b7088f4af9b35a9143e486c3fba3d1a`
- DEC-229 result-decision blob: `185e2cdf089cb6f1a12619af58fd32860366498f`
- DEC-230 diagnostic blob: `09e88b85a51b858296a3af7d146251606f1d5533`

EXP-057 evidence fingerprint:

`4bf67108e0df38d4f213d08898fadd338285ac7a2ce56920b61e4dba0f3eec4c`

EXP-058 evidence fingerprint:

`7e5019f0e00ada90a8f9c111d2b6fdb4ba41908f86a47203258b333439c8c8ee`

## Comparison result

Variant accounting is unchanged:

- 54 total variants;
- 28 available;
- 26 unavailable;
- 26,392 utility-eligible selection rows.

Aggregate-pass identity is also unchanged: USDJPY / 5m / 60m at budgets 250, 500, and 1000. Both experiments have zero temporal-stability passes and zero accepted model candidates.

The regime-floor layer changes candidate identity in 27 of 28 available variants. Aggregate 0.5-pip total net pips improve in 14 variants, worsen in 13, and remain unchanged in one.

For the common USDJPY / 5m / 60m aggregate-pass cell:

- budget 250 net pips: EXP-057 `301.4` → EXP-058 `819.2`
- budget 500 net pips: EXP-057 `89.0` → EXP-058 `179.5`
- budget 1000 net pips: EXP-057 `362.1` → EXP-058 `297.0`

But chronology remains insufficient:

- budget 250 windows: `0 / 0 / 0 / 250`
- budget 500 windows: `0 / 0 / 7 / 493`
- budget 1000 windows: `0 / 3 / 72 / 925`

The unchanged 10% per-window candidate-share floor therefore still fails.

## Classification

DEC-241 classifies the result as:

`REGIME_FLOOR_RANKING_CHANGED_CANDIDATE_MIX_AND_FINANCIALS_BUT_DID_NOT_CREATE_TEMPORAL_STABILITY`

The fit-regime floor materially changes ranking and financial mix, but it still does not create selection-time temporal breadth.

## Authorization state

DEC-241 keeps false:

- EXP-058 rerun;
- EXP-058 replacement run;
- stability-share relaxation;
- stability-financial relaxation;
- removal of early stability windows;
- selection-outcome ranking;
- selection-window recalibration;
- selection-window quotas;
- regime-floor retuning on selection outcomes;
- successor model fit;
- successor historical result execution;
- promotion;
- shadow/demo execution;
- broker mutation;
- live orders;
- real-money action;
- trading.

Only successor protocol source design is open.

## Source identity

Diagnostic source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_post_result_diagnostics.py`

Git blob:

`c0717252dabd625bd6a65b78f9acb5217ed44c84`

Focused tests:

`tests/test_phase8a_exp058_post_result_diagnostics.py`

Git blob:

`b3a1f930d088e279dbc17c86d4b4bd3b6c60fe83`

## Next gate

After DEC-241 is green and merged, the next safe gate is a source-only successor protocol under a new experiment identity. It may use fit-derived information only and must preserve the frozen selection/validation/holdout chronology and execution locks.
