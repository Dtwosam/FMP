# DEC-1945 — Exact builtin datetime at metric checkpoint boundary

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One exact-parent source/tests/docs child of PR #2193 `fa2e96760a582873a2d1e43c11f66afd9a49c7d3`.

The backtest metric calculation checked checkpoint timestamps with `isinstance(timestamp, datetime)`. Unlike the already hardened artifact writer, that admits caller-defined datetime subclasses and can execute arbitrary override code in `utcoffset()`. Require the exact builtin `datetime` type in the checkpoint metric validation before consulting timezone methods, retaining native UTC and chronological behavior. Two synthetic tests cover a hostile subclass getter that must not run and a genuine UTC checkpoint positive control. **6,974 cumulative proposed source-defined test methods**. Own Phase3/full historical-general CI and independent review required.

Full historical/general failures in PRs #2178, #2189 and #2190 remain historically FAILED. Separate exact-parent source repairs #2189 (NaN/inf error classification) and #2192 (financing subtotal overflow) have not retroactively changed those run outcomes; #2193 derived metric overflow fix is likewise not independent market or OS proof.

Phase8A blockers #779/#820/#821 and eight independent external security proof packages MISSING/BLOCKED. Accepted annual catalogue ends 2022/run384. Protected 2023/run385/attempt1, future annual research, Strategy V1 economics, shadow/demo/Phase10/11 broker/live capital, installed GitHub ref/workflow/ruleset/runner changes forbidden. No protected dispatch, orders or money.
