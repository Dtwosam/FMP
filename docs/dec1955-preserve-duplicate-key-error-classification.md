# DEC-1955 — Preserve exact duplicate-manifest-key refusal classification

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source/tests/docs child of PR #2203 at `198233bc901e5a99cc3aefa82eff47b5c2f99ab5`.

The Phase3 verifier's strict `object_pairs_hook` introduced by DEC-1950 correctly raises `ValueError("artifact manifest contains duplicate JSON key")`, but `verify_backtest_artifacts` caught **all** `ValueError` from `json.loads` and rewrote them as generic `"artifact manifest must be valid JSON"`. Existing duplicate-key regression tests explicitly require the more useful precise classification. Narrow the catch to the parser's `json.JSONDecodeError` and `UnicodeDecodeError` only; duplicate-key `ValueError` propagates unchanged and malformed syntax still gets the generic parse-error classification. Add one source-defined method covering both.

**6,990 cumulative proposed source-defined test methods**, +1. Exact-head Phase3/full historical-general checks and qualified verifier review mandatory. This source-only classification correction is distinct from DEC-1954's invalid duplicate-path test fixture; all prior full historical/general failures stay recorded as FAIL.

Phase8A #779/#820/#821 and eight independent security proof packages MISSING/BLOCKED. Accepted annual catalogue ends 2022/run384; protected 2023/run385/attempt1, future research, Strategy V1 economics, shadow/demo/live broker capital and installed GitHub refs/workflows/rulesets/runner changes unauthorized. DRAFT NEVER MERGE NEVER PROMOTE; no protected dispatch, merges, trades or capital.
