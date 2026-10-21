# DEC-2069 — Chronological close order places neutral before consecutive losses

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2317 at `943a256ff18e7cdf27301044c0ea564c2b8f9b89`.

The source realizes a loss and a flat close at UTC T+1 and a further loss at T+2. The writer canonically orders M-FLAT then Z-EARLY-LOSS at T+1 and A-LATE-LOSS at T+2, despite the later trade having a lexicographically earlier ID. Published loss streak is therefore **two**, although realization sequence LOSS/FLAT/LOSS has a one-loss streak. This complements DEC-2068's two-win boundary. A breakeven still contributes to the three-trade count, win rate remains zero, and **profit factor is numeric zero** because realized loss denominator is present.

Five source-defined tests accept the legitimate two-timestamp checkpoint/ledger witness and reject manifest-rehashed realization-order losing streak 1, illegal null profit factor, 1e-9 gross-loss inflation, and a premature final equity checkpoint timestamp. Each altered digest passes manifest verification before the opt-in independent semantic audit refuses the false claim. No production change.

**7,348 cumulative proposed test methods** (+5). Own exact-head Phase3 acceptance and full historical/general suite required. Historical full-suite failures remain recorded and pending checks unconfirmed. Phase8A #779/#820/#821 and eight independent external security proof packages still blocked. No protected annual research, installed workflows/refs/runners, merging, strategy promotion, broker orders or real capital.
