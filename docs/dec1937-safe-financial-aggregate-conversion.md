# DEC-1937 — Controlled integer conversion overflow for economic aggregates

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One exact-parent source/tests/docs child of #2185 at `d7822e6c5a43a42fabbe1277225e7fdb3cfe4f32`.

Although each source financial field can be an ordinary finite Python integer, `sum` of large individually float-convertible integers may produce an integer too large for `math.isfinite` to convert. The writer already catches this class for aggregate net PnL but did not catch it for explicit cost and gross-profit/loss aggregates. Convert Python `OverflowError` to a controlled `ValueError` with the failing aggregate name, before filesystem mutation. Ordinary finite numbers, mathematical undefined-ratio behavior and source record economics remain unchanged.

Two synthetic methods cover a huge positive integer financing cost total and a balanced gain/loss case where net PnL is zero but gross profit overflows float conversion. **6,966 cumulative proposed source-defined test methods**. Own exact-head Phase3/full historical/general CI and independent financial review required. This is exception-atomicity only, not proof of correct market input or profitable Strategy V1.

Phase8A #779/#820/#821 and eight independent security proof packages remain MISSING/BLOCKED. Protected 2023/run385/attempt1 and future years, Strategy V1 economics, shadow/demo/Phase10/11, installed workflows/refs/rulesets/runners, broker/live capital remain forbidden. No protected research, orders or money.
