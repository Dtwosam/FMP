# DEC-2029 — Cross-pair source economics and near-equal declared fee-rate tamper

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2277 at `2efa202b6d62e2d88cb9a738a0180529e913bedd`.

DEC-2028 assembled an integrated installed-source economic fixture with 1.5-pip adverse execution, deterministic reference-price gross and modeled slippage, a 25 USD per million per side built-in commission rate, zero financing, consistent net PnL and checkpoint equity. This test-only child extends that fixture to SHORT USDJPY, where source `pnl_usd` converts JPY quote PnL into USD, and SHORT GBPUSD, which reverses entry/exit order sides.

Two new source-defined methods: acceptance of combined model reports for SHORT USDJPY and SHORT GBPUSD; and a checksum-verified rehashed commission model rate changed from 25 to 25.0000001, causing only 2e-9 expected aggregate fee drift on 10,000 units while preserving stored trade fees, net PnL, checkpoints and manifest consistency. The source exact built-in commission witness must reject the forged rate.

**7,200 cumulative proposed source-defined methods** (+2). No production source change in this draft. Own exact-head Phase3 and full historical/general suites mandatory; #2266–#2269 failed workflows remain failed, and newer checks remain independent. These synthetic tests do not prove real FX quote provenance, cost billing, broker executions or profitable strategy performance.

Phase8A #779/#820/#821 and eight independent external security proofs remain blocked. No protected annual research, installed workflows/refs/runners, strategy promotion, merges, brokers, orders or real capital.
