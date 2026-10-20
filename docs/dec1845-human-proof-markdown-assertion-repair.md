# DEC-1845 — Repair Markdown formatting checks in external proof test harness

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent test-only repair of #2091 `0b172a187bf52033761da19413f230f9842c1f21`.

Two DEC-1844 regression assertions expected literal unformatted substrings that were not present in the owner handoff: the source document marks `navigation` with Markdown bold delimiters and says the local SHA-256 fingerprint is `not an independent signature` rather than `not a signed bundle`. Those false assertions could fail full regression even though the eight source-defined proof IDs, owners, issue links and MISSING statuses had not changed.

Normalize only Markdown `**` formatting for the relevant assertions and check the **actual reviewed, non-authorizing wording**. Keep all four test methods, production code, evidence acceptance requirements and permanent BLOCKED state unchanged. Cumulative proposed source-defined methods remain **6,729**. This is not an external review/OS isolation signoff or run approval. No protected 2023/run385/attempt1, main/ref/workflow/ruleset changes, broker/demo/live activity, capital or profit. #779/#820/#821 and all eight proof packages remain MISSING/BLOCKED. Exact-head Phase3/full CI and qualified independent review required.
