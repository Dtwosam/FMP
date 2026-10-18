# DEC-1624 — Private, malformed or nonliteral diagnostic codes cannot leave portable review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1870 at `e23dbca48cad30efd0d7340acbe93283453c3633`. Sixteen synthetic methods (**3,540 proposed source-defined tests**).

The nested composite reviewer may produce adversarial diagnostic identifiers, including non-string scalars/containers, raw source-path suffixes, escape codes, invisible Unicode, newline text, and syntactically plausible but non-allowlisted names. Fifteen mocked negative verdicts must be rejected at the public boundary as **only** `BUNDLE_RESULT_SHAPE_UNREVIEWED`, without leaking caller paths or private messages through direct-memory/JSON/stdin. A genuine reviewed, allowlisted negative diagnostic is retained by the portable source-only reviewer and remains nonauthorizing.

This asserts reviewer result-shape safety, not GitHub evidence authentication or protected annual permission. Exact-head Phase 3/general CI and qualified independent review required. No production/parser/resources/workflow/security/admission changes; no protected original/archive/artifact access, annual execution/retry, merge, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
