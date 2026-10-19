# DEC-1660 — Strict nested JSON grammar errors precede forged outer-envelope claims

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1906 at `24d260fa3b5dfe3c7a1f647f1312b1ed7143c996`, adding seventeen regression methods (**4,070 proposed**).

This draft combines escaped Unicode-equivalent duplicate object member names inside one of four required evidence categories (`pr`, `tree`, `raw_ci_log_receipts`, `phase3_evidence_snapshot`) with one of four distinct outer-envelope defects: forged schema identity, forged approval flag, invalid `runs` type, and invalid `compare` type. The malformed input remains legal JSON for permissive parsers, but strict bounded text/stdin review must refuse `BUNDLE_JSON_GRAMMAR_UNREVIEWED` before any inventory, schema, type or nested proof review.

The tests require no caller evidence mutations, the exact safe verdict fields, no synthetic source-path echo, and no protected annual dispatch authority. The clean control remains source-consistent but nonauthorizing. All changes are tests/docs only; no parser limits, production paths, workflows or security gates change.

Own exact-head Phase 3/full general CI and independent qualified review required. No protected originals/archive/artifact access, annual execution/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
