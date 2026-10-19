# DEC-1674 — Restore a silently shadowed forged-approval regression test

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit test/docs child of #1920 at `7d0660f6f6df104f8ea2e1e4ae8c9d4d3198dd84`.

The portable bundle test class had **two methods with the same name**, `test_rehashed_nonstage_log_fake_approval_cannot_mask_wrong_pr_ref`. Python's class construction kept only the later one. They test different forged approval strings: `can_authorize_annual_run=true` versus the prose claim `protected 2023 annual run385 attempt1 permission granted`.

This repair gives the Boolean-claim test its own unique name, allowing **both** distinct cases to be discovered and run. It also adds one source-level AST uniqueness-guard test, which scans the methods of `PortableSourceBundleNeverGrantsAnnualRunAdmission` and fails if any `test_*` name occurs twice. The fixture's reviewer and protected-gate behavior are not altered.

**Source-defined total: 4,428 proposed methods** (+1 newly defined AST guard); **discoverable total increases by 2** (one restored existing test and one new AST guard). These totals remain proposed until exact-head CI confirms them. No annual authority is granted.

Own exact-head Phase 3/full general CI and independent qualified review required. Tests/docs only. No production/parser/resource-limit/workflow/security changes, protected originals/archive/artifacts, annual execution/retry, merge/deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
