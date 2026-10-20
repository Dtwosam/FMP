# DEC-1957 — Require canonical Phase3 artifact manifest ordering

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source/tests/docs child of PR #2205 `0f40d1ce465b3b85718b3ee6965f6cfeddec9253`.

`write_backtest_artifacts` deterministically emits four manifest entries sorted by the fixed artifact filename set, while `verify_backtest_artifacts` previously accepted arbitrary permutations of the same name/digest records. Extend the read-only verifier to require the exact canonical sorted order after all per-entry shape/hash checks; refuse noncanonical permutations as `ValueError`. Valid writer manifests preserve compatibility and roundtrip unchanged.

Two synthetic source-defined methods reverse an otherwise authentic writer-produced manifest and check rejection, and confirm normal sorted output still verifies. **6,994 cumulative proposed source-defined methods**. Own exact-head Phase3/full historical-general CI and independent reporting review mandatory. This protects canonical representation only; it does not authenticate input quote provenance or demonstrate profitable trading.

Historical failures #2178–#2191 and #2198 remain FAILED. Phase8A #779/#820/#821 and eight independent external administrator/ref/installed workflow/real OS isolation/provenance/fresh 2023 one-shot inventory/human approval proofs MISSING/BLOCKED. Accepted annual catalogue ends 2022/run384; protected 2023/run385/attempt1 and future annual research, Strategy V1 economics, shadow/demo/live broker capital and installed GitHub refs/workflows/rulesets/runner changes forbidden. No protected dispatch, merges, broker orders or money.
