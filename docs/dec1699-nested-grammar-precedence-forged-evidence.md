# DEC-1699 — Nested JSON grammar outranks forged review evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent tests/docs child of #1945 at `35dc70a4c3276df0f0191a357495c60fc7662a17`.

Adds **97 source-defined methods** (**5,485 proposed total**): four malformed JSON token spellings at each of six array-contained evidence paths, crossed with four independent forged root envelope defects (`schema` replacement, missing `schema`, forged annual approval flag and null required PR evidence), plus a clean synthetic control. Legal precedence is strict JSON grammar ingress first: even overlapping forged schema, missing inventory or approval attempts cannot reclassify malformed JSON as ordinary evidence review or authorize anything. Text and stdin must emit exactly `BUNDLE_JSON_GRAMMAR_UNREVIEWED`.

All changes operate on deep-copied synthetic source, leaving the original clean fixture unchanged. Exact safe verdict shape, no marker/source path echo and false annual/original-OS/dispatch proof flags. Own exact-head Phase 3/full historical-general CI and independent qualified review required. Tests/docs only; no production/parser/limits/workflow/security updates, protected originals/archive/artifacts, annual dispatch/retry, merging/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
