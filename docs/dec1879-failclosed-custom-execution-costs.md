# DEC-1879 — Reject malformed custom execution costs before computing net P&L

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2126 `0a28f6260a48fdfebf71cab6c0fdc4ad2df376dc`.

The Phase3 backtest permits structurally compatible custom commission and financing models, but execution previously passed their raw `cost_usd()` results directly into the position/exit records. A malicious or mistaken custom commission could return a **negative amount** and thereby inflate hypothetical net P&L; NaN, infinity, Boolean, string or enormous integer outputs could corrupt net P&L or risk equity. Add `_checked_model_cost` at entry commission, exit commission and exit financing boundaries, accepting exact built-in finite int/float results, requiring **nonnegative commissions**, and allowing **signed finite financing** to preserve legitimate rollover credits.

Four new Phase3 execution methods (6,817 cumulative proposed source-defined) test negative entry cost, nonfinite/Boolean/untyped entry costs, forbidden exit costs and legitimate negative financing credits versus malformed financing outputs. Engine aggregate overflow remains a separate boundary to review. The output is still invented or synthetic local backtesting, **not verified live/after-cost profit, broker activity, an authorized Strategy V1 or an installed security gate**.

All eight independently verified external proof packages #779/#820/#821 MISSING; accepted annual research ends at 2022/run384, protected 2023/run385/attempt1 and later phases and demo/live/real capital remain BLOCKED. No protected workflow/ref/ruleset mutation, data read or broker order. Requires exact-head Phase3/full CI and qualified scoped review.
