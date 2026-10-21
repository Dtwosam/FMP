# DEC-2021 — Preserve gross-PnL regression test specificity after TARGET guard

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2269 at `71675571737dcf12a199fbf736bf27a6865aa406`.

The full historical/general suites of #2266–#2269 FAILED on the same single method `Phase3AuditSourceEngineReferencePnLTests.test_audit_refuses_rehashed_false_reference_price_gross_pnl`. Its rehashed fixture changed `exit_reference_price` while leaving `target_price` unchanged. DEC-2017 correctly rejects the resulting installed-engine TARGET mismatch before reaching the earlier gross-PnL reconstruction guard. The test's intended precise rejection `gross PnL conflicts with reference-price` was masked by its own now-invalid setup; this is not evidence the gross calculation is wrong.

Repair the *test only* by changing `target_price` alongside the forged `exit_reference_price`, preserving TARGET equality but leaving the original stored gross amount unchanged. Manifest rehash verification must still pass, and the source gross-PnL auditor must now report the intended economic mismatch. Add three tests for wrong trade units in EURUSD/GBPUSD, wrong USDJPY units (including quote conversion), and generic synthetic economic flexibility. No production change in this draft.

**7,171 cumulative proposed source-defined methods** (+3); 7,168 carried from #2269. The earlier #2266–#2269 runs remain failed; they must never be relabeled. Own exact-head Phase3 and full historical/general CI is required for this repair. This is internal consistency, not independent FX quote provenance, broker execution or profitable performance.

Phase8A #779/#820/#821 and eight independent external security proof packages remain blocked. No protected annual research, workflow/ref/runner mutation, strategy promotion, broker orders, capital or merge.
