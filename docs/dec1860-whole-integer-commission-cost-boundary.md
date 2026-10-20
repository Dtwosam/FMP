# DEC-1860 — Fail-closed whole-integer commission position units

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Source-only exact-parent child of PR #2107 at `709d20aef720c504046948294fdca9d6002bfa09`. Any future merge requires explicit scoped cost-contract review, Phase3 and full historical/general CI. No installed workflow, privileged runner or broker is changed here.

DEC-1855 proved that the fixed per-million-per-side commission model silently accepts fractional units such as 0.5 although its interface requires integer position units. A fraction or Boolean can contaminate hypothetical after-cost sizing economics. Reject all values where `type(units) is not int` with ValueError. Preserve zero and positive/negative whole-unit absolute-position commission calculations. This does not change the rate, market data, risk model, engine version or broker.

Update the constants-only BLOCKED diagnostic to report `fractional_commission_units_rejected=true` and historical accepted flag false; no real market or broker activity. Add three tests covering fractions, Booleans/nonnumeric values and signed whole-unit symmetry: **6,763 cumulative proposed source-defined methods**. The ZeroCommission and ZeroFinancing input contracts remain outside this scoped proposal and require separate review.

Protected 2023/run385/attempt1 and all later annual research and Strategy V1 economic selection remain blocked, as are shadow/demo/live, broker orders, money and profit claims. All eight independent security/inventory/human proofs under #779/#820/#821 remain MISSING. Unmerged draft only.
