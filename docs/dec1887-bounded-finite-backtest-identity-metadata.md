# DEC-1887 — Bound recursive synthetic run-identity metadata

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2135 `8b62d42f2bfd8b51131c2eefd95d3d035e2dcf8e`.

The recursively immutable `BacktestConfig.decision_config` must also reject oversized, non-evidence-like inputs before attempting report serialization. A wide list of many nested values or enormous string/integer can otherwise cause excessive memory allocations or Python integer conversion errors. Enforce a shared **8,192-node traversal budget**, **32-level nesting limit**, **512-bit integer width limit** and **64 KiB canonical serialized UTF-8 size limit**. Serialize using sorted keys and `allow_nan=False`; the external `run_identity` remains plain nested JSON-like dictionaries/lists, with no mutable aliases back to the config.

Four new Phase3 test methods (**6,838 cumulative proposed source-defined**) cover budget exhaustion, oversized serialized payloads, huge signed integers and valid nested Unicode/finite values. Limits are source-only defensive defaults that require independent compatibility/cost/risk review; not externally signed provenance, a real runner OS attestation or after-cost forex profitability.

Annual-first accepted evidence ends 2022/run384, protected 2023/run385/attempt1 and later years remain BLOCKED. Eight independent #779/#820/#821 security/runner/provenance/fresh-inventory/human proof packages remain MISSING. No installed GitHub ref/workflow/ruleset mutation, protected research, broker/demo/live order, money or financial performance. Exact-head Phase3/full regression and scoped human review required.
