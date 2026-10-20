# DEC-1883 — Fail closed on non-datetime risk-policy UTC inputs

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2130 `84d8c83d96e053a2aaf3b97c1959a35afa11b22a`.

The risk-policy `_require_utc` helper accessed `.tzinfo` on values before checking their declared `datetime` type. Direct calls to `roll_utc_day` or `record_realized_pnl` with `None`, a string, mapping or ordinary `date` could produce AttributeError rather than the same documented UTC ValueError applied to naïve/non-UTC datetimes. Require `isinstance(value, datetime)` before UTC offset validation. This matches the proposed Phase3 backtest configuration datetime boundary, but is reviewed separately for the risk subsystem.

Three new source-defined Phase3 methods (**6,827 cumulative proposed**) verify malformed rolling/realization timestamps fail without updating risk or day state and valid UTC day updates continue unchanged. No real broker time synchronization, protected data, after-cost Strategy V1 expectancy or real-money risk enforcement is established.

Accepted annual-first research remains 2022/run384 only; protected 2023/run385/attempt1, future research, shadow/demo/live/broker actions, workflow/ref/ruleset/security edits and capital BLOCKED. External independent #779/#820/#821 administration, OS runner, provenance, fresh one-shot and human approval packages remain MISSING. Exact-head Phase3/full CI and qualified human code review required before promotion.
