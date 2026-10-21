# DEC-2071 — Source positive gross PnL becomes neutral after financing

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2319 at `8b8b938f4c959c5a7fb349d343b404b9b09d5be8`.

An executed trade can have a positive execution-price `gross_pnl_usd` while its realized **net PnL is exactly zero** after legitimate source-defined financing and explicit commission/slippage costs. The trade is economically neutral: its gross *performance* profit metric (sum of positive **net** trade outcomes) is zero, win rate is zero despite one completed trade, expectancy is zero, win/loss averages are null, profit factor is undefined, and both streaks are zero. This must not be confused with the trade's positive pre-cost gross-PnL field.

This fixture uses the existing accepted combined slippage/fixed-commission source trade and custom signed-financing source model; a deterministic financing debit exactly cancels the remaining PnL. Five source-defined tests verify writer/audit acceptance, installed compute_backtest_metrics classification, and refusal of independently manifest-rehashed false win rate, raw-gross-as-performance-gross-profit, and numeric profit factor. The opt-in audit must reject each forged claim *after* digest verification. No production changes and no assumptions of real trading returns.

**7,358 cumulative proposed methods** (+5). Own exact-head Phase3 acceptance and full historical/general suite required; pending checks unconfirmed. Prior #2300–#2312 completed full-suite failures remain failures, and #2313 is last full-green parent until descendants complete. Phase8A #779/#820/#821 and eight independent security proofs BLOCKED. No protected research, installed workflows/refs/runners, merges, strategy promotion, broker orders or real capital.
