# DEC-1865 — Integrated synthetic backtest after-cost monotonicity regression

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent test-only child of PR #2112 `616ae1efe8fd17ff1f8a1a03d217e749b69dfb08`.

The Phase3 backtest cost model must carry quote-side slippage and commission through entry, exit and realized net P&L without accidentally rewarding increased friction. Using **three invented EURUSD quote bars** and one invented LONG decision, these deterministic tests execute the real Phase3 engine locally under several commission and slippage settings. With identical timing and baseline inputs, increasing the per-million commission rate must never improve net trade P&L. Similarly, increasing adverse slippage must raise synthetic BUY entry price, lower synthetic SELL exit price and never increase net results. A third test checks deterministic results and provenance labeling.

These are **not** market observations, a discovered trading signal, independently reviewed annual discovery, forward/live transactions, or a prediction of after-cost profitable expectancy. The code fixture explicitly labels all bars invented. There is no protected data, workflow dispatch or broker call. Three source-defined methods bring cumulative proposed tests to **6,780**.

The proposed cost input hardening in #2107–#2112 remains unmerged and must pass own exact-head full regression plus independent scoped review. Phase8A annual-first accepted catalogue ends at 2022/run384. Protected 2023/run385/attempt1, all later research, Strategy V1 selection, shadow/demo/real-money broker operations, installed workflow/ref/ruleset changes and capital are still BLOCKED. All eight security/inventory/human evidence packages under #779/#820/#821 remain MISSING.
