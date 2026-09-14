# EXP-20260914-003 — Mean Reversion Baseline

**Status:** PLANNED  
**Decision:** DEC-020  
**Design:** `docs/superpowers/specs/2026-09-14-phase4-mean-reversion-design.md`

The experiment is frozen before result-producing implementation.

- Pairs: EURUSD, GBPUSD, USDJPY.
- Timeframes: 5m, 15m, 1h.
- Development: 2015-01-01 through 2020-12-31 inclusive.
- Validation: 2021-01-01 through 2023-12-31 inclusive.
- Final-test touched?: NO.
- Lookbacks: exactly 4h, 8h, 16h.
- Fresh-excursion thresholds: exactly 1.5σ and 2.0σ.
- Reference distribution: preceding N fully closed midpoint closes; the observation itself is excluded.
- Eligible current signal labels: 08:00 through 14:00 inclusive, Europe/London.
- Mandatory flat timestamp: exact 16:00 Europe/London.
- Cost scenarios: exactly 0.2, 0.5, 1.0 pips adverse slippage per fill; historical BID/ASK spread; zero commission and financing.
- Planned matrix: 18 pair/timeframe/split cells and 324 configuration rows.
- Candidate generation is reused unchanged across cost scenarios.
- No post-result parameter expansion is authorized under this experiment ID.
- Result-producing benchmark: NOT RUN.
- Conclusion: not assigned.

The final-test period remains locked. Phase 4 remains ACTIVE. Phase 5 and live execution permissions remain unchanged.
