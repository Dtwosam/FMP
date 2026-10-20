# DEC-1889 — Fail closed for malformed risk pricing and position inputs

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2137 `ef6a608edda0e7607336a4ff4012e15e2909d67b`.

The `fmp.risk.sizing` helpers were typed but accepted Boolean scalar values through Python's numeric coercion, and a string or unhashable list used as a symbol/direction could produce an uncontrolled `TypeError` instead of a clear risk-input failure. `_positive_decimal` now requires an exact built-in int or float with positive finite value and converts float-conversion overflow into controlled ValueError. Pair lookup requires an exact supported string; P&L direction requires the LONG/SHORT enum; P&L units must be an exact positive integer, not Boolean. Normal EURUSD/GBPUSD/USDJPY synthetic sizing and P&L results are unchanged.

Three new Phase3 tests (**6,844 cumulative proposed source-defined**) cover Boolean/non-numeric price and budget fields, malformed symbol values and untyped direction/units. This is a proposed defensive risk-contract fix, not external market evidence, a validated Strategy V1 strategy, or an authorization for protected annual research.

Accepted Phase8A evidence ends at 2022/run384. Protected 2023/run385/attempt1, later research, shadow/demo/live broker orders, real capital and installed workflow/ref/ruleset changes remain BLOCKED. Eight independent security/provenance/runner/inventory/human proof packages #779/#820/#821 remain MISSING. Exact-head Phase3/full regression and independent scoped human review required.
