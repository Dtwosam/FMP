# DEC-1991 — Audit checkpoint drawdown and recovery economics

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2239 at `997348e44b324bd96d7ee289372208f8d035969a`.

The source's `compute_backtest_metrics` starts a running peak from `starting_equity_usd`, walks chronologically published realized equity checkpoints, then computes max_drawdown_usd, max_drawdown_fraction (at the record largest USD drawdown) and recovery_factor as realized trade net PnL over max USD drawdown. A self-rehashed metrics document could previously falsely report tiny drawdowns, a false drawdown percentage or a false recovery factor while its other economics remained internally correct.

When the source-defined starting-equity field exists in summary run identity, the optional read-only audit now recomputes these three optional stored metrics from the audited chronological checkpoint sequence and ledger net PnL. It retains `recovery_factor = null` when no drawdown occurred, and does not force unprovided optional metrics or synthetic run identities without a starting-equity field. It catches non-finite interval differences and excludes Boolean fake numeric claims.

Four synthetic methods exercise a valid $300 maximum drawdown and rate, forged/rehashed dollar drawdown, forged percentage/recovery factor, and a flat curve's null recovery. **7,067 cumulative proposed source-defined tests** (+4), not an accepted independent backtest/profitability verdict. Exact-head Phase3 and complete historical/general suite required.

Phase8A security #779/#820/#821 and eight independently supplied proof requirements still BLOCKED; no protected annual research, live/demo FX orders, strategy promotion, capital, merge, or installed runner/ref/workflow changes.
