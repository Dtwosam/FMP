# DEC-1910 — Reject corrupted reservation risk state before approval

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent source-only child of PR #2158 at `e8b7e6b22d5a71ff0e71dff0c9c9ebc4c54d5920`.

`RiskState.reservations_usd` is a mutable dictionary. The previous `total_reserved_risk_usd` used plain `sum` without verifying its elements. A corrupted `NaN` entry can make the simultaneous-risk comparison false, potentially approving additional risk on invalid ledger data. Reject non-dictionary containers, malformed reservation IDs, wrong/nonpositive/nonfinite/overflowing amounts and nonfinite summed totals. Assess decisions against the validated total **before** advancing the UTC risk day. Normal amounts and valid existing reservation calculations are unchanged.

Three new source-defined synthetic tests cover contaminated ledger denial before approval or mutation, malformed IDs/map types and overflowing aggregates, and a valid sum/release control. **6,895 cumulative proposed source-defined methods**. Own exact-head Phase3/full historical-general CI and independent qualified risk review required; no inherited check proves this SHA.

Phase 8A retains #779/#820/#821, all eight independent security proof packages missing, and protected 2023/run385/attempt1, later annual research, Strategy V1 economics, shadow/demo/Phase10/11, broker/live funds BLOCKED. No protected data, dispatch, installed GitHub workflow/ref/ruleset/runner change, brokerage action or verified profits.
