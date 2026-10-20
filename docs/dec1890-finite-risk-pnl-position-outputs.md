# DEC-1890 — Finite realized P&L and bounded synthetic risk position sizing

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2138 `5ee87ae99882a7c6f57faa786d62c40e9ba8dec0`.

Even finite synthetic FX prices and positive integer positions can yield a nonfinite *derived* Decimal-to-float result, especially for USDJPY conversion where `abs(entry-stop)/stop` and `quote_pnl/exit` may be extreme. Likewise, a tiny stop distance and huge yet finite dollar budget can produce a nonsensically large integer unit count. Require that converted synthetic risk loss and P&L stay finite, translate numeric overflow into controlled ValueError and reject calculated sizes above the signed 63-bit positive-unit safety limit. Keep ordinary small EURUSD/GBPUSD/USDJPY sizing, JPY conversion and signed P&L semantics unchanged.

Three new Phase3 test methods (**6,847 cumulative proposed source-defined**) cover extreme position sizing, nonfinite converted JPY loss and nonfinite realized P&L on artificially extreme synthetic numbers. These tests are contract stress checks, not market forecasts, broker orders, profitability or security attestation. All proposed changes remain unmerged and require exact-head Phase3/full historical/general CI plus independent scoped risk review.

Accepted Phase8A catalogue ends 2022/run384. Protected 2023/run385/attempt1, later annual research, Strategy V1 economics, shadow/demo/live capital and installed GitHub ref/workflow/ruleset changes remain BLOCKED. All eight independent proof packages under #779/#820/#821 are MISSING.
