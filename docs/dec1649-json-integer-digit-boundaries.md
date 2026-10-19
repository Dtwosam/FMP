# DEC-1649 — Oversized JSON integer tokens fail the bounded parser before source review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1895 at `407d927c746a98c950a8c28c27de684c7cbdaaae`. Fourteen synthetic regression methods (**3,920 proposed source-defined methods**).

Thirteen malformed but syntactically valid JSON documents replace a required evidence category value with a positive or negative integer containing one decimal digit beyond `MAX_JSON_INTEGER_DIGITS` (64). A clean direct-memory source fixture must remain consistent only; bounded raw JSON text and stdin must return `BUNDLE_JSON_GRAMMAR_UNREVIEWED` without echoing sensitive paths, allocating unrestricted numeric objects, or granting protected annual permission. A final control preserves canonical source-only consistency.

Own exact-head Phase 3/general CI and independent qualified review required. Tests/docs only, no production/parser/resource-budget/workflow/security/admission changes, protected originals/archives/artifacts, annual dispatch/retry, merging, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
