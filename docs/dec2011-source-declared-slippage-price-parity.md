# DEC-2011 — Declared source slippage pips and execution fill parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2259 at `1279e6693c14ea5a0232d08f107505b4bfc625f8`.

The installed Phase3 source engine applies `apply_adverse_slippage` independently to the entry and exit reference price with the same `run_identity.slippage_pips` setting, symbol pip size, and buy/sell direction. DEC-2007 rechecked reported costs against published execution prices, but a self-rehashed source report could still change the declared pip setting without changing otherwise consistent fill prices, gross PnL, slippage cost, net PnL, or checkpoints.

For reports explicitly declaring the *installed* source version **and** carrying `slippage_pips`, recompute the engine's entry and exit fills via the source's own deterministic arithmetic. Compare both exactly with serialized fill prices (direct source copies). Reject mismatches. Preserve optional synthetic identity fields and do not impose engine-specific slippage on generic or other-version reports. Other semantic, cost, ledger, digest and canonical-format checks remain unchanged.

Three new source-defined test methods cover: positive declared model parity for EURUSD LONG, GBPUSD SHORT, and USDJPY LONG; a rehashed false `slippage_pips` identity that passes checksum verification but must fail optional source audit; and generic synthetic report compatibility.

**7,133 cumulative proposed source-defined test methods** (+3). This draft requires *its own exact-head* Phase3 acceptance and full historical/general regression checks. An unconfirmed or failed check is not green; older failing CI runs remain unchanged. These checks verify only internal source-contract consistency, **not** independently authenticated external quotes or any real trading outcome.

Phase8A blockers #779/#820/#821 and eight independent external security proof packages remain outstanding. No protected annual research, installed workflow/ref/runner change, strategy promotion, brokerage orders, merge or real capital.
