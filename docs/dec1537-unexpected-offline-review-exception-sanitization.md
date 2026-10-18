# DEC-1537 — Sanitize unexpected offline JSON reviewer exceptions in CLI

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit, tests/docs-only child of #1782 at `0b4e64729c47361ae99f4e5d42321ece23d024f4`. Nine synthetic methods, **2,598 proposed source-defined methods**.

The stdin-only CI/source review command already catches stream read and write/flush exceptions, but its invocation of `review_bundle_json_text(raw)` could itself raise an unforeseen ordinary runtime/type/OS/Unicode/assertion/lookup exception. When the source-review component unexpectedly fails, return a canonical, single-line, non-echoing fail-closed verdict with `BUNDLE_OFFLINE_REVIEW_UNREVIEWED` rather than allowing an exception string or traceback to escape. Suppress no `KeyboardInterrupt`, `SystemExit` or `MemoryError`; do not retry the evidence review and do not emit original contents. Existing structured negative verdicts and local source-consistency-only success remain unchanged.

Nine synthetic tests inject runtime, assertion, OS, Unicode, overflow, index and value failures, verify safe stdout, one review invocation, no exception echo, all protected annual flags false, and the unchanged positive fixture. No authenticated provider data or original OS proof is established.

Own exact-head Phase 3/full historical-general CI plus qualified independent review required. DEC-650/#820 independently witnessed original protected OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected annual execution/retry, originals/archives/artifacts, installed workflow/security changes, merges, deployment or trading.
