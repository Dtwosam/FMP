# DEC-1650 — Nonfinite JSON constants and overflowing exponent literals fail closed

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1896 at `1abcc04f0072395f503f9607b10b60ae342a301b`. Thirteen regression methods (**3,933 proposed source-defined tests**).

Twelve JSON lexical mutants replace one required evidence category value with a non-JSON `NaN`/`Infinity` constant or a syntactically valid but nonfinite floating-point exponent. Python's permissive JSON decoder ordinarily accepts the former as extension constants and may convert the latter to infinity. The bounded source ingress must refuse all of them as `BUNDLE_JSON_GRAMMAR_UNREVIEWED` before source consistency review, with JSON-text/bounded stdin agreement, no source path disclosure and false protected annual-run authority. The unchanged clean direct-memory fixture stays source-consistent only.

Own exact-head Phase 3/full general CI and qualified independent review required. Tests/docs only, no production/parser/resource limits/workflow/security/admission changes, protected original/archive/artifact access, annual dispatch/retry, merge/deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
