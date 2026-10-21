# DEC-2024 — Exact-copy initial equity checkpoint witness

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2272 at `186ea0ac446c9cb1a0fa23eb362ef357f92b4163`.

The installed Phase3 engine initializes `RiskState` from `config.starting_equity_usd` and writes `EquityCheckpoint(bars[0].timestamp_utc, config.starting_equity_usd)`; its `run_identity` publishes the **same** `config.starting_equity_usd` numeric value. DEC-2003 previously used `math.isclose` when reconciling the initial source checkpoint against run identity, admitting small self-rehashed discrepancies despite both being copied from one source value. Subsequent DEC-2008 uses exact checkpoint ledger transition witnesses already.

For exact installed source-engine reports with a declared starting equity, require direct numeric equality for this source-copied initial checkpoint. Do not tighten comparisons for generic synthetic/other-engine envelopes. Preserve existing finite-positive starting-equity classification before any ledger chaining, exact source close witnesses and the existing error message.

Three new source-defined tests cover valid zero-trade source initial equality, a self-rehashed 1e-9 discrepancy inside the old tolerance that passes manifest verification but fails source audit, and generic synthetic tolerance preservation. **7,182 cumulative proposed source-defined methods** (+3). Own exact-head Phase3 and full historical/general suite required; the older failed #2266–#2269 runs remain failures. No authenticated external quotes, broker trade provenance or performance claims.

Phase8A #779/#820/#821 plus eight independent external security proof packages remain blocked. No protected annual research, installed workflows/refs/runners, strategy promotion, merges, broker orders or real capital.
