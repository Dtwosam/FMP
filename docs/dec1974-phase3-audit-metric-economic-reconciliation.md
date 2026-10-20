# DEC-1974 — Reconcile stored Phase3 metric economics with trade evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of PR #2222 at `acb81c8aff84e0e834564cdf54d260b9b5274fe2`.

The opt-in auditor already checks counts, canonical record shape, timestamp order and trade-level gross-minus-cost arithmetic, but a self-rehashed `metrics.json` can claim a different net PnL or execution-cost total and still pass the low-level SHA256 verifier and prior audit.

Add optional-key reconciliation of stored `net_pnl_usd`, `slippage_cost_usd`, `commission_cost_usd`, `financing_cost_usd` and `total_explicit_cost_usd` against the *same verified trades*. Reject non-finite aggregate economics, numeric Booleans and conflicting totals. Accommodate tiny float-order differences since the writer's inputs may differ in order from sorted JSONL. Absent optional metrics remain allowed, preserving the original writer schema.

Four source-defined synthetic methods cover normal writer-compatible economics including a financing credit, a self-rehashed forged net PnL metric, forged cost component/total and a forged Boolean metric. Projected inventory: **7,022 proposed source-defined methods** (+4 from PR #2221); project-wide full regression and Phase3 must pass at the new exact commit before claiming validation.

The earlier #2212 full regression is FAILED; #2222 repair is not green unless its own CI proves it. **This is internal consistency, not independent source/market provenance, realistic transaction costs, strategy profitability or authorization.** Phase8A #779/#820/#821 and eight external independent proofs remain missing. Accepted catalogue ends 2022/run384; protected 2023/run385/attempt1, future research, Strategy V1, shadow/demo/live brokers and real capital remain blocked.
