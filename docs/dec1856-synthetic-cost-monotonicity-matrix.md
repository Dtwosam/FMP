# DEC-1856 — Fixed synthetic three-pair slippage and commission monotonicity tests

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent test-only child of #2102 `e4550823eb75ab6102107b442b92884e87246064`.

DEC-1855 documents an untyped `OrderSide` branch and fractional commission-unit contract issue without changing production code. Add four deterministic **synthetic-only** test methods exercising normal correct-enum behavior of `fmp.backtest.costs` across EURUSD, GBPUSD and USDJPY.

- For each supported pair, fixed representative quote and a deterministic 0/0.25/0.5/1/3 pip grid, validate BUY fills move only upward, SELL fills only downward, with pip-accurate monotonic displacement.
- For per-side commission rates of $0/$10/$30 per million, verify whole-unit cost is nonnegative, monotone with absolute position size and symmetric for deliberately supported signed positions.
- Reject negative, nonfinite NaN/Infinity slippage and a nonpositive displaced SELL fill.
- Retain exact `BLOCKED_NO_STRATEGY_OR_TRADING_PERMISSION` and empty `allowed_actions` in the related offline diagnostic.

The numerical values are invented test constants, **not downloaded price bars, broker quotes, trades, live execution or evidence of after-cost expectancy**. These tests do not approve Strategy V1 or change the production-side input flaw: its remedy still needs a separate scoped code/security review and ordinary regression. Four new test methods bring cumulative **6,756 proposed source-defined methods**.

Accepted annual-first catalogue ends at 2022/run384; protected 2023/run385/attempt1 and all later research are BLOCKED pending eight independently witnessed security/inventory/human approval packages, #779/#820/#821 OPEN. No installed workflow/ref/ruleset mutation, broker/demo/live order, real money or profit. Exact-head Phase3/full CI and qualified review required.
