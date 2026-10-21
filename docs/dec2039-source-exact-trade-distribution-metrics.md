# DEC-2039 — Exact source trade distribution metrics

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2287 at `6b7c13bb0d0afa4822f36f2ae7a9d4e9a0375bc8`.

The installed source's `compute_backtest_metrics` calculates optional win rate, mean win, mean loss and expectancy directly from canonical `net_pnl_usd` values, with longest win/loss streaks derived from canonical exit-time/ID order. The optional auditor already recomputes the same values from published trades but uses a numeric tolerance for generic providers. The installed writer does not round those intermediate distribution values.

For reports declaring the exact installed source engine version, require direct numeric equality for the **present** float-valued distribution metrics: `win_rate`, `average_win_usd`, `average_loss_usd` and `expectancy_usd`. Preserve existing generic source tolerance and all integer-streak and null/no-trade behaviors.

Four source-defined tests: valid mixed winner/loss source metrics including longest streaks; manifest-rehashed 1e-9 win-rate drift; manifest-rehashed 1e-9 expectancy drift; and generic near-equal compatibility. **7,234 cumulative proposed source-defined test methods** (+4). Own exact-head Phase3 and full historical/general CI required; previous failures remain recorded, and queued/running checks are not passes. This only tests internal arithmetic, not external fills or profitability.

Phase8A issues #779/#820/#821 and eight external security proofs are unresolved. No protected annual research, installed workflow/ref/runner changes, strategy promotion, brokers, orders, merges or real-capital use.
