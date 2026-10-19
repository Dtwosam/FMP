# DEC-1689 — Decoded duplicate JSON keys inside array-contained evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1935 at `a2a60c10b65d68d127abfdbc7a7bff66e767db2e`.

Adds **31 methods** (**5,104 proposed source-defined total**): five duplicate member-name spellings at six nested array-contained evidence dictionary locations, plus a clean control. Both literal duplicates and Unicode-escaped aliases must be rejected after JSON key decoding, at `BUNDLE_JSON_GRAMMAR_UNREVIEWED`, rather than silently overwriting a member or accepting a normal category review. Strict JSON-text and stdin output must agree and remain nonauthorizing.

Only synthetic caller-supplied evidence. Checks clean source immutability, exactly safe verdict fields, no synthetic value/path echo, and false protected original OS proof, server dispatch and annual authority. Own exact-head Phase 3/full historical-general CI plus qualified independent review required. No parser/production/limits/workflow/security changes, protected originals/archive/artifacts, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
