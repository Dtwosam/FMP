# DEC-2031 — Exact source net PnL arithmetic

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent draft PR #2279 at `4aefb1c372a3ab9b21723907b9a7968e0d8afe5d`.

The installed Phase3 backtest calculates the reported `net_pnl_usd` directly as `gross_pnl_usd - slippage_cost_usd - commission_cost_usd - financing_cost_usd`, using ordinary Python float operations, with no currency rounding in between. The source audit formerly accepted near-equal reported net PnL via `math.isclose`, despite a deterministic source arithmetic result and already-exact constituent gross, modeled slippage and built-in fee checks.

For exact installed-engine reports only, require `net_pnl_usd == expected_net` after the finite check. Preserve pre-existing `math.isclose` behavior for generic synthetic or other-engine reports. Keep the same error class/message for a net arithmetic mismatch.

Three source-defined methods cover a valid combined economic record across EURUSD LONG, GBPUSD SHORT and USDJPY SHORT, a manifest-rehashed 1e-9 near-equal net PnL discrepancy rejected by the source auditor, and generic near-equal compatibility. **7,207 cumulative proposed source-defined methods** (+3). Own exact-head Phase3 and full historical/general validation are required; earlier failed runs stay failed and pending runs remain unconfirmed. Internal arithmetic is not authenticated quote, broker fee or execution evidence.

Phase8A blockers #779, #820, #821 and eight external independent security proofs remain unresolved. No protected research, installed runner/ref/workflow changes, merges, strategy promotion, broker orders or real capital.
