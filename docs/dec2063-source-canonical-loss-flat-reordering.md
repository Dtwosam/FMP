# DEC-2063 — Equal-time neutral trade moves behind canonical losing streak

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2311 at `b7950c26b6c9db0c2a51a5d7316474deebdc5349`.

The source realizes a loss, a flat END_OF_DATA close, and another loss, with matching initial/close checkpoints including a repeated equity value for the zero-PnL trade. The canonical writer orders same-UTC trade IDs as A-LOSS, B-LOSS, Z-FLAT, despite realization order A-LOSS, Z-FLAT, B-LOSS. The canonical longest losing streak becomes **two**, not one, while win rate remains zero, profit factor numeric zero, average win null, and average loss negative. Checkpoint order remains an independent witness, never quietly replaced by trade-ID publication order.

Four source-defined tests cover the valid dual-view report, semantic rejection of false realization-order losing streak 1, near-equal forged average-loss drift, and rejection of a manifest-rehashed checkpoint jump omitting the realized flat transition. No installed production logic or workflow changes.

**7,322 cumulative proposed methods** (+4). Own exact-head Phase3 and full historical/general regression required, prior failed checks remain recorded as failed, pending checks are unconfirmed. Phase8A issues #779/#820/#821 and eight independent security proofs remain BLOCKED. No protected annual research, workflows/refs/runners, merge, strategy promotion, broker orders or real capital.
