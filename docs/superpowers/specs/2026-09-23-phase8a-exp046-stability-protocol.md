# Phase 8A — EXP-046 Temporal-Stability Successor Protocol

**Date:** 2026-09-23
**Status:** APPROVED SOURCE-ONLY BEFORE ANY EXP-046 MODEL RESULT
**Decision:** DEC-104
**Experiment:** EXP-20260923-046

## 1. Purpose

DEC-104 freezes a separately identified successor model protocol after DEC-103 recorded temporal instability as the dominant observed EXP-045 failure mode.

EXP-046 is deliberately post-result-informed. It is not untouched OOS.

DEC-104 authorizes no model fit, no historical result execution, no workflow, no promotion, no shadow/demo execution, no broker mutation, and no trading.

## 2. Predecessor binding

EXP-046 is bound to:

- predecessor experiment: `EXP-20260923-045`
- predecessor result decision: `DEC-102`
- predecessor diagnostic decision: `DEC-103`
- predecessor model run: `35911916239`
- predecessor result fingerprint: `3e0ebac02dbba690b4c03dd10c3fdd30c5eb0d6356b881e38f9a3527f0135c55`
- predecessor protocol fingerprint: `35526f123190c93948b4791920e7b350f7fbe0d8ec751b8c0f9d41e69b91944e`
- DEC-103 diagnostic source blob: `f1ccda0d393b851cd7c1db1399da57a920a0a7c1`

EXP-045 remains closed to rerun or replacement.

## 3. Frozen unchanged research identity

EXP-046 preserves the exact predecessor:

- symbols: EURUSD, GBPUSD, USDJPY;
- timeframes: 5m, 15m, 1h;
- horizons: 60m and 240m;
- 18 model cells;
- exact 48 feature columns;
- target: `best_direction_0p5`;
- target classes: LONG, SHORT, NO_TRADE;
- target slippage: 0.5 pips per fill;
- fit split: 2015-01-01 through 2020-12-31;
- selection split: 2021-01-01 through 2022-12-31;
- validation split: 2023-01-01 through 2024-12-31;
- retrospective holdout: 2025-01-01 through 2026-08-20;
- no refit after the fit split;
- model families: logistic regression and hist-gradient boosting;
- exact DEC-095 model configurations;
- confidence thresholds: 0.50, 0.60, 0.70;
- minimum directional candidates: 250;
- original aggregate financial selection gate;
- original validation and retrospective-holdout scenarios;
- original logistic non-convergence policy.

DEC-104 authorizes no change to features, target, chronology, model families, model configs, confidence thresholds, candidate-count floor, or logistic failure handling.

## 4. Sole protocol change: selection temporal stability

A variant must first pass the unchanged aggregate selection gate.

An aggregate-gate-passing variant is then evaluated over four non-overlapping six-month windows contained entirely inside the existing selection split:

| Window | Start | End exclusive |
| --- | --- | --- |
| selection_2021_h1 | 2021-01-01 | 2021-07-01 |
| selection_2021_h2 | 2021-07-01 | 2022-01-01 |
| selection_2022_h1 | 2022-01-01 | 2022-07-01 |
| selection_2022_h2 | 2022-07-01 | 2023-01-01 |

Every stability window must pass all of:

- directional candidate share >= 10% of the variant's full selection-period directional candidates;
- total net pips > 0;
- mean net pips > 0;
- gross positive pips > absolute gross negative pips.

All four windows must pass.

The 10% share is a concentration guard, not a replacement for the existing 250-candidate aggregate floor. The aggregate 250-candidate requirement remains mandatory.

## 5. Selection semantics

A variant becomes an EXP-046 selection challenger only when:

1. its model family fitted under the unchanged predecessor mechanics;
2. it passes the unchanged aggregate EXP-045 selection gate;
3. it passes all four DEC-104 temporal-stability windows.

Only those stability-qualified variants participate in the unchanged selection tie-break.

No low-count EXP-045 variant is grandfathered into EXP-046.

No threshold is chosen from EXP-045 validation or holdout evidence.

## 6. Validation and retrospective holdout

The selected variant, if any, is evaluated without refit on the unchanged:

- 2023-2024 validation split;
- 2025 through 2026-08-20 retrospective holdout.

Validation remains required before retrospective holdout is unlocked.

The evidence remains retrospective and prior-result-informed.

## 7. Logistic family policy

DEC-104 deliberately does not repair or retune logistic regression.

The DEC-095 family-level `FAILED_NON_CONVERGENCE` policy remains unchanged:

- one fit attempt;
- unavailable family variants when LBFGS reaches max iterations;
- no retry;
- no solver fallback;
- no max-iter change;
- no preprocessing rescue;
- the cell may continue with another frozen fitted family.

This isolates the temporal-stability change from model-family/configuration changes.

## 8. Source identity

Protocol source:

`src/fmp/market_learning/model_successor_stability_protocol.py`

Git blob:

`4c8da2259f1fd6d27862a50a47a0d8108b58bc2e`

Protocol version:

`fmp-exp046-stability-protocol-v1`

Protocol decision:

`DEC-104`

## 9. Authorization state

DEC-104 keeps false:

- model-protocol result production;
- model fitting;
- historical result execution;
- feature change;
- target change;
- chronology change;
- model-family change;
- model-config change;
- confidence-threshold change;
- minimum-candidate-count change;
- logistic rescue;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 10. Next gate

A later separate decision may implement a deterministic EXP-046 training/evaluation core that adds only the frozen temporal-stability screen.

That implementation must bind the exact DEC-104 protocol source before any result-producing workflow or fit is authorized.
