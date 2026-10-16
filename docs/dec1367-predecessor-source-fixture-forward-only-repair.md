# DEC-1367 — Correct source fixture indentation, never rewrite original CI

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict forward-only one-commit child of #1590 DEC-1366 at `020856096eb859ed71425475f7e20cf8f7bfc3d6`. **1,032 proposed source-defined test methods unchanged.** In the immediately prior newly authored predecessor review, the test asserted 15 spaces before a `test -z "$PREVIOUS_RUN_ID"` line while the committed annual workflow YAML actually has **14 spaces**. The source intent and underlying predicate are sound; only the fixture's exact whitespace was wrong. Correct that assertion in a future exact SHA, never revise #1590's immutable SHA or its eventual own full historical CI verdict.

This test-source correction touches neither checked-in annual workflow nor CLI/runtime, does not run historical jobs, access protected annual inputs, install policy, dispatch GitHub Actions, mutate broker/trading, or merge/promote. Every exact head requires its own complete successful Phase 3 plus full historical suite and qualified independent review.

DEC-650/#820 independent OS original no-write and DEC-651/#821/#779 exclusive immutable 2023 run385 attempt1 admission remain **BLOCKED**. No protected annual execution, retries or permissions changes authorized.
