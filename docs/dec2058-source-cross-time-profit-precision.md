# DEC-2058 — Exact source profit metrics on cross-timestamp mixed streaks

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2306 at `77bc4a98ecfbce0b0a416482d06311153de5d0f9`.

DEC-2056/2057 established symmetrical four-close reports where timestamps and trade IDs change the published win/loss streak relative to checkpoint realization. This follow-on adds optional aggregate profitability claims to the same **source-engine** evidence: for both three-win and three-loss distributions, gross profit and gross loss must be positive, profit factor finite and positive, and the winning/losing averages must reconcile exactly to stored realized net PnL. The fixture deliberately omits net and expectancy aggregates to avoid introducing order-sensitive summation differences unrelated to the precision contract.

Five source-defined tests cover valid full profit distributions for both sign majorities and four independently manifest-rehashed near-equal 1e-9 lies: gross profit, gross loss, profit factor, and average loss. The verifier must accept each manipulated digest; the read-only semantic audit must reject each economic claim. No production, trading, or workflow changes.

**7,304 cumulative proposed methods** (+5). Exact-head Phase3 acceptance and full historical/general CI required. Preserve historical failed runs; pending results are not passes. Phase8A blockers #779/#820/#821 and eight independent security proofs still missing. No protected annual research, installed workflow/ref/runner mutation, merger, strategy promotion, broker orders or real capital.
