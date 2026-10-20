# DEC-1933 — Reconcile gross-profit, gross-loss and profit-factor evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One exact-parent source/tests/docs child of PR #2181 at `80810f5ae4be8e9adfbd07f76bc742ff6bcfa7c6`.

The artifact writer reconciled net PnL and explicit cost totals, but a supplied summary could still publish a fabricated `gross_profit_usd`, `gross_loss_usd` or `profit_factor`. Recompute the deterministic wins/losses from the trade net-PnL ledger, enforce finite aggregates and validate each **supplied** metric against them. Preserve `profit_factor=None` whenever no loss makes the ratio mathematically undefined, including zero-trade inputs; reject a numeric ratio in that case. This does not make gross-profit claims independently trustworthy without real market/provenance evidence.

Three synthetic tests cover forged profitability, a profit factor with no loss denominator, and valid normal/undefined-ratio controls. **6,959 cumulative proposed source-defined methods**. Exact-head Phase3/full historical-general CI and qualified independent financial review mandatory.

External Phase8A blockers #779/#820/#821 and eight independently attested security proofs MISSING; accepted annual catalogue ends 2022/run384. Protected 2023/run385/attempt1, future discovery, Strategy V1 economics, shadow/demo/live broker funds and installed ref/workflow/ruleset/runner changes BLOCKED. No protected research, order or money movement.
