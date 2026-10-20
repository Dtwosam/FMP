# DEC-1800 — Preserve real no-follow reader capability during mock negative control

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2046, SHA `f784a853af77525ed0d980a504e0998182af8b7e`.

The DEC-1799 regression test intentionally wraps `os.open` to catch any write/create/truncate flags during source-only six-source compilation. The production source reader correctly requires `os.open in os.supports_dir_fd` before it trusts `O_NOFOLLOW` and directory descriptors. Patching `os.open` with a mock replaces the callable's identity, which would incorrectly make that capability check fail before any file was inspected, creating a *test-harness* failure rather than evidence of attempted writes.

In the guarded test scope only, include the mock wrapper in the `os.supports_dir_fd` capability registry while forwarding all actual calls to the saved original OS primitive. All attempts to use write flags still trigger the test failure. The source reader, its flags, the historical workflow/doc proofs, and production permissions are **unchanged**. The tests continue to distinguish a source-only regression guard from real runner isolation.

No new test methods (**6,596 cumulative proposed source-defined**), no security gate loosening or installed GitHub workflow/ref/ruleset change, protected 2023/run385 attempt1 access, broker/demo/live execution, money or economics. External #779/#820/#821 and eight independent proof packages remain MISSING/BLOCKED. Exact-head Phase3 and full regression CI plus independent review required.
