# DEC-1532 — Sanitize common stdin read-origin exceptions

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1777 at `26cd103a00933c5c678381cd15fed6bd9631b26c`. Nine synthetic unittest methods; **2,554 proposed source-defined methods**.

A synthetic or malicious caller-supplied text stream can raise ordinary `AssertionError`, `AttributeError`, `OverflowError`, `IndexError` or `EOFError` during `read()`. Previously the stdin boundary sanitized I/O, Unicode, type and runtime errors but could still expose traceback and input text for these exceptions. Convert these additional ordinary exceptions to `BUNDLE_STDIN_READ_UNREVIEWED` before any JSON review. Deliberately do not swallow `KeyboardInterrupt`, `SystemExit` or `MemoryError`. This is only local error sanitation, never protected-original OS isolation.

Nine tests cover each failure, missing read method, property-getter errors, one-line non-disclosing CLI result and a clean synthetic source-consistency-only control. All protected annual authority booleans remain false.

Own exact-head Phase 3 and full historical/general CI plus independent qualified review required. DEC-650/#820 independently witnessed protected-original OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected annual dispatch/retry, original/archive/artifacts, installed workflow/security setting changes, merges, deployment or trading.
