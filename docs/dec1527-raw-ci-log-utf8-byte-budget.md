# DEC-1527 — Bound UTF-8 byte volume of raw CI log evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict exact-parent one-commit tests/docs child of #1772 at `d6fb1f59da3a5d792a14d62ec0f2f64e2ac58bf5`. Nine synthetic methods; **2,509 proposed source-defined tests**.

DEC-1497 capped `raw_ci_runner_logs` at 2 million Unicode characters per run and 4 million characters total, but a multibyte Unicode log can require much more memory in UTF-8. Keep the character bounds and additionally reject a log that encodes to over **2,000,000 UTF-8 bytes per run** or **4,000,000 UTF-8 bytes in aggregate**. Check before run-ID parsing or nested CI log review; use fixed, non-echoing `BUNDLE_RAW_LOG_UTF8_OVERSIZE` or `BUNDLE_TOTAL_RAW_LOG_UTF8_OVERSIZE` diagnostics. Decode errors refuse with existing `BUNDLE_RAW_LOG_TEXT_UNREVIEWED`. This does not claim bounded Python Unicode memory internals or that a supplied log was authenticated by GitHub.

Nine synthetic tests cover exact and over 2-/4-byte character boundaries, aggregate budgets, error precedence, safe stdin refusal, ASCII baseline and clean synthetic source-only review. Annual execution authority remains false.

Own exact-head Phase 3/full historical-general CI and qualified independent review required. DEC-650/#820 witnessed protected original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 GitHub admission remain **BLOCKED**. No protected annual dispatch/retry, originals/archives/artifacts, workflow/security changes, merge, deployment or trading.
