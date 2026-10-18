# DEC-1539 — Correct global JSON versus per-log UTF-8 guard precedence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1784 at `d52cba005b26c3e6119087579f4f34cdd17bef8f`. Eight new synthetic unittest methods; **2,616 proposed source-defined methods**.

Historical/general CI for #1779 failed a single inherited test, `test_utf8_log_cap_stdin_does_not_echo_unicode_log`. DEC-1529/1530 added a **2,000,000-byte global JSON/stdin text ceiling**, so a stdin input containing one raw log over the independently enforced **2,000,000-byte per-log** ceiling cannot reach the per-log decoder: its JSON document must be even larger than the log due to JSON field overhead. The old assertion incorrectly required `BUNDLE_RAW_LOG_UTF8_OVERSIZE` from the stdin path when the correct earlier error is `BUNDLE_JSON_TEXT_UNREVIEWED`. Rename and correct that test without weakening either budget. Direct in-memory input can still independently reach the per-log or aggregate UTF-8 raw CI log guards.

Eight new tests demonstrate this source-specific diagnostic precedence, direct per-log/aggregate budget retention, small multibyte positive controls, no echo, and permanently false original OS/server/annual authorization flags. This is synthetic input-contract verification, not permission for annual workflow execution.

Own exact-head Phase 3/full historical/general CI plus independent qualified review required. DEC-650/#820 independently witnessed original protected OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected dispatch/retry, originals/archive/artifacts, installed workflow/security changes, merges, deployment or trading.
