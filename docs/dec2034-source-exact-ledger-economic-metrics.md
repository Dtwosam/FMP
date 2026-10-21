# DEC-2034 — Exact installed-source economic metric aggregation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2282 at `4255b2771c155fc2929a76f049e19eb2567df906`.

The installed source's `compute_backtest_metrics` computes net, slippage, commission and financing totals by summing the already-canonical sorted trade sequence. The optional artifact audit walks the same canonical `trades.jsonl` sequence, adding the identical published float amounts. It then recomputes the optional `total_explicit_cost_usd` from those cost totals. The prior general-purpose 1e-8 absolute tolerance accommodated synthetic providers' differing aggregation orders, but the installed source writer does not do separate rounding that justifies accepting a near-equal forged metric.

For reports declaring the exact installed `backtest_engine_version`, require exact equality between each **present** economic metric and the canonical trade-ledger aggregate. Preserve the historic tolerance for synthetic and alternate source reports. Do not require optional metrics to be present, reorder the ledger, change writer output or infer external market data authenticity.

Four source-defined methods: valid combined source net/cost metric totals; rehashed 1e-9 metric net PnL mutation; rehashed 1e-9 total-explicit-cost metric mutation; generic near-equal aggregate compatibility. **7,217 cumulative proposed source-defined methods** (+4). Exact-head Phase3 and full historical/general CI remain mandatory. Previously failed checks are preserved. Phase8A #779/#820/#821 and eight independent security proofs remain blocked. No protected research, workflow/ref/runner changes, strategy promotion, broker orders or real capital.
