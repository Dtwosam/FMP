# EXP-20260914-005 — Rolling Volatility-Breakout Baseline

**Status:** PROPOSED — explicit approval required before implementation  
**Decision:** not yet assigned  
**Result:** no implementation or benchmark authorized

DEC-018 remains authoritative for the chronological split, final-test isolation, left-labelled timing bridge, source-free research boundary, historical BID/ASK execution, shared cost model, and unchanged Phase 3 risk controls.

## Motivation and family separation

The project source defines volatility features around ATR-like range measures, rolling realized volatility, range expansion/contraction, and current range relative to recent history. This baseline tests that structure directly without reusing a fixed London/Asian/New-York session boundary.

Unlike EXP-001 session breakout, the reference is a rolling wall-clock window that moves with every candidate bar. Unlike EXP-004 previous-day rejection and the later session high/low sweep/rejection family, the setup requires a **close outside a rolling channel plus contemporaneous range expansion** rather than a penetration-and-rejection of a frozen session level.

## Proposed frozen protocol

- Pairs: EURUSD, GBPUSD, USDJPY.
- Signal timeframes: 5m, 15m, 1h.
- Development: 2015-01-01 through 2020-12-31 inclusive.
- Validation: 2021-01-01 through 2023-12-31 inclusive.
- Final untouched test: 2024-01-01 through 2026-08-20 inclusive. Normal EXP-005 tooling must not access it.
- Eligible observation labels: 08:00 through 14:00 inclusive in `Europe/London`.
- Mandatory flat: exact 16:00 `Europe/London`.
- For each eligible signal bar with left label `T`, define the rolling reference window as exactly `[T - 8h, T)` at the tested signal timeframe. The current signal bar is excluded.
- The full 8-hour reference must have exact expected cadence and finite midpoint OHLC values. Missing or malformed reference data fails closed; history is never shortened or repaired.
- Compute from the reference window:
  - `reference_high = max(midpoint_high)`;
  - `reference_low = min(midpoint_low)`;
  - each bar's midpoint range `range_i = midpoint_high_i - midpoint_low_i`;
  - `reference_median_range = median(range_i)`.
- `reference_median_range` must be finite and strictly positive or the observation is ineligible.
- Current signal-bar range is `current_midpoint_high - current_midpoint_low`.
- Range-expansion multipliers are exactly **1.0x, 1.5x, and 2.0x**. These are the only strategy configurations.
- LONG requires both:
  - current midpoint close strictly above `reference_high`; and
  - current midpoint range at least `multiplier * reference_median_range`.
- SHORT requires both:
  - current midpoint close strictly below `reference_low`; and
  - current midpoint range at least `multiplier * reference_median_range`.
- Because `reference_high >= reference_low`, a valid close cannot qualify LONG and SHORT simultaneously. Any malformed state that makes directional classification non-unique fails closed rather than being repaired.
- Only the first qualifying directional volatility breakout per symbol/configuration/London date is emitted. A later Phase 3 rejection does not permit another attempt that date.
- LONG stop is frozen at the signal midpoint low; SHORT stop is frozen at the signal midpoint high.
- Define signal-time risk `R` from signal midpoint close to the frozen stop. Target is fixed at exactly **1.0R** from the signal midpoint close in the trade direction. Target multiple is not searched under EXP-005.
- Actual next-bar BID/ASK entry remains authoritative. If the executable entry makes the frozen stop/target geometry invalid, existing Phase 3 `INVALID_STOP_TARGET` semantics reject it; the order is never repaired, chased, widened, or retried.
- Required signal-session cadence through the exact 16:00 flat timestamp must be present. Completeness failures emit deterministic reasoned no-trade evidence wherever a valid timestamp can be represented.
- A complete London date/configuration with no qualifying setup emits deterministic `NO_VOLATILITY_BREAKOUT` evidence.
- Cost scenarios are exactly 0.2, 0.5, and 1.0 pips adverse slippage per fill, with historical BID/ASK spread, zero commission, and zero financing.
- Candidate generation and candidate bytes must be identical across all three cost scenarios for each fixed pair/timeframe/split/multiplier.
- Search space: exactly **3 configurations** per pair/timeframe.
- Planned benchmark matrix: 18 pair/timeframe/split cells × 3 multipliers × 3 costs = **162 benchmark rows**.
- Accepted Phase 3 risk settings remain unchanged: 0.25% requested risk/trade, 0.50% hard max risk/trade, 1.00% simultaneous open risk, and 1.50% UTC day-start realized-loss halt.

## Proposed promotion screen

Promotion begins at 0.2-pip adverse slippage. The same multiplier must have all three on both development and validation:

- net return > 0;
- expectancy/trade > 0;
- profit factor > 1.

Only baseline survivors receive the already-established downstream review:

- 0.5-pip cost robustness;
- neighboring-multiplier stability;
- calendar/subperiod concentration;
- sample size;
- drawdown;
- top-winner dependence.

The 1.0-pip scenario remains diagnostic rather than a universal mandatory promotion condition.

No post-result parameter expansion, alternate lookback, extra multiplier, target retuning, or rescue rule is permitted under `EXP-20260914-005`.

## Locked boundaries

This proposal does not authorize implementation or benchmark execution. The frozen USDJPY 15m session-breakout / 5-pip / 1.5x candidate remains unchanged. EXP-004 remains FAIL / REJECT. Session high/low sweep/rejection remains the later sixth baseline family. Phase 4 remains ACTIVE; the final test, Phase 5, broker/live integration, and real-money trading remain locked.
