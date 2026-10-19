# DEC-1677 — Invalid JSON number spellings fail before required evidence review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1923 at `6dd3d4ce868297054e926c475750b52c04c4d201`, adding 97 synthetic regression test definitions (**4,607 proposed total**).

Six strictly invalid JSON numeric literal spellings — `01`, `+1`, `-.`, `.5`, `1.` and `1e` — are substituted independently for each of the sixteen required top-level evidence categories. They complement the bounded valid-number length tests and the nonfinite-number rejection tests; ordinary strict Python JSON must refuse to parse every case. Strict bounded JSON-text and stdin review must refuse `BUNDLE_JSON_GRAMMAR_UNREVIEWED` before schema or evidence-type validation.

Every case preserves the original clean synthetic source-only envelope, returns the exact safe verdict fields, does not echo synthetic file paths and keeps protected original OS, exclusive server dispatch and annual-run authorization false. One clean control remains. The DEC-1674 source-level test-name uniqueness guard continues to run.

Own exact-head Phase 3 and historical/general CI, plus independent qualified review, required. Tests/docs only; no production/parser/resource-limit/workflow/security controls, protected originals/archive/artifact reads, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
