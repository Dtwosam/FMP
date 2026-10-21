# DEC-2005 — Source-engine close identifier parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2253 `983651844c2f0eaab4688d78707868e39d6fb34a`.

The Phase3 engine's `fill_entry` records `position.position_id = intent.decision_id` and its close writer emits `TradeRecord.trade_id = position.position_id` alongside `decision_id = position.decision_id`. For an artifact explicitly identifying the installed source engine, a self-rehashed trade whose trade_id diverges from its decision_id is not a source-compatible execution record. The optional audit previously enforced uniqueness and printable bounded identifiers but did not reconcile their version-specific equality.

Enforce `trade_id == decision_id` only for `run_identity.backtest_engine_version == BACKTEST_ENGINE_VERSION`; synthetic/other-version runs remain unaffected. Correct the preexisting synthetic source-engine checkpoint fixture to reflect the real engine's identifier contract. Add three source-defined test methods for a valid versioned source run, self-rehashed wrong trade ID, and generic synthetic compatibility.

**7,115 cumulative proposed source-defined methods** (+3), pending exact-head Phase3 and full historical/general suites. Do not relabel #2248–#2251 failed full regressions. The #2253 exact-head suite must still be checked. No independent provenance or broker claim follows from internal equality checks.

Phase8A security blockers #779/#820/#821 and eight independently provided external proofs still blocked; no protected annual research, installed runner/ref/workflow change, strategy promotion, broker trades, merges or real capital.
