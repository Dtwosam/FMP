# DEC-1492 — Bound JSON integer digits and non-finite numeric overflow

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1737 at `18985407165db591f6bfa410d579c63edd153298`. Adds 12 synthetic unittest methods: **2,164 proposed source-defined tests**.

DEC-1478 rejected explicit JSON `NaN` and `Infinity`, but an enormous valid-looking exponent such as `1e400` parses as Python floating-point infinity without invoking `parse_constant`. Also, the Python runtime's global bigint digit limit is configurable and cannot be relied upon as a deterministic input resource limit. Use parser callbacks to reject any non-finite floating-point result and integers longer than 64 decimal digits before `int()`; retain finite numerical literals, structural/UTF-16 checks, existing JSON size and depth caps. Error codes remain safe `BUNDLE_JSON_GRAMMAR_UNREVIEWED`, with no raw numeric or evidence echo.

Twelve tests cover positive/negative/nested overflow, overlarge mantissa/exponent, finite underflow, normal finite decimal, at-limit/over-limit signed integers, huge nested digits, stdout non-disclosure and clean synthetic envelope source-consistency. This is local shape/source review, never GitHub provider attestation or protected annual execution authority.

Own exact-head PR Phase 3/full historical/general CI and qualified independent review required. DEC-650/#820 OS protected-original no-write and DEC-651/#821/#779 exclusive immutable one-shot protected 2023 run385/attempt1 server admission remain **BLOCKED**. No annual dispatch/retry, protected originals/archive/artifacts, workflow/security-setting changes, merges, deployment or trading.
