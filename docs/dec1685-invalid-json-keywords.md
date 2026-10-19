# DEC-1685 — Malformed JSON keywords in required evidence categories

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1931 at `853c5924e3356071e90e7758f60eac48c19e9d5a`.

Adds 97 source-defined methods (**4,938 proposed total**). Six invalid unquoted JSON keyword spellings (`True`, `FALSE`, `Null`, `None`, `undefined`, `tru`) are substituted into each of the 16 required top-level categories, plus a clean synthetic control. Strict JSON text and offline stdin review must both emit `BUNDLE_JSON_GRAMMAR_UNREVIEWED` rather than accepting Python-style or case-mutated primitives or skipping grammar to category-type review.

The original caller fixture must remain immutable. No synthetic source-path disclosure, annual authority, independent-original-OS proof or server dispatch gate is permitted. Exact safe verdict shape is checked.

Tests/docs only, offline synthetic data only. Own exact-head Phase 3 and full historical/general CI plus qualified independent review required. No parser/production/limits/workflows/security updates, protected originals or archived artifacts, dispatch/retry, annual execution, merge, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
