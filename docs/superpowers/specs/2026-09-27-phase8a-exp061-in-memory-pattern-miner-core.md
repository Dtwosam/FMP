# Phase 8A — EXP-061 Deterministic In-Memory Pattern Miner Core

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY CORE / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-271  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-270

## 1. Purpose

DEC-271 implements the first deterministic in-memory execution core for the DEC-270 discovery-first pattern protocol.

The core consumes already-supplied feature and outcome rows only. It does not:

- locate or download historical artifacts;
- open source data;
- dispatch a workflow;
- read the reserved 2023-2026 robustness block into EXP-061 logic;
- compile a pattern into a tradable strategy;
- authorize promotion, demo, broker mutation, live orders, or trading.

Its role is to prove the search mechanics before any historical result-producing path is opened.

## 2. Input contracts

The core defines two immutable row types.

### FeatureObservation

Each row binds:

- observation id;
- EURUSD / GBPUSD / USDJPY;
- 5m / 15m / 1h;
- exact UTC availability timestamp;
- all 20 DEC-270 continuous discovery measurements;
- exact boolean session flags.

Continuous values must be finite numbers or null. Session flags must be booleans.

### OutcomeObservation

Each row binds:

- the same observation id/cell/time identity;
- exact UTC exit timestamp;
- 60m or 240m horizon;
- LONG and SHORT net pips at 0.5-pip adverse slippage;
- LONG and SHORT net pips at 1.0-pip adverse slippage.

The exit timestamp must equal `available_at_utc + horizon` exactly. All economic values must be finite.

Duplicate feature or outcome identities fail closed. Window membership also requires the exit timestamp to remain strictly before the frozen window end, so cross-boundary targets are purged.

## 3. State calibration

`calibrate_state_model` reads only 2015-2017 rows for the requested symbol/timeframe.

For each of the exact 20 continuous dimensions it calls the frozen DEC-270 empirical-tertile rule. A dimension with insufficient finite rows or tied cutpoints is omitted for that cell.

The deterministic session dimension is always available.

Later rows cannot influence cutpoints.

## 4. Pattern enumeration

`enumerate_patterns` constructs:

- every one-state pattern;
- every two-state pattern formed from two different dimensions.

It never combines two states from the same dimension and refuses to exceed the DEC-270 bound of 2,075 patterns per full cell/horizon state model.

The enumeration order is deterministic.

## 5. Discovery mining

`mine_discovery_shortlist` uses only the 2015-2017 discovery window.

For every enumerated pattern and LONG/SHORT direction it:

1. finds matching observations with exact supplied outcomes;
2. rejects total support below 300;
3. rejects any discovery year with support below 75 before yearly means are computed;
4. calculates exact 0.5-pip and 1.0-pip directional means;
5. applies the frozen DEC-270 discovery economic gates;
6. creates the immutable DEC-270 pattern fingerprint;
7. sorts by the frozen discovery ranking;
8. removes same-direction near-duplicates with discovery-event Jaccard >= 0.90;
9. keeps at most 10 per cell/horizon.

The report records:

- active continuous dimensions;
- enumerated pattern count;
- directional search count;
- qualifying count before deduplication;
- count after deduplication;
- the ordered shortlist.

## 6. Confirmation

`confirm_shortlist` uses only 2018 rows.

Every discovery-shortlisted hypothesis is evaluated in its original discovery order.

A hypothesis passes with:

- support >= 75;
- mean 0.5-pip net outcome > 0.

Confirmation cannot alter predicates, direction, cutpoints, fingerprint, or discovery rank.

At most the first three passers per cell/horizon are frozen. Later confirmation profitability cannot outrank an earlier discovery-ranked candidate.

## 7. Validation

`validate_frozen_patterns` uses only 2019-2022 rows.

For each frozen pattern it records:

- total support;
- support for each calendar year;
- aggregate 0.5-pip mean;
- yearly 0.5-pip means;
- number of positive years.

The frozen DEC-270 gate is applied unchanged:

- total support >= 200;
- each year support >= 40;
- aggregate mean > 0;
- at least 3 of 4 yearly means > 0.

Validation does not retrain, rerank, alter cutpoints, or redefine a pattern.

## 8. Reserved-history isolation

`run_in_memory_discovery` composes calibration, discovery, confirmation, and validation only.

Rows dated 2023-01-01 or later are outside every EXP-061 core window and therefore cannot affect:

- state cutpoints;
- search results;
- discovery rank;
- confirmation;
- frozen candidates;
- validation outcome.

Focused tests inject catastrophic 2023 observations and require the complete in-memory result to remain byte-semantically equivalent at the Python object level.

## 9. Synthetic proof

The focused test suite constructs an artificial market history in which:

- only `return_1h` has non-tied discovery variation;
- the HIGH state has positive LONG economics in all three discovery years;
- the redundant `return_1h=HIGH + OFF_SESSION` pair matches the same event set and is removed by Jaccard deduplication;
- the single-state HIGH pattern passes 2018 confirmation;
- it passes 2019-2022 validation with exactly three positive years;
- severe 2023 losses do not alter the EXP-061 result because that block is reserved.

The synthetic proof demonstrates mechanics only. It is not market evidence.

## 10. Frozen implementation identities

- core source: `src/fmp/discovery/pattern_miner.py`;
- core blob: `495a67699eb5014e52129f0238a2737049fe38e6`;
- focused tests: `tests/test_phase8a_exp061_pattern_miner.py`;
- focused-test blob: `9694a4185906c48dc5222722723ac28810cd2340`.

## 11. Authorization boundary

All remain false:

- historical source access;
- historical discovery execution;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo order placement;
- broker mutation;
- live orders;
- real-money action;
- trading.

DEC-271 authorizes only deterministic in-memory computation over supplied test/input rows.

## 12. Next gate

The next safe task is a non-executable EXP-061 artifact/evidence contract plus a deterministic adapter that converts already-approved market-learning feature/outcome artifacts into the DEC-271 in-memory row contracts.

That next gate must still perform no historical source opening or result-producing discovery run.
