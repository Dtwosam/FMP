# DEC-1679 — Malformed JSON number grammar precedes forged outer-envelope claims

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1925 at `48f955f167391bb1c61730803c987a4efc6c359b`. Adds 17 synthetic test methods (**4,705 proposed source-defined tests**).

Four required evidence categories (`pr`, `compare`, `tree`, `raw_ci_log_receipts`) are independently poisoned with the invalid JSON number token `01`. Each is combined with one of four otherwise independently invalid envelope claims: forged schema identity, forged `can_authorize_annual_run`, null `runs` category or missing required schema inventory. The primary defect is lexical: strict bounded JSON text/stdin must refuse `BUNDLE_JSON_GRAMMAR_UNREVIEWED` before subsequent inventory, schema, type, or authorization review.

The tests verify Python JSON itself rejects the malformed document, the original clean synthetic caller envelope is unchanged, verdict fields are fixed, no sensitive source-path echo occurs, and all three protected annual-run proof/authority flags remain false. A clean nonauthorizing control and the DEC-1674 method-name guard are preserved.

Own exact-head Phase 3/full historical-general CI and qualified independent review required. Tests/docs only; no production/parser/resources/workflow/security updates, protected originals/archive/artifacts, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
