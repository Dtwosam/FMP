# DEC-1988 — Preserve semantic error classification before JSONL byte check

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2236 `7da609eae6913325413f9326f5c767fe52ed50a5`.

Post-commit source review discovered the DEC-1986 canonical-JSONL byte-format check was inserted immediately after field-name checking, ahead of symbol/direction, timestamp, trade and rejection identity, economics, row chronology and other focused safeguards. Existing self-rehashed negative fixtures intentionally serialize modified JSONL with ordinary spaced separators. Early canonicality refusal would mask the precise security/audit error those tests assert, even when the economic or identity field is actually invalid. #2235/#2236 full suites were still running when reviewed; this is a **source-identified ordering repair**, not a claim about CI outcome.

Retain the writer-exact JSONL byte requirement, but run it only after all established per-row semantic checks. Add one source-defined test confirming a rehashed unsupported trade symbol still triggers the specific symbol refusal despite the forged row also having noncanonical spaces. Existing tests for missing terminal LF and pretty-printed otherwise-valid rejection rows continue to exercise byte-level refusal.

Cumulative proposed test methods **7,060** (+1); exact-head Phase3 and full historical/general regressions mandatory. #2225–#2230 full suites PASS; #2231–#2233 historical FAIL preserved. #2234–#2236 statuses must be checked independently.

This does not authenticate real FX quotes, establish strategy profits, or authorize protected research. Phase8A #779/#820/#821 and eight independent external security proofs remain outstanding. **DRAFT NEVER MERGE NEVER PROMOTE.**
