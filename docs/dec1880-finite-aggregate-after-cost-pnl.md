# DEC-1880 — Reject aggregate nonfinite economics before realized equity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2127 `7472ce8ae1b7f0b540cf0c12e7835248ea3d06c7`.

Custom commission values can each be positive and finite but **their sum can overflow**: two execution-side costs of `1e308` yield infinite combined commission, even though DEC-1879's individual entry/exit checks pass. The engine previously subtracted that infinity from trade gross P&L and could contaminate the realized risk-equity path.

Add a finite check on gross P&L, slipped P&L, slippage cost, combined commission, financing and net P&L **before** releasing position risk or updating realized equity. The guard raises a controlled ValueError rather than recording infinite profit/loss. Financing credits remain allowed when finite. Two new tests (**6,819 cumulative proposed source-defined**) use invented EURUSD bars to provoke overflow from individually finite custom charges and confirm ordinary finite synthetic costs still satisfy the net accounting identity.

This does not validate actual market cost models, investor returns or Strategy V1 expectancy. All work is source-only unmerged draft requiring its own Phase3/full CI and independent code review. Phase8A protected run385/attempt1 and later research, shadow/demo/live trading and real money remain BLOCKED. Issues #779/#820/#821 and eight external administrator/ref/runner/inventory/human proofs remain MISSING. No installed workflow/ref/ruleset or broker mutation.
