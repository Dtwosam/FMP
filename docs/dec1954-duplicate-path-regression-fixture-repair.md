# DEC-1954 — Repair falsely valid duplicate-manifest test fixture

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent tests/docs child of PR #2202 at `e22ed4d51bf92a054710df18e1cf3b9b7659353c`.

**Historical negative CI evidence:** PR #2198 commit `72b23cabd75acf304569dba6d01fea5dec91ddf7` full historical/general [39503736058](https://github.com/Dtwosam/FMP/actions/runs/39503736058) **FAILED** in `test_verifier_refuses_duplicate_or_escape_manifest_names` (subcase forged='metrics.json'). The writer sorts artifact paths lexicographically, so `manifest["artifacts"][0]["path"]` already equals `metrics.json`; replacing that path with `metrics.json` leaves an intact valid manifest and correctly does **not** raise. This is a **synthetic test fixture defect**, not proof of a verifier duplicate-path bypass. Preserve historical full failure.

**Correction:** use the *different* already-present `rejections.jsonl` path in that test to produce a real duplicate, and add a source-defined test that iterates all four entry slots and duplicates a different entry's filename, rejecting each case. Product source is unchanged. **6,989 cumulative proposed source-defined tests** (+1); own exact-head Phase3 and full historical/general suites must pass before any candidate repair is claimed validated. This does not retroactively turn #2198 or potentially inherited later full CI into a pass.

Phase8A #779/#820/#821 and eight independent security proof packages remain MISSING/BLOCKED. Accepted annual catalogue through 2022/run384; protected 2023/run385/attempt1, future years, Strategy V1 economics, shadow/demo/live, broker capital and installed GitHub refs/workflows/rulesets/runners unauthorized. DRAFT NEVER MERGE NEVER PROMOTE, no protected dispatch, funds or trades.
