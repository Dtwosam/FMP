# DEC-1912 — Daily-loss ledger is authoritative for risk admission

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One exact-parent source/tests/docs child of PR #2160 at `e9e756e99737256b52bb6aaa420bec5cabae2673`.

Daily risk policy previously trusted the mutable `daily_halt_active` Boolean alone. If a stale/restored state preserved a realized loss below the configured daily threshold but lost the halt Boolean, `assess_decision` could allow a new trade. Reject when **either** the halt Boolean is set **or** the current day's validated realized PnL has reached the negative daily-loss threshold. Also reject malformed, Boolean, nonfinite and overflowing `day_start_equity_usd` or `day_realized_pnl_usd` before UTC-day rollovers.

Three synthetic source-defined methods verify refused trading when the halt flag is reset despite a genuine loss ledger, refusal of contaminated day ledger values at roll/assessment, and valid subthreshold-loss trade approval. **6,901 cumulative proposed source-defined methods**. Scope is Phase3 risk-contract source; exact-head Phase3 and historical/general CI and independent qualified review mandatory. No CI outcome inherited from a parent commit.

External Phase8A blockers #779/#820/#821 and eight security proofs remain MISSING. Protected 2023/run385/attempt1 and later annual discovery, Strategy V1 economic evidence, shadow/demo/Phase10/11 live brokers/capital, installed GitHub ref/workflow/ruleset/runner changes remain BLOCKED. No protected run, broker activity, capital or verified profit.
