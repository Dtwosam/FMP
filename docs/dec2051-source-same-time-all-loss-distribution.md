# DEC-2051 — Equal-timestamp all-loss source distribution witnesses

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2299 at `2e6b009dba76ecb6f041641e92002ef747d5d9a3`.

The installed source evidence writer sorts equal-timestamp exits by trade ID, while the engine's equity checkpoints preserve realization order. In this synthetic installed-source witness, the engine closes Z-LOSS before A-LOSS at the same UTC instant but the artifact trade rows are published A-LOSS before Z-LOSS. Both exits are adverse STOP fills with net losses; therefore the realized-loss streak is two, gross profit and win rate are zero, profit factor is **numeric zero** (because gross loss is positive), and mean win remains null.

Four source-defined test methods cover a valid two-loss same-timestamp source report with reverse publication order, a canonical manifest-rehashed false shorter losing streak, a false null profit factor on a loss-only run, and a rehashed 1e-9 near-equal average loss. Every mutation is digest verified before independent semantic auditing. This child adds only tests and documentation; it does not change the installed engine or claim authenticated broker outcomes.

**7,275 cumulative proposed test methods** (+4). Own exact-head Phase3 and full historical/general regression suites required. Previous failed workflows remain failed, unfinished checks remain unconfirmed. Phase8A blockers #779/#820/#821 and eight independent external security proofs remain unresolved. No protected annual research, installed workflows/refs/runners, merging, strategy promotion, broker orders or real capital.
