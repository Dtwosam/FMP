# DEC-1531 — One checked output path for stdin and denied CLI arguments

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1776 at `a931b2e13f08074d0ffda748542e01203215072f`. Nine new synthetic regression methods, **2,545 proposed source-defined tests**.

The stdin-only review command already checked complete stdout write counts and flushed streams before claiming local source consistency, but its invalid-command-line argument branch used a direct unchecked `sys.stdout.write()`. Refactor to one narrow `_emit_safe_verdict` helper for both paths, preserving one compact JSON line, sanitized diagnostic fields, checked complete write, checked callable flush and ordinary output exception refusal. An invalid invocation always returns 2 and must not read stdin or echo argument contents, even if stdout is unusable. Successful source consistency still proves nothing about protected annual execution.

Nine synthetic tests cover rejection JSON and non-echo, no stdin access, short writes, broken pipe, flush exceptions/noncallable flush, exactly one flush and clean normal main-path success.

Own exact-head Phase 3 and full historical/general CI plus qualified independent review required. DEC-650/#820 independently witnessed original protected OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected dispatch/retry, original/archive/artifact access, installed workflow/security changes, merges, deployment or trading.
