# DEC-1767 — Published Phase7 historical profit/loss contribution

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2013, SHA `7ed223336f68b6776cc87b85949a35cf526d3f00`.

The historical seven-window Phase7 baseline earned **+$1,923.43 in positive windows** but suffered **−$1,166.16 in two negative windows**. On the source's **0.2-pip** assumption, losses consumed **60.6292%** of gross positive-window PnL, leaving **+$757.27**. The biggest winning window of **+$674.39** contributed approximately **35.062%** of gross positive-window gains (computed from published cents; tiny differences from the official 35.061843% are expected because original artifact data have greater precision). This ratio does **not** imply consistent profitability, a tradeable cost threshold, or a future edge.

DEC-1764/1765 now reports these directly reconciled retrospective dollar contributions. Each historic Stage2 window restarted at **$100,000**; the window PnLs/returns are not a compounded equity-curve result. We do **not** pretend to know the window-by-window results under the 0.5- or 1.0-pip slippage scenarios; only their original published aggregate statistics are available in this replay. This does **not** select Strategy V1 or conduct new annual research.

Adds **4** checks (**6443 proposed source-defined cumulative**), preserves pinned original Phase7 documentary source, no-follow bounded read and nonzero report exit3. No protected 2023 run385/attempt1, separate admin approval, workflow/runner changes, market feeds, broker/demo/live orders or trading. Issue #779/#820/#821 BLOCKED; exact-head Phase3/full historical-general CI plus independent qualified review required.
