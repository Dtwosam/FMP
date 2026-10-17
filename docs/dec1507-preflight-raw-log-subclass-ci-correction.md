# DEC-1507 — Correct preflight diagnostic precedence for raw-log subclasses

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit forward-only tests/docs child of #1752, parent `1a91c683eeed2660f8e642a6ffdfd3d124e68097`. Nine additional synthetic unittest methods; **2,314 proposed source-defined methods**.

Both #1751 and #1752 passed Phase 3 but their historical/general suites failed the inherited `test_raw_log_string_subclass_is_rejected`. DEC-1505 intentionally added an early exact-built-in-type graph preflight, so a `str` subclass is rejected as `BUNDLE_STRUCTURE_BUDGET_UNREVIEWED` before the downstream raw-CI-log category's plain-string check. The older assertion demanded `BUNDLE_RAW_LOG_TEXT_UNREVIEWED`, a now-unreachable diagnostic for subclassed strings. Rename and correct that assertion without weakening the preflight or allowing subclass input.

Nine tests distinguish ordinary bytes/null category type errors from subclass and custom-object graph refusal, malformed run-ID keys, non-echoing diagnostic precedence, no invocation of the nested reviewer for untrusted objects, and positive direct/JSON source-consistency-only behavior. This changes no protected run authority.

Own exact-head Phase 3 and historical/general CI plus qualified independent review required. DEC-650/#820 independently witnessed protected-original OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected annual dispatch/retry, original/archive/artifact access, workflow/security changes, merge, deployment or trading.
