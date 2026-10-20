# DEC-1899 — Strict identifiers and event fields for synthetic scheduled exits

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2147 `eef7ddc293bfd1c808c3c9f3c3e3a3753d76651c`.

A `ScheduledExit` previously used `decision_id.strip()` without confirming the ID's type, allowing newlines, carriage returns or terminal-control characters in an exit's audit identity and raising uncontrolled AttributeError for non-string input. Require a nonempty printable ordinary string, consistent with the previous DEC-1898 Decision identifier contract. The shared symbol and UTC time guards from DEC-1896 apply to scheduled exits as well. Valid exit records, supported FX symbols and timing remain unchanged.

Three new Phase3 methods bring proposed source-defined tests to **6,868**. They cover malformed IDs, unsupported/unhashable symbols or non-UTC timestamps, and valid synthetic exits. No quote data or protected research was read. Unmerged draft only, requires own exact-head Phase3/full CI and scoped human review.

External #779/#820/#821 eight independent source/admin/OS/one-shot/human proofs remain MISSING/BLOCKED. Accepted annual Phase8A catalogue stops at 2022/run384. No protected run385/attempt1, downstream Strategy V1 authorization, demo/live broker or money, workflow/ref/ruleset or runner changes, or established profitability.
