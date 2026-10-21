# DEC-1979 — Reconcile reported win/loss distribution to sorted trades

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2227 `97f89ce9400758e51b31c205da04687742378e23`.

The optional Phase3 artifact audit checks sorted trade/rejection chronology, count, gross/net PnL and explicit costs but had not reconstructed `win_rate`, winning/losing averages, expectancy and longest winning/losing streaks. A fabricated `metrics.json` with internally valid SHA256 manifest could therefore report false strike rates and streaks despite intact stored trade rows.

Recompute optional distribution metrics from canonically sorted `trades.jsonl`, matching the original writer's exit-time sequence. Check ordinary finite numerics and exact integer streak counts; keep null for undefined empty-trade or zero-win/loss averages; tolerate bounded float-order rounding on writer-compatible metrics. Four synthetic methods exercise writer-valid win/loss economics, self-rehashed forged win rate/expectancy, false winning streak or Boolean alias, and empty-trade null metrics.

**7,036 cumulative proposed source-defined methods** (+4). Own exact-head Phase3, historical/general suites and review required. Older full regression failures remain FAILED, not overridden by an independent green Phase3 check.

Phase8A #779/#820/#821 and eight independent security proofs remain blocked; no protected 2023/run385/attempt1 or later research, strategy promotion, installed runner/ref/workflow mutation, broker orders or real money.
