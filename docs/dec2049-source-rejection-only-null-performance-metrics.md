# DEC-2049 — Rejected-only source performance metric nulls

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2297 at `ff79e88515b73526e3a2cab1c5e9a2e70e4272bb`.

A source engine can reject one or more decisions without closing any trades. Such a run legitimately has nonzero rejection evidence and its initial equity checkpoint, but the profitability denominator remains empty. Win rate and expectancy remain null, while win/loss streaks remain zero, regardless of the number of rejected orders. DEC-2047/2048 verify null source metrics for zero-trade and one-sided closed-trade ledgers; this dependent test/docs draft exercises the distinct rejection-only outcome.

Four source-defined tests: valid exact source-engine NO_TRADE rejection with zero trades, one rejection and one checkpoint while optional performance metrics are null; a manifest-rehashed false numeric win rate; a rehashed false numeric expectancy; and a rehashed losing streak despite zero trades. Each manipulated canonical metrics JSON passes digest verification and must be refused by the opt-in semantic audit. No production source changes.

**7,268 cumulative proposed test methods** (+4), subject to exact-head Phase3 and full historical/general regression validation. Earlier failed suites remain recorded as failed; pending checks do not count as success. Phase8A issues #779/#820/#821 and eight independent external security proof packages remain outstanding. No protected annual research, installed workflow/ref/runner changes, merging, strategy promotion, brokerage/orders or real capital.
