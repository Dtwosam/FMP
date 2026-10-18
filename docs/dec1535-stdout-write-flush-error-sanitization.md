# DEC-1535 — Sanitize exceptional stdout writer and flush callbacks

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit, tests/docs-only child of #1780 at `e55f2e86f8141964b504f3726ce10d460384bed4`. Nine synthetic unittest methods: **2,580 proposed source-defined tests**.

The shared checked offline CI verdict writer handles ordinary stdout I/O, type and runtime exceptions, but a caller-supplied output stream can raise `OverflowError`, `IndexError` or `EOFError` from `write`, `flush` or the `flush` property itself. Treat these ordinary exceptions as output failure without echoing the exception text and without retrying or writing a secondary verdict. This keeps both normal stdin review and denied argument invocation fail closed on output errors. Do not suppress process-control `KeyboardInterrupt`/`SystemExit` or memory exhaustion.

Nine synthetic tests cover each writer/flush failure, property getter failure, denied-argv path, one-write guarantee and clean single-line, nonauthorizing source-consistency-only behavior. The output sink's return codes cannot establish protected annual workflow execution consent.

Own exact-head Phase 3/full historical/general CI and qualified independent review required. DEC-650/#820 independently witnessed original protected OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 GitHub admission remain **BLOCKED**. No protected runs/retries, originals/archives/artifact access, installed workflow/security modifications, merges, deployment or trading.
