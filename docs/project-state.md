# FMP Project State

**Updated:** 2026-09-23
**Repository:** `Dtwosam/FMP`  
**V1 scope:** Forex only  
**Current phase:** Phase 8A — Multi-pair, multi-strategy portfolio research
**Phase status:** ACTIVE — EXP-044 V1 CLOSED + EXP-045 CLOSED/REVIEWED + EXP-046 PROTOCOL/CORE/ARTIFACT/WORKFLOW SOURCES FROZEN THROUGH DEC-107; NO EXP-046 AUTHORITATIVE FIT OR RESULT
**Next milestone:** Merge DEC-107's locked EXP-046 workflow/CLI/execution-gate source, then predeclare terminal-result review before any historical-run authorization is considered. A later authorization decision must add a prior-run rejection guard before opening at most one result-producing run. No authoritative EXP-046 model fit, historical result execution, workflow run, promotion, shadow/demo execution, broker mutation, live orders, real-money trading, or trading authorization is authorized.

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

Phase 8 is not PASS. Phase 8B source-free preparation is active under DEC-046 through DEC-049. EXP-044 feature and outcome data-preparation workflows completed successfully. One guarded EXP-044 V1 model-training workflow, run `35891605645`, executed under DEC-093 and failed; DEC-094 reviews that failure, records zero persisted model artifacts and no aggregate model result, and closes V1 execution without rerun or replacement authorization. DEC-095 through DEC-101 freeze and authorize the single guarded EXP-045 historical model run. Run `35911916239` completed successfully at `6d42a5053c5f2f696071715640dab24973a40517`; DEC-102 records no accepted model challenger and DEC-103 freezes the post-result diagnostic. DEC-104 opens source-only `EXP-20260923-046` with a four-window temporal-stability selection screen, DEC-105 implements its deterministic source-only training core, DEC-106 freezes the artifact-backed runner/aggregate evidence contract, and DEC-107 freezes the manual workflow/CLI/execution-gate source while keeping all execution authorization closed. No EXP-046 result-producing workflow run has occurred. Promotion/shadow/demo/broker/live/real-money/trading paths remain locked. No prospective shadow campaign has begun.

