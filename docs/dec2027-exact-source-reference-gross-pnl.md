# DEC-2027 — Exact source reference-price gross-PnL witness

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2275 at `81bc6afcc94962c620b4ba7664f8c7389bf85b66`.

The installed Phase3 engine records `gross_pnl_usd = pnl_usd(symbol, direction, units, entry_reference_price, exit_reference_price)` directly from its source formula. DEC-2006's optional auditor recomputes the same source routine from published trade fields but admitted small `math.isclose` drift, which is not part of the source writer's deterministic formula. Such a near-equal amount can also be rehashed while staying within the net-PnL arithmetic tolerance.

For exact installed source-engine reports, preserve source `pnl_usd` calculation and its error classification but require the stored source gross amount to match the independently recomputed source gross **exactly**. Generic synthetic/other-engine report economics remain governed by the older broad net arithmetic and domain checks. This verifies only internal source semantics; the stored market reference prices are not authenticated.

Four new source-defined test methods: valid EURUSD LONG, GBPUSD SHORT and USDJPY converted gross amounts; self-rehashed 1e-9 EURUSD gross drift; self-rehashed 1e-9 USDJPY converted gross drift; and generic synthetic near-equal gross compatibility. **7,194 cumulative proposed source-defined methods** (+4). Own exact-head Phase3 and full historical/general tests required. Prior failed #2266–#2269 suites remain failures; earlier pending suites require independent verification.

Phase8A #779/#820/#821 and eight independent external security proof packages remain blocked. No protected annual research, installed workflows/refs/runners, strategy promotion, merges, broker orders or real capital.
