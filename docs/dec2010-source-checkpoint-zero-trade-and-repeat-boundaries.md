# DEC-2010 — Source checkpoint zero-trade and repeated-close boundary witnesses

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2258 at `9a1182377e1310fa65344aaee54aa81347c733d9`.

DEC-2008 changed source-engine checkpoint reconciliation to consume a multiset of realized trade transition witnesses in actual checkpoint order, handling same-time trade exits that differ from canonical trade-ID sort. Add three boundary tests to verify the source-only invariants without introducing new production code:
1. Valid source-engine zero-trade result retains exactly one initial checkpoint at starting equity.
2. A self-rehashed zero-trade result with its only checkpoint omitted passes the independent digest verifier but fails the opt-in source parity audit.
3. Two distinct source-engine trades closing at the same timestamp with zero PnL, identical before/after balances and identical checkpoint values are both consumed correctly as separate multiset witnesses.

These are source-defined synthetic test methods and do not claim externally authentic trades, real quote provenance or profitable performance. **7,130 cumulative proposed methods** (+3). Exact-head Phase3/full historical-general CI required; prior failed workflows remain failed, not relabeled. No new production code in this draft.

Phase8A issues #779/#820/#821 and eight independently supplied security proof packages remain blocked. No protected annual research, installed workflows/refs/runners, strategy promotion, brokers, merges, real capital or orders.
