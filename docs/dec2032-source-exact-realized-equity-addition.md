# DEC-2032 — Exact source realized-equity addition

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2280 at `df7133f29f577c2b2e93fcf14f95d236fb0b6c34`.

The installed Phase3 engine records each realized trade PnL through `record_realized_pnl`, which calculates `state.risk_equity_usd + pnl_usd` before storing the updated `RiskState`. The same immediately preceding and updated risk-state values are recorded as `risk_equity_before_usd` and `risk_equity_after_usd` on the `TradeRecord`. DEC-2002 compared the stored after amount against that same addition with `math.isclose`, admitting a small independently rehashed drift in a field directly copied from the engine.

For the exact installed source-engine version only, require direct numeric equality for `risk_equity_after_usd == risk_equity_before_usd + net_pnl_usd` after finite arithmetic. Keep generic/other-version reporting with its existing relative and absolute tolerance. Existing exact source checkpoint transition witnesses remain separate.

Three source-defined methods verify valid EURUSD LONG and USDJPY SHORT source transitions, reject a self-rehashed 1e-9 drift in reported source after-equity, and retain generic approximate-equity compatibility. **7,210 cumulative proposed source-defined methods** (+3). The exact-head Phase3 and full historical/general regression suites must separately pass; no pending or previous failed check is treated as green. Internal arithmetic is not independent broker or data authentication.

Phase8A #779/#820/#821 and eight outstanding independent external security proof packages remain blocked. No protected annual research, installed workflow/ref/runner changes, strategy promotion, brokers, orders, merges or real capital.
