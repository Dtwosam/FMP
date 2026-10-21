# DEC-2056 — Canonical winning streak across a close-time boundary

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2304 at `c69e80429544c0af46ac2f1005ed72ad69d569ce`.

The source engine realizes a winner at UTC T+1, then a loss and two wins at UTC T+2. All three later closes share a timestamp but their trade IDs order the published rows as A-WIN, B-WIN, Z-LOSS. Publication must first sort by exit time, then trade ID: Z-EARLY-WIN at T+1 remains ahead of all later events. The canonical observed longest winning streak is three even though checkpoint realization order reads win, loss, win, win. The denominator includes the losing exit, so win rate is 0.75; longest losing streak is one.

Four source-defined tests cover this valid two-timestamp witness plus canonically rehashed false shortened winning streak 2, false 100% win rate, and a fabricated two-loss streak. Each digest-verifiable mutation must fail the independent opt-in semantic audit. Only test/docs source changes, no execution or reporting implementation changes.

**7,295 cumulative proposed methods** (+4). Own exact-SHA Phase3 acceptance and complete historical/general regression required; pending checks are not pass evidence and prior failed runs remain failed. Phase8A #779/#820/#821 and eight independent external security proofs remain blocked. No protected data/research, installed workflow/ref/runner mutations, mergers, strategy promotion, broker orders or real-capital actions.
