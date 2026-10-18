# DEC-1552 — JSON text versus stdin reviewer verdict parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact one-commit tests/docs child of #1798 at `a392fde52ae15bf13e52ce99465c40e671dcbf3b`. Eight new synthetic unittest methods and one test helper; **2,731 proposed source-defined tests**.

Verify that the same caller-supplied JSON text gives identical fail-closed verdicts through the direct `review_bundle_json_text` entry point and the bounded stdin CLI. Cover malformed container closers, exact and one-over aggregate decoded JSON object member budgets, exact and over-limit global JSON array items, decoded duplicate escaped keys, nonfinite JSON constants, global Unicode UTF-8 bytes, and positive source-consistency controls across serializations. The CLI must emit exactly the reviewed five-field result schema and must never echo private input or mark protected annual authority true.

No changes to parser implementation, resource ceilings, workflow/security configuration, protected admission or trading. Both exact-head CI suites and independent qualified review required. DEC-650/#820 independent protected-original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 admission remain BLOCKED. No protected annual run or retry, original/archive/artifact access, merge, deployment or trading.
