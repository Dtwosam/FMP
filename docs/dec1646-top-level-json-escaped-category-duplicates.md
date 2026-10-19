# DEC-1646 — Duplicate decoded top-level JSON category keys must fail at parse time

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1892 at `cf2426a7e1c15d337d7ecdcda7ab7b73a7049e4c`. Seventeen regression methods (**3,876 proposed source-defined tests**).

All sixteen mandatory categories are vulnerable to a permissive JSON parser silently collapsing two lexically different yet decoded-identical object keys. For each category, place a `null` first member and the original value under a Unicode-escaped spelling of the **same decoded key**. A naive last-wins `json.loads` reconstructs the untouched, source-consistent evidence, but the bounded ingress must refuse as `BUNDLE_JSON_GRAMMAR_UNREVIEWED` in both JSON text and stdin, with no untrusted path echo or annual-run authority. The untouched control still passes source-only consistency. This checks top-level members, complementing earlier nested-map duplicate tests.

Require own exact-head Phase 3 and historical/general CI and qualified independent review. Tests/docs only; no production/parser/resource budgets/workflow/security/admission changes, protected originals/archives/artifacts, annual dispatch/retry, merge/deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
