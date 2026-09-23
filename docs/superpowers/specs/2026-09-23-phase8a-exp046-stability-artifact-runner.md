# Phase 8A — EXP-046 Artifact-Backed Runner and Evidence Contract

**Date:** 2026-09-23
**Status:** SOURCE-ONLY; AUTHORITATIVE EXP-046 RESULT EXECUTION CLOSED
**Decision:** DEC-106
**Experiment:** EXP-20260923-046

## 1. Purpose

DEC-106 freezes the artifact-backed historical-data runner and aggregate evidence contract around the merged DEC-104 protocol and DEC-105 deterministic training core.

It reuses the exact previously verified EXP-044 feature/outcome/readiness artifacts only as source data. It adds no new market-history preparation and authorizes no model fitting.

## 2. Exact source bindings

DEC-106 binds:

- DEC-104 protocol merge: `bb2ee82a7d081138e1c0847e8c406d6c3ac68589`
- DEC-104 protocol blob: `4c8da2259f1fd6d27862a50a47a0d8108b58bc2e`
- DEC-105 training-core merge: `7aa3d86f6c1fce61dd7e35d9ba9830b1fa7355b5`
- DEC-105 training-core blob: `6733d3c530fba944b9ea0c62783ed2110552e532`
- verified historical artifact loader blob: `27c0848d16722a22b4762f5842396c2aebc92bec`

Any source-byte drift fails closed.

## 3. Historical data identity

DEC-106 reuses the exact already-verified data chain:

- source data experiment: `EXP-20260923-044`
- feature run: `35867307338`
- feature evidence artifact: `10753455784`
- feature evidence fingerprint: `1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815`
- outcome run: `35876715434`
- outcome evidence artifact: `10758027876`
- outcome evidence fingerprint: `b24ad576e8234870dabf73000dacd7053241bf9c2b23e9f15dc8125d40c17117`
- readiness artifact: `10757578276`
- readiness fingerprint: `412573f505ec7912ff934cc6338cf4591b604e0beddb2cb6abb79447c777b105`

The exact nine pair/timeframe feature and outcome artifact identities remain inherited from the verified DEC-091 loader.

## 4. Cell-result validation

Every authoritative EXP-046 cell result must revalidate:

- exact 18-cell identity;
- EXP-046 / DEC-104 / DEC-105 identities;
- post-result-informed and non-untouched-OOS labels;
- exact model-family inventory;
- one fit attempt per fitted family;
- only the predeclared logistic `FAILED_NON_CONVERGENCE` family failure;
- six exact family/threshold selection slots;
- aggregate 0.5-pip gate identity;
- aggregate-gate / temporal-stability / final-gate consistency;
- exact four temporal-stability windows for every aggregate-gate-passing variant;
- recomputed per-window directional-candidate share;
- recomputed per-window financial-sign criteria;
- selected-variant eligibility;
- selection/validation/holdout chronology status chain;
- canonical cell result fingerprint.

## 5. Temporal-stability evidence rules

For a fitted variant that fails the unchanged aggregate selection gate:

- `aggregate_selection_gate_passed=false`;
- temporal stability must be `LOCKED_AGGREGATE_REJECT`;
- stability windows must be empty;
- final `selection_gate_passed=false`.

For an aggregate-gate-passing variant:

- full-selection candidate count must be positive;
- exactly four DEC-104 windows must be present in frozen order;
- each window identity and row count must be valid;
- directional-candidate share is recomputed as:
  - window directional candidates / full-selection directional candidates;
- the four DEC-104 criteria are recomputed from metrics;
- the window's supplied gate must exactly match recomputation;
- temporal-stability status is derived from all four window gates;
- final `selection_gate_passed` must equal temporal-stability PASS.

Unavailable logistic variants remain ineligible and contain no stability windows.

## 6. Cell summary evidence

The aggregate evidence stores, per cell:

- symbol, timeframe, horizon;
- cell result fingerprint;
- selection status;
- validation status;
- retrospective-holdout status;
- logistic fit status;
- HGB fit status;
- number of aggregate-selection-pass variants;
- number of stable-selection-pass variants;
- number of aggregate-pass variants rejected by stability.

For each cell:

`stable_pass_variant_count + stability_reject_variant_count == aggregate_pass_variant_count`

must hold.

## 7. Aggregate result evidence

Aggregate evidence requires all 18 exact cells and records:

- evidence version;
- runner version / DEC-106 identity;
- DEC-104 protocol identity and fingerprint;
- DEC-105 core identity;
- exact code commit of any future result-producing execution;
- exact historical feature/outcome/readiness evidence identities;
- deterministic sorted cell summaries;
- canonical aggregate evidence fingerprint;
- all result/fit/promotion/shadow/demo/broker/live/real-money/trading locks false.

Independent validation recomputes the aggregate fingerprint, exact identities, cell inventory, status chains, variant accounting, and summary counts.

## 8. Source identity

Artifact/evidence source:

`src/fmp/market_learning/model_successor_stability_artifacts.py`

Git blob:

`2d8d6f82cd15f5bdb75bb384fe3efe1dc560857a`

Version:

`fmp-exp046-stability-artifact-runner-v1`

Decision:

`DEC-106`

Focused tests:

`tests/test_phase8a_exp046_stability_artifacts.py`

Git blob:

`16583c84e40eb1f3aea03a2407720ee7f53ef6ab`

## 9. Execution boundary

`AUTHORITATIVE_STABILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = false`

The authoritative bundle function raises before:

- readiness validation;
- artifact loading;
- model fitting;
- cell execution.

DEC-106 adds no CLI, workflow, dispatch command, or result-producing path.

## 10. Authorization state

DEC-106 keeps false:

- authoritative EXP-046 result execution;
- model fit authorization;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

## 11. Next gate

A later separate decision may freeze workflow/CLI/execution-gate source around the exact merged DEC-104/105/106 identities.

That source must remain non-executable until another separate authorization decision.
