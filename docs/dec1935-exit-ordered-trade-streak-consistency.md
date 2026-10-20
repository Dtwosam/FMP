# DEC-1935 — Reconcile streak metrics in published trade exit order

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit source/tests/docs child of PR #2183 `6a56e0fcc8bb4567446f334feab36109bef4a47b`.

`write_backtest_artifacts` writes `trades.jsonl` sorted by `(exit_timestamp_utc, trade_id)`, but the newly introduced optional streak reconciliation used the caller's raw `run.trades` ordering. For unsorted synthetic input, published trades could imply one streak while validated `longest_winning_streak` claimed another. Derive `pnls` and streak metrics from exactly the same stable sorted trades used for serialization; reuse the ordered collection when writing the JSONL. Ordinary chronological engine-produced trades remain unchanged.

Two synthetic methods prove correctly separated wins in chronological published output despite shuffled caller order, and reject a falsely claimed two-win streak based only on the unsorted input. **6,964 cumulative proposed methods**. Requires own Phase3/full historical-general exact-commit CI and independent financial evidence review; no market profitability evidence is implied.

Phase8A external #779/#820/#821 and eight independent security proof packages MISSING/BLOCKED. Protected 2023/run385/attempt1 and later research, Strategy V1 economics, shadow/demo/Phase10/11, broker/live funds and installed GitHub workflow/ref/ruleset/runner changes unauthorized. No protected dispatch, broker trade or money.
