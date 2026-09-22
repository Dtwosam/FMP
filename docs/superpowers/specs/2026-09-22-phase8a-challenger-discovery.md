# Phase 8A — Rule-Based Challenger Discovery and Qualification

**Date:** 2026-09-22  
**Status:** APPROVED  
**Decision:** DEC-043  
**Experiment:** EXP-20260922-015  
**Scope:** New immutable rule-based challengers across EURUSD / GBPUSD / USDJPY

## 1. Purpose

DEC-042 cannot run a meaningful multi-strategy portfolio search because the current historical inventory contains only one selection-eligible strategy.

DEC-043 defines a new, predeclared rule-based challenger experiment across all three V1 pairs and all three supported signal timeframes. It expands the parameter regions of the six already-implemented rule families without changing the historical identity or outcome of any Phase 4–7 configuration.

All DEC-043 evidence is retrospective and already seen. The purpose is to create a bounded set of new immutable `HISTORICAL_QUALIFIED` challengers that can later enter DEC-042. Nothing in DEC-043 authorizes shadow, demo, live, or real-money trading.

## 2. Fixed universe

Pairs:

- EURUSD
- GBPUSD
- USDJPY

Signal timeframes:

- 5m
- 15m
- 1h

Families:

- session_breakout
- trend_continuation
- mean_reversion
- previous_day_rejection
- volatility_breakout
- session_sweep_rejection

No ML overlay, discretionary regime override, alternate pair, or new family is allowed in EXP-014.

## 3. New parameter regions

The EXP-014 search uses only the following new values. These grids are deliberately non-overlapping with the original Phase 4 parameter points.

### session_breakout

- `buffer_pips`: 1, 3, 4, 6, 8
- `target_range_multiple`: 0.75, 1.25, 1.75, 2.0

20 configurations per pair/timeframe cell.

### trend_continuation

- `trend_window_id`: A, B, C
- `target_r_multiple`: 0.75, 1.25, 1.75, 2.0

12 configurations per pair/timeframe cell.

### mean_reversion

- `lookback_hours`: 2, 6, 12, 24
- `threshold_sigma`: 1.25, 1.75, 2.25, 2.5

16 configurations per pair/timeframe cell.

### previous_day_rejection

- `buffer_pips`: 1, 3, 4, 6, 8

5 configurations per pair/timeframe cell.

### volatility_breakout

- `range_multiplier`: 0.75, 1.25, 1.75, 2.25, 2.5

5 configurations per pair/timeframe cell.

### session_sweep_rejection

- `buffer_pips`: 1, 3, 4, 6, 8

5 configurations per pair/timeframe cell.

Total frozen search space:

- 63 configurations per pair/timeframe cell;
- 9 pair/timeframe cells;
- 567 immutable challenger configurations.

No value may be added, removed, substituted, or rescued after results are observed.

## 4. Strategy identity

Every configuration receives a new immutable `StrategyVersion` identity under EXP-014. Old Phase 4–7 identities remain bound to their original code commits and evidence.

A new strategy identity must include:

- family;
- EXP-014 strategy version;
- pair;
- timeframe;
- complete parameters;
- signal contract;
- result-producing code commit.

Expanding the validators to accept new DEC-043 parameter values does not reclassify any old result.

## 5. Cost and risk

Each strategy is evaluated independently with the existing research backtest semantics:

- starting equity: $100,000;
- requested risk: 0.25%;
- hard per-trade maximum: 0.50%;
- simultaneous-risk maximum: 1.00%;
- daily realized-loss halt: 1.50%;
- zero commission and zero financing under the existing intraday-flat contracts;
- adverse slippage: exactly 0.2, 0.5, and 1.0 pips per fill;
- 0.2 and 0.5 are gating;
- 1.0 is diagnostic.

## 6. Three chronological stages

All stages are retrospective and non-overlapping.

### Stage A — discovery

- start: 2015-01-01 inclusive
- end: 2019-01-01 exclusive

All 567 frozen configurations may be evaluated.

A configuration passes the Stage A gate only if, at both 0.2 and 0.5 pips:

- net return > 0;
- expectancy > 0;
- profit factor > 1.05;
- maximum drawdown <= 5%;
- completed trades >= 40.

Within each exact `(symbol, family, timeframe)` cell, passing candidates are ranked by:

1. higher 0.5-pip annualized compounded return;
2. lower 0.5-pip maximum drawdown;
3. higher 0.5-pip profit factor;
4. higher 0.2-pip annualized compounded return;
5. lexicographically smaller strategy fingerprint.

At most **2** candidates per cell advance. No later stage may add a candidate not present in the frozen Stage A survivor manifest.

Maximum Stage A survivors: 54.

### Stage B — qualification

- start: 2019-01-01 inclusive
- end: 2023-01-01 exclusive

Only Stage A survivors may be opened.

A candidate passes Stage B only if, at both 0.2 and 0.5 pips:

- net return > 0;
- expectancy > 0;
- profit factor > 1.05;
- maximum drawdown <= 5%;
- completed trades >= 40.

At 0.2 pips additionally:

- at least 3 of calendar years 2019, 2020, 2021, 2022 have positive net PnL.

No retuning, replacement, or same-cell rescue is allowed after Stage B begins.

### Stage C — robustness

- start: 2023-01-01 inclusive
- end: 2026-08-21 exclusive

Only Stage B passers may be opened.

A candidate passes Stage C only if, at both 0.2 and 0.5 pips:

- net return > 0;
- expectancy > 0;
- profit factor > 1.05;
- maximum drawdown <= 5%;
- completed trades >= 30.

At 0.2 pips additionally:

- at least 3 of the four windows 2023, 2024, 2025, and 2026-partial have positive net PnL.

## 7. Final shortlist

Candidates passing all three stages are ranked by the following immutable order:

1. higher minimum of Stage B and Stage C 0.5-pip annualized compounded return;
2. lower maximum of Stage B and Stage C 0.5-pip maximum drawdown;
3. higher minimum of Stage B and Stage C 0.5-pip profit factor;
4. higher combined Stage B + Stage C 0.2-pip net PnL;
5. lexicographically smaller strategy fingerprint.

Walk down this ranking and select at most **11** new challengers, subject to:

- at most 4 selected challengers per pair;
- at most 3 selected challengers per strategy family;
- at most 2 selected challengers per exact `(pair, family, timeframe)` cell.

The selected set receives lifecycle `HISTORICAL_QUALIFIED` under EXP-014.

Any EXP-015 candidate not selected in the final shortlist is recorded as `RETIRED` with its exact rejection/non-selection reason. No unselected candidate remains silently available for DEC-042.

With the existing Phase 7 baseline added later, DEC-042 can therefore receive at most 12 eligible strategies without changing its frozen pool-size rule.

## 8. Stage authorization and data-opening discipline

Stage manifests are immutable evidence gates.

- Stage B source partitions may not be opened until the exact Stage A survivor manifest is written and verified.
- Stage C source partitions may not be opened until the exact Stage B PASS manifest is written and verified.
- A candidate absent from an upstream survivor manifest is forbidden downstream.
- Stage results cannot rewrite an upstream manifest.
- The result-producing code commit and accepted Phase 2 manifest identity must be bound into every stage.

## 9. Evidence and multiple-comparison accounting

Evidence must record:

- all 567 frozen candidate identities before Stage A results;
- exact count of tested candidates;
- exact Stage A cell rankings and survivors;
- Stage B and C authorization manifests;
- every scenario metric and gate;
- every retirement reason;
- final shortlist ordering and diversity-cap skips;
- selected 0-to-11 challengers.

All results must state:

- `evidence_label = RETROSPECTIVE_ALREADY_SEEN`;
- `untouched_oos = false`;
- `promotion_authorized = false` for broker/shadow execution.

The large search count is itself evidence of multiple-comparison risk and must be carried into Phase 8A acceptance.

## 10. Outcome

Possible EXP-014 outcomes:

- `CHALLENGER_DISCOVERY_PASS`: at least 1 and at most 11 new HISTORICAL_QUALIFIED challengers selected;
- `NO_CHALLENGER_QUALIFIED`: zero candidates survive/qualify;
- `PROTOCOL_FAILURE`: evidence identity, stage authorization, or deterministic replay fails.

If `NO_CHALLENGER_QUALIFIED`, DEC-042 remains blocked and thresholds may not be relaxed retroactively.

## 11. Continuous-learning relationship

EXP-014 is the first controlled challenger-discovery implementation. The same champion/challenger separation applies later to new shadow/live observations:

- active champions do not mutate;
- new data may launch a new challenger experiment;
- the experiment must freeze its search/protocol first;
- successful challengers receive new immutable identities;
- promotion still requires future prospective evidence.

## 12. Safety boundary

Throughout EXP-014:

- no MT5 demo orders;
- no broker mutation;
- no live orders;
- no real-money trading;
- no change to Phase 8B lock;
- no automatic champion promotion.

A historical qualifier is only eligible for later DEC-042 retrospective portfolio selection.


## Identity correction note

This protocol was first drafted as `DEC-042` / `EXP-20260922-014` while the repository still contained an uncorrected duplicate identity for the portfolio-selection protocol. Before any Stage A historical run, it was renumbered to `DEC-043` / `EXP-20260922-015`. No historical stage, benchmark, shortlist, or qualification result was produced under the earlier draft identity.
