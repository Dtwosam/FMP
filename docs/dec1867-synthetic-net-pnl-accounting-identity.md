# DEC-1867 — Synthetic net-P&L accounting and gross-winner reversal tests

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2114 `7117804868e67b7964980c137ca88adab726ba58`.

The Phase3 engine defines realized hypothetical `net_pnl_usd = gross_pnl_usd - slippage_cost_usd - commission_cost_usd - financing_cost_usd`, and realized risk equity must advance using **net**, not gross. Add three engine-level regression methods on the existing DEC-1865 *invented* EURUSD bars and decision: require exact per-trade gross-to-net decomposition across a synthetic cost grid; require a positive invented gross P&L to become net negative under a deliberately high per-million commission rate; and verify both trade risk equity and the final equity checkpoint use the after-cost result.

These are accounting invariants, **not real market data, a trading strategy, evidence of favorable expectancy, realized income, or an authorized research deployment**. The high fee is an intentionally artificial stress input, not a broker quote. Three new proposed source-defined methods bring cumulative count to **6,783**. Costs remain subject to scoped human code review and own exact-head Phase3/full historical-general regression.

Security issue #779 and runner/ref-review drafts #820/#821 remain OPEN with eight independently authenticated proofs MISSING. Accepted annual research ends at 2022/run384; protected 2023/run385/attempt1, later discovery and selection, shadow/demo/live orders, capital, and installed ref/workflow/ruleset/runner changes remain BLOCKED. No merge or promotion from this draft.
