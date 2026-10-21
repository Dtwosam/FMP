# DEC-2038 — Exact source profitability metric summaries

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2286 at `5db4e84b663197b5a243f414ea55209d983d459d`.

The installed `compute_backtest_metrics` derives optional `gross_profit_usd`, `gross_loss_usd`, and `profit_factor` from the net-PnL values of the canonically sorted trade sequence. The optional artifact auditor reconstructs the same profit/loss buckets and profit-factor division from published trade rows. The historical near-equality tolerance is useful for synthetic independent publishers, but the installed engine does not round these quantities separately.

For the exact installed `backtest_engine_version`, require direct equality of any present profitability metric with the reconstructed source ledger. Preserve historical tolerance for generic reports and the existing null profit-factor behavior when no losses occur. Do not change source trade execution or assert outside broker profit.

Four source-defined methods cover a source-version winning/losing ledger with matching exact gross profit/loss and profit factor; a self-rehashed 1e-9 gross-profit drift; a self-rehashed 1e-9 profit-factor drift; and generic synthetic compatibility. **7,230 proposed cumulative source-defined methods** (+4). Own exact-head Phase3 and full historical/general CI required; failed historical checks remain failed and pending results are not green.

Phase8A #779/#820/#821 and eight independent security proofs remain blocked. No protected annual research, installed workflow/ref/runner mutations, merges, strategy promotion, broker orders or real capital.
