# DEC-2002 — Trade stop and target geometry source parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2250 at `70998fe610e17174228dcad2531e63bbb39bc8a2`.

The source risk policy `_valid_geometry` admits LONG trades only with stop<entry reference and target>entry reference when a target exists, and SHORT trades only with stop>entry reference and target<entry reference when present. Earlier reporting audit checks finite positive stop/target prices and adverse-only fill monotonicity, but self-rehashed files could carry a stop or target on the wrong side of the position.

Recheck source-defined directional stop/target geometry in the optional artifact auditor immediately after the price-domain and adverse-fill checks; retain the nullable target. The DEC-2001 SHORT fixture used a LONG stop and target while testing just adverse fills, so update those pre-existing tests to source-valid SHORT stop/target values rather than weaken geometry.

Four new synthetic methods cover long and short valid geometry, forged bad long stop/target, forged bad short stop/target and valid null target in both directions. **7,108 cumulative proposed source-defined tests** (+4). Historical/full suite statuses must be checked on exact commit; prior failures remain recorded, and Phase3 alone is not sufficient.

Phase8A issues #779/#820/#821 and eight independent external proofs remain blocked. No protected 2023 run385, later research, installed workflow/ref/runner changes, broker/demo/live order, strategy promotion, merge or capital deployment.
