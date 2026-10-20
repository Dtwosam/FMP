# DEC-1857 — Exact-head Phase 8A security and synthetic cost-input checkpoint

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent documentation-only child of #2103 SHA `7893020dd5280a9c01bb3403dcd49672afba83d6`.

Draft #2102 audits the **existing** untyped adverse-slippage side and fractional commission-unit behavior using fixed synthetic prices only. Draft #2103 tests correct-enum slippage monotonicity across EURUSD, GBPUSD, USDJPY and signed whole-unit per-side commission symmetry. The production backtest helper is **unchanged**, so the string `"BUY"` routed through the sell branch and fractional `units` contract gaps are **identified but not repaired**. These scripts/tests neither ingest protected annual market history nor estimate Strategy V1 expectancy or profitability.

As verified on 20 October, #2093–2094 own exact-head Phase3 and full general/historical regression PASS, #2095–2102 exact-head Phase3 PASS/full still IN PROGRESS, #2103 checks IN PROGRESS. Original #2092 full FAIL remains in the history. The 6,756 cumulative **proposed** source-defined test methods do not represent approvals, a merged main release or broker validation.

External qualified admin/ruleset/bypass lock or independently authorized immutable ref path (#779/#821), real early-admission runner OS protection (#820), frozen provenance, complete fresh annual run385 inventory and separate human 2023/run385/attempt1 decision remain MISSING. No protected run/market read, installed workflow/ref/ruleset/runner mutation, broker/demo/live trade, capital or financial performance claim. Own exact-head CI and qualified external review required.
