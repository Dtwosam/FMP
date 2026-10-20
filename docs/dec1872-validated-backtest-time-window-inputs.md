# DEC-1872 — Controlled type and UTC admission for backtest time windows

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2119 `f755ae60873df773d0281bb0826c9dad0d57a518`.

`BacktestConfig` already requires UTC request-window boundaries and an end that is not before the start. Its `_require_utc` helper accessed `.tzinfo` on an unvalidated input; a string, date, mapping or `None` could raise AttributeError before the documented time-window ValueError. Require a real `datetime` before evaluating UTC offset so malformed requested_start_utc/requested_end_utc values fail under the same declared contract. Normal UTC-aware intervals and same-time window semantics remain unchanged.

Three new deterministic test methods (6,799 cumulative proposed source-defined) cover non-datetime values, naïve/non-UTC timestamps and valid UTC windows. This is not protected research, historical source validation or market data processing. It is an unmerged Phase3 cost/timing configuration proposal requiring exact-head Phase3 and full historical/general regression and scoped human review.

Accepted Phase8A annual catalogue through 2022/run384 only. Protected 2023/run385/attempt1, later-year annual research and Strategy V1 economics, shadow/demo/broker/live capital remain BLOCKED. Eight independent #779/#820/#821 administrator/ref/runner/provenance/inventory/human proofs still MISSING. No installed workflow/ref/ruleset security settings were changed.
