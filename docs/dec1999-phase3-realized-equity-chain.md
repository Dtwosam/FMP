# DEC-1999 — Reconcile the trade-level realized equity chain

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2247 at `0e8671937b61f06ad71ea425ee30f6d97ca69436`.

The source engine starts risk equity from `BacktestConfig.starting_equity_usd`. When closing each position it records the current realized equity before the trade, realizes its net PnL, then records the after-equity. Canonical stored trades are exit-time/trade_id ordered. Until now the optional report audit reconciled every trade's **own** before+net PnL=after but did not ensure adjacent transitions formed a single realized-equity ledger. Two independently rehashed trades could claim contradictory equity balances even though each row is locally arithmetic-consistent.

Collect before/after equity of each fully validated trade and, when summary.run_identity contains source starting equity, validate each before value agrees with the preceding after value, beginning from source starting equity. Use bounded float tolerance for writer-compatible serialized values. Run the check only after per-record parsing so malformed records retain precise rejection classification; synthetic evidence without starting equity is intentionally unaffected.

Four new source-defined methods cover a continuous pair, a fully rehashed and internally consistent forged second trade, forged first trade with a different starting balance, and synthetic evidence without the optional source field. **7,098 cumulative proposed source-defined methods** (+4). Own exact-commit Phase3/full historical and general CI required. Earlier #2238–#2244 and #2246 full-suite PASS as individually verified; older failed histories unchanged. #2245 and #2247 status must be verified independently.

No live broker or capital claims, no source authentication of starting balance. Phase8A #779/#820/#821 and eight independent security proofs still BLOCKED. No protected annual research, merge, or installed workflow/ref/runner mutation.
