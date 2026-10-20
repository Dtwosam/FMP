# DEC-1932 — Reconcile explicit execution costs to published trade ledger

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One exact-parent source/tests/docs child of PR #2180 at `976aebf8fdabbf4cee630fd52c3b43e29dbd1c9c`.

`write_backtest_artifacts` already rejects mismatched optional reported `trade_count` and `net_pnl_usd`. It previously allowed metrics to disagree with `slippage_cost_usd`, `commission_cost_usd`, `financing_cost_usd` and `total_explicit_cost_usd`, even when each number individually looked finite. Recompute finite aggregate costs from the exact trade ledger being published, compare each **supplied** metric to the deterministic per-trade sum and combined cost, and refuse mismatches before filesystem mutation. Preserve intentionally sparse synthetic metrics maps and legitimate negative financing credit.

Three synthetic source-defined methods cover wrong cost claims, untyped/nonfinite/overflowed cost values and a positive financing-credit reconciled control. **6,956 cumulative proposed methods**. Must pass own exact-head Phase3/full historical-general CI and independent financial-evidence review. This strengthens internal consistency; it does not prove source quotes, cost model realism or investment returns.

Phase8A #779/#820/#821 eight independent security proof packages remain MISSING/BLOCKED. Protected 2023/run385/attempt1 and future annual research, Strategy V1 economics, shadow/demo/Phase10/11, live brokers/capital, installed GitHub workflow/ref/ruleset/runner changes remain unauthorized. No protected execution or real trading.
