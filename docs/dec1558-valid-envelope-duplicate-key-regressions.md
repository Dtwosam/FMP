# DEC-1558 — Duplicate decoded members in otherwise-valid CI source envelopes

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1804 at `c5ce533e43df36c7e7c5ca58d7025e048b7d033a`; nine new synthetic unittest methods and a small fixture builder (**2,783 proposed source-defined methods**).

The JSON object-pairs hook must refuse duplicate decoded keys even if all other CI/source material is a valid synthetic evidence envelope. Mutations duplicate root schema, root runs (attempted provenance replacement), nested PR members, Base64 source-file paths, and raw CI log run identifiers. Test literal and Unicode-escaped alternate spellings to prevent a last-wins JSON parser from admitting altered evidence. Identical run identifiers appearing in **different** required maps remain legitimate and the clean fixture stays source-consistency-only.

No production parser changes, new authority, workflow/security-control edits, protected originals, dispatch/retry, merge, deployment or trading. Own exact-head Phase 3 and historical/general CI and independent qualified review required. DEC-650/#820 protected-original independent OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 admission remain **BLOCKED**.
