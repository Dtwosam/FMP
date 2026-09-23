# Phase 8A — Direct Market Learning and Controlled Retraining Foundation

**Date:** 2026-09-23  
**Status:** APPROVED — SOURCE FOUNDATION  
**Decision:** DEC-073  
**Experiment:** EXP-20260923-044  
**Scope:** Direct market-behaviour learning across EURUSD / GBPUSD / USDJPY

## 1. Purpose

FMP's long-term research objective is broader than testing hand-written trading rules. The accepted Dukascopy history should also be used to learn repeatable relationships between observable market state and later price behaviour.

Existing rule-based work remains valid and useful. EXP-015 and the Phase 7 baseline remain benchmark/challenger sources; they are not reclassified, rewritten, or discarded by this experiment.

EXP-044 opens a separate data-driven learning track. The machine-learning track studies market outcomes from eligible feature rows directly instead of receiving rows only when a hand-written strategy has already emitted a signal.

## 2. Safety and evidence boundary

This experiment is research only.

- no MT5 order;
- no broker mutation;
- no demo order;
- no live order;
- no real-money trading;
- no hot-swap of an active champion;
- no in-place self-modification of a running model.

Historical evidence through 2026-08-20 is already seen by the project and must be labeled `RETROSPECTIVE_ALREADY_SEEN`. It is not a new untouched out-of-sample test.

## 3. Data universe

The learning universe remains the accepted V1 instruments and signal timeframes:

- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h;
- canonical Phase 2 BID/ASK history rooted in the accepted Dukascopy snapshot.

The first model generation will begin from the 48 leakage-safe Phase 5 feature definitions. A new versioned market-learning feature materialization may extend those definitions beyond the original Phase 5 pre-2024 lock, because that lock remains historically authoritative for `fmp-feature-v1`. The old artifact is never rewritten.

Cross-pair, multi-timeframe, or newly invented feature families require a later predeclared amendment before result-producing use.

## 4. Direct market-outcome labels

The first implementation slice creates deterministic labels from every eligible feature-row timestamp, not only from rule-strategy signals.

A feature row is usable only after its declared `available_at_utc`. The earliest hypothetical entry timestamp is exactly that time.

Frozen first-generation forward horizons:

- 60 minutes;
- 240 minutes.

For each horizon, the exact bar at `available_at_utc + horizon` is required. Missing exact timestamps are not interpolated, shifted, backfilled, or repaired.

For each observation/horizon, record:

- future midpoint-open move in pips;
- hypothetical LONG net pips;
- hypothetical SHORT net pips;
- best positive direction, otherwise `NO_TRADE`;
- exact entry and horizon timestamps;
- exact adverse-slippage scenario.

Historical BID/ASK remains authoritative. Adverse slippage scenarios are exactly 0.2, 0.5, and 1.0 pips per fill. LONG enters from ASK and exits to BID; SHORT enters from BID and exits to ASK. Slippage is adverse on both sides.

These labels describe future market behaviour and cost-aware directional opportunity. They do not themselves authorize a trade.

## 5. Leakage rule

Features may use only information available at or before the observation's `available_at_utc`. Future bars are used only to construct the supervised target after the feature row has been frozen.

Model inputs may never include:

- future bars;
- future labels;
- realized future PnL;
- later shadow/demo outcomes unavailable at decision time;
- result-derived feature selection performed outside a frozen protocol.

## 6. Model-research sequence

EXP-044 is intentionally staged.

1. Build and verify deterministic market-outcome labels.
2. Build a new immutable full-history market-learning feature materialization using the approved feature definitions.
3. Freeze the first model families, preprocessing, chronological splits, prediction target, thresholds, and financial evaluation gate before any result-producing fit.
4. Fit on earlier history and select/validate only on later chronological history.
5. Compare model-derived trading candidates against the simple rule-based benchmarks after realistic costs.
6. Freeze any accepted model/challenger before prospective shadow evidence begins.

The source foundation in this decision performs step 1 only. No model-training result exists under EXP-044 yet.

## 7. Continuous-learning rule

FMP may learn from new shadow and demo experience, but the running champion may not rewrite itself.

Prospective operation follows champion/challenger separation:

1. the active champion remains immutable;
2. predictions, market context, decisions, hypothetical/actual fills, and outcomes are appended to an immutable learning ledger;
3. at a predeclared retraining point, a new challenger is trained offline from an explicitly frozen data cutoff;
4. the challenger receives a new immutable model/strategy identity;
5. champion and challenger are compared under a frozen gate;
6. promotion requires separate evidence and approval.

A losing challenger is retained as evidence. New paper trades may inform a later challenger but never mutate the currently active model in place.

## 8. Relationship to EXP-015 and DEC-042

EXP-015 remains a frozen rule-based challenger search and is still useful as a transparent benchmark and potential source of diversified rule strategies.

EXP-044 is not a rescue or retune of EXP-015. Its candidates must receive new identities and their own evidence.

DEC-042 portfolio selection remains blocked until its eligibility requirements are satisfied. A later decision may admit a historically qualified market-learning candidate to the same portfolio registry, but EXP-044 source-foundation code alone does not do so.

## 9. First source deliverable

The first source deliverable is a small `fmp.market_learning` package containing:

- immutable observation identity;
- deterministic market-outcome label/result contracts;
- 60m/240m exact-horizon labeling;
- 0.2/0.5/1.0-pip cost scenarios;
- deterministic batch ordering;
- fail-closed missing/duplicate-bar handling;
- unit tests for LONG, SHORT, NO_TRADE, pip scaling, exact-horizon gaps, and deterministic output.

It performs no data acquisition, feature generation, model fitting, order placement, or broker access.

## 10. Next gate

After this foundation is merged and green, the next authorized source task is the immutable full-history market-learning feature materialization and its tests. A separate predeclared model-training protocol is required before the first EXP-044 result-producing fit.
