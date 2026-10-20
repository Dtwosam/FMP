# DEC-1893 — Reject malformed reference prices before rolling the risk day

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2141 `1894bdff838202bc5c4599114cbbb49de0afcb0d`.

`assess_decision` formerly advanced UTC risk-day bookkeeping before validating an entry price. A Boolean `True` could be accepted as a finite positive price by `math.isfinite`, while a malformed list or `None` raised TypeError, and an oversized integer could raise OverflowError. More importantly, those bad inputs could mutate the day state even though no valid risk assessment could proceed. Validate exact built-in numeric price type and finite positive value **before** rolling the day. For malformed inputs return a controlled `INVALID_SIZE` assessment and leave the UTC date, reservations and risk equity untouched. This deliberately prioritizes invalid-input rejection over daily-halt reporting only for malformed prices; valid inputs retain prior daily-halt and risk checks.

Two new Phase3 source-defined tests bring cumulative proposed methods to **6,855**. No actual market bars or orders are involved, and none of this establishes profitable expectancy or approved research. All changes are unmerged drafts requiring own exact-head Phase3/full regression and independent scoped risk review.

Accepted annual-first catalogue ends with 2022/run384. Protected 2023/run385/attempt1, later research, Strategy V1, shadow/demo/live real capital and installed GitHub workflow/ref/ruleset changes remain BLOCKED. #779/#820/#821 eight external independent protection/runner/provenance/inventory/human proofs MISSING.
