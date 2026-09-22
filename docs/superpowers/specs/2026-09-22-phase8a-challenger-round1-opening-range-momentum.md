# Phase 8A Challenger Round 1 — Opening-Range Momentum

**Date:** 2026-09-22  
**Status:** APPROVED / PREDECLARED BEFORE BENCHMARK RESULTS  
**Decision:** DEC-041  
**Experiment:** EXP-20260922-013  
**Family:** `opening_range_momentum`  
**Strategy version:** `fmp-opening-range-momentum-v1`

## 1. Purpose

Phase 8A now has deterministic strategy identities, retrospective evaluation, shared-account portfolio simulation, and non-promotional evidence packaging. The next requirement is to create genuinely new challenger strategy versions under a frozen search protocol rather than recycling Phase 4 rejects.

This round introduces one new deterministic rule family across the full V1 universe:

- EURUSD
- GBPUSD
- USDJPY

Signal timeframes:

- 5m
- 15m
- 1h

All evidence in this experiment is retrospective. No result is untouched OOS and no result can authorize demo/live execution.

## 2. Market hypothesis

The hypothesis is that a directional close outside the pre-London opening range is more informative when the breakout candle itself shows directional conviction.

The family combines:

- a short pre-open London range;
- a fixed executable breakout buffer;
- candle-body direction and body-to-range fraction;
- a fixed structural stop inside the prior range;
- a fixed R-multiple target;
- mandatory same-day flat.

This is distinct from the Phase 4 `session_breakout` family because the reference window, signal-quality filter, stop geometry, and target geometry are all different and are frozen before benchmark results.

## 3. Exact session semantics

Timezone: `Europe/London`.

Reference range:

- starts 06:00 London;
- ends 08:00 London;
- uses exact complete signal-timeframe bars whose labels fall in `[06:00, 08:00)`;
- reference high/low use midpoint OHLC:
  - midpoint high = (bid high + ask high) / 2
  - midpoint low = (bid low + ask low) / 2.

Signal window:

- starts 08:00 London;
- ends 12:00 London;
- evaluates exact signal-timeframe bar labels in `[08:00, 12:00)`;
- only the first qualifying directional observation per London date may emit a trade candidate.

Mandatory flat:

- exact 16:00 `Europe/London`;
- if the required scheduled-exit bar is absent, the session fails closed as incomplete.

No overnight position is permitted.

## 4. Frozen signal rule

For an observation bar, define midpoint open/high/low/close.

`candle_range = midpoint_high - midpoint_low`

`body = abs(midpoint_close - midpoint_open)`

`body_fraction = body / candle_range`

If `candle_range <= 0`, that observation cannot qualify.

Fixed breakout buffer:

- exactly 2 pips;
- pip size follows the existing FMP pair convention.

Long candidate requires all:

1. midpoint close > reference high + 2 pips;
2. midpoint close > midpoint open;
3. body_fraction >= configured threshold.

Short candidate requires all:

1. midpoint close < reference low - 2 pips;
2. midpoint close < midpoint open;
3. body_fraction >= configured threshold.

If neither side qualifies, continue through the signal window. If no observation qualifies, emit a reasoned `NO_TRADE`.

## 5. Frozen stop and target geometry

Let:

`reference_width = reference_high - reference_low`

Reference width must be finite and strictly positive.

Long:

- stop = reference_high - 0.25 × reference_width
- risk_reference = midpoint_close - stop
- target = midpoint_close + target_r_multiple × risk_reference

Short:

- stop = reference_low + 0.25 × reference_width
- risk_reference = stop - midpoint_close
- target = midpoint_close - target_r_multiple × risk_reference

`risk_reference` must be finite and strictly positive or the session fails closed.

The first executable timestamp is the existing signal-known timestamp: observation label + signal timeframe width.

## 6. Frozen parameter grid

The search grid is intentionally small.

Fixed:

- breakout buffer = 2 pips
- reference window = 06:00–08:00 London
- signal window = 08:00–12:00 London
- flat = 16:00 London
- stop depth = 0.25 reference range

Searched:

- `body_fraction_threshold ∈ {0.50, 0.70}`
- `target_r_multiple ∈ {1.0, 1.5}`

This yields exactly:

- 4 configurations per pair/timeframe;
- 3 pairs × 3 timeframes × 4 = 36 strategy configurations;
- each configuration is evaluated at 0.2, 0.5, and 1.0 pips adverse slippage.

No other buffer, body threshold, stop depth, target, session window, pair, or timeframe may be added after results are inspected under EXP-013.

## 7. Data and chronology

Canonical source: accepted Phase 1/2 Dukascopy BID/ASK history.

### Stage A — retrospective discovery / robustness

Development:

- 2015-01-01 inclusive
- 2021-01-01 exclusive

Validation:

- 2021-01-01 inclusive
- 2024-01-01 exclusive

Both ranges are already known to the project and are labeled retrospective.

### Stage B — retrospective chronological confirmation

Only Stage A survivors may be evaluated on:

- 2024-01-01 inclusive
- 2026-08-21 exclusive

This period was already opened during Phase 7 and therefore **must not** be described as untouched, hidden, prospective, or final-test evidence for this new family.

No 2024+ source may be used to change EXP-013 parameters or gates.

## 8. Cost and risk

Historical BID/ASK is authoritative.

Adverse slippage per fill:

- 0.2 pips — mandatory
- 0.5 pips — mandatory
- 1.0 pip — diagnostic

Commission:

- zero

Financing:

- zero because the strategy is mandatory intraday flat

Risk:

- starting equity $100,000 per independent scenario
- requested risk 0.25%
- hard per-trade maximum 0.50%
- simultaneous risk maximum 1.00%
- UTC day-start realized-loss halt 1.50%

The existing Phase 3 risk engine remains authoritative.

Individual EXP-013 Stage A and Stage B strategy benchmarks use the same signal-timeframe next-bar execution convention as the established Phase 4 retrospective family benchmarks: 5m signals execute on the next supplied 5m bar, 15m signals on the next supplied 15m bar, and 1h signals on the next supplied 1h bar. DEC-040 canonical 1m execution is reserved for later joint-account portfolio simulation of explicitly frozen strategy sets and is not used to alter EXP-013 single-strategy selection results.

## 9. Stage A gate

A configuration is a Stage A survivor only if **all** of the following are true.

At 0.2 pips on both development and validation:

- net return > 0
- expectancy > 0
- profit factor > 1.0
- maximum drawdown <= 5%
- development completed trades >= 100
- validation completed trades >= 50

At 0.5 pips on both development and validation:

- net return > 0
- expectancy > 0
- profit factor > 1.0
- maximum drawdown <= 5%

Additionally, local robustness is required:

- at least one other configuration in the same pair/timeframe cell must also pass all 0.2/0.5 profitability/drawdown gates;
- the neighbor may differ by exactly one frozen grid coordinate: body threshold or target multiple.

This means an isolated single-point winner cannot survive Stage A.

The 1.0-pip result is preserved but is not a Stage A gate.

## 10. Stage B gate

Only Stage A survivors are opened on the 2024-01-01 through 2026-08-20 retrospective confirmation range.

At both 0.2 and 0.5 pips:

- net return > 0
- expectancy > 0
- profit factor > 1.0
- maximum drawdown <= 5%

At 0.2 pips:

- completed trades >= 75

The 1.0-pip result remains diagnostic.

A Stage B pass may move the immutable strategy version to `HISTORICAL_QUALIFIED` only. It does not make the strategy `SHADOW_VALIDATED`, `DEMO_ELIGIBLE`, or live eligible.

## 11. Evidence requirements

Every row must bind:

- experiment ID `EXP-20260922-013`
- family/version
- pair
- timeframe
- exact parameters
- exact code commit
- processed manifest SHA-256
- retrospective range
- cost/risk identity
- candidate SHA-256
- metrics
- reason counts

Stage A evidence must contain all 36 configuration identities before any Stage B authorization is derived.

Stage B authorization must identify exact Stage A survivor fingerprints and may not substitute another parameter point after 2024+ results are opened.

## 12. Continuous-learning boundary

EXP-013 is one challenger-generation round, not self-modifying production.

The system may:

- generate all predeclared configuration identities;
- benchmark them deterministically;
- apply the frozen gates;
- record survivors/rejections.

The system may not:

- invent new parameters after viewing outcomes;
- change gates to rescue a result;
- hot-swap any survivor into Phase 8B;
- authorize broker orders;
- alter an active champion set.

A later portfolio-selection protocol must decide whether any EXP-013 historical survivor belongs in a future frozen shadow candidate set.

## 13. Safety

Throughout EXP-013:

- MT5 AutoTrading remains OFF;
- no demo order placement;
- no live order placement;
- no broker mutation;
- no real-money trading;
- Phase 8B remains locked.
