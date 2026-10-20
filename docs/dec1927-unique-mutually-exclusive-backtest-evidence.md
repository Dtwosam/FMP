# DEC-1927 — Unique and mutually exclusive backtest decision evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One exact-parent source/tests/docs child of PR #2175 at `283d7a80383c32a07148b55ec7ed9c0279ec4612`.

A manually constructed `BacktestRun` previously could contain duplicate `TradeRecord.trade_id`, repeated trade `decision_id`, repeated rejection decision identities, or simultaneous trade and rejection records for the same decision. A manifest checksum would still be generated, and counts could be inflated. After prior structural/numeric validation, refuse duplicates and mutually contradictory decision outcomes before writing any artifact directory. Preserve the canonical engine invariant of one trade *or* one rejection per input decision.

Three synthetic source-defined regression methods cover duplicate trade IDs and decision IDs, duplicate/conflicting rejection identity, and a valid distinct trade+rejection control. **6,942 cumulative proposed source-defined test methods**. Own exact-head Phase3/full historical-general CI and independent reporting audit remain mandatory. Not a claim of profitable economics, authentic data lineage or protected runner security.

Phase8A external #779/#820/#821 and eight independent administrator/ref/installed early workflow/real OS/provenance/2023 inventory/human authorization proofs MISSING. Protected 2023/run385/attempt1, later annual research, Strategy V1 economics, shadow/demo/Phase10/11, broker/live money and installed GitHub workflow/ref/ruleset/runner changes BLOCKED. No protected dispatch, trade or capital movement.
