# DEC-1993 — Optional source-identity scalar value-domain audit

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2241 at `f4713d79e73cb4630746786f07ae6207fd0a5cd2`.

The Phase3 engine's source BacktestConfig validates supported execution timing modes, finite non-negative slippage pips and nonempty control-free identity strings (code_commit, processed_data_manifest_id, schema_version, timeframe); the run identity also publishes a backtest_engine_version string. Previously self-rehashed summary evidence could carry invalid values while the optional cross-file audit accepted the field names and digests.

For source-identity scalar fields that are present, check ordinary printable nonempty text, finite nonnegative slippage_pips excluding Boolean aliases, and execution timing mode membership in the engine's two allowed modes. Leave absent fields optional for synthetic BacktestRun fixtures and do not claim this authenticates code_commit provenance or GitHub SHA.

Four source-defined synthetic tests cover source-compatible identity, rehashed fake slippage, invalid commit strings and unsupported execution timing. **7,075 proposed cumulative source-defined methods** (+4). Exact-head Phase3/full historical and general regressions required. Historical full-regression failures remain failed; green short Phase3 alone is insufficient.

Phase8A #779/#820/#821 and eight independently supplied security proofs outstanding; no protected annual research, installed refs/workflows/runners, brokerage orders, strategy promotion, real capital or merges. **DRAFT NEVER MERGE NEVER PROMOTE.**
