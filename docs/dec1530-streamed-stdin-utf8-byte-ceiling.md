# DEC-1530 — Streamed UTF-8 byte limit for stdin-only offline evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1775 at `cdc0c38ca9ab445a6934f5aded341b69441348ad`. Nine synthetic regression tests; **2,536 proposed source-defined methods**.

DEC-1529 places a 2,000,000-byte UTF-8 cap on completed JSON text. The stdin adapter previously accumulated up to 2,000,000 **characters**, potentially buffering considerably more text bytes before invoking the JSON review function. Count per-chunk UTF-8 bytes as text arrives, preserving the separate character cap and conservative 65,536-character read request. Refuse if either total exceeds 2,000,000; reject actual invalid Unicode via the safe Unicode code. Do not echo supplied input. This is a text-stream budget, not an OS-level byte stream limit or a promise of physical memory isolation.

Nine tests cover exact/over multibyte byte limits, four-byte emoji, invalid surrogates, short reads, no success from valid JSON prefix, safe stdout diagnostics and the unchanged clean source-consistency-only fixture. No protected annual authorization is conferred.

Own exact-head Phase 3 and full historical/general CI with independent qualified review required. DEC-650/#820 protected-original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected annual dispatch/retry, originals/archives/artifacts, installed workflows/security changes, merges, deployment or trading.
