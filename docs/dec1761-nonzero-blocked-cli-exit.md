# DEC-1761 — Nonzero exit for BLOCKED offline review output

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2007 at `a8c495ce8a08940677713f8b4ecf26e03f847c94`.

Safety defect: the DOC-only CLI used to print a BLOCKED report and **return 0**, even though green process exits are often (incorrectly) used as authorization gates in shell scripts or workflow conditionals. No code was authorized to consume this as a trading signal, but the success value invited accidental coupling.

Now any well-formed **BLOCKED** source report, in either JSON or Markdown mode, prints its full deterministic review data but exits **3 (BLOCKED)**. Invalid/missing/fabricated inputs still exit **2**, explicitly log `BLOCKED` to stderr and produce **no** partial stdout. There is *no exit-0 READY state* in this script; ordinary `--help` remains standard CLI help. Operator scripts must not use the report as permission or dispatch; only independent qualified human and real authority controls can unlock 2023/run385/attempt1.

Reconciles prior DEC-1752 and DEC-1756 docs and the two earlier CLI smoke assertions, and adds 4 focused safety tests (**6404 cumulative proposed source-defined**). No workflow source, process privileges, GitHub security/ref/tag/ruleset, protected annual data, dispatch/retry, broker demo/live action or trading changes. Issue #779/#820/#821 BLOCKED. Own Phase3/full historical-general CI and qualified review required.
