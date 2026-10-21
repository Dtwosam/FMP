# DEC-2015 — Installed source scheduled TIME_EXIT parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2263 at `f50b3c38f4d8eaa389046dd2a8bc77fbb5c6e972`.

The installed Phase3 engine emits `ExitReason.TIME_EXIT` only when it finds a `ScheduledExit` for the open position's `decision_id`, with matching symbol and timestamp. Those canonical scheduled-exit descriptors are published in `run_identity.scheduled_exits` if the caller supplies any. Previously, the optional artifact audit verified the descriptors' shapes and order but did not connect them to stored TIME_EXIT trade records.

Capture a source-only index of the validated scheduled-exit descriptors keyed by decision ID. For each exact installed source-engine TIME_EXIT trade, require a matching index entry with the same symbol and recorded close timestamp. This does **not** require every scheduled exit to produce a time exit: a decision can be rejected or a position can hit its stop or target before the scheduled timestamp. Generic other-engine/synthetic reports remain unchanged.

Four new synthetic source-defined tests: valid time exit with matching descriptor; rehashed changed scheduled timestamp that passes manifest verification; TIME_EXIT with no scheduled descriptor; generic unscheduled TIME_EXIT compatibility. **7,148 cumulative proposed source-defined methods** (+4). This does not independently verify outside bar prices or market data; it checks the engine's own declared execution contract.

Own exact-head Phase3 acceptance and historical/general suite required before a pass claim. Existing failed runs stay failed. Phase8A #779/#820/#821 plus eight independent external security proofs remain blocked. No protected annual research, installed workflow/ref/runner changes, strategy promotion, merges, brokers, orders or real capital.
