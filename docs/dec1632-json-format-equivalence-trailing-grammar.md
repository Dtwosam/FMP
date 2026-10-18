# DEC-1632 — Legal JSON whitespace cannot change source-only review; invalid extra bytes fail closed

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1878 at `e421fbbb9fb2b8bc27cce49e3c6a302a7abfb56c`. Nineteen new methods (**3,663 proposed source-defined tests**).

Twelve positive lexical variations of the exact same JSON evidence envelope (compact, default, sorted, pretty-printed, alternate comma/colon whitespace, newline, CRLF/tab, and decoded Unicode) must give **identical** source-consistent, nonauthorizing portable verdicts. Six malformed serializations—leading BOM, trailing comma, second top-level JSON value, comment, raw NUL after the document, and non-JSON NBSP whitespace—must fail the bounded parser with exactly `BUNDLE_JSON_GRAMMAR_UNREVIEWED` and no source-path echo. One clean control checks the unchanged direct-memory fixture. JSON formatting neither authenticates GitHub source nor grants protected annual dispatch authority.

Own exact-head Phase 3 and historical/general CI and qualified independent review required. Tests/docs only; no production/parser/resource budgets/workflow/security/admission changes, protected original/archive/artifact access, annual execution/retry, merge/deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
