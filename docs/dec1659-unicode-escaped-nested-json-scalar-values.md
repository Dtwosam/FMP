# DEC-1659 — Equivalent JSON Unicode escapes in nested scalar values

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1905 at `fb3872b292377d5df8bb5c9e22f6c13401f463f8`. Sixteen new source-defined methods (**4,053 proposed**).

The nested key regression family now covers rejecting decoded duplicates and accepting single legal Unicode-escaped key aliases. This complementary fixture changes **only the lexical spelling of one nested JSON string value** in each of fifteen required nonschema categories (including `runs`, source-byte maps, CI receipts and Phase 3 evidence). A deterministic path-preserving serializer replaces the first ASCII scalar character with its `\\uXXXX` spelling; decoded evidence remains exactly equal to the original caller-supplied envelope.

Each positive case proves direct-memory, strict JSON text and stdin return identical source-only consistency without diagnostics; caller evidence stays unchanged, sensitive sample paths are not echoed, and independent-original OS proof, exclusive dispatch proof and annual-run authority stay false. An original clean control is included.

Own exact-head Phase 3/general CI and qualified independent review required. Tests/docs only, no production/parser/resource-limit/workflow/security changes, protected original/archive/artifact access, annual execution/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
