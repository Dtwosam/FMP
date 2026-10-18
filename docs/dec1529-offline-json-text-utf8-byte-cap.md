# DEC-1529 — UTF-8 byte cap on offline JSON evidence text

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit, tests/docs-only child of #1774 at `4c9f08d35da597a79ed429a25e5b5b62a2b19584`. Nine synthetic methods; **2,527 proposed source-defined methods**.

The portable offline JSON evidence entry point limits source text to 2,000,000 Python Unicode characters. Multi-byte Unicode can exceed that byte budget while staying within the character count. Enforce an additional maximum of 2,000,000 encoded UTF-8 bytes on plain input text *before* lexical-nesting and JSON parsing; refuse encoding errors with the sanitized `BUNDLE_JSON_UNICODE_UNREVIEWED` verdict. Retain existing character, nesting, numeric-token, duplicate-key, object-inventory, and value guards. This is a conservative input resource limit, not a guarantee of interpreter-level memory isolation.

Nine synthetic tests cover exact and over ASCII byte boundaries, two-/four-byte Unicode inflation, raw versus escaped surrogate diagnostics, valid multilingual input, safe stdin non-disclosure, and an unchanged nonauthorizing positive source-only fixture.

Exact-head Phase 3/full historical-general CI and qualified independent review required. DEC-650/#820 independently witnessed protected-original OS no-write and DEC-651/#821/#779 immutable protected 2023 run385/attempt1 exclusive GitHub server admission remain **BLOCKED**. No protected annual execution/retry, originals/archives/artifacts, installed workflow/security changes, merges, deployment or trading.
