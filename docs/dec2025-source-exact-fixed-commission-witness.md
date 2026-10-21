# DEC-2025 — Exact built-in fixed-rate source commission witness

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2273 at `c6ac2293827dd9181c55d7d0b61913abfc16b76e`.

The installed `FixedCommissionPerMillion.cost_usd(units)` computes `abs(units) / 1_000_000 * usd_per_million_per_side` for **each** side, and the engine adds the two identical per-side values to publish `commission_cost_usd`. DEC-2009 independently reconstructs the expected amount using the same positive integer units and declared built-in rate, but admitted `math.isclose` drift (1e-8 absolute tolerance) even though this source computation is deterministic and copied without rounding.

For the exact installed engine version and recognized `fixed_per_million_per_side` config, retain finite validation and require **exact numeric equality** between the reported aggregate commission and the recomputed pair of per-side fees. Keep custom/other-provider fee models unaffected and retain source zero-commission exact checks.

Four additional source-defined test methods cover valid zero and positive fixed rates, self-rehashed near-equal commission/financing swap preserving net PnL under a positive fixed rate, near-equal forged commission under a declared zero fixed rate, and generic synthetic-report flexibility. **7,186 cumulative proposed source-defined test methods** (+4). Own exact-head Phase3 and full historical/general regressions required; old #2266–#2269 full failures remain failed. This is internal source-model economics, not authenticated broker fees, trades or profits.

Phase8A #779/#820/#821 and eight independent external security proof packages remain unresolved. No protected annual research, installed workflow/ref/runner modifications, strategy promotion, merges, broker orders or real capital.
