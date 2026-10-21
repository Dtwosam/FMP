# DEC-2076 — Zero net PnL after signed financing has null recovery

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2324 `8d7db1636d3bd4497f9bfe1337517d605d4a7b6b`.

Two independent one-trade source histories have opposite **execution gross** signs but identical neutral **net** outcomes: a positive-gross trade canceled by custom financing debit, and an adverse-stop gross loser canceled by financing credit. The checkpoint equity curve is unchanged in both. The correct maximum drawdown USD and fraction are numeric zero; the **recovery factor must be null**, not numeric zero, because its denominator (drawdown) is absent. The producer `compute_backtest_metrics` is independently checked for both classes.

Four new test methods cover valid artifact-audit roundtrips for both gross signs and hash-valid forgery rejection of positive drawdown USD, near-zero positive fraction, and numeric zero recovery. Distinguishing null from zero must remain precise. No production or workflow mutations and no claim of realistic signed financing.

**7,386 proposed methods** (+4). Require own exact-head Phase3 and full historical/general CI; pending checks unconfirmed, prior failed runs retain failure. Phase8A #779/#820/#821 and eight independent security proof packages BLOCKED. No protected research, installed workflows/refs/runners, merge, strategy promotion, orders or real capital.
