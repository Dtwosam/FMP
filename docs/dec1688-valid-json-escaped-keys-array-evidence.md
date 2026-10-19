# DEC-1688 — Valid escaped JSON member names inside array-contained evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1934 at `1210e4db01dfc7bbd6fb63b130a1e182a4974c8e`.

Adds **49 source-defined methods** (**5,073 proposed total**): eight legal JSON escape forms inside extra synthetic object member names, at each of six array-contained evidence paths, plus a clean control. Cases exercise three ASCII Unicode escape positions, escaped slash, quote and backslash, a valid surrogate pair and a newline escape. Direct-memory review of the decoded key must equal strict JSON-text and offline stdin review. The escaped syntax is legal even when subsequent evidence validation refuses an extra field.

Asserts fixture immutability, no false grammar/Unicode refusal, exact safe stdout verdict field inventory, no synthetic source-path echo and false protected annual run/dispatch/proof fields. Only tests/docs and synthetic offline evidence. Own exact-head Phase 3/full historical-general CI and qualified independent review required. No parser/production/limits/workflow/security updates, protected originals/archive/artifacts, annual execution/dispatch/retry, merging/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
