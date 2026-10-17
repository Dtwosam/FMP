# DEC-1528 — Regression tests for NFKC-introduced dot traversal segments

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit, tests/docs-only child of #1773 at `18a74166735cfb2a41a2c01b05d47658cc48f658`. Nine new synthetic unittest methods; **2,518 proposed source-defined methods**.

DEC-1526 validates the Unicode NFKC comparison spelling of each source-label component, including rejecting newly introduced `.` and `..` segments. Fullwidth periods U+FF0E can otherwise make `src/．．/file.py` appear distinct from a forbidden parent-directory traversal while normalizing to `src/../file.py`. Record explicit regression cases for fullwidth and mixed ASCII/fullwidth dot segments, both source-byte maps, safe CLI diagnostic non-disclosure and positive leading-dot filenames that are not standalone dot/parent segments. These are lexical caller-supplied source-label tests only; no path is resolved or opened.

Own exact-head Phase 3/full historical-general CI plus independent qualified review required. DEC-650/#820 independently witnessed original protected OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected annual dispatch/retry, original/archive/artifact reads, workflow/security changes, merges, deployment or trading.
