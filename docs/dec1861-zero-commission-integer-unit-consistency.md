# DEC-1861 — Reject malformed unit sizes in zero-commission backtests

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2108 `c5aedc3ce8b70598f90c9251f7d065abcbd02b6f`.

`ZeroCommission.cost_usd` historically returned 0.0 without looking at its required `units: int` input, potentially hiding fractional, Boolean or corrupted position sizes during synthetic hypothetical backtests. Following the scoped DEC-1860 fixed-commission correction, enforce the same `type(units) is int` contract in the zero-commission model. Allow signed whole integers and zero, keeping the returned cost exactly 0.0 and configuration serialization unchanged.

Three new Phase3 cost tests (6,766 cumulative proposed source-defined methods) cover malformed units, nonfinite/nonnumeric inputs and normal signed whole-unit behavior. This is a proposed pure backtester semantic validation subject to separate scoped code review and full regression; it is **not** evidence of trading profits or permission to run protected annual market research. `ZeroFinancing` remains unchanged and requires separate contract evaluation.

All eight independent administrator/ref/runner/inventory/human security proofs in #779/#820/#821 remain MISSING. Annual-first evidence stops 2022/run384; protected 2023/run385/attempt1, Strategy V1 approval, shadow/demo/live, installed workflow/ref/ruleset changes and real-money trading remain BLOCKED. No merge or promotion from this draft.
