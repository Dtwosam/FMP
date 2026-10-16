# DEC-1427 — CI critical-step sequencing and unique step-number evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit source-only test/docs child of #1650 DEC-1426 at dbbef380ce763fa6740bd311d880dbcef2c6a2ea. Eight new source-defined tests; **1,523 proposed source-defined methods** in the unmerged lineage.

The checked GitHub Actions job snapshots from #1648 show the historical/general test job executes its full historical unit-test step before package compilation, and the Phase 3 acceptance job generates deterministic evidence, verifies its shape and only then uploads the acceptance artifact. Checking each critical step for success alone would not detect unreviewed changes in their ordering. The new negative fixtures mutate the *caller-supplied* job step arrays or step numbers and reject duplicate/noninteger/missing step sequence metadata, an unsorted step listing, a historical compile before testing, or a Phase 3 artifact publication prior to shape verification.

This remains a source-only, offline evidence-shape check. GitHub Actions snapshots must be obtained and independently authenticated elsewhere. Passing fixtures and even completed GitHub CI do **not** prove real OS original-data no-write, exclusive immutable 2023 run385/attempt1 admission, or permission to run historical research. Neither the protected annual workflow nor its data or runner are opened or changed. Exact-head Phase3 and full historical/general CI plus independent qualified review required.

DEC-650/#820 actual OS-protected original no-write and DEC-651/#821/#779 one-shot server-side admission stay **BLOCKED**. No annual dispatch/retry, artifact/source read, branch/ruleset/permission mutation, merge, deployment, broker or trading.
