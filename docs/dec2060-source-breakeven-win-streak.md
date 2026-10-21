# DEC-2060 — A realized breakeven trade interrupts a winning streak

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2308 at `fd9a4d8483863c1a85c9b1e6de5069c2dfd41264`.

At the same UTC exit instant, a source-engine report can close a profitable trade, a legitimate zero-net END_OF_DATA trade, then another profitable trade. Its canonical trade rows publish A-WIN, M-FLAT, Z-WIN with net outcomes +11, 0, +11. The zero-net close is **not** a win or loss, but it **does** count in the trade_count and win-rate denominator and resets the consecutive winning streak. Correct optional metrics: trade count 3; win rate 2/3; average win 11; average loss null; profit factor null (no negative denominator); longest winning streak 1 and losing streak 0.

Five source-defined tests cover the valid zero-PnL checkpoint/ledger witness and digest-verified semantic rejection of falsely merged two-win streak, false 100% win rate, false numeric profit factor, and false zero average loss. This expands performance semantics without altering the installed backtester or reporting implementation.

**7,309 cumulative proposed methods** (+5). Own exact-head Phase3 acceptance and full historical/general suite required; #2300 historical failed workflow stays FAILED, including after DEC-2059 assertion repair. Phase8A #779/#820/#821 and eight independent security proofs still blocked. No protected annual research, workflow/ref/runner changes, merges, strategy promotion, orders, brokers or real capital.
