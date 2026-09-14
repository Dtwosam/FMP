# EXP-20260914-004 — Previous-Day High/Low Rejection Baseline

**Status:** PREDECLARED  
**Decision:** DEC-022  
**Result:** pending merged-main benchmark

This experiment is frozen before any result-producing benchmark. DEC-018 remains authoritative for the chronological split, final-test isolation, Phase 3 execution/risk semantics, and source-free research boundary.

- Pairs: EURUSD, GBPUSD, USDJPY.
- Timeframes: 5m, 15m, 1h.
- Development: 2015-01-01 through 2020-12-31 inclusive.
- Validation: 2021-01-01 through 2023-12-31 inclusive.
- Final-test touched?: NO.
- Final test remains 2024-01-01 through 2026-08-20 inclusive and inaccessible from normal development/validation tooling.
- Reference session: for each London research date, use the most recent completed FX trading session `[17:00 America/New_York, 17:00 America/New_York)`, with session ends restricted to Monday through Friday. Monday-morning signals therefore reference the completed Friday session rather than the Sunday reopen.
- Reference completeness: require the exact expected signal-timeframe cadence for the full New-York-close reference session. Missing reference data fails closed with deterministic reasoned no-trade evidence whenever a valid timestamp can be represented.
- Reference levels: previous-day high and low are midpoint-quote extrema at the tested signal timeframe; `previous_day_midpoint = (previous_day_high + previous_day_low) / 2` is frozen at signal generation time.
- Eligible current observation labels: 08:00 through 14:00 inclusive in `Europe/London`. The immediately preceding closed bar may lie before 08:00. The exact mandatory flat timestamp is 16:00 Europe/London.
- Signal/session completeness: required signal-session cadence, including the immediately preceding closed bar and the exact 16:00 flat timestamp, must exist or the date fails closed with deterministic reasoned no-trade evidence.
- Penetration buffers: exactly 0, 2, and 5 pips.
- SHORT: previous midpoint close is at or below the previous-day high; current midpoint high reaches at least `previous_day_high + buffer`; current midpoint close finishes strictly below the previous-day high.
- LONG: previous midpoint close is at or above the previous-day low; current midpoint low reaches at or below `previous_day_low - buffer`; current midpoint close finishes strictly above the previous-day low.
- If a bar qualifies simultaneously at both levels, the date/configuration fails closed as `AMBIGUOUS_DUAL_REJECTION`.
- Only the first directional rejection per symbol/configuration/London date is emitted. A later Phase 3 rejection does not permit another attempt that day.
- LONG stop is frozen at the signal midpoint low; SHORT stop is frozen at the signal midpoint high. Target is frozen at the previous-day midpoint.
- Actual next-bar BID/ASK entry remains authoritative. Invalid stop/target geometry is rejected by the existing Phase 3 semantics and is never repaired, chased, widened, or retried.
- Complete dates with no qualifying rejection emit deterministic `NO_REJECTION` evidence.
- Search space: exactly 3 strategy configurations per pair/timeframe.
- Cost scenarios: exactly 0.2, 0.5, and 1.0 pips adverse slippage per fill, historical BID/ASK spread, zero commission, zero financing.
- Candidate generation and candidate bytes are identical across all three cost scenarios for a fixed pair/timeframe/split/buffer.
- Planned matrix: 18 pair/timeframe/split cells × 3 buffers × 3 cost scenarios = 162 benchmark rows.
- Phase 3 risk settings remain unchanged: 0.25% requested risk/trade, 0.50% hard max risk/trade, 1.00% simultaneous open risk, and 1.50% UTC day-start realized-loss halt.
- Promotion begins at 0.2-pip slippage: the same buffer must have net return > 0, expectancy/trade > 0, and profit factor > 1 on both development and validation.
- Only baseline survivors receive 0.5-pip robustness, neighboring-buffer stability, subperiod concentration, sample-size, drawdown, and top-winner-dependence review. The 1.0-pip scenario remains diagnostic.
- No post-result parameter expansion is permitted under EXP-20260914-004.

The frozen USDJPY 15m session-breakout candidate remains unchanged. Phase 4 remains ACTIVE. Phase 5, final-test access, broker/live integration, and real-money trading remain locked.
