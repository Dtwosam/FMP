# DEC-1534 — Strict text-stream flush return contract for offline verdict

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1779 at `095ce4438cab7a55c49f5de310a6feee699c7a5e`. Eight synthetic methods, **2,571 proposed source-defined tests**.

A standard Python text stream `flush()` returns `None`; the shared offline CI verdict writer previously ignored an unexpected return value. For caller-supplied output streams, require a present callable `flush` to return precisely `None` in addition to a successful complete `write`. An unexpected boolean, integer or string result forces failure without a retry or secondary write. Streams without a `flush` method still follow the existing complete-write contract. This does not prove downstream receipt or filesystem durability.

Eight tests cover normal `None` returns, unexpected values, both stdin and denied-argv paths, no second write after refusal and ordinary machine-readable source-consistency-only success. It never authorizes protected annual research.

Own exact-head Phase 3 and full historical/general CI and independent qualified review required. DEC-650/#820 independently witnessed original protected OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected dispatch/retry, originals/archives/artifacts, installed workflow/security changes, merges, deployment or trading.
