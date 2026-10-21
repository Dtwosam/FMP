# DEC-2020 — Source NO_TRADE rejection timing and scheduling restrictions

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2268 at `63eab1e009fdd6b551a1c77d9aa8f883809e2157`.

In the installed Phase3 `run_backtest` implementation, an explicit `Direction.NO_TRADE` decision takes the early rejection path immediately, setting `evaluated_timestamp_utc = decision_timestamp_utc` and `code = NO_TRADE`. The source `_scheduled_exit_map` rejects a scheduled exit for a NO_TRADE decision before execution. The optional artifact auditor formerly checked rejection timestamp ordering and allowed code values but did not enforce these exact source-specific semantics.

For the exact installed source version only, require a NO_TRADE rejection's evaluated instant to equal its original decision instant and prohibit a scheduled-exit descriptor naming the same decision. Other rejection codes and generic synthetic/other-engine reports retain existing behavior.

Four source-defined test methods: valid zero-trade source NO_TRADE rejection, self-rehashed delayed NO_TRADE evaluation that passes digest verification, source NO_TRADE with prohibited scheduled-exit identity, and generic delayed NO_TRADE/schedule compatibility. **7,168 cumulative proposed source-defined methods** (+4). This verifies internal source semantics only, not external price or order outcomes. Own exact-head Phase3 and full historical/general regressions are required; previous failed suite results remain failed.

Phase8A #779/#820/#821 and eight independent external security proofs remain outstanding. No protected annual research, workflow/ref/runner mutations, strategies promoted, brokers, orders, real capital or merges.
