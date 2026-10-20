# DEC-1917 — Typed Phase3 artifact writer collections before I/O

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2165 at `a61d52acad9f9cfeb538343ce86ae3cb2fc14fe0`.

`write_backtest_artifacts` previously assumed that `run.trades`, `run.rejections` and `run.equity_checkpoints` contained real dataclass records. Malformed container values or hostile member objects could trigger incidental AttributeError or arbitrary properties while sorting/serializing output. After the canonical `BacktestRun` gate, require ordinary `tuple`/`list` of exact `TradeRecord`, `RejectionRecord` and `EquityCheckpoint` objects *before* any filesystem mutation. Existing valid empty ordinary containers and deterministic artifact bytes are unchanged.

Three synthetic regression methods cover untyped/hostile sequences with denied directory creation, hostile property getters not called, and positive valid-empty-list publication. **6,913 cumulative proposed source-defined test methods**. Must pass its own Phase3/full historical-general CI and independent scoped financial evidence review. This is not multi-file crash atomicity or real runner isolation.

Phase8A external #779/#820/#821, eight independent security proofs remain MISSING; protected 2023/run385/attempt1 and subsequent research, Strategy V1 economics, shadow/demo/Phase10/11, installed workflow/ref/ruleset/runner changes, broker orders/real money remain BLOCKED. No protected dispatch, trade or profit was created.
