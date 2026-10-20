# DEC-1913 — Fail closed on non-finite derived backtest metrics

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent source/tests/docs child of #2161 `9f255b6fa006f2fec79e48f09e303f2d2907a1a3`.

`compute_backtest_metrics` rejected nonfinite *individual* net trade PnLs, yet could return an infinite aggregate PnL, cost total, profit factor or drawdown when individually finite trade values overflowed during summation/division. Such evidence cannot be safely serialized or treated as finite financial metrics. Validate exact ordinary numeric positive starting equity (reject Boolean, opaque, huge integers), then check every computed float metric for finiteness before returning. No clipping or fabricated profitable values; legitimate finite no-trade and regular metrics remain unchanged.

Three synthetic source-defined regression methods cover invalid starting equity, finite-trade sum overflow, and overflow from aggregate costs, profit factor or drawdown. **6,904 cumulative proposed methods.** Exact-head Phase3/full historical-general CI and scoped financial evidence review required. No real bars, market performance, protected annual research, broker activity or profit is claimed.

Phase8A blockers #779/#820/#821 and eight external security proofs still MISSING; protected 2023/run385/attempt1, later research, Strategy V1 economic qualification, shadow/demo/Phase10/11, installed GitHub ref/workflow/ruleset/runner mutations and live funds remain BLOCKED.
