# DEC-1770 — Exhaustive loss-concentration sensitivity of *published* Phase7 windows

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2016, SHA `2feef6eabc84a8f4521c49494fc27a643313ff7a`.

The source-only Stage2 Phase7 USDJPY 15m session_breakout baseline reported **+$757.27** net PnL across seven *independently reset* retrospective 0.2-pip windows (199 trades). To make concentration risk inspectable, this draft derives **all seven leave-one-window-out** and **21 leave-two-window-out** rounded-dollar arithmetic outcomes from the same published table; no new quotes, execution, backtest, resampling, confidence interval, or annual catalogue is created.

- Excluding the single strongest window, **2025-Q4**, leaves **+$82.88**; this small remnant illustrates material winner dependence.
- Excluding **2025-Q2 and 2025-Q4** together yields **−$591.29**. Five of the 21 possible two-window exclusions turn the historical dollar sum negative.
- These are *counterfactual omissions* from an existing seven-window historical table, **not independently sampled experiments or a portfolio distribution**, and are not a valid OOS inference or prediction. The source table is pinned by its Git blob and preserves both losing windows, adverse slippage, and a 1.0-pip negative aggregate.

Adds **5** targeted tests (**6456 cumulative proposed source-defined**) while the earlier PR #2016 repairs a demonstrated historical/general CI test failure in its own exact-parent draft. **No additional claims of research readiness or earnings.** Run385/attempt1, the 2023 protected annual research gate, #779/#820/#821 independent admin/runner controls, Strategy V1 selection and any broker/demo/live trading all remain BLOCKED. Own exact-head Phase3 and full historical/general CI and qualified review required.
