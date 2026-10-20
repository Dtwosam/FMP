# DEC-1891 — Fail closed before invalid risk reservation state mutation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2139 `ec9acb2a53ceedf65b5e41383bbe0ddfb64acc84`.

The Phase3 risk state accepted `True` as starting equity and Boolean risk reservations because `math.isfinite(True)` is True; unsupported types could also escape as TypeError, and reserving multiple large but finite amounts could overflow total reserved risk to `inf` after mutation. Enforce real built-in finite positive numeric equity and reserve amounts, printable nonempty string position IDs for both reservation and release, and require the sum of new plus previously reserved risk to be finite *before* writing the reservation. Keep ordinary position release and daily risk semantics unchanged.

Four new Phase3 source-defined tests (**6,851 cumulative proposed**) cover malformed starting equity, malformed reservation sizes, invalid IDs and aggregate overflow without partial mutations. These synthetic unit tests do not demonstrate a profitable forex strategy, a protected historical run or real OS/administrator gate. All changes remain unmerged subject to exact-head Phase3/full historical-general regression and independent scoped risk-code review.

Phase8A accepted annual-first evidence stops at 2022/run384. Protected 2023/run385/attempt1, later research, Strategy V1 selection, shadow/demo/live broker operations, capital and installed GitHub workflow/ref/ruleset changes remain BLOCKED. All eight external #779/#820/#821 proof packages remain MISSING.
