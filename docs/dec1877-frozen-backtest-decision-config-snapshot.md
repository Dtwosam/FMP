# DEC-1877 — Snapshot caller-owned decision metadata for stable backtest identity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2124 `04d4a85722324c45a73bfee6d870bf4c8b1f76a4`.

The frozen `BacktestConfig` dataclass previously stored `decision_config` by reference. A caller could mutate their original dict after a configuration passed validation but before `run_backtest` generated its run identity, changing purported provenance without changing the constructed config. Copy the top-level mapping at construction, then wrap the stored copy with `MappingProxyType` so later top-level edits fail. Existing `_run_identity` still converts the mapping into a normal dict and its output schema remains unchanged. **This is a shallow snapshot, not deep immutability**: nested mutable values and custom mapping side effects require separate review.

Three new deterministic Phase3 tests (**6,810 cumulative proposed source-defined methods**) cover post-construction mutation of the original mapping, direct mutation of the retained mapping, and preservation of the original synthetic run-identity fields. No genuine historical market data, live broker, strategy alpha or protected run is used; the change is an unmerged reproducibility hardening proposal requiring exact-head Phase3/full historical-general CI and independent scoped review.

All eight independently authenticated external proof packages under #779/#820/#821 remain MISSING/BLOCKED, including no-bypass GitHub admission, real runner OS isolation, provenance, fresh one-shot inventory and separate human 2023/run385/attempt1 decision. No protected research, workflow/ref/ruleset modification, shadow/demo/live trading, real money or validated profit.
