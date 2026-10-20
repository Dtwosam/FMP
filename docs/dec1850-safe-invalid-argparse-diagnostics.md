# DEC-1850 — No attacker-controlled argparse error rendering

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2096 `6477e4a838fe93bba4fd2c5f3286cf5ea8bde83d`.

The DEC-1849 invalid-packet exception handler now escapes control characters, but malformed **command-line** options still triggered Python argparse's default `error()`, which prints a usage/error block containing attacker-controlled option values to stderr *before* the CLI returned status 2. A newline, ANSI terminal code or confidential-looking argument could become a misleading status line or unintended disclosure in the diagnostic.

Introduce `_FailClosedReviewParser` overriding `error()` to raise a fixed `InvalidReviewBundle` instead of echoing untrusted text. `main()` catches it and emits one stable `BLOCKED: invalid or abbreviated review argument` line, exit 2 and no stdout. The standalone `-h` or `--help` informational exception remains as reviewed; all combinations with evidence flags stay blocked by DEC-1848.

Three adversarial test methods (6,738 cumulative proposed source-defined) inject LF, terminal ESC, unknown options, missing triplet args and a private-looking value, and prove the original CLI never echoes it. Valid source-only evidence still exits 3 with BLOCKED, not permission; this is log integrity, not real administrator/no-bypass/runner OS witness. #779/#820/#821 and eight external independent proofs MISSING, protected 2023/run385/attempt1, downstream research, broker/demo/live/ref/workflow/ruleset/capital/profit all blocked. Own exact-head Phase3/full CI and qualified review required.
