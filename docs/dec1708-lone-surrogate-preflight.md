# DEC-1708 — Lone surrogate escapes are rejected before nested evidence review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1954 at `e68727f07115dfae05becf632621a0ab4fabb880`.

Adds **49 source-defined methods** (**5,728 proposed**): the minimum and maximum lone high-/low-surrogate code points as JSON object **keys and values** in six array-contained evidence dictionaries, plus a clean control. Unlike malformed JSON token grammar, these strings can decode as JSON, but they are unpaired Unicode surrogates. Tests assert the exact `BUNDLE_JSON_UNICODE_UNREVIEWED` refusal and, crucially, patch the composite nested reviewer to confirm it is **never invoked**, via both direct JSON text and offline stdin.

Input is generated as ASCII JSON with escaped surrogate characters, protecting serialization. Original synthetic fixture remains unchanged, no exception/marker/source-path echo and no original OS proof, exclusive server dispatch or annual execution authority. Own exact-head Phase 3/full historical/general CI and qualified independent review required. Test/docs only; no production/parser/limits/workflow/security changes, protected originals/archives/artifacts, annual dispatch/retry, merging/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
