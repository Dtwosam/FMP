# DEC-2042 — Source economic error-order and generic metric fixture repair

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2290 head `7ac08ff62dcf7b2c0c219ca6a58ef859eeb2831e`.

Full historical/general runs for #2280–#2285 recorded FAIL despite each Phase3 acceptance success. Seven recurrent test failures arose because DEC-2031 immediately rejected an exact source net-PnL inconsistency **before** checking the underlying source reference gross, slipped execution cost and built-in commission witnesses. Each test deliberately tampered one economic component while preserving its stored net amount, expecting a precise component-level source error. This is a validation-order regression, not permission to weaken any source economics.

The repair computes the finite net reconciliation witness as before, then performs exact source gross / declared pips / slippage / built-in commission and financing validations, **then** rejects any remaining net mismatch before adding values to ledger totals. This restores specific root-cause rejection without allowing a bad net amount through. The same source exact-net requirement remains active.

The #2283 test `test_audit_keeps_generic_metric_aggregate_summation_tolerance` independently errored during `write_backtest_artifacts`, because the writer correctly refuses an inconsistent claimed metric. Repair the test setup by writing consistent generic evidence, then deliberately changing and rehashing `metrics.json` in the writer's canonical JSON indentation and verifying its manifest before invoking the opt-in auditor. Generic aggregate tolerance remains unchanged.

Two new source-defined tests cover precise gross and commission error ordering despite an inconsistent net witness. **7,243 cumulative proposed source-defined methods** (+2). #2280–#2285 historical failures remain failures; this draft requires its own exact-head Phase3 and full historical/general suites. No market quotes, broker executions, cost billing or profits are authenticated.

Phase8A #779/#820/#821 and eight independent external security proof packages remain blocked. No protected annual research, installed workflow/ref/runner changes, strategy promotion, merges, orders, brokers or real capital.
