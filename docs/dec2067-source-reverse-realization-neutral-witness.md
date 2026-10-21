# DEC-2067 — Source realization order reversed around a neutral close

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2315 `f0b63787cf1369f4861ff29a0f68caa3b4797909`.

DEC-2066 proves valid same-UTC winning, flat and losing outcomes in that realization order. This independent source witness realizes the **losing close first**, then the flat close, then the winning close; the canonical writer still publishes A-WIN, M-FLAT, Z-LOSS by trade ID. The engine's four checkpoints prove LOSS/FLAT/WIN realization including a repeated equity checkpoint for the breakeven. Published metrics remain determined from canonical trade rows: win rate 1/3, finite positive profit factor, defined win/loss averages, and single-trade winning/losing streaks. The same ledger must not be rejected merely for different source realization order.

Five source-defined tests accept that valid reverse-realization report, reject a manifest-rehashed missing first-loss checkpoint, and reject three forged metrics (half win rate, 1e-9 average-win drift, and zero profit factor). Manifest digest verification precedes the separate opt-in semantic audit. Production engine/reporting code unchanged.

**7,339 cumulative proposed methods** (+5), pending own exact-head Phase3 and full historical/general checks. Earlier failed runs remain failed, and latest full-green parent remains #2313 until descendant completion. Phase8A #779/#820/#821 plus eight independent security proofs remain blocked. No protected annual research, workflow/ref/runner mutations, merges, strategy promotion, broker orders or real capital.
