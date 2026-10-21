# DEC-2057 — Canonical losing streak across a close-time boundary

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2305 at `b31aa098825ba37e0733007afc500716577813cb`.

The source engine realizes one loss at T+1, then a win and two more losses at T+2. The writer's canonical sort places the earlier loss first regardless of its Z-EARLY-LOSS trade ID, and the three equal-time later rows A-LOSS, B-LOSS, Z-WIN in ID order. This yields a canonical **three-loss streak** and a one-win streak even though checkpoint realization order is loss, win, loss, loss. One winning close among four gives a win rate of exactly 0.25.

Four source-defined tests cover a valid checkpoint-aware two-timestamp witness; canonically rehashed false shorter losing streak 2, false zero win rate, and invented two-win streak are digest-verified but must fail independent semantic audit. No engine or reporting production changes.

**7,299 cumulative proposed methods** (+4). Exact-head Phase3 acceptance and full historical/general regressions required; prior failures remain failed and pending checks unconfirmed. Phase8A blockers #779/#820/#821 and eight independent security packages remain unresolved. No protected research, installed workflow/ref/runner changes, merge, strategy promotion, orders, broker use or real capital.
