# DEC-1515 — Refuse embedded NUL in offline raw CI log evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict exact-parent one-commit tests/docs child of #1760 at `5e0701ce7f9554e995fad17ffeaeafba391040ee`. Adds nine synthetic unittest methods; **2,389 proposed source-defined methods**.

The portable reviewer requires bounded plain Unicode `str` values in `raw_ci_runner_logs`, but ordinary JSON decoding accepts `\\u0000`, which is an embedded NUL character that can be treated as a terminator by downstream text consumers or obscured during review. Require raw log text to contain no U+0000 before decoding run identifiers or calling the composite source reviewer, returning only the existing `BUNDLE_RAW_LOG_TEXT_UNREVIEWED` code. Preserve common log newlines/tabs, avoid truncation or content echo, and keep the previous per-run/cumulative size caps.

Nine tests cover leading/embedded/trailing NUL, invalid run-ID diagnostic precedence, JSON-escaped NUL, safe log formatting, stdout non-disclosure, false protected annual authorization and clean synthetic source consistency. This only validates caller-supplied log shapes, not GitHub provenance, independently witnessed original OS no-write, or protected annual admission.

Exact-head Phase 3/full historical-general CI and qualified independent review mandatory. DEC-650/#820 protected-original OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected dispatch/retry, original/archive/artifact access, installed workflow/security changes, merges, deployment or trading.
