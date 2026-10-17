# DEC-1485 — Complete capped stdin evidence intake across short reads

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict forward-only one-commit tests/docs child of #1730, exact parent `f21ffe52772104e85227d48ac2d78651aca9ff5e`. Adds **12 synthetic unittest methods** for **2,099 proposed source-defined tests**.

The DEC-1479 stdin-only offline evidence checker formerly called `read(MAX_TEXT_CHARS+1)` only once. Text streams may legally return a short read before EOF, so a complete valid JSON prefix followed by additional malicious or contradictory bytes could be accepted if the first read returned only the prefix. The fixed reader accumulates bounded text chunks until EOF, enforcing the pre-existing 2,000,000-character total limit as it reads, and rejects non-text chunks, read exceptions, invalid JSON trailers and excess data without echoing caller evidence.

Twelve synthetic tests cover valid evidence arriving in short or single-character chunks, tampered content appended after a valid prefix, a second JSON document, incomplete JSON, late I/O and Unicode errors, binary/null chunks, per-read caps, safe diagnostics, and deterministic rejection across different chunking schedules. A consistency-only exit code still cannot authorize any annual workflow or establish provider authenticity.

Own head-associated PR merge-checkout Phase 3 acceptance and full historical/general CI, plus independent qualified review, required. DEC-650/#820 witnessed protected-original OS no-write and DEC-651/#821/#779 exclusive immutable GitHub server admission for protected 2023 run385/attempt1 remain **BLOCKED**. No protected run/dispatch/retry, originals/artifacts, installed workflow/security modifications, merges, deployments or trading.
