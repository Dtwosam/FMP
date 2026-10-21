# DEC-1977 — Audit realized risk equity arithmetic per stored trade

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2225 at commit `8feea38d2b852c714c023c4efeb6c39c572a0669`.

The Phase3 backtest engine's `finalize_position` stores `risk_equity_before_usd`, calls `record_realized_pnl` to add net PnL to realized risk equity, and records `risk_equity_after_usd`. The separate opt-in audit previously checked only each trade's gross-minus-cost arithmetic, identifiers, chronology and reported metric totals. A self-rehashed artifact could therefore misstate before/after equity yet pass the checksum and structural audits.

Validate each trade's two serialized risk-equity values are ordinary finite numerics, calculate `before + net_pnl_usd` in the engine's order, reject non-finite results, and compare to stored `after` with a bounded float tolerance. This does not change the canonical writer or low-level manifest verifier.

Three synthetic methods cover writer-compatible equity, self-rehashed false closing equity, and a forged Boolean before-equity. Proposed cumulative source-defined inventory **7,029 methods** (+3).

GitHub full-regression failures #2221–#2224 remain FAILED; #2225 and this exact head each require separate Phase3/full suites before claiming validation. Phase8A #779/#820/#821 and eight independent external proofs remain blocked. No protected research, live broker, real money, merge or installed runner/ref/workflow authority.
