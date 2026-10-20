# DEC-1944 — Fail-closed derived metric arithmetic overflow

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source/tests/docs child of #2192 `75bd82002f358317f654f2541c8561b9e19d3168`.

`compute_backtest_metrics` validates finite individual trades and aggregate metrics, but a Python `OverflowError` raised during eager metric-dictionary expression evaluation (e.g. an extreme return or ratio) could exit before the final nonfinite sweep. Wrap the final metric construction in a narrow OverflowError-to-`ValueError("backtest metric calculation must remain finite")` translation. Preserve all normal values, undefined metric None semantics, and existing metric schema. One synthetic method covers a valid individual large net PnL divided by a tiny but positive starting equity and expects controlled rejection. **6,972 cumulative proposed source-defined methods**. Own exact-head Phase3/full historical/general CI and scoped financial code review required; no actual economic claims.

Historical #2178 full [39496009035](https://github.com/Dtwosam/FMP/actions/runs/39496009035) and #2190 full [39498712521](https://github.com/Dtwosam/FMP/actions/runs/39498712521) remain FAILED. Earlier dependent repairs #2189 (nonfinite classification) and #2192 (cost subtotal preflight) are source proposals and do not change their historical outcomes.

Phase8A #779/#820/#821 eight independent security proof packages remain MISSING/BLOCKED, accepted research still ends 2022/run384; protected 2023/run385/attempt1, later research, Strategy V1 economics, shadow/demo/live, broker capital and installed GitHub ref/workflow/ruleset/runner changes remain unauthorized. No protected data access, dispatch, merge, trading or money.
