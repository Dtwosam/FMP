# DEC-1908 — Monotone UTC-day risk state

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Source/tests/docs one-commit exact-parent child of #2156 at `2cded478f394da4e0b3fe75f640629d4c95cb3a1`.

`roll_utc_day` previously treated a **backward** UTC date like a new day and reset `day_realized_pnl_usd`, `daily_halt_active` and the halt timestamp. That allowed an accidental or hostile backdated risk-policy call to erase the later day's loss halt. Reject an earlier `timestamp_utc.date()` with a controlled `ValueError` before mutating any risk-state field. Preserve idempotent same-day calls and forward rollovers. A full intraday timestamp-order contract is separate and not claimed here.

Three synthetic methods verify backdating cannot clear an active loss halt; realized PnL fails atomically; and directional risk assessment cannot roll backward or remove an existing reservation. **6,889 cumulative proposed source-defined methods.** Own Phase3 and full historical/general CI, independent qualified review and economic/provenance checks remain required. No results inherited from previous commits.

All eight external administrator/ref/runner/provenance/inventory/human authorization proof packages remain MISSING under Phase8A issues #779/#820/#821. Protected 2023/run385/attempt1, future annual research, Strategy V1 economic approval, shadow/demo/Phase10/11 and broker/live capital remain BLOCKED. No protected data, workflow/runner/ruleset installation, order or money was touched.
