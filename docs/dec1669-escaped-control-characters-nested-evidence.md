# DEC-1669 — Escaped control-character JSON remains valid grammar

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit test/docs child of #1915 at `0f12f5a9d1e7e6802420fa138f2d61041dbe3e46`, adding 29 regression methods (**4,295 proposed**).

DEC-1668 rejects *unescaped literal* NUL and newline in nested JSON strings. This draft proves the complementary case. For all fourteen required dictionary-valued evidence categories, an extra key containing U+0000 is encoded as `\\u0000`, or an extra child string with a newline is encoded as `\\n`. Both are legal JSON lexical forms. Python's JSON decoder, the strict offline JSON reviewer, and the stdin wrapper must decode the same in-memory envelope and yield the exact same source review verdict. Additional unreviewed evidence may still be rejected on semantic grounds; these tests do **not** grant it authority.

The tests explicitly disallow false `BUNDLE_JSON_GRAMMAR_UNREVIEWED` and `BUNDLE_JSON_UNICODE_UNREVIEWED` outcomes for valid escaped controls, preserve the original caller fixture, require safe verdict structure without synthetic sample paths, and keep original-OS, exclusive-dispatch and annual-run flags false. One untouched source-only control remains.

Own exact-head Phase 3/full historical-general CI and qualified independent review required. Tests/docs only, no production/parser/limit/workflow/security updates, protected original/archive/artifact access, annual execution/retry, merge/deploy/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
