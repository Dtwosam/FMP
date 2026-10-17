# DEC-1487 — Strict capped stdin stream-read contract

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1732 at `a5b64da3ec6cb57ddfd44f757e6ceeb375999d2e`. Eight synthetic methods, **2,117 proposed source-defined tests**.

DEC-1485's complete capped stdin review reads until EOF, but a nonconforming stream can return a string longer than requested, bypassing the declared per-read resource bound. Refuse any returned chunk longer than its explicit request; the reader still enforces the unchanged two-million-character total bound. Failures emit only `BUNDLE_STDIN_READ_UNREVIEWED`, with no caller data echoed.

Eight regression methods cover over-return at initial and later read, exact 65,536-character per-read boundary, exactly 2,000,000 characters, one character above that total, exactly one output verdict after short reads, a late read error with an untrusted message, and non-plain-string chunks. All positive results mean only internal caller-supplied consistency, never GitHub provider authenticity or annual run authorization.

Own PR-associated Phase 3/full historical-general CI and independent qualified review required. DEC-650/#820 independently witnessed protected-original OS no-write and DEC-651/#821/#779 exclusive immutable protected annual 2023 run385/attempt1 server admission remain **BLOCKED**. No protected runs/retries, originals/archives, workflow/security modifications, merges, deployments or trading.
