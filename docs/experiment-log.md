# FMP Experiment Log

This file is the human-readable experiment registry until/unless a machine-readable registry is introduced. Do not delete failed experiments.

## Experiment ID format

`EXP-YYYYMMDD-NNN`

Example: `EXP-20260903-001`

## Required experiment record

Copy this section for each serious experiment:

```markdown
### EXP-YYYYMMDD-NNN — Short descriptive name

- Date:
- Status: PLANNED | RUNNING | PASS | FAIL | INCONCLUSIVE
- Hypothesis:
- Code commit:
- Data manifest/version:
- Pair(s):
- Timeframe(s):
- Data range:
- Train period:
- Validation period:
- Final-test touched?: NO
- Strategy/model:
- Features:
- Parameters/search space:
- Random seed (if relevant):
- Spread/cost model:
- Slippage model:
- Risk assumptions:
- Trade count:
- Net return after costs:
- Expectancy/trade:
- Profit factor:
- Max drawdown:
- Key subperiod results:
- Robustness/cost sensitivity:
- Result summary:
- Conclusion: PROMOTE | REJECT | REVISE | NEED_MORE_DATA
- Reason:
- Follow-up:
```

## Registry

### EXP-20260914-001 — Session breakout baseline

- Date: 2026-09-14
- Status: PASS
- Hypothesis: After a completed pre-London range, a confirmed break during the early London session may exhibit enough short-horizon continuation on some V1 pair/timeframe combinations to overcome historical spread and adverse slippage under fixed-risk execution. No profitability was assumed.
- Code commit: `cc01929b80cbd1d5619de8476caa8f3d3410262e`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; this experiment loaded development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic `session_breakout` baseline, `Europe/London`; range 00:00–08:00, breakout observation 08:00–12:00, exact mandatory flat timestamp 16:00 local; first qualifying breakout only.
- Features: midpoint OHLC only for range/signal analysis; Phase 3 historical BID/ASK execution remained the sole fill/PnL source of truth.
- Parameters/search space: `buffer_pips = {0, 2, 5}` × `target_range_multiple = {0.5, 1.0, 1.5}`; exactly 9 predeclared configurations per pair/timeframe and no post-result expansion under this experiment ID.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: 0.25% requested; 0.50% hard per-trade max; 1.00% simultaneous max; 1.50% UTC day-start realized-loss halt; accepted Phase 3 sizing/execution rules unchanged.
- Trade count: frozen serious candidate USDJPY 15m, 5-pip buffer, 1.5x target: 620 development trades and 362 validation trades.
- Net return after costs: at 0.2-pip slippage, +5.8023% development and +3.7076% validation for the frozen serious candidate.
- Expectancy/trade: at 0.2-pip slippage, +$9.3585 development and +$10.2421 validation.
- Profit factor: at 0.2-pip slippage, 1.1477 development and 1.1449 validation.
- Max drawdown: at 0.2-pip slippage, 2.9370% development and 2.9860% validation.
- Key subperiod results: selected-candidate yearly net PnL at 0.2-pip slippage was 2015 -$1,025.12, 2016 +$2,794.76, 2017 -$870.72, 2018 +$975.35, 2019 +$7.88, 2020 +$3,920.14; validation was 2021 -$1,308.81, 2022 +$4,595.37, 2023 +$421.08. About 91.6% of validation gross positive PnL occurred in 2022, a material concentration weakness.
- Robustness/cost sensitivity: all three USDJPY 15m target-1.5 buffer neighbors remain positive on both splits at 0.5-pip slippage; the same 5-pip / 1.5x point also remains positive on both splits at 5m and 1h under 0.5-pip slippage. The selected USDJPY 15m point is +3.4625% development / +2.5224% validation at 0.5 pips. At 1.0 pip it is -0.3228% development / +0.5769% validation, and no configuration in the full experiment remains positive on both splits at 1.0-pip stress.
- Result summary: merged-main run `34848137086` completed SUCCESS. All 18/18 matrix artifacts and 486/486 configuration rows were independently inspected with zero ZIP, manifest, code/data identity, grid, candidate-reuse, or accounting discrepancies. At 0.5-pip stress exactly nine configurations remain positive on both development and validation, all USDJPY. GBPUSD has two baseline 5m target-1.5 points positive on both splits but neither survives 0.5-pip stress; EURUSD has no baseline configuration positive on both splits.
- Conclusion: PROMOTE
- Reason: promote the frozen USDJPY 15m, 5-pip buffer, 1.5x target configuration as a serious Phase 4 candidate because development and validation agree, neighboring parameter points show support, moderate 0.5-pip cost stress survives, and the same parameter point has cross-timeframe support. Promotion is limited by 1.0-pip cost failure and material 2022 validation concentration.
- Follow-up: retain this candidate unchanged, proceed to the next predeclared Phase 4 family, trend continuation, and keep the 2024-01-01 through 2026-08-20 final-test period untouched until candidate selection across the admitted baseline program is materially complete. This conclusion does not make Phase 4 PASS, start Phase 5, authorize broker/live integration, or unlock real-money trading. Detailed evidence is in `docs/phase4-session-breakout-evidence.md`.

### EXP-20260914-002 — Trend continuation baseline

- Date: 2026-09-14
- Status: FAIL
- Hypothesis: During the London trading day, a pullback that temporarily crosses a short trend average and then resumes in the direction of an established multi-hour trend may have enough continuation to overcome historical BID/ASK spread and adverse slippage under fixed-risk execution. No profitability was assumed.
- Code commit: `d1c821cb8b4bfaaddbc334fee0f2f3b1dfe054a2`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; this experiment loaded development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic London-session trend-continuation baseline; signals observed on fully closed bars from 08:00 through 14:00 `Europe/London`, first qualifying signal only, exact mandatory flat timestamp 16:00 local.
- Features: midpoint OHLC only for SMA context, pullback/resumption detection, three-bar structural stop, and frozen R-target geometry; Phase 3 historical BID/ASK execution remained the sole fill/PnL source of truth.
- Parameters/search space: trend windows `2h/8h`, `4h/16h`, `8h/32h` × target `{1.0R, 1.5R}`; exactly 6 strategy configurations per pair/timeframe and no post-result parameter expansion under this experiment ID.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: 0.25% requested; 0.50% hard per-trade max; 1.00% simultaneous max; 1.50% UTC day-start realized-loss halt; accepted Phase 3 sizing/execution rules unchanged.
- Trade count: no promoted candidate; the full frozen matrix is preserved in the benchmark artifacts and detailed evidence.
- Net return after costs: no candidate-level value because no configuration passed the development-to-validation promotion screen. Strongest split-only baseline example was GBPUSD 1h `8h/32h / 1.5R`: +14.8309% development versus -2.7022% validation.
- Expectancy/trade: no promoted candidate; that same split-only GBPUSD 1h point was +$24.7595 development versus -$8.5784 validation.
- Profit factor: no promoted candidate; that same split-only GBPUSD 1h point was 1.2294 development versus 0.9251 validation.
- Max drawdown: no candidate-level value; the split-only GBPUSD 1h point had 3.3801% development max drawdown and 7.4834% validation max drawdown.
- Key subperiod results: split instability dominates. EURUSD validation had zero baseline qualifiers on all three timeframes. GBPUSD development produced isolated 15m/1h positives that did not persist into validation. USDJPY 15m reversed the other way: zero development qualifiers but two validation qualifiers, with `2h/8h / 1.5R` reaching +9.2320% in validation.
- Robustness/cost sensitivity: matched development↔validation survivors are zero for every pair/timeframe at 0.2-pip baseline slippage, and remain zero at 0.5-pip and 1.0-pip stress. Cost stress therefore cannot rescue the missing temporal agreement.
- Result summary: merged-main run `34863705913` completed SUCCESS on exact commit `d1c821cb8b4bfaaddbc334fee0f2f3b1dfe054a2`. All 18/18 matrix artifacts and 324/324 configuration rows were independently inspected with zero ZIP, manifest, code/data identity, split, grid, candidate-reuse, or accounting discrepancies.
- Conclusion: REJECT
- Reason: no frozen configuration achieved positive net return, positive expectancy, and profit factor above one on both development and validation even at baseline 0.2-pip adverse slippage. Split-only winners reverse across chronology and fail the predeclared temporal-robustness requirement.
- Follow-up: retain the frozen USDJPY 15m session-breakout candidate unchanged and proceed to the next predeclared Phase 4 family, mean reversion. Keep the 2024-01-01 through 2026-08-20 final-test period untouched. This rejection does not make Phase 4 PASS, start Phase 5, authorize broker/live integration, or unlock real-money trading. Detailed evidence is in `docs/phase4-trend-continuation-evidence.md`.

### EXP-20260914-003 — Mean reversion baseline

- Date: 2026-09-14
- Status: FAIL
- Hypothesis: Fresh intraday displacement from a preceding rolling midpoint-close distribution may revert toward its pre-existing mean strongly enough to overcome historical spread and adverse slippage under fixed-risk execution. No profitability was assumed.
- Code commit: `87003a3982ca61eb6fd030c5291616d98dbb0c1a`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic London-session mean-reversion baseline using preceding-N midpoint-close population mean/std, fresh z-score excursions, first signal only, and exact 16:00 Europe/London flat.
- Features: midpoint close, rolling mean, rolling population standard deviation, and current/previous z-score; Phase 3 historical BID/ASK execution remained authoritative.
- Parameters/search space: lookbacks 4h/8h/16h × fresh-excursion thresholds 1.5σ/2.0σ; exactly 6 configurations per pair/timeframe.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: accepted Phase 3 policy unchanged: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.
- Trade count: no promoted candidate; full 324-row matrix retained in evidence.
- Net return after costs: no promoted candidate; all 54 development and all 54 validation baseline rows were negative.
- Expectancy/trade: no promoted candidate; all baseline rows were negative on both splits.
- Profit factor: no promoted candidate; development range 0.6150–0.9596 and validation range 0.5396–0.9582 at baseline.
- Max drawdown: no candidate-level value; fixed-risk drawdowns remain in benchmark evidence.
- Key subperiod results: the family failed broadly rather than through one isolated chronology reversal.
- Robustness/cost sensitivity: zero baseline survivors; 0.5/1.0-pip rows remain diagnostic evidence only and cannot rescue the family.
- Result summary: merged-main benchmark run `34875463677` completed SUCCESS; 18/18 artifacts and 324/324 rows independently verified with zero integrity/identity/grid/candidate-reuse/accounting errors.
- Conclusion: REJECT
- Reason: zero of 54 pair/timeframe/lookback/threshold points achieved positive net return, positive expectancy, and PF > 1 on both development and validation at 0.2-pip baseline.
- Follow-up: retain EXP-001 unchanged; no post-result expansion; final-test remains locked. Detailed evidence: `docs/phase4-mean-reversion-evidence.md`.

### EXP-20260914-004 — Previous-day high/low rejection baseline

- Date: 2026-09-14
- Status: FAIL
- Hypothesis: Penetration beyond the previous completed New-York-close FX session high/low followed by a close back inside may revert toward the frozen previous-day midpoint strongly enough to overcome costs. No profitability was assumed.
- Code commit: `7db3a747236942fa393521e5866e3245d1a22a99`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic previous-day high/low rejection using the most recent completed New-York-close FX session, first directional rejection only, and exact 16:00 Europe/London flat.
- Features: previous-day midpoint high/low/midpoint and current midpoint penetration/rejection; Phase 3 BID/ASK execution.
- Parameters/search space: penetration buffers 0/2/5 pips; no post-result expansion.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: accepted Phase 3 policy unchanged: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.
- Trade count: sole baseline survivor USDJPY 5m / 5-pip buffer had 29 development and 28 validation trades.
- Net return after costs: +4.0039% development and +0.0657% validation for the sole baseline survivor at 0.2 pips.
- Expectancy/trade: +$138.0644 development and +$2.3461 validation.
- Profit factor: 1.9002 development and 1.0133 validation.
- Max drawdown: 2.0245% development and 1.7179% validation.
- Key subperiod results: validation negative in 2021 and 2022 and positive only in 2023; top three winners contributed about 85.38% of validation positive R.
- Robustness/cost sensitivity: validation turned negative at 0.5-pip slippage; neighboring 0/2-pip buffers were negative on both splits; 1.0-pip validation also failed.
- Result summary: merged-main benchmark run `34883815436` completed SUCCESS; 18/18 artifacts and 162/162 rows independently verified with zero integrity/identity/grid/candidate-reuse/accounting errors.
- Conclusion: REJECT
- Reason: the only baseline survivor was thin, isolated, cost-sensitive, chronologically concentrated, and winner-dependent, failing the predeclared robustness review.
- Follow-up: no candidate promoted and no rescue search authorized. Detailed evidence: `docs/phase4-previous-day-rejection-evidence.md`.

### EXP-20260914-005 — Rolling volatility-breakout baseline

- Date: 2026-09-14
- Status: PASS
- Hypothesis: A close outside a preceding rolling 8h midpoint channel accompanied by contemporaneous range expansion may continue far enough to overcome historical spread and adverse slippage. No profitability was assumed.
- Code commit: `3bf36186900f5065e9e3ddced0305865433b9d69`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic rolling 8h volatility breakout; strict close beyond rolling channel plus current range expansion; first signal only; signal-bar extreme stop; fixed 1.0R target; exact 16:00 Europe/London flat.
- Features: rolling midpoint high/low, median reference bar range, current midpoint range, and expansion multiple.
- Parameters/search space: range-expansion multipliers 1.0x/1.5x/2.0x; fixed 1.0R target.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: accepted Phase 3 policy unchanged: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.
- Trade count: promoted USDJPY 1h / 2.0x point had 596 development and 364 validation trades.
- Net return after costs: +11.4235% development and +5.5971% validation at 0.2 pips.
- Expectancy/trade: +$19.1670 development and +$15.3766 validation.
- Profit factor: 1.2321 development and 1.1931 validation.
- Max drawdown: 2.5228% development and 1.9853% validation.
- Key subperiod results: all six development years positive; validation negative in 2021 but positive in 2022 and 2023; top-three winner dependence about 1.30% development and 2.22% validation positive R.
- Robustness/cost sensitivity: survives 0.5-pip stress on both splits but fails 1.0-pip diagnostic; neighboring multipliers and adjacent timeframes do not confirm the development edge.
- Result summary: merged-main benchmark run `34888225242` completed SUCCESS; 18/18 artifacts and 162/162 rows independently verified; exactly one of 27 baseline points survived: USDJPY 1h / 2.0x.
- Conclusion: PROMOTE
- Reason: the exact predeclared point clears both chronological splits, survives required 0.5-pip stress, has a substantial sample and low drawdown, broad development-year support, and very low top-winner dependence despite parameter/timeframe isolation and 2021 weakness.
- Follow-up: freeze USDJPY 1h / 2.0x / fixed 1.0R as the second serious Phase 4 candidate alongside EXP-001. Detailed evidence: `docs/phase4-volatility-breakout-evidence.md`.

### EXP-20260914-006 — Session high/low sweep-rejection baseline

- Date: 2026-09-14
- Status: FAIL
- Hypothesis: Intrabar penetration beyond the frozen 00:00–08:00 Europe/London session high/low followed by a strict close back inside may revert toward the frozen session midpoint strongly enough to overcome costs. No profitability was assumed.
- Code commit: `120348d4a5df806f674551590610b216a9bc33ac`
- Data manifest/version: accepted Phase 2 processed manifests, schema `fmp-canonical-1m-v1`; EURUSD `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`, GBPUSD `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`, USDJPY `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Data range: accepted Phase 2 coverage 2015-01-01 through 2026-08-20 inclusive; development and validation only.
- Train period: 2015-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive
- Final-test touched?: NO
- Strategy/model: deterministic session high/low sweep-rejection; frozen 00:00–08:00 Europe/London midpoint range; strict rejection back inside; first signal only; signal-bar extreme stop; session-midpoint target; exact 16:00 flat.
- Features: frozen session midpoint high/low/midpoint and current midpoint sweep/rejection state.
- Parameters/search space: penetration buffers 0/2/5 pips; no alternate session or rescue grid.
- Random seed (if relevant): not applicable; deterministic strategy and backtester.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2, 0.5, 1.0 pips per fill, adverse on every execution side.
- Risk assumptions: accepted Phase 3 policy unchanged: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.
- Trade count: no promoted candidate; clearest split-only point USDJPY 5m / 2 pips had 337 development and 240 validation trades.
- Net return after costs: that point reversed from +1.9167% development to -15.4056% validation at baseline.
- Expectancy/trade: +$5.6874 development versus -$64.1899 validation.
- Profit factor: 1.0282 development versus 0.6706 validation.
- Max drawdown: 7.6380% development versus 16.7821% validation.
- Key subperiod results: zero of 27 pair/timeframe/buffer points cleared the required development-and-validation gate; two USDJPY 1h validation-only qualifiers failed development.
- Robustness/cost sensitivity: no baseline survivor, so downstream cost rows cannot rescue any point and remain evidence only.
- Result summary: merged-main benchmark run `34895426037` completed SUCCESS; 18/18 artifacts and 162/162 rows independently verified with zero ZIP/manifest/identity/grid/candidate-reuse/accounting/cost/risk errors.
- Conclusion: REJECT
- Reason: no exact predeclared buffer achieved positive net return, positive expectancy, and PF > 1 on both development and validation at 0.2-pip baseline.
- Follow-up: promote nothing; retain EXP-001 and EXP-005 candidates frozen unchanged. This completes all six planned Phase 4 baseline families. Detailed evidence: `docs/phase4-session-sweep-rejection-evidence.md`.

### EXP-20260915-007 — Phase 6 statistical / ML candidate filters

- Date: 2026-09-15
- Status: PASS
- Hypothesis: A predeclared supervised outcome model may filter lower-quality entries from either frozen Phase 4 serious rule candidate and improve financial quality without changing the strategy, execution, or fixed-risk contract. No model improvement was assumed.
- Code commit: `2dccb0f00d2a443bc41646ac1b3b494d81e1f13c`
- Data manifest/version: Phase 5 `fmp-feature-v1` checkpoint `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`; accepted USDJPY processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`; authoritative Phase 5 USDJPY 15m artifact `10374600839` ZIP `2e9b19935fc2699c94e5c3b91675c332892da9448e994438e479cf501e3c6215`; USDJPY 1h artifact `10374645600` ZIP `3db4d9d4fd4613c9e91f4c3fc1d815750038e33ea993608513066cec53aa617f`.
- Pair(s): USDJPY
- Timeframe(s): 15m session breakout and 1h volatility breakout
- Data range: accepted pre-2024 data only; fit 2015-2018 and selection 2019-2020 were opened. The predeclared 2021-2023 validation split remained unopened because neither strategy produced a qualifying selection-period challenger.
- Train period: fit 2015-01-01 through 2018-12-31 inclusive; selection 2019-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive, gated and not opened
- Final-test touched?: NO
- Strategy/model: unchanged USDJPY 15m session-breakout 5-pip/1.5x rule and USDJPY 1h volatility-breakout 2.0x/1.0R rule; exact L2 logistic regression and shallow histogram gradient boosting challengers.
- Features: exactly 48 frozen `fmp-feature-v1` values plus signal direction; exact observation/availability join; no outcome/PnL/future feature input.
- Parameters/search space: exactly two model families × retained fractions 0.75, 0.50, and 0.25 per strategy; cutoffs derived from fit scores only; no post-result widening, extra model, or rescue search.
- Random seed (if relevant): `20260915`
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2 pips per fill for selection; 0.5-pip validation robustness only for a selected challenger; 1.0 pip diagnostic only. Validation was not opened because no challenger survived selection.
- Risk assumptions: unchanged Phase 3 contract: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.
- Trade count: selection rule baselines were 192 session-breakout trades and 222 volatility-breakout trades; no filtered candidate was promoted.
- Net return after costs: selection rule baselines were +3.8558% session breakout and +3.8457% volatility breakout at 0.2-pip adverse slippage. No session ML variant was fit; all six volatility filtered variants were below the volatility baseline net return.
- Expectancy/trade: selection rule baselines +$20.0822 session breakout and +$17.3228 volatility breakout. Best volatility filtered expectancy was +$21.0354 for logistic 0.50, but that variant still failed the all-conditions gate because its +2.7136% net return was below baseline.
- Profit factor: selection rule baselines 1.3010 session breakout and 1.2014 volatility breakout. No session model fit; volatility filtered PF ranged 0.9703 to 1.2101 and did not produce a qualifying all-conditions variant.
- Max drawdown: selection rule baselines 1.4390% session breakout and 1.4105% volatility breakout; drawdown improvement alone could not rescue a variant that failed another frozen selection condition.
- Key subperiod results: no validation subperiod result exists because DEC-031 forbids validation from rescuing a strategy without a qualifying selection-period challenger.
- Robustness/cost sensitivity: validation and the 0.5-pip robustness gate remained unopened for both strategies; no 1.0-pip diagnostic result was used.
- Result summary: authoritative run `34966406652` completed SUCCESS with double execution, byte-identical evidence, and locked pre-2024 coverage. Session breakout failed closed for both models on `ALL_NULL_FIT_COLUMN` / `minutes_since_new_york_open`, leaving all six variants not evaluated. Volatility breakout fit both models once, but all six variants failed selection and every variant had `net_return_beats_baseline = false`. Audited artifacts are session `10395810196` / ZIP `36cb9f80ca043da23250669dd974036eb9fb985c3f7f9ffd7844b9d99c96073d` and volatility `10395670751` / ZIP `0cf71a4d725fb1e609a512bb95aa13e4ad8771ae2b5864dd09e2833fe160a8d2`.
- Conclusion: REJECT
- Reason: neither frozen strategy produced a valid ML challenger under the predeclared selection protocol; `NO_ML_CHALLENGER` is the authoritative outcome for both.
- Follow-up: retain both frozen Phase 4 rule candidates unchanged, close Phase 6 as PASS because the deterministic leakage-safe experiment completed correctly with negative evidence preserved, create `fmp-v1-phase6-models` only after verified acceptance-closure merge, keep Phase 7 UNSTARTED, and keep the final-test period locked. Detailed evidence: `docs/phase6-ml-filter-evidence.md`.

### EXP-20260915-008 — Phase 7 walk-forward evaluation

- Date: 2026-09-15
- Status: PASS
- Hypothesis: Either frozen Phase 4 serious rule candidate may retain positive, cost-robust expectancy through a one-shot untouched 2024 out-of-sample gate and repeated 2025-2026 forward windows without parameter retuning or ML filtering. No viability was assumed.
- Code commit: Stage 1 `e33270de1f89757d1bf2a0d12ef40b2dc36bc110`; Stage 2 `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d`.
- Data manifest/version: Phase 6 checkpoint `fmp-v1-phase6-models` / `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`; accepted Phase 2 USDJPY artifact `10327600628`, ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`; accepted USDJPY processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Pair(s): USDJPY
- Timeframe(s): 15m session breakout and 1h volatility breakout
- Data range: Stage 1 opened bounded 2023-12 warm-up context plus scored 2024; Stage 2 for the sole survivor opened only the exact seven frozen forward windows plus each immediate seven-day warm-up, covering scored 2025-01-01 through 2026-08-20 inclusive.
- Train period: not applicable; both strategies are fixed rules and no Phase 7 refit or optimization is authorized.
- Validation period: Stage 1 one-shot OOS gate 2024-01-01 through 2024-12-31; Stage 2 seven frozen independent forward windows 2025-Q1 through 2026-partial-Q3 for the sole Stage 1 survivor.
- Final-test touched?: YES — Stage 1 2024 and Stage 2 2025-2026
- Strategy/model: unchanged USDJPY 15m session breakout, 5-pip buffer, 1.5x target range; unchanged USDJPY 1h volatility breakout, 2.0x range expansion, fixed 1.0R target; no ML overlay.
- Features: existing strategy-native midpoint OHLC/reference logic only; historical BID/ASK remains the execution source of truth; Phase 5 model features are not used.
- Parameters/search space: no search space. Candidate identities and parameters remained frozen exactly; no neighboring-parameter substitution, rescue search, candidate replacement, or post-result threshold change.
- Random seed (if relevant): not applicable; deterministic fixed-rule evaluation.
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: exactly 0.2, 0.5, and 1.0 pips adverse per fill; 0.2 and 0.5 are gating, 1.0 is diagnostic only.
- Risk assumptions: unchanged Phase 3 contract: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt; every Stage 1/Stage 2 evaluation window starts independently at $100,000 as specified.
- Trade count: Stage 1 `session_breakout` 122 trades at each cost and `volatility_breakout` 103 trades at each cost. Stage 2 `session_breakout` completed 199 trades across the seven independent windows at each cost.
- Net return after costs: Stage 1 `session_breakout` +1.383287% / +1.102509% / +0.636234% at 0.2 / 0.5 / 1.0 pips; Stage 1 `volatility_breakout` -2.603768% / -3.051558% / -3.793353%. Stage 2 `session_breakout` aggregate +0.757266% at 0.2 pips and +0.262176% at 0.5 pips; the 1.0-pip diagnostic is -0.562118%.
- Expectancy/trade: Stage 2 `session_breakout` +$3.8054 at 0.2 pips and +$1.3175 at 0.5 pips; 1.0-pip diagnostic -$2.8247.
- Profit factor: Stage 2 `session_breakout` 1.062731 at 0.2 pips and 1.021310 at 0.5 pips; 1.0-pip diagnostic 0.955760.
- Max drawdown: Stage 2 maximum independent-window drawdown 1.140640% at 0.2 pips, 1.170046% at 0.5 pips, and 1.219045% in the 1.0-pip diagnostic.
- Key subperiod results: at 0.2 pips, five of seven Stage 2 windows have positive net PnL. The two negative windows are 2025-Q1 (-0.520185%) and 2026-partial-Q3 (-0.645978%). The maximum positive-window contribution is 35.061843%, below the frozen 50% concentration ceiling.
- Robustness/cost sensitivity: Stage 2 remains positive with PF > 1, positive expectancy, and sub-5% drawdown at both mandatory 0.2- and 0.5-pip costs. The negative 1.0-pip diagnostic is retained as material cost-sensitivity evidence and does not change the frozen outcome because DEC-033 explicitly defines it as non-gating.
- Result summary: Stage 1 run `35013047267` produced `session_breakout` `STAGE1_PASS` artifact `10414407590` / ZIP `d9950ceb37188761a3460df7b4ab75463cdf1c19ce42634d910d33bae3f8c8bb` and `volatility_breakout` `STAGE1_REJECT` artifact `10414905151` / ZIP `5ee8b6b96382741f454d2b72a6ae6de04e85c9eca04c17ac846c0d594fd27d24`. Authoritative Stage 2 run `35015277625` on exact merged-main SHA `a1f8a0466463c79fdbceb9d6ebad9e3ea809474d` completed SUCCESS after verifying the exact Stage 1 PASS package before source I/O, re-verifying accepted Phase 2 identity, executing twice with byte-identical complete evidence, independently validating all 21 window rows, and recomputing the gate. Stage 2 artifact `10414817824` has ZIP SHA-256 `2522bbfd22979fd753fb1f51d2bb0d1ada957090102712fffbfdf59fe345bad4`; final status `PHASE7_PROMOTE_TO_SHADOW_DESIGN`. Detailed evidence: `docs/phase7-stage1-evidence.md` and `docs/phase7-walk-forward-evidence.md`.
- Conclusion: PROMOTE
- Reason: `session_breakout` is the sole frozen candidate to pass the one-shot Stage 1 gate and then every mandatory Stage 2 aggregate/stability criterion without retuning, refitting, rescue search, or protocol changes. `volatility_breakout` remains rejected from Stage 1. The successful mandatory costs are accompanied by a negative 1.0-pip diagnostic, which remains a deployment-cost limitation rather than a failed predeclared gate.
- Follow-up: close Phase 7 as PASS after the acceptance evidence/state change is merged and freshly verified on `main`; create checkpoint `fmp-v1-phase7-walk-forward` at that verified closure commit. The surviving `session_breakout` is eligible for Phase 8 shadow design only. Phase 8 remains UNSTARTED, and broker/demo/live/real-money trading remain locked.


### EXP-20260915-009 — Phase 8 live shadow evaluation

- Date: 2026-09-15
- Status: INCONCLUSIVE
- Connector transition: STOPPED BEFORE QUALIFICATION — OANDA Practice account unavailable to the operator jurisdiction; no qualification or scored live-shadow campaign occurred.
- Hypothesis: The sole Phase 7 survivor may preserve materially comparable timing, spread conditions, operational integrity, and positive hypothetical after-cost behavior when driven by real-time OANDA Practice USD_JPY quotes without any broker order-submission capability. No live viability is assumed.
- Code commit: source-of-truth activation commit first; shadow runtime implementation commits and accepted campaign code identity will be recorded as they are verified.
- Data manifest/version: upstream Phase 7 checkpoint `fmp-v1-phase7-walk-forward` / `b6fb0176555b071fef6d1070edf3407b03cd60c9`; accepted Phase 2 USDJPY artifact `10327600628`, ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`; processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`; live evidence uses the Phase 8 append-only evidence protocol and manifest defined by DEC-036.
- Pair(s): USDJPY only; provider instrument `USD_JPY`.
- Timeframe(s): frozen 15m session breakout; 1m shadow-live bars are an operational construction input only.
- Data range: future explicitly registered live-shadow campaign only; no hidden historical backfill is permitted after campaign gaps.
- Train period: not applicable; fixed rule, no fitting or optimization.
- Validation period: live campaign after frozen connector qualification/implementation verification; acceptance review requires the predeclared minimum sample/time/coverage gates.
- Final-test touched?: YES upstream in Phase 7; Phase 8 itself opens no additional historical final-test search and performs no retuning.
- Strategy/model: unchanged USDJPY 15m `session_breakout`, 5-pip buffer, 1.5x target range, exact London timing, no ML overlay.
- Features: strategy-native midpoint/session structure only; no Phase 5 model features or new predictive features.
- Parameters/search space: none. Provider/environment, method/host/path/instrument, stale threshold, quote deadlines, bar completeness, cost scenarios, risk settings, historical spread-reference method, sample minimums, and acceptance thresholds are frozen by DEC-036.
- Random seed (if relevant): not applicable; deterministic fixed-rule shadow/replay pipeline.
- Spread/cost model: observed live bid/ask spread plus zero commission and zero financing for the mandatory intraday-flat strategy.
- Slippage model: exactly 0.2, 0.5, and 1.0 pips adverse per fill; 0.2 and 0.5 are gating, 1.0 is diagnostic only.
- Risk assumptions: unchanged Phase 3 policy — 0.25% default requested risk, 0.50% hard per-trade maximum, 1.00% simultaneous open-risk maximum, 1.50% UTC day-start realized-loss halt; independent $100,000 virtual account per cost scenario.
- Trade count: pending live campaign; at least 40 completed financially scorable 0.2-pip trades are required before acceptance review.
- Net return after costs: pending.
- Expectancy/trade: pending.
- Profit factor: pending.
- Max drawdown: pending.
- Key subperiod results: pending; acceptance also requires at least 8 elapsed calendar weeks, at least 30 fully observed London dates, and at least 90% valid denominator-date coverage.
- Robustness/cost sensitivity: pending; mandatory gates apply at 0.2 and 0.5 pips while 1.0 pip remains diagnostic.
- Result summary: STOPPED BEFORE QUALIFICATION. The required OANDA Practice account was unavailable to the operator jurisdiction, so no qualification or scored live-shadow campaign occurred. DEC-037 supersedes only the connector path and preserves this negative operational evidence.
- Conclusion: NEED_MORE_DATA
- Reason: the OANDA connector path could not be qualified and produced no scored campaign evidence.
- Follow-up: preserve this record as stopped operational history; continue Phase 8 only under `EXP-20260917-010` and DEC-037. Keep Phase 9/demo/live-order/real-money paths locked.

### EXP-20260917-010 — Phase 8 MT5 demo live-shadow evaluation

- Date: 2026-09-17
- Status: INCONCLUSIVE / STOPPED FOR LIVENESS AMENDMENT
- Hypothesis: The unchanged Phase 7-promoted USDJPY 15m session-breakout rule can be evaluated prospectively using a read-only FP Markets MT5 demo quote bridge without changing strategy, execution-simulation, risk, or acceptance semantics.
- Code commit: UTC-correct campaign implementation `97715805498784badcb617debabc2b81c15cf5a8`.
- Data manifest/version: historical reference remains bound to accepted Phase 2 USDJPY identity and Phase 7 checkpoint; live evidence protocol `fmp-phase8-shadow-evidence-v2`.
- Pair(s): USDJPY only
- Timeframe(s): 15m strategy bars built from live 1m bid/ask bars
- Data range: prospective live-shadow diagnostic capture only; no backfill.
- Train period: not applicable; fixed rule, no refit.
- Validation period: prospective Phase 8 registered campaign.
- Final-test touched?: YES upstream in Phase 7; Phase 8 itself is prospective and performs no historical retuning.
- Strategy/model: unchanged `session_breakout`, 5-pip buffer, 1.5x target-range multiple, London-session/DST semantics, exact 16:00 `Europe/London` flat, no ML overlay.
- Features: live bid/ask quote stream only; no new feature/model fitting.
- Parameters/search space: none.
- Random seed (if relevant): not applicable.
- Spread/cost model: observed live demo bid/ask spread; zero commission and zero financing.
- Slippage model: 0.2, 0.5, and 1.0 adverse pips per fill; 0.2/0.5 gating, 1.0 diagnostic.
- Risk assumptions: existing Phase 3 risk policy unchanged; three independent $100,000 virtual scenarios.
- Trade count: no scored acceptance result; this experiment is diagnostic only.
- Net return after costs: not scored for acceptance.
- Expectancy/trade: not scored for acceptance.
- Profit factor: not scored for acceptance.
- Max drawdown: not scored for acceptance.
- Key operational result: clean UTC-source-time qualification passed, and the live bridge/capture remained active. Diagnostic quote-gap analysis over 46,721 normalized quotes found 102 gaps above 15 seconds, 23 above 30 seconds, 3 above 60 seconds, and a maximum gap of 4,301.580 seconds. During the long approximately 10:18–11:30 UTC no-tick interval on 2026-09-21, 870 valid bridge heartbeats continued.
- Result summary: the original live runner treated any 15-second market no-tick interval as a whole-date stale continuity failure even when the bridge remained healthy. That behavior made valid-date eligibility depend on tick sparsity and invalidated the first prospective Tuesday within minutes. The issue is a liveness-protocol defect, not evidence for or against strategy profitability.
- Conclusion: NEED_MORE_DATA
- Reason: DEC-038 amends live-capture liveness semantics; evidence collected under the superseded EXP-010 runner semantics cannot be reclassified or counted toward the amended campaign.
- Follow-up: preserve EXP-010 evidence for audit. Continue only with fresh `EXP-20260922-011` qualification/reference/registration after the DEC-038 implementation is merged and verified.

### EXP-20260922-011 — Phase 8 MT5 demo live-shadow evaluation with separated bridge/market liveness

- Date: 2026-09-22
- Status: STOPPED BEFORE REGISTRATION / SUPERSEDED BY PHASE 8A
- Protocol decision: DEC-038 APPROVED
- Hypothesis: The unchanged Phase 7-promoted USDJPY 15m session-breakout rule can be evaluated prospectively when true bridge continuity failures are separated from heartbeat-healthy no-tick intervals, while unseen trade paths and missing strategy context still fail closed.
- Code commit: DEC-038 implementation merged by PR #119 to `main` at `71fca1ccbfd14edd71c736f61187558f6f6a7909`; all qualification/reference/campaign evidence must bind this merged implementation identity.
- Data manifest/version: accepted Phase 2 USDJPY artifact `10327600628`, ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`; processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`; Phase 7 checkpoint `fmp-v1-phase7-walk-forward` / `b6fb0176555b071fef6d1070edf3407b03cd60c9`; live evidence protocol remains `fmp-phase8-shadow-evidence-v2`.
- Pair(s): USDJPY only
- Timeframe(s): 15m strategy bars built from observed live 1m bid/ask bars
- Data range: fresh prospective live-shadow campaign only after new qualification and registration; no EXP-010 evidence is scored or backfilled.
- Train period: not applicable; fixed rule, no refit.
- Validation period: prospective Phase 8 registered campaign.
- Final-test touched?: YES upstream in Phase 7; Phase 8 remains prospective, not historical retuning.
- Strategy/model: unchanged `session_breakout`, 5-pip buffer, 1.5x target-range multiple, London-session/DST semantics, exact 16:00 `Europe/London` flat, no ML overlay.
- Features: live bid/ask quote stream only.
- Parameters/search space: none.
- Random seed (if relevant): not applicable.
- Spread/cost model: observed live demo bid/ask spread; zero commission and zero financing.
- Slippage model: exactly 0.2, 0.5, and 1.0 adverse pips per fill; 0.2/0.5 gating, 1.0 diagnostic.
- Risk assumptions: unchanged Phase 3 policy; independent $100,000 virtual account per scenario.
- Liveness semantics: 15-second bridge silence remains date-invalidating `stale`; 15-second no-tick intervals with healthy bridge records emit `market_quiet` and do not by themselves invalidate the date. Open simulated positions crossing such a gap become `OUTCOME_UNKNOWN_AFTER_GAP`; missing required bars remain incomplete; 5-second entry/scheduled-exit quote deadlines remain frozen.
- Campaign minimums: at least 8 elapsed calendar weeks, 30 fully observed London dates, 40 completed scorable 0.2-pip trades, and at least 90% valid denominator-date coverage, plus all existing timing/spread/financial/replay/safety gates.
- Trade count: no EXP-011 campaign was registered; zero scored campaign trades.
- Net return after costs: not scored.
- Expectancy/trade: not scored.
- Profit factor: not scored.
- Max drawdown: not scored.
- Result summary: DEC-038 implementation and source-free verification passed. The operator then completed a fresh local qualification under code commit `5cb884dfb15d7798b023658e025221a38dfec9fc`: PASS, 100 prices, 15 heartbeats, zero rejection codes, max bridge/market liveness gap 3.884147625s. A fresh historical reference was also built under the same commit with SHA-256 `e920b3254235d2bb0766762551b5eb9d21439d429c59aebd14c3e4bb16e8cc64` and 199 historical trades. Before campaign registration, the operator rejected the economic case for evaluating this strategy alone and approved DEC-039.
- Conclusion: STOPPED
- Reason: research objective changed before campaign registration; the sole Phase 7 strategy is too economically weak for the operator's revised multi-strategy/high-return objective despite having passed its prior robustness gate.
- Follow-up: preserve qualification/reference and all EXP-009/010/011 evidence; do not register or start EXP-011. Continue under EXP-20260922-012 / Phase 8A.


### EXP-20260922-012 — Phase 8A multi-pair, multi-strategy portfolio research

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION
- Protocol decisions: DEC-039 APPROVED; DEC-040 APPROVED for joint-account retrospective simulation
- Hypothesis: a versioned portfolio of independently tested strategies across EURUSD, GBPUSD, and USDJPY can materially improve capital utilization and the economic return profile relative to the sole Phase 7 USDJPY 15m session-breakout strategy without relying on martingale, loss chasing, hidden leverage escalation, or hot-swapped self-modification.
- Code commit: implementation branch begins from `5cb884dfb15d7798b023658e025221a38dfec9fc`; exact result-producing commit(s) will be recorded as the experiment progresses.
- Data manifest/version: accepted Phase 1/2 Dukascopy EURUSD/GBPUSD/USDJPY canonical 1m BID/ASK histories plus deterministic 5m/15m/1h derived bars. Existing accepted manifests/checksums remain authoritative.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h where each strategy contract is valid.
- Data range: accepted historical coverage through 2026-08-20 for retrospective research/robustness; later prospective observations only after a challenger version is frozen.
- Train period: strategy-specific and must be predeclared before each new experiment result is inspected.
- Validation period: strategy-specific chronological validation / retrospective walk-forward; no post-Phase-7 strategy may call 2024-2026 an untouched final test.
- Final-test touched?: YES — the former final-test period was already opened by Phase 7.
- Strategy/model: multi-strategy library; initial research reuses implemented baseline families and may add new predeclared strategy/regime experiments. No strategy version may mutate in place after its evidence identity is frozen.
- Features: existing canonical bars and leakage-safe Phase 5 features may be used only under explicit experiment protocols; future information remains forbidden.
- Parameters/search space: each strategy/version search surface must be predeclared in its own experiment record before promotion use. Earlier rejected parameter points remain rejected under their original experiments.
- Random seed (if relevant): experiment-specific and recorded when stochastic methods are used.
- Spread/cost model: historical BID/ASK spread remains authoritative; 0.2/0.5/1.0-pip adverse-slippage views remain the default sensitivity set unless a later strategy-specific decision justifies a different executable model.
- Risk assumptions: existing Phase 3 risk contract remains the default: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous open-risk max, 1.50% UTC day-start realized-loss halt. Portfolio exposure/correlation controls are added above, not around, this risk engine.
- Economic objective: materially improve on the Phase 7 single-strategy economic case. The operator's aspiration includes possible +10% days; the experiment measures the frequency and risk required for such days rather than assuming or guaranteeing them.
- Required reporting: daily return distribution, monthly/annualized net return, expectancy, profit factor, max drawdown, losing streaks, tail/concentration diagnostics, trade count, cost sensitivity, and contribution by pair/strategy/timeframe/session/regime.
- Continuous-learning rule: new observations may create challengers, but active champions are immutable during registered campaigns. No challenger can automatically replace a champion or authorize demo/live orders.
- Trade count: pending implementation and research runs.
- Net return after costs: pending.
- Expectancy/trade: pending.
- Profit factor: pending.
- Max drawdown: pending.
- Conclusion: NEED_MORE_DATA
- Implementation progress: PR #121 merged the registry/lifecycle/router and explicit retrospective evaluator; PR #122 merged the deterministic retrospective batch/CLI/manual 3-pair × 3-timeframe workflow; PR #123 merged the DEC-040 shared-account simulator with 1m execution, time-local conflict routing, and a single Phase 3 risk state. PR #122 pre-merge verification completed with 819 tests PASS; PR #123 pre-merge verification completed with 828 tests PASS; unchanged Phase 3 acceptance passed for both.
- Joint-simulation protocol: DEC-040 freezes canonical 1m BID/ASK as the execution path, strategy-native 5m/15m/1h bars as the signal path, one shared $100,000 account/risk state per slippage scenario, and time-local same-symbol conflict handling. These results remain `RETROSPECTIVE_ALREADY_SEEN` and cannot authorize promotion.
- Follow-up: complete deterministic joint evidence packaging and explicit-fingerprint manual CLI. After that evidence layer is green, predeclare a separate portfolio-selection protocol before any historical combination search or winner selection is allowed. Phase 8B live shadow remains locked until Phase 8A acceptance.


### EXP-20260922-013 — Phase 8A opening-range momentum challenger round 1

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION / NO BENCHMARK RESULTS INSPECTED
- Protocol decision: DEC-041 APPROVED / PREDECLARED
- Hypothesis: a breakout of the 06:00–08:00 London opening range may carry more persistent intraday information when the breakout candle also shows directional body conviction, producing a more robust multi-pair edge than an unfiltered range break.
- Family/version: `opening_range_momentum` / `fmp-opening-range-momentum-v1`
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Reference window: 06:00–08:00 `Europe/London`
- Signal window: 08:00–12:00 `Europe/London`
- Mandatory flat: exact 16:00 `Europe/London`
- Fixed buffer: 2 pips
- Fixed stop geometry: 0.25 reference-range depth inside the breached boundary
- Parameters/search space: `body_fraction_threshold ∈ {0.50, 0.70}`; `target_r_multiple ∈ {1.0, 1.5}`; exactly 36 pair/timeframe/configuration identities
- Stage A development: 2015-01-01 through 2020-12-31 inclusive
- Stage A validation: 2021-01-01 through 2023-12-31 inclusive
- Stage B retrospective confirmation: 2024-01-01 through 2026-08-20 inclusive, only for exact Stage A survivors
- Final-test touched?: YES upstream; all EXP-013 evidence is retrospective and Stage B must not be labeled untouched OOS
- Spread/cost model: historical BID/ASK plus 0.2/0.5/1.0-pip adverse-slippage scenarios; 0.2 and 0.5 mandatory, 1.0 diagnostic
- Commission/financing: zero / zero under mandatory intraday flat
- Risk assumptions: unchanged Phase 3 risk — $100,000 starting equity, 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous risk max, 1.50% UTC daily realized-loss halt
- Stage A gate: positive net return/expectancy/PF>1.0 and DD<=5% at 0.2 and 0.5 on both development and validation; at least 100 development and 50 validation 0.2-pip trades; at least one same-pair/timeframe neighboring grid point must also pass mandatory profitability/drawdown gates
- Stage B gate: positive net return/expectancy/PF>1.0 and DD<=5% at both 0.2 and 0.5; at least 75 completed 0.2-pip trades
- Trade count: pending implementation and benchmark
- Net return after costs: pending
- Expectancy/trade: pending
- Profit factor: pending
- Max drawdown: pending
- Conclusion: NEED_MORE_DATA
- Implementation status: PR #125 merged the signal contract, 36 challenger identities, Stage A cell runner, and frozen gate logic. PR #128 merged deterministic Stage A development/validation/gate artifacts, nine-cell authorization aggregation, and the frozen manual Stage A workflow. PR #129 merged strategy-source SHA-256 binding plus the guarded Stage B confirmation runner/workflow. PR #128 verified 868 tests PASS; PR #129 verified 875 tests PASS; unchanged Phase 3 acceptance passed for both. No EXP-013 Stage A or Stage B historical workflow has been dispatched.
- Follow-up: deliberately dispatch Stage A only when an authorized workflow-dispatch path is available. No Stage B source may open unless the resulting nine-cell authorization artifact explicitly lists one or more exact survivor fingerprints and the opening-range strategy source SHA-256 still matches.


### EXP-20260922-014 — Phase 8A frozen portfolio selection

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION ONLY / SEARCH BLOCKED
- Protocol decision: DEC-042 APPROVED
- Hypothesis: if Phase 8A produces at least two independently qualified immutable strategies, a bounded shared-account portfolio chosen under predeclared stability, concentration, cost, drawdown, and deterministic ranking rules can improve the economic case without post-result threshold changes.
- Eligible lifecycle states: HISTORICAL_QUALIFIED, SHADOW_CANDIDATE, SHADOW_VALIDATED, DEMO_ELIGIBLE only.
- Current eligible baseline count: 1 — the existing Phase 7 USDJPY 15m session-breakout survivor.
- Search status: BLOCKED until at least one additional immutable challenger reaches HISTORICAL_QUALIFIED under a separate predeclared discovery/qualification experiment.
- Pool bounds: 2 to 12 eligible strategies.
- Portfolio cardinality: evaluate all unique unordered sets of 1 through 6; 1-strategy sets are controls only.
- Retrospective selection range: 2019-01-01 inclusive through 2026-08-21 exclusive.
- Execution: DEC-040 shared $100,000 account, canonical 1m BID/ASK execution, native 5m/15m/1h signal bars, unchanged Phase 3 risk.
- Slippage scenarios: exactly 0.2, 0.5, and 1.0 pips adverse per fill; 0.2/0.5 gating, 1.0 diagnostic.
- Mandatory gates: positive net return/expectancy, PF > 1.0, max drawdown <= 5%, and >=200 trades at both gating costs; additional 0.2-pip yearly-stability, strategy/pair concentration, and diversity gates per DEC-042.
- Ranking: immutable lexicographic order frozen in DEC-042; no tunable score weights.
- Evidence label: RETROSPECTIVE_ALREADY_SEEN.
- Untouched OOS?: NO.
- Promotion authorized?: NO.
- Trade count: not run.
- Net return after costs: not run.
- Expectancy/trade: not run.
- Profit factor: not run.
- Max drawdown: not run.
- Conclusion: NEED_MORE_DATA
- Implementation status: PR #133 merged the guarded DEC-042 runner and manual workflow to `main` at `a10bf42b75b48c300ac48edaa6616a4af6fa2e9c` after 910 tests PASS, compile PASS, and unchanged Phase 3 acceptance PASS. It reconstructs the Phase 7 baseline + exact EXP-015 HISTORICAL_QUALIFIED shortlist, binds the EXP-015 final artifact by SHA-256, freezes the complete 1–6 strategy set universe before historical source download, evaluates only that immutable universe, converts joint evidence to frozen DEC-042 metrics, and emits deterministic winner/no-winner evidence. A zero-trade scenario represents expectancy as null and therefore fails the positive-expectancy gate rather than raising.
- Execution status: SEARCH BLOCKED / NOT RUN. EXP-015 Stage A/B/C are still undispatched, so no eligible challenger pool exists yet. A 12-strategy pool would enumerate 2,509 sets and 7,527 cost runs; practical sharding/caching may be added without changing the frozen set universe or gates before any large-pool dispatch.
- Follow-up: preserve source-free dispatch guards and do not run DEC-042 until an exact successful EXP-015 final shortlist produces at least one new HISTORICAL_QUALIFIED challenger.


- Identity correction: initially recorded with duplicate EXP-013 / DEC-041 identifiers already assigned to opening_range_momentum; renumbered before any portfolio combination search or result.

### EXP-20260922-015 — Phase 8A rule-based challenger discovery

- Date: 2026-09-22
- Status: CLOSED — AUTHORITATIVE STAGE A FAILED / NO RETRY / PRE-DEC-268 HISTORICAL EVIDENCE
- Protocol decisions: DEC-043 APPROVED; DEC-044 APPROVED BEFORE ANY HISTORICAL STAGE
- Hypothesis: new predeclared parameter regions of the existing deterministic rule families can produce additional robust immutable challengers across EURUSD, GBPUSD, and USDJPY without reviving rejected Phase 4 points or tuning after later-period observation.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Families: session_breakout, trend_continuation, mean_reversion, previous_day_rejection, volatility_breakout, session_sweep_rejection
- Frozen candidate count: 567 new configurations, all non-overlapping with the original Phase 4 parameter grid.
- Stage A: 2015-01-01 to 2019-01-01 exclusive; all 567 candidates; 54 exact pair/family/timeframe ranking cells; at most 2 survivors per cell; absolute maximum 108 survivors under DEC-044.
- Stage B: 2019-01-01 to 2023-01-01 exclusive; only Stage A survivors; no retune.
- Stage C: 2023-01-01 to 2026-08-21 exclusive; only Stage B passers; no retune.
- Cost model: 0.2/0.5/1.0 pips adverse per fill; 0.2/0.5 gating, 1.0 diagnostic.
- Risk: unchanged Phase 3 defaults; $100,000 starting equity per independent strategy/scenario run; 0.25% requested risk.
- Final shortlist: at most 11 new HISTORICAL_QUALIFIED challengers under frozen cross-pair/family/cell caps.
- Evidence label: RETROSPECTIVE_ALREADY_SEEN
- Untouched OOS?: NO
- Broker/shadow promotion authorized?: NO
- Stage A opened?: YES — sole authoritative run `36279397331`, attempt 1, head `500f12ca5cb6e611f93b5d3a9eb52fb678e7774f`, terminal conclusion FAILURE
- Stage B opened?: NO
- Stage C opened?: NO
- Trade count: no authoritative aggregate Stage A result; 8/9 cells persisted diagnostics only.
- Net return after costs: no authoritative aggregate result.
- Expectancy/trade: no authoritative aggregate result.
- Profit factor: no authoritative aggregate result.
- Max drawdown: no authoritative aggregate result.
- Conclusion: FAIL — USDJPY 1h failed on `ValueError: daily start equity must be finite and positive`; Stage A authorization was skipped and no authoritative survivor set exists.
- Implementation status: PR #130 merged the validator-region + exact 567-identity catalog at `7e3eac44a14815ab65b1f85af9e2469517ed3efb` after 880 tests PASS and unchanged Phase 3 acceptance PASS. DEC-044 corrected the pre-run Stage A survivor arithmetic from 54 to 108 while retaining at most 2 survivors in each of 54 exact ranking cells. PR #131 merged the Stage A preflight catalog freeze, exact 63-strategy/189-scenario pair-timeframe cells, deterministic family rankings, richer gate/ranking authorization evidence, and manual Stage A workflow at `bde29280d08cf347265ea06f186972a61f2561f4` after 891 tests PASS, compile PASS, and unchanged Phase 3 acceptance PASS. DEC-267 later consumed the one authoritative Stage A slot. DEC-269 freezes the terminal failed result: catalog + 8 cell artifacts persisted, USDJPY 1h failed, and no authorization artifact/survivor set exists.
- Implementation status continued: PR #132 merged guarded Stage B/C execution and final deterministic shortlist/lifecycle accounting to `main` at `3d36368811e155d41d45b73313827bca83a66518` after 898 tests PASS, compile PASS, and unchanged Phase 3 acceptance PASS. Stage B/C validate upstream artifact hashes, runner commits, catalog/source digests, processed manifests, yearly gates, and candidate-sequence identity before downstream source access. Finalization applies the frozen Stage B/C ranking and 11-total / 4-per-pair / 3-per-family / 2-per-cell caps, then records one explicit lifecycle disposition for all 567 candidates.
- Follow-up: none inside EXP-015. Do not retry, replace, rescue, or continue to Stage B/C. Preserve the eight successful cell artifacts as diagnostics only and continue new research under DEC-268 discovery-first rules.
- Identity correction: initially drafted as EXP-014 / DEC-042 during reconciliation; renumbered before any historical stage or benchmark result.


### EXP-20260922-016 — Phase 8A acceptance review

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION ONLY / NO ACCEPTANCE RESULT
- Protocol decision: DEC-045 APPROVED BEFORE ANY DEC-042 SELECTION RESULT
- Purpose: deterministically review exact DEC-042 preflight/selection evidence and either freeze one immutable multi-strategy shadow candidate or record a credible Phase 8A research rejection.
- Inputs: exact successful DEC-042 manual run from main; exact preflight.json and selection.json bytes and SHA-256 values; exact frozen Phase 7 baseline control in the DEC-042 pool.
- Economic-improvement gate: the DEC-042 selected portfolio must already pass all frozen DEC-042 gates and have strictly higher 0.5-pip annualized compounded return than the Phase 7 baseline control over the same 2019-01-01..2026-08-21 selection range.
- Acceptance outcome: selected strategy records transition exactly HISTORICAL_QUALIFIED -> SHADOW_CANDIDATE and an immutable champion/shadow-candidate set is frozen.
- Rejection outcome: no lifecycle transition; Phase 8B remains locked.
- No new historical data may be opened and no strategy/backtest may run under EXP-016.
- Evidence remains RETROSPECTIVE_ALREADY_SEEN; untouched_oos = false.
- Broker/demo/live/real-money promotion remains false.
- Historical run status: NOT RUN.
- Implementation status: current `phase8a/acceptance-review` branch contains the deterministic acceptance compiler, lifecycle/champion-set freeze, resolver, artifact writer, CLI, guarded main-only manual workflow, exact DEC-042 upstream provenance/artifact binding, full repository/compile checks, and deterministic Phase 3 verification before artifact creation. No DEC-042 or DEC-045 historical/result workflow has been dispatched.
- Follow-up: source-free verify and merge the DEC-045 implementation; only then may a future successful DEC-042 run be reviewed.


### EXP-20260922-017 — Phase 8B shadow design

- Date: 2026-09-22
- Status: ACTIVE — DESIGN IMPLEMENTATION ONLY / NO CAMPAIGN
- Protocol decision: DEC-046 APPROVED BEFORE ANY PHASE 8B CAMPAIGN
- Purpose: compile an exact accepted DEC-045 shadow candidate into an immutable multi-symbol read-only Phase 8B design without opening a live campaign.
- Required input: exact `PHASE8A_SHADOW_CANDIDATE_ACCEPTED` DEC-045 artifact.
- Supported symbols: EURUSD / GBPUSD / USDJPY only; exact required subset derived from accepted champion set.
- Intended connector topology: one read-only MT5 EA per required symbol chart; fixed FILE_COMMON feed per symbol; common demo account fingerprint/server; no arbitrary path/symbol override; no broker-order surface.
- Liveness: DEC-038 bridge/market separation retained independently per required symbol.
- Campaign registration authorized?: NO.
- Campaign start authorized?: NO.
- Demo/live/broker mutation/real-money/Phase 9 authorized?: NO.
- Historical/live run status: NOT RUN.
- Implementation status: current `phase8b/design-contract` branch contains the deterministic design compiler/validator/artifact writer, source-free CLI, guarded main-only manual workflow, and tests that derive the exact symbol/file topology from an accepted DEC-045 champion set while keeping campaign/order authorizations false.
- Follow-up: source-free verify/merge DEC-046 design implementation, then separately freeze and implement multi-symbol MT5 bridge qualification/registration before any Phase 8B campaign can start.


### EXP-20260922-018 — Phase 8B bridge qualification and registration

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION ONLY / NO CAMPAIGN
- Protocol decision: DEC-047 APPROVED BEFORE ANY PHASE 8B CAMPAIGN
- Purpose: implement the separate multi-symbol read-only MT5 bridge, per-symbol qualification, cross-feed identity gate, and immutable registration boundary for an accepted DEC-046 design.
- Bridge protocol: fmp-mt5-demo-multisymbol-file-bridge-v1.
- Required feeds: exact DEC-046 symbol subset only, using fixed FILE_COMMON files.
- Per-symbol qualification: <=600 seconds, >=100 prices, >=6 heartbeats, bridge gap <=15 seconds, market gap <=15 seconds during qualification, source-time skew <=5 seconds.
- Multi-symbol PASS: every required symbol PASS; same approved demo account fingerprint/server; distinct bridge session IDs; exact required-symbol coverage.
- Qualification PASS authorizes registration only.
- Campaign start authorized?: NO.
- Demo/live/broker mutation/real-money/Phase 9 authorized?: NO.
- Runtime status: NOT RUN.
- Implementation status: current `phase8b/bridge-qualification-registration` branch contains the separate multi-symbol bridge parser/session validator/file-tail discovery, read-only Phase 8B MT5 EA, exact legacy-threshold per-symbol qualification, cross-feed account/server/session gate, deterministic qualification evidence, immutable exactly-once registration, and CLI/tests exposing only `design`, `qualify`, and `register`. No `run`/capture/start command exists.
- Follow-up: source-free verify/merge DEC-047. A later separately frozen decision is still required before any Phase 8B live-shadow segment may start.


### EXP-20260922-019 — Phase 8B campaign start authorization

- Date: 2026-09-22
- Status: ACTIVE — IMPLEMENTATION ONLY / NO LIVE-SHADOW SEGMENT
- Protocol decision: DEC-048 APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
- Purpose: verify that the currently visible multi-symbol MT5 bridge sessions still exactly match one immutable DEC-047 campaign registration, freeze the prospective start boundary, and establish EOF-only reader semantics before any later capture runtime may begin.
- Input: exact valid `fmp-phase8b-campaign-registration-v1` artifact and its SHA-256; fixed required-symbol bridge files only.
- Start gate: every required symbol's active `BRIDGE_START` must match the registration on symbol, protocol, bridge session, account fingerprint, and server; required coverage must be exact.
- Reader semantics: `TAIL_AT_EOF_NO_BACKFILL`; all pre-reader transport content is excluded from future prospective evidence.
- Frozen boundary: explicit UTC start timestamp plus derived `Europe/London` first date, registration/champion/strategy identities, bridge sessions, liveness, quote deadline, and slippage scenarios.
- Authorized on PASS: `campaign_start_authorized = true`; `prospective_capture_authorized = true`.
- Still forbidden: promotion, demo/live orders, broker mutation, real money, Phase 9.
- CLI scope: add only `authorize-start`; no `run`, `start`, `capture`, or `review` command under DEC-048.
- Implementation status: the current DEC-048 branch adds deterministic registration/session revalidation, London start-date freezing, `TAIL_AT_EOF_NO_BACKFILL`, start-authorization fingerprinting, exactly-once artifacts, and the sole new CLI command `authorize-start`. The implementation contains no prospective capture loop.
- Historical/live execution status: NOT RUN.
- Follow-up: merge DEC-048 only after the final exact branch head passes the repository suite, compile checks, and unchanged Phase 3 acceptance. A later separately frozen capture/replay/acceptance protocol must independently revalidate DEC-048 evidence before any live-shadow segment can begin.


### EXP-20260922-020 — Phase 8B prospective capture foundation

- Date: 2026-09-22
- Status: ACTIVE — SOURCE-FREE IMPLEMENTATION MERGED / NO LIVE-SHADOW SEGMENT
- Protocol decision: DEC-049 APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
- Purpose: freeze and implement the exact source-free boundary between DEC-048 campaign-start authorization and a later live capture/replay/acceptance runtime.
- Required inputs: one exact valid DEC-047 `fmp-phase8b-campaign-registration-v1` artifact plus one exact valid DEC-048 `fmp-phase8b-campaign-start-v1` artifact.
- Upstream binding: exact registration/start-artifact SHA-256 values and semantic equality for champion set, strategies, symbols/timeframes, connector identity, fixed bridge files, account/server, bridge sessions, liveness, slippage, and all safety authorization flags.
- Fresh-session gate: every required-symbol bridge is independently revalidated from a fresh EOF-tailing reader against the frozen registration/start identity.
- Reader semantics: `TAIL_AT_EOF_NO_BACKFILL`.
- New source-free artifact: `fmp-phase8b-capture-preflight-v1`, with deterministic fingerprint and `capture_runtime_ready = true` while `live_shadow_segment_started = false`.
- Raw envelope: `fmp-phase8b-capture-record-v1` freezes deterministic post-preflight TICK/HEARTBEAT serialization with receive UTC/monotonic metadata and existing bridge-session duplicate/source-time/identity validation.
- CLI scope: unchanged; no `capture`, `run`, `start`, `replay`, or `review` command.
- Broker/demo/live/real-money/Phase 9 authorized?: NO.
- Live execution status: NOT RUN.
- Implementation status: PR #140 merged DEC-049 to `main` at `39066f10c60bd1bade4f6f6e78e05ab3b7621c8e`, adding capture preflight/record-envelope APIs, exactly-once preflight artifacts, exports, and six focused contract tests. The exact final PR head passed 961 tests plus workflow-YAML validation and compile checks in run `35745448870`; unchanged Phase 3 acceptance run `35745448859` passed.
- Follow-up: separately freeze and implement the Phase 8B runtime/replay/acceptance protocol before any prospective Phase 8B segment may begin.


### EXP-20260922-021 — Phase 8B runtime and deterministic replay kernel

- Date: 2026-09-22
- Status: ACTIVE — SOURCE-FREE IMPLEMENTATION MERGED / NO LIVE-SHADOW SEGMENT
- Protocol decision: DEC-050 APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
- Purpose: implement the deterministic finite-sequence market-processing, multi-strategy routing, shared-account shadow simulation, segment evidence, and offline replay kernel over exact DEC-049 capture records.
- Input boundary: one exact valid `fmp-phase8b-capture-preflight-v1` artifact plus an ordered finite sequence of exact `fmp-phase8b-capture-record-v1` envelopes.
- Market processing: per-symbol bridge/market liveness separation; no backfill/interpolation; only fully observed 1m bars; exact 5m/15m/1h aggregation from complete one-minute constituents.
- Strategy path: immutable `StrategyVersion` reconstruction from frozen identity JSON; recomputed fingerprint validation; existing Phase 8A strategy generators reused unchanged.
- Routing: existing champion eligibility, same-symbol same-time direction-conflict handling, and USD exposure accounting reused.
- Simulation: one shared $100,000 Phase 3 risk account per 0.2/0.5/1.0-pip scenario across all champion strategies and symbols; five-second entry/exit deadlines; symbol-specific stale-path invalidation.
- Replay: exact same preflight + exact ordered raw envelopes must reproduce the canonical segment payload byte-for-byte.
- CLI scope: unchanged; no `capture`, `run`, `start`, or `review` command.
- Broker/demo/live/real-money/Phase 9 authorized?: NO.
- Live execution status: NOT RUN.
- Implementation status: PR #141 merged DEC-050 to `main` at `4a8431d17f3fd050839d7841fc27e5543b258dc4`, adding the runtime/replay kernel, deterministic segment/replay artifact support, Phase 8B API exports, and five focused runtime/replay tests. Exact final PR-head verification passed 966 tests plus workflow-YAML validation and compile checks; unchanged Phase 3 acceptance passed.
- Follow-up: separately freeze and implement the Phase 8B acceptance compiler before any prospective Phase 8B segment may begin.


### EXP-20260922-022 — Phase 8B acceptance compiler and prospective evidence contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE-FREE IMPLEMENTATION MERGED / NO LIVE-SHADOW SEGMENT
- Protocol decision: DEC-051 APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
- Purpose: freeze and implement the deterministic Phase 8B acceptance compiler plus the exact prospective campaign-evidence and historical spread-reference contracts required before any champion can become SHADOW_VALIDATED.
- Campaign-evidence protocol: `fmp-phase8b-campaign-evidence-v1`; prospective=true and closed=true are mandatory, with exact DEC-049 preflight, DEC-050 segment/replay, champion/strategy/symbol/cost identities and deterministic fingerprint validation.
- Spread-reference protocol: `fmp-phase8b-spread-reference-v1`; exact symbol coverage, historical spread sample counts and median/p95 entry/exit values, bound to the same preflight/champion/cost identities.
- Minimum evidence: >=40 completed 0.2-pip scorable trades, >=8 elapsed weeks, >=30 complete London dates, >=2 represented strategy families, and >=2 represented V1 pairs.
- Operational gates: >=90% date coverage, zero malformed records silently admitted, zero stale-gap trades in financial metrics, complete operational logging, identical candidate sequence across scenarios, replay match, p99 processing <=250ms, and zero scored entry/scheduled-exit deadline violations.
- Spread gate: live median/p95 entry/exit spread per traded required symbol <= historical value +0.5 pip.
- Financial gates: at 0.2 and 0.5 pips, net return >0, expectancy >0, PF >1, max drawdown <=5%; 1.0 pip diagnostic only.
- Outcome precedence: protocol failure -> safety rejection -> replay/integrity operational rejection -> NEED_MORE_DATA -> operational rejection -> market mismatch -> financial mismatch -> PASS.
- PASS authority: exact champion SHADOW_CANDIDATE -> SHADOW_VALIDATED transition plus demo-design eligibility only; all demo/live/broker/real-money/Phase-9 execution authorizations remain false.
- Live execution status: NOT RUN.
- Initial PR CI: run `35749097079` correctly failed one tamper test because a derived 0.2-pip trade-count check fired before the immutable evidence fingerprint check; unchanged Phase 3 acceptance `35749097176` passed.
- Fix: commit `8628f0810a55353da3bbe299635d0bd89fa4ab94` authenticates campaign and spread-reference fingerprints before derived consistency validation.
- Fixed verification: PR tests run `35749385885` passed 973 tests plus workflow-YAML validation and compile checks; unchanged Phase 3 acceptance run `35749385867` passed.
- Merge status: PR #143 merged DEC-051 to `main` at `2c9577be8eafb9e307e05214609206dfeb7c6c69`. Superseded PR #142 remained unmerged because its displayed head lagged the branch ref; a fresh exact-head PR was used instead.
- Follow-up: a later separately frozen prospective capture/close protocol must create real `fmp-phase8b-campaign-evidence-v1` evidence; DEC-051 itself cannot create prospective evidence or start a live-shadow segment.


### EXP-20260922-023 — Phase 8B prospective capture segment journal

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION MERGED / NO LIVE SEGMENT CAPTURED
- Protocol decision: DEC-052 APPROVED BEFORE ANY PHASE 8B LIVE-SHADOW SEGMENT
- Purpose: add the first explicit bounded operator-invoked quote-only capture surface while preserving fixed bridge identity, EOF/no-backfill semantics, deterministic DEC-050 processing/replay, and all order-path locks.
- CLI scope: adds only `capture-segment --campaign-dir <path> --duration-seconds <1..86400>`; polling remains fixed at 0.10 seconds; generic run/start/review/campaign-close commands remain absent.
- First-segment rule: if no DEC-049 capture preflight exists, build it from the exact registration/start artifacts and continue capture on the same fresh EOF readers.
- Restart rule: later invocations use fresh EOF readers and therefore exclude records written while FMP was not observing; restart gaps are retained for later campaign-close accounting.
- Durable evidence: create-only per-segment directory, fsynced capture-record JSONL, one fsynced audit row per retained record with receive-to-raw-append latency, fsynced operational events, DEC-050 segment/replay artifacts, and immutable `fmp-phase8b-prospective-segment-v1` close artifact.
- Failure semantics: malformed/truncated/session-drift/identity failures terminate the invocation and may leave retained raw evidence, but no `prospective-segment.json` close artifact.
- Broker/demo/live/real-money/Phase 9 authorized?: NO.
- Acceptance/promotion authorized?: NO.
- Live execution status: NOT RUN.
- Implementation status: PR #144 merged DEC-052 to `main` at `8d28dc3dfdc1bb41112034f7b1a91fd54ad55e46`. The exact final PR head `0d61fcb6f678a8c76cef78b6ab93df5485abe791` passed 977 tests plus workflow-YAML validation and compile checks in run `35751972199`; unchanged Phase 3 acceptance run `35751972226` passed.
- Follow-up: separately freeze and implement the multi-segment campaign-close protocol before DEC-051 acceptance can consume real prospective evidence.


### EXP-20260922-024 — Phase 8B prospective campaign evidence close

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION MERGED / NO ACCEPTANCE RESULT
- Protocol decision: DEC-053 APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
- Purpose: compile immutable DEC-051 campaign-evidence snapshots from exact ordered DEC-052 prospective segment journals without resetting the shared virtual account at process boundaries.
- Segment eligibility: exact valid prospective-segment closure, raw/audit/operational digests, child DEC-050 segment identity, child replay match, exact DEC-049 preflight identity, no duplicate prospective/runtime/replay/capture fingerprints, and non-overlapping wall-clock intervals.
- Restart semantics: receive monotonic values remain segment-local; cross-segment source-time progression is mandatory; restart gaps are explicit and never backfilled.
- Aggregate runtime: all eligible raw records are replayed as one continuous DEC-050 aggregate with one shared $100,000 Phase 3 risk account per slippage scenario; child financial summaries are integrity-only and are never summed.
- Terminal snapshot rule: every aggregate scenario must have zero open and zero pending hypothetical decisions before campaign evidence can be written.
- Derived DEC-051 evidence: London weekday denominator/full-day coverage, nearest-rank p99 processing latency, entry/exit deadline violations, strategy-family/pair representation, exact live entry/exit spread samples and median/p95, scenario financial metrics, structural safety, and integrity evidence.
- Snapshot semantics: each close is immutable and create-only, but not a permanent capture shutdown; later clean segments may produce a newer snapshot after NEED_MORE_DATA.
- CLI scope: adds only `close-campaign --campaign-dir <path>`; it reads existing artifacts only and does not access MT5 or a broker.
- Broker/demo/live/real-money/Phase 9 authorized?: NO.
- Acceptance/lifecycle transition executed?: NO.
- Initial CI: run `35754471148` found one test-ordering issue: a copied duplicate segment failed as temporal overlap before duplicate immutable identity. Phase 3 acceptance `35754471080` passed.
- Fix: commit `8f1eb49fb8ea84093c86da52779e74b91650591d` authenticates duplicate segment/runtime/replay/capture identities before interval overlap evaluation.
- Additional pre-result safety amendment: commits `7d845ce8d437c8ab0b515358d075dd5c912de000` and `3244459b456f4c05e07cb4e52ae7c50aeef96061` freeze and enforce zero open/pending aggregate decisions before closure.
- Verification: exact source head `3244459b456f4c05e07cb4e52ae7c50aeef96061` passed 982 tests plus workflow-YAML validation and compile checks in run `35754791092`; unchanged Phase 3 acceptance run `35754790877` passed.
- Merge status: PR #145 merged DEC-053 to `main` at `3b0d7be25a8d5f2ff6eff2fb495aaa6c2ca3c09f`. The exact final PR head `ddce81d0e3fc948eb0d251e7d2dc488eba5cefae` passed 982 tests plus workflow-YAML validation and compile checks in run `35754982384`; unchanged Phase 3 acceptance run `35754982244` passed.
- Follow-up: no real DEC-052 capture or DEC-051 acceptance result has been produced. The next milestone is to freeze the explicit acceptance-review invocation/lifecycle transition boundary over immutable DEC-053 snapshots and pre-frozen spread-reference evidence.


### EXP-20260922-025 — Phase 8B acceptance review and shadow-validation freeze

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION MERGED / NO REAL ACCEPTANCE RESULT
- Protocol decision: DEC-054 APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
- Purpose: freeze the final source-only Phase 8B review boundary over exact DEC-053 closures and one deterministic campaign-bound DEC-051 historical spread reference.
- Pre-capture ordering: `authorize-start` now persists DEC-048 start authorization and DEC-049 capture preflight from the same fresh EOF readers, then stops without capturing a prospective record.
- Historical spread reference: fixed accepted Phase 8A complete canonical 1m snapshot, 2015-01-01 through 2026-08-21, fixed manifest layout, entry spread from bar open, exit spread from bar close, exact sample counts, median, nearest-rank p95, and exact processed-manifest/month provenance.
- Capture gate: `capture-segment` requires the exact campaign-bound spread reference and fails after any terminal campaign marker.
- Review: `review-campaign --campaign-dir <path> --closure-id <sha256>` binds one exact closure, one exact campaign-bound spread reference, and the review code commit into a deterministic create-only review ID.
- NEED_MORE_DATA: non-terminal; writes acceptance evidence only and permits later clean capture/closure/review snapshots.
- PASS/rejection: terminal for Phase 8B capture/review; writes `fmp-phase8b-campaign-terminal-v1` with all order/broker/real-money/Phase-9 execution flags false.
- PASS lifecycle evidence: only exact PASS may create `fmp-phase8b-shadow-validation-v1`, applying existing registry transition SHADOW_CANDIDATE -> SHADOW_VALIDATED while reproducing the exact champion-set fingerprint.
- Demo/live orders, broker mutation, real-money trading, DEMO_ELIGIBLE transition, and Phase 9 execution authorized?: NO.
- Live execution status: NOT RUN.
- Verification: PR #146 implementation head `57b94fc0ec1f30fea0acb036364d1ca0667f8c8c` passed 988 tests plus workflow-YAML validation and compile checks in run `35758432987`; unchanged Phase 3 acceptance run `35758432967` passed.
- Merge status: PR #146 merged DEC-054 to `main` at `7e3e1f03fcdf9f2314cd96864eb1825b1b3c2a18`. The exact final PR head `aaa5500776fa4a8d7a4e5ddcfb0b8ec4d24498c5` passed 988 tests plus workflow-YAML validation and compile checks in run `35758599011`; unchanged Phase 3 acceptance run `35758598901` passed.
- Follow-up: no real prospective capture, spread-reference freeze, campaign closure review, lifecycle transition, or Phase 9 design has been executed. A later separately frozen Phase 9 demo-design protocol may consume only an exact DEC-054 PASS/shadow-validation artifact.


### EXP-20260922-026 — Phase 9 demo design proposal

- Date: 2026-09-22
- Status: ACTIVE — SOURCE DESIGN MERGED / NO DEMO ORDER
- Protocol decision: DEC-055 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: freeze a source-only Phase 9 demo architecture from one exact terminal DEC-054 PASS review while preserving accepted Phase 8B champion/account/server/symbol identity and unchanged Phase 3 risk policy.
- Input boundary: exact DEC-049 preflight, exact terminal DEC-054 PASS review/acceptance/shadow-validation bytes, and exact campaign-terminal marker.
- Integrity: Phase 9 loader verifies the DEC-054 review-manifest SHA-256 bindings for acceptance and shadow-validation before compiling the design.
- Provider path: accepted FP Markets MT5 demo identity only; changing provider requires a new decision.
- Future protocol: `fmp-mt5-demo-order-bridge-v1` requirements frozen for practice-account assertion, deterministic client order IDs, mandatory protective stops, requested-vs-fill logging, order journal, startup reconciliation, orphan fail-closed behavior, restart/recovery, daily halt, and secret handling.
- Risk: exact unchanged Phase 3 `RiskConfig` is embedded; DEC-055 cannot widen per-trade, simultaneous-risk, or daily-loss limits.
- CLI: separate Phase 9 source-only `design-demo --campaign-dir <path> --review-id <sha256>`; no `run-demo`, `order`, `trade`, broker, or live command.
- Authorization: `demo_adapter_source_authorized=true` only. Demo execution/order, live order, broker mutation, real-money trading, and Phase 10 remain false.
- Live/demo execution status: NOT RUN.
- Verification: PR #147 exact implementation head `c796c4988ebafb6d357b5a49de2d6ced928bd2a5` passed 993 tests plus workflow-YAML validation and compile checks in run `35759609550`; unchanged Phase 3 acceptance run `35759609484` passed.
- Merge status: PR #147 merged DEC-055 to `main` at `559d8787daf014e64ba1b1d114f8384bed5ab84f`. The exact final PR head `660c92274e64f5a8786cf18e71d037bbaecc48ee` passed 993 tests plus workflow-YAML validation and compile checks in run `35759782638`; unchanged Phase 3 acceptance run `35759782621` passed.
- Follow-up: a later separately frozen decision is required before any demo order adapter can be implemented or enabled. No real Phase 8B PASS or Phase 9 design artifact has been executed.


### EXP-20260922-027 — Phase 9 locked demo-order protocol foundation

- Date: 2026-09-22
- Status: ACTIVE — SOURCE PROTOCOL MERGED / NO DEMO ORDER
- Protocol decision: DEC-056 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: implement only the deterministic post-risk request, dry-run journal, reconciliation, and structurally locked adapter boundary required by DEC-055 before any future MT5 mutation transport exists.
- Request source: exact existing Phase 3 `OrderIntent` values only; units and reserved risk are copied, never recomputed or widened.
- Deterministic identity: `fmp-phase9-demo-order-request-v1` binds exact DEC-055 design/champion/strategy/decision/symbol/direction/units/stop-target/timing identity and derives `fmp9-<24 hex>` client order IDs.
- Practice identity: provider, DEMO account fingerprint, server, and identity symbol mapping are copied from the exact DEC-055 design with no caller override surface.
- Protective geometry: mandatory direction-aware stop and optional target are validated against a reference price that is not a fill and causes no broker action.
- Dry-run evidence: `fmp-phase9-demo-dry-run-v1` validates the exact request while keeping submission, broker mutation, demo/live order, real-money, and Phase 10 flags false; writes are create-only.
- Reconciliation: `fmp-phase9-demo-reconciliation-v1` normalizes caller-supplied fixtures only, replays duplicate/unknown/orphan/missing-stop diagnostics from the snapshot itself, and performs no broker read.
- Adapter lock: `LockedDemoOrderAdapter` contains no broker/MT5 transport field; its only submission method validates the request then always raises `DemoExecutionLockedError`.
- CLI scope: unchanged Phase 9 design-only CLI; no `run-demo`, `submit-order`, `order`, `trade`, broker, or mutation command.
- Demo execution/order, live order, broker mutation, real-money trading, and Phase 10 authorized?: NO.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `97e8153ae7b8b00e0960ab95eba076dd027de982` passed 999 tests plus workflow-YAML validation and compile checks in run `35762091445`; unchanged Phase 3 acceptance run `35762091454` passed.
- Merge status: PR #148 merged DEC-056 to `main` at `c069e33fec82fc1e516120ee23923955f054bf89`. The exact final PR head `b3cfb9e1e2d2f0a3306a026566ad4b25df55a99b` passed 999 tests plus workflow-YAML validation and compile checks in run `35762297677`; unchanged Phase 3 acceptance run `35762297505` passed. Post-merge `main` runs `35762518616` and `35762518646` also passed.
- Follow-up: a later separately frozen decision is mandatory before any MT5 mutation transport can be implemented, wired, or enabled. No real Phase 8B PASS, Phase 9 design artifact, demo order, or broker mutation has been executed.


### EXP-20260922-028 — Phase 9 MT5 demo preflight and order-check foundation

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-057 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: add only the MT5-specific practice-account, symbol-contract, current-quote, exact volume translation, protective-stop validation, and non-mutating order-check layer required before any future broker mutation transport exists.
- Input boundary: exact DEC-055 demo design plus exact DEC-056 post-risk demo-order request.
- Backend boundary: `MT5DemoCheckBackend` exposes account/symbol/tick snapshots and `order_check` only; it exposes no `order_send`, submit, modify, cancel, or close-position method.
- Practice identity: exact accepted DEMO account fingerprint and server are asserted; no caller override surface exists.
- Volume: Phase 3/DEC-056 units remain authoritative and are translated by exact `units / trade_contract_size`; non-representable broker volume-grid requests fail closed rather than being resized or rounded.
- Market/stop validation: BUY uses current ask, SELL uses current bid; broker price grid and minimum stop-distance constraints are checked without widening/removing stops or targets.
- Order-check semantics: deterministic `fmp-phase9-mt5-demo-order-check-request-v1`, fixed GTC, broker filling mode, check-only deviation 0, and only normalized MT5 `retcode=0` is check-passed.
- Preflight evidence: successful source-only checks produce `fmp-phase9-mt5-demo-preflight-v1` with all execution/order/mutation/real-money/Phase-10 flags false; writes are create-only.
- CLI scope: unchanged Phase 9 design-only CLI; no broker-connected or order-capable command was added.
- Demo execution/order, live order, broker mutation, real-money trading, and Phase 10 authorized?: NO.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `19a6ad3f653b053d6c32e2f6e95dd05c999bddb1` passed 1005 tests plus workflow-YAML validation and compile checks in run `35766703078`; unchanged Phase 3 acceptance run `35766703266` passed.
- Merge status: PR #149 merged DEC-057 to `main` at `366f271ca951108cf8fdb1df01604817baa076dc`. The exact final PR head `b5e97f06658f487ad553241616ff53049c7f2fba` passed 1005 tests plus workflow-YAML validation and compile checks in run `35766872553`; unchanged Phase 3 acceptance run `35766872565` passed. Post-merge `main` runs `35767028347` and `35767028362` also passed.
- Follow-up: a later separately frozen decision is required before any backend containing `order_send` or any broker mutation method can exist. No real Phase 8B PASS, Phase 9 design/preflight artifact, demo order, or broker mutation has been executed.


### EXP-20260922-029 — Phase 9 gated MT5 mutation transport source

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-058 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: implement the MetaTrader5 Python mutation-capable infrastructure source while keeping the official FMP demo execution path hard-disabled.
- Identity continuity: current terminal login is hashed exactly as the Phase 8B bridge, `sha256(str(ACCOUNT_LOGIN))`; account mode/server/trade permissions are read from the connected terminal rather than accepted as caller overrides.
- Symbol policy: actual symbol execution/filling properties determine RETURN/FOK/IOC behavior; Market Execution requires allowed FOK or IOC and otherwise fails closed.
- Request integrity: future `order_send` receives the exact freshly checked DEC-057 request with no post-check resize, stop/target edit, symbol/account swap, or price-field mutation.
- Result semantics: `fmp-phase9-mt5-demo-send-result-v1` normalizes retcode/tickets/fill volume/price/bid/ask/comment/request ID; only retcode 10009 with full confirmed volume is marked completed.
- Reconciliation reads: active order/position fixtures are normalized with client-order comments and deterministic protective-stop presence identifiers.
- Hard gate: `DEMO_EXECUTION_SOURCE_ARMED=false`; no DEC-058 setter, config, environment variable, artifact, or CLI can change it. The official adapter checks the gate before any broker read or mutation.
- CLI scope: unchanged Phase 9 design-only CLI; no run-demo/order-send/trade/close/cancel/broker command was added.
- Demo execution/order, live order, FMP broker mutation, real-money trading, and Phase 10 authorized?: NO.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `daf97700e123a025db626ea2d18bc1e7a8fecde2` passed 1011 tests plus workflow-YAML validation and compile checks in run `35767811967`; unchanged Phase 3 acceptance run `35767812096` passed.
- Merge status: PR #150 merged DEC-058 to `main` at `03617bcd609b61084f4dd09690f9d2166b391a61`. The exact final PR head `46825d1138392baff7b71465704df17260c28d88` passed 1011 tests plus workflow-YAML validation and compile checks in run `35768044631`; unchanged Phase 3 acceptance run `35768044648` passed. Post-merge `main` runs `35768227486` and `35768227484` also passed.
- Follow-up: a later separately frozen decision must explicitly arm one bounded demo session and freeze its operator/journal/recovery boundary before any real practice-account order. No real Phase 8B PASS, Phase 9 design/preflight/session artifact, demo order, or broker mutation has been executed.


### EXP-20260922-030 — Phase 9 bounded first demo-session contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-059 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: freeze one exact post-risk request into a one-order, practice-only, UTC-day-bounded demo-session contract before the DEC-058 execution source lock can ever change.
- Arm identity: exact DEC-055 design, DEC-056 request/client ID, champion, strategy, symbol, accepted DEMO account/server, one operator approval reference, and `max_new_orders=1`.
- Risk-day guard: not-before/expiry must remain inside one UTC civil date; readiness requires `daily_halt_active=false`.
- Startup safety: exact DEC-056 reconciliation must be healthy; duplicate/unknown/orphan/missing-stop states fail closed and no auto-mutation is attempted.
- Ambiguity/idempotency: after one `SEND_ATTEMPTED` journal event the arm is spent regardless of eventual broker result.
- Journal: `fmp-phase9-demo-session-journal-v1` is create-only, hash-chained, identity-stable, sequence-contiguous, and every append is flushed/fsynced.
- Future send ordering: the durable SEND_ATTEMPTED event binds the freshly checked DEC-057 payload digest before any later-approved mutation call.
- Source lock: DEC-058 `DEMO_EXECUTION_SOURCE_ARMED=false` is unchanged; `BoundedDemoSessionController` still reaches the locked adapter and fails before broker access.
- CLI scope: unchanged design-only Phase 9 CLI; no arm/run/order/broker/mutation command and no repository-created real arm.
- Phase 9 acceptance / Phase 10 authorized?: NO. One first practice order would not by itself satisfy deployment review.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `c273bb5a21d865d09edefbd425f18c4049e58399` passed 1017 tests plus workflow-YAML validation and compile checks in run `35768964040`; unchanged Phase 3 acceptance run `35768964070` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required before a real arm can be created or the DEC-058 execution lock can change.


### EXP-20260922-031 — Phase 9 demo execution-arm artifact contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT MERGED / NO REAL ARM / NO DEMO ORDER
- Protocol decision: DEC-060 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: implement only the deterministic future operator execution-arm artifact over exact DEC-055/056/059 identities while keeping the DEC-058 source gate false.
- Input binding: exact demo design, exact post-risk request/client ID, exact DEC-059 session-arm and session-ready fingerprints, unchanged champion/strategy/symbol, accepted DEMO account/server, exact UTC window, exact operator approval reference, and max-new-orders=1.
- Override policy: the builder exposes no caller parameters for account/server/symbol/units, arm window, or approval reference; those values are copied from already validated upstream artifacts.
- Readiness guard: session-ready must be healthy, daily halt inactive, zero prior attempts, max-new-orders=1, and bound to the exact arm/design/request.
- Source-gate guard: construction fails closed if DEC-058 `DEMO_EXECUTION_SOURCE_ARMED` is anything other than false.
- Persistence: create-only `execution-arm.json` + manifest with deterministic fingerprint and byte SHA-256.
- CLI scope: unchanged Phase 9 design-only CLI; no arming/run-demo/submit-order/broker command.
- Demo execution/order, broker mutation, live order, real-money trading, and Phase 10 authorized?: NO.
- Real operator arm created?: NO.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `a62be09eda02f09b255211ea5dca8b63055ae361` passed 1023 tests plus workflow-YAML validation and compile checks in run `35771299138`; unchanged Phase 3 acceptance run `35771299314` passed.
- Merge status: PR #152 merged DEC-060 to `main` at `71cb40bd00970696cee91f4c35755ca87c9f3eab`. The exact final PR head `5694c7b54d0729e0340539aa280f126d7cc420e9` passed 1023 tests plus workflow-YAML validation and compile checks in run `35771474118`; unchanged Phase 3 acceptance run `35771474159` passed.
- Follow-up: a later separately frozen decision is required before a real arm can be materialized or the execution source gate may change.


### EXP-20260922-032 — Phase 9 offline demo-arm materialization

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION MERGED / NO REAL DEMO ORDER
- Protocol decision: DEC-061 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: add one local-only operator command that materializes the exact DEC-060 execution-arm package from already-frozen JSON evidence without MT5/broker access.
- CLI: adds only `materialize-arm --design --request --session-arm --session-ready --out-dir` beside `design-demo`.
- Override policy: no CLI option exists for strategy, symbol, units, reserved risk, stop/target, account/server/provider, client-order ID, UTC arm window, approval reference, or order count.
- Import boundary: `src/fmp/phase9/cli.py` directly imports only local artifact/validation code for materialization and does not directly import or instantiate the mutation backend, MetaTrader5 wrapper, or order-send runner.
- Gate refactor: the hard source lock remains `DEMO_EXECUTION_SOURCE_ARMED=false` in neutral `execution_gate.py`; DEC-058 mutation source and DEC-060 arming validation both consume that lock without adding a setter/config/env/artifact override.
- Persistence: materialization writes only create-only `execution-arm.json` and manifest; repository tests use temporary fixture directories only.
- Broker access/order_check/order_send performed?: NO.
- Demo execution/order, broker mutation, live order, real-money trading, and Phase 10 authorized?: NO.
- Real operator arm for an actual broker session created?: NO.
- Verification: exact source head `25f7a315266605097d51b92c2faca9364a1651db` passed 1025 tests plus workflow-YAML validation and compile checks in run `35772227156`; unchanged Phase 3 acceptance run `35772227085` passed.
- Merge status: PR #153 merged DEC-061 to `main` at `ad4dea51f537225f7bbb18335c68beebb9c58067`. The exact final PR head `b6584aff886dad7fac513cdeb57d3c86430b67c4` passed 1025 tests plus workflow-YAML validation and compile checks in run `35772414863`; unchanged Phase 3 acceptance run `35772414631` passed.
- Follow-up: a later separately frozen decision is required before a materialized arm can become runtime authority or the execution source gate can change.


### EXP-20260922-033 — Phase 9 demo runtime arm authority contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-062 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: accept one exact DEC-060/061 materialized demo arm as source-only runtime authority evidence without changing the DEC-058 execution source lock.
- Upstream chain: exact DEC-055 design, DEC-056 request/client ID, DEC-059 session arm/readiness, and DEC-060 execution-arm fingerprints are revalidated and bound.
- Runtime checks: current UTC must remain inside the unchanged arm window and not precede session readiness; daily halt must be inactive; one-order budget remains exactly one.
- Journal replay: exact DEC-059 journal identity is validated; event count and tip fingerprint are bound; any prior `SEND_ATTEMPTED` fails closed.
- Source isolation: runtime-authority source imports no MetaTrader5 backend or mutation adapter, adds no broker-connected CLI, and performs no broker access.
- Authorization: only `demo_runtime_arm_authority_ready=true`; `DEMO_EXECUTION_SOURCE_ARMED=false` and every demo/live order, broker-mutation, real-money, and Phase-10 flag remain false.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `f17f67c4407e6100abbb47c855fd564a88b46bc3` passed 1031 tests plus workflow-YAML validation and compile checks in run `35774162526`; unchanged Phase 3 acceptance run `35774162520` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required before the source execution gate can become true or any broker-connected runner may consume runtime-authority evidence.

- Merge status: PR #154 merged DEC-062 to `main` at `d0046f2b8119d34bf991ecb5d7f08136536a780a`. The exact final PR head `5fc6290b1a23cdee1d7d5acc72fb25284b9e38d2` passed 1031 tests plus workflow-YAML validation and compile checks in run `35774454431`; unchanged Phase 3 acceptance run `35774454262` passed. Post-merge `main` runs `35774570313` and `35774570327` also passed.
- Follow-up: a separately frozen decision is required before a broker-connected runtime preflight may consume the authority record; the source execution gate remains false and no demo order has been sent.


### EXP-20260922-034 — Phase 9 broker-connected demo launch preflight

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-063 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: consume exact DEC-062 runtime-authority evidence and perform only the final fresh DEMO account/symbol/tick reads, non-mutating order_check, and open-order/open-position reconciliation required before any later first-demo-order decision.
- Runtime guard: current UTC, daily halt, append-only journal prefix, exact journal identity, and zero SEND_ATTEMPTED events are revalidated before the first backend read.
- Backend boundary: `Phase9DemoLaunchPreflightBackend` exposes only account/symbol/tick reads, `order_check`, broker-orders read, and broker-positions read. It exposes no `order_send`, submit, cancel, modify, or close-position method.
- Fresh execution validation: exact DEC-057 no-resize volume, broker price-grid, stop-distance, target-geometry, filling-mode, practice-account identity, and retcode=0 order-check rules are reused.
- Fresh reconciliation: exact DEC-056 reconciliation must remain healthy; no automatic broker repair is permitted.
- Evidence: create-only `fmp-phase9-demo-launch-preflight-v1` binds exact runtime authority, current journal tip, account/symbol/tick evidence, order-check request/result, and reconciliation.
- Authorization: only `demo_launch_preflight_ready=true`; `DEMO_EXECUTION_SOURCE_ARMED=false` and every demo/live order, broker-mutation, real-money, and Phase-10 flag remain false.
- CLI: unchanged; no broker-connected or order-capable command was added.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `2f6a684f74058a7210e1613e2d9f6d729579b0bf` passed 1038 tests plus workflow-YAML validation and compile checks in run `35775307825`; unchanged Phase 3 acceptance run `35775308344` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required before the execution source gate can change or any runner may invoke `order_send`.

- Merge status: PR #155 merged DEC-063 to `main` at `4d053c8edfc7ff1325da50530405cc876e33ba61`. The exact final PR head `d87bc0547584c9b9f756fe99325ff0b1da95e23c` passed 1038 tests plus workflow-YAML validation and compile checks in run `35775591842`; unchanged Phase 3 acceptance run `35775591852` passed. Post-merge `main` runs `35775737773` and `35775737735` also passed.
- Follow-up: a separately frozen one-shot execution-permit contract is required before any future execution runner may be authorized; no real demo order has been sent.


### EXP-20260922-035 — Phase 9 one-shot demo execution permit contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-064 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: define only the immutable future one-shot execution-permit artifact over exact DEC-063 launch-preflight evidence.
- Exact binding: DEC-055 design, DEC-056 request/client ID, DEC-059 session arm/readiness, DEC-060 execution arm, DEC-062 runtime authority, DEC-063 launch preflight, champion/strategy/symbol, accepted DEMO account/server, UTC arm window, operator approval reference, and max-new-orders=1.
- Checked-request immutability: permit binds fresh order-check request/result fingerprints, healthy reconciliation fingerprint, and canonical SHA-256 of the exact checked MT5 request payload.
- Arm semantics: permit copies the exact one-order window and does not spend or widen it; future execution must still durably journal SEND_ATTEMPTED before any mutation call.
- Persistence: create-only `execution-permit.json` plus manifest.
- Source isolation: permit source imports no MetaTrader5 backend, mutation adapter, or broker runner and adds no CLI.
- Authorization: only `demo_execution_permit_artifact_ready=true`; `DEMO_EXECUTION_SOURCE_ARMED=false` and every execution/order/mutation/live/real-money/Phase-10 flag remain false.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `fc9fcc586fad03b90963ff636cb2275bbcbe1fd7` passed 1043 tests plus workflow-YAML validation and compile checks in run `35776256682`; unchanged Phase 3 acceptance run `35776256435` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required before any real execution runner may consume the permit or invoke `order_send`.


### EXP-20260922-036 — Phase 9 permit-aware one-shot demo runner source

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-065 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: implement the future one-shot permit-aware practice-order runner while keeping the DEC-058 execution source gate false.
- Upstream binding: exact DEC-055 design, DEC-056 request/client identity, DEC-059 session arm/readiness and journal, DEC-060 execution arm, DEC-062 runtime authority, DEC-063 launch preflight, and DEC-064 execution permit.
- Immediate checks: exact arm window, launch time ordering, daily halt inactive, exact permit journal count/tip, zero prior SEND_ATTEMPTED, one-order cap, practice-only identity, and exact checked MT5 request SHA-256.
- One-shot spend: future armed-path simulation fsyncs SEND_ATTEMPTED before any mutation call and never retries order_send.
- Send evidence: returned results are normalized through exact DEC-058 send-result semantics; broker-returned non-completion is distinct from transport ambiguity.
- Ambiguity: order_send exceptions spend the arm, journal SESSION_HALTED, prohibit retry, and still attempt one post-send reconciliation.
- Post-send reconciliation: exactly one broker-order/position read cycle is normalized through DEC-056 reconciliation; no automatic repair is allowed.
- Source lock: repository `DEMO_EXECUTION_SOURCE_ARMED=false`; current source fails before journal mutation and broker access. Armed-path tests patch only the runner-local gate and use fake in-memory backends.
- CLI: unchanged; no broker-connected or order-capable command added.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `54efe65ff66e90ff5939a11ad5bad704d9b60b70` passed 1049 tests plus workflow-YAML validation and compile checks in run `35779123073`; unchanged Phase 3 acceptance run `35779123145` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required before the execution source gate may be true in an operator path or the first practice-account order may actually be sent.


- Merge status: PR #157 merged DEC-065 to `main` at `94eb6d4af4f146e751f2baed86f9b85fae4e8cac`. The exact final PR head `797ca4c9f3f3af20367d47a47e0c2e2972d9cdf6` passed 1049 tests plus workflow-YAML validation and compile checks in run `35779313105`; unchanged Phase 3 acceptance run `35779312681` passed. Post-merge `main` runs `35779467788` and `35779467811` also passed.
- Follow-up: source-only construction is complete through the permit-aware one-shot runner. A separately approved first-demo execution decision is required before the execution source gate may be true in an operator path or any real practice-account order may be sent.


### EXP-20260922-037 — Phase 9 demo campaign evidence and acceptance contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-066 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: freeze the amount and quality of Phase 9 practice-account evidence required before a Phase 10 deployment review, before any practice result exists.
- Minimum evidence: at least 40 completed practice trades, 8 elapsed calendar weeks, 30 distinct demo-session dates, two represented strategy families, and two represented V1 pairs.
- Safety gate: zero practice-account assertion failures, live orders, real-money access, unauthorized broker mutations, duplicate client-order submissions, retries after durable SEND_ATTEMPTED, completed sends without protective stops, and daily-halt violations.
- Operational gate: zero journal-integrity failures, unresolved ambiguous sends, startup/post-send reconciliation failures, or restart/recovery failures; at least one restart/recovery drill; exact attempt accounting; requested-vs-fill completeness; and exact per-pair slippage sample accounting.
- Execution-cost gate: for every represented V1 pair, completed-send adverse entry slippage median <=0.5 pip and nearest-rank p95 <=1.0 pip.
- Financial evidence: demo return, expectancy, profit factor, and drawdown are diagnostic under DEC-066 and are reserved for the combined Phase 10 economic review rather than becoming a short-run demo promotion rule.
- Outcomes: NEED_MORE_DATA, safety rejection, operational rejection, execution-cost rejection, or PASS eligible only for a separate Phase 10 deployment review.
- Source isolation: compiler imports no MT5/backend/runner surface and performs no broker access.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `f105926b52b2b302bc549b50ce5ef21c4a269476` passed 1059 tests plus workflow-YAML validation and compile checks in run `35781835318`; unchanged Phase 3 acceptance run `35781835216` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. First-demo execution still requires a separately approved authorization decision.


- Merge status: PR #158 merged DEC-066 to `main` at `95f7001d98593d9d181b5176ad1f347352f667a4`. The exact final PR head `3c00e33eb38509d562c03d6139912fdfb007aa7a` passed 1059 tests plus workflow-YAML validation and compile checks in run `35781992487`; unchanged Phase 3 acceptance run `35781992474` passed. Post-merge `main` runs `35782129020` and `35782128865` also passed.
- Follow-up: Phase 9 demo evidence/acceptance criteria are frozen before any practice result. A separately approved first-demo execution authorization is still required before the source gate may be enabled in an operator path or any real practice-account order may be sent.


### EXP-20260922-038 — Phase 9 first-demo authorization packet contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO DEMO ORDER
- Protocol decision: DEC-067 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: produce one immutable human-review packet for the exact future first practice order without recording approval or enabling execution.
- Exact review binding: accepted DEMO account/server/provider, champion and strategy identity, family/timeframe, symbol/broker symbol, direction, units, MT5 volume, reserved USD risk, reference and checked prices, protective stop, optional target, fill mode, time-in-force, client-order ID, decision/executable timestamps, launch-preflight time, arm window, session operator reference, checked-request SHA-256, and exact DEC-064 execution-permit fingerprint.
- Acceptance context: packet binds the frozen DEC-066 obligations of 40 completed trades, 8 elapsed weeks, 30 demo-session dates, two represented strategy families, two represented V1 pairs, median adverse entry slippage <=0.5 pip, and p95 <=1.0 pip.
- Approval challenge: one deterministic authorization-challenge fingerprint is derived solely from the immutable order-review payload; builder-code changes do not change the challenge, while any review-detail change does.
- Independent defense-in-depth: checked MT5 request hash, MT5 side, client comment, broker symbol, stop, and target are rechecked locally even after upstream DEC-064 validation.
- Non-authorization: explicit execution approval remains unrecorded; source gate, demo execution/order, broker mutation, live order, real money, Phase 10, and Phase 11 remain false.
- Source isolation: no MetaTrader5 mutation adapter, runner, order_send, or SEND_ATTEMPTED dependency; CLI unchanged.
- Live/demo execution status: NOT RUN.
- Verification: exact source head `289dff872f3819c18ea37a2e33e27a35e27e3853` passed 1066 tests plus workflow-YAML validation and compile checks in run `35783034440`; unchanged Phase 3 acceptance run `35783034271` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately frozen decision is required to record explicit approval against the exact challenge and define any operator-only source-gate activation.


- Merge status: PR #159 merged DEC-067 to `main` at `a966147f31127b929d3a88e80d7ff7294a5c5fb4`. The exact final PR head `7c696843813df9be19cae9fd9cab4079ad38f300` passed 1066 tests plus workflow-YAML validation and compile checks in run `35783187529`; unchanged Phase 3 acceptance run `35783187315` passed. Post-merge `main` runs `35783318956` and `35783319029` also passed.
- Follow-up: the exact first-demo order can now be rendered as an immutable approval challenge, but no approval has been recorded. A separately approved decision must define explicit challenge-bound approval recording and any operator-only source-gate activation before a real practice order can be sent.


### EXP-20260922-039 — Phase 9 explicit approval record and gate-activation contract

- Date: 2026-09-22
- Status: ACTIVE — SOURCE CONTRACT VERIFIED / NO REAL APPROVAL / NO DEMO ORDER
- Protocol decision: DEC-068 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: define source-only challenge-bound explicit-approval and gate-activation artifacts without creating a real approval or enabling execution.
- Approval binding: exact DEC-067 packet/challenge, DEC-064 permit, request/client identity, DEMO account/server, arm window, opaque operator identity/reference, approval UTC, and exact statement `APPROVE FIRST DEMO ORDER <challenge>`.
- Approval timing: approval must be at/after launch preflight and inside the unchanged arm window.
- Activation binding: exact approval/packet/challenge plus activation UTC; activation must follow approval and remain inside the same arm window.
- Source semantics: fixture approval records may set `explicit_execution_approval_recorded=true`, but `demo_execution_source_armed=false`, runner activation remains unwired, and broker/live/real-money/Phase-10/Phase-11 authorizations remain false.
- Source isolation: no MetaTrader5, mutation adapter, runner import, order_send, SEND_ATTEMPTED, gate setter, environment override, config hook, or execution CLI.
- Real evidence status: no real Phase 8B acceptance/SHADOW_VALIDATED chain, no real Phase 9 artifact chain, no real approval record, and no demo order.
- Verification: exact source head `df64999f99aa8d5114b0a462e5d23723cb868fe1` passed 1075 tests plus workflow-YAML validation and compile checks in run `35784906657`; unchanged Phase 3 acceptance run `35784906607` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. A later separately approved operator-action decision is required before any real approval artifact, source-gate activation, runner wiring, or practice order.


- Merge status: PR #160 merged DEC-068 to `main` at `88d23744b23faf5035b2c67075af73b0e1c25abc`. The exact final PR head `c54ca6ae1a0bce9d74465039e85008c643d5fa28` passed 1075 tests plus workflow-YAML validation and compile checks in run `35785056511`; unchanged Phase 3 acceptance run `35785056455` passed. Post-merge `main` runs `35785181147` and `35785181186` also passed.
- Follow-up: challenge-bound approval and gate-activation schemas now exist, but no real approval record or activation has been created. A separately approved operator-action/runtime-wiring decision is required before the hard source gate can be enabled or the DEC-065 runner can consume a real activation contract.


### EXP-20260922-040 — Phase 9 approval-gated one-shot runtime wiring

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO REAL APPROVAL / NO DEMO ORDER
- Protocol decision: DEC-069 APPROVED BEFORE ANY PHASE 9 DEMO ORDER
- Purpose: wire one exact DEC-068 activation contract to the existing DEC-065 one-shot runner while preserving the repository hard source lock.
- Validator separation: immutable DEC-060/062/064/067/068 artifact validators are now independent of current source-gate state; their builders and create-only writers still require source-unarmed operation, and the artifacts themselves still bind all embedded non-authorization flags false.
- Runtime checks: exact DEC-068 activation lineage, current UTC inside the immutable arm window and at/after activation, daily halt inactive, journal integrity, zero prior SEND_ATTEMPTED, practice-only identity, one-order cap, and exact account/request/client/permit identities.
- Delegation: after the DEC-069 source-gate check, all send-attempt journaling, exact checked-request use, no-retry behavior, DEC-058 send-result normalization, ambiguity handling, and post-send reconciliation remain delegated to DEC-065.
- Repository safety: `DEMO_EXECUTION_SOURCE_ARMED=false`; no setter/env/config/artifact hook or order-capable CLI added. Armed-path unit tests patch the wrapper in-process and do not access a broker.
- Real evidence status: no real Phase 8B prospective campaign/acceptance/SHADOW_VALIDATED transition; no real Phase 9 artifact chain, approval, activation, demo order, or broker mutation.
- Verification: exact source head `b52c026324b67216f2060d120b13c36d30a6677d` passed 1080 tests plus workflow-YAML validation and compile checks in run `35786753220`; unchanged Phase 3 acceptance run `35786753236` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. After DEC-069, source construction for the first practice-order path is complete, but real execution still requires the real Phase 8B/Phase 9 evidence chain plus explicit operator action in a separately approved armed runtime.


- Merge status: PR #161 merged DEC-069 to `main` at `0569b2cafb97bf4529cc95224a0133423396d9b9`. The exact final PR head `123f89d9cd5e2559f57a1b24cfe61affceff8e25` passed 1080 tests plus workflow-YAML validation and compile checks in run `35786935231`; unchanged Phase 3 acceptance run `35786935239` passed. Post-merge `main` runs `35787170070` and `35787170138` also passed.
- Follow-up: source construction for the first practice-order path is complete. No real Phase 8B acceptance or Phase 9 artifact/approval/activation chain exists yet, so the next meaningful milestone is real prospective evidence and explicit operator action in a separately approved armed runtime; repository execution remains hard-locked.


### EXP-20260922-041 — Phase 8B prospective campaign readiness audit

- Date: 2026-09-22
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO REAL CAPTURE
- Protocol decision: DEC-070 APPROVED BEFORE ANY PHASE 8B PROSPECTIVE CAPTURE
- Purpose: add a read-only, non-authoritative readiness inspection over the real Phase 8B campaign directory and current fixed bridge identities.
- Readiness protocol: `fmp-phase8b-campaign-readiness-v1`.
- CLI: `readiness --campaign-dir <path>` prints one point-in-time JSON report only and writes no campaign artifact.
- Artifact checks: DEC-047 registration, optional DEC-048 start authorization, DEC-049 capture preflight, DEC-054 spread reference, and campaign terminal state are validated and cross-bound by exact SHA/fingerprint/portfolio identity.
- Bridge checks: exact required-symbol coverage, connector protocol, DEMO mode, common account/server, and frozen bridge-session IDs. The audit opens tails at current EOF but never calls `read_available` and therefore consumes no post-EOF tick/heartbeat evidence.
- Readiness semantics: ready only means current capture prerequisites align; it does not prove 15-second bridge liveness or 5-second quote freshness and is never consumed as authorization by `capture-segment`.
- Next actions: `authorize-start`, `freeze-spread-reference`, or `capture-segment`; terminal campaigns report `none-terminal`.
- Operator handoff: replaced the historical USDJPY-only workflow with the current `FMPPhase8BQuoteBridge.mq5` multi-symbol EURUSD/GBPUSD/USDJPY portfolio process while retaining AutoTrading OFF, fixed FILE_COMMON paths, approved DEMO servers, no-backfill semantics, and explicit non-authorization wording.
- Safety: no prospective segment started, no campaign artifact written by readiness, no broker mutation, no order API, no Phase 9 action, and repository `DEMO_EXECUTION_SOURCE_ARMED=false`.
- Verification: exact source head `a0bce886dc64e62eeafac9d642f63d13848c2ffb` passed 1085 tests plus workflow-YAML validation and compile checks in run `35789539447`; unchanged Phase 3 acceptance run `35789539375` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. The next meaningful action after merge is an explicit real operator Phase 8B campaign preparation/readiness/capture workflow; repository verification itself still performs none of those live actions.


- Merge status: PR #162 merged DEC-070 to `main` at `5e918a9a9ed7b9ab112d62993eee6f4e7672e186`. The exact final PR head `5a26f9c6cd38040871a841c8a17567b1785ff753` passed 1085 tests plus workflow-YAML validation and compile checks in run `35789729752`; unchanged Phase 3 acceptance run `35789729689` passed. Post-merge `main` runs `35789967258` and `35789967219` also passed; the merge-commit test run executed 1085 tests.
- Follow-up: Phase 8B source/operator preparation is complete. No real readiness inspection, prospective segment, campaign close/review, acceptance result, or SHADOW_VALIDATED transition has been executed. The next meaningful milestone is explicit real prospective shadow evidence on the accepted MT5 DEMO bridge; Phase 9 execution remains hard-locked.


### EXP-20260923-042 — Phase 8B prospective campaign progress preview

- Date: 2026-09-23
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO REAL CAPTURE
- Protocol decision: DEC-071 APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
- Purpose: provide a read-only in-campaign progress preview over clean DEC-052 prospective segments without creating closure/review/acceptance evidence.
- Aggregation parity: reuses the exact DEC-053 segment loader, duplicate/overlap checks, continuous aggregate simulation, deterministic replay, observation bounds, London-date coverage, and strategy-family/pair representation logic.
- Minimum parity: exact DEC-051 definitions for 8 elapsed weeks, 30 complete London dates, 40 completed 0.2-pip trades, 2 represented strategy families, and 2 represented pairs, including remaining amounts.
- Closeability diagnostic: reports whether all 0.2/0.5/1.0 scenarios currently have zero open/pending decisions and whether aggregate replay matches.
- Empty-campaign behavior: no clean closed segment returns PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS rather than protocol failure.
- Persistence: stdout JSON only; no closure directory, campaign-evidence artifact, review, acceptance, lifecycle transition, or terminal marker.
- Safety: all promotion/SHADOW_VALIDATED/Phase-9/order/broker/live/real-money authorization flags remain false.
- Verification: exact source head `2252f8889683992cdacce0d6080363ec3b19772f` passed 1089 tests plus workflow-YAML validation and compile checks in run `35801819236`; unchanged Phase 3 acceptance run `35801819264` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. Real prospective MT5 DEMO evidence remains the next operational milestone.


- Merge status: PR #163 merged DEC-071 to `main` at `e45f6a496885863be69f87fd2caa8c3f577b784e`. The exact final PR head `021aa2bc8f9337d4f1830985c2ec4ca03cd16f4f` passed 1089 tests plus workflow-YAML validation and compile checks in run `35801932548`; unchanged Phase 3 acceptance run `35801932553` passed. Post-merge `main` runs `35802013847` and `35802013896` also passed.
- Follow-up: Phase 8B now has read-only pre-capture readiness and in-campaign progress tooling. No real prospective capture, closure/review, acceptance result, SHADOW_VALIDATED transition, or Phase 9 artifact chain has been executed; real MT5 DEMO prospective evidence remains the next operational milestone.


### EXP-20260923-043 — Phase 8B interrupted segment observability amendment

- Date: 2026-09-23
- Status: ACTIVE — SOURCE IMPLEMENTATION VERIFIED / NO REAL CAPTURE
- Protocol decision: DEC-072 APPROVED BEFORE ANY PHASE 8B ACCEPTANCE RESULT
- Purpose: make DEC-071 progress truthfully report retained interrupted DEC-052 segment directories even when no clean segment has closed yet.
- Inventory: shared deterministic segment inventory reports sorted closed and unclosed segment-directory identities; non-directory entries remain outside campaign segment evidence.
- Empty/interrupted behavior: no closed segment still returns `PHASE8B_PROGRESS_NO_CLOSED_SEGMENTS`, but the true unclosed count/IDs are preserved rather than forced to zero.
- Mixed behavior: unclosed directories remain excluded from aggregate simulation, replay, coverage, trade counts, representation, and financial metrics.
- Identity hardening: a closed segment directory name must equal the immutable `segment_id` inside `prospective-segment.json`; renamed/copied closed directories fail closed before aggregation.
- Progress integrity: result now includes campaign terminal context, deterministic progress fingerprint, and validator-enforced count/list parity, sorted uniqueness, disjoint inventories, and all authorization flags false.
- Campaign-close parity: DEC-053 evidence still receives only the unclosed directory count; acceptance semantics are unchanged.
- Safety: no capture, repair, deletion, closure/review/acceptance artifact, broker mutation, Phase 9 action, or order is executed.
- Verification: exact corrected source head `1654564b4fc3cd971d369ea5717d0f7268aaf326` passed 1092 tests plus workflow-YAML validation and compile checks in run `35803297613`; unchanged Phase 3 acceptance run `35803297604` passed.
- Follow-up: merge only after the exact final bookkeeping head remains green. Real prospective MT5 DEMO evidence remains the next operational milestone.


- Merge status: PR #164 merged DEC-072 to `main` at `2732e00fa502219bf18de35ae861e72befe62661`. The exact final PR head `5efc050f31811e0f179638fc2c9bb83587eb22ef` passed 1092 tests plus workflow-YAML validation and compile checks in run `35803436296`; unchanged Phase 3 acceptance run `35803436276` passed. Post-merge `main` runs `35803529547` and `35803529528` also passed.
- Follow-up: interrupted prospective capture is now visible from the first failed attempt onward without being repaired or counted. No real prospective segment, campaign close/review, acceptance result, SHADOW_VALIDATED transition, or Phase 9 artifact chain has been executed; real MT5 DEMO prospective evidence remains the next operational milestone.


### EXP-20260923-044 — Phase 8A direct market-learning foundation

- Date: 2026-09-23
- Status: ACTIVE — SOURCE FOUNDATION / NO MODEL-TRAINING RESULT
- Protocol decision: DEC-073 APPROVED BEFORE ANY EXP-044 MODEL-TRAINING RESULT
- Purpose: restore the broader FMP learning objective by learning future market behaviour directly from leakage-safe market-state rows rather than training only on signals emitted by hand-written strategies.
- Universe: EURUSD, GBPUSD, USDJPY × 5m/15m/1h over accepted Phase 2 Dukascopy-derived BID/ASK history.
- Existing features: first generation reuses the 48 Phase 5 leakage-safe feature definitions; the historical `fmp-feature-v1` artifact is not rewritten or unlocked.
- Direct labels: exact 60m and 240m horizons from feature-row `available_at_utc`; future midpoint move plus hypothetical LONG/SHORT net pips at 0.2/0.5/1.0-pip adverse slippage; exact missing horizon is unavailable rather than shifted/interpolated.
- Evidence status: historical evidence is `RETROSPECTIVE_ALREADY_SEEN`; `untouched_oos=false`; no promotion authorization.
- Continuous learning: future shadow/demo observations may feed a later offline challenger retrain, but the active champion is immutable and cannot self-update after trades.
- Foundation merge: PR #166 merged the DEC-073 direct-outcome-label foundation to `main` at `b438ddd00bcc8b1f4b9adab0a0b84cc2777546df`. Exact PR head `0cea40d29139587c6707140c7f573228538d3403` passed 1101 tests plus workflow-YAML validation and compile in run `35836471528`; unchanged Phase 3 acceptance run `35836471517` passed.
- Full-history feature merge: PR #167 merged `fmp-market-feature-v1` source to `main` at `4e7af50751c3e74c29f7df82d05b6677fe4bd2ba`. Exact final PR head `0baa2848e9d4aeba975d959fc16e3c6421d65c91` passed 1107 tests plus workflow-YAML validation and compile in run `35837614313`; unchanged Phase 3 acceptance run `35837614254` passed. Post-merge `main` runs `35837744074` and `35837743994` also passed.
- Current deliverable: deterministic direct market-outcome labels plus a separate `fmp-market-feature-v1` full-history materialization path that reuses the exact 48 Phase 5 feature definitions while preserving the historical `fmp-feature-v1` lock. The manual `phase8a-exp044-market-features` workflow is frozen for nine EURUSD/GBPUSD/USDJPY × 5m/15m/1h cells over 2015-01-01 through 2026-08-20 inclusive, with deterministic double-generation and exact accepted Phase 2 artifact verification.
- Execution status: no authoritative EXP-044 full-history feature workflow has been dispatched yet; no model fit, model selection result, portfolio admission, shadow capture, demo order, broker mutation, live order, or real-money action exists.
- Existing-data rule: the EXP-044 feature workflow reuses the already accepted Phase 2 Dukascopy artifacts and verifies their frozen processed-manifest SHA-256 identities; it performs no new Dukascopy acquisition.
- Aggregate verification source: after all nine feature cells succeed, a dedicated evidence job verifies exact cell coverage, exact source hashes, every emitted artifact byte, the retrospective evidence label, and all non-promotion locks, then writes one deterministic feature-evidence fingerprint. This evidence still sets `model_fit_authorized=false`.
- Aggregate verifier merge: PR #169 merged to `main` at `f8e3b160c45dc346d22ad3aa8f5ac1a54df26174`. Exact final PR head `42875569e8d48862be20453b4963c57335904e45` passed 1111 tests plus workflow-YAML validation and compile in run `35840325472`; unchanged Phase 3 acceptance run `35840325448` passed. No EXP-044 historical feature workflow has been dispatched as a result of this merge.
- Source extension: a vectorized `fmp-market-outcome-grid-v1` layer now prepares the direct 60m/240m supervised targets from exact 1-minute BID/ASK opens. The three frozen adverse-slippage scenarios are stored side-by-side per observation/horizon to avoid tripling row count. Exact missing entry/exit timestamps are counted and excluded rather than shifted or interpolated. Outcome artifacts require a 64-character verified feature-evidence fingerprint and remain `model_fit_authorized=false`.
- Outcome materialization source: persisted aggregate feature evidence is reloaded and fingerprint-verified before use. Each requested cell must match its aggregate manifest SHA-256 and Phase 2 source identity; every feature parquet and every canonical 1-minute Dukascopy parquet used by the materializer is rechecked for size, SHA-256, row count, and schema before the outcome grid is written. The materializer is source-only and still emits `model_fit_authorized=false`.
- Outcome-grid merge: PR #171 merged to `main` at `4dfd9b4cc5d62d2585b027946a3056415fcd3ab7`; exact final PR head `cd6805af35865e589ad606ecd7065f1060ca474a` passed 1117 tests plus YAML/compile in run `35845107487`, and unchanged Phase 3 acceptance run `35845107495` passed.
- Outcome-materializer merge: PR #172 merged to `main` at `428541b310ccc806662818d2141bfe356df023d1`; exact final PR head `be55f852713c1544063b0590cd36207cd1417277` passed 1122 tests plus YAML/compile in run `35845611187`, and unchanged Phase 3 acceptance run `35845611278` passed.
- Outcome workflow source: `phase8a-exp044-market-outcomes` is manual and accepts one required successful feature-run ID. It validates that source run is the exact feature workflow, `workflow_dispatch`, successful, and from `main`; revalidates the feature-evidence fingerprint; rechecks the existing accepted Phase 2 Dukascopy ZIP/manifest identities; materializes the nine pair/timeframe outcome cells; and aggregates them into one deterministic outcome-evidence fingerprint. The aggregate evidence still sets `model_fit_authorized=false` and all shadow/demo/broker/live/real-money flags false. No outcome workflow has been dispatched.
- Outcome-workflow merge: PR #173 merged to `main` at `fc05230462d8743ba5780d3bd2633649e4019b00`; exact PR head `e29437e2ab93462b1a669797e973b7b18dfacd33` passed 1129 tests plus YAML/compile in run `35846186938`, and unchanged Phase 3 acceptance run `35846186891` passed. Post-merge main runs `35846386839` and `35846386975` passed.
- DEC-074 readiness source: after aggregate outcome evidence succeeds, the workflow re-downloads and revalidates the exact source aggregate feature evidence and cross-checks all nine cells. A readiness artifact may set `data_preparation_complete=true` and `model_protocol_source_open_authorized=true` only when outcome evidence binds the exact feature-evidence fingerprint, feature-manifest SHA-256, Phase 2 Dukascopy identity, and feature row count in every cell. It keeps `model_protocol_result_authorized=false`, `model_fit_authorized=false`, promotion false, and all shadow/demo/broker/live/real-money flags false.
- Follow-up: first dispatch and preserve the nine full-history feature artifacts plus aggregate feature evidence from merged `main`; then dispatch the outcome workflow against that exact successful feature-run ID and preserve its nine outcome cells plus aggregate outcome evidence. Only after both evidence layers exist may a separate predeclared model-training protocol freeze model families, preprocessing, chronological splits, targets, thresholds, and financial gates before any result-producing fit.

- DEC-075 execution observability source: a read-only status machine now distinguishes feature dispatch, feature success/evidence, outcome dispatch, outcome success/evidence, DEC-074 readiness, and protocol-source-open. It validates supplied workflow-run identity and persisted readiness fingerprints and fails closed on contradictory evidence. It creates no model-fit or trading authorization.
- DEC-075 merge: PR #176 merged to `main` at `212f3acb24a40084b5f19b24a5290ccb7be0930d`. Exact final PR head `ad0b7f94b5f44547e666ff03e512dcac02673d65` passed 1143 tests plus workflow-YAML validation and compile in run `35848603110`; unchanged Phase 3 acceptance run `35848603258` passed. Post-merge `main` tests run `35848748205` and Phase 3 acceptance run `35848748235` also passed. No EXP-044 feature or outcome workflow has been dispatched by this merge.

- DEC-076 execution optimization: before any EXP-044 feature/outcome run, both workflows were changed from nine pair/timeframe jobs to three pair jobs. Each pair now downloads and verifies its accepted Phase 2 Dukascopy artifact once, then processes 5m/15m/1h sequentially while still uploading the same nine per-timeframe artifacts and preserving the same aggregate evidence gates.
- DEC-076 merge: PR #178 merged to `main` at `b0c29b354470a27145847071a5f8b92fc87eb303`. Exact final PR head `5506add7da89c2ed47f34325882814c4ffb1130d` passed 1147 tests plus workflow-YAML validation and compile in run `35850179816`; unchanged Phase 3 acceptance run `35850179878` passed. Post-merge `main` tests run `35850302402` and Phase 3 acceptance run `35850302338` also passed. No EXP-044 feature or outcome workflow had been dispatched at the time of this merge.
- Point-in-time source availability check on 2026-09-23: accepted Phase 2 artifacts 10325737935, 10326096831, and 10327600628 were all downloadable; downloaded ZIP SHA-256 values exactly matched the frozen EURUSD, GBPUSD, and USDJPY identities already recorded by Phase 2.

- DEC-077 outcome execution optimization: the outcome workflow now uses one pair-level materializer per symbol. After all three feature cells bind the same accepted Phase 2 processed-manifest identity, the 140 one-minute monthly partitions are checksum-verified/read once and the same quote frame is reused sequentially for 5m/15m/1h. Regression tests require exact manifest equivalence with three independent single-cell materializations. No EXP-044 result-producing workflow had run before this amendment.

- DEC-077 merge: PR #180 merged to `main` at `30c500136283117ac24bad734abbc30b34831d46`. Exact final PR head `653b76866bae9dad299866c986a455d6f535430e` passed 1149 tests plus workflow-YAML validation and compile in run `35851579729`; unchanged Phase 3 acceptance run `35851579622` passed. Post-merge `main` tests run `35851703196` and Phase 3 acceptance run `35851703084` also passed.
- DEC-078 source availability gate: the accepted Phase 2 artifact metadata is now a precondition for both EXP-044 workflows. On 2026-09-23 EURUSD artifact `10325737935` (182037581 bytes), GBPUSD `10326096831` (190706384 bytes), and USDJPY `10327600628` (160033414 bytes) were non-expired and retained the frozen SHA-256 identities. EURUSD/GBPUSD expire at `2026-12-12T20:57:47Z`; USDJPY expires at `2026-12-12T21:42:34Z`. The workflow now requires at least 12 hours of remaining lifetime before heavy work begins.

- DEC-078 merge: PR #181 merged to `main` at `e2675cc6f0bac096895e422531443d34230d7109`. Exact final PR head `758cfc34d04af73ae57c224fa8b39109a68042a3` passed 1155 tests plus workflow-YAML validation and compile in run `35852173729`; unchanged Phase 3 acceptance run `35852173707` passed. Post-merge `main` tests run `35852290238` and Phase 3 acceptance run `35852290251` also passed.
- DEC-079 outcome memory optimization: pair-level outcome materialization still validates each complete 55-column feature parquet by size, SHA-256, schema, and row count, but retains only six identity/timing columns in memory for labeling. Projected-label output is required to be exactly equivalent to the full-feature builder.
- DEC-079 merge: PR #182 merged to `main` at `8a6628ed967c1f0318cc522a837554676519194e`. Exact final PR head `fafb8d677422ec924656756ecbadc28ba04d9035` passed 1157 tests plus workflow-YAML validation and compile in run `35852816657`; unchanged Phase 3 acceptance run `35852816582` passed. Post-merge `main` tests run `35852996238` and Phase 3 acceptance run `35852996232` also passed. No EXP-044 feature or outcome workflow had been dispatched at the time of this merge.

- DEC-080 feature execution optimization: each pair/timeframe Phase 2 derived-bar source is now checksum-verified/read once and reused for two sequential feature builds. The A/B outputs remain separately materialized and byte-compared, and regression tests require exact equivalence with the existing single-cell generator. No EXP-044 result-producing workflow had run before this amendment.

- DEC-080 merge: PR #184 merged to `main` at `64b43076751d576212015f40219264bde1d9ff97`. Exact corrected PR head `0d51aeba38d8e95fefb16f75d1dc6df4ba25965c` passed 1159 tests plus workflow-YAML validation and compile in run `35854983964`; unchanged Phase 3 acceptance run `35854983892` passed. Post-merge `main` tests run `35855107489` and Phase 3 acceptance run `35855107485` also passed. No EXP-044 feature or outcome workflow had been dispatched at merge time.
- DEC-081 operator launch source: a dry-run-by-default CLI now reproduces the exact manual feature/outcome dispatch commands while requiring clean merged `main`, exact repository identity, GitHub CLI authentication, no duplicate manual-main run, and (for outcomes) an exact successful feature-run identity. The helper itself claims no workflow result and authorizes no model/trading action.

- DEC-081 merge: PR #185 merged to `main` at `9895ec60ebedadc653f0ccf626d128a881de17e4`. Exact PR head `9be7dc5baebaffc9f35ae68972ed9dc0a21a6d36` passed 1165 tests plus workflow-YAML validation and compile in run `35855512952`; unchanged Phase 3 acceptance run `35855512940` passed. Post-merge `main` tests run `35855680240` and Phase 3 acceptance run `35855680389` also passed. No EXP-044 feature or outcome workflow had been dispatched at merge time.
- DEC-082 operator preflight: the manual helper now validates the exact live Phase 2 source artifact metadata before either stage and, before outcome preparation, downloads/fingerprint-validates the exact aggregate feature-evidence artifact bound to the successful feature run. The outcome workflow still independently repeats run/evidence validation.

- DEC-082 merge: PR #186 merged to `main` at `b825da0861d4bc5e550ef431ad12630607e3c545`. Exact PR head `f521404f38c8f6238281e3c123f994a841b9b32f` passed 1167 tests plus workflow-YAML validation and compile in run `35856107959`; unchanged Phase 3 acceptance run `35856107881` passed. Post-merge `main` tests run `35856298774` and Phase 3 acceptance run `35856298784` also passed. No EXP-044 feature or outcome workflow had been dispatched at merge time.
- DEC-083 readiness inspection source: the operator can now verify exact successful feature/outcome runs, download their aggregate evidence/readiness artifacts, and require the existing DEC-075 status machine to rebuild/cross-bind the chain as exactly `MODEL_PROTOCOL_SOURCE_OPEN`. This mode performs no workflow dispatch and does not authorize a model fit.

- DEC-084 preservation source: a manual merged-main workflow preserves the exact original Phase 2 ZIP bytes as a draft-verified GitHub release before publication. The release contract freezes original Actions IDs, source run/head, ZIP hashes/sizes, processed-manifest hashes, tag/title, and asset names. The current DEC-081/082/083 operator is extended with a dry-run-by-default `preserve-phase2` stage. No new data acquisition, research result, or model/trading authorization is introduced.

- DEC-084 merge: PR #190 merged to `main` at `5885d0bd9ee58f9ad9701742f6e7d4ae009f248c`. Exact PR head `d39280067f3868883edb983b147b7b6427e10c56` passed 1180 tests plus workflow-YAML validation and compile in run `35859236605`; unchanged Phase 3 acceptance run `35859236646` passed. Post-merge `main` tests run `35859370971` and Phase 3 acceptance run `35859371028` also passed. The preservation workflow was not dispatched and no release existed at merge time.
- DEC-085 source fallback: source availability is now resolved once for the full three-symbol bundle. Healthy original Actions artifacts remain preferred. If that complete bundle is unavailable, only the fully validated published DEC-084 release may be used, with all three pairs switched together and local ZIP/manifest revalidation still mandatory. No EXP-044 result-producing workflow had run before this amendment.

- DEC-085 merge: PR #191 merged to `main` at `8694f0fc07905347f08f40a37a0861eab14756ee`. Exact corrected PR head `7aa2d21003baa254d9ee8fecfeaac70df366e3f0` passed 1189 tests plus workflow-YAML validation and compile in run `35860573200`; unchanged Phase 3 acceptance run `35860573249` passed. Post-merge `main` tests run `35860816200` and Phase 3 acceptance run `35860816185` also passed. No preservation release and no EXP-044 preservation/feature/outcome run existed after merge.
- DEC-086 continuation planner source: the operator now has a read-only `next` mode that requires unique manual-main workflow histories and reports preservation, feature, outcome, or readiness progression without dispatching anything. It reuses the existing exact preservation/evidence/readiness validators rather than inventing a parallel authorization path.

- DEC-087 operator advance source: a dry-run-by-default `advance` command now reuses DEC-086 `next`, binds only the three dispatch-required states to their exact commands, replans immediately before explicit execution, and submits at most one workflow dispatch. Review/in-progress/readiness states remain non-mutating and failed runs are never automatically retried. No EXP-044 preservation/feature/outcome result is created by this source change.

- DEC-087 merge: PR #193 merged to `main` at `83594bb3b3870a17233b7839d0d331bf58d841d3`. Exact corrected PR head `0b9f3394ecf020be5f923cf55d39e7fa58b1433a` passed 1195 tests plus workflow-YAML validation and compile in run `35863676652`; unchanged Phase 3 acceptance run `35863676644` passed. Post-merge `main` tests run `35863827077` and Phase 3 acceptance run `35863826964` also passed. No EXP-044 preservation/feature/outcome workflow or preservation release existed after merge.

## EXP-20260926-060 — fit-temporal residual regime-balance utility implementation repair

- **Date:** 2026-09-26
- **Phase:** 8A direct market-learning track
- **Hypothesis:** preserving the frozen EXP-059 regime-balance protocol while correcting only the four breadth-metadata predecessor-depth accesses may allow the intended regime-balance ranking to complete and produce a temporally stable model challenger.
- **Universe:** EURUSD, GBPUSD, USDJPY; 5m, 15m, 1h; 60m and 240m horizons.
- **Protocol:** DEC-253 implementation-only repair; DEC-254 deterministic core; DEC-255 artifact contract; DEC-256 workflow/runtime freeze; DEC-257 terminal review.
- **Historical run:** `36260155597`, head `0062546fda38bfc768122cf03b9a4d69d1b8e0b7`, attempt 1, success.
- **Aggregate artifact:** `10912798284`, digest `sha256:9090a1a1c7849c703eaa38e5571a36a65f5a47f250c6c0e3a7e21777367b8bc9`.
- **Evidence fingerprint:** `52a840d0919992e1fe9ef3342ddefe46cfb1ad8ccd23c8dfe55963d4c1669b37`.
- **Search accounting:** 18 cells; 54 budget variants; 28 available; 26 budget-unavailable; 26,392 utility-eligible selection rows.
- **Result:** exactly two aggregate-gate passes, both USDJPY/5m/60m (budgets 500 and 1000). Their directional-candidate counts across the four frozen selection windows are `0/0/27/473` and `0/3/105/892`. Neither passes temporal stability.
- **Conclusion:** technically successful negative result. Zero stable selection passes, zero selected cells, zero validation passes, zero retrospective-holdout passes, and zero accepted model candidates. The repaired implementation completed the intended experiment, but the tested regime-balance formulation did not produce a robust challenger.
- **Rerun/replacement:** forbidden for EXP-060.
- **Deployment effect:** none. Promotion, shadow/demo, broker, live-order, real-money, and trading remain unauthorized.

### EXP-20260927-061 — Discovery-first market-state pattern mining

- Date: 2026-09-27
- Status: CLOSED — HISTORICAL RUN #2 TERMINAL FAILURE / SLOT CONSUMED / NO RETRY
- Protocol decisions: DEC-270 protocol; DEC-271 deterministic in-memory core; DEC-272 market-learning adapter/evidence; DEC-273 verified range-limited loader; DEC-274 run contract; DEC-275 dormant workflow/CLI source; DEC-276 locked active-workflow installation; DEC-277 gate-proof contract; DEC-278 read-only proof operator; DEC-279 one-shot proof executor; DEC-280 reviewed gate-proof freeze; DEC-281 source-only historical-run authorization; DEC-282 read-only historical-slot operator; DEC-283 repository-hosted read-only historical-plan proof; DEC-284 reviewed historical-plan proof freeze; DEC-285 one-shot historical runtime authorization; DEC-286 read-only historical execution operator; DEC-287 repository-hosted historical execution plan proof; DEC-288 reviewed historical execution-plan proof freeze; DEC-289 one-shot historical executor; DEC-290 predeclared historical terminal review; DEC-292 terminal failure freeze
- Purpose: derive interpretable repeated market-state/future-outcome hypotheses from the data without requiring a predefined strategy family.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Outcome horizons: 60m, 240m
- Discovery: 2015-01-01 to 2018-01-01 exclusive.
- Confirmation: 2018-01-01 to 2019-01-01 exclusive.
- Validation: 2019-01-01 to 2023-01-01 exclusive.
- Reserved robustness block: 2023-01-01 to 2026-08-21 exclusive; CLOSED TO EXP-061.
- State vocabulary: exactly 20 leakage-safe continuous features in LOW/MID/HIGH empirical-tertile states plus one deterministic five-state session dimension.
- Search depth: 1 or 2 distinct state predicates.
- Maximum search: 65 atomic states; 2,075 admissible state patterns per cell/horizon; 4,150 LONG/SHORT directional hypotheses per cell/horizon; 74,700 maximum directional hypotheses globally.
- Discovery shortlist cap: 10 per cell/horizon; 180 global.
- Frozen validation cap: 3 per cell/horizon; 54 global.
- Primary cost outcome: 0.5-pip adverse slippage per fill.
- Stress outcome: 1.0-pip adverse slippage per fill.
- Evidence label: RETROSPECTIVE_ALREADY_SEEN.
- Untouched OOS?: NO.
- Output meaning: PATTERN_HYPOTHESIS_NOT_EXECUTABLE_STRATEGY.
- Historical source opened?: YES — 2015-2022 only; reserved 2023-2026 remained closed.
- Discovery run executed?: YES — run `36335879839`, workflow run #2 / attempt 1, head `a7b3bc2d0b196da2631b64c19331efb3af12c98e`, terminal FAILURE. Preflight succeeded; all 18 discovery cells failed before producing cell evidence; aggregate was skipped; only preflight artifact `10937316246` persisted.
- Promotion/shadow/demo/live authorized?: NO.
- Conclusion: IMPLEMENTATION_FAILURE — `market_learning_adapter.adapt_feature_frame` forwarded non-finite warm-up feature values instead of normalizing them to null. Representative failures were `realized_vol_1h` / `realized_vol_8h must be finite or null`. This is not a negative market-pattern result.
- Implementation status: DEC-270 through DEC-290 built, proved, authorized, and executed the sole historical slot. DEC-289 executor run `36335739823` successfully submitted run #2 and froze executor artifact `10936194549`. Historical run `36335879839` then failed in all 18 cells at feature adaptation because Phase-5 warm-up/non-finite values were not normalized to null. DEC-292 freezes the failure as an implementation/input-normalization defect. EXP-061 has no usable cell or aggregate result and cannot be retried.
- Next gate: open a new EXP-062 repair identity. Preserve DEC-270 research semantics and exact 2015-2022 sources, but normalize non-finite continuous feature warm-up/missing values to `None` at the adapter boundary before any new historical execution slot is considered.


### EXP-20260927-062 — Discovery adapter non-finite normalization repair

- Date: 2026-09-27
- Status: ACTIVE — REPAIR VERIFIED + ACTIVE WORKFLOW INSTALLED LOCKED + ONE-SHOT PROOF EXECUTOR SOURCE + READ-ONLY PROOF RESULT REVIEW / HISTORICAL EXECUTION LOCKED
- Protocol decisions: DEC-293 isolated implementation-only normalization repair; DEC-294 read-only real-data adapter proof; DEC-295 predeclared adapter-proof review; DEC-296 predeclared proof-content review; DEC-297 verified adapter-proof result freeze; DEC-298 run/evidence contract; DEC-299 dormant workflow/CLI source; DEC-300 locked active-workflow installation; DEC-301 gate-proof terminal contract; DEC-302 read-only proof operator; DEC-303 one-shot proof executor; DEC-304 read-only proof-result review; DEC-270 research semantics preserved.
- Predecessor: closed EXP-20260927-061 / DEC-292 failure freeze.
- Hypothesis: EXP-061's all-cell failure was caused by representation mismatch at the adapter boundary; normalizing Phase-5 non-finite missing/warm-up continuous values to `None` should allow the unchanged discovery protocol to consume the accepted historical feature artifacts.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): 5m, 15m, 1h
- Outcome horizons: 60m, 240m
- Discovery: 2015-01-01 to 2018-01-01 exclusive.
- Confirmation: 2018-01-01 to 2019-01-01 exclusive.
- Validation: 2019-01-01 to 2023-01-01 exclusive.
- Reserved robustness block: 2023-01-01 to 2026-08-21 exclusive; CLOSED.
- Research/search semantics changed?: NO.
- Adapter repair: numeric NaN/+inf/-inf in continuous feature values -> `None`; finite values unchanged; session booleans and outcomes remain strict.
- Historical source opened?: NO under EXP-062.
- Historical run executed?: NO.
- Candidate compilation/demo/live authorized?: NO.
- Conclusion: ADAPTER_REPAIR_VERIFIED_ON_ACCEPTED_REAL_DATA.
- Next gate: merge DEC-300/301/302/303/304 after green checks. DEC-303 may submit exactly one proof run; DEC-304 must review the actual fail-closed proof and a later immutable freeze must bind its exact evidence before any historical-result slot is considered.

### EXP-20260927-062 — DEC-305 source-only freeze preparation

- DEC-305 freeze builder implemented for a future valid DEC-304 reviewed proof result.
- Actual EXP-062 proof runtime evidence is still required; no run/artifact identity is
  fabricated in source.
- Historical-result slot remains closed.
- Historical execution, candidate compilation, Phase 8B, demo/live, real-money, and
  trading remain unauthorized.


### EXP-20260927-062 — DEC-306 runtime gate-proof freeze

- Authoritative DEC-303 executor run: `36358278933`, run #1 / attempt 1, SUCCESS.
- Authoritative EXP-062 gate proof: `36358289723`, run #1 / attempt 1, expected FAILURE at the locked execution gate.
- Proof output: one preflight artifact only; zero cell-result artifacts; zero aggregate-result artifacts.
- DEC-305 reviewed-freeze fingerprint:
  `fadd6e512b95179fa682d05c8550c914db81e559d9c0ad8da0bedb03bb43a096`.
- Downloaded executor/proof evidence is bound by raw and canonical SHA-256 hashes in DEC-306.
- Redundant bootstrap executor run `36360111479` was run #2 / attempt 1 and failed closed before dispatch; it created no second proof and consumed no historical slot.
- Historical source opened under EXP-062?: NO.
- Candidate compilation/demo/live authorized?: NO.
- Next gate: source-only one-slot historical-run authorization for 2015-2022 only; reserved 2023-2026 remains closed.


### EXP-20260927-062 — DEC-307 one-slot source authorization

- Frozen proof run `36358289723` remains excluded from historical-result slot consumption.
- Historical-result slot source-authorized?: YES, for at most one future run #2 / attempt 1.
- Historical-result dispatch authorized?: NO.
- Historical discovery execution authorized?: NO.
- Discovery result production authorized?: NO.
- Historical research window remains 2015-2022 only.
- Reserved 2023-2026 robustness block remains CLOSED.
- Rerun/retry/replacement, candidate compilation/promotion, Phase 8B, demo/live, real-money, and trading remain unauthorized.
- Next gate: clean-main read-only historical-slot operator.


### EXP-20260927-062 — DEC-308 read-only historical-slot operator

- Exact-main read-only historical planner implemented.
- Empty-slot plan evidence: `gh workflow run phase8a-exp062-discovery.yml --ref main`.
- Execute mode available?: NO.
- Historical-result dispatch/execution authorized?: NO.
- Any later run #2 removes the plan command and routes to review.
- Reserved 2023-2026 data, candidate compilation/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- Next gate: repository-hosted read-only proof of the merged-main slot plan.


### EXP-20260927-062 — DEC-309 repository-hosted plan proof

- Read-only push-to-main proof workflow added for DEC-308.
- First proof run / attempt must be 1 / 1 on exact merged main.
- Proof executes only the planner and uploads only historical-plan.json.
- The future discovery dispatch command is verified as data and is not executed.
- Historical dispatch/execution/result production remains unauthorized.
- Reserved 2023-2026, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- Next gate after real successful proof: immutable plan-proof review/freeze.



### EXP-20260927-062 — DEC-310 historical-plan review preparation

- Added a source-only reviewer for future DEC-309 runtime plan-proof evidence.
- Requires run #1 / attempt 1 success, one successful plan job, one non-expired plan
  artifact, and exact slot-available DEC-308 plan content.
- Records raw and canonical plan SHA-256 hashes.
- Performs no dispatch or historical execution.
- Reserved data, candidates, demo/live, real-money, and trading remain unauthorized.

### EXP-20260927-062 — DEC-311 concrete historical-plan proof freeze

- DEC-309 read-only plan proof run `36403342301`, run #1 / attempt 1, completed successfully on merged head `95c193343a905acd40daf0eea5d27d55fd2537e1`.
- Sole plan job: `108866149073`, success.
- Sole plan artifact: `10960559187`, digest `sha256:07679d85ea3ee0a9373bbd78363ab98eb973377ace6d68828528f91188ff3cf8`.
- Independent artifact ZIP SHA-256 matches the GitHub digest exactly.
- Frozen plan raw SHA-256: `ac34769d589dbcc18a056d1ebaf960b6881f943f221d771e80216df32d313672`.
- Frozen plan canonical SHA-256: `d6cd04c0c29a2e82da12e687ce56ae80387f7ad3c9727b23018ee548684e62a6`.
- Historical-result attempt count remains zero; source-authorized slot remains unconsumed.
- Historical dispatch/execution/result production authorized?: NO.
- Reserved 2023-2026 data, candidate compilation/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- Next gate: source-only historical execution authorization contract with no dispatch path.

### EXP-20260927-062 — DEC-312 one-shot historical runtime authorization

- Concrete DEC-311 reviewed plan proof is the prerequisite.
- Historical execution source-authorized?: YES.
- Valid runtime identity: EXP-062 discovery workflow run #2 / attempt 1 only.
- Historical-result dispatch authorized?: NO.
- Historical discovery/result production inside exact run #2 runtime?: YES.
- Historical research range remains 2015-2022 only.
- Reserved 2023-2026 robustness block remains CLOSED.
- Rerun/retry/replacement, candidate compilation/promotion, Phase 8B, demo/live, real-money, and trading remain unauthorized.
- Next gate: read-only exact-main historical execution operator; no execute mode.

### EXP-20260927-062 — DEC-313 read-only historical execution planner

- Exact-main execution planner implemented for the one DEC-312 run #2 / attempt 1 runtime.
- Empty-slot plan evidence: `gh workflow run phase8a-exp062-discovery.yml --ref main`.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Run #2 presence immediately removes the command and consumes the slot.
- Reserved 2023-2026 data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- Next gate: repository-hosted read-only execution-plan proof.

### EXP-20260927-062 — DEC-314 repository-hosted execution-plan proof

- Push-to-main read-only proof workflow added for DEC-313.
- Proof requires first workflow run / attempt 1 / 1 and exact DEC-311/312/313 source blobs.
- Proof runs only the execution planner and uploads only `historical-execution-plan.json`.
- Future discovery command is checked as data and is not executed.
- Historical-result dispatch remains unauthorized.
- Reserved 2023-2026 data and all candidate/demo/live/trading paths remain locked.
- Next gate after actual success: concrete execution-plan proof review/freeze.

### EXP-20260927-062 — DEC-315 execution-plan proof reviewer

- Source-only reviewer prepared for future successful DEC-314 runtime evidence.
- Requires run #1 / attempt 1 success, one successful proof job, one non-expired artifact, and exact DEC-313 plan content.
- Binds raw and canonical execution-plan SHA-256 hashes.
- Historical-result dispatch/execute mode authorized?: NO.
- Reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- Next gate after actual proof: immutable concrete execution-plan freeze.

### EXP-20260927-062 — DEC-316 reviewed execution-plan freeze source

- Deterministic freeze builder added for a valid future DEC-315 reviewed result.
- No runtime ids or hashes are fabricated before DEC-314 evidence exists.
- Freeze preserves the actual proof run/job/artifact ids, artifact digest, plan hashes, and reviewed source blobs.
- Historical-result dispatch/execute mode authorized?: NO.
- Target historical runtime remains run #2 / attempt 1 only.
- Reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- Next gate after real proof: concrete runtime-evidence binding before a one-shot dispatcher.

### EXP-20260927-062 — DEC-317 concrete execution-plan runtime freeze

- Bound real DEC-314 proof run `36414282818`, job `108901556593`, artifact `10966632240`.
- GitHub artifact digest and independently recomputed ZIP SHA-256 both equal `9299ebfd344c0bd2a66ccd6e29339e035840c8b4204cbfc16bb6d3e938a53254`.
- Frozen plan raw SHA-256: `594b5bd129a93ad7b07f69e00826251dd693f1bb388e6b4dff64eda0b34a7c72`.
- Frozen plan canonical SHA-256: `152bbb90efe3941f1338c73cf24f91f10a877cda3ee5c46f08c4f556d653a12f`.
- Replays DEC-315 review and DEC-316 freeze; expected DEC-316 fingerprint `7c7d99f4c89aac4e11d27536b9f8d2d39322672a9a0332f141d1d86f93b19be3`.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Historical dispatch/execute mode authorized?: NO.
- Reserved data and all candidate/demo/live/trading paths remain locked.

### EXP-20260927-062 — DEC-318 dispatch source contract

- Concrete DEC-317 runtime freeze is the prerequisite.
- One-shot dispatch source contract authorized?: YES.
- Historical-result dispatch authorized?: NO.
- Historical executor available?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Reserved 2023-2026 data and all candidate/demo/live/trading paths remain locked.
- Next gate: read-only current-main one-shot dispatch operator.

### EXP-20260927-062 — DEC-319 read-only dispatch planner

- Current-main one-shot dispatch planner implemented.
- Empty-slot command evidence: `gh workflow run phase8a-exp062-discovery.yml --ref main`.
- Actual dispatch authorized?: NO.
- Historical executor available?: NO.
- Execute mode available?: NO.
- Existing run #2 immediately consumes the slot and removes the command.
- Reserved data and all candidate/demo/live/trading paths remain locked.
- Next gate: repository-hosted read-only dispatch-plan proof.

### EXP-20260927-062 — DEC-320 read-only dispatch-plan proof

- Repository-hosted first-run/attempt-1 proof prepared for DEC-319.
- Exact DEC-317/318/319 sources are pinned.
- Proof runs only the planner and uploads only `historical-dispatch-plan.json`.
- Actual workflow dispatch/executor authority remains NO.
- Target remains run #2 / attempt 1 while the slot is empty.
- Reserved data and all candidate/demo/live/trading paths remain locked.
- Next gate after actual success: concrete dispatch-plan proof review/freeze.

### EXP-20260927-062 — DEC-321 dispatch-plan proof reviewer

- Source-only reviewer prepared for future DEC-320 runtime evidence.
- Requires first proof run/attempt success, one successful job, one artifact, and exact DEC-319 plan content.
- Records raw and canonical plan SHA-256 hashes.
- Actual dispatch/executor/execute mode remain NO.
- Target remains run #2 / attempt 1 while the slot is empty.
- Reserved data and all candidate/demo/live/trading paths remain locked.

### EXP-20260927-062 — DEC-322 reviewed dispatch-plan freeze source

- Deterministic freeze builder prepared for valid future DEC-321 review evidence.
- Preserves real run/job/artifact ids and plan hashes without inventing them.
- Actual historical dispatch/executor/execute mode remain NO.
- Target remains run #2 / attempt 1 while the slot is empty.
- Reserved data and all candidate/demo/live/trading paths remain locked.

### EXP-20260927-062 — DEC-323 concrete dispatch-plan runtime freeze

- Bound real DEC-320 proof run `36418793172`, job `108916232597`, artifact `10967344018`.
- GitHub artifact digest and independently recomputed ZIP SHA-256 both equal `ca0f1156fab234327bbcdd9c3150cb7904ed6def230f035019b2139c4c523adf`.
- Frozen dispatch-plan raw SHA-256: `a6fa5f3a7f3f45df5d64efe1661a5b17887f88fded31e1cbb1620df5b18a95d1`.
- Frozen dispatch-plan canonical SHA-256: `41ca6c710d8750851350c2108b42970501a5efa14481cff61e2a66877ee90f6d`.
- Replays DEC-321 review and DEC-322 freeze; expected DEC-322 fingerprint `b7d3e5461511c8e14dd4402028ad24daefcf431cece3b59575588ba915db510e`.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Actual dispatch/executor/execute mode authorized?: NO.
- Reserved data and all candidate/demo/live/trading paths remain locked.

### EXP-20260927-062 — DEC-324 executor source contract

- Concrete DEC-323 runtime freeze is the prerequisite.
- One-shot executor source contract authorized?: YES.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Reserved data and all candidate/demo/live/trading paths remain locked.
- Next gate: read-only current-main executor preflight.

### EXP-20260927-062 — DEC-325 read-only executor preflight

- Current-main executor preflight implemented.
- Empty-slot command evidence: `gh workflow run phase8a-exp062-discovery.yml --ref main`.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Existing run #2 immediately consumes the slot and removes the command.
- Reserved data and all candidate/demo/live/trading paths remain locked.
- Next gate: repository-hosted read-only executor-preflight proof.

### EXP-20260927-062 — DEC-326 repository-hosted executor-preflight proof

- Push-to-main read-only proof workflow added for DEC-325.
- Proof requires first workflow run / attempt 1 / 1 and exact DEC-323/324/325 source blobs.
- Proof runs only the executor preflight planner and uploads only `historical-executor-preflight.json`.
- Future discovery command is checked as data and is not executed.
- Historical executor availability, actual dispatch, and execute mode remain unauthorized.
- Reserved 2023-2026 data and all candidate/demo/live/trading paths remain locked.
- Next gate after actual success: concrete executor-preflight runtime evidence review/freeze.

### EXP-20260927-062 — DEC-327 executor-preflight proof reviewer

- Source-only reviewer prepared for future successful DEC-326 runtime evidence.
- Requires run #1 / attempt 1 success, one successful proof job, one non-expired artifact, and exact DEC-325 preflight content.
- Binds raw and canonical executor-preflight SHA-256 hashes.
- Historical executor/dispatch/execute mode authorized?: NO.
- Reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- Next gate after actual proof: immutable concrete executor-preflight freeze.

### EXP-20260927-062 — DEC-328 reviewed executor-preflight freeze source

- Deterministic freeze builder added for a valid future DEC-327 reviewed result.
- No runtime ids or hashes are fabricated before DEC-326 evidence exists.
- Freeze preserves actual proof run/job/artifact ids, artifact digest, preflight hashes, and reviewed source blobs.
- Historical executor/dispatch/execute mode authorized?: NO.
- Target historical runtime remains run #2 / attempt 1 only.
- Reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- Next gate after real proof: concrete runtime-evidence binding before an executor workflow.

### EXP-20260927-062 — DEC-329 concrete executor-preflight runtime freeze

- Bound real DEC-326 proof run `36422936991`, job `108929843306`, artifact `10970303347`.
- GitHub artifact digest and independently recomputed ZIP SHA-256 both equal `fe116a7fff7ffdec27e787d3cd7981ac67772276efb12a5b434b04ee3855c74c`.
- Frozen preflight raw SHA-256: `5dfa7800a8dcbe4537910690a0ba70b3c93467c685d7c5c99898d0b6d111f9d8`.
- Frozen preflight canonical SHA-256: `9970dcbf44241a3b9ffc6aab01d8a3bab6749813f88d0771dee101ea640aec3d`.
- Replays DEC-327 review and DEC-328 freeze; expected DEC-328 fingerprint `2e295d03066fcfa4dcea300c3f263bcf6a67cb96d6b356410821af493b2d5675`.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Executor availability / dispatch / execute mode authorized?: NO.
- Reserved data and all candidate/demo/live/trading paths remain locked.

### EXP-20260927-062 — DEC-330 executor activation source contract

- Concrete DEC-329 runtime freeze is the prerequisite.
- One-shot executor activation source authorized?: YES.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Reserved data and all candidate/demo/live/trading paths remain locked.
- Next gate: read-only current-main executor activation preflight.

### EXP-20260927-062 — DEC-331 read-only executor activation preflight

- Current-main activation preflight implemented and bound to DEC-330.
- Empty-slot command evidence: `gh workflow run phase8a-exp062-discovery.yml --ref main`.
- Executor activation source authorized?: YES.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Existing run #2 immediately consumes the slot and removes the command.
- Reserved data and all candidate/demo/live/trading paths remain locked.
- Next gate: repository-hosted read-only executor activation-preflight proof.

### EXP-20260927-062 — DEC-332 repository-hosted executor activation-preflight proof

- Push-to-main read-only proof workflow added for DEC-331.
- Proof requires first workflow run / attempt 1 / 1 and exact DEC-330/331 source blobs.
- Proof runs only the activation-preflight planner and uploads only `historical-executor-activation-preflight.json`.
- Future discovery command is checked as data and is not executed.
- Historical executor availability, actual dispatch, and execute mode remain unauthorized.
- Reserved 2023-2026 data and all candidate/demo/live/trading paths remain locked.
- Next gate after actual success: concrete activation-preflight runtime evidence review/freeze.

### EXP-20260927-062 — DEC-333 activation-preflight proof reviewer

- Source-only reviewer prepared for future successful DEC-332 runtime evidence.
- Requires run #1 / attempt 1 success, one successful proof job, one non-expired artifact, and exact DEC-331 preflight content.
- Binds raw and canonical activation-preflight SHA-256 hashes.
- Historical executor availability/dispatch/execute mode authorized?: NO.
- Reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- Next gate after actual proof: immutable concrete activation-preflight freeze.

### EXP-20260927-062 — DEC-334 terminal review criteria frozen

- Future historical result identity: workflow run #2 / attempt 1 only.
- Complete success shape: exact 20 jobs and 20 expected non-expired artifacts.
- Terminal non-success permanently consumes the historical-result slot.
- Rerun/retry/replacement authorized?: NO.
- Candidate compilation/promotion authorized?: NO.
- Reserved 2023-2026 data, Phase 8B, demo/live, real-money, and trading remain locked.
- Contract is frozen before the historical result exists.


### EXP-20260927-062 — DEC-335 reviewed activation-preflight freeze

- Deterministic source-only freeze builder added for a valid DEC-333 review.
- Preserves DEC-332 proof run/job/artifact identity, artifact digest, and raw/canonical preflight hashes.
- Preserves exact DEC-333 review source blobs and target run #2 / attempt 1.
- Emits one canonical `freeze_fingerprint_sha256`.
- Historical executor availability/dispatch/execute mode authorized?: NO.
- Reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- DEC-334 terminal-review contract remains a required sibling gate.
- Next gate: concrete DEC-332 activation-preflight runtime-evidence binding.


### EXP-20260927-062 — DEC-336 activation-preflight runtime evidence freeze

- Bound real DEC-332 proof run `36431469794`, job `108958446980`, and artifact `10973597441`.
- Artifact/ZIP SHA-256: `ee6e7ac2e8c18e1f8d276bba14ca942e20615143316ac185f4b814333804c2d5`.
- Raw activation-preflight SHA-256: `775010a0c3d4afe11191adb53d8ad54e7cf0d5de85b1a0b5adcb28c470e9a4a5`.
- Canonical activation-preflight SHA-256: `98b9180ae3b438b3c372ba34cbab9473d7f38ba5c1eb1add2dee988df4e09ad8`.
- Replays DEC-333 review and DEC-335 freeze; expected DEC-335 fingerprint `567320a598f245a8e7521281ddde3a1acaa0e3f294aebe12554688d2258f020b`.
- Pins DEC-334 terminal-review contract before executor progression.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Executor availability / dispatch / execute mode authorized?: NO.
- Reserved data and all candidate/demo/live/trading paths remain locked.


### EXP-20260927-062 — DEC-337 one-shot historical executor source

- Source-only executor contract added and pinned to DEC-336.
- Requires fresh DEC-331 empty-slot activation preflight.
- Target remains run #2 / attempt 1.
- One-shot historical executor source authorized?: YES.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Reserved data and all candidate/demo/live/trading paths remain locked.
- Next gate: repository-hosted source-contract proof.


### EXP-20260927-062 — DEC-338 one-shot executor source proof

- Push-to-main read-only proof workflow added for DEC-337.
- Replays real DEC-332 artifact evidence through DEC-333 / DEC-335 / DEC-336.
- Rebuilds fresh DEC-331 activation preflight from current main and run inventory.
- Requires zero historical-result attempts and target run #2 / attempt 1.
- Uploads only `one-shot-historical-executor-source-contract.json`.
- Historical executor availability / dispatch / execute mode authorized?: NO.
- Reserved data and all candidate/demo/live/trading paths remain locked.
- Next gate after actual success: immutable source-proof review/freeze.


### EXP-20260927-062 — DEC-339 source-proof reviewer

- Source-only reviewer prepared for future successful DEC-338 runtime evidence.
- Requires run #1 / attempt 1 success, one successful proof job, one non-expired artifact, and exact DEC-337 source-contract content.
- Binds raw and canonical source-contract SHA-256 hashes.
- Requires DEC-336 runtime-freeze fingerprint and DEC-334 terminal-review identity.
- Historical executor availability/dispatch/execute mode authorized?: NO.
- Reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- Next gate after actual proof: immutable source-proof freeze.


### EXP-20260927-062 — DEC-340 reviewed source-proof freeze

- Deterministic source-only freeze builder added for a valid DEC-339 review.
- Preserves DEC-338 proof run/job/artifact identity and artifact digest.
- Preserves raw/canonical DEC-337 source-contract hashes.
- Preserves DEC-336 runtime-freeze fingerprint, DEC-334 terminal-review decision, and target run #2 / attempt 1.
- Emits one canonical `freeze_fingerprint_sha256`.
- Historical executor availability/dispatch/execute mode authorized?: NO.
- Reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading remain locked.
- Next gate after actual proof: concrete source-proof runtime-evidence binding.


### EXP-20260927-062 — DEC-341 one-shot executor source-proof runtime evidence freeze

- Bound real DEC-338 proof run `36442399041`, job `108995955292`, and artifact `10979242048`.
- Artifact/ZIP SHA-256: `7dff775fc559cf9dbd754f45c24fbc814035b1602b59ca5eb9f82678af4e8b88`.
- Raw source-contract SHA-256: `484ad49fa3b3e925ae4a3576af840a8736c9b25ef439b619e8b60e8011f94d63`.
- Canonical source-contract SHA-256: `cb650b81c2549bfb5bfa62f6609bec9b39e4ed118f3e54c302a48a3a27a11616`.
- Replays DEC-339 review and DEC-340 freeze; expected DEC-340 fingerprint `e340394fb987c68d9203a57c9cd363f255729b3424a9600ec03533ff421960a8`.
- Pins DEC-334 terminal-review criteria.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Executor availability / dispatch / execute mode authorized?: NO.
- Reserved data and all candidate/demo/live/trading paths remain locked.


### EXP-20260927-062 — DEC-342 one-shot executor workflow contract

- Concrete DEC-341 runtime freeze is the prerequisite.
- One-shot executor workflow source authorized?: YES.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- DEC-334 terminal-review criteria remain pinned.
- Reserved data and all candidate/demo/live/trading paths remain locked.
- Next gate: read-only current-main one-shot executor workflow preflight.


### EXP-20260927-062 — DEC-343 read-only executor workflow preflight

- Current-main workflow preflight implemented and bound to DEC-342.
- Empty-slot command evidence: `gh workflow run phase8a-exp062-discovery.yml --ref main`.
- Workflow source authorized?: YES.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Existing run #2 immediately consumes the slot and removes the command.
- Reserved data and all candidate/demo/live/trading paths remain locked.
- Next gate: repository-hosted read-only workflow-preflight proof.


### EXP-20260927-062 — DEC-344 workflow-preflight proof

- Push-to-main read-only proof workflow added for DEC-343.
- Invokes only the plan surface.
- Requires zero historical-result attempts and target run #2 / attempt 1.
- Uploads only `one-shot-historical-executor-workflow-preflight.json`.
- Historical executor availability / dispatch / execute mode authorized?: NO.
- Reserved data and all candidate/demo/live/trading paths remain locked.
- Next gate after actual success: immutable workflow-preflight proof review/freeze.


### EXP-20260927-062 — DEC-345 workflow-preflight proof reviewer

- Future DEC-344 proof reviewer added.
- Requires run #1 / attempt 1 success, one successful job, one non-expired artifact.
- Revalidates exact DEC-343 slot-available preflight bytes.
- Records raw/canonical preflight SHA-256 hashes.
- Executor/dispatch/execute authority authorized?: NO.
- Next gate: immutable review freeze.


### EXP-20260927-062 — DEC-346 workflow-preflight proof freeze

- Deterministic freeze added for a valid DEC-345 review.
- Preserves proof run/job/artifact identity plus raw/canonical preflight hashes.
- Emits canonical freeze fingerprint.
- Executor availability / dispatch / execute mode authorized?: NO.
- Reserved data and all downstream trading paths remain locked.
- Next gate after real proof: concrete runtime-evidence binding.


### EXP-20260927-062 — DEC-347 workflow-preflight proof runtime evidence freeze

- Bound real DEC-344 proof run `36455684780`, job `109041310360`, and artifact `10984953455`.
- Artifact/ZIP SHA-256: `eec64c9bb1f6688dca010825e83e191c6a423d21bf6522396d7f650ec2db675f`.
- Raw preflight SHA-256: `56981ba62638129f39693239d22b76c65cb3a8e0b236741b3a80984137c2c0d7`.
- Canonical preflight SHA-256: `d6bf96a73b1377ad65887c6ba001c2c2d39812d58205e59e304c1c88e3ef22dc`.
- Replays DEC-345 review and DEC-346 freeze; expected DEC-346 fingerprint `3ba4b6aba0cafab3989c1f20536ad36603786efdcef49964a31bc99b73a79988`.
- Pins DEC-334 terminal-review criteria.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Executor availability / dispatch / execute mode authorized?: NO.
- Reserved data and all downstream trading paths remain locked.


### EXP-20260927-062 — DEC-348 one-shot executor workflow-install contract

- Concrete DEC-347 runtime freeze is the prerequisite.
- Future executor workflow path fixed.
- Workflow-install source authorized?: YES.
- Workflow installed?: NO.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: read-only current-main workflow-install preflight.


### EXP-20260927-062 — DEC-349 read-only workflow-install preflight

- Current-main install preflight implemented and bound to DEC-348.
- Future executor workflow path must remain absent.
- Install-source authorized?: YES.
- Install authorized?: NO.
- Workflow installed?: NO.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: repository-hosted read-only install-preflight proof.


### EXP-20260927-062 — DEC-350 workflow-install preflight proof

- Push-to-main read-only proof workflow added for DEC-349.
- Requires future executor workflow path absent.
- Requires zero historical-result attempts and target run #2 / attempt 1.
- Uploads only `one-shot-historical-executor-workflow-install-preflight.json`.
- Install / executor / dispatch / execute authority authorized?: NO.
- Reserved data and all downstream trading paths remain locked.
- Next gate after actual success: immutable proof review/freeze.


### EXP-20260927-062 — DEC-351 workflow-install preflight proof reviewer

- Future DEC-350 proof reviewer added.
- Requires run #1 / attempt 1 success, one successful job, one non-expired artifact.
- Revalidates exact DEC-349 source-absent preflight bytes.
- Records raw/canonical preflight SHA-256 hashes.
- Install / executor / dispatch / execute authority authorized?: NO.
- Next gate: immutable review freeze.


### EXP-20260927-062 — DEC-352 workflow-install preflight proof freeze

- Deterministic freeze added for a valid DEC-351 review.
- Preserves proof run/job/artifact identity plus raw/canonical preflight hashes.
- Preserves absent future executor workflow path.
- Emits canonical freeze fingerprint.
- Install / executor / dispatch / execute authority authorized?: NO.
- Reserved data and all downstream trading paths remain locked.
- Next gate after real proof: concrete runtime-evidence binding.


### EXP-20260927-062 — DEC-353 workflow-install preflight proof runtime evidence freeze

- Bound real DEC-350 proof run `36461898040`, job `109062250103`, and artifact `10987972547`.
- Artifact/ZIP SHA-256: `60a723a55502ee9b8145258c5482ce71b82b2331c572378536b14d78f6ef2f91`.
- Raw install-preflight SHA-256: `ee754581b87576c3c23228a2371b88b3b8a38fdcd9c20ebd2c222c18f7c65e0d`.
- Canonical install-preflight SHA-256: `5c1893ea24a627ea421f05564d6d0cc490215201c01162fbe0b6ab519a323c8b`.
- Replays DEC-351 review and DEC-352 freeze; expected DEC-352 fingerprint `75fad6795f4046d83f5ae29f08475c969e29d3fe3af0e3448dde46292a959f4a`.
- Future executor workflow path remains absent.
- Install / executor / dispatch / execute authority authorized?: NO.
- Reserved data and all downstream trading paths remain locked.


### EXP-20260927-062 — DEC-354 dormant executor workflow-installation source contract

- Concrete DEC-353 runtime freeze is the prerequisite.
- Dormant executor template path fixed outside `.github/workflows/`.
- Reserved active executor workflow path fixed.
- Installation source authorized?: YES.
- Dormant template present?: NO.
- Active workflow installed?: NO.
- Executor / dispatch / execute authority authorized?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: dormant executor workflow template source.


### EXP-20260927-062 — DEC-355 dormant one-shot executor workflow source

- Disabled executor template source added outside `.github/workflows/`.
- Dormant template blob: `51ce87584369be957482460d81649adb1cb9f05d`.
- Encodes executor run #1 / attempt 1 and historical result run #2 / attempt 1.
- Encodes exactly one historical discovery shell dispatch.
- Encodes immutable executor receipt and no retry/replacement authority.
- Active executor workflow installed?: NO.
- Historical dispatch authorized under this decision?: NO.
- Next gate: read-only dormant-source proof.


### EXP-20260927-062 — DEC-356 dormant executor source proof

- Push-to-main read-only proof workflow added for DEC-355.
- Pins DEC-354/355, dormant template, and active discovery workflow blobs.
- Requires active executor workflow path absent.
- Requires zero historical-result attempts and target run #2 / attempt 1.
- Uploads only `dormant-one-shot-historical-executor-workflow-source.json`.
- Install / executor / dispatch / execute authority authorized?: NO.
- Next gate after actual success: immutable proof review/freeze.


### EXP-20260927-062 — DEC-357 dormant executor source-proof reviewer

- Future DEC-356 proof reviewer added.
- Requires run #1 / attempt 1 success, one successful job, one non-expired artifact.
- Revalidates exact DEC-355 dormant-source JSON.
- Records raw/canonical source SHA-256 hashes.
- Install / executor / dispatch / execute authority authorized?: NO.
- Next gate: immutable review freeze.


### EXP-20260927-062 — DEC-358 dormant executor source-proof freeze

- Deterministic freeze added for a valid DEC-357 review.
- Preserves proof run/job/artifact identity plus raw/canonical source hashes.
- Preserves dormant template identity and target run #2 / attempt 1.
- Emits canonical freeze fingerprint.
- Install / executor / dispatch / execute authority authorized?: NO.
- Next gate after real proof: concrete runtime-evidence binding.


### EXP-20260927-062 — DEC-359 dormant executor source proof runtime evidence freeze

- Bound real DEC-356 proof run `36473192632`, job `109100293950`, and artifact `10991479562`.
- Artifact/ZIP SHA-256: `092e1daebf889560d27ebe57242772c3806322627dab03e64a2ff400d9b4b1d1`.
- Raw dormant-source SHA-256: `1dfae5078e400fc2dbf0b10ef6d4297dc4d3c0660386ebb8c46b63c6dbe69060`.
- Canonical dormant-source SHA-256: `4d6cf8999ecb5346a10ecb31cdc1b669736d4d466e6b31c503b3fbf1a5e633a7`.
- Replays DEC-357 review and DEC-358 freeze; expected DEC-358 fingerprint `8ba4411b8c7468a1f0eecc0352490e00577452ce96a81710fca6457e779e9897`.
- Pins DEC-334 terminal-review criteria.
- Dormant template remains source only; active workflow remains uninstalled.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Install / executor / dispatch / execute authority authorized?: NO.
- Reserved data and all downstream trading paths remain locked.


### EXP-20260927-062 — DEC-360 active executor workflow install contract

- Concrete DEC-359 runtime freeze is the prerequisite.
- Exact dormant executor template remains the only source template.
- Active install-source review authorized?: YES.
- Active workflow path present?: NO.
- Workflow install authorized?: NO.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: read-only current-main active workflow-install preflight.


### EXP-20260927-062 — DEC-361 read-only active workflow install preflight

- Current-main active install preflight implemented and bound to DEC-360.
- Dormant executor template must remain exact.
- Active executor workflow path must remain absent.
- Active install-source review authorized?: YES.
- Workflow install authorized?: NO.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: repository-hosted read-only active install-preflight proof.


### EXP-20260927-062 — DEC-362 active workflow install preflight proof

- Push-to-main read-only proof workflow added for DEC-361.
- Pins DEC-360/361, dormant template, active discovery workflow, and planning runtime.
- Requires active executor workflow path absent.
- Requires zero historical-result attempts and target run #2 / attempt 1.
- Uploads only `active-one-shot-historical-executor-workflow-install-preflight.json`.
- Install / executor / dispatch / execute authority authorized?: NO.
- Reserved data and all downstream trading paths remain locked.
- Next gate after actual success: immutable proof review/freeze.


### EXP-20260927-062 — DEC-363 active install-preflight proof reviewer

- Future DEC-362 proof reviewer added.
- Requires run #1 / attempt 1 success, one successful job, one non-expired artifact.
- Revalidates exact DEC-361 active-path-absent preflight bytes.
- Records raw/canonical preflight SHA-256 hashes.
- Install / executor / dispatch / execute authority authorized?: NO.
- Next gate: immutable review freeze.


### EXP-20260927-062 — DEC-364 active install-preflight proof freeze

- Deterministic freeze added for a valid DEC-363 review.
- Preserves proof run/job/artifact identity plus raw/canonical preflight hashes.
- Preserves dormant-template identity and active executor workflow absent state.
- Emits canonical freeze fingerprint.
- Install / executor / dispatch / execute authority authorized?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: concrete runtime-evidence binding.


### EXP-20260927-062 — DEC-365 active install-preflight proof runtime evidence freeze

- Bound real DEC-362 proof run `36478916362`, job `109119455390`, and artifact `10996155764`.
- Artifact/ZIP SHA-256: `5554cabdf72e87c6c860746f1d76d0816a3dd3ebdf2b443b911b5027e81f070a`.
- Raw active-install-preflight SHA-256: `c70cbdb3f593de110a21d6501d867ed23f6be70b7815993ef1b62fea1d2477fc`.
- Canonical active-install-preflight SHA-256: `010f1bcdd595de78ebe55ad3729e641345f3c486e3a46e38a60a7072555ad30b`.
- Replays DEC-363 review and DEC-364 freeze; expected DEC-364 fingerprint `2e8c36e891b20dc1811301a4b461d51c9fa46e34b098cbe5af1e3a27bc129932`.
- Pins DEC-334 terminal-review criteria.
- Active executor workflow path remains absent.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Install / executor / dispatch / execute authority authorized?: NO.
- Reserved data and all downstream trading paths remain locked.


### EXP-20260927-062 — DEC-366 active workflow-installation contract

- Concrete DEC-365 runtime freeze is the prerequisite.
- Dormant executor template identity is pinned.
- Active workflow-installation source authorized?: YES.
- Workflow install authorized?: NO.
- Workflow installed?: NO.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: read-only current-main active workflow-installation preflight.


### EXP-20260927-062 — DEC-367 active workflow-installation preflight

- Current-main installation preflight implemented and bound to DEC-366.
- Dormant executor template must match the exact frozen blob.
- Active executor workflow path must remain absent.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Workflow-install authorization / installed state / executor / dispatch / execute?: NO.
- Next gate: repository-hosted read-only installation-preflight proof.


### EXP-20260927-062 — DEC-368 workflow-installation preflight proof

- Push-to-main read-only proof workflow added for DEC-367.
- Requires exact dormant-template identity and active executor workflow path absent.
- Requires zero historical-result attempts and target run #2 / attempt 1.
- Uploads only `active-one-shot-historical-executor-workflow-installation-preflight.json`.
- Install / executor / dispatch / execute authority authorized?: NO.
- Reserved data and all downstream trading paths remain locked.
- Next gate after actual success: immutable proof review/freeze.


### EXP-20260927-062 — DEC-369 active installation-preflight proof reviewer

- Future DEC-368 proof reviewer added.
- Requires run #1 / attempt 1 success, one successful job, one non-expired artifact.
- Revalidates exact DEC-367 source-ready active-workflow-absent preflight bytes.
- Records raw/canonical preflight SHA-256 hashes.
- Install / executor / dispatch / execute authority authorized?: NO.
- Next gate: immutable review freeze.


### EXP-20260927-062 — DEC-370 active installation-preflight proof freeze

- Deterministic freeze added for a valid DEC-369 review.
- Preserves proof run/job/artifact identity plus raw/canonical preflight hashes.
- Preserves active executor workflow path absent state.
- Emits canonical freeze fingerprint.
- Install / executor / dispatch / execute authority authorized?: NO.
- Reserved data and all downstream trading paths remain locked.
- Next gate after real proof: concrete runtime-evidence binding.


### EXP-20260927-062 — DEC-371 active workflow-installation proof runtime evidence freeze

- Bound real DEC-368 proof run `36484309283`, job `109137344254`, and artifact `10997847720`.
- Artifact/ZIP SHA-256: `d122e474752f1ec8127eb610b55321dbf94cc7dcb339eca43eafb7e429ef4a07`.
- Raw installation-preflight SHA-256: `5bf7760c7ad36e642eeeaf9e29b5fb0e5108a4059207ff2d7d75bd4c9f6bcf3b`.
- Canonical installation-preflight SHA-256: `30de670f8483139b23fbd51bd05444677278fd7d1ba1f1eb8f0cc33409cf3a74`.
- Replays DEC-369 review and DEC-370 freeze; expected DEC-370 fingerprint `51e47a3d6d2876b52e2090714e6f89b4c2ce0ae2d869d79e5b2cd4586c774af6`.
- Pins DEC-334 terminal-review criteria.
- Active executor workflow path remains absent.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Install / executor / dispatch / execute authority authorized?: NO.
- Reserved data and all downstream trading paths remain locked.


### EXP-20260927-062 — DEC-372 active install-authorization contract

- Concrete DEC-371 runtime freeze is the prerequisite.
- DEC-371 runtime-freeze fingerprint: `a498bf1cae3c6e92803fc750331c3090c35bb3af13bf01a62866831d29bb95f8`.
- Install-authorization source authorized?: YES.
- Actual workflow install authorized?: NO.
- Workflow installed?: NO.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: read-only current-main install-authorization preflight.


### EXP-20260927-062 — DEC-373 read-only install-authorization preflight

- Current-main install-authorization preflight implemented and bound to DEC-372.
- Active executor workflow path must remain absent.
- Install-authorization source authorized?: YES.
- Actual workflow install authorized?: NO.
- Workflow installed?: NO.
- Historical executor available?: NO.
- Historical-result dispatch authorized?: NO.
- Execute mode available?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: repository-hosted read-only install-authorization preflight proof.


### EXP-20260927-062 — DEC-374 install-authorization preflight proof

- Push-to-main read-only proof workflow added for DEC-373.
- Requires active executor workflow path absent.
- Requires zero historical-result attempts and target run #2 / attempt 1.
- Uploads only `active-one-shot-historical-executor-workflow-install-authorization-preflight.json`.
- Actual install / executor / dispatch / execute authority authorized?: NO.
- Reserved data and all downstream trading paths remain locked.
- Next gate after actual success: immutable proof review/freeze.


### EXP-20260927-062 — DEC-375 install-authorization proof reviewer

- DEC-374 proof reviewer added.
- Requires run #1 / attempt 1 success, one successful job, one non-expired artifact.
- Revalidates exact DEC-373 install-authorization preflight bytes.
- Records raw/canonical preflight SHA-256 hashes.
- Install / executor / dispatch / execute authority authorized?: NO.
- Next gate: immutable review freeze.


### EXP-20260927-062 — DEC-376 install-authorization proof freeze

- Deterministic freeze added for a valid DEC-375 review.
- Preserves proof run/job/artifact identity plus raw/canonical preflight hashes.
- Preserves active workflow-absent state and target run #2 / attempt 1.
- Emits canonical freeze fingerprint.
- Install / executor / dispatch / execute authority authorized?: NO.
- Next gate: concrete runtime-evidence binding.


### EXP-20260927-062 — DEC-377 install-authorization proof runtime evidence freeze

- Bound real DEC-374 proof run `36542684978`, job `109321600936`, and artifact `11020419084`.
- Artifact/ZIP SHA-256: `f7829f71c481143517b918c7d54b1cb43136edcd50ea9076e3795935bd994384`.
- Raw install-authorization-preflight SHA-256: `e5de1145a6f39ca42413fb5ce1eed297d8bdcf572923e296d2b6d773e945e45f`.
- Canonical install-authorization-preflight SHA-256: `994b96d76cf50cfae019d21b4b478d6e0b6ffc0c99fda9efa7c7aa4bf50263dc`.
- Replays DEC-375 review and DEC-376 freeze; expected DEC-376 fingerprint `fb4c445610884db868a516f9a2086c8d0a6f22d397cb7e8d39806548101c1595`.
- Pins DEC-334 terminal-review criteria.
- Active executor workflow path remains absent.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Install / executor / dispatch / execute authority authorized?: NO.


### EXP-20260927-062 — DEC-378 active workflow install-decision contract

- Pinned DEC-377 runtime-freeze source and fingerprint.
- Pinned the dormant executor workflow template.
- Install-decision source authorized?: YES.
- Actual install / installed / executor / dispatch / execute authority?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: read-only current-main install-decision preflight.


### EXP-20260927-062 — DEC-379 install-decision preflight

- Pinned DEC-378 install-decision contract source.
- Requires exact current main and active executor workflow path absent.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- CLI surface: plan only.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: repository-hosted read-only preflight proof.


### EXP-20260927-062 — DEC-380 install-decision preflight proof

- Added push-to-main first-run/attempt-1 read-only proof for DEC-379.
- Pinned DEC-378/379, dormant template, active discovery workflow, and runtime source identities.
- Invokes only the install-decision preflight plan surface.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Uploads only the install-decision-preflight JSON.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate after success: immutable proof review/freeze.


### EXP-20260927-062 — DEC-381 install-decision proof reviewer

- Added source-only review of future DEC-380 runtime evidence.
- Pinned DEC-380/379/378 source identities, dormant executor template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates install-decision preflight content and records raw/canonical hashes.
- Install / executor / dispatch / execute authority authorized?: NO.
- Next gate after real evidence: immutable review freeze.


### EXP-20260927-062 — DEC-382 install-decision proof freeze

- Added deterministic source-only freeze for valid DEC-381 review evidence.
- Preserves proof identities, artifact digest, preflight hashes, source map, and active-workflow-absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Install / executor / dispatch / execute authority authorized?: NO.
- Next gate after real DEC-380 evidence: concrete runtime-evidence binding.


### EXP-20260927-062 — DEC-383 concrete install-decision proof runtime binding

- Bound DEC-380 merged-main head `fa96bc731ed8d21cec883451f7ec5e984b74df40`.
- Bound proof run/job/artifact: `36553935570` / `109358450875` / `11025737149`.
- Verified artifact ZIP digest `f863ea57b45e2c0e12892732747094f8f4f63793cf212be018d7d6cbade6555b`.
- Bound DEC-379 raw/canonical hashes and DEC-382 freeze fingerprint `be15d3ffe0a66befeec91694e5c412e0d7678818835774361258edf06b06b6f8`.
- Active executor workflow path remains absent; install/executor/dispatch/execute authority remains NO.
- Next gate: source-only install-execution authorization contract.


### EXP-20260927-062 — DEC-384 install-execution authorization contract

- Pinned DEC-383 runtime-freeze source and fingerprint.
- Pinned the dormant executor workflow template.
- Install-execution authorization source authorized?: YES.
- Actual install / installed / executor / dispatch / execute authority?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: read-only current-main install-execution authorization preflight.


### EXP-20260927-062 — DEC-385 install-execution authorization preflight

- Pinned DEC-384 install-execution authorization contract source.
- Requires exact current main and active executor workflow path absent.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Preserves all three source-only authorization gates.
- CLI surface: plan only.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: repository-hosted read-only execution-authorization preflight proof.


### EXP-20260927-062 — DEC-386 install-execution authorization preflight proof

- Added push-to-main first-run/attempt-1 read-only proof for DEC-385.
- Pinned DEC-384/385, dormant template, active discovery workflow, and runtime source identities.
- Invokes only the execution-authorization preflight plan surface.
- Confirms all three source-only gates, zero historical-result attempts, and target run #2 / attempt 1.
- Uploads only the execution-authorization-preflight JSON.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate after success: immutable proof review/freeze.


### EXP-20260927-062 — DEC-387 execution-authorization proof reviewer

- Added source-only review of future DEC-386 runtime evidence.
- Pinned DEC-386/385/384 source identities, dormant executor template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates execution-authorization preflight content and records raw/canonical hashes.
- Preserves all three source-only gates while actual install / executor / dispatch / execute authority remains NO.
- Next gate after real evidence: immutable review freeze.


### EXP-20260927-062 — DEC-388 install-execution authorization proof freeze

- Added deterministic source-only freeze for valid DEC-387 review evidence.
- Preserves DEC-386 proof identities, artifact digest, DEC-385 preflight hashes, source map, and active-workflow-absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Actual install / executor / dispatch / execute authority authorized?: NO.
- Next gate after real DEC-386 evidence: concrete runtime-evidence binding.


### EXP-20260927-062 — DEC-389 concrete install-execution authorization proof runtime binding

- Bound DEC-386 merged-main head `cdbef40d1c9908650155933ae5073909ad9be24d`.
- Bound proof run/job/artifact: `36558750341` / `109374198795` / `11029316948`.
- Verified artifact ZIP digest `5908aff795243b98d8dc0f2b15b603df77ec1b1313c03d76b63452c181bf8d02`.
- Bound exact DEC-385 raw/canonical hashes and DEC-388 freeze fingerprint `594b2db3aa50b5c09d7f53a4635cea40b4e566fddd0d16a6574e1322ef8a48af`.
- Active executor workflow remains absent; install/executor/dispatch/execute authority remains NO.
- Next gate: source-only workflow install-execution contract.


### EXP-20260927-062 — DEC-390 install-execution contract

- Pinned DEC-389 runtime-freeze source and fingerprint.
- Correctly binds real DEC-386 merged head `cdbef40d1c9908650155933ae5073909ad9be24d`.
- Preserves install-authorization, install-decision, and install-execution-authorization source-only gates.
- Install-execution contract source authorized?: YES.
- Actual install / executor / dispatch / execute authority?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: read-only current-main workflow install-execution preflight.


### EXP-20260927-062 — DEC-391 install-execution preflight

- Pinned DEC-390 install-execution contract source.
- Requires exact current main and active executor workflow path absent.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Preserves all four source-only gates.
- CLI surface: plan only.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: repository-hosted read-only install-execution preflight proof.


### EXP-20260927-062 — DEC-392 workflow install-execution preflight proof

- Added push-to-main first-run/attempt-1 read-only proof for DEC-391.
- Pinned DEC-390/391, dormant template, active discovery workflow, and runtime source identities.
- Invokes only the install-execution preflight plan surface.
- Confirms all four source-only gates, zero historical-result attempts, and target run #2 / attempt 1.
- Uploads only the install-execution-preflight JSON.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate after success: immutable proof review/freeze.


### EXP-20260927-062 — DEC-393 install-execution proof reviewer

- Added source-only review of future DEC-392 runtime evidence.
- Pinned DEC-392/391/390 source identities, dormant executor template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates DEC-391 preflight content and records raw/canonical hashes.
- Preserves all four source-only gates.
- Actual install / executor / dispatch / execute authority authorized?: NO.
- Next gate after real evidence: immutable review freeze.


### EXP-20260927-062 — DEC-394 install-execution proof freeze

- Added deterministic source-only freeze for valid DEC-393 review evidence.
- Preserves DEC-392 proof identities, artifact digest, DEC-391 preflight hashes, source map, and active-workflow-absent state.
- Preserves all four source-only gates.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Actual install / executor / dispatch / execute authority authorized?: NO.
- Next gate after real DEC-392 evidence: concrete runtime-evidence binding.


### EXP-20260927-062 — DEC-395 install-execution proof runtime freeze

- Bound real DEC-392 merged-main proof head/run/job/artifact identities.
- Bound GitHub artifact digest plus raw/canonical DEC-391 preflight hashes.
- Replays DEC-393 review and DEC-394 deterministic freeze.
- Requires DEC-394 fingerprint `9357b1c6591a801237acacf7cb7eab1f5302608770ad7b3033566bda39cb3548`.
- Preserves all four source-only gates.
- Actual install / executor / dispatch / execute authority authorized?: NO.
- Next gate: source-only workflow install-activation contract.


### EXP-20260927-062 — DEC-396 workflow install-activation contract

- Pinned corrected DEC-395 runtime-freeze blob and fingerprint.
- Preserves all four predecessor source-only gates.
- Adds only the workflow install-activation source gate.
- Keeps the active workflow path absent and the historical-result slot unused.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: read-only current-main workflow install-activation preflight.


### EXP-20260927-062 — DEC-397 workflow install-activation preflight

- Pinned DEC-396 install-activation contract source.
- Requires exact current main and active executor workflow path absent.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Preserves all five source-only gates.
- CLI surface: plan only.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: repository-hosted read-only install-activation preflight proof.


### EXP-20260927-062 — DEC-398 workflow install-activation preflight proof

- Added push-to-main first-run/attempt-1 read-only proof for DEC-397.
- Pinned DEC-396/397 source identities, dormant template, active discovery workflow, and runtime requirements.
- Invokes only the install-activation preflight plan surface.
- Confirms all five source-only gates, zero historical-result attempts, and target run #2 / attempt 1.
- Uploads only the activation-preflight JSON.
- Actual install / executor / dispatch / execute authority?: NO.


### EXP-20260927-062 — DEC-399 install-activation proof reviewer

- Added source-only review of future DEC-398 runtime evidence.
- Pinned DEC-398/397/396 source identities, dormant executor template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates DEC-397 preflight content and records raw/canonical hashes.
- Preserves all five source-only gates.
- Actual install / executor / dispatch / execute authority authorized?: NO.
- Next gate after real evidence: immutable review freeze.


### EXP-20260927-062 — DEC-400 install-activation proof freeze

- Added deterministic source-only freeze for valid DEC-399 review evidence.
- Preserves DEC-398 proof identities, artifact digest, DEC-397 preflight hashes, source map, and active-workflow-absent state.
- Preserves all five source-only gates.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Actual install / executor / dispatch / execute authority authorized?: NO.
- Next gate after real DEC-398 evidence: concrete runtime-evidence binding.


### EXP-20260927-062 — DEC-401 install-activation proof runtime binding

- Bound real DEC-398 merged-main run #1 / attempt 1.
- Run/job/artifact: 36579901387 / 109445012411 / 11039017180.
- Artifact ZIP/GitHub digest: c19012d3e4fc794e40a930e0eac82d799773f6a9050bf56adc75a0b0f2245b85.
- Raw/canonical DEC-397 preflight hashes: 8db03c11f255bcc724c4d7c18df7e5a8f539039032dbb5787291ca8810427116 / 229fec80d76273f5320966acb63d0661ff7aa03c04ded8d953bb3e9e3f363ceb.
- Required DEC-400 freeze fingerprint: 441c508902f816faee66c58768552a7d3ab05f0b145193a3e6349f18c9062808.
- All five source-only gates remain true; actual install/executor/dispatch/execute authority remains false.
- Next gate: source-only workflow-install contract.


### EXP-20260927-062 — DEC-402 workflow-install source contract

- Pinned DEC-401 runtime-freeze source and fingerprint.
- Preserved the historical DEC-360 install-contract blob unchanged.
- Preserves all five predecessor source-only gates.
- Final workflow-install source gate authorized?: YES.
- Actual install / executor / dispatch / execute authority?: NO.
- Historical-result attempts remain zero; target remains run #2 / attempt 1.
- Next gate: read-only current-main workflow-install source preflight.


### EXP-20260927-062 — DEC-403 workflow-install source preflight

- Pinned DEC-402 workflow-install source contract.
- Requires exact current main and active executor workflow path absent.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Preserves all six source-only gates.
- CLI surface: plan only.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: repository-hosted read-only source-preflight proof.


### EXP-20260927-062 — DEC-404 workflow-install source-preflight proof

- Added push-to-main first-run/attempt-1 read-only proof for DEC-403.
- Pinned DEC-402/403, dormant template, active discovery workflow, and runtime source identities.
- Invokes only the source-preflight plan surface.
- Confirms all six source-only gates, zero historical-result attempts, and target run #2 / attempt 1.
- Uploads only the source-preflight JSON.
- Actual install / executor / dispatch / execute authority?: NO.


### EXP-20260927-062 — DEC-407 workflow-install source-preflight proof recovery

- Preserved DEC-404 run #1 / attempt 1 as failed evidence.
- Confirmed DEC-403 preflight execution succeeded before the wrapper-only verifier failure.
- Failure cause: assertion of absent `install_source_slot_verified_available` field.
- Recovery is restricted to workflow run #2 / attempt 1.
- Failed run/job/head are pinned as provenance.
- Recovery workflow remains push-to-main, read-only, plan-only, and artifact-only.
- Actual install / executor / dispatch / execute / trading authority?: NO.


### EXP-20260927-062 — DEC-408 recovery proof reviewer

- Added source-only review of successful DEC-407 run #2 / attempt 1 evidence.
- Pins corrected recovery workflow blob `2adfc7bd1ccacd158a78532d31ff38f4f175229f`.
- Parses the actual DEC-403 JSON shape; no synthetic slot field is assumed.
- Carries failed DEC-404 run `36613664506`, job `109561121322`, and head provenance.
- Records raw/canonical preflight hashes.
- Actual install / executor / dispatch / execute / trading authority?: NO.


### EXP-20260927-062 — DEC-409 recovery proof freeze

- Added deterministic freeze for valid DEC-408 recovery reviews.
- Preserves failed run #1 and successful recovery run #2 provenance together.
- Preserves exact run/job/artifact identities, artifact digest, preflight hashes, and source map.
- Emits one canonical freeze fingerprint.
- Actual install / executor / dispatch / execute / trading authority?: NO.


### EXP-20260927-062 — DEC-410 concrete recovery runtime binding

- Preserved failed DEC-404 proof run #1 / attempt 1 as immutable provenance.
- Bound successful DEC-407 recovery run #2 / attempt 1.
- Bound run/job/artifact identities plus ZIP/raw/canonical SHA-256 values.
- Re-runs DEC-408 review and DEC-409 deterministic freeze.
- Requires DEC-409 fingerprint `c0c04735c57638fde0a57122c240ea6c9aacd86fc7e43cdc532aaf8ba54cd9d3`.
- All six source-only gates remain true.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: source-only final workflow-install authorization contract before install.


### EXP-20260927-062 — DEC-411 final workflow-install authorization contract

- Pinned DEC-410 runtime-freeze blob and fingerprint.
- Preserves failed DEC-404 and successful DEC-407 recovery lineage transitively.
- Preserves six predecessor source-only gates.
- Adds only the final authorization-contract source gate.
- Actual workflow install authorized?: NO.
- Executor / dispatch / execute / trading authority?: NO.
- Next gate: read-only current-main final authorization preflight.


### EXP-20260927-062 — DEC-412 final authorization preflight

- Pinned DEC-411 final authorization contract source.
- Requires exact current main and active executor workflow path absent.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Preserves all seven source-only gates.
- CLI surface: plan only.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: repository-hosted read-only final-authorization preflight proof.


### EXP-20260927-062 — DEC-413 final authorization preflight proof

- Added push-to-main first-run/attempt-1 read-only proof for DEC-412.
- Pinned DEC-411/412 source identities, dormant template, discovery workflow, and planning runtime.
- Invokes only the final-authorization preflight plan surface.
- Confirms seven source-only gates, zero historical-result attempts, and target run #2 / attempt 1.
- Uploads only the final-authorization-preflight JSON.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate after success: immutable proof review/freeze.


### EXP-20260927-062 — DEC-414 final authorization proof reviewer

- Added source-only review of future DEC-413 runtime evidence.
- Pinned DEC-413/412/411 source identities and planning dependencies.
- Requires exact successful proof run/job/artifact shape.
- Revalidates DEC-412 preflight content and records raw/canonical hashes.
- Preserves all seven source-only gates.
- Actual install / executor / dispatch / execute authority authorized?: NO.


### EXP-20260927-062 — DEC-415 final authorization proof freeze

- Added deterministic source-only freeze for valid DEC-414 review evidence.
- Preserves DEC-413 proof identities, artifact digest, DEC-412 hashes, and source map.
- Preserves all seven source-only gates.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Actual install / executor / dispatch / execute authority authorized?: NO.


### EXP-20260927-062 — DEC-416 final authorization proof runtime binding

- Bound successful DEC-413 run `36622849087` / job `109592333745` / artifact `11058592607`.
- Verified artifact ZIP SHA-256 `8303140ebc7a5e37922080051ab634bc7a6c9f13940d52f3802b1017fd658c7a`.
- Verified DEC-412 raw/canonical preflight hashes.
- Reproduced DEC-415 freeze fingerprint `4a71a6b29ccea4d5415ce64ca84fc0c43988a2daf98cbe912f4654868b907ffa`.
- All seven source-only gates remain true.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: source-only workflow-install action contract before install.


### EXP-20260927-062 — DEC-417 workflow-install action contract

- Pinned DEC-416 runtime-freeze blob and fingerprint.
- Preserves all seven predecessor source-only gates.
- Adds only the install-action-contract source gate.
- Active executor workflow path remains absent.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: read-only current-main workflow-install action preflight.


### EXP-20260927-062 — DEC-418 workflow-install action preflight

- Pinned DEC-417 action-contract source.
- Requires exact current main and active executor workflow path absent.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Preserves all eight source-only gates.
- CLI surface: plan only.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: repository-hosted read-only action-preflight proof.


### EXP-20260927-062 — DEC-419 workflow-install action preflight proof

- Added push-to-main first-run/attempt-1 read-only proof for DEC-418.
- Pinned DEC-417/418 source identities, dormant template, active discovery workflow, and planning runtime.
- Invokes only the action-preflight plan surface.
- Preserves all eight source-only gates and confirms zero historical-result attempts / target run #2 attempt 1.
- Uploads only the action-preflight JSON.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate after real proof evidence: immutable proof review/freeze.

### EXP-20260927-062 — DEC-420 workflow-install action proof reviewer

- Added source-only review of successful DEC-419 merged-main runtime evidence.
- Pins DEC-419/418/417 source identities, dormant template, and discovery workflow.
- Requires exact successful run #1 / attempt 1, one successful job, and one non-expired artifact.
- Revalidates DEC-418 preflight content and records raw/canonical hashes.
- Preserves all eight source-only gates.
- Actual install / executor / dispatch / execute authority authorized?: NO.


### EXP-20260927-062 — DEC-421 workflow-install action proof freeze

- Added deterministic source-only freeze for valid DEC-420 review evidence.
- Preserves DEC-419 proof identities, artifact digest, DEC-418 hashes, and source map.
- Preserves all eight source-only gates and active-workflow-absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Actual install / executor / dispatch / execute authority authorized?: NO.

### EXP-20260927-062 — DEC-422 workflow-install action proof runtime binding

- Bound successful DEC-419 run `36634716243` / job `109632428957` / artifact `11063264562`.
- Verified artifact ZIP SHA-256 `1f06c7b589f46ca7a473bae5a0666b79b1b627dc6a8eaf85804211424e09f0be`.
- Verified DEC-418 raw/canonical preflight hashes.
- Reproduces DEC-421 freeze fingerprint `78bcceaf580672b97858ec972c590300316f8b7b369137ca96e957c39d1d9a5d`.
- All eight source-only gates remain true.
- Actual install / executor / dispatch / execute authority?: NO.
- Next gate: separate explicit repository-mutation authorization.

### EXP-20260927-062 — DEC-423 active workflow mutation authorization

- Bound explicit operator authorization to the concrete DEC-422 runtime freeze.
- Pins DEC-422 blob/fingerprint and the dormant executor template blob.
- Sets only workflow-install authorization true.
- Active workflow remains absent.
- Installed state / executor availability / dispatch / execute authority?: NO.
- Trading authority?: NO.
- Next gate: repository mutation installing the active workflow.

### EXP-20260927-062 — DEC-424 active workflow installation

- Installed the active one-shot historical executor workflow.
- Active workflow bytes exactly match dormant template blob `51ce87584369be957482460d81649adb1cb9f05d`.
- Pins DEC-423 mutation-authorization source.
- Workflow-install authorization / installed state / executor availability: YES.
- Historical dispatch / execute authority: NO.
- Trading authority: NO.
- Next gate: explicit one-shot executor dispatch authorization.

### EXP-20260927-062 — DEC-425 installed executor dispatch preflight

- Pins DEC-424 receipt and exact active executor workflow blob.
- Rechecks current main, zero executor runs, and zero historical-result attempts.
- Requires target run #2 / attempt 1 and unused historical slot.
- CLI surface: plan only.
- Historical dispatch / execute authority: NO.
- Trading authority: NO.

### EXP-20260927-062 — DEC-426 installed executor dispatch-preflight proof

- Added push-to-main read-only proof of DEC-425.
- Pins DEC-424/425 source identities and active executor workflow blob.
- Requires zero executor runs and zero historical-result attempts.
- Requires unused historical slot and target run #2 / attempt 1.
- Dispatch / execute / trading authority: NO.

### EXP-20260927-062 — DEC-427 dispatch-preflight proof review

- Reviewed successful merged-main DEC-426 proof.
- Bound run `36688457000` / job `109799712311` / artifact `11085100742`.
- Verified artifact ZIP and raw/canonical DEC-425 hashes.
- Installed executor state remains true; executor run count remains zero.
- Dispatch / execute / trading authority: NO.


### EXP-20260927-062 — DEC-428 dispatch-preflight proof freeze

- Added deterministic freeze for valid DEC-427 review evidence.
- Preserves exact proof identities, source map, installed state, and unused slot.
- Emits a canonical freeze fingerprint for later runtime binding.
- Dispatch / execute / trading authority: NO.

### EXP-20260927-062 — DEC-429 dispatch-preflight proof runtime binding

- Bound real DEC-426 run `36688457000` / job `109799712311` / artifact `11085100742`.
- Verified ZIP/raw/canonical hashes and DEC-428 freeze fingerprint.
- Re-runs DEC-427 review and DEC-428 deterministic freeze.
- Executor installed/available: YES.
- Executor run count: 0.
- Dispatch / execute / trading authority: NO.

### EXP-20260927-062 — DEC-430 one-shot executor dispatch authorization

- Bound explicit one-shot dispatch authorization to DEC-429.
- Pins exact DEC-429 runtime-freeze fingerprint and active workflow blob.
- Authorized executor run #1 / attempt 1 only.
- Authorized historical result run #2 / attempt 1 only.
- Workflow triggered?: NO.
- Rerun / retry / replacement?: NO.
- Trading authority?: NO.

### EXP-20260927-062 — DEC-431 one-shot dispatch action preflight

- Pins DEC-430 authorization and active executor workflow.
- Requires zero executor runs and zero historical-result attempts.
- Requires executor run #1 / attempt 1 and historical run #2 / attempt 1.
- Exposes the future executor command as evidence only.
- Workflow triggered?: NO.
- Trading authority?: NO.

### EXP-20260927-062 — DEC-432 one-shot dispatch action-preflight proof

- Added push-to-main read-only proof of DEC-431.
- Requires zero executor runs and zero historical-result attempts.
- Verifies executor run #1 / attempt 1 and historical run #2 / attempt 1.
- Confirms one-shot dispatch authorization is true.
- Executor triggered?: NO.
- Trading authority?: NO.

### EXP-20260927-062 — DEC-433 action-preflight proof review

- Added strict reviewer for future successful DEC-432 evidence.
- Requires exact authorization, zero executor runs, and zero historical attempts.
- Trading authority?: NO.


### EXP-20260927-062 — DEC-434 action-preflight proof freeze

- Added deterministic freeze for valid DEC-433 evidence.
- Preserves authorized-but-unstarted one-shot state.
- Emits canonical freeze fingerprint.
- Executor triggered?: NO.


### EXP-20260927-062 — DEC-435 action-preflight proof runtime evidence binding

- Bound successful DEC-432 run `36695220474`, job `109821445046`, artifact
  `11087821283` to exact raw/canonical proof hashes.
- Re-runs DEC-433 review and DEC-434 freeze; freeze fingerprint is
  `9a59f7329cb5abe0786511b91d7b6d8e33d4df8f027271a7387830f8fbf11c8a`.
- Executor runs at binding: 0.
- Historical-result attempts at binding: 0.
- Authorized executor target remains run #1 / attempt 1.
- Historical result target remains run #2 / attempt 1.
- General execute mode / rerun / retry / replacement: NO.
- Trading authority: NO.


### EXP-20260927-062 — DEC-436 one-shot executor recovery

- Original executor run `36702494195` failed before historical dispatch.
- GitHub assigned original executor run #2 / attempt 1; the run #1 guard rejected it.
- Failed job: `109844958600`.
- Historical-result attempts after failure: 0.
- Historical result target remains discovery run #2 / attempt 1.
- Recovery uses a separate manual-only workflow with expected run #1 / attempt 1.
- Original executor workflow is unchanged.
- Generic rerun / retry / replacement: NO.
- Reserved-data and trading authority: NO.


### EXP-20260927-062 — DEC-437/438 recovery receipt review/freeze

- Adds strict source-only review of a future DEC-436 recovery receipt.
- Requires recovery run #1 / attempt 1 success.
- Preserves failed original executor run `36702494195`.
- Requires historical target run #2 / attempt 1 on the same head.
- Adds deterministic freeze fingerprint.
- Adds no dispatch or trading authority.

### EXP-20261002-067 — DEC-470 Annual Pattern Catalogue V1 protocol

- Governing method: DEC-469 annual-first discovery.
- Collection scope: 2015-2025 full calendar years plus 2026 through 2026-08-20.
- Former 2023-2026 reserve: authorized for this catalogue/Strategy V1 research path; not untouched OOS for Strategy V1 after use.
- Pattern grammar: 65 snapshot singles + 2,010 cross-dimension snapshot pairs + 410 same-dimension exact-lag transitions.
- Nominal annual search: 89,460 directional hypotheses per segment; 1,073,520 annual records across 12 segments.
- Annual winner selection: NONE; all nominal records are preserved.
- Cross-year gate/ranking/dedup/caps: frozen before results.
- Historical artifact read / execution / result production: NO.
- Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_MINER`.

### EXP-20261002-067 — DEC-471 annual catalogue in-memory miner

- Protocol: exact DEC-470 Catalogue V1.
- Unit of work: one annual segment × symbol × timeframe × horizon.
- Output: exactly 4,970 LONG/SHORT records per unit; no winner filtering.
- State encoding: strict prior-only same-year expanding tertiles; 300 finite prior rows required.
- Transitions: exact T-60m / T-240m only.
- Annual boundary: signal and fixed-horizon exit must remain inside the same segment.
- Historical artifact access / execution / result production: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_EVIDENCE_CONTRACT`.

### EXP-20261002-067 — DEC-472 Annual Catalogue V1 evidence contract

- Cell evidence: complete 4,970-record annual cell payload + canonical SHA/size + source/code identities.
- Semantic validation: reconstructs every frozen pattern/direction identity and validates support/economic statistics.
- Aggregate universe: 12 annual segments × 18 cells = 216 annual cells.
- Nominal aggregate records: 1,073,520.
- Aggregate input: validated-cell summaries only for full replay.
- Historical artifact read / execution / result production: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_FULL_HISTORY_LOADER`.

### EXP-20261002-067 — DEC-473 source-only annual catalogue full-history loader

- Reuses only accepted EXP-044 feature/outcome artifacts; no new data acquisition or materialization.
- Exact partition universe: 140 months, 2015-01 through 2026-08.
- Exact segment universe: 2015-2025 plus `2026_YTD_TO_2026_08_20`.
- Unit of loading: one annual segment × symbol × timeframe.
- Verifies selected artifact path/size/SHA/schema/row count plus aggregate evidence and manifest bindings.
- Filters any outcome whose fixed-horizon exit crosses the annual segment boundary.
- Historical artifact read / catalogue execution / result production: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_SEGMENT_ADAPTER`.

### EXP-20261002-067 — DEC-474 source-only annual segment adapter

- Input: verified DEC-473 annual segment bundle only; arbitrary raw frames are not a public input.
- Output: exact DEC-471 `FeatureObservation` / `OutcomeObservation` inputs with source/evidence identities retained.
- Observation identity: accepted EXP-044/EXP-061 canonical projection.
- Range: all DEC-469 segments, including 2023-2025 and `2026_YTD_TO_2026_08_20`.
- Annual isolation: feature/outcome availability and fixed-horizon exits cannot escape the requested segment.
- Non-finite continuous features: normalized to null under the accepted DEC-293 behavior.
- Historical artifact read / catalogue execution / result production: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_RUNTIME_WIRING`.

### EXP-20261002-067 — DEC-475 source-only locked annual catalogue runtime wiring

- Exact call graph: authorization gate -> DEC-473 loader -> DEC-474 adapter -> DEC-471 miner -> DEC-472 cell evidence compiler.
- Unit of work: one annual segment × symbol × timeframe × horizon.
- Gate occurs before every filesystem-backed historical read.
- Historical artifact read / catalogue execution / result production: NO.
- Workflow installed / workflow dispatch: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_PLAN`.

### EXP-20261002-067 — DEC-476 annual catalogue workflow plan

- Future run unit: one annual segment only.
- Exact per-segment shape: 18 cells + preflight + annual freeze = 20 jobs / 20 planned artifacts.
- Full collection: 12 separately frozen annual segments × 18 cells = 216 cells.
- Required order: 2015 through 2025, then `2026_YTD_TO_2026_08_20`.
- Next segment authority requires prior segment freeze.
- Single 216-cell workflow execution: FORBIDDEN.
- Cross-year comparison inside annual run: NO.
- Workflow installed / dispatch / historical execution / result production: NO.
- Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_SEGMENT_FREEZE_CONTRACT`.

### EXP-20261002-067 — DEC-477 annual segment freeze contract

- Input: exactly 18 validated DEC-472 cell summaries from one annual segment.
- Annual frozen inventory: 18 cells × 4,970 directional records = 89,460 records.
- Missing / duplicate / cross-year / mixed-code cells: fail closed.
- Input ordering: canonicalized before annual fingerprinting.
- Annual totals: recomputed from bound cell summaries.
- Next-segment execution authorization: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_SOURCE`.

### EXP-20261002-067 — DEC-478 dormant annual catalogue workflow source

- Source state: disabled template only; active workflow path absent.
- Input: exactly one of the 12 frozen annual segment labels.
- Run shape: preflight + 18 annual cells + annual freeze = 20 jobs / 20 artifacts.
- Historical sources: exact accepted EXP-044 feature/outcome runs and artifacts only.
- Cell product: DEC-472 cell evidence + complete catalogue payload.
- Annual product: one DEC-477 same-segment freeze.
- Sequential dependency: 2016+ requires the immediately prior successful annual run and validated DEC-477 freeze; 2015 requires none.
- Full-collection aggregate / cross-year comparison inside workflow: NONE.
- Workflow install / dispatch / historical reads / execution / results: NO.
- Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_CONTRACT`.

### EXP-20261002-067 — DEC-479 annual workflow installation contract

- Binds exact DEC-478 workflow-source, CLI, and disabled-template Git blobs.
- Reserved active workflow path must remain absent.
- Only future allowed mutation: create active workflow from exact dormant-template bytes.
- Dormant template / CLI / workflow-source edits during install: FORBIDDEN.
- Repository mutation authorization: NO.
- Workflow install / dispatch / historical execution / results: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: `SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT`.
### EXP-20261002-067 — DEC-480 read-only annual workflow installation preflight

- Verifies exact DEC-479 install-contract blob and transitive DEC-478 source bindings.
- Requires exact `main` branch metadata and caller-supplied expected head SHA.
- Requires reserved active workflow path to remain absent.
- Fingerprints both the preflight and embedded install-action payload.
- Rehashed authority escalation: fails semantic validation.
- Rehashed top-level `install_sources` substitution: fails semantic validation.
- CLI surface: `plan` only; no install/execute/dispatch/advance command.
- Repository mutation / workflow install / dispatch / historical execution: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: repository-hosted read-only preflight proof.

### EXP-20261002-067 — DEC-481 repository-hosted install-preflight proof contract

- Input: fully validated DEC-480 preflight.
- Binds exact DEC-480 preflight-source Git blob.
- Requires proof main SHA = preflight expected main SHA.
- Future proof run identity: frozen workflow, manual dispatch, main, attempt 1, completed success, exact positive run ID.
- Binds preflight fingerprint + install-action fingerprint.
- Frozen proof retains exact run event / branch / head / attempt / completed status / successful conclusion.
- Rehashed run-provenance tampering: fails semantic validation.
- Rehashed authority escalation: fails semantic validation.
- Repository mutation / annual workflow install/dispatch / historical execution: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: source-only proof-workflow source.

### EXP-20261002-067 — DEC-482 dormant install-preflight proof workflow source

- Disabled proof template only; reserved proof workflow path remains absent.
- Dormant template is pinned to exact Git blob `0d6c93e2af04501f9ac2589fd24d6672b2b41910`; byte drift fails closed.
- Exact run surface: manual main check -> read-only main metadata -> DEC-480 plan -> preflight artifact upload.
- DEC-481 proof compilation inside same run: NO; completed run metadata is required later.
- Annual cell/freeze execution surface: NONE.
- `gh workflow run` / repository mutation surface: NONE.
- Proof workflow install/dispatch / annual workflow install/dispatch / historical execution: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: source-only proof-workflow install contract.

### EXP-20261002-067 — DEC-483 proof-workflow installation contract

- Binds exact DEC-482 proof-workflow source and dormant-template blobs.
- Revalidates DEC-482 transitive DEC-481 proof-contract / DEC-480 CLI dependencies.
- Reserved active proof-workflow path must remain absent.
- Only future allowed mutation: create the active proof workflow from exact dormant-template bytes.
- Exact top-level key set plus nested source/mutation semantic validation.
- Repository mutation / proof-workflow install / dispatch: NO.
- Annual workflow install / dispatch / historical execution: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: source-only proof-workflow install preflight.
### EXP-20261002-067 — DEC-484 proof-workflow install preflight

- Binds exact DEC-483 install-contract source and validated source report.
- Requires exact current-main metadata and reserved proof-workflow target absence.
- Embeds and fingerprints the exact DEC-483 install action.
- Exact top-level key set and semantic nested action/source validation.
- Rehashed authority / target / source-report / extra-field tampering: rejected.
- CLI surface: `plan` only; no install/execute/dispatch/advance command.
- Repository mutation / proof-workflow install / dispatch: NO.
- Annual workflow install / dispatch / historical execution: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Finite bootstrap: no proof workflow may be required to prove its own installation.
- Explicit operator authorization required before the exact proof-workflow file creation.
- Unopened provisional DEC-485/486 recursive branches: superseded / non-authoritative.
- Next gate: explicit operator proof-workflow install authorization.

### EXP-20261003-068 — DEC-485 proof-workflow installation receipt

- Installed the active annual-catalogue install-preflight proof workflow.
- Active workflow bytes exactly match frozen dormant template blob `0d6c93e2af04501f9ac2589fd24d6672b2b41910`.
- Pins DEC-484 authorization-preflight source blob `ab434212007f3777fa4436a51268438ea44be6dd`.
- Single-file installation authorization: consumed.
- Future repository mutation: NO.
- Proof workflow installed / available: YES.
- Proof workflow dispatch: NO.
- Annual workflow install / dispatch / historical execution: NO.
- Cross-year result / Strategy V1 synthesis / promotion / trading authority: NO.
- Next gate: explicit proof-workflow dispatch authorization before any run.
### EXP-20261003-069 — DEC-486 proof-workflow dispatch preflight

- Pins DEC-485 receipt blob `638c988524ccf8ada27067c2b0bdb3403823a6f5`.
- Pins active proof-workflow blob `0d6c93e2af04501f9ac2589fd24d6672b2b41910`.
- Requires exact current main and zero proof-workflow runs.
- CLI surface: plan only.
- Proof-workflow dispatch: NO.
- Annual workflow install / dispatch / historical execution: NO.
- Strategy V1 / promotion / trading authority: NO.
- Next gate: explicit proof-workflow dispatch authorization before run.
### EXP-20261003-070 — DEC-487 first proof-workflow dispatch authorization

- Pins DEC-486 preflight blob `9f5d4b2abbfdb02280b0011a5d61e189be1d6fed`.
- Pins active proof-workflow blob `0d6c93e2af04501f9ac2589fd24d6672b2b41910`.
- Explicit first dispatch authorization: YES.
- Expected proof run: #1 / attempt 1.
- Rerun / retry / replacement: NO.
- Workflow triggered by this decision: NO.
- Annual workflow install / dispatch / historical execution: NO.
- Strategy V1 / promotion / trading authority: NO.
### EXP-20261003-071 — DEC-488 future proof-workflow run reviewer

- Pins DEC-487 dispatch authorization, DEC-481 proof contract, and the active proof workflow.
- Requires proof run #1 / attempt 1 on exact current main.
- Requires successful run + successful proof job.
- Requires one unexpired artifact named for the exact main head.
- Semantically validates the downloaded DEC-480 preflight through DEC-481.
- Records raw and canonical preflight SHA-256 identities.
- Reviewer dispatch authority: NO.
- Annual workflow install / dispatch / historical execution: NO.
- Strategy V1 / promotion / trading authority: NO.
### EXP-20261003-072 — DEC-489 deterministic proof-run freeze

- Pins DEC-488 reviewer blob `ec92323d910785d342028c5896528fa1dcf1cc96`.
- Accepts only a semantically valid DEC-488 review on the exact expected main head.
- Preserves run/job/artifact and preflight/proof fingerprints.
- Emits one canonical freeze SHA-256.
- Concrete runtime evidence claimed before real run?: NO.
- Further proof dispatch: NO.
- Annual workflow install / dispatch / historical execution: NO.
- Strategy V1 / promotion / trading authority: NO.
### EXP-20261003-073 — DEC-490 proof-workflow runtime evidence binding

- Proof run: `37120635769`, run #1 / attempt 1, success.
- Main head: `6ee059cb451e7c6d2235b7744542dc194acc014e`.
- Proof job: `111195887975`, success.
- Artifact: `11273008137`, unexpired.
- Artifact ZIP SHA-256: `3b242f14e89950eb828c614bf1b021dd51d9fc43b9045c2efccc6a1f7bcd8e32`.
- Raw preflight SHA-256: `70f6aaaca16fbb5de9e481e135cd8ec85d6dc7c6df524fcf328e23fd0d8de3d3`.
- Canonical preflight SHA-256: `f151fcbd487b40be35b54356f7b3002ba416812ec4ece2ea4bd7868cf5c0a163`.
- DEC-481 proof fingerprint: `4ad886232c6af5566c8ac5581c153274b8328c7cd41d508ba93dcf343fdf8578`.
- DEC-489 freeze fingerprint: `99397d1593f724bcc6024c5d0a2f4abf2b230273bf7ffb0edcc0b88562cd58fb`.
- Further proof dispatch: NO.
- Annual workflow install / dispatch / historical execution: NO.
- Strategy V1 / promotion / trading authority: NO.
### EXP-20261003-074 — DEC-491 annual workflow install receipt

- Explicit annual-workflow installation authorization: CONSUMED.
- Active workflow path: `.github/workflows/phase8a-annual-pattern-catalogue.yml`.
- Active workflow blob: `31633e87b79551f5b7dfa6b0deb76a82eb070129`.
- Dormant template blob: `31633e87b79551f5b7dfa6b0deb76a82eb070129`.
- Exact byte identity: YES.
- Trigger mode: manual workflow_dispatch only.
- Permissions: contents read / actions read.
- Separate execution gates retained: 3.
- Annual workflow dispatch / 2015 execution: NO.
- Strategy V1 / promotion / trading authority: NO.
### EXP-20261003-075 — DEC-492 2015 execution preflight

- Installed annual workflow: YES.
- Active workflow blob: `31633e87b79551f5b7dfa6b0deb76a82eb070129`.
- Annual workflow run count required: 0.
- Expected first run: #1 / attempt 1.
- Annual segment: 2015.
- Prior segment / prior freeze required: NO.
- DEC-475 historical read / execution / result authority: NO.
- CLI surface: plan only.
- Workflow dispatch / Strategy V1 / promotion / trading authority: NO.
### EXP-20261003-076 — DEC-493 first 2015 execution authorization

- Explicit operator authorization: YES.
- Annual segment: `2015` only.
- Expected annual workflow run: #1 / attempt 1.
- Historical artifact reads for that run: YES.
- Annual catalogue execution for that run: YES.
- Annual result production for that run: YES.
- Rerun / retry / replacement: NO.
- 2016+ / next-segment execution: NO.
- Strategy V1 / promotion / trading authority: NO.
### EXP-20261003-077 — DEC-494 first 2015 dispatch preflight

- Exact current main required: YES.
- Annual workflow run count required: 0.
- Annual segment: 2015.
- Previous annual freeze run id: empty.
- Expected run: #1 / attempt 1.
- DEC-493 2015 execution authority required: YES.
- CLI surface: plan only.
- Rerun / retry / replacement: NO.
- 2016+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-078 — First 2015 run failure

- Run: `37126711695`, #1 / attempt 1.
- Head: `fd85a886d07234ad584dcca08692b37e6af54b2e`.
- Preflight job: `111213380390`.
- Source validation: PASS.
- Scoped 2015 execution authorization: PASS.
- 2015 no-predecessor validation: PASS.
- Artifact upload: FAIL.
- Root cause: hidden `.preflight` directory filtered by upload-artifact default.
- Annual cell execution: NONE.
- Annual freeze: NONE.
- First-run authorization: CONSUMED.

### EXP-20261003-079 — Hidden-artifact upload repair

- Upload action count: 3.
- `include-hidden-files: true`: 3.
- Preflight upload repaired: YES.
- Cell-product upload repaired: YES.
- Annual-freeze upload repaired: YES.
- Rerun / retry / replacement authorization: NO.
- 2016+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-080 — DEC-497 2015 replacement-run preflight

- Prior annual run count required: 1.
- Required prior run: `37126711695`.
- Required prior run identity: #1 / attempt 1 / completed failure.
- Repaired workflow blob: `f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.
- Expected replacement identity: #2 / attempt 1.
- Replacement execution authorization: NO.
- 2016+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-081 — DEC-498 2015 replacement execution authorization

- Authorization basis: standing operator autonomous-build authorization.
- Annual segment: 2015 only.
- Replacement run identity: #2 / attempt 1.
- Failed first run id: `37126711695`.
- Historical artifact reads for replacement: YES.
- Catalogue execution for replacement: YES.
- Result production for replacement: YES.
- Failed-run rerun / retry: NO.
- Run #3+ / 2016+ / Strategy V1 / promotion / trading: NO.

### EXP-20261003-082 — DEC-499 final 2015 replacement dispatch preflight

- Exact current main required: YES.
- Required prior annual run count: 1.
- Required failed run: `37126711695`, #1 / attempt 1.
- Repaired workflow blob: `f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.
- Live replacement runtime blob: `ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b`.
- Expected replacement run: #2 / attempt 1.
- DEC-498 replacement execution authority: YES.
- CLI dispatch surface: NO.
- Run #3+ / 2016+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-083 — DEC-500 2015 replacement-run reviewer

- Expected runtime identity: #2 / attempt 1.
- Expected successful jobs: 20.
- Expected unexpired artifacts: 20.
- Annual cell jobs/artifacts: 18.
- Freeze payload validator: DEC-477.
- Expected directional records: 89,460.
- Freeze ZIP digest must match GitHub artifact digest.
- Review fingerprint: canonical SHA-256.
- 2016+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-084 — DEC-501 deterministic 2015 replacement-run freeze

- Input: semantically valid DEC-500 review.
- Preserved runtime identity: run #2 / attempt 1.
- Preserved jobs/artifacts: preflight + 18 cells + freeze.
- Preserved DEC-477 annual-freeze fingerprint and totals.
- Output fingerprint: canonical SHA-256.
- Head mismatch: fail closed.
- Refingerprinted authority tamper: fail closed.
- 2016+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-085 — DEC-502 concrete 2015 runtime binding

- Input: semantically valid DEC-501 freeze.
- Required run identity: #2 / attempt 1 / completed success.
- Required jobs: preflight + 18 cells + freeze.
- Required artifacts: preflight + 18 cells + freeze.
- Freeze ZIP digest must match freeze artifact digest.
- Preserves DEC-500 review fingerprint and DEC-501 freeze fingerprint.
- Annual cells: 18.
- Directional records: 89,460.
- Binding fingerprint: canonical SHA-256.
- 2016+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-086 — DEC-503 2016 execution preflight

- Requires concrete DEC-502 2015 runtime binding.
- Prior annual workflow run count: exactly 2.
- Required history: failed run #1 + successful replacement run #2.
- Target segment: 2016.
- Required predecessor: 2015.
- Previous freeze run id: successful 2015 replacement run id.
- Expected next workflow identity: #3 / attempt 1.
- CLI surface: plan only.
- 2016 execution authorization: NO.
- Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-087 — DEC-504 2016 authorization contract

- Input: valid DEC-503 preflight.
- Authorization basis: standing autonomous-build instruction.
- Annual segment: 2016.
- Required predecessor: 2015.
- Expected run identity: #3 / attempt 1.
- Dispatch / historical read / execution / result scope: YES in receipt.
- Runtime authorization installed: NO.
- Runtime gate active: NO.
- 2017+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-088 — DEC-505 dormant 2016 runtime authorization plan

- Live runtime mutation: NO.
- Dormant 2016 gate template: frozen.
- Dormant 2016-wired runtime target: frozen.
- Segment: 2016 only.
- Expected run: #3 / attempt 1.
- Previous annual-freeze run id required: YES.
- 2017+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-089 — DEC-506 2016 runtime install preflight

- Input authorization: canonical DEC-504 receipt.
- Exact current main required: YES.
- Segment / run identity: 2016 / #3 / attempt 1.
- Previous annual-freeze run id required: YES.
- Activation mutation file count: 2.
- Live runtime mutation: NO.
- Runtime gate active: NO.
- 2017+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-090 — DEC-507 exact 2016 runtime install action

- Input: valid concrete DEC-506 preflight.
- Exact current main recheck: REQUIRED.
- Action count: 2.
- Action 1: create active 2016 gate source.
- Action 2: replace runtime with frozen 2016-wired target.
- Extra mutation: rejected.
- Live runtime mutation by compiler: NO.
- 2017+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-091 — DEC-508 future 2016 runtime install receipt

- Required changed file count: 2.
- Installed 2016 gate blob: exact DEC-505 target.
- Installed runtime blob: exact DEC-505 target.
- Install action consumed: YES.
- Runtime gate installed/active: YES.
- Annual workflow dispatch: NO.
- 2017+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-092 — DEC-509 read-only 2016 dispatch preflight

- DEC-508 install receipt: REQUIRED and validated.
- Concrete DEC-502 predecessor binding: REQUIRED and matched.
- Prior annual workflow run count: exactly 2.
- Current main equals install commit: REQUIRED.
- Expected 2016 run: number 3, attempt 1.
- Runtime authorization installed/active: YES.
- Dispatch command present: NO.
- Annual workflow dispatch authority: NO.
- 2017+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-093 — DEC-510 source-only 2016 dispatch authorization

- Source DEC-509 preflight: REQUIRED and validated.
- Authorized annual segment: 2016 only.
- Authorized run: number 3, attempt 1 only.
- Runtime authorization installed/active: YES.
- Annual workflow dispatch authority: YES, contract-only.
- Historical read/execution/result authority: YES, exact run only.
- Dispatch command present/executed: NO.
- Rerun / retry / run 4+: NO.
- 2017+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-094 — DEC-511 final read-only 2016 dispatch preflight

- Source DEC-510 authorization: REQUIRED and validated.
- Current main = authorization head = install commit: REQUIRED.
- Prior annual workflow runs: exactly 2.
- Successful 2015 predecessor run ID + head SHA: exact.
- Frozen dispatch ref: main.
- Frozen annual segment: 2016.
- Frozen predecessor input: exact successful 2015 run ID.
- Dispatch authority: YES, inherited exact-run contract.
- Dispatch command present/executed: NO.
- Rerun / retry / run 4+ / 2017+ / Strategy V1 / promotion / trading: NO.

### EXP-20261003-095 — DEC-512 one-shot replacement executor

- Live annual workflow inventory before execution: exactly run 1 only.
- Required prior run: \`37126711695\`, #1, attempt 1, failed.
- Authorized replacement: 2015, run #2, attempt 1 only.
- Executor trigger: first merged-main push touching only its workflow path.
- DEC-499 is rebuilt against exact merged main immediately before dispatch.
- Target dispatch count added by executor: exactly 1.
- Retry / rerun / run 3+: NO.
- 2016+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-096 — DEC-513 automated replacement evidence binding

- Trigger: completed annual workflow run #2 only.
- Required attempt / conclusion: attempt 1 / success.
- Required executor: exact successful DEC-512 run at same head.
- DEC-500 review: REQUIRED.
- DEC-501 deterministic freeze: REQUIRED.
- DEC-502 concrete runtime binding: REQUIRED.
- Artifact ZIP SHA-256 verified against GitHub digest: YES.
- Actions write / dispatch / retry / rerun: NO.
- 2016+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-097 — DEC-514 read-only 2016 activation plan

- Trigger: successful DEC-513 reviewer only.
- DEC-513 runtime-binding artifact: unique, unexpired, digest-verified.
- Current main equals reviewed evidence head: REQUIRED.
- DEC-503 preflight: COMPILED.
- DEC-504 run-3 authorization: COMPILED.
- DEC-506 install preflight: COMPILED.
- DEC-507 two-file install action: COMPILED.
- Repository mutation performed: NO.
- Workflow dispatch performed: NO.
- 2017+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-100 — DEC-517 replacement executor recovery

- Original executor run: `37149151549`.
- Original executor conclusion: FAILURE before dispatch.
- Failure cause: missing pinned Python runtime / `polars` import.
- Annual workflow dispatch inventory after failure: exactly run #1 only.
- Target replacement slot consumed: NO.
- Recovery installs pinned runtime before DEC-499 import: YES.
- Recovery target: 2015 run #2 / attempt 1 only.
- Retry / rerun / run 3+: NO.
- 2016+ / promotion / broker / trading authority: NO.

### EXP-20261003-101 — DEC-518 recovered exact 2016 runtime install

- Trigger: successful recovered DEC-514 activation plan only.
- DEC-514 workflow blob: `6069421af6ffc72a40bca9250627c9f81135fd16`.
- DEC-514 artifact: unique, unexpired, digest-verified.
- Concrete DEC-502 runtime binding carried forward: YES.
- Mutation count: exactly 2 files.
- Result gate blob: `87c00381c5c12a0593378f565e6be4bad003514f`.
- Result runtime blob: `d7d3713cb3259e793c448153fd75ca043f511389`.
- Push mode: normal fast-forward only.
- Concrete DEC-508 receipt: REQUIRED.
- Workflow dispatch / rerun / retry / broker / trading: NO.

### EXP-20261003-102 — DEC-519 folded post-install 2016 dispatch plan

- Execution location: second job of DEC-518 workflow.
- Job dependency: successful exact install.
- Job permissions: contents read / actions read.
- Concrete DEC-508 receipt: REQUIRED.
- Concrete DEC-502 binding: REQUIRED.
- Installed gate/runtime blobs: EXACT.
- DEC-509 → DEC-510 → DEC-511: REBUILT IN ORDER.
- Expected next annual run: #3 / attempt 1.
- Dispatch / mutation / rerun / retry / trading: NO.

### EXP-20261003-103 — DEC-520 workflow validity and run-number recovery

- Malformed live workflow before repair: duplicate YAML keys on preflight upload.
- Last invalid annual workflow global run number observed: 375.
- Additional annual `workflow_dispatch` runs observed: 0.
- Corrected live workflow blob: `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`.
- Hidden-file flags after repair: exactly one per preflight/cell/freeze upload.
- Recovered 2015 replacement identity: run 376 / attempt 1.
- Future 2016 identity: run 377 / attempt 1.
- New dispatch/retry/trading authority created by repair: NO.

### EXP-20261003-099 — DEC-521 exact 2016 run-377 dispatch

- Trigger: successful DEC-518 install + successful DEC-519 plan in the same workflow.
- Installed main equals concrete DEC-508 install commit: REQUIRED.
- Latest annual workflow global run before dispatch: 376, successful.
- Manual dispatch inventory before dispatch: failed run 1 + successful run 376 only.
- Authorized target: annual segment 2016, run 377, attempt 1.
- Previous annual freeze input: exact concrete DEC-502 run ID.
- Dispatch count: exactly 1.
- Result claimed at dispatch time: NO.
- Rerun / retry / run 378+: NO.
- 2017+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261003-100 — DEC-522 2016 run-377 evidence binding

- Target: exact successful annual run 377 / attempt 1.
- DEC-521 receipt/run ID/head binding: REQUIRED.
- Successful job count: exactly 20.
- Artifact count: exactly 20, unexpired, SHA-256 addressed.
- 2016 freeze ZIP digest verified against GitHub: REQUIRED.
- DEC-477 freeze validation: REQUIRED.
- Concrete 2016 runtime evidence binding output: YES.
- Repository mutation / workflow dispatch / rerun / retry: NO.
- 2017+ / Strategy V1 / promotion / trading authority: NO.

### EXP-20261117-001 — Hypothetical 30-day return-versus-ruin reconstruction

- Date: 2026-11-17
- Status: INCONCLUSIVE
- Hypothesis: A repeatable after-cost edge under FMP's constraints can support a 100% net return within 30 calendar days on a small disposable account.
- Code commit: uncommitted DEC-627 source on top of `53e203133bbc141b2f48c7b8b8241d56b35166a3`
- Data manifest/version: none. No market-data files were opened.
- Pair(s): EURUSD, GBPUSD, USDJPY named only as the study's hypothetical universe
- Timeframe(s): not used. The calculator is in trades per window, not bars.
- Data range: not applicable
- Train period: not applicable
- Validation period: not applicable
- Final-test touched?: NO
- Strategy/model: independent binary R-multiple lattice, plus the study's illustrative regime, within-group correlation, Pareto stop gap, and lognormal cost noise. Fixed fractional sizing only.
- Features: none
- Parameters/search space: the study's printed S1–S11 assumptions. Risk fraction was not searched.
- Random seed (if relevant): 11 for the stress reconstruction. Exact lattice uses no seed.
- Spread/cost model: study assumption of 0.08R round trip, described there as 1.2 pips on a 15-pip stop. This is not a broker-page cost table.
- Slippage model: inside the 0.08R assumption, plus the stress model's lognormal cost noise and 0.5% Pareto gaps. Not a measured fill record.
- Risk assumptions: caller-supplied fixed fraction. Study rows use 0.25% through 30%. FMP policy default remains 0.25%, hard maximum 0.50%.
- Trade count: hypothetical window counts from the study, including 60 and 120. The Phase 7 comparison uses the documented 199 stage-2 trades and 122 stage-1 trades only as published aggregates.
- Net return after costs: not a market result. Exact S6 terminal expectation is the compound of a +0.005R hypothesis, not an observed return.
- Expectancy/trade: study hypothesis. The Phase 7 stage-2 aggregate implies about +0.00527R at 0.5 pip of adverse slippage and about -0.0113R at 1.0 pip, using $250 per 1R at the $100,000 window start. Those are aggregate conversions, not a trade-level R series.
- Profit factor: not recomputed from fills
- Max drawdown: Monte Carlo quantiles are available from the calculator. They were not estimated from Phase 7 fills in this experiment.
- Result: the exact printed scenario table reproduces within rounding. The stress table is an independent reconstruction because `fmpsim.py` was absent. The documented Phase 7 forward aggregate fails the edge-first check, so its doubling probabilities are illustrations rather than a candidate outcome. The 100%-in-30-days hypothesis is not supported by current documented evidence. No trading authority.

### EXP-20261117-002 — Retail cost quotations and Phase 7 aggregate re-read

- Date: 2026-11-17
- Status: INCONCLUSIVE
- Hypothesis: A source-backed retail cost changes the after-cost expectancy of the documented Phase 7 candidate enough to identify its 30-day doubling and loss probabilities.
- Code commit: `research/dec627-dec629-measurement`, parent `53e203133bbc141b2f48c7b8b8241d56b35166a3`
- Data manifest/version: none. No market-data files were opened. Broker pages were read on 2026-11-17.
- Pair(s): EURUSD, GBPUSD, USDJPY
- Timeframe(s): not used
- Data range: not applicable
- Train period: not applicable
- Validation period: not applicable
- Final-test touched?: NO
- Strategy/model: no new strategy. The existing return-versus-ruin lattice receives a labeled round-trip cost. Phase 7 is re-read from its published aggregates only.
- Features: none
- Parameters/search space: published OANDA US, IC Markets EU, and Pepperstone quotations. Risk fraction was not searched. No hourly spread grid.
- Random seed (if relevant): not applicable. The lattice is exact.
- Spread/cost model: see `src/fmp/research/retail_costs.py`. Minimum spreads are not used as typical spreads. Bid/ask fills are not charged a second spread.
- Slippage model: no retrieved page publishes a typical slippage. Scenarios that include slippage label it as an assumption. Phase 7's 0.2, 0.5, and 1.0 pip columns are the existing research assumptions and are already inside those aggregates.
- Risk assumptions: fixed fractional sizing only. A zero gross edge stays non-positive at 0.25%, 4%, and 15%.
- Trade count: no new market trades. Phase 7 stage 2 remains the documented 199 trades.
- Net return after costs: not a new market result. Stage 2 aggregate expectancy remains +$3.8054, +$1.3175, and -$2.8247 at 0.2, 0.5, and 1.0 pip per side.
- Expectancy/trade: about +0.01522R, +0.00527R, and -0.01130R on the $250 window-start risk unit. These are aggregate conversions.
- Profit factor: not recomputed
- Max drawdown: not recomputed from fills
- Key subperiod results: not recomputed. The stage-2 window was already scored.
- Robustness/cost sensitivity: on a hypothetical EURUSD 15-pip-stop lattice with the study's +0.085R gross edge held fixed, the higher published intraday package is the unlabeled OANDA quote at 0.0933R before slippage. Adding an assumed 0.5 pip per side moves that hypothetical net expectancy to -0.075R. Those probabilities are not Phase 7 estimates.
- Result summary: the aggregate blocks a reliable doubling or loss probability. Commission and financing in R for Phase 7 need stop distance and hold time, which the aggregate does not contain. GBPUSD and USDJPY swap points have no published USD point value in the retrieved pages. No trading authority.
- Conclusion: NEED_MORE_DATA
- Reason: the documented strategy's trade-level record is absent, and several published cost components are missing or unlabeled. The edge-first check still fails at the 1.0-pip aggregate.
- Follow-up: keep the annual catalogue as the governing method. DEC-629 and DEC-630 are proposals awaiting an owner decision. The next measurement that would change the probability statement is a real trade-level R series for an already frozen candidate, with this cost record attached before the test is counted. That series is not available from repository documents, and protected artefacts stay closed.

### EXP-20261118-068 — Synthetic cross-year comparison engine V1

- Date: 2026-11-18
- Status: INCONCLUSIVE
- Hypothesis: A source-only join of validated annual pattern records can report recurrence, descriptive after-cost effects, and the frozen DEC-470 gate without treating a pass as significance or manufacturing a strategy.
- Code commit: `draft/cross-year-engine-v1`, parent `84644dd06e0d330d8a0fdb40c9d220b4b52956ef`
- Data manifest/version: none. No market-data files and no protected annual artifacts were opened.
- Pair(s): EURUSD, GBPUSD, USDJPY appear only as synthetic catalogue cells in the bounded performance check. The hand report and the null harness use EURUSD.
- Timeframe(s): 5m in the hand report and harness. The performance check uses 5m, 15m, and 1h.
- Data range: not applicable. Segment labels are the DEC-469 collection labels. No prices were read.
- Train period: not applicable
- Validation period: not applicable
- Final-test touched?: NO
- Strategy/model: no strategy. The engine joins existing annual records. Pattern grammar stays the DEC-470 catalogue grammar.
- Features: none added
- Parameters/search space: none. DEC-470 gate thresholds were read and not changed.
- Random seed (if relevant): 20261118. Noise uses `random.Random` and Box-Muller.
- Spread/cost model: harness assumption only, not a measured spread. One 0.8-pip round-trip spread. The engine does not charge that spread again. Annual nets already contain bid/ask spread plus slippage.
- Slippage model: source base 0.5 pip per fill and stress 1.0 pip per fill. Harness round trips are 1.0 and 2.0 pips. Stored `mean_net_pips_0p5` and `mean_net_pips_1p0` are used as-is.
- Risk assumptions: not applied. This experiment does not size trades.
- Trade count: no market trades. Harness support is 100 when a year is meant to be evaluable and 40 when it is meant to stay below the 75-observation label.
- Net return after costs: not a market result. Zero gross edge becomes -1.8 pips at the base cost and -2.8 pips at the stress cost under the stated harness formula. A constant 4.0-pip gross edge becomes +2.2 and +1.2 pips.
- Expectancy/trade: descriptive annual means only. Support-weighted pools are not independent-trial estimates.
- Profit factor: not computed
- Max drawdown: not computed
- Key subperiod results: not market years. With seed 20261118, zero-gross and negative-after-cost scenarios produced 0 gate passes across 336 synthetic patterns, including independent and correlated noise at 0.25, 1.0, and 3.0 pips. Strong planted patterns recovered 48 of 48. Alternating-sign, low-support, and eight-segment controls produced 0 passes. Eight evaluable segments stay `GATE_INOPERABLE_LT_9_SEGMENTS`.
- Robustness/cost sensitivity: both stored cost columns are reported. Jaccard near-duplicate evidence is unavailable because annual records store event-set hashes, not event ids. No substitute dedup is applied. No p-value is emitted.
- Result summary: the join, ranking cap, and frozen gate agree on synthetic records. A gate pass is not statistical significance. Historical cross-year result production, Strategy V1 synthesis, workflow changes, and trading remain unauthorized.
- Conclusion: NEED_MORE_DATA
- Reason: the engine can compare validated annual records, but this run did not compare frozen historical catalogues. Annual run 385 was not consumed.
- Follow-up: use the engine only on catalogues that have already passed their own evidence validators. Do not relax the nine-segment gate from these synthetic counts.

### EXP-20261118-069 — Catalogue-scale cross-year gate calibration

- Date: 2026-11-18
- Status: INCONCLUSIVE
- Hypothesis: The frozen DEC-470 cross-year gate, applied to a synthetic universe of 89,460 hypotheses, has a measurable false-pass count once annual noise reaches 4 and 8 pips, and the join can score a complete synthetic catalogue without dropping patterns.
- Code commit: `draft/cross-year-engine-v1`, parent `4b2426e22fdaa19fa6b1ecc80b97257088dbf4e5`. The acceptance commit that records this entry follows that parent.
- Data manifest/version: none. No market-data files and no protected annual artifacts were opened.
- Pair(s): the workload measurement uses EURUSD, GBPUSD, and USDJPY. The calibration scores anonymous hypotheses with the same gate.
- Timeframe(s): 5m, 15m, and 1h in the workload measurement. The calibration does not use bar prices.
- Data range: not applicable. Segment labels are the DEC-469 collection labels. No prices were read.
- Train period: not applicable
- Validation period: not applicable
- Final-test touched?: NO
- Strategy/model: no strategy. DEC-470 thresholds were read and were not changed after the counts below.
- Features: none added
- Parameters/search space: none. The gate is not a searched parameter.
- Random seed (if relevant): base seeds 20261118, 20261119, and 20261120. Generator seed = base seed + 1,000,000 when correlated, plus round(sigma × 1000), plus round(mean × 1000) × 100. Noise is `random.Random` plus Box-Muller. Counts below are in that base-seed order.
- Spread/cost model: harness assumption only, not a measured spread. One 0.8-pip round-trip spread. Base slippage round trip 1.0 pip. Stress slippage round trip 2.0 pips. Zero gross becomes −1.8 pips base and −2.8 pips stress. A gross mean of 0.4 pips stays negative after those costs when noise is zero. The engine does not charge spread or slippage again.
- Slippage model: source base 0.5 pip per fill and stress 1.0 pip per fill, inside the harness formula above.
- Risk assumptions: not applied. This experiment does not size trades.
- Trade count: no market trades. Evaluable synthetic years use support 100. The low-support control uses support 40.
- Net return after costs: not a market result.
- Expectancy/trade: descriptive annual means only. Support-weighted pools are not independent-trial estimates. No p-value was computed. The seed-to-seed range is the recorded uncertainty. It is not a standard error or a confidence interval.
- Profit factor: not computed
- Max drawdown: not computed
- Key subperiod results: not market years. Each stochastic scenario scores 89,460 hypotheses on 12 segments. Agreement with `cross_year_gate_passes` and with `compare_cross_year_patterns` was checked on 71 sampled pattern decisions, with 0 mismatches. The streamed tally matched the stored-path tally. Threshold comparisons were not reimplemented.
- Robustness/cost sensitivity: false passes are gate passes under zero gross or gross +0.4 pips. At noise 0, 0.25, and 1.0 pip, independent and correlated, every false-pass count was 0 of 89,460. Independent zero-gross noise of 4 pips passed 12, 10, and 15 hypotheses. Independent gross +0.4 at 4 pips passed 21, 39, and 30. Correlated versions of both 4-pip designs passed 0. Independent zero-gross noise of 8 pips passed 163, 147, and 143. Independent gross +0.4 at 8 pips passed 230, 255, and 231. Correlated zero-gross noise of 8 pips passed 0, 0, and 4,922. Correlated gross +0.4 at 8 pips passed 0. The 4,922 count is seed 20261120. Low-support and eight-segment controls were inoperable for all 89,460 hypotheses.
- Result summary: planted gross of 2.0 and 2.8 pips recovered 0 of 89,460 with no noise, because 2.0 pips stays below the stress and pooled-base hurdles and 2.8 pips leaves the stress net at 0. Planted gross of 3.0, 4.0, and 6.0 pips with no noise recovered 89,460 of 89,460. At 4.0 pips gross and 0.25 pip noise, independent and correlated recovery were both 89,460. At 6.0 pips gross and 1.0 pip noise, both were 89,460. Higher noise cuts recovery, and correlated seeds swing widely. Examples at 8 pip noise, seeds in the same order: planted 3.0 independent 2,360, 2,395, 2,214 and correlated 0, 1, 770; planted 4.0 independent 4,716, 4,630, 4,801 and correlated 34,644, 37, 0; planted 6.0 independent 14,341, 14,294, 14,122 and correlated 745, 53,948, 25,889. The nine-segment synthetic join scored 805,140 records (89,460 hypotheses × 9 segments) in 10.196 seconds of construction, 11.664 seconds of comparison, and 3.490 seconds of canonical JSON. Output size was 866,402,242 bytes, sha256 `d191fcc9086e3635008e4f37afa9c154e133d46564722a5fdac4feaf0075ed2d`, process max RSS 3,122,790,400 bytes. The twelve-segment join scored 1,073,520 records in 13.696, 15.164, and 3.551 seconds. Output size was 955,058,220 bytes, sha256 `1ea5d48bacfed7233da9a614ae9756e0d8b93084765bc6531a113f1ffe2c4022`, process max RSS 3,006,496,768 bytes. Both runs kept 89,460 patterns, dropped none, preserved fingerprint order, and filled every supplied panel. Python 3.12.13 on darwin. The figure 804,780 is 360 records below 9 × 89,460 and was not executed, because that would omit 40 hypotheses. Caller-supplied records are labeled `CALLER_SUPPLIED_ANNUAL_RECORDS_NOT_INDEPENDENTLY_VALIDATED`. Authentic research use remains unauthorized until prior evidence validation.
- Conclusion: NEED_MORE_DATA
- Reason: the calibration and the timing runs are synthetic. Frozen historical catalogues were not joined. The false-pass counts stand as observed and were not used to edit DEC-470.
- Follow-up: keep the nine-segment rule and the other DEC-470 thresholds unchanged. Future authentic research use still requires evidence validation of the source annual catalogues before submission. Annual run 385 stays unopened.

### EXP-20261119-070 — Event-level evidence V1 synthetic contract

- Date: 2026-11-19
- Status: INCONCLUSIVE
- Hypothesis: A source-only event contract can preserve caller-supplied outcome windows well enough to count overlap and connected episode groups, while keeping those counts descriptive and leaving DEC-470 unchanged.
- Code commit: branch `draft/event-level-evidence-v1`, parent `85536adadedeee59abdc4a13f02de23ee0b3979a`
- Data manifest/version: none. No market-data files and no protected annual artifacts were opened. The synthetic manifest in the unit tests is SHA-256 of the literal `synthetic-event-evidence-v1\n`.
- Pair(s): EURUSD, GBPUSD, and USDJPY appear only as synthetic observation labels.
- Timeframe(s): 5m and 1h in the synthetic rows. Horizons are the frozen 60 and 240 minutes.
- Data range: not applicable. Segment labels are the DEC-469 collection labels. No prices were read.
- Train period: not applicable
- Validation period: not applicable
- Final-test touched?: NO
- Strategy/model: no strategy. Pattern grammar stays the DEC-470 catalogue grammar. Event identity is a new observation-key hash and is not an annual `event_fingerprint`.
- Features: none added. A supplied feature row is checked for identity alignment and is not copied into the event document.
- Parameters/search space: none. DEC-470 gate thresholds were read and were not changed. The 89,460-hypothesis universe and the EXP-20261118-069 false-pass counts, including 4,922 correlated zero-gross passes at 8 pips on seed 20261120, stay recorded constraints.
- Random seed (if relevant): 20261119, used only to shuffle 4,000 synthetic rows before a determinism check.
- Spread/cost model: none applied. Stored base and stress nets are the caller-supplied `net_pips_0p5` and `net_pips_1p0`.
- Slippage model: DEC-470 base 0.5 pip per fill and stress 1.0 pip per fill are recorded and are not reapplied.
- Risk assumptions: not applied. This experiment does not size trades.
- Trade count: no market trades. The bounded measurement uses 2,000 fully overlapping synthetic events and 2,000 non-overlapping synthetic events.
- Net return after costs: not a market result.
- Expectancy/trade: not computed. Overlap counts and candidate episode sizes are descriptive. They are not independent-trial estimates and they are not p-values.
- Profit factor: not computed
- Max drawdown: not computed
- Key subperiod results: not market years. Touching windows stay separate groups. A partial overlap is one group. A chain of three windows is one group even when the first and third do not overlap directly. A 60-minute window nested inside a 240-minute window is one cross-horizon group and two within-horizon groups. Duplicate and contradictory rows fail closed.
- Robustness/cost sensitivity: not a cost study. The large synthetic document counted 1,999,000 overlapping pairs in the 2,000-event clique and stored none of those pairs. One compile, including validation, took 2.260 seconds. Python tracemalloc peak was 39,863,757 bytes. Canonical JSON was 4,899,373 bytes. SHA-256 of the body was `193533043e2279a3c0b486389c9722a8517317e1e61be2643f228dcdd91e0ac5`. Python 3.12.13 on darwin. The final local run of `tests.test_annual_pattern_catalogue_event_evidence` together with the miner, cell-evidence, protocol, segment-freeze, and cross-year modules was 67 tests and exited 0 in 7.307 seconds.
- Result summary: the contract distinguishes raw directional support, unique physical events, overlapping pairs, connected episode groups, and a candidate component count. Episode groups are recorded as statistically unresolved. Cross-symbol and cross-timeframe independence is not established. Structural validation is not validation of frozen annual evidence. Historical event recovery remains blocked because annual records store membership hashes rather than event rows.
- Conclusion: NEED_MORE_DATA
- Reason: the rows are synthetic. Frozen historical catalogues were not opened, and event ids cannot be recovered from their `event_fingerprint` hashes without the original observations.
- Follow-up: keep DEC-470 unchanged. Use this contract only on caller-supplied events until a separate decision authorizes the historical observation rows. Annual run 385 stays unopened. The pre-merge review of identity, membership, canonical bytes, and overlap complexity is `EXP-20261119-071`.

### EXP-20261119-071 — Event-level evidence V1 pre-merge hardening

- Date: 2026-11-19
- Status: INCONCLUSIVE
- Hypothesis: The source-only event contract can enforce the existing one-timestamp observation identity, reject contradictory state assertions, require canonical serialized bytes, and count half-open overlaps in O(n log n), while leaving DEC-470 and the frozen miner unchanged.
- Code commit: branch `draft/event-level-evidence-v1`, parent `ce62d5adc560dd2863711d5edbe887f0bcd08ae6`
- Data manifest/version: none. No market-data files and no protected annual artifacts were opened. The synthetic manifest in the unit tests is SHA-256 of the literal `synthetic-event-evidence-v1\n`.
- Pair(s): EURUSD, GBPUSD, and USDJPY appear only as synthetic observation labels.
- Timeframe(s): 5m and 1h in the synthetic rows. Horizons are the frozen 60 and 240 minutes.
- Data range: not applicable. No prices were read.
- Train period: not applicable
- Validation period: not applicable
- Final-test touched?: NO
- Strategy/model: no strategy. No new trading threshold. Pattern membership is a caller assertion. Contradictory current states of one dimension, and contradictory prior states at one lag, are rejected. Feature values and DEC-471 cutpoints are not used.
- Features: none added. A supplied feature row is still an identity check only.
- Parameters/search space: none. The 89,460-hypothesis universe and DEC-470 constants were not retuned. EXP-20261118-069, including 4,922 correlated zero-gross passes at 8 pips on seed 20261120, stays a recorded constraint.
- Random seed (if relevant): 20261119, used only to shuffle 4,000 synthetic rows before the compile measurement.
- Spread/cost model: none applied.
- Slippage model: DEC-470 base 0.5 pip per fill and stress 1.0 pip per fill are recorded and are not reapplied.
- Risk assumptions: not applied.
- Trade count: no market trades. Measurements use synthetic intervals only.
- Net return after costs: not a market result.
- Expectancy/trade: not computed. Overlap counts remain descriptive. They are not independent-trial estimates and they are not p-values.
- Profit factor: not computed
- Max drawdown: not computed
- Key subperiod results: not market years. The same observation id on horizons 60 and 240 is accepted when both start at the same timestamp and rejected when the starts differ. LOW and HIGH of one dimension on that observation are rejected. A LOW-to-HIGH transition remains a prior state plus a current state.
- Robustness/cost sensitivity: not a cost study. One compile of 2,000 fully overlapping synthetic events plus 2,000 non-overlapping synthetic events, including validation, took 2.370933 seconds. Python tracemalloc peak was 41,655,298 bytes. Canonical JSON was 4,900,035 bytes. SHA-256 of the body was `38d6b8c30ef4f0e4b6d44a23bf340b0ae9c92458df159ecbba17dd2bb4079c81`. The 2,000-event clique counted 1,999,000 pairs and stored none. Isolated pair-counter timings on a same-window clique, Python 3.12.13 on darwin: 2,000 events, 0.001836 seconds mean over five repeats, tracemalloc peak 159,988 bytes; 8,000 events, 0.008142 seconds mean over five repeats, peak 639,688 bytes, 31,996,000 pairs; 20,000 events, 0.022327 seconds, peak 1,600,032 bytes, 199,990,000 pairs. The replaced active-list scan on the same cliques took 0.026569 seconds at 2,000, 0.433818 seconds at 8,000, and 2.481579 seconds at 20,000, with the same pair counts. No catalogue-scale historical run was executed. The local run of the event-evidence tests with the miner, cell-evidence, protocol, segment-freeze, and cross-year modules was 70 tests and exited 0 in 7.693 seconds.
- Result summary: serialized evidence that is not canonical UTF-8 JSON is rejected, including duplicate object keys, reordered keys, extra whitespace, a byte-order mark, and UTF-16. Malformed timestamps and event identities that do not match the observation key fail closed. Cross-symbol and cross-timeframe reuse of a caller-supplied id stays unresolved. Structural validation is not validation of frozen annual evidence.
- Conclusion: NEED_MORE_DATA
- Reason: the rows are synthetic. Frozen historical catalogues were not opened, and event ids cannot be recovered from their `event_fingerprint` hashes without the original observations. A consistent membership assertion is not evidence that a feature row satisfied the pattern.
- Follow-up: keep DEC-470 unchanged. Annual run 385 stays unopened. No merge is authorized by this experiment.

### EXP-20261119-072 — Statistical uncertainty V1 synthetic calibration

- Date: 2026-11-19
- Status: INCONCLUSIVE
- Hypothesis: A source-only uncertainty contract can keep event-evidence inference unavailable, and a predeclared synthetic harness can show how overlap, serial correlation, shared events, and a multiple-testing family change exploratory interval behavior, without retuning DEC-470 or claiming calibrated catalogue error control.
- Code commit: branch `draft/statistical-uncertainty-v1`, parent `10ac7086c18ca1002a4529e37dd36e6c36983043`
- Data manifest/version: none. No market-data files and no protected annual artifacts were opened. The synthetic manifest in the unit tests is SHA-256 of the literal `synthetic-statistical-uncertainty-v1\n`.
- Pair(s): EURUSD, GBPUSD, and USDJPY appear only as synthetic labels. The common-shock scenario is two unlabeled series, not a market pair.
- Timeframe(s): 5m appears only as a synthetic event-evidence label. Horizons in that fixture are the frozen 60 and 240 minutes. The overlapping-horizon scenario uses a span of 4 synthetic observations, not those market horizons.
- Data range: not applicable. No prices were read.
- Train period: not applicable
- Validation period: not applicable
- Final-test touched?: NO
- Strategy/model: no strategy. The governing method remains DEC-469 / DEC-268 annual catalogue discovery. This module is the statistical-uncertainty pattern tool. IID normal intervals, Newey-West Bartlett lags 1, 4, and 8, moving-block lengths 1, 4, and 8, a shared-clock block resample, and Holm step-down are exploratory. Block length 1 and independent column resampling are incorrect-assumption diagnostics. None was selected by observed coverage.
- Features: none added. Asserted pattern membership is not treated as feature-state proof.
- Parameters/search space: the frozen family remains 89,460 directional hypotheses per annual segment. Holm is not applied to that family. A method check uses 40 known-sigma Gaussian hypotheses, series length 30, alpha 0.05, and 160 complete-null replications. Closed-form scenarios use 160 replications. Dependence scenarios add 20 block-bootstrap replications of 99 draws. Seeds are 20261121, 20261122, 20261123, and Holm seed 20261124. Seeds 20261118, 20261119, and 20261120 are refused. EXP-20261118-069, including 4,922 correlated zero-gross passes at 8 pips on seed 20261120, was not used to tune any threshold.
- Random seed (if relevant): primary seed 20261121. Each scenario restarts there, so iid scenarios that consume the same normal draws share a noise path. Variability across seeds is a separate stream.
- Spread/cost model: `negative_after_cost` subtracts a synthetic 0.5 pip shift from standard normal draws. That shift is not a broker model and is not applied to event evidence.
- Slippage model: not applied. DEC-470 base 0.5 and stress 1.0 pip slippage stay recorded and unchanged.
- Risk assumptions: not applied. No trade is sized. Overlapping signals are not treated as simultaneously executable independent trades. Interval results are not portfolio profits.
- Trade count: no market trades.
- Net return after costs: not a market result.
- Expectancy/trade: not a market expectancy. On event evidence the unweighted mean of supplied base nets is descriptive and has no standard error. Effective sample size is unavailable there. Under a declared iid scenario it equals n. Under the declared AR(1) with phi 0.8 it is `n * (1 - phi) / (1 + phi)` using that known phi, not an estimated autocorrelation. Shared-event copies use the event count, not the doubled row count. Overlapping horizons and common shocks stay unavailable.
- Profit factor: not computed
- Max drawdown: not computed
- Key subperiod results: not market years. At seed 20261121 and 160 replications, the iid 95 percent interval covered the true mean on 144/160 independent zero-edge series and excluded zero on 16/160. The same interval on the negative-after-cost series was entirely above zero on 0/160. The planted mean of 0.4 had sample-mean average 0.4086505280466667, coverage 144/160, and 148/160 intervals entirely above zero. The same iid interval on AR(1) phi 0.8 covered zero on 73/160 and excluded zero on 87/160. Its median width was 0.6754540834406229, against 1.3805102957545334 for Newey-West lag 8. Moving-block median widths on that series were 0.6706575962752688 at block length 1 and 1.216905620318538 at block length 8, from 20 replications. Stacking two copies of one event series narrowed the median iid width from 0.43570384868063305 to 0.3071187840659161 and cut coverage from 144/160 to 126/160. The overlapping four-observation average had iid coverage 95/160 against 144/160 for the short series, and Newey-West lag 8 median width 0.3565615326723143 against iid width 0.2094512651184083. The common-shock stacked interval had median width 0.43882343455091744 against 0.5427501321698607 for the contemporaneous average. Sparse n=12 median width was 1.1014312107593385 against dense n=240 width 0.25348399582201. Constant series produced no interval. Coverage of the zero-edge iid interval on seeds 20261121, 20261122, and 20261123 was 144/160, 147/160, and 150/160. The Holm method check rejected 139/160 families uncorrected and 6/160 after Holm. That check is not the 89,460-hypothesis family, and no catalogue error control is claimed.
- Robustness/cost sensitivity: not a market cost study. One canonical calibration, including the validation recompute, took 4.778543 seconds. Python tracemalloc peak was 401,753 bytes. Canonical JSON was 59,976 bytes. SHA-256 of the document was `315594a298991932970684c10f3dca86314275271f6daa19f94055608ed25afc`. Python 3.12.13 on darwin. The focused uncertainty tests were 16 and exited 0 in 11.553 seconds. Together with the event-evidence, miner, annual-evidence, protocol, segment-evidence, and cross-year modules, the run was 86 tests and exited 0 in 18.991 seconds. No catalogue-scale resample was run.
- Result summary: event-evidence sampling uncertainty, effective sample size, and multiple-testing adjustment remain unavailable. Episode groups are not independent trials. The synthetic harness shows the expected direction for incorrect independence, serial correlation, overlap, common shocks, sparse versus dense support, a planted mean, and a negative shift. Those diagnostics are not calibrated catalogue error control.
- Conclusion: NEED_MORE_DATA
- Reason: the rows are synthetic. Frozen historical catalogues were not opened. Valid individual p-values for the 89,460-hypothesis family are not available, so Holm is not applied to that family. Dependence-preserving resampling was not treated as a p-value generator.
- Follow-up: keep DEC-470, the event-evidence schema, the annual miner, and the cross-year statistical block unchanged. Annual run 385 stays unopened. No merge is authorized by this experiment. The pre-merge review of finite-sample effective sample size, Monte Carlo uncertainty, dependence-scenario seeds, and the synthetic clock contract is `EXP-20261119-073`.

### EXP-20261119-073 — Statistical uncertainty V1 pre-merge hardening

- Date: 2026-11-19
- Status: INCONCLUSIVE
- Hypothesis: The source-only uncertainty contract can distinguish the finite-sample AR(1) variance-equivalent size from its large-sample approximation, report Monte Carlo uncertainty for synthetic coverage and rejection rates, extend seed variability to the dependence scenarios, and label shared-clock inputs as synthetic, without retuning DEC-470 or authorizing catalogue inference.
- Code commit: branch `draft/statistical-uncertainty-v1`, parent `f9ffc238077288659dd61ffcc43d1bc8915a7192`
- Data manifest/version: none. No market-data files and no protected annual artifacts were opened. The synthetic manifest in the unit tests is SHA-256 of the literal `synthetic-statistical-uncertainty-v1\n`.
- Pair(s): EURUSD, GBPUSD, and USDJPY appear only as synthetic labels. The common-shock scenario is two unlabeled series, not a market pair.
- Timeframe(s): 5m appears only as a synthetic event-evidence label. Horizons in that fixture are the frozen 60 and 240 minutes. The overlapping-horizon scenario uses a span of 4 synthetic observations, not those market horizons.
- Data range: not applicable. No prices were read.
- Train period: not applicable
- Validation period: not applicable
- Final-test touched?: NO
- Strategy/model: no strategy. The governing method remains DEC-469 / DEC-268 annual catalogue discovery. This module remains the statistical-uncertainty pattern tool. No lag, block length, method, or threshold was selected from observed coverage. EXP-20261118-069 false-pass counts were not used as tuning targets.
- Features: none added. Asserted pattern membership is not treated as feature-state proof.
- Parameters/search space: the frozen family remains 89,460 directional hypotheses per annual segment. That count is the per-segment search universe. It is not evidence that multiple testing or selection across years is controlled. Holm is not applied to that family. The method check remains 40 known-sigma Gaussian hypotheses, series length 30, alpha 0.05, and 160 replications. A second stream uses seed 20261125 and a shared Gaussian shock with marginal variance 1. Closed-form scenarios use 160 replications. Dependence scenarios add 20 block-bootstrap replications of 99 draws. Variability seeds remain 20261121, 20261122, and 20261123. Seeds 20261118, 20261119, and 20261120 stay refused. The seeds are not pooled into one denominator.
- Random seed (if relevant): primary seed 20261121. Each scenario restarts there, so scenarios that consume the same normal draws share a noise path. The variability row at 20261121 is that primary row, not an additional sample. Seed-to-seed range is not a binomial standard error.
- Spread/cost model: `negative_after_cost` still subtracts a synthetic 0.5 pip shift. That shift is not a broker model and is not applied to event evidence.
- Slippage model: not applied. DEC-470 base 0.5 and stress 1.0 pip slippage stay recorded and unchanged.
- Risk assumptions: not applied. No trade is sized. Overlapping signals are not treated as simultaneously executable independent trades.
- Trade count: no market trades.
- Net return after costs: not a market result.
- Expectancy/trade: not a market expectancy. On event evidence the effective sample size stays unavailable. Neither AR(1) formula is applied there. Under the declared stationary AR(1) with phi 0.8 and n 80, the finite-sample variance-equivalent size is 9.411764696100496 and the large-sample approximation `n * (1 - phi) / (1 + phi)` is 8.888888888888888. The difference is 0.5228758072116086. The reported value is the finite-sample expression. At n 2 the same phi gives 1.1111111111111112 against an approximation of 0.22222222222222215. At n 2,000 the values are 222.71714922048997 and 222.22222222222214. The absolute gap stays near one half of an observation while the relative gap shrinks. Phi 0 leaves both expressions at 80. Absolute phi of 1 or more is unavailable. Phi is the declared constant, not an estimate.
- Profit factor: not computed
- Max drawdown: not computed
- Key subperiod results: not market years. The primary-seed closed-form counts are unchanged from EXP-20261119-072: zero-edge iid coverage 144/160 and exclusions 16/160; AR(1) iid coverage 73/160 and exclusions 87/160; stacked shared-event coverage 126/160; overlapping long-horizon coverage 95/160 against 144/160 for the short series. The Wilson 95 percent interval for 144/160 is 0.8437374796961266 to 0.9375055641666694, with binomial standard error 0.023717082451262844. That interval is not an exact population error rate. The AR(1) moving-block length 8 diagnostic covered on 13/20 draws. Its Wilson interval is 0.43285427668523624 to 0.818808175898918. The bootstrap calibration conclusion is unresolved, and those 20 replications do not establish calibrated confidence intervals. Constant series still have 0 available intervals out of 160, so their Wilson interval is unavailable. Across seeds 20261121, 20261122, and 20261123, zero-edge iid coverage spanned 0.900 to 0.9375. AR(1) iid coverage spanned 0.43125 to 0.45625 and false exclusion spanned 0.54375 to 0.56875. AR(1) Newey-West lag 8 coverage spanned 0.73125 to 0.78125. AR(1) moving-block length 8 coverage spanned 0.650 to 0.850. The wider bootstrap span is Monte Carlo noise from 20 replications, not a reason to choose a block length. The independent Holm check rejected 139/160 families uncorrected and 6/160 after Holm. The correlated-null check rejected 78/160 uncorrected and 6/160 after Holm. The Wilson interval for 6/160 is 0.017297923166500122 to 0.07938980736714218. Familywise calibration stays unresolved. The check does not control the 89,460-hypothesis segment or selection across years.
- Robustness/cost sensitivity: not a market cost study. One canonical calibration, including the validation recompute, took 13.600200 seconds. Python tracemalloc peak was 2,416,478 bytes. Canonical JSON was 361,184 bytes. SHA-256 of the document was `d300633d49dca9696e83d3f57f989dff2aecd9f79baffc8fefa9a48d8e5fdf51`. Python 3.12.13 on darwin arm64. Focused `tests.test_annual_pattern_catalogue_statistical_uncertainty` was 19 tests and exited 0 in 32.229 seconds. Neighboring event-evidence, miner, annual-evidence, protocol, segment-evidence, and cross-year tests were 70 tests and exited 0 in 7.465 seconds. No catalogue-scale resample was run. Workflow files were not edited.
- Result summary: event-evidence sampling uncertainty, effective sample size, and catalogue Holm adjustment remain unavailable. The finite-sample AR(1) size and the large-sample approximation are both reported for the declared synthetic model and are not interchangeable. Coverage and rejection rates now carry numerator, denominator, binomial standard error, and Wilson interval. Dependence-scenario seed ranges are recorded separately from that Monte Carlo uncertainty. Shared-clock resampling validates a synthetic clock id or records that equal length is not timestamp alignment. Authentic event timelines were not aligned.
- Conclusion: NEED_MORE_DATA
- Reason: the rows are synthetic. Frozen historical catalogues were not opened. Valid individual p-values for the 89,460-hypothesis family are not available. One hundred sixty closed-form replications do not establish an exact population error rate, and twenty bootstrap replications do not establish calibrated confidence intervals.
- Follow-up: keep DEC-470, the event-evidence schema, the annual miner, and the cross-year statistical block unchanged. Annual run 385 stays unopened. No merge is authorized by this experiment.

### EXP-20261119-074 — Dependence-aware statistical validation V1 synthetic harness

- Date: 2026-11-19
- Status: INCONCLUSIVE
- Hypothesis: A source-only, predeclared synthetic harness can show which uncertainty procedures keep nominal coverage and which null tests keep their size under serial dependence, overlap, shared events, common shocks, and selection, while leaving catalogue inference unauthorized.
- Code commit: branch `draft/dependence-aware-validation-v1`, parent `168d4c2b850fb0ff6f97fba3b0d287332d9cfe4f`
- Data manifest/version: none. No market-data files and no protected annual artifacts were opened. The synthetic manifest in the unit tests is SHA-256 `3bc70c9120e8c09c4850bf63f274e1a9236ce2cb21d736660647491766c69e32` of the literal `synthetic-dependence-aware-validation-v1\n`.
- Pair(s): none. The common-shock scenario is two unlabeled synthetic series.
- Timeframe(s): none. Overlap uses a horizon of 4 synthetic observations. That horizon is not the frozen 60-minute or 240-minute event horizon.
- Data range: not applicable. No prices were read.
- Train period: calibration partition, master seed 20261126, closed-form replicates 80, bootstrap replicates 20. This partition cannot validate a method.
- Validation period: holdout partition, master seed 20261211, closed-form replicates 400, bootstrap replicates 60 of 99 draws, studentized replicates 60 of 49 draws. Stability seeds 20261212 and 20261213 use 40 replicates and are not pooled into the holdout denominator.
- Final-test touched?: NO
- Strategy/model: no strategy. The governing method remains DEC-469 / DEC-268 annual catalogue discovery. This module is the dependence-aware-validation pattern tool. Candidate procedures are the IID normal interval, an IID variance z test, a declared-model Gaussian z test, Newey–West Bartlett lags 1, 4, 8, and 16, moving-block lengths 1, 4, 8, and 16, circular and stationary block length 16, a shared-clock block of length 8, an independent-column diagnostic, a cluster-event bootstrap, a shock-rebuild bootstrap, a null-centered studentized moving-block test, and Holm step-down on exact Gaussian family p-values. No lag, block, or threshold was chosen from holdout coverage. The prior statistical-uncertainty AR(1) counts 73/160, 117/160, and 13/20 were not used as targets.
- Features: none added.
- Parameters/search space: the frozen family remains 89,460 directional hypotheses per annual segment. Bounded synthetic families have sizes 10, 40, and 160. Holm is not applied to the 89,460 family. Familywise error at 89,460 was not estimated. DEC-470 constants were not retuned. Seeds 20261118 through 20261125 are refused.
- Random seed (if relevant): holdout master 20261211. Calibration master 20261126. Family seeds 20261130, 20261215, 20261216, 20261217, 20261219, 20261220, 20261221, and 20261222. Bootstrap streams use salt `0x5A17C3D1`. The generator is Box–Muller on `random.Random`.
- Spread/cost model: none applied. Planted means of +0.35 and −0.35 are synthetic location shifts, not broker costs.
- Slippage model: not applied. DEC-470 base 0.5 and stress 1.0 pip slippage stay recorded and unchanged.
- Risk assumptions: not applied. No trade is sized.
- Trade count: no market trades.
- Net return after costs: not a market result.
- Expectancy/trade: not a market expectancy. The estimand is the mean of a synthetic series. Effective sample size is identified only from the declared model. Independent series of length 120 have size 120. Weak AR(1) phi 0.3 has size 64.97237569060773. Strong AR(1) phi 0.8 has size 13.84615384615259. The long-memory moving average has size 7.663093882562344. Overlapping windows of horizon 4 have size 30.31578947368421. Shared events have size 60, including the duplicated-row target. The regime-change series and the horizon contrast have no identified size. None of these sizes is applied to event evidence.
- Profit factor: not computed
- Max drawdown: not computed
- Key subperiod results: not market years. On the holdout, the declared-model z interval covered the true zero mean at 375/400 independent, 376/400 weak AR(1), 376/400 strong AR(1), 374/400 long memory, 376/400 overlapping windows, 386/400 unique events, 380/400 common-shock primary, 380/400 common-shock contrast, 376/400 short horizon, 376/400 long horizon, 377/400 horizon contrast, 378/400 changing volatility, and 377/400 regime change. Those rows validated, and their null rejection counts support `valid_p_values_established` on the zero-mean eligible series. Eligible Newey–West lag 16 failed at 325/400 on the strong AR(1), 343/400 on overlapping windows, and 347/400 on the 60 unique events. Eligible moving block 16 failed at 49/60 on the strong AR(1). Eligible moving block 4 failed at 48/60 on overlapping windows. Eligible Newey–West lags on the horizon contrast overcovered at 400/400. Those lags and blocks were not increased or decreased after the counts were seen. IID intervals failed where independence is false: 342/400 weak AR(1), 186/400 strong AR(1), 133/400 long memory, 266/400 overlapping windows, 132/400 regime change, and 340/400 duplicated rows. Studentized tests rejected 4/60, 4/60, 5/60, and 3/60 and stay below the 200-replicate validation floor, so their p-values are computed and not established. Holm on a size-40 complete null rejected 17/400 equicorrelated families and 19/400 independent families, against uncorrected 286/400 and 348/400. The size-10 Holm count was 26/400, Wilson bounds 0.04474048189620036 to 0.09353521417463759, which is insufficient precision rather than a clear familywise failure. The size-160 study at 80 replicates is insufficient by design. Four segments of 20 complete-null hypotheses recurred by chance on 115/400 replicates. An identical shared copy had correlation 1.0. Confirmation p-values for those copies are `P_VALUES_UNAVAILABLE`.
- Robustness/cost sensitivity: not a market cost study. One canonical compile took 17.177 seconds. Python tracemalloc peak was 7,871,316 bytes. Canonical JSON was 974,640 bytes. SHA-256 of the document was `296cd7113a302a893717cbc1d442efffc487c5169b5ca60568451116ac4b7c59`. Python 3.12.13 on darwin. Holm arithmetic on one vector, outside the hashed document, took 0.035872 seconds at 89,460 hypotheses and estimated no familywise error. A bootstrap validation of at least 200 replicates was specified and was not launched. Focused dependence-validation tests were 10 and exited 0 in 24.177 seconds. Neighboring statistical-uncertainty, event-evidence, protocol, miner, cross-year, and segment-evidence tests were 82 and exited 0 in 41.133 seconds. Workflow files were not edited.
- Result summary: the declared-model Gaussian interval met its synthetic coverage and null-size checks on the eligible zero-mean processes. Several eligible HAC and block-bootstrap settings failed finite-sample calibration and remain failed. Bootstrap and studentized p-values lack the predeclared Monte Carlo precision. Bounded Holm can control a declared Gaussian family of size 40 and does not control the 89,460-hypothesis universe. Every synthetic validation status leaves catalogue inference unauthorized.
- Conclusion: NEED_MORE_DATA
- Reason: the rows are synthetic. Frozen historical catalogues were not opened. Valid p-values for the 89,460-hypothesis family are not available. Sixty bootstrap replicates do not establish calibrated percentile intervals. A synthetic pass is not catalogue validity.
- Follow-up: keep DEC-470, the event-evidence schema, the statistical-uncertainty schema, the annual miner, and the cross-year statistical block unchanged. Annual run 385 stays unopened. No merge is authorized by this experiment. EXP-20261120-075 withdraws the claim that the inspected 17/400 and 19/400 Holm counts validated empirical familywise control. Those numerators are unchanged.

### EXP-20261120-075 — Dependence-aware validation V1 interpretation correction

- Date: 2026-11-20
- Status: INCONCLUSIVE
- Hypothesis: The synthetic harness in EXP-20261119-074 can separate Holm's conditional theorem, an observed familywise rate, a one-sided Monte Carlo upper bound, excessive familywise error, and an inconclusive simulation, and it can separate an exact finite dependence horizon from a practical truncation, an asymptotic approximation, and an unverified approximation, without a new large validation experiment.
- Code commit: branch `draft/dependence-aware-validation-v1`, parent of this correction `34fe084bbef82b6bdc351b88432bd2597a65e309`, branch base `168d4c2b850fb0ff6f97fba3b0d287332d9cfe4f`
- Data manifest/version: none. No market-data files and no protected annual artifacts were opened. The synthetic manifest is unchanged: SHA-256 `3bc70c9120e8c09c4850bf63f274e1a9236ce2cb21d736660647491766c69e32` of the literal `synthetic-dependence-aware-validation-v1\n`.
- Pair(s): none.
- Timeframe(s): none.
- Data range: not applicable. No prices were read.
- Train period: unchanged. Calibration master seed 20261126. That partition cannot validate a method.
- Validation period: unchanged. Holdout master seed 20261211. The holdout was already inspected. The revised acceptance rule is a methodological correction of that inspection, not a fresh independent validation.
- Final-test touched?: NO
- Strategy/model: no strategy. The governing method remains DEC-469 / DEC-268 annual catalogue discovery. This module remains the dependence-aware-validation pattern tool. No lag, block, or threshold was chosen from the inspected holdout. The prior AR(1) counts 73/160, 117/160, and 13/20 were not used as targets.
- Features: none added.
- Parameters/search space: unchanged. The frozen family remains 89,460 directional hypotheses per annual segment. Familywise error at 89,460 was not estimated. The positive familywise rule is now the one-sided 95 percent Wilson upper bound at or below alpha 0.05, using quantile 1.6448536269514722, plus the predeclared precision floor of at least 200 replicates and a two-sided Wilson half-width of at most 0.04, plus exact finite-sample assumptions. A point estimate at or below alpha is not sufficient. The excessive-error rule is unchanged: two-sided Wilson lower bound above alpha with at least 40 replicates. The quantile was not selected to make 17/400 or 19/400 pass. No new large familywise experiment was launched.
- Random seed (if relevant): the harness seeds are unchanged. A bounded generator check uses seed 20261230, 4 replications, and family size 3. That seed is not a holdout seed and not an acceptance threshold.
- Spread/cost model: none applied.
- Slippage model: not applied. DEC-470 slippage stays recorded and unchanged.
- Risk assumptions: not applied. No trade is sized.
- Trade count: no market trades.
- Net return after costs: not a market result.
- Expectancy/trade: not a market expectancy. Effective sample sizes are unchanged and are not applied to event evidence.
- Profit factor: not computed
- Max drawdown: not computed
- Key subperiod results: not market years. Raw numerators and denominators are unchanged on all 284 rows and on all six family studies. Status changes come only from the corrected rules. Holdout row labels moved from 40 validated, 47 failed, 46 insufficient, and 24 unverified to 30 validated, 47 failed, 7 insufficient, and 73 unverified. The ten rows that left validated are Newey–West intervals whose coverage was not a clear failure: independent lag 1 at 374/400, unique-events lag 1 at 382/400 and lag 4 at 376/400, common-shock primary lags 1 and 4 at 378/400, common-shock contrast lag 1 at 377/400 and lag 4 at 372/400, short-horizon lag 1 at 375/400, and planted means lag 1 at 374/400. They are `MODEL_ASSUMPTIONS_UNVERIFIED` because a Bartlett lag is not an exact finite-sample model. Thirty-nine previously insufficient Newey–West and block-bootstrap rows moved to the same unverified status. Four studentized rows stayed insufficient at 4/60, 4/60, 5/60, and 3/60. Failed coverage stayed failed, including strong AR(1) Newey–West lag 16 at 325/400, overlapping Newey–West lag 16 at 343/400, unique-events Newey–West lag 16 at 347/400, horizon-contrast Newey–West lags 4, 8, and 16 at 400/400, strong AR(1) moving block 16 and circular block 16 at 49/60, and overlapping moving block 4 at 48/60. No lag or block was retuned. Holm counts stayed 17/400 equicorrelated, 19/400 independent, 17/400 mixed, 26/400 at family size 10, and 4/80 at family size 160. One-sided 95 percent upper bounds are 0.062391672641129325, 0.06823777952908633, 0.062391672641129325, 0.08833948478967546, and 0.10679896023205511. All five are above 0.05, so the empirical claim is inconclusive. Uncorrected counts stayed 286/400, 348/400, 400/400, 174/400, and 78/80 and remain excessive. The calibration study stayed 1/40 and exploratory, with one-sided upper bound 0.10458856696171026. Twenty-two known-model oracle rows and eight IID normal rows on exact horizon 0 remain validated. No practical dependence estimator and no experimental bootstrap is validated. An oracle pass is not evidence that a dependence estimator has been validated.
- Robustness/cost sensitivity: not a market cost study. One canonical compile on Python 3.12.13 took 18.127 seconds. Tracemalloc peak was 9,447,726 bytes. Canonical JSON was 1,200,625 bytes. SHA-256 was `45fc28d57302936bcd6af144081dab8850eee10ba26bb5ab803566f67df1a090`. The EXP-20261119-074 document remains SHA-256 `296cd7113a302a893717cbc1d442efffc487c5169b5ca60568451116ac4b7c59`. The hash changed because labels changed. The numerators did not. Holm arithmetic outside the document took 0.035565 seconds at 89,460 hypotheses and estimated no familywise error. Routine validation does not regenerate the 400-replicate experiment. The bounded check at seed 20261230 only requires two runs of the generator to agree. Focused dependence-validation tests were 11 and exited 0 in 24.844 seconds. Neighboring statistical-uncertainty, event-evidence, protocol, miner, cross-year, and segment-evidence tests were 82 and exited 0 in 42.161 seconds. Workflow files were not edited. A bootstrap validation of at least 200 replicates was not launched.
- Result summary: Holm's theorem still applies only when the marginal p-values are valid, and that theorem was not established by these simulations. The inspected familywise rates do not establish a one-sided upper bound at or below 0.05. Fixed-lag Newey–West and fixed-block bootstrap assumptions are truncations or asymptotic approximations, not exact finite-sample models. The declared-model interval remains an oracle. Catalogue inference stays unauthorized.
- Conclusion: NEED_MORE_DATA
- Reason: the rows are synthetic. The holdout was already inspected, so the revised rule is not an independent confirmation. Frozen historical catalogues were not opened. Valid p-values for the 89,460-hypothesis family are not available. Sixty bootstrap replicates and sixty studentized replicates do not establish calibrated intervals or p-values.
- Follow-up: keep DEC-470, the event-evidence schema, the statistical-uncertainty schema, the annual miner, and the cross-year statistical block unchanged. Annual run 385 stays unopened. No merge is authorized by this experiment. EXP-20261120-076 withdraws the claim that the eight IID normal rows on exact horizon 0 are finite-sample exact. Those numerators are unchanged.

### EXP-20261120-076 — Dependence-aware validation V1 finite-sample classification correction

- Date: 2026-11-20
- Status: INCONCLUSIVE
- Hypothesis: The already inspected synthetic holdout in EXP-20261119-074 and EXP-20261120-075 can separate a matching dependence structure from an exact finite-sample reference distribution, without changing interval calculations or launching a new validation experiment.
- Code commit: branch `draft/dependence-aware-validation-v1`, parent of this correction `5dda82ffd7613ec1dbb842fcc91e4a8e1ab53c8a`, branch base `168d4c2b850fb0ff6f97fba3b0d287332d9cfe4f`
- Data manifest/version: none. No market-data files and no protected annual artifacts were opened. The synthetic manifest is unchanged: SHA-256 `3bc70c9120e8c09c4850bf63f274e1a9236ce2cb21d736660647491766c69e32` of the literal `synthetic-dependence-aware-validation-v1\n`.
- Pair(s): none.
- Timeframe(s): none.
- Data range: not applicable. No prices were read.
- Train period: unchanged. Calibration master seed 20261126. That partition cannot validate a method.
- Validation period: unchanged. Holdout master seed 20261211. The holdout was already inspected. Reclassifying those counts is a methodological correction, not a fresh independent validation.
- Final-test touched?: NO
- Strategy/model: no strategy. The governing method remains DEC-469 / DEC-268 annual catalogue discovery. This module remains the dependence-aware-validation pattern tool. No lag, block, threshold, or interval formula was changed. The IID normal interval still uses the sample variance with divisor n−1 and the normal z quantile 1.959963984540054. The prior AR(1) counts 73/160, 117/160, and 13/20 were not used as targets.
- Features: none added.
- Parameters/search space: unchanged. The frozen family remains 89,460 directional hypotheses per annual segment. Familywise error at 89,460 was not estimated. The positive familywise rule remains the one-sided 95 percent Wilson upper bound at or below alpha 0.05, using quantile 1.6448536269514722, plus the predeclared precision floor and valid marginal p-values. A point estimate at or below alpha is not sufficient. No new large familywise experiment was launched. Bootstrap replicates stay at 60 of 99 draws. Studentized replicates stay at 60 of 49 draws.
- Random seed (if relevant): the harness seeds are unchanged. The bounded generator check remains seed 20261230, 4 replications, and family size 3. That seed is not a holdout seed and not an acceptance threshold.
- Spread/cost model: none applied.
- Slippage model: not applied. DEC-470 slippage stays recorded and unchanged.
- Risk assumptions: not applied. No trade is sized.
- Trade count: no market trades.
- Net return after costs: not a market result.
- Expectancy/trade: not a market expectancy. Effective sample sizes are unchanged and are not applied to event evidence.
- Profit factor: not computed
- Max drawdown: not computed
- Key subperiod results: not market years. Raw numerators and denominators are unchanged on all 284 rows and on all six family studies. Status changes come only from the corrected reference classification. Holdout row labels moved from 30 validated, 47 failed, 7 insufficient, and 73 unverified to 22 validated, 47 failed, 7 insufficient, and 81 unverified. The eight rows that left validated are IID normal intervals: independent 374/400, unique events 384/400, common-shock primary 381/400, common-shock contrast 378/400, short horizon 374/400, changing volatility 378/400, planted positive 374/400, and planted negative 374/400. Seven of those series are independent and identically distributed. The interval remains a sample-variance z approximation, so those rows are `MODEL_ASSUMPTIONS_UNVERIFIED`. The changing-volatility series is serially independent and is not identically distributed. The 22 remaining validated rows are known-variance Gaussian oracles, including the changing-volatility declared-model interval at 378/400 and the regime-change declared-model interval. Moving block length 1 on the independent series stayed insufficient at 56/60. The cluster-event bootstrap stayed insufficient at 58/60. The shock-rebuild bootstrap stayed insufficient at 55/60. Each of those three preserves its resampling structure and is not an exact finite-sample confidence interval. Four studentized rows stayed insufficient at 4/60, 4/60, 5/60, and 3/60. Failed coverage stayed failed. No lag or block was retuned. Holm counts stayed 17/400 equicorrelated, 19/400 independent, 17/400 mixed, 26/400 at family size 10, and 4/80 at family size 160. Their one-sided upper bounds remain above 0.05, so the empirical claim stays inconclusive. Uncorrected counts stayed failed. No catalogue-wide familywise-error control is authorized.
- Robustness/cost sensitivity: not a market cost study. One canonical compile on Python 3.12.13 took 18.334 seconds. Tracemalloc peak was 9,821,734 bytes. Canonical JSON was 1,270,910 bytes. SHA-256 was `a010913db8697ad6535fb49dae8ed8709d92829811b5d8471d6361c8ccb35ae9`. The EXP-20261120-075 document remains SHA-256 `45fc28d57302936bcd6af144081dab8850eee10ba26bb5ab803566f67df1a090`. The hash changed because labels changed. The numerators did not. Holm arithmetic outside the document took 0.044332 seconds at 89,460 hypotheses and estimated no familywise error. Routine validation does not regenerate the 400-replicate experiment. Altered counts plus a recomputed digest are not independently reproduced evidence. Focused dependence-validation tests were 12 and exited 0 in 25.514 seconds. Neighboring statistical-uncertainty, event-evidence, protocol, miner, cross-year, and segment-evidence tests were 82 and exited 0 in 42.588 seconds. Workflow files were not edited. A bootstrap validation of at least 200 replicates was not launched.
- Result summary: A known-variance Gaussian oracle can have an exact finite-sample reference. An IID interval that estimates the variance and uses a normal z quantile does not. Correct event or shock resampling does not make a percentile interval exact. Changing-volatility observations are not identically distributed. The 22 oracle rows remain the only validated rows. Catalogue inference stays unauthorized. This correction is not a new independent validation.
- Conclusion: NEED_MORE_DATA
- Reason: the rows are synthetic. The holdout was already inspected, so the revised classification is not an independent confirmation. Frozen historical catalogues were not opened. Valid p-values for the 89,460-hypothesis family are not available. Sixty bootstrap replicates and sixty studentized replicates do not establish calibrated intervals or p-values. Student's t was not substituted for the existing z interval.
- Follow-up: keep DEC-470, the event-evidence schema, the statistical-uncertainty schema, the annual miner, and the cross-year statistical block unchanged. Annual run 385 stays unopened. No merge is authorized by this experiment.

### EXP-20261123-078 — N1-v0 synthetic signal check

- Date: 2026-11-23
- Status: INCONCLUSIVE
- Hypothesis: Frozen N1-v0 emits reproducible EURUSD decisions from synthetic quotes, and the existing engine records the hypothetical spread, one slippage assumption, and the published commission without changing the signal or the original stop.
- Code commit: branch `draft/dec637-n1-v0-synthetic-exception`. Authorization parent `ca5ba3c6533a667d93e57ef22369bfab3fe3042b`. Branch base `845e571a451fed51e638140ea3d1f0c72fa8c907`.
- Data manifest/version: `n1-v0-synthetic-quotes`. No market-data file and no protected artifact was opened.
- Pair(s): EURUSD is the only traded symbol. GBPUSD and USDJPY are direction inputs in the synthetic fixture.
- Timeframe(s): 1m quotes supplied directly. No derived-bar builder was used.
- Data range: not applicable. Clocks are 2026-01-13, 2026-03-08, 2026-03-09, 2026-07-14, and 2026-11-02 America/New_York.
- Train period: not applicable
- Validation period: not applicable
- Final-test touched?: NO
- Strategy/model: N1-v0 News-Shock USD Continuation, isolated in `src/fmp/research/n1_news_shock.py`. Not registered. Not Strategy V1. DEC-469 / DEC-268 remain the governing method.
- Features: none
- Parameters/search space: none. The rule, the 0.25% risk fraction, the 08:36 entry, and the 09:30 exit are frozen.
- Random seed (if relevant): not applicable
- Spread/cost model: the spread is the synthetic bid/ask. Commission is the published IC Markets Raw Spread MetaTrader figure of 3.50 USD per standard lot per side, accessed 2026-11-17, passed through `FixedCommissionPerMillion` at 35 USD per million per side. The package is hypothetical. It is not a verified Dukascopy fill and not verified broker execution.
- Slippage model: one adverse `slippage_pips` value per run. The recorded check uses 0.5 pip, and separate runs use 0.2 and 1.0 pip. Those runs are not combined into an asymmetric or worst-extreme fill.
- Risk assumptions: 0.25% of current risk equity, subject to the existing 0.50% per-trade, 1.00% simultaneous, and 1.50% daily-halt limits. An entry through the original stop is `INVALID_STOP_TARGET`. A risk budget that sizes to zero units is `INVALID_SIZE`.
- Trade count: synthetic fixtures only. No market trades.
- Net return after costs: not a market result. The 100,000-unit short fixture records 7.00 USD round-turn commission at the published 3.50 per-side rate, plus adverse slippage on the 0.5-pip run.
- Expectancy/trade: not estimated
- Profit factor: not computed
- Max drawdown: not computed
- Key subperiod results: not market years. Winter and summer clocks convert to 13:30 UTC and 12:30 UTC. The 2026-03-08 02:30 America/New_York gap is rejected.
- Robustness/cost sensitivity: later synthetic prices change the fill and the size and leave the direction and the original stop unchanged. A separate 1.0-pip run is a second single-assumption stress, not one asymmetric fill.
- Result summary: 16 focused tests in `tests.test_n1_news_shock` exited 0. USD strength is short EURUSD. USD weakness is long EURUSD. Mixed, flat, missing, unpublished, delayed, mistimed, and unsupported releases stay NO TRADE. Two releases on one New York date stay NO TRADE. The fill is the 08:36 open. The scheduled exit is the 09:30 open. A gap stop fills at the opened-through price. A missing 08:36 bar is `TIMING_CONTRACT`. A missing 09:30 bar stays `END_OF_DATA` and is not rewritten. NO TRADE rows are kept.
- Conclusion: NEED_MORE_DATA
- Reason: the rows are synthetic engineering checks. They do not show a market edge. Prospective collection is written and not approved.
- Follow-up: keep DEC-470, DEC-629, and DEC-630 unchanged. Do not collect market data until a later separate approval. Do not merge this branch as a promotion. Annual run 385 stays unopened.
- Addendum 2026-11-23: `review_n1_observation` labels the same synthetic fixtures after the engine returns. Focused `tests.test_n1_news_shock` was 24 tests and exited 0. A missing 09:30 bar stays `END_OF_DATA` and is not an ordinary time exit. A missing intermediate bar stays incomplete when the engine returns `TIME_EXIT`. The 08:35 bar is not required. The signal, the original stop, and the engine are unchanged. Collection remains unapproved.
