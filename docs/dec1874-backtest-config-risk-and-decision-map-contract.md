# DEC-1874 — Typed risk contract and printable synthetic decision metadata

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2121 `0f0022a918a585f8339fd12808b2c4001f9ae55b`.

The Phase3 `BacktestConfig` previously allowed `risk_config=None` or `decision_config=42` through construction, only to fail at execution or report identity serialization. The run identity also includes decision configuration keys that are typed as strings but were not checked, permitting unreadable control characters in source-only provenance labels. Require a real `RiskConfig`, a `Mapping` decision configuration and nonempty ordinary string keys without C0/DEL terminal controls. Valid string-keyed synthetic configurations and numeric values remain supported; this draft does not enforce arbitrary strategy value serialization or accept external approval evidence.

Four new Phase3 methods (**6,803 cumulative proposed source-defined**) cover bad risk objects, missing/wrong decision maps, malformed keys and ordinary synthetic configuration preservation. This is a proposed pure test/backtest config contract, not production workflow admission or broker execution. Exact-head Phase3 and full historical/general CI and independent scoped code review required.

No protected data access or 2023/run385/attempt1 dispatch/retry, installed workflow/ref/ruleset changes, live/demo trade, real money or Strategy V1 profit. All eight external independent #779/#820/#821 security/provenance/runner/inventory/human proofs remain MISSING/BLOCKED.
