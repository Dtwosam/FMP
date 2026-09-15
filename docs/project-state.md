# FMP Project State

**Updated:** 2026-09-15
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 7 — Walk-forward Evaluation
**Phase status:** ACTIVE
**Next milestone:** execute the frozen seven-window Stage 2 evaluation only for the audited `session_breakout` Stage 1 survivor; required 2025/2026 data remains locked until the exact Stage 1 PASS package is verified before source I/O

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
- per pair: 4,250 days; 8,500 verified raw reads; 140 months; 140 monthly partitions for each 1m/5m/15m/1h timeframe; 561 processed-manifest artifacts
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

## Phase 4 — PASS

DEC-018 freezes the chronological split, final-test lock, left-labelled timing bridge, exact shared cost assumptions, and unchanged Phase 3 risk settings. DEC-019 freezes the completed trend-continuation family-specific protocol, DEC-020 freezes the completed mean-reversion family-specific protocol, DEC-021 records the mean-reversion rejection, DEC-022 freezes the previous-day high/low rejection protocol, DEC-023 records the EXP-004 FAIL / REJECT outcome, DEC-024 freezes the EXP-005 rolling volatility-breakout protocol, DEC-025 records the EXP-005 PASS / PROMOTE outcome, DEC-026 freezes the EXP-006 session high/low sweep-rejection protocol, DEC-027 records the EXP-006 FAIL / REJECT outcome, and DEC-028 records the Phase 4 PASS acceptance review; DEC-018 remains authoritative for shared research rules.

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

The session-breakout candidate remains frozen unchanged while subsequent baseline families are evaluated.

### EXP-20260914-002 — Trend continuation baseline

- experiment status: FAIL
- conclusion: REJECT; detailed evidence is `docs/phase4-trend-continuation-evidence.md`
- implementation / benchmark commit: `d1c821cb8b4bfaaddbc334fee0f2f3b1dfe054a2`
- merged-main tests: run `34863705694` — SUCCESS, 378 tests PASS, workflow YAML PASS, compile PASS
- unchanged Phase 3 acceptance: run `34863705935` — SUCCESS
- Phase 4 benchmark: run `34863705913` — SUCCESS
- matrix: 3 pairs × 3 signal timeframes × development/validation = 18/18 cells successful
- independently inspected benchmark rows: 324/324 with zero ZIP, manifest, code/data identity, split, grid, candidate-reuse, or accounting discrepancies
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive
- Final-test touched: NO
- frozen grid: trend windows 2h/8h, 4h/16h, 8h/32h × targets 1.0R/1.5R × adverse slippage 0.2/0.5/1.0 pips per fill
- commission/financing: zero / zero for the mandatory-intraday-flat family
- risk: accepted Phase 3 policy unchanged
- promotion screen: zero configurations have positive net return, positive expectancy, and profit factor above one on both development and validation at 0.2-pip baseline; zero also survive at 0.5 or 1.0 pip
- failure character: isolated split-only winners reverse across chronology. GBPUSD 1h `8h/32h / 1.5R` is +14.8309% development but -2.7022% validation; USDJPY 15m has zero development qualifiers but two validation qualifiers
- no trend-continuation candidate is promoted and no post-result parameter expansion is authorized under EXP-20260914-002

### EXP-20260914-003 — Mean reversion baseline

- experiment status: FAIL
- conclusion: REJECT; detailed evidence is `docs/phase4-mean-reversion-evidence.md`
- implementation / benchmark commit: `87003a3982ca61eb6fd030c5291616d98dbb0c1a`
- merged-main tests: run `34875463710` — SUCCESS; workflow YAML PASS; compile PASS
- unchanged Phase 3 acceptance: run `34875463714` — SUCCESS
- Phase 4 benchmark: run `34875463677` — SUCCESS
- matrix: 3 pairs × 3 signal timeframes × development/validation = 18/18 cells successful
- independently inspected benchmark rows: 324/324 with zero ZIP, manifest, code/data identity, split, grid, candidate-reuse, or accounting discrepancies
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive
- Final-test touched: NO
- frozen grid: lookbacks 4h/8h/16h × fresh-excursion thresholds 1.5σ/2.0σ × adverse slippage 0.2/0.5/1.0 pips per fill
- commission/financing: zero / zero for the mandatory-intraday-flat family
- risk: accepted Phase 3 policy unchanged
- promotion screen: zero of 54 pair/timeframe/lookback/threshold points survive the 0.2-pip development-and-validation gate
- stronger baseline result: on both development and validation, zero of 54 0.2-pip rows have positive net return, zero have positive expectancy, and zero have profit factor above one
- no mean-reversion candidate is promoted and no post-result parameter expansion is authorized under EXP-20260914-003

### EXP-20260914-004 — Previous-day high/low rejection baseline

- experiment status: FAIL
- conclusion: REJECT; detailed evidence is `docs/phase4-previous-day-rejection-evidence.md`
- protocol decision: DEC-022 APPROVED; outcome decision: DEC-023 APPROVED
- implementation / benchmark commit: `7db3a747236942fa393521e5866e3245d1a22a99`
- merged-main tests: run `34883815429` — SUCCESS, 423 tests PASS, workflow YAML PASS, compile PASS
- unchanged Phase 3 acceptance: run `34883815462` — SUCCESS
- Phase 4 benchmark: run `34883815436` — SUCCESS
- matrix: 3 pairs × 3 signal timeframes × development/validation = 18/18 cells successful
- independently inspected benchmark rows: 162/162 with zero ZIP, manifest, code/data identity, split, grid, candidate-reuse, accounting, or cost/risk identity errors
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive
- Final-test touched: NO
- frozen grid: previous-day penetration buffers exactly 0/2/5 pips × adverse slippage 0.2/0.5/1.0 pips per fill
- commission/financing: zero / zero; historical BID/ASK remains authoritative for Phase 3 execution
- risk: accepted Phase 3 policy unchanged
- initial 0.2-pip screen: exactly one of 27 pair/timeframe/buffer points survives — USDJPY 5m / 5-pip buffer
- survivor development: +4.0039%, +$138.0644 expectancy/trade, PF 1.9002, 29 trades
- survivor validation: +0.0657%, +$2.3461 expectancy/trade, PF 1.0133, 28 trades
- robustness failure: validation turns negative at 0.5-pip slippage (-0.2343%, -$8.3685 expectancy/trade, PF 0.9547); both neighboring buffers are negative on both splits; validation is negative in 2021 and 2022 and positive only in 2023; top three winners contribute about 85.38% of validation positive R
- no previous-day rejection candidate is promoted and no post-result parameter expansion is authorized under EXP-20260914-004

### EXP-20260914-005 — Rolling volatility-breakout baseline

- experiment status: PASS
- conclusion: PROMOTE one serious research candidate; detailed evidence is `docs/phase4-volatility-breakout-evidence.md`
- protocol decision: DEC-024 APPROVED; outcome decision: DEC-025 APPROVED
- implementation / benchmark commit: `3bf36186900f5065e9e3ddced0305865433b9d69`
- merged-main tests: run `34888225240` — SUCCESS, workflow YAML PASS, unit tests PASS, compile PASS
- unchanged Phase 3 acceptance: run `34888225252` — SUCCESS
- Phase 4 benchmark: run `34888225242` — SUCCESS
- matrix: 3 pairs × 3 signal timeframes × development/validation = 18/18 cells successful
- independently inspected benchmark rows: 162/162 with zero ZIP, inner-manifest, code/data identity, split, grid, candidate-reuse, accounting, cost, or risk-identity errors
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive
- Final-test touched: NO
- frozen grid: rolling 8h reference × range-expansion multipliers 1.0x/1.5x/2.0x × fixed 1.0R target × adverse slippage 0.2/0.5/1.0 pips per fill
- commission/financing: zero / zero; historical BID/ASK remains authoritative for Phase 3 execution
- risk: accepted Phase 3 policy unchanged
- initial 0.2-pip screen: exactly one of 27 pair/timeframe/multiplier points survives — USDJPY 1h / 2.0x
- survivor development: +11.4235%, +$19.1670 expectancy/trade, PF 1.2321, 596 trades, max drawdown 2.5228%
- survivor validation: +5.5971%, +$15.3766 expectancy/trade, PF 1.1931, 364 trades, max drawdown 1.9853%
- 0.5-pip robustness: +6.5350% development / +3.2953% validation; PF 1.1297 / 1.1111
- 1.0-pip diagnostic: negative on both splits (-1.1416% / -0.4304%)
- robustness strengths: all six development calendar years positive, 2022 and 2023 validation positive, large sample, low drawdown, top-three winner dependence about 1.30% development / 2.22% validation positive R
- robustness weaknesses: 2021 validation negative; neighboring multipliers and adjacent timeframes do not confirm the development edge; 1.0-pip stress fails
- promoted serious candidate: retain USDJPY 1h / 2.0x / fixed 1.0R unchanged for later cross-family selection
- no post-result parameter expansion, alternate lookback, extra multiplier, target retuning, or rescue rule is authorized


### EXP-20260914-006 — Session high/low sweep-rejection baseline

- experiment status: FAIL
- conclusion: REJECT; detailed evidence is `docs/phase4-session-sweep-rejection-evidence.md`
- protocol decision: DEC-026 APPROVED; outcome decision: DEC-027 APPROVED
- implementation / benchmark commit: `120348d4a5df806f674551590610b216a9bc33ac`
- merged-main tests: run `34895426082` — SUCCESS; unit tests, workflow YAML validation, and compile PASS
- unchanged Phase 3 acceptance: run `34895426066` — SUCCESS
- Phase 4 benchmark: run `34895426037` — SUCCESS
- matrix: 3 pairs × 3 signal timeframes × development/validation = 18/18 cells successful
- independently inspected benchmark rows: 162/162 with zero ZIP, inner-manifest, code/data identity, split, grid, candidate-reuse, accounting, cost, or risk-identity errors
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive
- Final-test touched: NO
- frozen grid: 00:00–08:00 `Europe/London` session reference × penetration buffers 0/2/5 pips × adverse slippage 0.2/0.5/1.0 pips per fill
- commission/financing: zero / zero; historical BID/ASK remains authoritative for Phase 3 execution
- risk: accepted Phase 3 policy unchanged
- promotion screen: zero of 27 pair/timeframe/buffer points survive the 0.2-pip development-and-validation gate
- clearest chronology failure: USDJPY 5m / 2-pip buffer is +1.9167% development with +$5.6874 expectancy/trade and PF 1.0282, then -15.4056% validation with -$64.1899 expectancy/trade and PF 0.6706
- two USDJPY 1h validation-only qualifiers fail development; no 0.5/1.0-pip result may rescue a failed baseline point
- no session sweep-rejection candidate is promoted and no post-result parameter expansion or rescue rule is authorized


Phase 4 is formally PASS under DEC-028. All six planned baseline families have complete benchmark evidence and experiment-log entries. Two serious research candidates remain frozen unchanged: the EXP-001 USDJPY 15m / 5-pip / 1.5x session-breakout point and the EXP-005 USDJPY 1h / 2.0x / fixed-1.0R volatility-breakout point. EXP-002, EXP-003, EXP-004, and EXP-006 remain FAIL / REJECT. Detailed acceptance evidence is `docs/phase4-acceptance-evidence.md`. The final-test period remains locked. Phase 4 checkpoint: `fmp-v1-phase4-baselines` at `115bb8080e951db16ca1a1174227ffa181a03d1b`; post-merge tests `34903338560` SUCCESS and Phase 3 acceptance `34903338538` SUCCESS.


## Phase 5 — PASS

DEC-029 freezes the leakage-safe `fmp-feature-v1` protocol; DEC-030 records the Phase 5 acceptance review.

- implementation merge: `74dce1b945ad31a05416a4fc9e63443a884cb90c`
- merged-main tests: run `34910118880` — SUCCESS
- unchanged Phase 3 acceptance: run `34910118886` — SUCCESS
- authoritative feature generation: run `34910227756` — SUCCESS
- matrix: 3 pairs × 3 timeframes = 9/9 cells successful
- independent evidence audit: 9/9 ZIP digests and 972/972 monthly Parquet partitions verified with zero validation errors
- total accepted feature rows: 4,023,279
- source coverage: 2015-01-01 through 2023-12-31 only
- feature schema: `fmp-feature-v1`, 55 columns = 7 identity + 48 feature values
- Final-test touched: NO
- Phase 5 closure merge: `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`
- post-merge tests: run `34912677109` — SUCCESS, 510 tests PASS, workflow YAML PASS, compile PASS
- post-merge Phase 3 acceptance: run `34912677100` — SUCCESS
- checkpoint: `fmp-v1-phase5-features` at `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`

Phase 5 is formally PASS under DEC-030. Checkpoint `fmp-v1-phase5-features` is frozen at the verified acceptance-closure commit `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`; post-merge tests `34912677109` and Phase 3 acceptance `34912677100` completed SUCCESS. Normal Phase 5 tooling still rejects any processed source request reaching 2024-01-01 or later before that partition is opened. The final-test period remains locked.

## Phase 6 — PASS

DEC-031 remains the frozen statistical / ML filter protocol for `EXP-20260915-007`. DEC-032 records the completed experiment outcome and Phase 6 acceptance without changing the protocol, strategy parameters, features, models, thresholds, gates, or Phase 3 execution/risk semantics.

- Candidate A: USDJPY 15m session breakout, 5-pip buffer, 1.5x target range — rule baseline retained unchanged.
- Candidate B: USDJPY 1h volatility breakout, 2.0x range expansion, fixed 1.0R target — rule baseline retained unchanged.
- feature checkpoint: `fmp-v1-phase5-features` at `e0b2fc7bf12b0c9d76668564df6b7714b1fe0`
- feature schema: `fmp-feature-v1`, exact 48 feature values plus signal direction for modeling
- accepted USDJPY processed-manifest SHA-256: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`
- experiment: `EXP-20260915-007` — PASS / ML overlay REJECT
- authoritative run: `34966406652` on `2dccb0f00d2a443bc41646ac1b3b494d81e1f13c` — SUCCESS
- session-breakout evidence: artifact `10395810196`, ZIP SHA-256 `36cb9f80ca043da23250669dd974036eb9fb985c3f7f9ffd7844b9d99c96073d`; `ALL_NULL_FIT_COLUMN` on `minutes_since_new_york_open`; both models fail closed; all six variants not evaluated; `NO_ML_CHALLENGER`; validation unopened
- volatility-breakout evidence: artifact `10395670751`, ZIP SHA-256 `0cf71a4d725fb1e609a512bb95aa13e4ad8771ae2b5864dd09e2833fe160a8d2`; both models fit exactly once; all six variants fail the selection gate; `NO_ML_CHALLENGER`; validation unopened
- fit: 2015-01-01 through 2018-12-31 inclusive
- selection: 2019-01-01 through 2020-12-31 inclusive
- external validation: 2021-01-01 through 2023-12-31 inclusive; not opened because neither strategy produced a qualifying selection-period challenger
- no refit after selection; no post-result threshold widening or model/strategy retuning
- Final-test touched: NO
- checkpoint: `fmp-v1-phase6-models` — CREATED at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`
- closure merge: `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`
- post-merge tests run: `34972534430` — SUCCESS, 573/573 tests PASS, workflow YAML PASS, compile PASS
- post-merge Phase 3 acceptance run: `34972534435` — SUCCESS

Phase 6 is formally PASS under DEC-032 because both frozen strategies completed the predeclared deterministic leakage-safe experiment and all negative evidence was preserved. No ML filter is promoted. Normal Phase 6 tooling still cannot open any required source or feature partition reaching 2024-01-01 or later. The final-test period remains locked; DEC-008 remains unchanged.

## Phase 7 — ACTIVE

DEC-033 freezes the approved Phase 7 protocol for `EXP-20260915-008`; DEC-034 records the audited Stage 1 final-gate outcome without changing any frozen protocol rule.

- frozen candidates: USDJPY 15m session breakout, 5-pip buffer, 1.5x target range; USDJPY 1h volatility breakout, 2.0x range expansion, fixed 1.0R target
- ML overlay: none; Phase 6 rejected all ML challengers
- implementation / Stage 1 code SHA: `e33270de1f89757d1bf2a0d12ef40b2dc36bc110`
- pre-dispatch merged-main tests: run `35010868101` — SUCCESS, 620/620 tests PASS, workflow YAML PASS, compile PASS
- pre-dispatch unchanged Phase 3 acceptance: run `35010868091` — SUCCESS
- authoritative Stage 1 workflow: `phase7-final-gate`, run `35013047267` — SUCCESS
- Stage 1 scored range: 2024-01-01 through 2024-12-31 inclusive
- Stage 1 warm-up: 2023-12-25 through 2023-12-31 context only and never scored
- Final-test touched: YES — Stage 1 2024 only
- Stage 2 forward horizon: 2025-01-01 through 2026-08-20 inclusive, partitioned into the seven frozen quarterly/partial-quarter windows; required 2025/2026 partitions have not yet been opened
- Stage 2 survivor: `session_breakout`
- Stage 2 rejected candidate: `volatility_breakout`
- `session_breakout` Stage 1 evidence: artifact `10414407590`, ZIP SHA-256 `d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb`, inner `manifest.json` SHA-256 `a8ca80186708aedbfd52fd688c843c4dc06e2ce8a81f543bd7224abc0a955faa`, outcome `STAGE1_PASS`
- `volatility_breakout` Stage 1 evidence: artifact `10414905151`, ZIP SHA-256 `5ee8b6b96382741f454d2b72a6ae6de04e85c9eca04c17ac846c0d594fd27d24`, inner `manifest.json` SHA-256 `a2526d90312e85a2ab2d57ab86d5502e8644a16735aa0a677cda5626976dda35`, outcome `STAGE1_REJECT`
- Stage 2 authorization: only the exact `session_breakout` package from artifact `10414407590` / ZIP `d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb` may authorize Stage 2, and the Stage 2 workflow must verify it before any required 2025/2026 source I/O
- accepted Phase 2 USDJPY artifact: `10327600628`, ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`
- accepted USDJPY processed-manifest SHA-256: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`
- Phase 6 checkpoint: `fmp-v1-phase6-models` at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`
- experiment: `EXP-20260915-008` — RUNNING

The independently audited Stage 1 metrics and constituent digests are recorded in `docs/phase7-stage1-evidence.md`. `session_breakout` passed every frozen 0.2/0.5-pip Stage 1 gate and has 122 baseline trades; `volatility_breakout` failed mandatory profitability/expectancy/profit-factor gates and is not eligible for Stage 2. No retuning, rescue search, or candidate replacement is authorized.

Existing Phase 4, Phase 5, and Phase 6 guards remain unchanged and continue failing before 2024+ source or feature I/O. Phase 7 may now open only the frozen Stage 2 windows for the exact authorized `session_breakout` identity after verifying the Stage 1 evidence package. No 2025/2026 Stage 2 partition has been opened at this state checkpoint.

Phase 8 remains UNSTARTED. Broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged.
