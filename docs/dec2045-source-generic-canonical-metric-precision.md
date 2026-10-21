# DEC-2045 — Source versus generic canonical metric precision

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent draft PR #2293 at `4ee55c0581447774322fbe26c17025832291242f`.

Recent source-only acceptance work requires exact arithmetic for installed-engine optional performance metrics but retains measured near-equality tolerance when auditing generic or alternate-provider reports. DEC-2043 supplied a canonical metrics mutation helper so compatibility tests reach the opt-in auditor instead of being rejected prematurely by the strict artifact writer or a noncanonical JSON encoding.

This test/docs-only child adds four source-defined methods: a source-version `average_loss_usd` claim deviating by 1e-9 must fail despite its valid rehashed canonical manifest; the same near-equal generic claim must be admitted; a source-version `recovery_factor` deviating by 1e-13 must fail exact checkpoint reconstruction; and the same near-equal generic recovery claim remains admissible. Both source and generic cases share the same canonical byte mutation and manifest verification path, isolating the intended source-contract distinction.

**7,253 cumulative proposed source-defined test methods** (+4). Own exact-head Phase3/full historical-general suites required before any validated status; earlier failed runs remain failed. Internal metric consistency is not proof of strategy performance, authentic market quotes, or broker execution.

Phase8A #779/#820/#821 and eight independent external security proof packages remain blocked. No protected annual research, installed workflow/ref/runner changes, strategy promotion, broker orders, merges or real capital.
