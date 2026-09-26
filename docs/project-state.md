# FMP Project State

**Updated:** 2026-09-26
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 8A — Multi-pair, multi-strategy portfolio research
**Phase status:** ACTIVE — EXP-044 V1 CLOSED; direct market-learning track closed by DEC-262; EXP-015 Stage A now has DEC-264 first-run governance, DEC-265 one-way operator, and DEC-266 repository-hosted read-only proof source; the single authoritative slot remains unconsumed pending merged-main proof; Stage B/C, DEC-042 portfolio selection, and DEC-045 Phase 8A acceptance remain blocked
**Next milestone:** Merge DEC-266 and require its push-to-main proof workflow to succeed with an exact non-expired MISSING-state plan artifact. Only then may a separately reviewed one-shot Stage A executor source be considered. Phase 8B and all demo/live/broker/real-money paths remain locked.

## Current baseline

- Instruments: EUR/USD, GBP/USD, USD/JPY
- Canonical history: 1-minute bid/ask
- Derived bars: 5m, 15m, 1h
- Frozen Phase 1 snapshot: 2015-01-01 through 2026-08-20 inclusive
- Frozen raw identities: 25,500
- Historical source: Dukascopy daily M1 BID/ASK `.bi5`
- Persistent immutable raw snapshot: Supabase private bucket `fmp-raw`
- Frozen Phase 1 plan SHA-256: `2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6`
- Phase 7 checkpoint: `fmp-v1-phase7-walk-forward` at `b6fb0176555b071fef6d1070edf3407b03cd60c9`
- Demo trading: locked
- Live order placement / broker mutation: locked
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
- feature checkpoint: `fmp-v1-phase5-features` at `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`
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

## Phase 7 — PASS

DEC-033 freezes the approved Phase 7 protocol for `EXP-20260915-008`; DEC-034 records the audited Stage 1 final-gate outcome; DEC-035 records the audited Stage 2 outcome and Phase 7 acceptance without changing any frozen protocol rule.

- frozen candidates: USDJPY 15m session breakout, 5-pip buffer, 1.5x target range; USDJPY 1h volatility breakout, 2.0x range expansion, fixed 1.0R target
- ML overlay: none; Phase 6 rejected all ML challengers
- implementation / Stage 1 code SHA: `e33270de1f89757d1bf2a0d12ef40b2dc36bc110`
- Stage 2 code SHA: `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d`
- pre-dispatch merged-main tests: run `35010868101` — SUCCESS, 620/620 tests PASS, workflow YAML PASS, compile PASS
- pre-dispatch unchanged Phase 3 acceptance: run `35010868091` — SUCCESS
- authoritative Stage 1 workflow: `phase7-final-gate`, run `35013047267` — SUCCESS
- Stage 1 scored range: 2024-01-01 through 2024-12-31 inclusive
- Stage 1 warm-up: 2023-12-25 through 2023-12-31 context only and never scored
- authoritative Stage 2 workflow: `phase7-walk-forward`, run `35015277625` — SUCCESS
- Stage 2 scored range: seven frozen independent windows covering 2025-01-01 through 2026-08-20 inclusive
- Final-test touched: YES — Stage 1 2024 and Stage 2 2025-2026
- Stage 2 survivor: `session_breakout` — PASS
- Stage 2 rejected candidate: `volatility_breakout` — not evaluated in Stage 2 because it was rejected at Stage 1
- `session_breakout` Stage 1 evidence: artifact `10414407590`, ZIP SHA-256 `d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb`, inner `manifest.json` SHA-256 `a8ca80186708aedbfd52fd688c843c4dc06e2ce8a81f543bd7224abc0a955faa`, outcome `STAGE1_PASS`
- `volatility_breakout` Stage 1 evidence: artifact `10414905151`, ZIP SHA-256 `5ee8b6b96382741f454d2b72a6ae6de04e85c9eca04c17ac846c0d594fd27d24`, inner `manifest.json` SHA-256 `a2526d90312e85a2ab2d57ab86d5502e8644a16735aa0a677cda5626976dda35`, outcome `STAGE1_REJECT`
- Stage 2 evidence: artifact `10414817824`, ZIP SHA-256 `2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4`; `result.json` SHA-256 `ce7ef3f732bf2da7cd9c0df5e5d695dcdadd63e309c9428a6f572801fcb197b7`; `windows.json` SHA-256 `66a1d35b12b68a0762dd98cd6838a2befcaf57ef9ae43bce181241fe4d23a4f0`
- 0.2-pip Stage 2 aggregate: +0.757266% net return, +$3.8054 expectancy/trade, PF 1.062731, 199 trades, 1.140640% max independent-window drawdown, 5 of 7 positive windows, 35.061843% max positive-window share
- 0.5-pip Stage 2 aggregate: +0.262176% net return, +$1.3175 expectancy/trade, PF 1.021310, 199 trades, 1.170046% max independent-window drawdown
- 1.0-pip diagnostic: -0.562118% net return, -$2.8247 expectancy/trade, PF 0.955760, 1.219045% max independent-window drawdown; preserved as non-gating cost-sensitivity evidence
- Stage 2 outcome: `PHASE7_PROMOTE_TO_SHADOW_DESIGN`
- accepted Phase 2 USDJPY artifact: `10327600628`, ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`
- accepted USDJPY processed-manifest SHA-256: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`
- Phase 6 checkpoint: `fmp-v1-phase6-models` at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`
- experiment: `EXP-20260915-008` — PASS / PROMOTE

The independently audited Stage 1 evidence is recorded in `docs/phase7-stage1-evidence.md`; complete Stage 2 acceptance evidence is recorded in `docs/phase7-walk-forward-evidence.md`. `session_breakout` passed every frozen Stage 1 and Stage 2 mandatory gate. The negative 1.0-pip diagnostic remains evidence and does not alter the predeclared decision because DEC-033 defines it as diagnostic only. `volatility_breakout` remains rejected at Stage 1. No retuning, rescue search, alternate candidate, new pair/timeframe, ML overlay, or post-result threshold change is authorized.

Phase 7 is formally PASS and checkpoint `fmp-v1-phase7-walk-forward` is frozen at `b6fb0176555b071fef6d1070edf3407b03cd60c9`. DEC-036 separately activates Phase 8 shadow-only implementation for the unchanged surviving `session_breakout` rule. Broker mutation, demo order placement, production/live order placement, and real-money trading remain locked; DEC-008 remains unchanged.


## Phase 8 — ACTIVE AS AMENDED PHASE 8A / 8B

DEC-039 changes Phase 8 from a single-strategy live-shadow campaign into two ordered subphases because the sole Phase 7 survivor is robust enough to have passed its historical gates but is not economically attractive enough for the operator's revised objective.

DEC-036, DEC-037, and DEC-038 remain preserved as the historical single-strategy shadow/connector/liveness contracts where they are not superseded by DEC-039. Their EXP-011 USDJPY-only campaign launch path is superseded; the read-only, no-broker-mutation and fail-closed safety lessons carry forward into Phase 8B.

### Phase 8A — Multi-pair, multi-strategy portfolio research — ACTIVE

Approved design: `docs/superpowers/specs/2026-09-22-phase8a-portfolio-research-redesign.md`

Umbrella experiment: `EXP-20260922-012`

Active research tracks: `EXP-20260922-015` / DEC-043 (frozen rule-based challenger benchmark) and `EXP-20260923-044` / DEC-073 (direct market learning)

Core scope:

- research universe: exactly EURUSD, GBPUSD, and USDJPY
- historical source: reuse the accepted Dukascopy Phase 1/2 canonical 1m BID/ASK histories and deterministic 5m/15m/1h bars for all three pairs
- strategy architecture: many immutable versioned strategy instances rather than one permanently selected strategy
- DEC-073 learning architecture: study future market behaviour directly from leakage-safe feature rows across all three pairs/timeframes, while retaining hand-written strategies as transparent benchmarks rather than the sole source of candidate trades
- active model/champion identities remain immutable; new shadow/demo observations may train offline challengers later, but no running model may update itself in place or hot-swap into an active campaign
- initial family universe: session breakout, trend continuation, mean reversion, previous-day high/low rejection, rolling volatility breakout, and session high/low sweep/rejection; any new family or material parameter-region expansion requires a new predeclared experiment
- lifecycle: `DISCOVERY -> CHALLENGER -> HISTORICAL_QUALIFIED -> SHADOW_CANDIDATE -> SHADOW_VALIDATED -> DEMO_ELIGIBLE`, with `RETIRED` preserved as durable evidence
- active champion sets are immutable during registered campaigns; continuous learning may create challengers but may not hot-swap production/shadow strategy code
- portfolio routing must evaluate eligible strategies across all three pairs and then apply conflict/correlated-exposure checks before the independent risk engine
- existing Phase 3 risk defaults remain authoritative unless explicitly amended: 0.25% requested risk/trade, 0.50% hard maximum, 1.00% maximum simultaneous open risk, 1.50% UTC day-start realized-loss halt
- operator economic objective: materially higher returns than the Phase 7 single-strategy result; possible +10% days are an aspiration to measure, not a guaranteed or mandatory daily pass gate
- mandatory reporting includes daily return distribution, frequency of >=10% days, monthly/annualized return, expectancy, profit factor, drawdown, losing streaks, tail/concentration diagnostics, trade count, cost sensitivity, and pair/strategy/timeframe/session/regime contributions
- return improvement may not be manufactured through martingale, loss chasing, silent leverage multiplication, or post-result parameter rescue

Historical-data status:

- Phase 7 already opened the former 2024-01-01 through 2026-08-20 final-test period
- new post-Phase-7 strategies may use that history for retrospective discovery, diagnostics, and walk-forward robustness
- they may **not** call it an untouched final test
- genuinely new forward evidence begins only after a challenger version/protocol is frozen and later enters Phase 8B prospective shadow observation

Implementation progress:

- PR #121 merged at `e9e7bd7dfa31b8a566cc299e8988856e21071d13`: deterministic strategy registry/lifecycle, immutable champion sets, multi-pair router, USD-direction exposure summaries, historical-inventory identity, explicit retrospective loader/evaluator, and DEC-039 documentation.
- PR #122 merged at `63389442ab65cdd0e610fa76f6c93a47d23cc01f`: retrospective batch orchestration, deterministic artifacts, CLI, and manual 3-pair × 3-timeframe workflow over accepted Phase 2 artifacts.
- PR #122 verified 819 tests PASS and unchanged Phase 3 acceptance PASS before merge.
- DEC-040 is the active joint-account portfolio simulation protocol.
- PR #123 merged at `b27ff8cb1e89471686b2bfe1107cd54d5e9101d9`: time-local conflict routing, explicit declared-earliest execution timing, canonical 1m execution-data role, and shared-account joint portfolio simulation.
- PR #123 pre-merge verification: 828 tests PASS, compile PASS, unchanged Phase 3 acceptance PASS.
- PR #124 merged at `b8c54cf4530e93827270d10a0fb5c1248a14716b`: exact-fingerprint joint evidence envelopes, deterministic artifact serialization, and explicit manual `resolve`/`run` CLI with hard non-promotion boundaries.
- PR #124 pre-merge verification: 835 tests PASS, compile PASS, unchanged Phase 3 acceptance PASS.
- DEC-041 / EXP-20260922-013 is the original predeclared Challenger Round 1: `opening_range_momentum` across all three V1 pairs and 5m/15m/1h.
- PR #125 merged the EXP-013 signal/catalog/Stage A runner implementation to `main` before any benchmark dispatch. PR #128 then merged the missing frozen Stage A workflow/evidence layer at `c086936a650e74d48f71c1b5e9a133acbe29d957` after 868 tests PASS and unchanged Phase 3 acceptance PASS. PR #129 merged the source-digest hardening plus guarded Stage B confirmation path at `204187fa0eb56908d705bbde76e7423894015dae` after 875 tests PASS and unchanged Phase 3 acceptance PASS. No EXP-013 Stage A or Stage B historical workflow has been dispatched.
- DEC-042 / EXP-20260922-014 is the frozen portfolio-selection protocol. PR #133 merged the guarded execution layer to `main` at `a10bf42b75b48c300ac48edaa6616a4af6fa2e9c` after 910 tests PASS, compile PASS, and unchanged Phase 3 acceptance PASS. It reconstructs the exact eligible pool from the Phase 7 baseline plus EXP-015 final shortlist, freezes every 1–6-strategy set before source download, evaluates only that immutable universe, preserves non-promotion boundaries, and returns either the exact selected set or `NO_PORTFOLIO_SELECTED`. The actual combination search remains BLOCKED because no EXP-015 historical stages have been dispatched.
- DEC-043 / EXP-20260922-015 predeclares a broader 567-configuration six-family challenger search. PR #130 merged the frozen validator-region + 567-identity catalog slice to `main` at `7e3eac44a14815ab65b1f85af9e2469517ed3efb` after 880 tests PASS and unchanged Phase 3 acceptance PASS. DEC-044 corrected the pre-run Stage A arithmetic: 54 exact ranking cells × at most 2 survivors = maximum 108 Stage A survivors. PR #131 merged the frozen Stage A preflight catalog, 567-candidate evaluator, family-cell ranking, nine-cell authorization, CLI, and manual workflow to `main` at `bde29280d08cf347265ea06f186972a61f2561f4` after 891 tests PASS, compile PASS, and unchanged Phase 3 acceptance PASS. PR #132 merged guarded Stage B/C execution, exact upstream evidence validation, final deterministic 0–11 shortlist, and explicit lifecycle dispositions for all 567 identities to `main` at `3d36368811e155d41d45b73313827bca83a66518` after 898 tests PASS, compile PASS, and unchanged Phase 3 acceptance PASS. No EXP-015 historical stage has been opened.
- Identity audit: the later selection work temporarily duplicated DEC-041/EXP-013 identifiers; the correction branch renumbers selection to DEC-042/EXP-014 and broad discovery to DEC-043/EXP-015. No benchmark/search result was produced under the duplicate identities.

Current milestone:

1. Existing Phase 8A portfolio and Phase 8B safety/source infrastructure through DEC-072 is merged and verified; DEC-073 adds the source-only direct market-learning foundation without producing a training result;
2. no real DEC-052 prospective segment, DEC-051 acceptance result, SHADOW_VALIDATED transition, Phase 9 artifact chain, demo order, or broker mutation has been executed;
3. PR #164 merged DEC-072 / `EXP-20260923-043` to `main` at `2732e00fa502219bf18de35ae861e72befe62661`; the exact final PR head `5efc050f31811e0f179638fc2c9bb83587eb22ef` passed 1092 tests plus YAML/compile in run `35803436296` and unchanged Phase 3 acceptance run `35803436276` passed; post-merge `main` runs `35803529547` and `35803529528` passed;
4. DEC-072 fixes crash-before-first-close observability, adds deterministic closed/unclosed segment inventory and terminal context, validates progress fingerprints/count parity, and rejects renamed/copied closed directories whose path identity no longer matches the immutable segment ID; interrupted directories still never enter aggregate or acceptance evidence;
5. source-side Phase 8B preparation, readiness, progress, and interrupted-capture observability are complete, but real prospective capture remains locked behind the Phase 8A acceptance chain; Phase 9 execution, broker mutation, live trading, real-money trading, Phase 10 decision, and Phase 11 remain locked.
6. DEC-073 re-centers the active research path on learning market behaviour from the accepted Dukascopy history. PR #166 merged the exact 60m/240m direct-outcome-label foundation; PR #167 merged the separate `fmp-market-feature-v1` full-history materialization source while preserving the historical Phase 5 lock.
7. PR #169 merged the EXP-044 nine-cell aggregate evidence validator to `main` at `f8e3b160c45dc346d22ad3aa8f5ac1a54df26174`. Exact final PR head `42875569e8d48862be20453b4963c57335904e45` passed 1111 tests plus workflow-YAML validation and compile in run `35840325472`; unchanged Phase 3 acceptance run `35840325448` passed. The validator binds every cell to the existing accepted Phase 2 Dukascopy manifest SHA-256, exact 140 monthly artifact paths, and actual artifact bytes while keeping `model_fit_authorized=false`.
8. PR #171 merged the vectorized `fmp-market-outcome-grid-v1` source to `main` at `4dfd9b4cc5d62d2585b027946a3056415fcd3ab7`. Exact final PR head `cd6805af35865e589ad606ecd7065f1060ca474a` passed 1117 tests plus workflow-YAML validation and compile in run `35845107487`; unchanged Phase 3 acceptance run `35845107495` passed.
9. PR #172 merged persisted feature-evidence revalidation and the file-based outcome materializer to `main` at `428541b310ccc806662818d2141bfe356df023d1`. Exact final PR head `be55f852713c1544063b0590cd36207cd1417277` passed 1122 tests plus workflow-YAML validation and compile in run `35845611187`; unchanged Phase 3 acceptance run `35845611278` passed.
10. Source now includes a separate manual outcome workflow that accepts only a successful `phase8a-exp044-market-features` run from `main`, revalidates its aggregate feature evidence, reuses the accepted Phase 2 Dukascopy artifacts, materializes all nine outcome cells, and emits one aggregate outcome-evidence fingerprint. This workflow has not been dispatched; no EXP-044 model fit is authorized.
11. PR #173 merged that evidence-gated outcome workflow to `main` at `fc05230462d8743ba5780d3bd2633649e4019b00`. Exact PR head `e29437e2ab93462b1a669797e973b7b18dfacd33` passed 1129 tests plus workflow-YAML validation and compile in run `35846186938`; unchanged Phase 3 acceptance run `35846186891` passed. Post-merge main runs `35846386839` and `35846386975` also passed.
12. DEC-074 adds a source-only data-preparation readiness gate: persisted feature and outcome evidence must revalidate and cross-bind exact evidence fingerprints, cell manifests, Phase 2 Dukascopy identities, and feature row counts before model-protocol source work may open. Readiness never authorizes fitting or promotion.


13. Authoritative EXP-044 data preparation is now complete: feature run `35867307338` and replacement outcome run `35876715434` are verified; aggregate outcome evidence artifact `10758027876` and readiness artifact `10757578276` revalidate; DEC-075 reports `MODEL_PROTOCOL_SOURCE_OPEN`.
14. DEC-088 freezes the first direct-market model-training protocol source across exactly 18 pair/timeframe/horizon cells. It creates no result authorization: model fitting, promotion, shadow/demo activity, broker mutation, live orders, and real-money trading remain locked.
15. DEC-089 binds the exact merged DEC-088 protocol fingerprint to the verified DEC-074 evidence chain and exposes only `model_run_source_open_authorized=true`. The resulting `MODEL_PROTOCOL_FROZEN` stage is non-dispatchable and still authorizes no model fit.
16. DEC-090 implements the deterministic in-memory two-family training/selection/validation/retrospective-holdout core with synthetic-only tests. No authoritative artifact loader, model-training workflow, CLI, or dispatch path exists; `MODEL_TRAINING_RESULT_EXECUTION_AUTHORIZED=false`.
17. DEC-091 freezes the exact persisted feature/outcome artifact inventory, revalidates readiness and every manifest-listed parquet partition, and predeclares deterministic 18-cell result evidence. `AUTHORITATIVE_MODEL_RESULT_EXECUTION_AUTHORIZED=false`, so no historical fit can execute.
18. DEC-092 freezes a manual main-only no-input model-training workflow, fail-closed CLI, and operator stage `MODEL_RUN_WORKFLOW_SOURCE_FROZEN`. Dispatch/result/fit authorization remains false, so the workflow cannot progress beyond authorization preflight.
19. DEC-093 authorizes exactly one guarded historical model-result run, adds a workflow-internal prior-run rejection guard, pins the numerical runtime, and freezes post-run aggregate evidence validation. No model run has been dispatched by this decision; promotion and all trading permissions remain false.
20. DEC-094 reviews the executed run `35891605645` as terminal failure: five pair/timeframe computations completed but their hidden `.results` evidence was not persisted; four pair/timeframe jobs hard-failed because frozen logistic regression did not converge within `max_iter=2000`; aggregate evidence was skipped and zero artifacts persisted. The upload defect is repaired source-only, EXP-044 V1 execution is closed, and no rerun/replacement or parameter rescue is authorized.
21. DEC-095 opens `EXP-20260923-045` as a post-result-informed retrospective successor. It keeps DEC-088 model configurations unchanged, predeclares logistic non-convergence as an ineligible family-level outcome, freezes evidence-persistence requirements, and keeps every result/fit/promotion/trading authorization false.
22. DEC-096 implements the deterministic EXP-045 in-memory training/evaluation core, binds the exact DEC-090 base-core and DEC-095 protocol blobs, implements predeclared family-level logistic non-convergence handling, and keeps historical result execution and all promotion/trading authorization false.
23. DEC-097 freezes the EXP-045 artifact-backed source and aggregate evidence contract, reuses the exact DEC-091 historical data loader under a blob binding, requires all 18 successor cells and deterministic fingerprints, and keeps authoritative model-result execution and all promotion/trading authorization false.
24. DEC-098 freezes a manual main-only EXP-045 workflow, fail-closed CLI, pinned runtime, and exact-source execution gate. Dispatch/result/fit authorization remains false, so no EXP-045 historical result can be produced.
25. DEC-099 binds merged DEC-098, confirms zero prior manual-main EXP-045 model runs, hardens the workflow with a first-run guard, and authorizes at most one historical result-producing run after merge. No run is dispatched by this decision; promotion and all trading permissions remain false.
26. DEC-100 predeclares the terminal review for that one run before any result exists. Success requires the exact complete job/artifact inventory plus DEC-097 aggregate-evidence validation; non-success preserves only valid partial cell evidence, forbids aggregate claims, and authorizes no replacement run.
27. DEC-101 freezes a clean-main, double-plan single-step operator for the DEC-099-authorized run. It exposes exactly one dispatch command only while no EXP-045 run exists, routes terminal state through DEC-100, and adds no retry or alternate trigger.
28. DEC-102 reviews the single EXP-045 run `35911916239` as successful execution with complete 18-cell aggregate evidence but no accepted challenger. Seventeen cells had no challenger; GBPUSD 5m / 240m was selected and rejected at validation. The run slot is consumed and all result/fit/promotion/shadow/demo/broker/live/real-money/trading authorizations are closed.
29. DEC-103 freezes detailed post-result diagnostics before any successor protocol: 90 variants evaluated, one complete selection-gate pass, 25 low-count positive variants not validation-tested, and the sole selected challenger collapsing from 460 selection candidates to 83 validation candidates with negative validation net performance. Only successor-protocol source work is opened; no execution.
30. DEC-104 opens `EXP-20260923-046` as a post-result-informed temporal-stability successor protocol. It preserves the full EXP-045 model/data/gate identity and adds only a four-half-year selection stability screen with a 10% per-window candidate-share floor and positive financial signs in every window. No fit or result execution is authorized.
31. DEC-105 implements the source-only EXP-046 deterministic training/evaluation core. It reuses the predecessor fit/scoring mechanics, evaluates temporal stability only after the unchanged aggregate gate, slices one fixed selection probability matrix across the four half-year windows, and keeps all authoritative fit/result/promotion/trading authorizations false.
32. DEC-106 freezes the source-only EXP-046 artifact-backed runner and aggregate evidence contract. It reuses the exact verified historical feature/outcome/readiness artifacts, validates all 18 temporal-stability cell results and canonical fingerprints, and remains non-executable before artifact loading.
33. DEC-107 freezes the manual main-only input-free EXP-046 workflow, fail-closed CLI, pinned runtime, and exact-source execution gate. The source can preserve all nine pair/timeframe artifacts plus aggregate evidence, but run/result/fit authorization remains false and the preflight cannot pass.
34. DEC-108 predeclares terminal review before any EXP-046 authorization or result. It accepts only attempt-1 exact workflow/job/artifact identities, validates successful aggregate evidence through DEC-106, preserves valid partial evidence on non-success, rejects reruns, and authorizes no replacement/promotion/trading.
35. DEC-109 verifies zero prior manual-main EXP-046 runs, hardens the workflow with a first-run rejection guard, and opens at most one outer historical result-producing authorization after merge. The first attempt consumes the slot; no run is dispatched by DEC-109 and all promotion/trading permissions remain false.
36. DEC-110 freezes a clean-main, double-plan one-way operator for the DEC-109-authorized EXP-046 run. Only the zero-run state is dispatchable; active/terminal states cannot expose a second dispatch, and terminal evidence routes through DEC-108.
37. DEC-111 reviews the single EXP-046 run `35978474425` as successful execution with complete 18-cell aggregate evidence but no stable challenger. Two variants passed the predecessor aggregate gate and both failed the DEC-104 temporal-stability screen; validation and holdout stayed locked. The run slot is consumed and all result/fit/promotion/shadow/demo/broker/live/real-money/trading authorizations are closed.
38. DEC-112 freezes a cross-run reproducibility audit of EXP-045 versus EXP-046. HGB model fingerprints and all 54 thresholded candidate sets reproduce materially; logistic family availability changes in five cells and one intermediate aggregate-gate outcome changes. Logistic result-producing reuse is closed pending a separately frozen successor protocol/remedy.
39. DEC-113 opens `EXP-20260924-047` as a source-only HGB candidate-density successor. Logistic is excluded; all predecessor data/model/gate mechanics remain frozen except confidence-to-density mapping. Selection-derived budget anchors 250/500/1000 generate numeric cutoffs that must be applied unchanged to validation/holdout. No fit/result execution is authorized.
40. DEC-114 implements the source-only deterministic EXP-047 HGB density training/evaluation core. It fits HGB once, scores selection once, derives deterministic 250/500/1000 cutoffs with row-id tie ordering, preserves the unchanged aggregate/stability gates, and reuses the exact selection cutoff forward. No authoritative fit/result execution is authorized.
41. DEC-115 freezes the source-only EXP-047 artifact-backed runner and aggregate evidence contract. It reuses the exact verified historical feature/outcome/readiness artifacts, requires the exact three HGB budget variants per cell, keeps logistic excluded, validates all 18 cell/result fingerprints, and remains non-executable before artifact loading.
42. DEC-116 freezes the manual main-only input-free EXP-047 workflow, CLI, pinned runtime, and exact-source execution gate. The workflow can preserve nine pair/timeframe partial artifacts plus aggregate evidence, but dispatch/result/fit authorization remains false and the preflight cannot pass. Terminal review must be frozen separately before any authorization.
43. DEC-117 predeclares EXP-047 terminal review before any run authorization. Only attempt-1 exact workflow/job/artifact identities are accepted; successful aggregate evidence must revalidate through DEC-115, non-success may preserve partial cell artifacts, reruns are rejected, and no replacement/promotion/trading authorization is opened.
44. DEC-118 verifies zero prior manual-main EXP-047 runs, hardens the workflow with a first-run rejection guard, and opens at most one outer historical result-producing authorization after merge. The first attempt consumes the slot; no run is dispatched by DEC-118 and all promotion/trading permissions remain false.
45. DEC-119 freezes a clean-main, double-plan one-way operator for the DEC-118-authorized EXP-047 run. Only the zero-run state is dispatchable; active/terminal states cannot expose a second dispatch, and terminal evidence routes through DEC-117.
46. DEC-120 repairs the DEC-119 public `next` metadata projection before any EXP-047 run occurred. A stale `dec107_merged_commit` lookup is replaced by fail-closed validation of the actual DEC-113 through DEC-117 gate chain; the DEC-118 one-run slot remains unconsumed.
47. DEC-121 reviews the single EXP-047 run `35993400007` as successful execution with complete 18-cell aggregate evidence but no stable challenger. Twelve density-budget variants pass the aggregate gate and all 12 fail the frozen temporal-stability screen; validation and holdout stay locked. The run slot is consumed and all result/fit/promotion/shadow/demo/broker/live/real-money/trading authorizations are closed.
48. DEC-122 freezes the EXP-047 post-result temporal-concentration diagnostic. All 12 aggregate-passing density variants fail candidate-share stability, 10 also fail a financial window, and six produce zero candidates across both 2021 half-years. Only successor-protocol source work is opened; no stability relaxation or execution is authorized.
49. DEC-123 opens `EXP-20260924-048` as a source-only HGB fit-regime consensus successor. The 2015-2020 fit span is partitioned into three disjoint two-year HGB fits; only unanimous LONG/SHORT top-class agreement is eligible, with minimum agreed-direction probability as consensus confidence. Density/stability gates remain unchanged and no fit/result execution is authorized.
50. DEC-124 implements the deterministic source-only EXP-048 regime-consensus training core. Three HGB models fit the exact disjoint regime windows, unanimous directional consensus and minimum support define eligibility/confidence, and the unchanged density/stability/validation/holdout pipeline is reused without refit. No authoritative fit/result execution is authorized.
51. DEC-125 freezes the source-only EXP-048 artifact-backed runner/evidence contract. It reuses the exact accepted historical feature/outcome/readiness artifacts, validates all three regime fits and consensus/density/stability/forward evidence across all 18 cells, and remains non-executable before artifact loading.
52. DEC-126 freezes the source-only manual-main EXP-048 workflow, CLI, pinned Python 3.12.14 runtime, and exact-source execution gate. The workflow has no first-run guard yet and the preflight cannot pass because dispatch/result/fit authorization remains false; terminal review must be predeclared separately before authorization.
53. DEC-127 predeclares exact attempt-1 EXP-048 terminal review before any authorization. Success requires all 11 jobs, all nine cell artifacts, the aggregate artifact, and DEC-125 evidence revalidation; non-success may preserve partial cell evidence but opens no retry/replacement.
54. DEC-128 independently verifies zero prior manual-main EXP-048 runs, hardens the workflow with a first-run rejection guard, and opens at most one outer historical result-producing authorization after merge. The first attempt consumes the slot; no run is dispatched by DEC-128 and all promotion/trading permissions remain false.
55. DEC-129 freezes a clean-main, double-plan one-way operator for the DEC-128-authorized EXP-048 run. Only the zero-run state is dispatchable; active/terminal states cannot expose a second dispatch, gate metadata binds DEC-126/128 and the DEC-123-through-127 chain, and terminal evidence routes through DEC-127.
56. DEC-130 reviews the single EXP-048 run `36006524422` as successful execution with complete 18-cell aggregate evidence but no stable challenger. Seventeen regime-consensus density variants pass the aggregate gate and all 17 fail the frozen temporal-stability screen; validation and holdout stay locked. The run slot is consumed and all result/fit/promotion/shadow/demo/broker/live/real-money/trading authorizations are closed.
57. DEC-131 freezes the EXP-048 post-result diagnostic. All 17 aggregate-passing variants fail at least one financial stability window; 13 also fail candidate-share stability, while four fail financial stability only. No rerun, stability relaxation, or successor execution is authorized.
58. DEC-132 opens `EXP-20260924-049` as a source-only HGB regime-utility successor. It replaces class-probability fitting with paired LONG/SHORT 0.5-pip net-utility regressors inside each of the three frozen fit regimes, requires unanimous positive-utility direction, ranks by worst-regime predicted utility, and preserves the exact density, candidate-share, financial-stability, chronology, and forward-cutoff gates. No fit/result execution is authorized.
59. DEC-133 implements the deterministic source-only EXP-049 training/evaluation core. It fits exactly six HGB regressors per cell across the three frozen fit regimes, records deterministic fit/prediction identities, applies unanimous positive-utility consensus and worst-regime utility cutoffs, and reuses the unchanged aggregate/stability/validation/holdout gates. No authoritative historical fit/result execution is authorized.
60. DEC-134 freezes the source-only EXP-049 artifact-backed runner/evidence contract. It binds the accepted historical feature/outcome/readiness identities plus exact DEC-132/DEC-133 sources, requires complete 18-cell / 108-regressor evidence with recomputed utility, density, financial, stability, and forward-stage checks, and keeps the authoritative bundle locked before artifact loading. No historical fit/result execution is authorized.
61. DEC-135 freezes the source-only manual-main EXP-049 workflow, CLI, Python 3.12.14 runtime, and exact-source execution gate. The workflow is input-free and has no first-run guard yet; dispatch/result/fit authorization remains false, so preflight fails before readiness loading or fitting. Terminal review must be predeclared separately before any run authorization.
62. DEC-136 freezes the predeclared attempt-1 EXP-049 terminal-result review. Success requires the exact 11-job workflow shape, all nine cell artifacts, the aggregate artifact, and DEC-134 evidence revalidation; non-success may preserve partial cell evidence but cannot claim aggregate evidence, and no rerun/replacement is authorized.
63. DEC-137 independently verifies zero prior manual-main EXP-049 runs, hardens the workflow with a first-run rejection guard, and opens at most one outer historical result-producing authorization after merge. The first attempt consumes the slot; no run is dispatched by DEC-137 and all promotion/trading permissions remain false.
64. DEC-138 freezes the clean-main, double-plan one-way EXP-049 operator. Only the zero-run state can expose the DEC-137 dispatch; active/terminal states cannot expose a second run, exact terminal evidence routes through DEC-136, and no retry/replacement/promotion/trading authority is introduced.
65. DEC-139 reviews the single EXP-049 run `36029925264` as successful execution with complete 18-cell / 108-regressor aggregate evidence but no stable challenger. Eight regime-utility density variants pass the aggregate gate and all eight fail the frozen temporal-stability screen; validation and holdout stay locked. The run slot is consumed and all result/fit/promotion/shadow/demo/broker/live/real-money/trading authorizations are closed.
66. DEC-140 freezes the EXP-049 post-result diagnostic. Thirty-one of 54 budget variants are unavailable for insufficient utility-eligible rows; eight of 23 available variants pass the aggregate gate, all eight fail both candidate-share and financial temporal stability, all eight passes are 240m, and six fail financial signs in 2022 H2. Only successor-protocol source work is opened; no gate relaxation, rerun, fit, result execution, promotion, or trading authority is introduced.
67. DEC-141 opens EXP-050 as a source-only temporal-jackknife regime-utility successor. It preserves the exact EXP-049 cost-aware targets, HGB structure, unanimous positive utility, minimum-view score, density anchors, aggregate/stability gates, chronology, and forward-cutoff semantics, while replacing three narrow two-year fits with three four-year leave-one-regime-out views. No fit/result execution is authorized.
68. DEC-142 implements the deterministic source-only EXP-050 training/evaluation core. It exact-binds DEC-141 plus the DEC-133 predecessor training helper blob, constructs the three frozen jackknife view frames, fits six cost-aware HGB regressors per cell, and reuses the unchanged utility, cutoff, financial, stability, validation, and holdout semantics. Authoritative fit/result execution remains closed.
69. DEC-143 freezes the source-only EXP-050 artifact-backed runner/evidence contract. It exact-binds DEC-141/DEC-142 plus the accepted historical loader and DEC-134 helper blob, requires complete 18-cell / 108-regressor jackknife evidence with independently revalidated consensus, budget, financial, stability, status-chain, and fingerprint semantics, and keeps the authoritative bundle locked before artifact loading.
70. DEC-144 freezes the source-only manual-main EXP-050 workflow, CLI, Python 3.12.14 runtime, and exact-source execution gate. The workflow is input-free and has no first-run guard yet; dispatch/result/fit authorization remains false, so preflight fails before readiness loading or fitting. Terminal review must be predeclared separately before any run authorization.
71. DEC-145 predeclares the exact attempt-1 EXP-050 terminal review before any run authorization. Success requires exactly 11 completed jobs, all nine cell artifacts, the aggregate artifact, and DEC-143 evidence revalidation; non-success may preserve only valid partial cell evidence, cannot claim aggregate evidence, rejects reruns, and authorizes no replacement/promotion/trading.
72. DEC-146 independently verifies zero prior manual-main EXP-050 runs, hardens the workflow with a first-run rejection guard, and opens at most one outer historical result-producing authorization after merge. The first attempt consumes the slot on any terminal outcome; DEC-146 dispatches nothing and keeps replacement/promotion/trading authority closed.
73. DEC-147 freezes the clean-main, double-plan one-way EXP-050 operator. Only the zero-run state can expose the DEC-146 dispatch; active/terminal states cannot expose a second run, exact terminal evidence routes through DEC-145, and no retry/replacement/promotion/trading authority is introduced.
74. DEC-148 reviews the single EXP-050 run `36049824739` as successful execution with complete 18-cell / 108-regressor aggregate evidence but no stable challenger. Three USDJPY 5m / 60m variants pass the aggregate gate and all three fail the frozen temporal-stability screen; validation and holdout stay locked. The run slot is consumed and all result/fit/promotion/shadow/demo/broker/live/real-money/trading authorizations are closed.
75. DEC-149 freezes the EXP-050 post-result diagnostic. Twenty-six of 54 budget variants are unavailable; three of 28 available variants pass the aggregate gate and all three are concentrated in USDJPY 5m / 60m. All three have zero candidates in 2021 H1, two also have zero in 2021 H2, and none passes temporal stability. Utility-eligible selection coverage is descriptively higher than EXP-049, but only successor-protocol source work is opened; no gate relaxation, rerun, fit, result execution, promotion, or trading authority is introduced.
76. DEC-150 opens EXP-051 as a source-only out-of-fit calibrated-utility successor. It preserves EXP-050's six HGB regressors, jackknife views, unanimous positive-utility eligibility, budgets, financial gates, four stability windows, chronology, and no-refit semantics. Its sole research change calibrates each view/target prediction against that view's excluded fit-regime prediction distribution and ranks by the minimum calibrated percentile, with raw robust utility secondary. No fit, historical result execution, promotion, or trading authority is opened.
77. DEC-151 implements the deterministic source-only EXP-051 training/evaluation core. It preserves the six EXP-050 regressors and fit topology, freezes six excluded-regime calibration-reference vectors per cell, applies the right-empirical-CDF percentile score with minimum-view aggregation, uses a calibrated/raw cutoff pair for all selection and forward stages, and reuses the unchanged financial/stability pipeline. Authoritative artifact loading, result execution, promotion, and trading remain closed.
78. DEC-152 freezes the source-only EXP-051 artifact-backed runner/evidence contract. It exact-binds DEC-150/151 plus the accepted historical loader and generic financial/stability helper, validates all 18 cells, 108 regressors, 108 calibration references, calibrated/raw cutoffs, chronology/status chains, and canonical fingerprints, and rejects authoritative execution before readiness or artifact loading. No workflow, dispatch, fit/result execution, promotion, or trading authority is opened.
79. DEC-153 freezes the source-only manual-main EXP-051 workflow, CLI, Python 3.12.14 runtime, and exact-source execution gate. The workflow is input-free and main-only, preserves the nine accepted pair/timeframe cells and both horizons, has no first-run guard yet, and cannot pass preflight because dispatch/result/fit authorization remains false. Terminal review must be predeclared separately before any run authorization.
80. DEC-154 predeclares the exact attempt-1 EXP-051 terminal-result review before any run authorization. Success requires exactly 11 completed jobs, all nine cell artifacts, the aggregate artifact, and DEC-152 evidence revalidation including 108 regressors and 108 calibration references; non-success may preserve only valid partial cell evidence, cannot claim aggregate evidence, rejects reruns, and authorizes no replacement/promotion/trading.
81. DEC-155 independently verifies zero prior manual-main EXP-051 runs, hardens the workflow with a first-run rejection guard, and opens at most one outer historical result-producing authorization without dispatch. The first attempt consumes the slot on any terminal outcome and must route through DEC-154; no rerun/replacement, promotion, or trading authority is opened.
82. DEC-156 freezes the clean-main, double-plan, one-way EXP-051 operator. Only a zero-run MISSING state can expose the single frozen workflow-dispatch command; active or terminal state exposes no second dispatch, and terminal evidence routes through DEC-154 with DEC-152 aggregate revalidation on success. DEC-156 itself dispatches nothing.
83. DEC-157 freezes a read-only GitHub Actions runner for the exact DEC-156 `next` path. It runs only when its own workflow file is introduced/changed on main, validates the MISSING/RUN_DISPATCH_REQUIRED plan, persists the plan artifact, and contains no advance, execute, direct model-workflow dispatch, retry, replacement, promotion, or trading path.
84. DEC-158 preserves the failed DEC-157 read-only observation, identifies editable installation as the worktree mutation, removes `-e .`, imports from `src` via `PYTHONPATH`, and adds an explicit post-install clean-worktree check before DEC-156. No run slot is consumed and no dispatch authority changes.
85. DEC-159 preserves the second failed read-only run after DEC-158, identifies checkout-local `tee operator-plan.json` as the remaining preflight mutation, moves plan output/verification/upload to `RUNNER_TEMP`, and keeps the DEC-156 operator checkout untouched. No EXP-051 dispatch occurs.
86. DEC-160 freezes a one-shot repository-hosted executor after read-only plan run 36065565456 successfully proves the DEC-156 MISSING/RUN_DISPATCH_REQUIRED state and persists artifact 10835714803. The executor contains no independent model-dispatch path and may only invoke DEC-156 `advance --execute`; no retry/replacement, promotion, or trading path is opened.
87. Run `36066217609` completes successfully on attempt 1 at `3443b95ae3c524c74df4b2daebe9c526eb01ec9c`. DEC-161 reviews the complete 18-cell / 108-regressor / 108-calibration-reference evidence, records exactly one USDJPY 5m / 60m budget-250 aggregate pass with zero temporal-stability passes, records no stable challenger, and closes the consumed EXP-051 run slot.
88. DEC-162 compares immutable EXP-050/EXP-051 evidence: eligibility and budget availability are unchanged, calibrated ranking improves the USDJPY 5m / 60m top-250 result by +675.2 net pips but leaves 2021 H1/H2 with zero candidates, adds only three losing 2022 H1 candidates, and turns the 500/1000 aggregate passes into rejects. Stable passes remain zero; only successor protocol source design opens.
89. DEC-163 opens EXP-052 as a source-only fit-temporal-support successor. It preserves EXP-051 eligibility, six regressors, six pooled calibration references, budgets, gates, chronology, and no-refit semantics, while adding 24 out-of-fit fit-half-year support references per cell and ranking by minimum support percentile before pooled calibrated and raw utility. No fit or historical execution is opened.
90. DEC-164 implements the deterministic in-memory EXP-052 core. It preserves the six EXP-051 regressors and six pooled references, freezes 24 excluded-regime half-year support references per cell, ranks by minimum support percentile before pooled and raw utility, freezes a support/pooled/raw cutoff triple, and reuses the unchanged financial/stability/forward pipeline. Authoritative artifact loading, result execution, promotion, and trading remain closed.
91. DEC-165 freezes the non-executable EXP-052 artifact/evidence contract. It independently validates all 18 cells, 108 regressors, 108 pooled references, 432 fit-half-year support references, support/pooled/raw cutoff triples, unchanged financial/stability gates, forward chronology, and canonical fingerprints while rejecting before readiness/artifact loading. Historical execution, promotion, and trading remain closed.
92. DEC-166 freezes the manual-main, input-free EXP-052 workflow, public CLI, Python 3.12.14 pinned runtime, and exact-source execution gate. The workflow preserves the exact 9-dataset × 2-horizon evidence path but deliberately has no first-run guard yet; dispatch, historical result execution, protocol-result production, model fit, rerun/replacement, promotion, and trading remain false.
93. DEC-167 predeclares the exact attempt-1 EXP-052 terminal-result review before any run authorization. Success requires exactly 11 completed jobs, all nine cell artifacts, the aggregate artifact, and DEC-165 revalidation including 108 regressors, 108 pooled references, and 432 support references; non-success may preserve only partial cell evidence, cannot claim aggregate evidence, rejects reruns, and authorizes no replacement/promotion/trading.
94. DEC-168 independently verifies zero prior manual-main EXP-052 runs, hardens the workflow with a first-run rejection guard, and opens at most one outer historical result-producing authorization without dispatch. The first attempt consumes the slot on any terminal outcome and must route through DEC-167; no rerun/replacement, promotion, or trading authority is opened.
95. DEC-169 freezes the clean-main, double-plan, one-way EXP-052 operator. Only a zero-run MISSING state can expose the single frozen workflow-dispatch command; active or terminal state exposes no second dispatch, and terminal evidence routes through DEC-167 with DEC-165 aggregate revalidation on success. DEC-169 itself dispatches nothing.
96. DEC-170 freezes a repository-hosted read-only runner for the exact DEC-169 next plan, using non-editable dependencies and RUNNER_TEMP output so the operator's clean-worktree check remains valid. It contains no advance/execute or direct model-workflow dispatch path and changes no authorization.
97. DEC-170 automatic run `36114078121` succeeds on attempt 1 at `07afb1194442320f730e53b5c5d5825b053ee1a5` and persists plan artifact `10853944005`, proving the exact DEC-169 MISSING/RUN_DISPATCH_REQUIRED state. DEC-171 freezes a one-shot executor whose only execution path is DEC-169 advance --execute and which contains no direct model-workflow dispatch or retry path.
98. DEC-171 dispatches the sole EXP-052 attempt through DEC-169. Run `36114617377` completes successfully on attempt 1 at `d477555cf116f07fa195de1b4a4c0d2f3b2838c5`. DEC-172 reviews complete 18-cell / 108-regressor / 108-pooled-reference / 432-support-reference evidence, records one USDJPY 5m / 60m budget-250 aggregate pass with all 250 candidates concentrated in 2022 H2, records zero temporal-stability passes and no stable challenger, and closes the consumed EXP-052 run slot.
99. DEC-173 compares immutable EXP-050/051/052 results: eligibility and budget availability remain unchanged, all aggregate passes remain USDJPY 5m / 60m, EXP-052 top-250 quality is slightly below EXP-051, and its selection-window distribution regresses to `[0,0,0,250]`. Fit-period temporal support changes candidate identity but does not transfer into selection-period support; only successor source design may open.
100. DEC-174 opens source-only EXP-053, preserving the complete EXP-052 utility/eligibility/gate/chronology pipeline while adding 12 fit-only view-by-half-year feature-support references per cell. Ranking becomes feature-support first, then EXP-052 utility support, pooled calibrated utility, raw utility, and row identity; the budget-th row freezes a four-part cutoff reused forward. No EXP-053 fit/result execution is authorized.
101. DEC-175 implements the deterministic in-memory EXP-053 core with the same six regressors, six pooled references, 24 utility-support references, 12 feature-support references, a feature/utility-support/pooled/raw cutoff quadruple, and unchanged financial/stability/forward semantics. Historical artifact loading and authoritative execution remain closed.
102. DEC-176 freezes the non-executable EXP-053 artifact/evidence contract, requiring complete 18-cell / 108-regressor / 108-pooled-reference / 432-utility-support-reference / 216-feature-support-reference evidence, exact feature-reference identities, four-part cutoffs, forward chronology, and canonical fingerprints.
103. DEC-177 freezes the manual-main input-free workflow, public CLI, pinned Python 3.12.14 runtime, and exact-source execution gate while deliberately omitting a first-run guard and keeping dispatch/result/fit authorization false.
104. DEC-178 predeclares exact attempt-1 terminal review: success requires all 11 jobs, all nine cell artifacts, the aggregate artifact, and DEC-176 revalidation; non-success may preserve only partial cell evidence and opens no rerun/replacement.
105. DEC-179 independently verifies zero prior manual-main EXP-053 runs, adds the first-run rejection guard, and opens exactly one outer historical result-producing slot without dispatch. The first attempt consumes the slot on any terminal outcome and must route through DEC-178; no rerun/replacement, promotion, or trading authority is opened.
106. DEC-180 freezes the clean-main, double-plan, one-way EXP-053 operator. Only a zero-run MISSING state can expose the single frozen workflow-dispatch command; active or terminal state exposes no second dispatch, and terminal evidence routes through DEC-178 with DEC-176 aggregate revalidation on success. DEC-180 itself dispatches nothing.
107. DEC-181 freezes a repository-hosted read-only runner for the exact DEC-180 next plan, using non-editable dependency installation and RUNNER_TEMP output so the clean-worktree gate remains valid. It contains no advance/execute or direct model-workflow dispatch path and changes no authorization.
108. Run `36126977702` succeeds on attempt 1 and proves the exact DEC-180 MISSING/RUN_DISPATCH_REQUIRED state at `7e5d042ab7cc46c18de0f72bd4302ec9dd676e84`, with immutable plan artifact `10860591486` / digest `sha256:9ca87fe6ec7c0ff8193ee4eef943e82053721c3fd762e5e69d7fa711471f6066`. DEC-182 freezes a one-shot main-push executor whose only execution-capable action is DEC-180 `advance --execute`; it contains no direct model-workflow dispatch, retry, rerun, or replacement path.
109. DEC-183 closes EXP-053 after successful attempt-1 run `36127730584` at `1a6e3670215665f2aed04d28c66c674408080953`: 18 cells, 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 10 aggregate passes, zero stable passes, and zero selected cells.
110. DEC-184 freezes the EXP-050/051/052/053 post-result diagnostic. Feature support expands aggregate passes from 1 to 10 across six cells, but all 10 still miss the 2021 share floor somewhere and 9 of 10 fail 2022 H1 financially. Only successor source design may open; rerun/execution/promotion/trading remain locked.
111. DEC-185 opens source-only EXP-054 with 24 target-specific out-of-fit fit-half-year residual references per cell. A fixed lower-quartile residual creates a conservative residual-bound utility score that ranks already EXP-053-eligible rows first, while feature support, utility support, pooled calibration, raw utility, budgets, chronology, financial gates, and temporal-stability gates remain unchanged. No fit or result execution is authorized.
112. DEC-186 merges the first EXP-054 residual-bound training primitives at `0fc2192152824ca2c3411517dff192d240ea9cd2`; review then identifies that the complete cell-level selection/validation/holdout runner is still missing, so no workflow or result execution is opened.
113. DEC-187 merges the first non-executable EXP-054 residual-evidence contract at `1c56ec7241d5795791ac83f1b58ac875b74e9645`, requiring 24 residual references per cell / 432 total and keeping all fit/result/trading authority false.
114. DEC-188 supersedes the incomplete DEC-186 executable shape by freezing the complete deterministic EXP-054 cell runner and rebinding the artifact contract to exact training blob `4f3f189c104d41352433397421f021896c03a5e9`. Historical result execution, workflow dispatch, promotion, shadow/demo, broker mutation, live orders, real-money action, and trading remain locked.
115. DEC-189 freezes the manual-main input-free EXP-054 model workflow, public CLI, pinned Python 3.12.14 runtime, and exact-source execution gate. It deliberately has no first-run guard and keeps model-run dispatch, authoritative result execution, model-protocol result production, model fit, promotion, shadow/demo, broker mutation, live orders, real-money action, and trading false.
116. DEC-190 predeclares the attempt-1-only EXP-054 terminal review before any run is authorized. Success requires all 11 jobs, all nine cell artifacts plus the aggregate artifact, and deterministic aggregate recompilation proving all 18 cells and 432 residual references; terminal non-success preserves only partial cell evidence and opens no rerun/replacement. Dispatch, result execution, model fit, promotion, shadow/demo, broker mutation, live orders, real-money action, and trading remain locked.
117. DEC-191 independently verifies zero prior manual-main EXP-054 model-workflow runs among 25 repository manual-main dispatches, adds the first-run rejection guard, and opens exactly one outer historical result-producing slot without dispatch. The first attempt consumes the slot on any terminal outcome and must route through DEC-190; promotion, shadow/demo, broker mutation, live orders, real-money action, and trading remain locked.
109. DEC-182 executor run `36127676468` submits the single EXP-053 model attempt through DEC-180; its later receipt-verification step fails on empty/non-JSON receipt output after dispatch and opens no second attempt. Run `36127730584` completes successfully on attempt 1 at `1a6e3670215665f2aed04d28c66c674408080953`. DEC-183 reviews complete 18-cell / 108-regressor / 108-pooled-reference / 432-utility-support-reference / 216-feature-support-reference evidence, records 10 aggregate financial passes with zero temporal-stability passes, accepts no model candidate, and closes the consumed EXP-053 slot.

### EXP-011 disposition — STOPPED BEFORE CAMPAIGN REGISTRATION

`EXP-20260922-011` is preserved but will not be launched.

Completed non-scored evidence:

- source code updated to post-liveness-amendment main `5cb884dfb15d7798b023658e025221a38dfec9fc`
- fresh local connector qualification: PASS
- qualification: 100 prices, 15 heartbeats, zero rejection codes, maximum bridge/market liveness gap 3.884147625 seconds
- fresh historical reference code commit: `5cb884dfb15d7798b023658e025221a38dfec9fc`
- fresh reference SHA-256: `e920b3254235d2bb0766762551b5eb9d21439d429c59aebd14c3e4bb16e8cc64`
- fresh reference historical trade count: 199
- no EXP-011 campaign registration occurred
- no EXP-011 live-shadow segment is authorized to start

The older EXP-009 and EXP-010 evidence also remains preserved unchanged.

### Phase 8B — Multi-strategy live shadow — LOCKED

Phase 8B may begin only after Phase 8A produces and freezes one or more portfolio/shadow candidates under an acceptance review.

DEC-046 freezes the source-free design/connector topology that may be compiled only from an exact accepted DEC-045 artifact. Design compilation alone does not register or start a campaign.

Phase 8B must:

- expand or replace the current USDJPY-only read-only bridge as needed to observe all approved portfolio instruments
- preserve structural impossibility of broker order submission
- freeze the champion strategy set and exact versions for each registered campaign
- retain bridge/market liveness separation and fail-closed missing-path behavior from DEC-038
- collect genuinely prospective evidence for post-Phase-7 challengers
- prevent the research/learning path from mutating the active campaign

### Execution locks

- MT5 AutoTrading: OFF
- Phase 9/demo order placement: LOCKED
- production/live order placement and broker mutation: LOCKED
- real-money trading: LOCKED

DEC-143 freezes the artifact-backed result-evidence contract against the exact DEC-141/142 sources and accepted historical feature/outcome/readiness identities, validates complete three-view / 18-cell / 108-regressor evidence, and keeps the authoritative bundle locked before readiness or historical artifact loading. DEC-144 freezes the manual-main workflow, CLI, pinned runtime, and exact-source execution gate while keeping dispatch/result/fit authorization false. DEC-145 predeclares the exact attempt-1 terminal review. DEC-146 independently verifies zero prior manual-main EXP-050 runs, hardens the workflow with a first-run guard, and opens exactly one outer historical result-producing slot without dispatching it; the first attempt consumes the slot on any terminal outcome and must route through DEC-145. DEC-147 freezes the clean-main double-plan one-way operator. Run `36049824739` then completes successfully on attempt 1 at `25d48828b981c4309f4a859d2a33a56094638f21`. DEC-148 reviews the complete 18-cell / 108-regressor evidence, records three USDJPY 5m / 60m aggregate-pass variants with zero temporal-stability passes, records no stable challenger, and closes the consumed EXP-050 run slot. DEC-149 freezes the post-result diagnostic: 26 of 54 budget variants are unavailable, three of 28 available variants pass the aggregate gate, all three passes are concentrated in USDJPY 5m / 60m, and early-2021 candidate coverage prevents every pass from clearing temporal stability. DEC-150 opens source-only EXP-051, preserving EXP-050 eligibility/gates while replacing raw-utility-only ranking with out-of-fit excluded-regime percentile calibration; selection-period windows do not enter calibration. DEC-151 implements the deterministic in-memory EXP-051 core with six excluded-regime calibration references per cell and a frozen calibrated/raw cutoff pair while preserving the unchanged financial/stability pipeline. DEC-152 freezes the artifact-backed result-evidence contract, requiring complete 18-cell / 108-regressor / 108-calibration-reference evidence and keeping the authoritative bundle locked before readiness/artifact loading. DEC-153 freezes the manual-main workflow, CLI, pinned runtime, and exact-source gate while keeping dispatch/result/fit authorization false and intentionally omitting any first-run guard. DEC-154 predeclares exact attempt-1 terminal review: success requires all 11 jobs, all nine cell artifacts, the aggregate artifact, and DEC-152 revalidation; non-success can preserve only partial cell evidence and opens no rerun/replacement. DEC-155 verifies zero prior manual-main EXP-051 runs, adds the first-run rejection guard, and opens exactly one outer historical result-producing slot without dispatch. DEC-156 freezes the clean-main double-plan one-way operator; only zero-run state may expose one dispatch and terminal evidence routes through DEC-154. DEC-157 adds a read-only repository-hosted runner for the exact DEC-156 next plan and still contains no dispatch path. Run `36064683930` fails closed because editable installation dirtied the checkout; DEC-158 removes that mutation. Run `36065119686` fails closed because checkout-local plan output is created before DEC-156 preflight; DEC-159 moves plan output to `RUNNER_TEMP`. Run `36065565456` succeeds and proves the exact DEC-156 MISSING/RUN_DISPATCH_REQUIRED state with plan artifact `10835714803`. DEC-160 freezes the one-shot executor, which submits the sole EXP-051 attempt through DEC-156. Run `36066217609` completes successfully on attempt 1 at `3443b95ae3c524c74df4b2daebe9c526eb01ec9c`. DEC-161 reviews complete 18-cell / 108-regressor / 108-calibration-reference evidence, records one USDJPY 5m / 60m budget-250 aggregate pass with zero temporal-stability passes, records no stable challenger, and closes the consumed EXP-051 run slot. DEC-162 shows that calibration preserves eligibility, improves the top-250 financial result, fails to create 2021 support, and degrades the broader 500/1000 ranks; stable passes remain zero. DEC-163 opens source-only EXP-052 with 24 out-of-fit fit-half-year support references and support-first ranking while preserving EXP-051 eligibility, pooled calibration, budgets, gates, chronology, and no-refit semantics. DEC-164 implements the deterministic in-memory EXP-052 core with the same six regressors, six pooled references, 24 support references, support/pooled/raw cutoff triple, and unchanged financial/stability/forward pipeline. DEC-165 freezes the artifact-backed evidence contract, requiring complete 18-cell / 108-regressor / 108-pooled-reference / 432-support-reference evidence and keeping the authoritative bundle locked before readiness/artifact loading. DEC-166 freezes the manual-main, input-free workflow/CLI/pinned-runtime/exact-source gate while keeping dispatch/result/fit authorization false and deliberately omitting any first-run guard. DEC-167 predeclares exact attempt-1 terminal review: success requires all 11 jobs, all nine cell artifacts, the aggregate artifact, and DEC-165 revalidation; non-success may preserve only partial cell evidence and opens no rerun/replacement. DEC-168 verifies zero prior manual-main EXP-052 runs, adds the first-run rejection guard, and opens exactly one outer historical result-producing slot without dispatch. DEC-169 freezes the clean-main double-plan one-way operator; only zero-run state may expose one dispatch and terminal evidence routes through DEC-167. DEC-170 freezes a read-only repository-hosted runner for the exact DEC-169 next plan with clean-worktree-safe installation/output and no dispatch path. Run `36114078121` succeeds and proves the exact DEC-169 MISSING/RUN_DISPATCH_REQUIRED state with plan artifact `10853944005`. DEC-171 freezes the one-shot executor, whose only execution action is DEC-169 advance --execute and which contains no direct model-workflow dispatch/retry path. Run `36114617377` completes successfully on attempt 1 at `d477555cf116f07fa195de1b4a4c0d2f3b2838c5`. DEC-172 reviews complete 18-cell / 108-regressor / 108-pooled-reference / 432-support-reference evidence, records one USDJPY 5m / 60m budget-250 aggregate pass with all 250 candidates concentrated in 2022 H2, records no stable challenger, and closes the consumed EXP-052 run slot. DEC-173 shows that fit-half-year support ranking changes candidate identity but does not transfer into selection-period support: EXP-052 returns to `[0,0,0,250]`, slightly underperforms EXP-051 at budget 250, improves but still rejects budget 500, and leaves budget 1000 unchanged. DEC-174 opens source-only EXP-053 with 12 fit-only view-by-half-year feature-support references per cell, feature-support-first ranking, and a frozen feature-support/utility-support/pooled/raw cutoff quadruple while preserving EXP-052 eligibility, budgets, gates, chronology, and no-refit semantics. DEC-175 implements the deterministic in-memory EXP-053 core with the same six regressors, six pooled references, 24 utility-support references, 12 feature-support references, feature/utility-support/pooled/raw cutoff quadruple, and unchanged financial/stability/forward pipeline. DEC-176 freezes the non-executable artifact-backed evidence contract, requiring complete 18-cell / 108-regressor / 108-pooled-reference / 432-utility-support-reference / 216-feature-support-reference evidence and keeping the authoritative bundle locked before readiness/artifact loading. DEC-177 freezes the manual-main, input-free workflow, public CLI, pinned runtime, and exact-source gate while deliberately keeping dispatch/result/fit authorization false and omitting any first-run guard. DEC-178 predeclares exact attempt-1 terminal review: success requires all 11 jobs, all nine cell artifacts, the aggregate artifact, and DEC-176 revalidation; non-success may preserve only partial cell evidence and opens no rerun/replacement. DEC-179 verifies zero prior manual-main EXP-053 runs, adds the first-run rejection guard, and opens exactly one outer historical result-producing slot without dispatch. DEC-180 freezes the clean-main double-plan one-way operator; only zero-run state may expose one dispatch and terminal evidence routes through DEC-178. DEC-181 freezes a repository-hosted read-only runner for the exact DEC-180 next plan with clean-worktree-safe installation/output and no dispatch path. Run `36126977702` then succeeds and proves the exact DEC-180 MISSING/RUN_DISPATCH_REQUIRED state with plan artifact `10860591486`. DEC-182 freezes the one-shot executor, whose only execution-capable action is DEC-180 `advance --execute` and which contains no direct model-workflow dispatch/retry/rerun path. Executor run `36127676468` successfully submits the model workflow before its receipt parser fails on empty/non-JSON output; no second executor or replacement is authorized. Run `36127730584` completes successfully on attempt 1 at `1a6e3670215665f2aed04d28c66c674408080953`. DEC-183 reviews complete 18-cell / 108-regressor / 108-pooled-reference / 432-utility-support-reference / 216-feature-support-reference evidence, records 10 aggregate-selection passes but zero temporal-stability passes, accepts no model candidate, and closes the consumed EXP-053 slot. The next safe gate is post-result diagnostic analysis only; promotion/shadow/demo/broker/live/real-money/trading paths remain locked. No prospective shadow campaign has begun.



DEC-188 completes the EXP-054 deterministic residual-bound core and rebinds the evidence contract. DEC-189 freezes the manual-main workflow/CLI/runtime source with execution closed. DEC-190 predeclares terminal review. DEC-191 proves zero prior EXP-054 manual-main model runs, adds the first-run guard, and opens exactly one outer historical result-producing slot without dispatch. DEC-192 freezes the clean-main double-plan one-way operator: only an exact zero-run state may expose the single guarded dispatch; in-progress or terminal state forbids replacement, and terminal evidence must route through DEC-190. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.

DEC-193 adds the repository-hosted read-only proof for the exact DEC-192 next plan. It is main-push/path scoped, uses only read permissions, preserves a clean checkout, writes plan output under RUNNER_TEMP, invokes only the operator's read-only next action, and cannot dispatch or rerun the EXP-054 model workflow. The DEC-191 one-slot authorization remains unconsumed until a later separately frozen executor actually submits the guarded workflow. All promotion/shadow/demo/broker/live/real-money/trading paths remain locked.

DEC-194 corrects the read-only DEC-193 proof path after merged-main run 36147095990 failed on a nonexistent EXP-054 artifact-loader import before any dispatch-capable action. The operator now parses aggregate JSON locally and delegates authoritative evidence acceptance to the unchanged DEC-190 deterministic terminal review. The read-only proof workflow also retriggers on operator-source changes. The DEC-191 historical-run slot remains unconsumed; no executor or model workflow has been dispatched.

DEC-195 binds successful corrected read-only proof run 36151472585 and its exact non-expired plan artifact, then freezes a separate one-shot executor whose only execution-capable action is DEC-192 advance --execute. The executor has no independent model-workflow dispatch, rerun, retry, or replacement path; DEC-192 still performs fresh clean-main zero-run checks and double planning immediately before any dispatch. If the initial merged-main executor submits the EXP-054 historical workflow, that attempt consumes the DEC-191 slot on any terminal outcome and must route through DEC-190. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-196 closes the sole EXP-054 historical-result slot after run `36152351767` succeeds on attempt 1 at `5ca369a87f8a761c3232b75f95a701043721fd36`. DEC-190 review requirements are satisfied: all 11 jobs succeed, all nine exact cell artifacts plus the aggregate artifact are non-expired, the aggregate ZIP digest reproduces exactly, the aggregate evidence fingerprint `307b576f06c6aa2fb01a267232a0de553bfa79c1bdbe6bf5d55b2bfc3b40787c` recomputes exactly, and all 18 cell fingerprints validate. Reviewed evidence contains 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, and 432 residual references. Of 54 budget variants, 28 are available and 26 unavailable. EXP-054 preserves 26,392 utility-eligible selection rows and produces exactly two aggregate passes, both USDJPY 5m / 60m at budgets 250 and 1000, but zero temporal-stability passes, zero selected cells, zero validation/holdout passes, and zero accepted model candidates. The EXP-054 slot is closed with no rerun/replacement. The next safe gate is post-result diagnostic analysis only; promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.

DEC-197 freezes the EXP-054 post-result diagnostic after DEC-196 closes the consumed historical slot. Across EXP-050 through EXP-054, aggregate-pass counts are 3/1/1/10/2 while stable-pass counts remain zero throughout. EXP-054's residual-bound ranking narrows passes to USDJPY 5m / 60m budgets 250 and 1000. The top-250 set is entirely concentrated in 2022 H2; at budget 1000 the ranking improves 2022 H1 financial sign but reduces 2022 H1 share to 7.2% and shifts more candidates into a financially negative 2022 H2. The frozen classification is RESIDUAL_BOUND_NARROWED_AGGREGATE_PASSES_AND_IMPROVED_SOME_DOWNSIDE_WINDOWS_BUT_DID_NOT_CREATE_TEMPORAL_BREADTH. Only successor protocol source design may open; all execution/promotion/trading paths remain locked.


DEC-198 opens source-only EXP-055 after DEC-197 shows that EXP-054 improved some downside windows but still did not create temporal breadth. EXP-055 preserves the full EXP-054 eligibility/reference/gate/chronology pipeline and adds only a fit-temporal residual-breadth ranking score: for each eligible row, count the twelve frozen EXP-054 downside-adjusted fit-half-year lower bounds that remain strictly positive and divide by 12. Breadth ranks first, followed by the unchanged residual-bound, feature-support, utility-support, pooled-calibrated, and raw-utility scores; each budget freezes the resulting six-part cutoff. No selection-window information, quota, stability relaxation, model fit, historical execution, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading is authorized. The next gate is a deterministic in-memory EXP-055 training/evaluation core only.


DEC-199 implements the full deterministic in-memory EXP-055 residual-breadth cell core against merged DEC-198. It reuses the exact DEC-188 fitting/reference/gate mechanics and adds only breadth scoring over the twelve frozen EXP-054 lower bounds, breadth-aware consensus/digest, a breadth-first six-part cutoff, and unchanged forward application. The source contains no artifact loader, readiness execution, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading path. The next safe gate is a separate non-executable EXP-055 artifact/evidence contract.


DEC-200 freezes the non-executable EXP-055 artifact/evidence contract against merged DEC-199. It validates complete 18-cell evidence, deterministic cell fingerprints, 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 exact residual references, the twelve-bound breadth inventory, and breadth-first six-part cutoffs. The authoritative bundle remains fail-closed before execution. No workflow dispatch, historical result execution, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading is authorized. The next gate is a manual-main workflow/CLI/runtime source freeze with execution still closed.


DEC-201 freezes the manual-main/input-free EXP-055 workflow, public CLI, Python 3.12.14 pinned runtime, and exact-source execution gate against merged DEC-198/199/200. All four outer historical-run controls remain false, so the source can exist on main but any execution attempt fails closed before readiness/artifact loading. No first-run guard or historical slot is opened yet. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a separate predeclared attempt-1 terminal review.


DEC-202 predeclares exact attempt-1 terminal review for any later separately authorized EXP-055 historical run. Success requires the exact manual-main workflow, all 11 jobs successful, all nine non-expired cell artifacts plus the aggregate artifact, and deterministic DEC-200 revalidation of complete 18-cell / 108-regressor / 108-pooled-reference / 432-utility-support-reference / 216-feature-support-reference / 432-residual-reference evidence with the twelve-bound breadth inventory. Non-success opens no rerun/retry/replacement. All execution, promotion, shadow/demo, broker, live-order, real-money, and trading paths remain locked. The next safe gate is zero-prior-run proof plus a first-run guard and at most one bounded outer historical slot.


DEC-203 verifies zero exact prior EXP-055 manual-main model runs in the latest 100 Actions runs, hardens the frozen EXP-055 workflow with a first-run rejection guard, and opens exactly one outer historical-result slot without dispatching it. The guard rejects any prior manual-main EXP-055 run before result execution. Underlying protocol/core/artifact execution authorizations remain false; only the bounded outer gate exposes dispatch/result/fit for the first attempt. Any terminal outcome consumes the slot and must route through DEC-202; no rerun, retry, or replacement is authorized. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a clean-main double-plan one-way operator only.


DEC-204 freezes the clean-main double-plan one-way operator for EXP-055. Only an exact zero-run `MISSING` state may expose the single DEC-203-authorized dispatch command; `IN_PROGRESS` and `TERMINAL` states cannot produce replacement dispatches, and terminal evidence must route through DEC-202. The operator verifies clean current main and exact origin identity before planning, and its public CLI re-plans immediately before any explicit execution. DEC-204 itself does not dispatch or consume the EXP-055 slot. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a repository-hosted read-only plan proof only.


DEC-205 adds the repository-hosted read-only proof for the exact DEC-204 `next` plan. It is main-push/path scoped, uses only read permissions, preserves a clean checkout, writes plan output under `RUNNER_TEMP`, invokes only the operator's read-only `next` action, and cannot dispatch or rerun the EXP-055 model workflow. The DEC-203 one-slot authorization remains unconsumed until a later separately frozen executor actually submits the guarded workflow. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-206 binds successful merged-main read-only proof run `36162871611` and its exact non-expired plan artifact, then freezes a separate one-shot executor whose only execution-capable action is DEC-204 `advance --execute`. The executor has no independent model-workflow dispatch, rerun, retry, or replacement path; DEC-204 still performs fresh clean-main zero-run checks and double planning immediately before any dispatch. If the initial merged-main executor submits the EXP-055 historical workflow, that attempt consumes the DEC-203 slot on any terminal outcome and must route through DEC-202. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-207 closes the sole EXP-055 historical-result slot after run `36163466744` succeeds on attempt 1 at `fa3f90709fa71f3b49f43985c505707da3c524af`. DEC-202 review requirements are satisfied: all 11 jobs succeed, all nine exact cell artifacts plus the aggregate artifact are non-expired, the aggregate ZIP digest reproduces exactly, the aggregate evidence fingerprint `f3a386dad7f23ac9d6867d030ac90e0884f3ab658c9ffecce8647048037d2510` recomputes exactly, and all 18 cell fingerprints validate. Reviewed evidence contains 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, and the fixed twelve-bound residual-breadth inventory. Of 54 budget variants, 28 are available and 26 unavailable. EXP-055 preserves 26,392 utility-eligible selection rows and produces exactly two aggregate passes, both USDJPY 5m / 60m at budgets 250 and 1000, but zero temporal-stability passes, zero selected cells, zero validation/holdout passes, and zero accepted model candidates. The four-window candidate counts are 0/0/0/251 for budget 250 and 0/1/83/916 for budget 1000. The EXP-055 slot is closed with no rerun/replacement. The next safe gate is post-result diagnostic analysis only; promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-208 diagnoses the closed EXP-055 result against immutable EXP-054 evidence. The two experiments retain identical eligibility, budget availability, aggregate-pass identities, and zero stable passes. EXP-055 breadth-first ranking leaves the budget-250 pass fully concentrated in 2022 H2 despite a 10/12 breadth cutoff, moves the budget-1000 2022 H1 share only from 7.2% to 8.3% without clearing the 10% floor, and weakens the surviving pass variants' aggregate/window financial quality. Across the 28 available variants, 7 improve aggregate 0.5-pip net, 16 worsen, and 5 are unchanged. The result is classified as fit residual breadth not transferring to selection-time temporal breadth. Only successor protocol source design is open; rerun/replacement, stability relaxation, selection-window tuning, successor model fit/result execution, promotion, shadow/demo, broker mutation, live orders, real-money action, and trading remain locked.


DEC-209 opens source-only EXP-056 after DEC-208 shows that binary fit residual breadth did not transfer into selection-time chronological breadth. EXP-056 preserves the full EXP-055 eligibility/reference/gate/chronology pipeline and adds only a continuous residual lower-tail ranking score: for each eligible row, sort the same twelve frozen downside-adjusted fit-half-year lower bounds and average the three worst values. Lower-tail mean ranks first, followed by unchanged residual breadth, residual-bound utility, feature support, utility support, pooled-calibrated utility, raw utility, then row identity; each budget freezes the resulting seven-part cutoff. No selection-window information, quota, stability relaxation, model fit, historical execution, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading is authorized. The next gate is a deterministic in-memory EXP-056 training/evaluation core only.


DEC-210 implements the full deterministic in-memory EXP-056 residual lower-tail cell core against merged DEC-209. It reuses the frozen EXP-055/054 six-regressor, pooled-calibration, utility-support, feature-support, residual-reference, residual-bound, residual-breadth, financial-gate, temporal-stability, and forward-chronology machinery and adds only the continuous worst-three lower-tail mean, lower-tail-aware consensus digest, lower-tail-first seven-part cutoff, and matching forward application. No new reference family, artifact loading, readiness execution, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading path is opened. The next safe gate is a separate non-executable EXP-056 artifact/evidence contract bound to this exact training core.


DEC-211 freezes the non-executable EXP-056 artifact/evidence contract against merged DEC-210. It validates exact 18-cell evidence, deterministic cell fingerprints, 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, the twelve-bound residual-breadth inventory, the twelve-bound lower-tail source inventory, fixed worst-three lower-tail count, and seven-part lower-tail/breadth/residual-bound/support cutoffs. The authoritative bundle remains fail-closed before execution. No workflow dispatch, historical result execution, model fit, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading is authorized. The next gate is a manual-main EXP-056 workflow/CLI/runtime source freeze with execution still closed.


DEC-212 freezes the manual-main/input-free EXP-056 workflow, public CLI, Python 3.12.14 pinned runtime, and exact-source execution gate against merged DEC-209/210/211. All four outer historical-run controls remain false, so the source can exist on main but any execution attempt fails closed before readiness/artifact loading. No first-run guard or historical slot is opened yet. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a separate predeclared attempt-1 terminal review.


DEC-213 predeclares exact attempt-1 terminal review for any later separately authorized EXP-056 historical run. Success requires the exact manual-main workflow, all 11 jobs successful, all nine non-expired cell artifacts plus the aggregate artifact, and deterministic DEC-211 revalidation of complete 18-cell / 108-regressor / 108-pooled-reference / 432-utility-support-reference / 216-feature-support-reference / 432-residual-reference evidence with both twelve-bound breadth/lower-tail inventories and fixed lower-tail count 3. Non-success opens no rerun/retry/replacement. All execution, promotion, shadow/demo, broker, live-order, real-money, and trading paths remain locked. The next safe gate is zero-prior-run proof plus a first-run guard and at most one bounded outer historical slot.


DEC-214 proves zero exact prior EXP-056 manual-main model runs in the latest 100 Actions runs, hardens the frozen EXP-056 workflow with a first-run rejection guard, and opens exactly one outer historical-result slot without dispatching it. The guard rejects any prior exact manual-main EXP-056 run before result execution. Underlying protocol/core/artifact execution authorizations remain false; only the bounded outer gate exposes dispatch/result/fit for the first attempt. Any terminal outcome consumes the slot and must route through DEC-213; no rerun, retry, or replacement is authorized. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a clean-main double-plan one-way operator only.


DEC-215 freezes the clean-main double-plan one-way EXP-056 operator against merged DEC-214. Only a live `MISSING` state can expose the exact guarded dispatch command; `IN_PROGRESS` and `TERMINAL` states never expose a replacement action, and terminal evidence routes through DEC-213. The operator itself does not dispatch or consume the historical slot. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a repository-hosted read-only `next` proof runner with no dispatch path.


DEC-216 adds a repository-hosted read-only proof for the exact DEC-215 EXP-056 `next` plan. The workflow is main-push/path scoped, read-permission only, preserves a clean checkout, invokes only the public operator's read-only `next` action, writes only under runner temp, and persists the plan artifact. It cannot invoke `advance`, execute a dispatch, rerun/retry/replace a model run, or claim a result. A successful proof must show the live EXP-056 state is still `MISSING` and that only the already bounded DEC-214 first-run action is available, with all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false. DEC-216 consumes no historical slot.


DEC-217 binds the successful DEC-216 merged-main read-only proof and freezes exactly one repository-hosted EXP-056 executor. The executor independently revalidates the proof run, artifact metadata, artifact ZIP digest, and plan contents, then invokes only DEC-215 `advance --execute`. It contains no direct model-workflow dispatch, rerun, retry, or replacement path. After submission it independently confirms that exactly one manual-main EXP-056 run exists on the executor merge SHA at attempt 1. If submitted, that run consumes the DEC-214 slot on any terminal outcome and must route through DEC-213. No second executor attempt or replacement model run is authorized; promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-218 closes the consumed EXP-056 historical slot after attempt-1 run `36175841645` fails on merged-main commit `3ce20d7445f6837cae067c0c561002215b05b2f9`. DEC-213 non-success review is satisfied: preflight succeeded, all nine matrix jobs failed, aggregate evidence was skipped, zero cell artifacts persisted, and no aggregate artifact/evidence exists. The failure is classified as implementation dependency/export drift: eight jobs fail on missing predecessor export `MIN_STABILITY_WINDOW_CANDIDATE_SHARE` and one later path fails on missing `FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL`. EXP-056 therefore produced no model result and no evidence for or against its intended lower-tail ranking. No rerun/retry/replacement is authorized. The next safe gate is source-only implementation-defect diagnostic work; promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-219 performs a deterministic AST audit of the failed EXP-056 lower-tail training core and freezes the complete implementation defect inventory. Exactly seven inherited EXP-054 constants/rules were incorrectly dereferenced through the intermediate EXP-055 module; all seven exist on the frozen EXP-054 `_base` module. Two were observed at runtime and five are latent. The repair boundary is implementation-only: a future successor may change only those seven `_predecessor.<name>` accesses to `_base.<name>`, with no protocol/data/model/chronology/ranking/gate change. EXP-056 rerun/replacement and all successor fit/execution, promotion, shadow/demo, broker, live-order, real-money, and trading paths remain closed. Only successor protocol source design under a new experiment identity is open.


DEC-220 opens source-only EXP-057 under a new experiment identity after the failed EXP-056 slot is closed. EXP-057 is semantically identical to EXP-056 and authorizes only the seven-name implementation dependency repair proven by DEC-219: those inherited EXP-054 constants/rules move from invalid `_predecessor` dereferences to `_base`; legitimate breadth-specific predecessor accesses remain unchanged. No protocol/data/model/chronology/ranking/gate change, model fit, historical execution, promotion, shadow/demo execution, broker mutation, live order, real-money action, or trading is authorized. The next gate is a deterministic in-memory EXP-057 training core only.


DEC-221 implements the full deterministic in-memory EXP-057 lower-tail training core against merged DEC-220. It preserves EXP-056 model/data/chronology/ranking/gate/forward semantics and changes exactly the seven dependency roots authorized by DEC-219/220 from invalid intermediate `_predecessor` accesses to `_base`. Legitimate breadth-specific predecessor accesses remain unchanged. The source gate marks lower-tail semantics retained, protocol change false, and implementation repair true; result execution, model fit authorization outside the core, artifact loading, readiness execution, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next gate is a non-executable EXP-057 artifact/evidence contract only.


DEC-222 freezes the non-executable EXP-057 artifact/evidence contract against merged DEC-221. It validates exact DEC-220/221 repair provenance per cell plus the inherited 18-cell evidence structure: 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, 12 residual-breadth bounds, 12 lower-tail source bounds, fixed worst-three lower-tail count, seven-part cutoffs, deterministic cell fingerprints, and deterministic aggregate fingerprinting. The authoritative bundle remains fail-closed. No workflow dispatch, historical result execution, model fit, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading is authorized. The next gate is an execution-closed EXP-057 workflow/CLI/runtime source freeze.


DEC-223 freezes the manual-main/input-free EXP-057 workflow, public CLI, Python 3.12.14 numerical runtime, and exact-source execution gate against merged DEC-220/221/222. The workflow preserves the exact nine pair/timeframe datasets, 60m/240m horizons, frozen feature/outcome/readiness artifacts, partial cell evidence, and aggregate evidence, but has no first-run guard yet. The CLI requires authorization before readiness/artifact loading, calls the repaired artifact compiler and repaired training module with the actual exported cell-runner symbol, and has no direct dispatch path. Model-run dispatch, historical result execution, model-protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a predeclared attempt-1 terminal-review contract only.


DEC-224 predeclares exact attempt-1 terminal review for any later separately authorized EXP-057 historical run. Success requires the exact manual-main workflow, all 11 jobs successful, all nine non-expired cell artifacts plus the aggregate artifact, and deterministic DEC-222 revalidation of complete 18-cell / 108-regressor / 108-pooled-reference / 432-utility-support-reference / 216-feature-support-reference / 432-residual-reference evidence with both twelve-bound breadth/lower-tail inventories and fixed lower-tail count 3. Non-success may preserve only produced expected cell artifacts and opens no rerun/retry/replacement. All execution, promotion, shadow/demo, broker, live-order, real-money, and trading paths remain locked. The next safe gate is zero-prior-run proof plus a first-run guard and at most one bounded outer historical slot.


DEC-225 proves zero exact prior EXP-057 manual-main model runs in the latest 100 Actions runs, hardens the frozen EXP-057 workflow with a first-run rejection guard, and opens exactly one outer historical-result slot without dispatching it. The guard rejects any prior exact manual-main EXP-057 run before result execution. Underlying repaired protocol/core/artifact execution authorizations remain false; only the bounded outer gate exposes dispatch/result/fit for the first attempt. Any terminal outcome consumes the slot and must route through DEC-224; no rerun, retry, or replacement is authorized. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a clean-main double-plan one-way operator only.


DEC-226 freezes a clean-main, one-way EXP-057 operator against merged DEC-225. It requires exact clean local `main` equal to fetched `origin/main`, verifies the Dtwosam/FMP origin, permits at most one exact manual-main EXP-057 workflow run, and treats only `MISSING` as dispatchable. `IN_PROGRESS` and `TERMINAL` never expose dispatch/replacement actions; terminal evidence routes through DEC-224. The public CLI provides read-only `next`, non-executing `advance`, and double-plan `advance --execute` with fail-closed state-drift checks. DEC-226 itself does not dispatch or consume the DEC-225 slot. Replacement/promotion/shadow/demo/broker/live-order/real-money/trading remain locked. The next safe gate is a repository-hosted read-only `next` plan runner only.


DEC-227 adds a repository-hosted read-only proof for the exact DEC-226 EXP-057 `next` plan. The workflow is main-push/path scoped, read-permission only, preserves a clean checkout, invokes only the public operator's read-only `next` action, writes only under runner temp, and persists the plan artifact. It cannot invoke `advance`, execute a dispatch, rerun/retry/replace a model run, or claim a result. A successful proof must show the live EXP-057 state is still `MISSING` and that only the already bounded DEC-225 first-run action is available, with all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false. DEC-227 consumes no historical slot.


DEC-228 binds the successful DEC-227 merged-main read-only proof and freezes exactly one repository-hosted EXP-057 executor. The executor independently revalidates the proof run, artifact metadata, artifact ZIP digest, and plan contents, then invokes only DEC-226 `advance --execute`. It contains no direct model-workflow dispatch, rerun, retry, or replacement path. After submission it independently confirms that exactly one manual-main EXP-057 run exists on the executor merge SHA at attempt 1. If submitted, that run consumes the DEC-225 slot on any terminal outcome and must route through DEC-224. No second executor attempt or replacement model run is authorized; promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-229 closes the consumed EXP-057 historical slot after successful attempt-1 run `36192572271` at `491a2e2715b4da7013737ecaebc65a58ac3417f9`. DEC-224 success review is satisfied: all 11 jobs succeeded, all nine cell artifacts plus the aggregate artifact are non-expired, aggregate evidence fingerprint `4bf67108e0df38d4f213d08898fadd338285ac7a2ce56920b61e4dba0f3eec4c` revalidates, and the complete 18-cell / 108-regressor / 108-pooled-reference / 432-utility-support-reference / 216-feature-support-reference / 432-residual-reference / 12-breadth-bound / 12-lower-tail-bound / lower-tail-count-3 inventory is intact. Of 54 variants, 28 are available and 26 unavailable. Three USDJPY 5m / 60m variants at budgets 250, 500, and 1000 pass the aggregate gate, but their four-window candidate counts `0/0/0/250`, `0/0/3/497`, and `0/1/73/926` all fail temporal stability. No cell is selected; validation and holdout remain locked; accepted model candidate count is zero. No rerun/retry/replacement is authorized. The next safe gate is post-result diagnostic analysis only; promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-230 diagnoses the closed EXP-057 result against the nearest prior successful model-result baseline, EXP-055. Variant accounting and utility-eligible rows are unchanged. EXP-057 retains the USDJPY 5m / 60m budget-250 and budget-1000 aggregate passes and adds budget 500, while stable-pass count remains zero. Across 28 available variants, 15 improve aggregate 0.5-pip total net pips and 13 worsen. The new budget-500 pass is still concentrated `0/0/3/497`; budget 250 remains `0/0/0/250`; budget 1000 shifts from EXP-055 `0/1/83/916` to EXP-057 `0/1/73/926`. The result is classified as lower-tail ranking changing candidate financial mix and adding an aggregate pass without creating selection-time temporal stability. EXP-057 rerun/replacement, gate relaxation, selection-window tuning, successor fit/result execution, promotion, shadow/demo, broker, live-order, real-money, and trading remain locked. Only successor protocol source design is open.


DEC-231 opens source-only EXP-058 after DEC-230 shows that lower-tail ranking changes aggregate candidate identity/financial mix but does not create selection-time temporal stability. EXP-058 adds one fit-only regime-floor score from the same twelve frozen downside-adjusted residual lower bounds: average the four bounds inside each of the three jackknife-excluded two-year fit regimes, then take the minimum of the three regime means. Ranking places this regime floor ahead of the existing lower-tail/breadth/residual-bound/support stack and freezes an eight-part cutoff. Eligibility, references, budgets, financial gates, temporal-stability windows/share floor, chronology, validation/holdout, and no-refit semantics remain unchanged. Selection-window outcomes/quotas/recalibration and all fit/execution/promotion/trading paths remain closed. The next gate is a deterministic in-memory EXP-058 training/evaluation core only.


DEC-232 implements the full deterministic in-memory EXP-058 residual regime-floor cell core against merged DEC-231. It preserves the repaired EXP-057 model/data/chronology/reference/ranking/gate/forward stack and adds only the fit-only regime-floor score: mean the four downside-adjusted bounds within each of the three jackknife views, then take the minimum regime mean. Ranking becomes regime-floor first followed by the unchanged lower-tail/breadth/residual-bound/support/calibration/raw stack, with an eight-part cutoff. No artifact loading, readiness execution, workflow dispatch, model-result execution, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading is opened. The next safe gate is a non-executable EXP-058 artifact/evidence contract only.


DEC-233 freezes the non-executable EXP-058 artifact/evidence contract against merged DEC-232. It validates exact 18-cell evidence, deterministic cell fingerprints, 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, the twelve-bound residual-breadth inventory, the twelve-bound lower-tail source inventory, lower-tail count 3, three residual fit regimes, four residual windows per regime, the twelve-bound regime-floor source inventory, and eight-part regime-floor/lower-tail/breadth/residual-bound/support cutoffs. The authoritative bundle remains fail-closed before execution. No workflow dispatch, historical result execution, model fit, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading is authorized. The next gate is a manual-main EXP-058 workflow/CLI/runtime source freeze with execution still closed.


DEC-234 freezes the manual-main/input-free EXP-058 workflow, public CLI, Python 3.12.14 numerical runtime, and exact-source execution gate against merged DEC-231/232/233. The workflow preserves the exact nine pair/timeframe datasets, 60m/240m horizons, frozen feature/outcome/readiness artifacts, partial cell evidence, and aggregate evidence, but has no first-run guard yet. The CLI requires authorization before readiness/artifact loading or regime-floor model execution and has no direct dispatch path. Model-run dispatch, historical result execution, model-protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a predeclared attempt-1 terminal-review contract only.


DEC-235 predeclares exact attempt-1 terminal review for any later separately authorized EXP-058 historical run. Success requires the exact manual-main regime-floor workflow, all 11 jobs successful, all nine non-expired cell artifacts plus the aggregate artifact, and deterministic DEC-233 revalidation of complete 18-cell / 108-regressor / 108-pooled-reference / 432-utility-support-reference / 216-feature-support-reference / 432-residual-reference evidence plus 12 breadth bounds, 12 lower-tail bounds, lower-tail count 3, three residual fit regimes, four residual windows per regime, and 12 regime-floor source bounds. Non-success may preserve only produced expected cell artifacts and opens no rerun/retry/replacement. All execution, promotion, shadow/demo, broker, live-order, real-money, and trading paths remain locked. The next safe gate is zero-prior-run proof plus a first-run guard and at most one bounded outer historical slot.


DEC-236 proves zero exact prior EXP-058 manual-main model runs in the latest 100 Actions runs, hardens the frozen EXP-058 workflow with a first-run rejection guard, and opens exactly one outer historical-result slot without dispatching it. The guard rejects any prior exact manual-main EXP-058 run before result execution. Underlying DEC-231/232/233 protocol/core/artifact execution authorizations remain false; only the bounded outer gate exposes dispatch/result/fit for the first attempt. Any terminal outcome consumes the slot and must route through DEC-235; no rerun, retry, or replacement is authorized. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a clean-main double-plan one-way operator only.


DEC-237 freezes a clean-main, one-way EXP-058 operator against merged DEC-236. It requires exact clean local `main` equal to fetched `origin/main`, verifies the Dtwosam/FMP origin, permits at most one exact manual-main EXP-058 workflow run, and treats only `MISSING` as dispatchable. `IN_PROGRESS` and `TERMINAL` never expose dispatch/replacement actions; terminal evidence routes through DEC-235. The public CLI provides read-only `next`, non-executing `advance`, and double-plan `advance --execute` with fail-closed state-drift checks. DEC-237 itself does not dispatch or consume the DEC-236 slot. Replacement/promotion/shadow/demo/broker/live-order/real-money/trading remain locked. The next safe gate is a repository-hosted read-only `next` plan runner only.


DEC-238 adds a repository-hosted read-only proof for the exact DEC-237 EXP-058 `next` plan. The workflow is main-push/path scoped, read-permission only, preserves a clean checkout, invokes only the public operator's read-only `next` action, writes only under runner temp, and persists the plan artifact. It cannot invoke `advance`, execute a dispatch, rerun/retry/replace a model run, or claim a result. A successful proof must show the live EXP-058 state is still `MISSING` and that only the already bounded DEC-236 first-run action is available, with all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false. DEC-238 consumes no historical slot.


DEC-239 binds the successful DEC-238 merged-main read-only proof and freezes exactly one repository-hosted EXP-058 executor. The executor independently revalidates the proof run, artifact metadata, artifact ZIP digest, and plan contents, then invokes only DEC-237 `advance --execute`. It contains no direct model-workflow dispatch, rerun, retry, or replacement path. After submission it independently confirms that exactly one manual-main EXP-058 run exists on the executor merge SHA at attempt 1. If submitted, that run consumes the DEC-236 slot on any terminal outcome and must route through DEC-235. No second executor attempt or replacement model run is authorized; promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-240 closes the consumed EXP-058 historical slot after successful attempt-1 run `36207673978` on merged-main commit `2339762cda013322c8704cee12218ec4f4fb8c36`. Complete deterministic evidence is present: 18 cells, 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, 12 breadth bounds, 12 lower-tail bounds, lower-tail count 3, three residual fit regimes, four windows per regime, and 12 regime-floor source bounds. Of 54 variants, 28 are available and 26 unavailable. Three USDJPY 5m / 60m variants at budgets 250/500/1000 pass the aggregate gate but their window counts `0/0/0/250`, `0/0/7/493`, and `0/3/72/925` all fail temporal stability. No cell is selected; validation and holdout remain locked; accepted model candidate count is zero. No rerun/retry/replacement is authorized. The next safe gate is post-result diagnostic analysis only; promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-241 compares closed EXP-058 against successful EXP-057. Variant accounting and aggregate-pass identity are unchanged, but the fit-regime-floor layer changes candidate identity in 27 of 28 available variants and changes aggregate 0.5-pip financial mix (14 improved, 13 worsened, 1 unchanged). The three aggregate-pass variants remain USDJPY 5m / 60m at budgets 250/500/1000, with window counts `0/0/0/250`, `0/0/7/493`, and `0/3/72/925`; all fail temporal stability and accepted model candidate count remains zero. EXP-058 rerun/replacement and all gate-relaxation, selection-outcome tuning, successor fit/execution, promotion, shadow/demo, broker, live-order, real-money, and trading paths remain locked. Only successor protocol source design is open.


DEC-242 opens source-only EXP-059 after DEC-241 shows that regime-floor ranking changes candidate identities and financial mix without creating temporal stability. EXP-059 reuses the same three frozen fit-regime means and defines regime-balance utility as arithmetic mean minus exactly 1.0 times the regime range. Ranking places this score ahead of the retained regime-floor/lower-tail/breadth/residual-bound/support stack and freezes a nine-part cutoff. No new references, selection-window outcomes, gate changes, chronology changes, model fit, historical execution, promotion, shadow/demo, broker, live-order, real-money, or trading paths are opened. The next safe gate is a deterministic in-memory EXP-059 training/evaluation core only.


DEC-243 implements the full deterministic in-memory EXP-059 regime-balance cell core against merged DEC-242. It preserves the EXP-058 model/data/chronology/reference/financial/stability/forward stack and adds only a fit-only balance score from the same three frozen fit-regime means: arithmetic mean minus exactly 1.0 times max-minus-min. The core independently recomputes the retained regime floor and fails closed unless it exactly matches the predecessor value. Ranking becomes regime-balance first followed by the unchanged regime-floor/lower-tail/breadth/residual-bound/support/calibration/raw stack, with a nine-part cutoff. No artifact loading, readiness execution, workflow dispatch, model-result execution, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading is opened. The next safe gate is a non-executable EXP-059 artifact/evidence contract only.


DEC-244 freezes the non-executable EXP-059 artifact/evidence contract against merged DEC-243. It validates exact 18-cell evidence, deterministic cell fingerprints, 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, the twelve-bound residual-breadth inventory, twelve-bound lower-tail source inventory, lower-tail count 3, three fit regimes, four residual windows per regime, twelve regime-floor source bounds, three regime-balance source regimes, twelve regime-balance source bounds, fixed penalty multiplier 1.0, and nine-part regime-balance/regime-floor/lower-tail/breadth/residual-bound/support cutoffs. The authoritative bundle remains fail-closed before execution. No workflow dispatch, historical result execution, model fit, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading is authorized. The next gate is a manual-main EXP-059 workflow/CLI/runtime source freeze with execution still closed.


DEC-245 freezes the manual-main/input-free EXP-059 workflow, public CLI, Python 3.12.14 numerical runtime, and exact-source execution gate against merged DEC-242/243/244. The workflow preserves the exact nine pair/timeframe datasets, 60m/240m horizons, frozen feature/outcome/readiness artifacts, partial cell evidence, and aggregate evidence, but has no first-run guard yet. The CLI requires authorization before readiness/artifact loading or regime-balance model execution and has no direct dispatch path. Model-run dispatch, historical result execution, model-protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a predeclared attempt-1 terminal-review contract only.


DEC-246 predeclares exact attempt-1 terminal review for any later separately authorized EXP-059 historical run. Success requires the exact manual-main regime-balance workflow, all 11 jobs successful, all nine non-expired cell artifacts plus the aggregate artifact, and deterministic DEC-244 revalidation of complete 18-cell / 108-regressor / 108-pooled-reference / 432-utility-support-reference / 216-feature-support-reference / 432-residual-reference evidence plus 12 breadth bounds, 12 lower-tail bounds, lower-tail count 3, three residual fit regimes, four residual windows per regime, 12 regime-floor source bounds, three regime-balance source regimes, 12 regime-balance source bounds, and penalty multiplier 1.0. Non-success may preserve only produced expected cell artifacts and opens no rerun/retry/replacement. All execution, promotion, shadow/demo, broker, live-order, real-money, and trading paths remain locked. The next safe gate is zero-prior-run proof plus a first-run guard and at most one bounded outer historical slot.


DEC-247 verifies zero exact prior EXP-059 manual-main model runs in the latest 100 Actions runs, hardens the frozen EXP-059 workflow with a first-run rejection guard, and opens exactly one outer historical-result slot without dispatching it. The guard rejects any prior manual-main EXP-059 run before result execution. Underlying protocol/core/artifact execution authorizations remain false; only the bounded outer gate exposes dispatch/result/fit for the first attempt. Any terminal outcome consumes the slot and must route through DEC-246; no rerun, retry, or replacement is authorized. Promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a clean-main double-plan one-way operator only.


DEC-248 freezes a clean-main, one-way EXP-059 operator against merged DEC-247. It requires exact clean local `main` equal to freshly fetched `origin/main`, verifies the Dtwosam/FMP origin, permits at most one exact manual-main EXP-059 workflow run, and treats only `MISSING` as dispatchable. `IN_PROGRESS` and `TERMINAL` never expose dispatch/replacement actions; terminal evidence routes through DEC-246. The public CLI provides read-only `next`, non-executing `advance`, and double-plan `advance --execute` with fail-closed state-drift checks. DEC-248 itself does not dispatch or consume the DEC-247 slot. Replacement/promotion/shadow/demo/broker/live-order/real-money/trading remain locked. The next safe gate is a repository-hosted read-only `next` plan runner only.


DEC-249 adds a repository-hosted read-only proof for the exact DEC-248 EXP-059 `next` plan. The workflow is main-push/path scoped, read-permission only, preserves a clean checkout, invokes only the public operator's read-only `next` action, writes only under runner temp, and persists the plan artifact. It cannot invoke `advance`, execute a dispatch, rerun/retry/replace a model run, or claim a result. A successful proof must show the live EXP-059 state is still `MISSING` and that only the already bounded DEC-247 first-run action is available, with all replacement/promotion/shadow/demo/broker/live/real-money/trading locks false. DEC-249 consumes no historical slot.


DEC-250 binds the successful DEC-249 merged-main read-only proof and freezes exactly one repository-hosted EXP-059 executor. The executor independently revalidates the proof run, artifact metadata, artifact ZIP digest, and plan contents, then invokes only DEC-248 `advance --execute`. It contains no direct model-workflow dispatch, rerun, retry, or replacement path. After submission it independently confirms that exactly one manual-main EXP-059 run exists on the executor merge SHA at attempt 1. If submitted, that run consumes the DEC-247 slot on any terminal outcome and must route through DEC-246. No second executor attempt or replacement model run is authorized; promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-251 closes the consumed EXP-059 historical slot after attempt-1 run `36239443323` fails on merged-main commit `8b47a025598feea1b9a382c4f0c35ac644512acc`. DEC-246 non-success review is satisfied: preflight succeeded, all nine matrix jobs failed, aggregate evidence was skipped, zero cell artifacts persisted, and no aggregate artifact/evidence exists. All nine failures share the same implementation dependency/export-depth error: the regime-balance core reads `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE` from the lower-tail-repair training module, where that symbol is not exported. EXP-059 therefore produced no model result and no evidence for or against its intended regime-balance ranking. No rerun/retry/replacement is authorized. The next safe gate is source-only implementation-defect diagnostic work; promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked.


DEC-252 performs a deterministic AST audit of the failed EXP-059 regime-balance training core and freezes the complete predecessor-depth defect inventory. Four breadth metadata names are addressed at `_predecessor._predecessor`, which resolves to the EXP-057 lower-tail-repair training module where those names are not exported; all four exist one level deeper on the frozen EXP-055 breadth core. The historical run directly observed missing `FIT_TEMPORAL_RESIDUAL_BREADTH_RULE` in all nine matrix jobs. The repair boundary is implementation-only for a future successor identity: change exactly those four accesses to `_predecessor._predecessor._predecessor.<name>` and change no regime-balance protocol/data/model/chronology/ranking/cutoff/gate semantics. EXP-059 rerun/replacement and all successor fit/execution, promotion, shadow/demo, broker, live-order, real-money, and trading paths remain closed. Only successor protocol source design is open.


DEC-253 opens EXP-060 as a source-only implementation-repair successor to failed EXP-059. It preserves the complete EXP-059 regime-balance protocol and authorizes only four predecessor-depth corrections for breadth metadata, moving those accesses from `_predecessor._predecessor` to `_predecessor._predecessor._predecessor`. No protocol semantics, model configuration, data identity, chronology, ranking, cutoff, stability, validation, or holdout rule changes. Model result production, model fit, historical execution, promotion, shadow/demo, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is the deterministic in-memory EXP-060 training/evaluation core only.


DEC-254 implements the full deterministic in-memory EXP-060 regime-balance repair core against merged DEC-253. It preserves all EXP-059 regime-balance model/evaluation semantics and changes only four breadth metadata dependency paths from two predecessor levels to three, exactly as authorized. The full cell runner, nine-part ranking/cutoff, stability gates, validation/holdout chronology, and no-refit forward application remain intact. Historical result execution, artifact loading, workflow dispatch, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a separate non-executable EXP-060 artifact/evidence contract.


DEC-255 freezes the non-executable EXP-060 artifact/evidence contract against merged DEC-254. It validates repaired EXP-060 provenance, exact protocol fingerprinting, all 18 cell identities, deterministic cell fingerprints, 108 regressors, 108 pooled references, 432 utility-support references, 216 feature-support references, 432 residual references, the inherited breadth/lower-tail/regime-floor/regime-balance inventories, penalty multiplier 1.0, and unchanged nine-part cutoffs. The authoritative bundle remains fail-closed before execution. No workflow dispatch, historical result execution, model fit, rerun/replacement, promotion, shadow/demo execution, broker mutation, live orders, real-money action, or trading is authorized. The next gate is a manual-main EXP-060 workflow/CLI/runtime source freeze with execution still closed.

DEC-256 freezes the manual-main/input-free EXP-060 repaired regime-balance workflow, public CLI, Python 3.12.14 numerical runtime, and exact-source execution gate against merged DEC-253/254/255. The workflow preserves the exact nine pair/timeframe datasets, 60m/240m horizons, frozen feature/outcome/readiness artifacts, partial cell evidence, and aggregate evidence, but has no first-run guard yet. The CLI requires authorization before readiness/artifact loading or repaired regime-balance model execution and has no direct dispatch path. Model-run dispatch, historical result execution, model-protocol result production, model fit, promotion, shadow/demo execution, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a predeclared attempt-1 terminal-review contract only.

DEC-257 predeclares exact attempt-1 terminal review for any later separately authorized EXP-060 historical run. Success requires the exact manual-main repaired regime-balance workflow, all 11 jobs successful, all nine non-expired cell artifacts plus the aggregate artifact, and deterministic DEC-255 revalidation of complete 18-cell / 108-regressor / 108-pooled-reference / 432-utility-support-reference / 216-feature-support-reference / 432-residual-reference evidence plus 12 breadth bounds, 12 lower-tail bounds, lower-tail count 3, three residual fit regimes, four residual windows per regime, 12 regime-floor source bounds, three regime-balance source regimes, 12 regime-balance source bounds, and penalty multiplier 1.0. Non-success may preserve only produced expected cell artifacts and opens no rerun/retry/replacement. All execution, promotion, shadow/demo, broker, live-order, real-money, and trading paths remain locked. The next safe gate is zero-prior-run proof plus a first-run guard and at most one bounded outer historical slot.

DEC-258 proves the exact EXP-060 workflow has zero prior runs, adds a runtime first-run guard that also requires GitHub `run_attempt == 1`, and opens exactly one bounded outer historical-result slot without dispatching it. The underlying DEC-253/254/255 repair protocol/core/artifact authorization remains false; all promotion, shadow/demo, broker, live-order, real-money, and trading paths remain locked. The next safe gate is the clean-main, double-plan, one-way EXP-060 operator.

DEC-259 freezes the clean-main one-way EXP-060 operator against merged DEC-258. It requires exact current `main`, exact fetched `origin/main`, a clean working tree, the correct repository remote, and the exact DEC-258/257 source-gate and terminal-review identities. Live state is one-way and attempt-1-only: any `run_attempt != 1` fails closed, and only `MISSING` may produce the single frozen dispatch command; `IN_PROGRESS` and `TERMINAL` cannot dispatch or replace a run, and terminal state routes through DEC-257. The operator double-plans immediately before any explicit execution request and fails closed on drift. DEC-259 does not dispatch. Promotion, shadow/demo, broker, live-order, real-money, and trading paths remain locked. The next safe gate is a repository-hosted read-only `next` plan proof on merged main.

DEC-260 adds a repository-hosted, push-to-main, read-only proof for the exact DEC-259 EXP-060 operator `next` plan. It verifies merged-main cleanliness, zero existing EXP-060 manual-main runs, `MISSING` state, and the exact one-shot dispatch command as evidence only; it cannot invoke `advance`, dispatch, rerun, retry, replace, or claim a result. All downstream promotion, shadow/demo, broker, live-order, real-money, and trading paths remain locked. The next safe gate is to merge DEC-260, require its merged-main proof workflow to succeed, bind that exact non-expired plan artifact, and only then consider a separate one-shot executor.

DEC-261 binds the successful merged-main DEC-260 read-only proof and adds a one-shot repository-hosted EXP-060 executor. The executor can invoke only the already-frozen DEC-259 double-plan `advance --execute` path after independently revalidating the exact proof run, non-expired artifact, digest, and plan contents. It contains no independent dispatch/rerun/retry/replacement path. If merged and its push workflow succeeds, exactly one guarded manual-main EXP-060 historical model run may be submitted and the DEC-258 slot is consumed on any terminal outcome. All promotion, shadow/demo, broker, live-order, real-money, and trading paths remain locked; terminal outcome must route through DEC-257.

DEC-262 freezes the sole successful EXP-060 historical result. Run `36260155597` completed attempt 1 successfully with all nine model-cell jobs and aggregate evidence successful. Deterministic evidence verifies the full repaired regime-balance inventory but selects no stable model challenger: only USDJPY/5m/60m budgets 500 and 1000 pass the aggregate gate, and both fail temporal stability. All 18 cells remain unselected; validation and holdout stay locked; accepted model candidate count is zero. EXP-060 is closed with no rerun/retry/replacement authority. Promotion, Phase 8B shadow, demo, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a source-only Phase 8A post-result/acceptance assessment.

DEC-263 closes the direct market-learning branch as a credible negative research answer but keeps Phase 8A active. EXP-060 is immutable and closed. The remaining unresolved Phase 8A branch is DEC-043 / EXP-20260922-015 rule-based challenger discovery: Stage A has 12 preserved source-development failure runs but no authoritative manual-main historical attempt; Stage B and Stage C have zero runs. DEC-042 portfolio selection and DEC-045 Phase 8A acceptance therefore remain blocked. The next safe gate is source-only Stage A execution governance with an exact attempt-1 review contract, zero-authoritative-run proof, first-run guard, and at most one bounded historical slot. No Stage A dispatch is authorized by DEC-263; Phase 8B, demo, broker mutation, live orders, real-money action, and trading remain locked.

DEC-264 modernizes EXP-015 Stage A execution governance without changing DEC-043/044 research semantics. The workflow now rejects any prior authoritative manual-main attempt, requires exact current-main identity and run_attempt 1, and preserves the 12 old failed push/development runs outside the authoritative slot count. Attempt-1 terminal review is predeclared and requires the exact 11-job/11-artifact success shape plus deterministic 567-strategy authorization evidence. One bounded Stage A historical-result slot is open in governance only; DEC-264 does not dispatch it. Stage A retry/replacement, Stage B/C, DEC-042 selection, DEC-045 acceptance, Phase 8B, demo, broker mutation, live orders, real-money action, and trading remain locked. The next safe gate is a clean-main read-only one-way Stage A operator decision.

DEC-265 adds a clean-main, read-only one-way operator for the sole DEC-264 EXP-015 Stage A slot. It classifies only MISSING, IN_PROGRESS, or TERMINAL manual-main state, ignores the 12 preserved development push failures, and exposes the exact Stage A command only as plan evidence when the slot is still MISSING. Stage A dispatch/executor/retry/replacement authority remains false in every operator report. IN_PROGRESS exposes no dispatch plan; TERMINAL routes to the frozen DEC-264 terminal review. The next safe gate is a repository-hosted read-only proof of the exact DEC-265 `next` plan on merged main; Stage B/C, DEC-042 selection, DEC-045 acceptance, Phase 8B, demo, broker mutation, live orders, real-money action, and trading remain locked.

DEC-266 adds a repository-hosted, push-to-main, read-only proof for the exact DEC-265 EXP-015 Stage A `next` plan. It verifies exact DEC-264 workflow/reviewer and DEC-265 operator/CLI blobs, uses a minimal pinned Polars runtime without editable installation, requires the checkout to stay clean, and invokes only the `next` planner. A successful proof must show zero authoritative manual-main Stage A runs, MISSING state, the sole slot still available, and the exact future Stage A command as plan evidence only while every dispatch/executor/downstream field remains false. DEC-266 consumes no slot. The next safe gate is to merge DEC-266, bind its successful merged-main plan artifact, and only then consider a separately reviewed one-shot Stage A executor.
