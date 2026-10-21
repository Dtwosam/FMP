# DEC-2013 — Declared source slippage boundary witnesses

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2261 at `231bb3c2df98f560dc170a69410a6916b854e456`.

DEC-2011 recomputes source entry/exit fill prices using the optionally declared fixed adverse pip displacement. This test-only draft adds four source-defined checks around boundary cases not yet independently exercised:

1. Source-version EURUSD LONG and SHORT with declared zero slippage retain exact reference prices for both fills, with recomputed net PnL and checkpoints.
2. A self-rehashed identity falsely claiming 1.5 pips for a zero-slip SHORT fill passes checksum validation but fails the optional source economic auditor.
3. Source-version USDJPY SHORT with 1.5 declared pips uses the correct 0.01 pip size and reversed buy/sell sides.
4. Source-version synthetic envelope without the optional `slippage_pips` field preserves backward compatibility.

**7,140 cumulative proposed source-defined test methods** (+4). No production source change in this draft. Own exact-head Phase3 acceptance and full historical/general regressions must be checked before claiming success; previous failed CI stays failed. Internal parity does not prove independent FX quote provenance or real executions.

Phase8A #779/#820/#821 and eight independently supplied security proof packages remain blocked. No protected annual research, workflow/ref/runner changes, strategy promotion, broker activity, real capital, or merge.
