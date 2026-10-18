# DEC-1545 — Deterministic raw-log UTF-8 diagnostic precedence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1791 at `f259838f07bf24e92d830f4c6032609bd48c87e4`. Nine new synthetic unittest methods, **2,672 proposed source-defined methods**.

DEC-1527 added a per-run 2 MB UTF-8 log limit and an aggregate 4 MB log limit. Their checks previously ran in one loop: depending on source map insertion order, an aggregate failure could be returned before discovering a later individually oversized log. This violates the existing intent that equivalent malformed offline evidence yield stable diagnostics. Compute the UTF-8 byte sizes under the already checked 8,192-key and direct-memory budgets; reject *any* overlarge individual log first, then check the aggregate, before parsing run IDs or invoking nested review. Do not change the limits, decode any protected originals or echo log contents.

Nine synthetic tests verify per-run-over-aggregate precedence for opposite insertion orders, stable total-cap failures, invalid run-ID precedence, zero-length controls, safe diagnostics, annual authorization flags permanently false, and an unchanged clean source-only fixture.

Own exact-head Phase 3/full historical-general CI and qualified independent review required. DEC-650/#820 independently witnessed original protected OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected annual dispatch/retry, original/archive/artifact access, workflow/security control changes, merges, deployment or trading.
