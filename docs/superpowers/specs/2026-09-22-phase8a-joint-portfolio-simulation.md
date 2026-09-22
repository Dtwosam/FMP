# Phase 8A — Joint Portfolio Simulation Protocol

**Date:** 2026-09-22  
**Status:** APPROVED  
**Decision:** DEC-040  
**Experiment:** EXP-20260922-012  
**Scope:** Retrospective joint-account portfolio simulation only

## 1. Purpose

The individual Phase 8A retrospective batch can map strategy behavior one strategy at a time, but it cannot prove how multiple strategies interact when they share capital, simultaneous-risk limits, daily loss halts, and overlapping USD exposure.

DEC-040 therefore defines the next Phase 8A implementation layer: a deterministic joint-account historical simulator for frozen strategy sets.

This is a research protocol, not a promotion protocol. Retrospective joint results are labeled already seen and cannot by themselves authorize shadow, demo, or live execution.

## 2. Data roles

The accepted Dukascopy Phase 1/2 dataset remains authoritative.

Two data roles are separated explicitly:

- **signal bars:** deterministic 5m, 15m, or 1h bars required by each strategy version;
- **execution bars:** canonical 1m BID/ASK bars used to evaluate entries, stops, targets, time exits, PnL, and portfolio risk state.

No signal strategy is allowed to read 1m execution bars unless its own signal contract explicitly requires them. The 1m execution stream exists only to evaluate what could have happened after a signal became known.

## 3. Timing semantics

For every strategy candidate:

- observation bar label retains the existing family contract;
- true signal-known time remains the existing `signal_known_timestamp_utc`;
- earliest execution is exactly that signal-known timestamp;
- the joint simulator uses the first canonical 1m bar at that timestamp as the execution bar;
- if the required 1m execution bar is absent, the decision fails closed under existing backtest timing semantics;
- no signal may execute before it became known;
- no interpolation or synthetic execution bar is permitted.

## 4. Shared account / risk state

Each slippage scenario runs one independent shared virtual account beginning at exactly $100,000.

All strategies and all three V1 pairs in that scenario share:

- realized equity;
- open-position risk reservations;
- simultaneous-risk accounting;
- UTC daily realized-loss state;
- the existing Phase 3 risk engine.

Frozen default risk values remain:

- requested risk per approved directional decision: 0.25%;
- hard maximum per trade: 0.50%;
- maximum simultaneous open risk: 1.00%;
- UTC day-start realized-loss halt: 1.50%.

A strategy may not receive a private risk budget that bypasses the shared account.

## 5. Cost scenarios

Joint portfolio simulation runs exactly:

- 0.2 pips adverse slippage per fill;
- 0.5 pips adverse slippage per fill;
- 1.0 pip adverse slippage per fill.

Historical BID/ASK remains authoritative. Commission and financing remain zero only for the existing intraday-flat strategy contracts unless a later explicit protocol amends those assumptions.

## 6. Candidate conflict semantics

Candidate processing must be deterministic.

For candidates sharing the same symbol and exact signal-known timestamp:

- same-direction candidates may coexist and proceed to the risk engine as separate strategy decisions;
- opposite-direction candidates are a fail-closed strategy conflict and all conflicting candidates in that symbol/timestamp bucket are rejected before risk assessment.

Opposite directions on the same symbol at different timestamps are **not** automatically conflicting. They are separate market decisions and the backtest/risk state determines whether they can be accepted given open positions and risk.

This rule corrects the candidate router so conflict grouping is time-local, not whole-batch global.

## 7. Portfolio evidence identity

A joint run must bind:

- experiment ID;
- retrospective evidence label;
- exact runner code commit;
- exact strategy-version fingerprints;
- exact strategy signal timeframes and parameters;
- accepted processed-manifest SHA-256 for each pair;
- exact retrospective range;
- exact 1m execution data range;
- cost scenario;
- starting equity;
- risk configuration;
- candidate-set SHA-256;
- deterministic decision ordering.

No runtime clock, hostname, temporary path, UUID, or other nondeterministic field may enter evidence bytes.

## 8. Portfolio reporting

Every joint run must report at minimum:

- total completed trades;
- net PnL and net return;
- expectancy;
- profit factor;
- maximum drawdown;
- daily realized-return distribution;
- frequency of days at or above +10%;
- pair contribution;
- strategy contribution;
- timeframe contribution;
- rejection counts by reason;
- simultaneous-risk rejections;
- daily-halt rejections;
- candidate conflict rejections;
- requested USD-direction exposure by decision-time bucket;
- concentration of positive PnL by strategy and pair.

Where a metric cannot be computed honestly, it must be null/explicitly unavailable rather than fabricated.

## 9. Selection boundary

DEC-040 does **not** define the portfolio-selection algorithm.

The joint simulator may evaluate only explicitly supplied frozen strategy sets. It may not:

- search all combinations and silently select the best;
- promote a result automatically;
- mutate strategy parameters after observing joint results;
- change risk to manufacture a target return;
- resurrect a retired strategy as a champion.

A later predeclared selection protocol is required before joint results can choose a shadow-candidate portfolio.

## 10. Retrospective evidence label

All runs using history already opened by earlier phases remain:

`RETROSPECTIVE_ALREADY_SEEN`

and must record:

`untouched_oos = false`

No joint retrospective result under DEC-040 is prospective evidence.

## 11. Implementation order

1. Correct time-local same-symbol conflict routing.
2. Permit Phase 8A to load canonical 1m bars for execution while keeping strategy-version signal timeframes limited to 5m/15m/1h.
3. Build deterministic multi-strategy candidate assembly.
4. Merge canonical 1m execution bars across EURUSD/GBPUSD/USDJPY.
5. Run one shared Phase 3 backtest/risk state per cost scenario.
6. Add strategy/pair/timeframe contribution and USD-direction diagnostics.
7. Add deterministic artifact writer and tests.
8. Only after this is green may a separate portfolio-selection protocol be proposed.

## 12. Safety boundary

Throughout DEC-040:

- no MT5 demo orders;
- no broker mutation;
- no live orders;
- no real-money trading;
- no change to Phase 8B lock;
- no automatic strategy promotion.

Passing implementation tests means only that joint retrospective simulation is technically available.
