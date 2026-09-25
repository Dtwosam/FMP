# Phase 8A — EXP-053 Post-Result Diagnostics

**Date:** 2026-09-25
**Status:** APPROVED POST-RESULT DIAGNOSTIC / SUCCESSOR SOURCE DESIGN MAY OPEN
**Decision:** DEC-184

## Purpose

DEC-184 compares immutable reviewed EXP-050, EXP-051, EXP-052, and EXP-053 evidence after DEC-183 closes the single consumed EXP-053 run slot.

It is descriptive only. It does not authorize rerun, replacement, gate relaxation, selection-window recalibration, selection-outcome ranking, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.

## Frozen source bindings

DEC-184 binds:

- DEC-183 merge: `6635c874973576b5acac7ec46ee2bf4fd2bbe1ba`;
- DEC-183 result-decision blob: `7001c2b7944bd7b75a0c70e6fb1a775ff50ba6b5`;
- DEC-173 diagnostic blob: `af57f0eb6c00e18bb587203dc81530702e657e87`.

Reviewed evidence fingerprints:

- EXP-050: `866b4a8f26553bad8c80a7b2e0e68aedb50bfa42b3c767ce91478c9dfd720023`;
- EXP-051: `7dd836ed1c76c8eefd09b2b75e1eef9e875f5c6261c6fbb2cac8e3209781aaea`;
- EXP-052: `34e397e027a069db9344d56546b654f00bd34aff73240e5bca1d55e7b3dab7eb`;
- EXP-053: `cb32abc0e4ecd3df8b639d77b6770e255aa87701eb19180dfdfb25c37dfe48e1`.

## Unchanged eligibility and availability

All four experiments preserve:

- 54 total budget variants;
- 28 available variants;
- 26 unavailable variants;
- 26,392 utility-eligible selection rows.

Therefore EXP-053 still changes ranking only; it does not alter direction eligibility or budget availability.

## Aggregate-pass progression

Aggregate-pass counts:

- EXP-050: 3;
- EXP-051: 1;
- EXP-052: 1;
- EXP-053: 10.

Stable-selection-pass counts:

- EXP-050: 0;
- EXP-051: 0;
- EXP-052: 0;
- EXP-053: 0.

EXP-053 therefore broadens aggregate financial passes substantially without producing a single stable challenger.

## EXP-053 aggregate-pass distribution

The 10 exact aggregate-pass variants are:

- GBPUSD 15m / 240m / budget 250;
- GBPUSD 5m / 240m / budgets 250, 500, 1000;
- USDJPY 15m / 60m / budget 250;
- USDJPY 15m / 240m / budgets 250, 500, 1000;
- USDJPY 1h / 240m / budget 250;
- USDJPY 5m / 60m / budget 1000.

This spans:

- 6 distinct cells;
- 2 horizon-60 variants;
- 8 horizon-240 variants;
- 4 GBPUSD variants;
- 6 USDJPY variants;
- 0 EURUSD variants.

The exact EXP-052 aggregate-pass variant, USDJPY 5m / 60m / budget 250, is not retained by EXP-053. In the same cell, the EXP-053 aggregate pass moves to budget 1000.

## Temporal-stability result

All 10 EXP-053 aggregate passes still fail the unchanged temporal-stability gate.

Every one of the 10 variants fails the 10% candidate-share floor in at least one 2021 half-year.

Five have zero candidates in 2021 H1.

Nine of the 10 also fail the 2022 H1 financial-sign criteria.

Only USDJPY 15m / 60m / budget 250 has a positive 2022 H1 stability window, but it still fails both 2021 windows on candidate share.

Therefore feature-support ranking improves temporal spread relative to EXP-052 in several cells, but it does not remove the early-period coverage problem and usually does not remove 2022 H1 financial instability.

## Representative cases

### GBPUSD 5m / 240m / budget 500

Selection half-year candidate counts:

`[57, 33, 131, 279]`

Selection half-year total net pips:

`[1043.7000000000012, 323.7999999999927, -875.1000000000075, 646.200000000002]`

This case demonstrates that feature support can create meaningful early-period candidate coverage, but 2021 H2 remains below the 10% share floor and 2022 H1 is financially negative.

### USDJPY 15m / 240m / budget 250

Selection half-year candidate counts:

`[0, 27, 88, 135]`

Selection half-year total net pips:

`[0.0, 395.69999999999897, -558.1999999999983, 1078.6999999999916]`

This case improves distribution beyond the EXP-052 all-late-window pattern, but still has zero 2021 H1 support and negative 2022 H1 performance.

### USDJPY 5m / 60m / budget 1000

Selection half-year candidate counts:

`[0, 3, 130, 867]`

Aggregate total net pips:

`485.19999999998333`

This is the only aggregate-pass budget in the common USDJPY 5m / 60m cell under EXP-053. EXP-052 had passed budget 250 in that cell instead.

## Interpretation

DEC-184 records:

- eligibility changed: false;
- budget availability changed: false;
- feature support broadened aggregate passes: true;
- feature support broadened aggregate-pass cells: true;
- feature support created some 2021 candidates: true;
- feature support removed all 2021 share failures: false;
- feature support removed 2022 H1 financial instability: false;
- selection-time temporal stability demonstrated: false;
- accepted model candidate created: false.

The frozen diagnostic classification is:

`FEATURE_SUPPORT_BROADENED_AGGREGATE_PASSES_BUT_DID_NOT_CLEAR_TEMPORAL_STABILITY`

## Explicit non-authorizations

DEC-184 keeps false:

- EXP-053 rerun;
- EXP-053 replacement run;
- stability-share relaxation;
- stability-financial relaxation;
- removal of early stability windows;
- selection-window recalibration;
- selection-outcome ranking;
- selection-window quotas;
- successor result execution;
- successor model fitting;
- promotion;
- shadow/demo execution;
- broker mutation;
- live orders;
- real-money action;
- trading authorization.

Only successor protocol **source design** may open.

## Source identity

Diagnostic source:

`src/fmp/market_learning/model_successor_fit_temporal_feature_support_utility_post_result_diagnostics.py`

Git blob:

`a2fce33c15422abeb8323a6e3014ebf5a3a52794`

Focused tests:

`tests/test_phase8a_exp053_post_result_diagnostics.py`

Git blob:

`2029970d4f48f7667c73f123a65e9c3a5945fb81`

## Next gate

A later source-only successor protocol may be proposed only if it directly addresses the two residual observed failure classes:

1. early selection-period candidate-share insufficiency;
2. 2022 H1 financial instability.

It must not use realized selection outcomes for ranking, recalibrate on selection/validation/holdout windows, add selection-window quotas, or relax the unchanged stability/financial gates.

Any successor fit or historical result execution remains a separate later authorization.
