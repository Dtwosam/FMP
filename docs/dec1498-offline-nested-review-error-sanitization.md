# DEC-1498 — Sanitize nested offline review runtime and OS errors

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1743 at `6ac70a810d4551a1ef9fb580f7db7b0f6f4393e2`. Adds **9 synthetic unittest methods**; **2,226 proposed source-defined tests**.

The portable source-evidence bundle delegate already fails closed on many parsing/type errors thrown by the nested composite reviewer. An unexpected `RuntimeError`, `AssertionError` or `OSError` could instead escape to the CLI and expose tracebacks or untrusted error strings. Catch these ordinary exceptions at the narrow nested-review call boundary and return only `BUNDLE_NESTED_EVIDENCE_UNREVIEWED`. Do **not** catch process-control `SystemExit` or `KeyboardInterrupt`, nor out-of-memory conditions.

Nine synthetic tests inject runtime, assertion, permission, OS, index and value errors; validate single-line safe stdin verdicts and negative annual flags; and verify a clean source-only fixture continues to pass. No protected original or annual artifact is accessed by this test. No errors are echoed and no provider authenticity is inferred.

Own exact-head Phase 3/full historical-general CI and independent qualified review required. DEC-650/#820 protected-original OS no-write and DEC-651/#821/#779 exclusive immutable one-shot protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected workflow dispatch/retry, protected originals/archives/artifacts, installed workflow/security changes, merges, deployment or trading.
