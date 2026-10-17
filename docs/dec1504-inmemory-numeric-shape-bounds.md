# DEC-1504 — Fail closed on non-finite and oversized direct-memory numbers

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1749, exact parent `b4299667582a2c63db7249679a49bbfa3ff50939`. Eleven synthetic unittest methods; **2,285 proposed source-defined tests**.

DEC-1492 limits JSON-decoded integers to 64 decimal digits and requires finite floating-point values. However, callers can supply direct Python evidence objects through `review_bundle_envelope`, bypassing JSON's numeric parser. Extend the existing direct in-memory preflight to reject plain `int` values whose absolute magnitude exceeds `10**64-1` (exactly 64 decimal digits) and plain non-finite floats. The guard does not decimal-stringify gigantic integers or reflect numeric input. A rejected direct object returns the existing safe `BUNDLE_STRUCTURE_BUDGET_UNREVIEWED` verdict before nested evidence review.

Eleven synthetic tests cover extremely large positive/negative integers, exact 64- vs first 65-digit boundaries, positive/negative infinity, NaN, a finite float control, direct-envelope rejection, and clean consistency-only synthetic evidence. These are input resource/shape checks, not GitHub provider attestation, independent original OS no-write, or protected annual execution authorization.

Own exact-head Phase 3/full historical-general CI with qualified independent review required. DEC-650/#820 OS protected-original no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected annual dispatch/retry, original/archive/artifact access, workflow/security setting changes, merges, deployment or trading.
