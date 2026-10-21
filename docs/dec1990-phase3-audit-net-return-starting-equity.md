# DEC-1990 — Cross-check net return against source starting equity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2238 `82ed7241302632caac8f492c9e21b11513937e62`.

The real Phase3 backtest engine includes `starting_equity_usd` in the serialized run identity and computes `metrics.net_return = net_pnl_usd / starting_equity_usd`. The opt-in artifact audit previously reconciled the stored net PnL trade ledger and numerous other metrics, but left net return independently forgeable through a self-rehashed `metrics.json`. The low-level manifest verifier checks only checksums, not source authenticity.

When `summary.json.run_identity` contains the source-defined starting-equity field, the auditor now checks exact ordinary finite positive numeric starting equity and independently compares optional stored net return against audited net PnL divided by that base. It preserves legitimate synthetic evidence that omits the starting equity identity, and doesn't claim externally authenticated starting capital.

Three new synthetic source-defined methods cover writer-consistent return, forged/rehashed 50% return, and positive-numeric starting-equity domain. **7,063 cumulative proposed methods** (+3). Exact-head Phase3/full historical-general suite required. PRs #2234–#2237 full regressions remain FAILED; #2238 is not full-green until its own suite completes.

No main ref/workflow/runner changes, protected 2023/run385/attempt1 dispatch, broker/demo/live orders, strategy promotion, merges, or capital. Phase8A security #779/#820/#821 and eight independent external proof requirements still outstanding.
