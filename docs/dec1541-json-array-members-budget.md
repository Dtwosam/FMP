# DEC-1541 — Bound decoded JSON array members before nested review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1787 at `9cd2e7c07e1c1de46ee2b75ab55a5574252498be`. Nine synthetic unittest methods; **2,634 proposed source-defined tests**.

DEC-1540 bounds the total number of decoded object members. JSON arrays still have no standard-library array-hook: a client can supply large or many small arrays inside a text body below its 2 MB cap. After JSON decoding but before surrogate checks and composite evidence validation, iteratively inspect the parsed built-in lists/dictionaries with **16,384 items maximum in one list and 65,536 list items cumulative**. Refuse excess array items using the existing sanitized `BUNDLE_JSON_GRAMMAR_UNREVIEWED` diagnostic. Preserve lexical nesting checks and the separate valid top-level `runs` limit of 4,096. This is a post-decoding guard, not proof that JSON decoding itself avoided materializing the input list.

Nine synthetic tests exercise exact/over per-array boundaries, globally oversized nested arrays, a nested object with too-large list, per-document state isolation, safe stdin non-disclosure and a clean source-only fixture. No protected annual authorization, provider identity or witnessed OS no-write follows from success.

Own exact-head Phase 3 and full historical/general CI plus qualified independent review required. DEC-650/#820 protected originals OS no-write and DEC-651/#821/#779 immutable exclusive protected annual 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected execution/retry, originals/archives/artifact reads, workflow/security control changes, merges, deployments or trading.
