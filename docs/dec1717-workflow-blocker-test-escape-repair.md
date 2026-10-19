# DEC-1717 — Exact-string and regex escape repair in DEC-1716 workflow blocker tests

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1963 at `f21fb1b9fb2cf6707a11e94de48b78450fdbde5a`.

Fixes **six test-fixture-only escaped source strings** in the DEC-1716 current installed-workflow blocker regression suite, without changing its twelve source-defined tests or the intended security boundary:

- Git SHA-1 object framing must use the actual null byte via Python `b"\\x00"`, rather than a literal backslash followed by `x00`.
- Split the workflow around real newline characters and join job sections with real newlines; the prior doubled Python escape representation treated them as literal `\\n`.
- Use actual regex escape classes `\\w`, `\\S` and `\\d` in three raw regular expressions instead of matching a literal backslash.

All remaining assertions still pin the installed main-only annual-workflow blob, three-job post-checkout and post-install authorization ordering, preflight source-metadata access before authorization and 18-cell catalogue inventory. **Passing tests remain evidence of the known blocker, not safety to execute**. Additional methods: **0**; proposed source-defined total remains **5,854**.

Exact-head Phase3/full historical-general CI and independent qualified review mandatory. No protected evidence, annual run385, privileged access, workflow/runtime/security-policy mutation, broker, demo, live or real-money action; issue #779 and independent OS isolation remain **BLOCKED**.
