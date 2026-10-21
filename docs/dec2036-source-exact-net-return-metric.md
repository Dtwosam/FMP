# DEC-2036 — Exact source net return from canonical ledger

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2284 at `c065a657bf6c2f5d8499a17fd4db5064d286dd70`.

The installed source's `compute_backtest_metrics` calculates `net_return` as `net_pnl_usd / starting_equity_usd` using the same numeric values published in the run identity and source economic metrics. The optional audit already computes that ratio from canonical trade evidence but tolerated a 1e-12 discrepancy for generic reports. After DEC-2034 ensures installed-source ledger net-PnL aggregates match exactly, there is no separate rounding in the source ratio that justifies a near-equal self-rehashed net return.

For exact installed-source reports with an optional `net_return` metric, require direct numeric equality to the canonical ledger net divided by the published starting equity. Preserve generic and other-version tolerance and existing positive/finite starting equity validation. No additional mandatory metric is introduced.

Three source-defined tests cover valid derived net return, self-rehashed +1e-13 net return drift that passes hash verification but fails the optional source audit, and generic compatibility. **7,223 cumulative proposed source-defined methods** (+3). Exact-head Phase3 and full historical/general checks required; older failures remain recorded and running suites remain unconfirmed.

Phase8A issues #779/#820/#821 and eight independent external security proof packages remain blocked. No protected annual research, installed runner/ref/workflow changes, merging, broker orders, strategy promotion or real capital.
