# DEC-2062 — Equal-time neutral trade moves behind canonical winning streak

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2310 at `c6bdc9e3ac9ff88e81b56217a1fe032e82a8c319`.

The source engine realizes W, FLAT, W with one shared UTC exit timestamp and checkpoints 10000 -> 10011 -> 10011 -> 10022. With trade IDs A-WIN, Z-FLAT, B-WIN, the canonical publication is A-WIN, B-WIN, Z-FLAT. Unlike DEC-2060's published W/FLAT/W streak of one, this equally valid publication has **longest winning streak two** despite the zero-net close separating wins during realization. Canonical sorting drives performance streaks, while checkpoints independently prove each equity transition in realization order. The breakeven still counts toward the three-trade denominator: win rate 2/3 and profit factor null.

Four source-defined tests confirm the valid split in realization/publication orders, detect a forged realization-order streak of one, refuse inflated average-win 22, and reject a digest-verified altered checkpoint that no longer witnesses the flat transition. No source engine changes.

**7,318 cumulative proposed methods** (+4). Require own exact-head Phase3 and full historical/general regression. Prior failures remain failed, pending checks unconfirmed. Phase8A #779/#820/#821 and eight independent security packages remain unresolved. No protected annual research, installed workflow/ref/runner mutation, merging, strategy promotion, broker orders or real capital.
