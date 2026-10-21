# DEC-2073 — Financing debit changes execution gross winner into net loser

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2321 at `2a3ba1986a4a172e497c6e6dfd7c71dce8d4797a`.

The source-defined economic model preserves positive pre-cost gross PnL on a valid directional execution. A sufficiently large permitted custom financing **debit** makes the **realized net PnL negative**. Performance distributions must therefore report zero wins, a numeric zero profit factor (real loss denominator), a negative average loss and expectancy, and a losing streak of one. Gross profitability *metrics* aggregate net results, not the source trade's pre-cost gross PnL field.

Six new source-defined methods accept the report and validate the actual `compute_backtest_metrics` result, then independently reject rehashed false full win rate, positive performance gross profit from pre-cost trade gross, null profit factor despite real losses, and a numeric average win without any net winner. Digest-verifiable tampering must fail opt-in economic audit. All source data synthetic; no claim about real funding rates.

**7,370 cumulative proposed test methods** (+6). Own exact-head Phase3 and full historical/general CI required before green credit. Historical failures remain failed. Phase8A #779/#820/#821 plus eight independent security proof packages remain BLOCKED. No production code, protected annual research, installed workflow/ref/runner change, merge, strategy promotion, broker orders or real capital.
