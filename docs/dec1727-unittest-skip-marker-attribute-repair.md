# DEC-1727 — Correct unittest skip-marker absent-on-unskipped-class assertion

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent test/docs correction to #1973 at `098ed201e45aab3e3c4bf0489b1b1ea35cd96cfd`.

Historical/general CI for DEC-1725/#1972 (run `39273287785`, job `118130930733`) completed **failure**, with four subtest errors in `test_nonexact_snapshot_aliases_do_not_skip`. The new test incorrectly read `Class.__unittest_skip__` unconditionally. Python `@unittest.skipIf(False, ...)` returns the class without adding that optional attribute; `AttributeError` is expected when the class has **not** been skipped. The requested assertion was negative: alternate environment values `0`, `true`, `01`, `yes` **must not skip**.

Repair only that access to `getattr(Class, "__unittest_skip__", False)` and continue asserting `False`. No production class, skip decorator, branch protection, annual workflow, private evidence or economic data is touched. All other 10 DEC-1725 methods, including positive exact snapshot skip, fail-closed missing-file normal mode and synthetic negative workflow-order mutations, remain unchanged. Proposed source-defined method count **5,907**. No CI failures are treated as passed merely because Phase3 succeeded.

No annual run385, retry, protected historical download, OS/admin-control change, workflow install, branch/tag/ruleset mutation, Strategy V1 synthesis/promotion, demo/live or real money. Own exact-head Phase 3/full historical-general CI and independent qualified review required; #779 remains **BLOCKED**.
