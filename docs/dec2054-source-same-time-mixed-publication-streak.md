# DEC-2054 — Same-timestamp mixed-outcome canonical streak ordering

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2302 `8c4b86318e4565b9425ae7fe0354e002f7d03897`.

Canonical trade rows sort same-time closes by (exit UTC timestamp, trade ID). Source-engine equity checkpoints instead preserve realization order. This witness realizes loss, win, loss, so its checkpoint execution-order losing streak is one. At the same UTC close time, trade IDs A-LOSS, Z-WIN, B-LOSS publish as A-LOSS, B-LOSS, Z-WIN; the **canonical reported losing streak is two**. Gross profit, gross loss, positive finite profit factor, and one-third win rate remain functions of the same three realized outcomes.

Four source-defined methods cover that valid checkpoint/ledger-order split, a manifest-rehashed losing streak calculated from realization order instead of published order, an invented two-win streak, and a forged two-thirds win rate. Each mutation passes independent digest verification before the source semantic audit refuses the false metric. Source metric fields that could reflect input-order floating-point summation are intentionally omitted rather than rounded or fabricated.

**7,287 cumulative proposed test methods** (+4). Exact-head Phase3 and own complete historical/general regression required. Historical failing runs remain failed; in-progress checks earn no pass credit. Phase8A #779/#820/#821 and eight independent security proof packages still block protected research. No production source, installed workflows/refs/runners, merge, strategy promotion, broker orders or real capital.
