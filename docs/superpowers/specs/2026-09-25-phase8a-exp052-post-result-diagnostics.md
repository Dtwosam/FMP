# Phase 8A — EXP-052 Post-Result Diagnostics

**Date:** 2026-09-25
**Status:** APPROVED POST-RESULT DIAGNOSTIC / SUCCESSOR SOURCE DESIGN MAY OPEN
**Decision:** DEC-173

## Purpose

DEC-173 compares immutable reviewed EXP-050, EXP-051, and EXP-052 evidence after DEC-172 closes the consumed EXP-052 run slot.

It is descriptive only. It does not authorize rerun, replacement, gate relaxation, selection-window recalibration, selection-outcome ranking, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading.

## Frozen source bindings

DEC-173 binds:

- DEC-172 merge: `c06eb90953d1e38bd4db11ec6d7fc0d49ad0310c`;
- DEC-172 result-decision blob: `c9983c33792a8b143989b928a9c2af0c4ecda1e5`;
- DEC-162 merge: `3d8453c544fc4b06c691d1068828ec6da9fc7110`;
- DEC-162 diagnostic blob: `00b9cbb5b0c95bd161d429d1f973d1e807f02a48`.

Reviewed evidence fingerprints:

- EXP-050: `866b4a8f26553bad8c80a7b2e0e68aedb50bfa42b3c767ce91478c9dfd720023`;
- EXP-051: `7dd836ed1c76c8eefd09b2b75e1eef9e875f5c6261c6fbb2cac8e3209781aaea`;
- EXP-052: `34e397e027a069db9344d56546b654f00bd34aff73240e5bca1d55e7b3dab7eb`.

## Unchanged eligibility and availability

All three experiments preserve:

- 54 total budget variants;
- 28 available variants;
- 26 unavailable variants;
- 26,392 utility-eligible selection rows.

Therefore EXP-052 changes ranking, not direction eligibility or budget availability.

## Aggregate-pass comparison

Aggregate-pass counts are:

- EXP-050: 3;
- EXP-051: 1;
- EXP-052: 1.

Stable-selection-pass counts remain zero in all three experiments.

All aggregate passes remain confined to:

`USDJPY 5m / 60m`

Aggregate-pass budgets:

- EXP-050: 250 / 500 / 1000;
- EXP-051: 250;
- EXP-052: 250.

## Budget-250 comparison

### EXP-050

- selected candidates: 250;
- LONG / SHORT: 249 / 1;
- total net pips: `612.8999999999933`;
- mean net pips: `2.451599999999973`;
- selection half-year counts: `[0, 0, 0, 250]`.

### EXP-051

- selected candidates: 250;
- LONG / SHORT: 239 / 11;
- total net pips: `1288.1000000000117`;
- mean net pips: `5.152400000000047`;
- selection half-year counts: `[0, 0, 3, 247]`.

### EXP-052

- selected candidates: 250;
- LONG / SHORT: 248 / 2;
- total net pips: `1247.500000000025`;
- mean net pips: `4.9900000000001`;
- selection half-year counts: `[0, 0, 0, 250]`.

All three candidate-identity digests are different, proving the ranking changes the actual selected rows.

EXP-052 minus EXP-051:

- total net pips: `-40.59999999998672`;
- mean net pips: `-0.16239999999994748`;
- 2022 H1 candidates: `-3`;
- 2022 H2 candidates: `+3`.

EXP-052 therefore slightly reduces top-250 financial quality relative to EXP-051 and removes the only three pre-2022-H2 candidates that EXP-051 had introduced.

## Temporal-support transfer result

The EXP-052 support-first ranking was constructed entirely from out-of-fit fit-period half-year references.

It changes candidate identity but does not demonstrate transfer into selection-period temporal support.

EXP-052 selects:

- 2021 H1: 0;
- 2021 H2: 0;
- 2022 H1: 0;
- 2022 H2: 250.

The complete aggregate-pass candidate set is again concentrated in the latest selection half-year.

The frozen diagnostic classification is:

`FIT_TEMPORAL_SUPPORT_DID_NOT_TRANSFER_TO_SELECTION_TIME_AND_TOP250_FINANCIAL_QUALITY_SLIGHTLY_DECLINED`

## Broad-budget comparison

Budget 500 total net pips:

- EXP-050: `247.4000000000135` — aggregate pass;
- EXP-051: `-766.5999999999894` — aggregate reject;
- EXP-052: `-31.50000000000273` — aggregate reject.

EXP-052 improves budget 500 by `735.0999999999867` pips relative to EXP-051, but does not restore an aggregate pass.

Budget 1000 total net pips:

- EXP-050: `504.3000000000052` — aggregate pass;
- EXP-051: `-3.200000000010732` — aggregate reject;
- EXP-052: `-3.200000000010732` — aggregate reject.

EXP-052 does not change budget-1000 realized net pips relative to EXP-051.

## Interpretation

DEC-173 records:

- eligibility changed: false;
- budget availability changed: false;
- fit-support ranking changed candidate identity: true;
- fit-support ranking created 2021 candidates: false;
- fit-support ranking created 2022 H1 candidates: false;
- top-250 financial quality improved vs EXP-051: false;
- top-250 financial quality improved vs EXP-050: true;
- budget-500 financial quality improved vs EXP-051: true;
- budget-500 aggregate pass restored: false;
- budget-1000 changed vs EXP-051: false;
- selection-time transfer demonstrated: false.

The remaining blocker is not solved by adding fit-period half-year percentile support to the ranking.

## Explicit non-authorizations

DEC-173 keeps false:

- EXP-052 rerun;
- EXP-052 replacement run;
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

`src/fmp/market_learning/model_successor_fit_temporal_support_utility_post_result_diagnostics.py`

Git blob:

`af57f0eb6c00e18bb587203dc81530702e657e87`

Focused tests:

`tests/test_phase8a_exp052_post_result_diagnostics.py`

Git blob:

`e2850ede0f072b7739c6ce3e48e8d574df3a79de`

## Next gate

A later source-only successor protocol may be proposed only if it directly addresses the observed temporal-transfer failure without:

- using realized selection outcomes for ranking;
- recalibrating on selection/validation/holdout windows;
- adding selection-window quotas;
- relaxing the unchanged stability or financial gates.

Any successor fit or historical result execution remains a separate later authorization.
