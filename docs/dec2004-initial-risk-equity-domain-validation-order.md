# DEC-2004 — Repair initial starting-equity validation ordering

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2252 `408015ca2ad9902ddd00b40fd276788a998b9dda`.

The exact historical/general workflow on #2248 (39588539182), #2249 (39588782874) and #2250 (39589047957) FAILED with three identical subtest failures each. Source test `test_audit_refuses_nonpositive_or_boolean_start_equity_in_identity` expects a specific source-domain rejection for starting equity 0, false and -100. DEC-1999's realized equity continuity check was inserted before the original domain validation, so each malformed value produced `trade risk equity continuity conflicts` instead. The new check did not show a broken equity calculation, but it prevented precise malformed-input detection and caused full suite failure.

Move the existing source starting-equity finite-positive (non-Boolean) domain validation to immediately after validating summary.run_identity is an object. Remove its late duplicate, retaining the existing optional source net-return, drawdown and checkpoint checks. Existing synthetic regression test covers all three failing cases; no proposed test inventory increase.

**7,112 cumulative proposed source-defined methods**; this commit needs its own exact-head Phase3/full historical-general validation before claiming green. The historical failures are preserved as failures. Phase8A #779/#820/#821 and eight independent security proof requirements still missing. No protected annual research, installed ref/workflow/runner changes, broker orders, funds or merges.
