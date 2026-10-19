# DEC-1738 — Strict Boolean/integer aliases must fail readiness review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs-only child of #1984 at `2d2af3641e301c9b05a3fc54fcae95048a4f7e5a`.

Adds **30 source-defined methods** (**6,052 proposed total**) focused on a real CI-found false-equivalence. Python considers `True == 1` and `False == 0`; this caused the DEC-1729 mutated run385 attempt fixture to fail early and made seven descendant full suites red. DEC-1737 repairs its generic mutation-detection precondition with canonical JSON strings.

These tests run that **same repaired DEC-1729 helper and actual DEC-1728 existing strict refusal assertions** against 14 independently spoofed protected authority flags (using integer `0` instead of Boolean `false`), four blocked-year promotion markers, three previously observed `main` administrative-state fields, seven economics/prospective-demo/administrator evidence flags, and the one-shot 2023/run385 attempt value as Boolean `true` rather than exact integer `1`. A final control demonstrates that canonical JSON distinguishes both Boolean/integer alias pairs even though Python equality does not.

All cases require the **original guard's `AssertionError`**, not a failure in setup or serialization, and preserve the pristine original synthetic JSON ledger. This protects type fidelity of source-only denial flags. It does not establish administrator access, approved identity, actual runner host privilege, one-shot authorization, actual 2023 annual execution, Strategy V1 profitability or broker/live safety.

Own exact-head Phase3/full historical-general CI and independent qualified review required. No protected annual read, runtime, production/parser/workflow/security change, GitHub ruleset/tag/ref mutation, dispatch/retry, demo/live order or trading. Issue #779 and DEC-650/#820, DEC-651/#821 remain **BLOCKED**.
