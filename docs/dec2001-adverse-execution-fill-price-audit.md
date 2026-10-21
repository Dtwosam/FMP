# DEC-2001 — Adverse-only fill price audit for stored trades

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2249 at `1312bcfa5f2058666439974f3bf6eb15b2178373`.

The Phase3 source cost/execution engine only calls adverse slippage: a BUY execution price is at least its reference, and a SELL execution price is at most its reference. LONG trades enter by buying (execution entry>=reference) and exit by selling (execution exit<=reference); SHORT trades reverse both inequalities. Previously a rehashed `trades.jsonl` could claim a favorable execution fill while retaining per-row net PnL/cost arithmetic and manifest SHA-256 consistency.

Validate LONG and SHORT source-compatible entry and exit price order after finite-positive domain checks, before economics. Equal values (zero modeled slippage) remain acceptable. Three source-defined methods cover normal equal-reference long/short, forged favorable long entry/exit, and forged favorable short entry/exit after updating manifest hashes.

**7,104 cumulative proposed source-defined methods** (+3), not proven full-CI passing. This does not independently validate reported quote prices or calculate brokerage fill quality; only enforces source internal adverse-slippage direction. Own exact-head Phase3 + complete historical/general regressions and review mandatory; older failed CI records remain unchanged.

Phase8A #779/#820/#821 and eight external security proof packages outstanding. No protected research, trading, installed workflows/refs/runners, strategy promotion, merges or real capital. **DRAFT NEVER MERGE NEVER PROMOTE.**
