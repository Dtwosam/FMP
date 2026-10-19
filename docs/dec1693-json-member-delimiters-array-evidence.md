# DEC-1693 — Malformed JSON member delimiters inside evidence arrays

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1939 at `d22d2d0d8ae28ecd447c47e6a4d3ddd2f4f1bde3`.

Adds **49** source-defined methods (**5,191 proposed total**) covering eight invalid JSON object-member delimiter forms in each of six array-contained evidence dictionaries: missing colon, equals separator, repeated colon, extra comma, missing comma, semicolon separator, trailing comma and colon before key. One clean synthetic control preserves the baseline. These are malformed JSON documents, so strict JSON-text and offline stdin review must emit only `BUNDLE_JSON_GRAMMAR_UNREVIEWED`, not schema, type, Unicode or nested evidence judgments.

Each corruption is applied to a uniquely named synthetic last member of a deep-copied object. Original caller input remains immutable, no synthetic source paths or marker names appear in output, and annual-run/protected OS/dispatch flags remain false. Test/docs only; own exact-head Phase 3/full historical-general CI and qualified independent review required. No production/parser/workflow/security changes, protected originals/archives/artifacts, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
