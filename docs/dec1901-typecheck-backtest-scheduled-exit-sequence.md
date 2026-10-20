# DEC-1901 — Type-check scheduled-exit collections before Phase3 engine access

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2149 `a39238db8223d343fe0f8e784be99d1f0d3246e8`.

The Phase3 engine already validates quote-bar and decision collections; its `_scheduled_exit_map` previously assumed every supplied scheduled exit had canonical `decision_id` and `symbol` attributes. A malformed input such as `[None]`, `[{}]` or a string may raise incidental Python AttributeError/TypeError rather than a controlled ValueError before trade simulation. Add an exact typed sequence gate before constructing the exit map, without changing duplicate exit detection, decision ID linkage or exit ordering.

Three new source-defined tests (**6,874 proposed cumulative**) cover malformed schedule inputs and members, ordinary empty lists/tuples, and invalid schedule rejection with a valid synthetic directional decision. This is a local, unmerged, invented-bar engine contract. It does not validate actual market data or Strategy V1 expectancy, and does not touch brokerage, privileged runner, installed workflow, ref or ruleset.

All eight independent external #779/#820/#821 proof packages remain MISSING/BLOCKED, and protected 2023/run385/attempt1 and any further annual research, shadow/demo/live money remain forbidden. Exact-head Phase3/full CI and qualified independent review required.
