# DEC-2016 — Source STOP exit reference price and gap-through bound

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2264 at `6052e3e4dca988636d8042c3226377a62c27fb1d`.

The installed Phase3 engine's `evaluate_exit` chooses a STOP fill at the stop price when the bar trades through the stop, or at the adverse bar open if the position gaps through the stop. For LONG trades the reference STOP fill may equal or fall **below** the stop; for SHORT trades it may equal or rise **above** the stop. A source report that labels a profitable/less-adverse reference fill as STOP cannot be produced by this exit evaluator, even if the report is internally hashed and its arithmetic balances.

When `backtest_engine_version` matches the installed version and `exit_reason=STOP`, reject a LONG `exit_reference_price > stop_price` or SHORT `exit_reference_price < stop_price`. This adds a semantic source bound without claiming external bar/price authentication, and preserves legitimate adverse gap fills, ambiguous STOP contracts and generic synthetic reports.

Four new source-defined test methods cover valid adverse gap fills in both directions, checksum-verified rehashed false STOP reasons for both directions, and generic synthetic flexibility. **7,152 proposed cumulative methods** (+4). Requires own exact-head Phase3 and full historical/general tests; no previous failure reclassified.

Phase8A #779/#820/#821 and eight independent external security proofs remain blocked. No protected annual research, installed workflow/ref/runner changes, broker orders, strategy promotion, real capital or merges.
