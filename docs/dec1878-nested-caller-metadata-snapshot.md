# DEC-1878 — Detach nested caller metadata before a synthetic backtest run

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2125 `1278925cca1df4855549ea22cd4819aeb538efe6`.

DEC-1877 protects the *top level* of a caller-supplied decision-configuration mapping, but shallow copying retains aliases to nested lists and dictionaries. A caller can still alter a list of parameters or an inner dict after `BacktestConfig` construction, silently changing the eventual `_run_identity` evidence. Copy the full `dict(decision_config)` using Python `deepcopy`, then wrap its top level in the same read-only `MappingProxyType`. Catch unsupported copy failures as a controlled ValueError before a run is constructed.

This detaches nested caller aliases and preserves ordinary nested list/dictionary structures in run output, **but does not make retained nested values deeply immutable**, authenticate market provenance, or prove a mapping is safe for downstream serialization. A future independent design decision may require restricted JSON-only recursive immutability; it is not silently assumed here.

Three new deterministic Phase3 tests (**6,813 cumulative proposed source-defined**) verify nested list/dict caller independence, stable nested run-identity values and fail-closed unsupported deepcopy objects. Unmerged pure backtester draft, requiring exact-head Phase3/full regression and scoped human review. Phase8A accepted discovery ends at 2022/run384; protected run385/attempt1 and later research, Strategy V1 economics, broker/demo/live and capital all BLOCKED. Eight external #779/#820/#821 security/OS/provenance/inventory/human packages still MISSING; no installed ref/workflow/ruleset change.
