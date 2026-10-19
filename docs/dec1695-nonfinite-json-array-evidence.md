# DEC-1695 — Nonfinite numeric spellings in array-contained evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1941 at `e5f9b70856525cbc8c5dcdce5c58d0d55ca13019`.

Adds **49 source-defined methods** (**5,289 proposed total**): eight nonfinite or unreviewable numeric lexemes embedded in six array-contained evidence objects, with one clean synthetic control. Token coverage includes JavaScript-style `NaN`/`Infinity`/`-Infinity`/`+Infinity` and overflow-form exponent numbers `1e309`, `-1e309`, `9e999`, `-9e999`. Strict decoder and offline stdin must refuse `BUNDLE_JSON_GRAMMAR_UNREVIEWED` even when permissive Python JSON decoding might otherwise produce nonfinite floats.

Original synthetic evidence is immutable, safe verdict schema and no source path/marker echo enforced, annual-run, independent-original-OS and exclusive server dispatch flags remain false. Own exact-head Phase 3/full historical-general CI and qualified independent review required. No production/parser/limits/workflow/security changes, protected originals/archives/artifacts, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
