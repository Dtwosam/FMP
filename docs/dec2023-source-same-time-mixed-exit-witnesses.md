# DEC-2023 — Equal-timestamp mixed scheduled and target source witnesses

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2271 at `cf94a8d53facea5f250251373f8e5d33ac1fa891`.

The source engine can close an existing position under its scheduled TIME_EXIT before processing new entries at the same bar timestamp, with another trade subsequently closing via target on that same bar. The source writer then sorts published trade rows by exit timestamp and ID, not actual realization order. DEC-2008's checkpoint multiset tracks the realized sequence; DEC-2022 enforces exact scheduled-close precedence over other exit reasons. These two semantics need concurrent coverage when the published trade IDs reverse the actual close sequence.

Four source-defined tests exercise: accepted Z-before-A equity witness with a Z TIME_EXIT and A TARGET (writer rows A-before-Z); a self-rehashed additional A schedule at the same timestamp that must reject the false TARGET; rehashed TIME_EXIT assigned to unscheduled A instead of scheduled Z; and generic one-trade TARGET at planned time compatibility. No production source change in this draft.

**7,179 cumulative proposed source-defined test methods** (+4). Own exact-head Phase3/full historical-general CI mandatory. #2266–#2269 failed suites stay failed; repairs #2270 and onward require independent validation. No authenticated external quote, execution, strategy profitability or authorization claim.

Phase8A #779/#820/#821 and eight independent external security proof packages remain blocked. No protected annual research, installed workflows/refs/runners, strategy promotion, merges, broker orders or real capital.
