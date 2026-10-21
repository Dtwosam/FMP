# DEC-1976 — Fix summary-rewrite regression's JSON whitespace assumption

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2224 commit `68e1da9332a09d684ae503652763276681b2915a`.

GitHub full historical/general workflows for #2221 (39511460542), #2222 (39512941008), #2223 (39513209915) and #2224 (39513467981) all failed. The #2221 run had two failing tests; #2222–#2224 each had only `test_audit_detects_summary_rewrite_after_initial_verification` failing. That fixture incorrectly expects no space in the canonical pretty-printed summary (`"trade_count":0`), but the writer emits `"trade_count": 0`. The test aborts before the intended post-verification mutation occurs.

Parse the source-written JSON into an ordinary object, assert its original count, mutate the count to one, and write JSON bytes without modifying the existing manifest. This reproduces the original trust-boundary threat without relying on formatting whitespace, and should cause the opt-in auditor to refuse the bytes after their manifest digest no longer matches.

No source-code changes, no test count increase (**7,026 proposed methods**), and no historical failure reclassification. Passing Phase 3 is not proof the full historical/general suite passed. This exact commit needs both workflows verified.

Phase8A still blocked: #779/#820/#821, eight independent external proofs. No protected 2023/run385/attempt1, future research, strategy promotion, merges, ref/workflow/runner changes, broker activity or real capital authorization.
