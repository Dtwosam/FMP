# EXP-20260914-003 — Mean Reversion Baseline

**Status:** FAIL  
**Decision:** DEC-020  
**Design:** `docs/superpowers/specs/2026-09-14-phase4-mean-reversion-design.md`

The experiment protocol below was frozen before result-producing implementation. Result fields were appended only after the complete merged-main benchmark matrix finished and was independently verified.

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
- Result-producing benchmark: run `34875463677` — SUCCESS on code commit `87003a3982ca61eb6fd030c5291616d98dbb0c1a`.
- Completed matrix: 18/18 cells successful; 324/324 rows independently verified with zero integrity/identity errors.
- Baseline promotion result: zero of 54 pair/timeframe/lookback/threshold points passes the 0.2-pip development-and-validation gate; every 0.2-pip row has negative net return, negative expectancy, and profit factor below one on both splits.
- Conclusion: REJECT.

Detailed evidence: `docs/phase4-mean-reversion-evidence.md`.

The final-test period remains locked. The frozen USDJPY 15m session-breakout serious candidate remains unchanged. Phase 4 remains ACTIVE; the next approved baseline family is previous-day high/low rejection. Phase 5 and live execution permissions remain unchanged.
