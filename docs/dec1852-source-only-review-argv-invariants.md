# DEC-1852 — Fail closed on malformed embedded Python CLI arguments

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2098 `e1e3332da092b6e167efb6817c0a917df38f6ab6`.

The seven-source review executable's `main(argv)` may also be invoked from Python unit tests or embedding programs, where argument elements need not be OS-provided strings. Before this change, `main([None])`, `main([Path(...)])` or a noniterable argv value could raise an uncaught `AttributeError`/`TypeError` during duplicate-option inspection. An argument containing LF, ESC or NUL could also reach a file or option parser, potentially confusing logs and operator diagnostics.

Validate that the argument list is iterable, every element is a nonempty exact `str` and every character lacks ASCII C0 control or DEL before parsing. Reject unsafe input with one fixed **BLOCKED** stderr line, return 2 and **no stdout**. This is source-only Python API resilience; it is not an installed security control, a signature or trading approval. Normal offline reports still return nonzero 3 with BLOCKED.

Three new adversarial source-defined methods bring the cumulative proposed count to **6,744**. No protected 2023/run385/attempt1, actual administrator/runner OS proof, ref/workflow/ruleset edits, broker/demo/live orders, capital or profit. All eight independent security proof packages and #779/#820/#821 remain MISSING/BLOCKED. Exact-head Phase3/full regression CI and qualified review required.
