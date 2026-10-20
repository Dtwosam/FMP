# DEC-1929 — Reconcile published trade-count and net-PnL metrics

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One exact-parent source/tests/docs child of PR #2177 at `f575a13f5c169ec6d1d7e347b4f0a2fc443be202`.

`write_backtest_artifacts` previously accepted any ordinary `metrics` mapping; a synthetic run could publish a nonmatching `trade_count` or `net_pnl_usd` alongside its trade JSONL, each individually well-formed and digest-hashed. Reject nonfinite actual aggregate trade PnL and, **when those metric fields are supplied**, enforce exact ordinary integer count and ordinary finite numeric net PnL equal to the published trade ledger's deterministic `sum`. Preserve older intentionally minimal synthetic metrics dictionaries that omit these keys. The engine's normal `compute_backtest_metrics` output uses the same sum; this is a limited consistency check, not independent trading-performance validation.

Three synthetic source-defined test methods cover mismatched count, forged net PnL and positive reconciled/zero-trade controls with no I/O on failures. **6,948 cumulative proposed methods**. Own exact-head Phase3/full historical-general CI and independent qualified evidence review mandatory.

Phase8A #779/#820/#821 and eight external security proof packages still MISSING. Accepted annual catalogue ends 2022/run384; protected 2023/run385/attempt1, future annual research, Strategy V1 economic qualification, shadow/demo/live, broker capital and installed workflow/ref/ruleset/runner changes BLOCKED. No protected dispatch, orders, money or profit.
