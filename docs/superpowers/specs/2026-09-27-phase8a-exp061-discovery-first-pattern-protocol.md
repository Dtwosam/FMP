# Phase 8A — EXP-061 Discovery-First Market-State Pattern Protocol

**Date:** 2026-09-27  
**Status:** APPROVED SOURCE-ONLY PROTOCOL / RESULT EXECUTION LOCKED  
**Decision:** DEC-270  
**Experiment:** EXP-20260927-061  
**Scope:** First bounded implementation of the DEC-268 discovery-first research direction

## 1. Purpose

EXP-061 asks the market data what repeated conditions are followed by favorable directional outcomes. It does **not** start from session-breakout, trend-continuation, mean-reversion, or any other predefined strategy family.

The experiment produces interpretable **pattern hypotheses**, not executable trading strategies.

A later decision must separately define how any validated pattern is compiled into exact entry/stop/target/no-trade logic and tested on the reserved later history.

## 2. Evidence boundary

All accepted history through 2026-08-20 has already been seen somewhere in the project, so all EXP-061 historical evidence is labeled `RETROSPECTIVE_ALREADY_SEEN`.

The chronology is still frozen to prevent EXP-061 itself from using later observations to redesign earlier discovered patterns:

- discovery/search and cutpoint calibration: 2015-01-01 through 2017-12-31;
- confirmation: 2018-01-01 through 2018-12-31;
- chronological validation: 2019-01-01 through 2022-12-31;
- reserved robustness block: 2023-01-01 through 2026-08-20 inclusive.

The 2023-2026 block is closed to EXP-061.

## 3. Market universe

Exactly:

- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h;
- 60-minute and 240-minute future outcome horizons.

This yields exactly 18 symbol/timeframe/horizon cells.

The target directional economics use the existing market-learning BID/ASK outcome semantics:

- primary adverse slippage: 0.5 pips per fill;
- stress adverse slippage: 1.0 pip per fill;
- LONG and SHORT are searched as separate directional hypotheses.

## 4. Market-state dimensions

EXP-061 uses exactly 20 already-approved leakage-safe continuous measurements:

1. `return_1h`
2. `return_24h`
3. `realized_vol_1h`
4. `realized_vol_8h`
5. `realized_vol_24h`
6. `range_vs_prior_median_8h`
7. `sma_distance_2h_pips`
8. `sma_distance_8h_pips`
9. `sma_slope_2h_pips`
10. `sma_slope_8h_pips`
11. `roc_4h`
12. `roc_8h`
13. `momentum_accel_4h`
14. `body_to_range`
15. `close_location`
16. `prev_fx_day_high_dist_pips`
17. `prev_fx_day_low_dist_pips`
18. `prev_asia_high_dist_pips`
19. `prev_asia_low_dist_pips`
20. `spread_percentile_prior_24h`

Each continuous dimension is converted into LOW / MID / HIGH using empirical tertiles calculated **only from the 2015-2017 discovery window for that symbol/timeframe**.

For sorted finite values `x[0..n-1]`:

- lower index = `floor((n-1)/3)`;
- upper index = `floor(2*(n-1)/3)`.

At least 300 finite calibration rows are required. If the two cutpoints are not strictly ordered, that dimension is skipped for that symbol/timeframe rather than repaired or jittered.

A 21st dimension is the mutually exclusive session state with exact precedence:

1. LONDON_NEW_YORK_OVERLAP
2. LONDON
3. NEW_YORK
4. ASIA
5. OFF_SESSION

The precedence makes overlapping raw session flags deterministic.

## 5. Bounded search universe

There are at most:

- 20 × 3 continuous atomic states = 60;
- 5 session atomic states;
- 65 atomic states total.

Patterns contain exactly one or two state predicates. Two states from the same dimension are forbidden.

The resulting maximum is:

- 2,075 admissible state patterns per cell/horizon;
- × 2 directions = 4,150 directional hypotheses per cell/horizon;
- × 18 cells = **74,700 maximum directional hypotheses** in EXP-061.

If tied tertiles remove dimensions, the actual search count is lower and must be recorded.

No third predicate, added feature, alternate binning, extra horizon, extra pair, or result-driven feature invention is allowed under EXP-061.

This explicit bounded count is the experiment's multiple-comparison/search-volume accounting. EXP-061 does not claim that a backtest p-value alone establishes an edge; protection comes from the bounded search plus later frozen chronology and hard shortlist caps.

## 6. Discovery gate

For a pattern/direction to qualify inside 2015-2017:

- at least 300 total occurrences;
- at least 75 occurrences in each discovery calendar year;
- aggregate mean net pips at 0.5-pip slippage >= 0.25;
- mean net pips at 0.5-pip slippage > 0 in each of 2015, 2016, and 2017;
- aggregate mean net pips at 1.0-pip stress > 0.

A qualifying pattern is ranked by this immutable order:

1. worst discovery-year mean net pips at 0.5, descending;
2. aggregate mean net pips at 0.5, descending;
3. aggregate mean net pips at 1.0, descending;
4. support, descending;
5. pattern depth, ascending;
6. pattern fingerprint, ascending.

## 7. Discovery deduplication and shortlist

Near-identical pattern hypotheses are compared only within the same symbol/timeframe/horizon/direction.

If their discovery event sets have Jaccard similarity >= 0.90, only the higher frozen discovery rank is retained.

After deduplication, at most the top 10 patterns per symbol/timeframe/horizon proceed to confirmation.

Maximum confirmation shortlist:

- 10 × 18 = **180** pattern hypotheses.

## 8. 2018 confirmation

The 2018 block is pass/fail only.

A discovery-shortlisted pattern passes confirmation when:

- it has at least 75 occurrences in 2018;
- its 0.5-pip mean net outcome remains > 0.

The pattern definition, cutpoints, direction, ranking fields, and fingerprint cannot change.

2018 profitability magnitude does **not** rerank the candidates. Among confirmation passers, the original discovery ranking is preserved and at most the first 3 per cell/horizon are frozen.

Maximum frozen validation candidates:

- 3 × 18 = **54**.

## 9. 2019-2022 validation

Each frozen candidate is evaluated without retuning.

Required:

- at least 200 total validation occurrences;
- at least 40 occurrences in each calendar year;
- aggregate 0.5-pip mean net outcome > 0;
- at least 3 of the 4 calendar years have positive 0.5-pip mean net outcomes.

Validation cannot change a candidate. A failure is retained as evidence and rejected.

## 10. What a surviving EXP-061 result means

A survivor means only:

> this exact, interpretable market-state condition repeatedly preceded a favorable LONG or SHORT fixed-horizon outcome under the frozen retrospective chronology and cost assumptions.

It does **not** yet define:

- a tradable entry trigger beyond the observation boundary;
- stop placement;
- target placement;
- position sizing;
- overlapping-signal handling;
- portfolio interaction;
- live/demo eligibility.

Those require a later candidate-compilation protocol.

## 11. Reserved 2023-2026 block

EXP-061 cannot open the 2023-01-01 through 2026-08-21-exclusive block.

If EXP-061 yields validated pattern hypotheses, a later experiment may compile them into immutable trading rules and then use the reserved block as a later retrospective robustness test.

No EXP-061 result may be modified after seeing that reserved block and then claim the same block as validation.

## 12. Implementation identity

Frozen source:

- `src/fmp/discovery/pattern_protocol.py`;
- source blob: `a4a877b048a9cf4b70af7fcf484059a86a60644f`.

Focused tests:

- `tests/test_phase8a_exp061_pattern_protocol.py`;
- test blob: `e060c6e78166ececee1251ab322e8612b03e6873`.

## 13. Authorization boundary

DEC-270 is source-only.

All of the following remain false:

- historical source access for EXP-061;
- discovery execution;
- discovery-result production;
- candidate compilation;
- reserved 2023-2026 access;
- promotion;
- Phase 8B;
- demo order placement;
- broker mutation;
- live orders;
- real-money action;
- trading.

## 14. Next gate

After DEC-270 merges green, the next safe task is a deterministic **in-memory pattern miner core** that consumes supplied feature/outcome rows only and proves:

- exact state discretization;
- exact bounded pattern enumeration;
- exact support/economic gates;
- exact discovery ranking;
- exact Jaccard deduplication;
- exact shortlist/freeze semantics.

That core must still have no artifact loading, historical source access, workflow dispatch, promotion, demo, broker, live, or trading path.
