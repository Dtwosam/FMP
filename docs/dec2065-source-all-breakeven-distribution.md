# DEC-2065 — Source all-breakeven same-time performance distribution

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2313 at `43319fd60d468a5eb1da0470db0bc2eec910dbbf`, which passed its own Phase3 and full historical/general suite.

Unlike a zero-trade report, two realized breakeven closes have a nonzero trade denominator. Win rate and expectancy are **numeric zero**, while average win, average loss, and profit factor are **null**; both streaks are zero. This source-engine witness preserves two real equal-timestamp position identities, two zero-net END_OF_DATA trade rows, and both zero-change realized-equity checkpoints. The writer publishes close IDs in canonical order independent of the original execution order.

Six source-defined tests validate the legitimate all-flat run and independently reject five manifest-rehashed false claims: null win rate, zero average win, zero average loss, numeric zero profit factor, and a fabricated winning streak. Digest verification still succeeds before the separate opt-in semantic audit refuses each fake metric. Production engine and report verifier remain unchanged.

**7,328 cumulative proposed test methods** (+6). Require own exact-head Phase3 acceptance and full historical/general regression; a pending check is not a pass. Older #2300–#2312 full failures remain recorded as failures, and #2313 is the green starting head. Phase8A issues #779/#820/#821 and eight independent external security proof packages remain unresolved. No protected data or research, installed workflow/ref/runner changes, merge, strategy promotion, broker orders, or real capital.
