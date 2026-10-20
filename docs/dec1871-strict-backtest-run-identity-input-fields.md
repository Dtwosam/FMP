# DEC-1871 — Strict typed, printable Phase3 backtest identity fields

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2118 `9487a25ed579cea171e9274b6dcd329be57e2b60`; pure backtest configuration validation only.

The Phase3 `BacktestConfig` constructor previously called `.strip()` on fields that were annotated as string but not runtime validated. Passing a list, `None` or other type can produce uncaught exceptions. Embedding NUL, tabs, newlines or terminal escape characters in a manifest ID, schema/version/timeframe or commit identity can contaminate human audit logs and make the reported run provenance harder to reconcile. An unhashable execution timing mode can also escape with an unsupported TypeError rather than the existing fail-closed ValueError.

Require exact ordinary strings, non-blank content and no ASCII C0/DEL control characters for `processed_data_manifest_id`, `schema_version`, `timeframe` and `code_commit`; keep normal source labels intact. Require an ordinary string in the existing approved set for `execution_timing_mode`. Four new Phase3 regression tests (**6,796 cumulative proposed source-defined methods**) cover malformed types, control characters, unhashable timing modes and normal synthetic metadata.

This is not proof of an authenticated historical manifest, reviewed installed runner, strategy expectancy or trading permission. The code remains an unmerged, separately reviewable draft requiring exact-head Phase3/full historical/general CI and scoped human assessment. Eight independent external security/inventory/human requirements #779/#820/#821 remain MISSING; protected 2023/run385/attempt1, later annual research, demo/live/broker orders and capital remain BLOCKED.
