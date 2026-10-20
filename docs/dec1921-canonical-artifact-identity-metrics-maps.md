# DEC-1921 — Canonical Phase3 run-identity and metrics mapping admission

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2169 at `6ffdef4da1eeb079566666f1fa5957fa44603bf7`.

`write_backtest_artifacts` previously accepted null, list or scalar `BacktestRun.run_identity` and `BacktestRun.metrics` values and serialized them as JSON, potentially emitting a malformed but manifest-hashed artifact package. Require exact ordinary dictionaries or immutable `MappingProxyType` maps for both before any directory creation. Earlier typed record sequences, deterministic key/scalar and pre-serialization gates remain in force; compatible immutable mappings remain supported.

Three synthetic source-defined regression methods prove malformed identity or metric mappings are rejected without filesystem changes and that valid immutable maps are serialized normally. **6,925 cumulative proposed source-defined methods.** Own exact-head Phase3 and full historical/general CI plus independent financial evidence review mandatory. A manifest hash is not proof of legitimate economic research.

External Phase8A #779/#820/#821 and eight independent external security proofs MISSING. Accepted annual research ends 2022/run384; protected 2023/run385/attempt1, future catalogue, Strategy V1 economic approval, shadow/demo/Phase10/11, live broker capital and installed GitHub workflow/ref/ruleset/runner mutation BLOCKED. No protected dispatch, order, capital or profit action.
