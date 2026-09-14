# FMP Project State

**Updated:** 2026-09-14  
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 4 — Baseline Strategy Research  
**Phase status:** ACTIVE  
**Next milestone:** Merge the predeclared trend-continuation baseline and run its fixed source-free development/validation benchmark while retaining the frozen session-breakout candidate; final-test data remains locked

## Current baseline

- Instruments: EUR/USD, GBP/USD, USD/JPY
- Canonical history: 1-minute bid/ask
- Derived bars: 5m, 15m, 1h
- Frozen Phase 1 snapshot: 2015-01-01 through 2026-08-20 inclusive
- Frozen raw identities: 25,500
- Historical source: Dukascopy daily M1 BID/ASK `.bi5`
- Persistent immutable raw snapshot: Supabase private bucket `fmp-raw`
- Frozen Phase 1 plan SHA-256: `2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`
- Real-money trading: locked

## Phase 0 — PASS

- merge commit: `31cd8decca5dcb90f9d123ff33f71ac20413e269`
- checkpoint: `fmp-v1-phase0-source-of-truth`

Phase 0 source-of-truth rules remain authoritative except where later decision-log entries explicitly supersede them.

## Phase 1 — PASS

Phase 1 is closed for the frozen EURUSD/GBPUSD/USDJPY BID/ASK snapshot covering 2015-01-01 through 2026-08-20 inclusive.

- final provenance workflow: `phase1-final-cloud-audit`
- run ID: `34758527971`
- head SHA: `0ff45220cd930839059afcfba631e1e120cb38aa`
- result: SUCCESS
- artifact ID: `10318323714`
- artifact SHA-256: `53dbc184677393642e07c78fb6f2229a2c9bf5d8a38c2169935c23297003244b`
- acceptance: 25,500 expected/present raw-backed manifests, zero missing identities, zero unexpected identities, zero inferred `not_found`, zero checksum/size mismatches
- checkpoint: `fmp-v1-phase1-source-of-truth`

No further Phase 1 acquisition is required unless later integrity evidence demonstrates a defect.

## Phase 2 — PASS

Detailed acceptance evidence is `docs/phase2-acceptance-evidence.md`; DEC-015 records the acceptance review.

- exhaustive workflow: `phase2-full-history`
- run ID: `34782357048`, final attempt 2
- implementation head: `158c1c121655867b7fb2886fe755585dfcd682ec`
- result: SUCCESS
- per pair: 4,250 days; 8,500 verified raw reads; 140 months; 140 partitions for each 1m/5m/15m/1h; 561 processed-manifest artifacts
- row counts per pair: 1m 6,120,000; 5m 1,224,000; 15m 408,000; 1h 102,000
- EURUSD artifact `10325737935`: `db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3`
- GBPUSD artifact `10326096831`: `fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2`
- USDJPY artifact `10327600628`: `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`
- structural quality: zero duplicates, missing BID/ASK rows, required nulls, missing open-market minutes, or suspicious gaps across all three histories
- checkpoint: `fmp-v1-phase2-normalized-data`
- checkpoint commit: `80e763c46fc365d48922fb37de1a70dfe188de70`

Phase 2 is formally closed as PASS.

## Phase 3 — PASS

Detailed acceptance evidence is `docs/phase3-acceptance-evidence.md`; DEC-016 freezes simulator semantics and DEC-017 records the acceptance review.

- implementation merge: `96ca80b3baae4de511b5b14eb6c2f9d4d723645b`
- acceptance-runner merge / evidence code: `f7d98676d40f9af67f2d6f6cde36b3a465f68741`
- merged-main tests run: `34838682046` — 300 tests PASS; workflow YAML PASS; compile PASS
- formal acceptance run: `34838682032` — SUCCESS
- artifact ID: `10344943075`
- artifact SHA-256: `357152cef5118163f06f9d6166e7e02cdd7ed556a3de1c5723a6a6079bd6c4f0`
- independent deterministic/PnL/risk/manifest verification: PASS with zero validation errors
- checkpoint: `fmp-v1-phase3-backtester`
- checkpoint commit: `7685ba73f18457d5d3945f2fea21ceba3de81cf1`

Phase 3 is formally closed as PASS.

## Phase 4 — ACTIVE

DEC-018 freezes the chronological split, final-test lock, left-labelled timing bridge, exact session-breakout grid/cost assumptions, and unchanged Phase 3 risk settings. DEC-019 freezes the trend-continuation family-specific protocol while DEC-018 remains authoritative for shared research rules.

### EXP-20260914-001 — Session breakout baseline

- experiment status: PASS
- conclusion: PROMOTE one serious research candidate; detailed evidence is `docs/phase4-session-breakout-evidence.md`
- implementation / benchmark commit: `cc01929b80cbd1d5619de8476caa8f3d3410262e`
- merged-main tests: run `34848136901` — SUCCESS, 348 tests PASS, workflow YAML PASS, compile PASS
- unchanged Phase 3 acceptance: run `34848137105` — SUCCESS
- Phase 4 benchmark: run `34848137086` — SUCCESS
- matrix: 3 pairs × 3 signal timeframes × development/validation = 18/18 cells successful
- independently inspected benchmark rows: 486/486 with zero ZIP, manifest, identity, grid, candidate-reuse, or accounting discrepancies
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive
- Final-test touched: NO
- predeclared grid: buffers 0/2/5 pips × targets 0.5/1.0/1.5 × adverse slippage 0.2/0.5/1.0 pips per fill
- commission/financing: zero / zero for the mandatory-intraday-flat family
- risk: accepted Phase 3 policy unchanged

### Frozen serious candidate

Retain **USDJPY 15m, 5-pip breakout buffer, 1.5x target-range multiple** unchanged for later promotion testing.

At 0.2-pip adverse slippage:

- development: 620 trades, +5.8023% net return, +$9.3585 expectancy/trade, profit factor 1.1477, max drawdown 2.9370%
- validation: 362 trades, +3.7076% net return, +$10.2421 expectancy/trade, profit factor 1.1449, max drawdown 2.9860%

At 0.5-pip adverse slippage it remains positive on both splits (+3.4625% development / +2.5224% validation). All three USDJPY 15m target-1.5 buffer neighbors remain positive on both splits at 0.5-pip stress. At 1.0 pip no configuration in the full experiment remains positive on both development and validation; the selected point is -0.3228% development / +0.5769% validation.

Yearly results show material regime sensitivity, especially strong 2022 validation performance, so this is a serious research candidate rather than proof of deployment readiness. EURUSD supplies no baseline configuration positive on both development and validation; GBPUSD has two baseline-positive 5m target-1.5 configurations but both fail 0.5-pip stress.

The session-breakout candidate remains frozen unchanged while the second baseline family is evaluated.

### EXP-20260914-002 — Trend continuation baseline

- experiment status: PLANNED
- protocol: DEC-019; trend windows 2h/8h, 4h/16h, 8h/32h × 1.0R/1.5R targets; three-bar structural stop; fully closed London-session bars only
- pair/timeframe scope: EURUSD, GBPUSD, USDJPY × 5m, 15m, 1h
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive
- Final-test touched: NO
- cost stress: 0.2/0.5/1.0 adverse slippage pips per fill; historical BID/ASK spread; zero commission; zero financing
- risk: accepted Phase 3 policy unchanged
- benchmark size when merged: 18 workflow cells / 324 configuration rows
- current state: implementation and source-free workflow are under guarded review; no result-producing merged-main benchmark has run under EXP-20260914-002

Phase 4 remains ACTIVE. Candidate selection across the admitted baseline program is not materially complete, so the final-test period remains locked and checkpoint `fmp-v1-phase4-baselines` is not created.

## Phase 5 — UNSTARTED

Phase 5 has not started. No ML/feature-engine promotion is authorized by the Phase 4 baseline work completed so far.

Real-money trading remains locked; DEC-008 remains unchanged.
