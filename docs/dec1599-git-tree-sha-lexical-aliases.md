# DEC-1599 — Git SHA lexical aliases cannot change reviewed tree identity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1845 at `7c69ec0fc6985afb36f40211a46fb007f06de467`. Fourteen source-defined regression methods (**3,188 proposed tests**).

Full Git tree object-map keys, snapshot self-identifiers, commit root pointers and parent/leaf SHA pointers must be exact, canonical lowercase 40-character Git IDs. Uppercase spellings, fullwidth homoglyphs, zero-width insertions, newlines, trailing spaces and `0x` prefixes are **not** normalized into legitimate proof. Keep the canonical changed bytes and flat Git node records intact; assert existing `TREE_CHAIN_TREE_OBJECT_UNREVIEWED`, `TREE_CHAIN_ROOT_SHA_UNREVIEWED` or `TREE_CHAIN_ENTRY_SHA_UNREVIEWED` across direct-memory, JSON text, and bounded stdin, without a caller source echo. A clean control remains source-consistent only.

No authenticated GitHub objects, original protected OS evidence, exclusive server permission or annual-run authorization is inferred. Own exact-head Phase 3 and historical/general CI and qualified independent review required. Tests/docs only, no production, parser, limits, workflow/security/admission modifications, protected originals/archives/artifacts, annual dispatch/retry, merge, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
