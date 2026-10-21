# DEC-2066 — Mixed winning, breakeven and losing source trade distribution

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2314 `2fa13e5bb87fd6aef002700e753d678284c5a4c0`.

A source-engine backtest can realize a winning exit, a zero-PnL close, and a losing exit at the same UTC timestamp. The published order is A-WIN, M-FLAT, Z-LOSS; all three closes count in the trade denominator even though only two have directional PnL. The win rate is one-third, both win and loss averages are defined, profit factor is positive and finite because a losing denominator exists, and both longest sign streaks are one. Equity checkpoints must include the zero-change flat transition, not skip it.

Six source-defined tests accept this canonical source report and independently refuse manifest-rehashed false half win rate (ignoring the flat close), null profit factor (ignoring the real loss), zero average loss, false zero expectancy, and a fictional two-win streak. The manifest digest passes before the opt-in read-only semantic audit detects each economic conflict. Source-engine and production verifier logic remain unchanged.

**7,334 cumulative proposed methods** (+6), subject to own exact-head Phase3 and full historical/general validation. #2313 is the last confirmed full-green parent until descendant full suites complete. Historical failed runs remain failed. Phase8A #779/#820/#821 and eight independent security proofs remain blocked. No protected annual research, installed workflow/ref/runner changes, merges, strategy promotion, broker orders or real capital.
