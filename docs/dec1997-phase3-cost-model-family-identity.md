# DEC-1997 — Reject swapped built-in commission and financing tags

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2245 at `b7a8127167aaec824bf3c25e923bb9e5305febee`.

During source review of DEC-1996 the built-in-model audit was found to accept a `zero_financing` tag in the `commission_model` slot and a `zero_commission` tag in the `financing_model` slot: both looked like one-field zero-model configurations. However the source built-in implementations serialize model tags in exactly one category each. Fixing this avoids an independently rehashed run-identity claim that swaps risk/cost categories while preserving all checksums.

Distinguish the two zero-model source contracts and refuse cross-family use. Preserve custom provider model names, keep exact field-set checks for known built-ins, and keep the fixed-per-million commission category restriction. Two synthetic rehashed counterexamples assert swapped tags are rejected.

**7,089 proposed cumulative test methods** (+2); exact-head Phase3/full historical and general suites required. Previously failed jobs remain failed, no CI status inferred from proposed tests. Phase8A #779/#820/#821 and eight external security proofs outstanding; no annual run385 research, installed workflow/ref/runner changes, brokerage orders, strategy promotion, merges or real funds.
