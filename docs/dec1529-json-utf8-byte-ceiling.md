# DEC-1529 — UTF-8 byte ceiling for offline JSON evidence text

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict exact-parent one-commit tests/docs child of #1774 at `4c9f08d35da597a79ed429a25e5b5b62a2b19584`. Nine synthetic methods; **2,527 proposed source-defined methods**.

The portable JSON evidence reader caps decoded Python text at 2,000,000 characters, but 2,000,000 Unicode code points can represent up to 8,000,000 bytes of UTF-8. Before invoking lexical nesting inspection or JSON decoding, also cap its actual UTF-8 representation at **2,000,000 bytes**; retain the existing character limit and fail closed with `BUNDLE_JSON_TEXT_UNREVIEWED`. Refuse actual unpaired Unicode surrogate input with the specific `BUNDLE_JSON_UNICODE_UNREVIEWED` code. This check does not imply that the upstream input stream read avoids buffering characters before review.

Nine tests cover byte/character boundaries, multibyte 2- and 4-byte scalars, actual/escaped surrogates, safe stdin diagnostics and clean synthetic source consistency. None of this establishes original OS no-write, GitHub provider provenance or authorization for protected annual dispatch.

Own exact-head Phase 3 and full historical/general CI and independent qualified review required. DEC-650/#820 independently witnessed original protected OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected dispatch/retry, originals/archives/artifacts, workflow/security setting changes, merges, deployment or trading.
