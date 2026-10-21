# DEC-2037 — Zero-trade and same-time source net-return boundaries

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2285 at `0faccada9487ff7af08173b69d8b3a6eaea13c8c`.

DEC-2036 ties the installed source's optional `net_return` metric exactly to canonical net PnL divided by source starting equity. In the installed source, no trades means zero net PnL and zero net return; the writer also calculates metrics after sorting equal-timestamp trade rows by their published exit-time/ID order. These edge cases need explicit checks without changing engine production code.

Three source-defined methods cover an accepted same-time pair with valid net return, accepted zero-trade source net return zero, and a rehashed +1e-13 forged empty-run net return that passes manifest verification but must fail the exact source ratio audit. **7,226 cumulative proposed source-defined methods** (+3). Own exact-head Phase3/full historical-general validation required; previous failures retained. These tests establish internal consistency, not authentic market quotes or financial performance.

Phase8A #779/#820/#821 and eight external independent security proof packages remain blocked. No protected annual research, installed workflows/refs/runners, strategy promotion, broker orders, real funds or merges.
