# DEC-1934 — Reconcile win rate, averages, expectancy and streak economics

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit source/tests/docs child of PR #2182 at `499612c7e439b49dadcd041302ef266d2bd32c83`.

The writer now reconciles primary trade-ledger totals and profit factor, but untrusted synthetic `BacktestRun.metrics` could still assert a false `win_rate`, `average_win_usd`, `average_loss_usd`, `expectancy_usd` or winning/losing streak. Recompute these source-defined deterministic metrics from the exact ordered trade ledger and require every **supplied** field to match its canonical numerical/undefined representation. Preserve None for undefined zero-trade averages/rates, exact integer streak types, and intentionally sparse synthetic metrics maps.

Three synthetic source-defined methods verify refusal of forged distribution numbers; untyped/undefined values in no-trade reports; and positive full two-trade/zero-trade controls. **6,962 cumulative proposed test methods**. Own exact-head Phase3/full historical-general CI and qualified financial review mandatory; internally reconciled metrics do not demonstrate authentic data, realistic transaction costs or profitable strategy.

Phase8A external #779/#820/#821 and eight independent security proof packages remain MISSING/BLOCKED. Accepted annual catalogue stops 2022/run384; protected 2023/run385/attempt1, later annual research, Strategy V1 economics, shadow/demo/Phase10/11 brokers/live funds and installed GitHub ref/workflow/ruleset/runner changes remain unauthorized. No protected work, trading or money.
