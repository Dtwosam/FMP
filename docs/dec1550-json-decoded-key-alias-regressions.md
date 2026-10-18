# DEC-1550 — Decoded JSON key alias collision regressions

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict tests/docs one-commit child of #1796 at `c3870fe3b587967ecd4efbcc5375f57cf09434a5`. Nine new synthetic methods; **2,715 proposed source-defined methods**.

JSON lexical scanners operate on predecode characters, but duplicate-key identity must be established from the *decoded* key by the existing object-pairs hook. Cover ASCII Unicode escapes, escaped slash, escaped backslash, UTF-16 surrogate pairs, accented Unicode, and nested objects. Check that distinct case-sensitive keys and same-spelled keys in separate objects do not become accidental duplicate-key false positives. The CLI must emit one safe diagnostic and never echo an escaped private alias. All authority flags remain false.

Existing parsers, limits, workflow configuration and security controls stay unchanged. Independent qualified review and both exact-head CI suites required. DEC-650/#820 independently witnessed protected-original OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected annual dispatch/retry, original/archive/artifact access, merging, deployment or trading.
