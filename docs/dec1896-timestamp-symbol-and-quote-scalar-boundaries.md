# DEC-1896 — Fail-closed synthetic quote timestamp, symbol and numeric scalar contract

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2144 `c9d608285239a36b0f3d34a87ad1314656d61ff9`.

The Phase3 quote contract previously trusted `timestamp_utc`, `symbol` and `bid/ask` scalar type annotations without checking runtime types. Nonstr datetime timestamps and unhashable symbols could throw arbitrary AttributeError/TypeError rather than a controlled ValueError. Python treats `True` as 1, allowing an invalid Boolean quote price; very large integer prices trigger OverflowError inside `math.isfinite`. Reject these malformed values in three shared validators while preserving the exact three FX symbols, UTC offset requirement, finite positive ordinary int/float inputs and OHLC/spread consistency checks.

Four new source-defined Phase3 methods (**6,861 cumulative proposed**) cover malformed timestamps, nonstring/unhashable symbols, Boolean/nonfinite type problems and ordinary synthetic quote behavior. Existing `Decision` and `ScheduledExit` admission rules are left for separate review. This is unmerged synthetic backtest contract code, not real market data, an OS/administrator witness, verified alpha or trading authorization.

External proof packages under #779/#820/#821 remain MISSING. Phase8A accepted research ends 2022/run384; protected 2023/run385/attempt1, future-year research, Strategy V1, shadow/demo/live broker orders, capital and installed GitHub workflow/ref/ruleset changes remain BLOCKED. Exact-head Phase3/full regression and independent scoped code review required.
