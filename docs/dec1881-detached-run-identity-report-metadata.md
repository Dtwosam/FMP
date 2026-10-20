# DEC-1881 — Detach nested metadata from output run identity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2128 `18fe216ad772837bc138311319363cc34bb563af`.

After DEC-1878, `BacktestConfig` protects itself against edits to *caller-owned* nested decision metadata, but `_run_identity` still used `dict(config.decision_config)` to construct a result. That shallow copy exposed the retained nested dictionary/list objects in the **reported run identity**. Downstream consumers could accidentally mutate report metadata and thereby alter the still-retained configuration, contaminating subsequent deterministic comparisons.

Deep-copy the decision-configuration values when assembling the run identity. It retains the exact same output field shapes and ordering for normal configurations but removes mutable aliases between the original config and each reported identity. Two tests (6,821 cumulative proposed source-defined methods) verify nested changes to an identity cannot change its source configuration or a second identity. This is **not a guarantee of arbitrary custom object serialization, true external provenance, deep immutable config, or approved trading**.

The implementation remains unmerged and requires exact-head Phase3/full historical-general CI and independent scoped code review. No protected 2023/run385/attempt1 or later research, ref/workflow/ruleset/security changes, broker/demo/live capital or established Strategy V1 profitability. Eight external #779/#820/#821 proof packages remain MISSING.
