# DEC-2026 — Exact source-modeled slippage-cost witness

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2274 at `ce8082469f2e37c1c2eeda12785bdd63b5618a22`.

The installed Phase3 engine computes source reference gross and slipped execution PnL via the same `pnl_usd` routine, then publishes `slippage_cost_usd = max(0.0, gross_pnl - slipped_pnl)`. DEC-2007's source-version audit recomputes both PnL quantities from stored prices but admitted `math.isclose` drift in the claimed slippage cost. The installed engine serializes that exact deterministic result without intermediate rounding, so rehashed near-equal amounts are not source-compatible.

For exact installed source-engine identity only, replace the tolerance-based modeled slippage-cost comparison with direct numeric equality to `max(0.0, source_gross - slipped_pnl)` after validating the expected amount finite. Preserve generic/other-version synthetic economics flexibility and existing per-trade net reconciliation tolerances.

Four source-defined methods: positive parity for EURUSD LONG, GBPUSD SHORT, USDJPY LONG and zero-pip LONG; checksum-verified near-equal positive slipped cost; forged 1e-9 slipped cost under zero-pip source fill; and generic synthetic slight-difference tolerance. **7,190 cumulative proposed source-defined test methods** (+4). Own exact-head Phase3/full historical-general CI required; prior failed suites remain failed. These are internal source-model economics, not authenticated outside quotes, broker slips, profitability or live execution.

Phase8A #779/#820/#821 and eight independent external security proofs remain blocked. No protected annual research, installed workflow/ref/runner changes, strategy promotion, merges, broker orders or real funds.
